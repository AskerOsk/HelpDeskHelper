import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from telegram import Bot
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_PORT = int(os.getenv('WEBHOOK_PORT', '3002'))

# Валидация конфигурации
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
    logger.error("Please set TELEGRAM_BOT_TOKEN in backend/.env file")
    raise ValueError("TELEGRAM_BOT_TOKEN is required to run the webhook server")

app = FastAPI(title="Telegram Webhook")

# Создание бота с правильной конфигурацией httpx
request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=10.0,
    read_timeout=10.0
)
bot = Bot(token=TELEGRAM_BOT_TOKEN, request=request)


class SendMessageRequest(BaseModel):
    telegramUserId: int
    message: str
    ticketNumber: str


@app.post("/webhook/send-message")
async def send_message(request: SendMessageRequest):
    """Отправить сообщение клиенту в Telegram"""
    try:
        await bot.send_message(
            chat_id=request.telegramUserId,
            text=f"💬 *Ответ менеджера* ({request.ticketNumber}):\n\n{request.message}",
            parse_mode=ParseMode.MARKDOWN
        )
        return {"success": True}
    except Exception as e:
        logger.error(f"Error sending message to client {request.telegramUserId}: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Bot webhook listening on port {WEBHOOK_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT)

