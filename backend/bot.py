import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from dotenv import load_dotenv
import httpx
from datetime import datetime

from constants import (
    SENDER_CLIENT, MIN_MESSAGE_LENGTH, HTTP_TIMEOUT,
    STATUS_EMOJI, STATUS_TEXT_RU
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:3001')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '3002'))

# Валидация конфигурации
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
    logger.error("Please set TELEGRAM_BOT_TOKEN in backend/.env file")
    raise ValueError("TELEGRAM_BOT_TOKEN is required to run the bot")

async def get_session(user_id: int) -> dict:
    """Получить или создать сессию пользователя из БД"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BACKEND_URL}/api/v1/sessions/{user_id}",
                timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching session for user {user_id}: {e}")
        # Возвращаем дефолтную сессию в случае ошибки
        return {
            'user_id': user_id,
            'active_ticket_id': None,
            'awaiting_clarification': False,
            'original_message': '',
            'pending_media_type': None,
            'pending_media_url': None,
            'pending_media_file_id': None,
            'pending_media_caption': None
        }


async def update_session(session_data: dict):
    """Обновить сессию пользователя в БД"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/v1/sessions",
                json=session_data,
                timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return None


def main_menu() -> InlineKeyboardMarkup:
    """Главное меню"""
    keyboard = [
        [InlineKeyboardButton("📋 Мои запросы", callback_data="list_tickets")],
        [InlineKeyboardButton("➕ Новый запрос", callback_data="new_ticket")]
    ]
    return InlineKeyboardMarkup(keyboard)


def ticket_menu(ticket_id: int) -> InlineKeyboardMarkup:
    """Меню активного тикета"""
    keyboard = [
        [
            InlineKeyboardButton("📋 К списку", callback_data="list_tickets"),
            InlineKeyboardButton("➕ Новый запрос", callback_data="new_ticket")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


async def get_user_tickets(user_id: int) -> list:
    """Получить тикеты пользователя"""
    try:
        async with httpx.AsyncClient() as client:
            # Используем query параметр для фильтрации на уровне SQL
            response = await client.get(
                f"{BACKEND_URL}/api/v1/tickets",
                params={"user_id": user_id},
                timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching user tickets: {e}")
        return []


async def get_ticket_details(ticket_id: int) -> dict:
    """Получить детали тикета"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_URL}/api/v1/tickets/{ticket_id}", timeout=10.0)
            return response.json()
    except Exception as e:
        print(f"Error fetching ticket details: {e}")
        return None


async def show_ticket_list(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Показать список тикетов"""
    tickets = await get_user_tickets(user_id)

    if not tickets:
        await update.effective_message.reply_text(
            "📋 У вас пока нет запросов.",
            reply_markup=main_menu()
        )
        return

    message = '📋 *Ваши запросы:*\n\n'
    buttons = []

    for ticket in tickets:
        status = STATUS_EMOJI.get(ticket['status'], '📌')
        status_name = STATUS_TEXT_RU.get(ticket['status'], ticket['status'])
        preview = ticket.get('first_message', 'Без описания')
        if preview and len(preview) > 50:
            preview = preview[:50] + '...'

        message += f"{status} *{ticket['ticket_number']}* - {status_name}\n"
        message += f"{preview}\n\n"

        buttons.append([
            InlineKeyboardButton(f"📂 {ticket['ticket_number']}", callback_data=f"open_{ticket['id']}")
        ])

    buttons.append([InlineKeyboardButton("➕ Новый запрос", callback_data="new_ticket")])

    await update.effective_message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def show_ticket_details(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, ticket_id: int):
    """Показать детали тикета"""
    details = await get_ticket_details(ticket_id)

    if not details:
        await update.effective_message.reply_text("❌ Запрос не найден.")
        return

    session = await get_session(user_id)
    session['active_ticket_id'] = ticket_id
    await update_session(session)

    ticket = details['ticket']
    messages = details.get('messages', [])

    created_at = datetime.fromisoformat(ticket['created_at'].replace('Z', '+00:00'))

    message = f"📂 *Запрос {ticket['ticket_number']}*\n\n"
    message += f"Статус: {STATUS_EMOJI.get(ticket['status'], '📌')} {STATUS_TEXT_RU.get(ticket['status'], ticket['status'])}\n"
    message += f"Создан: {created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    message += "━━━━━━━━━━━━━━━━\n\n"

    for msg in messages:
        sender = '👤 Вы' if msg['sender_type'] == 'client' else '👨‍💼 Менеджер'
        msg_time = datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00'))
        time_str = msg_time.strftime('%H:%M')
        message += f"{sender} ({time_str}):\n{msg['content']}\n\n"

    message += "━━━━━━━━━━━━━━━━\n\n"
    message += "💬 *Активный запрос*\nВаши следующие сообщения будут добавлены в этот запрос."

    await update.effective_message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ticket_menu(ticket_id)
    )


async def create_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, username: str, message: str):
    """Создать новый тикет"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/v1/tickets",
                json={
                    "telegramUserId": user_id,
                    "telegramUsername": username,
                    "message": message
                },
                timeout=10.0
            )
            data = response.json()

        if data.get('needsClarification'):
            await update.effective_message.reply_text(f"❓ {data['suggestion']}")
            session = await get_session(user_id)
            session['awaiting_clarification'] = True
            session['original_message'] = message
            await update_session(session)
        elif data.get('success'):
            session = await get_session(user_id)
            ticket_id = data['ticket']['id']
            session['active_ticket_id'] = ticket_id

            # Если было отправлено медиа вместе с созданием тикета
            if session.get('pending_media_type'):
                try:
                    async with httpx.AsyncClient() as client:
                        await client.post(
                            f"{BACKEND_URL}/api/v1/tickets/{ticket_id}/messages",
                            json={
                                "senderType": "client",
                                "senderId": str(user_id),
                                "content": session['pending_media_caption'] or "Медиа",
                                "mediaType": session['pending_media_type'],
                                "mediaUrl": session['pending_media_url'],
                                "mediaFileId": session['pending_media_file_id']
                            },
                            timeout=HTTP_TIMEOUT
                        )
                    # Очистить pending media из сессии
                    session['pending_media_type'] = None
                    session['pending_media_url'] = None
                    session['pending_media_file_id'] = None
                    session['pending_media_caption'] = None
                except Exception as e:
                    logger.error(f"Error saving media to ticket {ticket_id}: {e}", exc_info=True)

            await update_session(session)

            await update.effective_message.reply_text(
                f"✅ *Запрос создан!*\n\n"
                f"📋 Номер: *{data['ticket']['ticketNumber']}*\n"
                f"📁 Категория: {data['category']}\n"
                f"⏰ Статус: В обработке\n\n"
                f"Менеджер свяжется с вами в ближайшее время.\n\n"
                f"💬 Ваши следующие сообщения будут добавлены в этот запрос.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=ticket_menu(ticket_id)
            )
        else:
            await update.effective_message.reply_text("❌ Произошла ошибка при создании запроса.")
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        await update.effective_message.reply_text("❌ Ошибка связи с сервером.")


async def add_message_to_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, ticket_id: int, message: str, media_type: str = None, media_url: str = None, media_file_id: str = None):
    """Добавить сообщение в существующий тикет"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_URL}/api/v1/tickets/{ticket_id}/messages",
                json={
                    "senderType": SENDER_CLIENT,
                    "senderId": str(user_id),
                    "content": message,
                    "mediaType": media_type,
                    "mediaUrl": media_url,
                    "mediaFileId": media_file_id
                },
                timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()

        response_text = "✅ Сообщение добавлено в запрос.\n\nМенеджер получит уведомление."
        if media_type:
            response_text = f"✅ {media_type.capitalize()} добавлено в запрос.\n\nМенеджер получит уведомление."

        await update.effective_message.reply_text(
            response_text,
            reply_markup=ticket_menu(ticket_id)
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error adding message: {e.response.status_code} - {e.response.text}")
        await update.effective_message.reply_text(f"❌ Ошибка сервера при добавлении сообщения: {e.response.status_code}")
    except httpx.TimeoutException:
        logger.error(f"Timeout adding message to ticket {ticket_id}")
        await update.effective_message.reply_text("❌ Превышено время ожидания. Попробуйте позже.")
    except Exception as e:
        logger.error(f"Error adding message to ticket {ticket_id}: {e}", exc_info=True)
        await update.effective_message.reply_text("❌ Ошибка при добавлении сообщения.")


# Обработчики команд

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "👋 *Добро пожаловать в Sulpak HelpDesk!*\n\n"
        "Я помогу вам решить любые вопросы.\n\n"
        "Выберите действие:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu()
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu"""
    await update.message.reply_text(
        "📱 *Главное меню:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu()
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "list_tickets":
        await show_ticket_list(update, context, user_id)
    elif data == "new_ticket":
        session = await get_session(user_id)
        session['active_ticket_id'] = None
        await update_session(session)
        await query.message.reply_text("✍️ Опишите вашу проблему:")
    elif data.startswith("open_"):
        ticket_id = int(data.replace("open_", ""))
        await show_ticket_details(update, context, user_id, ticket_id)


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    if not update.message or not update.message.text:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    message = update.message.text

    session = await get_session(user_id)

    try:
        # Если ожидаем уточнение
        if session.get('awaiting_clarification'):
            full_message = f"{session['original_message']}\n\nДополнительно: {message}"
            session['awaiting_clarification'] = False
            session['original_message'] = ''
            await update_session(session)

            await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
            await create_ticket(update, context, user_id, username, full_message)
            return

        # Если есть активный тикет - добавляем сообщение в него
        if session.get('active_ticket_id'):
            await add_message_to_ticket(update, context, user_id, session['active_ticket_id'], message)
            return

        # Создаем новый тикет
        await update.message.reply_text("⏳ Обрабатываю ваш запрос...")
        await create_ticket(update, context, user_id, username, message)

    except Exception as e:
        print(f"Bot error: {e}")
        await update.message.reply_text(
            "❌ Ошибка связи с сервером.",
            reply_markup=main_menu()
        )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка фото от пользователя"""
    if not update.message or not update.message.photo:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    caption = update.message.caption or "Фото"
    session = await get_session(user_id)

    try:
        # Получаем файл с максимальным разрешением
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Получаем URL файла из Telegram
        media_url = file.file_path
        media_file_id = photo.file_id

        # Если есть активный тикет - добавляем фото в него
        if session.get('active_ticket_id'):
            await add_message_to_ticket(
                update, context, user_id, session['active_ticket_id'],
                caption, media_type='photo', media_url=media_url, media_file_id=media_file_id
            )
        else:
            # Создаем новый тикет с фото
            await update.message.reply_text("⏳ Обрабатываю ваш запрос с фото...")
            # Для нового тикета сохраним информацию о медиа в сессию
            session['pending_media_type'] = 'photo'
            session['pending_media_url'] = media_url
            session['pending_media_file_id'] = media_file_id
            session['pending_media_caption'] = caption
            await update_session(session)
            await create_ticket(update, context, user_id, username, caption)

    except Exception as e:
        logger.error(f"Photo handler error: {e}", exc_info=True)
        await update.message.reply_text("❌ Ошибка обработки фото.", reply_markup=main_menu())


async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка видео от пользователя"""
    if not update.message or not update.message.video:
        return

    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name
    caption = update.message.caption or "Видео"
    session = await get_session(user_id)

    try:
        # Получаем файл видео
        video = update.message.video
        file = await context.bot.get_file(video.file_id)

        # Получаем URL файла из Telegram
        media_url = file.file_path
        media_file_id = video.file_id

        # Если есть активный тикет - добавляем видео в него
        if session.get('active_ticket_id'):
            await add_message_to_ticket(
                update, context, user_id, session['active_ticket_id'],
                caption, media_type='video', media_url=media_url, media_file_id=media_file_id
            )
        else:
            # Создаем новый тикет с видео
            await update.message.reply_text("⏳ Обрабатываю ваш запрос с видео...")
            session['pending_media_type'] = 'video'
            session['pending_media_url'] = media_url
            session['pending_media_file_id'] = media_file_id
            session['pending_media_caption'] = caption
            await update_session(session)
            await create_ticket(update, context, user_id, username, caption)

    except Exception as e:
        logger.error(f"Video handler error: {e}", exc_info=True)
        await update.message.reply_text("❌ Ошибка обработки видео.", reply_markup=main_menu())


def main():
    """Запуск бота"""
    logger.info("Starting Telegram bot...")

    # Создание приложения
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    application.add_handler(MessageHandler(filters.VIDEO, video_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    # Запуск бота
    logger.info("Telegram bot started successfully")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

