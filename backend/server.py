import os
import uuid
import logging
import asyncio
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import asyncpg
from dotenv import load_dotenv
import httpx

from constants import (
    MIN_MESSAGE_LENGTH, CATEGORY_GENERAL, STATUS_NEW,
    SENDER_MANAGER, HTTP_TIMEOUT, WEBHOOK_TIMEOUT
)

load_dotenv()

# Настройка логирования с ротацией (макс 10MB, 5 backup файлов)
log_handler = RotatingFileHandler(
    'server.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)
log_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        log_handler,
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация
DB_USER = os.getenv('DB_USER', 'postgres')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_NAME = os.getenv('DB_NAME', 'sulpak_helpdesk')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '3002'))

# CORS origins - в продакшене должны быть указаны конкретные домены
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')

print(f'DB Config: user={DB_USER}, host={DB_HOST}, database={DB_NAME}, port={DB_PORT}')

# Database pool
db_pool: Optional[asyncpg.Pool] = None


# Инициализация БД
async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT,
        min_size=5,
        max_size=20
    )

    # Создание таблиц
    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id SERIAL PRIMARY KEY,
                ticket_number VARCHAR(20) UNIQUE,
                telegram_user_id BIGINT,
                telegram_username VARCHAR(255),
                status VARCHAR(50) DEFAULT 'new',
                assigned_manager_id INT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                ticket_id INT REFERENCES tickets(id),
                sender_type VARCHAR(20),
                sender_id VARCHAR(255),
                content TEXT,
                media_type VARCHAR(20),
                media_url TEXT,
                media_file_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS managers (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                telegram_id BIGINT,
                active BOOLEAN DEFAULT true
            );
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id BIGINT PRIMARY KEY,
                active_ticket_id INT,
                awaiting_clarification BOOLEAN DEFAULT false,
                original_message TEXT,
                pending_media_type VARCHAR(20),
                pending_media_url TEXT,
                pending_media_file_id VARCHAR(255),
                pending_media_caption TEXT,
                updated_at TIMESTAMP DEFAULT NOW()
            );
        ''')

        # Создание индексов для оптимизации запросов
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_tickets_telegram_user_id
            ON tickets(telegram_user_id);
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_tickets_status
            ON tickets(status);
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_tickets_created_at
            ON tickets(created_at DESC);
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_ticket_id
            ON messages(ticket_id);
        ''')

        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_created_at
            ON messages(created_at ASC);
        ''')

    logger.info('Database initialized with indexes')
    print('Database initialized')


# Закрытие БД
async def close_db():
    global db_pool
    if db_pool:
        await db_pool.close()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


app = FastAPI(title="Sulpak HelpDesk API", version="1.0.0", lifespan=lifespan)

# CORS - ограничены конкретными доменами
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# API Router для версионирования
api_v1_router = APIRouter(prefix="/api/v1", tags=["v1"])



# Pydantic модели с валидацией
class CreateTicketRequest(BaseModel):
    telegramUserId: int = Field(gt=0, description="Telegram User ID должен быть положительным")
    telegramUsername: str = Field(min_length=1, max_length=255, description="Username не может быть пустым")
    message: str = Field(min_length=MIN_MESSAGE_LENGTH, max_length=4000, description=f"Сообщение должно быть от {MIN_MESSAGE_LENGTH} до 4000 символов")


class AddMessageRequest(BaseModel):
    senderType: str = Field(pattern="^(client|manager)$", description="Тип отправителя: client или manager")
    senderId: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1, max_length=4000, description="Сообщение не может быть пустым")
    mediaType: Optional[str] = Field(None, pattern="^(photo|video)$")
    mediaUrl: Optional[str] = Field(None, max_length=1000)
    mediaFileId: Optional[str] = Field(None, max_length=255)


class UpdateStatusRequest(BaseModel):
    status: str = Field(pattern="^(new|in_progress|resolved|closed)$", description="Недопустимый статус")


class AssignManagerRequest(BaseModel):
    managerId: int = Field(gt=0, description="Manager ID должен быть положительным")


class ValidationResult(BaseModel):
    isValid: bool
    missingInfo: List[str]
    suggestion: str
    category: str


# AI валидация (заглушка)
async def validate_with_ai(message: str) -> ValidationResult:
    message_length = len(message.strip())

    # Если сообщение слишком короткое
    if message_length < 10:
        return ValidationResult(
            isValid=False,
            missingInfo=['Описание проблемы'],
            suggestion='Пожалуйста, опишите вашу проблему более подробно.',
            category='general'
        )

    # Определяем категорию по ключевым словам
    category = 'general'
    lower_message = message.lower()

    if 'приложение' in lower_message or 'app' in lower_message:
        category = 'приложение'
    elif 'доставка' in lower_message or 'курьер' in lower_message:
        category = 'доставка'
    elif 'оплата' in lower_message or 'карта' in lower_message:
        category = 'оплата'
    elif 'товар' in lower_message or 'продукт' in lower_message:
        category = 'товар'

    return ValidationResult(
        isValid=True,
        missingInfo=[],
        suggestion='',
        category=category
    )


# Генерация номера тикета
def generate_ticket_number() -> str:
    """Генерация уникального номера тикета"""
    now = datetime.now()
    year = now.strftime('%y')
    month = now.strftime('%m')
    # Используем часть UUID для гарантии уникальности
    unique_part = str(uuid.uuid4().hex)[:6].upper()
    return f"SH{year}{month}{unique_part}"


# API Routes

@api_v1_router.post("/tickets")
async def create_ticket(request: CreateTicketRequest):
    """Создание нового тикета"""
    # AI валидация
    validation = await validate_with_ai(request.message)

    if not validation.isValid:
        return {
            "success": False,
            "needsClarification": True,
            "suggestion": validation.suggestion,
            "missingInfo": validation.missingInfo
        }

    # Создание тикета
    ticket_number = generate_ticket_number()

    async with db_pool.acquire() as conn:
        # Вставка тикета
        ticket = await conn.fetchrow(
            '''INSERT INTO tickets (ticket_number, telegram_user_id, telegram_username, status)
               VALUES ($1, $2, $3, $4) RETURNING *''',
            ticket_number, request.telegramUserId, request.telegramUsername, 'new'
        )

        # Вставка первого сообщения
        await conn.execute(
            '''INSERT INTO messages (ticket_id, sender_type, sender_id, content)
               VALUES ($1, $2, $3, $4)''',
            ticket['id'], 'client', str(request.telegramUserId), request.message
        )

    return {
        "success": True,
        "ticket": {
            "id": ticket['id'],
            "ticketNumber": ticket['ticket_number'],
            "status": ticket['status'],
            "createdAt": ticket['created_at'].isoformat()
        },
        "category": validation.category
    }


@api_v1_router.get("/tickets")
async def get_tickets(user_id: Optional[int] = None):
    """Получить все тикеты или отфильтровать по telegram_user_id"""
    async with db_pool.acquire() as conn:
        if user_id:
            # Фильтрация по user_id на уровне SQL
            tickets = await conn.fetch('''
                SELECT t.*,
                    (SELECT content FROM messages WHERE ticket_id = t.id ORDER BY created_at ASC LIMIT 1) as first_message,
                    (SELECT COUNT(*) FROM messages WHERE ticket_id = t.id) as message_count
                FROM tickets t
                WHERE t.telegram_user_id = $1
                ORDER BY t.created_at DESC
            ''', user_id)
        else:
            # Все тикеты (для менеджеров)
            tickets = await conn.fetch('''
                SELECT t.*,
                    (SELECT content FROM messages WHERE ticket_id = t.id ORDER BY created_at ASC LIMIT 1) as first_message,
                    (SELECT COUNT(*) FROM messages WHERE ticket_id = t.id) as message_count
                FROM tickets t
                ORDER BY t.created_at DESC
            ''')

    return [dict(ticket) for ticket in tickets]


@api_v1_router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = 0
):
    """Получить тикет по ID с сообщениями (с опциональной пагинацией)"""
    async with db_pool.acquire() as conn:
        ticket = await conn.fetchrow('SELECT * FROM tickets WHERE id = $1', ticket_id)

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Подсчет общего количества сообщений
        total_messages = await conn.fetchval(
            'SELECT COUNT(*) FROM messages WHERE ticket_id = $1',
            ticket_id
        )

        # Запрос сообщений с пагинацией
        if limit:
            messages = await conn.fetch(
                'SELECT * FROM messages WHERE ticket_id = $1 ORDER BY created_at ASC LIMIT $2 OFFSET $3',
                ticket_id, limit, offset
            )
        else:
            # Без пагинации - все сообщения
            messages = await conn.fetch(
                'SELECT * FROM messages WHERE ticket_id = $1 ORDER BY created_at ASC',
                ticket_id
            )

    return {
        "ticket": dict(ticket),
        "messages": [dict(msg) for msg in messages],
        "pagination": {
            "total": total_messages,
            "limit": limit,
            "offset": offset
        } if limit else None
    }


@api_v1_router.post("/tickets/{ticket_id}/messages")
async def add_message(ticket_id: int, request: AddMessageRequest):
    """Добавить сообщение в тикет"""
    async with db_pool.acquire() as conn:
        # Проверка существования тикета
        ticket_exists = await conn.fetchval('SELECT EXISTS(SELECT 1 FROM tickets WHERE id = $1)', ticket_id)
        if not ticket_exists:
            raise HTTPException(status_code=404, detail="Ticket not found")

        # Сохранить сообщение
        message = await conn.fetchrow(
            '''INSERT INTO messages (ticket_id, sender_type, sender_id, content, media_type, media_url, media_file_id)
               VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *''',
            ticket_id, request.senderType, request.senderId, request.content,
            request.mediaType, request.mediaUrl, request.mediaFileId
        )

        # Обновить время тикета
        await conn.execute(
            'UPDATE tickets SET updated_at = NOW() WHERE id = $1',
            ticket_id
        )

        # Если сообщение от менеджера - отправить клиенту в Telegram
        if request.senderType == SENDER_MANAGER:
            ticket = await conn.fetchrow(
                'SELECT telegram_user_id, ticket_number FROM tickets WHERE id = $1',
                ticket_id
            )

            if ticket:
                # Отправка в webhook с retry logic
                webhook_url = f"http://localhost:{WEBHOOK_PORT}/webhook/send-message"
                max_retries = 3
                retry_count = 0
                success = False

                while retry_count < max_retries and not success:
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                webhook_url,
                                json={
                                    "telegramUserId": ticket['telegram_user_id'],
                                    "message": request.content,
                                    "ticketNumber": ticket['ticket_number']
                                },
                                timeout=WEBHOOK_TIMEOUT
                            )
                            response.raise_for_status()
                            success = True
                            logger.info(f"Message sent to Telegram user {ticket['telegram_user_id']} for ticket #{ticket['ticket_number']}")
                    except (httpx.TimeoutException, httpx.HTTPError) as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.warning(f"Webhook attempt {retry_count} failed, retrying... Error: {e}")
                            await asyncio.sleep(1 * retry_count)  # Exponential backoff
                        else:
                            logger.error(f"Failed to send message to Telegram after {max_retries} attempts: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error sending to Telegram: {e}")
                        break

    return dict(message)


@api_v1_router.patch("/tickets/{ticket_id}/status")
async def update_status(ticket_id: int, request: UpdateStatusRequest):
    """Обновить статус тикета"""
    async with db_pool.acquire() as conn:
        ticket = await conn.fetchrow(
            'UPDATE tickets SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING *',
            request.status, ticket_id
        )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return dict(ticket)


@api_v1_router.patch("/tickets/{ticket_id}/assign")
async def assign_manager(ticket_id: int, request: AssignManagerRequest):
    """Назначить менеджера"""
    async with db_pool.acquire() as conn:
        ticket = await conn.fetchrow(
            '''UPDATE tickets SET assigned_manager_id = $1, status = $2, updated_at = NOW()
               WHERE id = $3 RETURNING *''',
            request.managerId, 'in_progress', ticket_id
        )

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return dict(ticket)


@app.get("/health")
async def health_check():
    """Health check endpoint для мониторинга"""
    try:
        # Проверка подключения к БД
        async with db_pool.acquire() as conn:
            await conn.fetchval('SELECT 1')

        return {
            "status": "healthy",
            "service": "api-server",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"status": "unhealthy", "error": str(e)}
        )


# User Sessions API
class UserSession(BaseModel):
    user_id: int = Field(gt=0)
    active_ticket_id: Optional[int] = None
    awaiting_clarification: bool = False
    original_message: str = ""
    pending_media_type: Optional[str] = None
    pending_media_url: Optional[str] = None
    pending_media_file_id: Optional[str] = None
    pending_media_caption: Optional[str] = None


@api_v1_router.get("/sessions/{user_id}")
async def get_session(user_id: int):
    """Получить сессию пользователя"""
    async with db_pool.acquire() as conn:
        session = await conn.fetchrow(
            'SELECT * FROM user_sessions WHERE user_id = $1',
            user_id
        )

        if not session:
            # Создать новую сессию с дефолтными значениями
            session = await conn.fetchrow(
                '''INSERT INTO user_sessions (user_id, active_ticket_id, awaiting_clarification, original_message)
                   VALUES ($1, NULL, false, '') RETURNING *''',
                user_id
            )

    return dict(session)


@api_v1_router.post("/sessions")
async def update_session(session_data: UserSession):
    """Обновить или создать сессию пользователя"""
    async with db_pool.acquire() as conn:
        session = await conn.fetchrow(
            '''INSERT INTO user_sessions
               (user_id, active_ticket_id, awaiting_clarification, original_message,
                pending_media_type, pending_media_url, pending_media_file_id, pending_media_caption, updated_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
               ON CONFLICT (user_id)
               DO UPDATE SET
                   active_ticket_id = $2,
                   awaiting_clarification = $3,
                   original_message = $4,
                   pending_media_type = $5,
                   pending_media_url = $6,
                   pending_media_file_id = $7,
                   pending_media_caption = $8,
                   updated_at = NOW()
               RETURNING *''',
            session_data.user_id,
            session_data.active_ticket_id,
            session_data.awaiting_clarification,
            session_data.original_message,
            session_data.pending_media_type,
            session_data.pending_media_url,
            session_data.pending_media_file_id,
            session_data.pending_media_caption
        )

    return dict(session)


# Подключаем router к приложению
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', '3001'))
    uvicorn.run(app, host="0.0.0.0", port=port)

