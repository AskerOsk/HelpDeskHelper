"""
Константы приложения - AI-powered HelpDesk
"""

# Валидация сообщений
MIN_MESSAGE_LENGTH = 10  # Минимальная длина сообщения для создания тикета

# Категории тикетов
CATEGORY_APP = 'приложение'
CATEGORY_DELIVERY = 'доставка'
CATEGORY_PAYMENT = 'оплата'
CATEGORY_PRODUCT = 'товар'
CATEGORY_GENERAL = 'general'

# Статусы тикетов (AI-focused)
STATUS_NEW = 'new'
STATUS_AI_PROCESSING = 'ai_processing'
STATUS_RESOLVED = 'resolved'
STATUS_ESCALATED = 'escalated'
STATUS_CLOSED = 'closed'

# Типы отправителей (AI вместо manager)
SENDER_USER = 'user'  # Клиент (renamed from client для ясности)
SENDER_AI = 'ai'      # AI ассистент (заменяет manager)

# Типы медиа
MEDIA_PHOTO = 'photo'
MEDIA_VIDEO = 'video'

# AI константы
AI_CONFIDENCE_THRESHOLD = 0.7  # Порог уверенности AI для автоответа
AI_MODEL_DEFAULT = 'qwen2.5:3b'  # Ollama default model (отлично работает с русским)
AI_MAX_CONTEXT_MESSAGES = 20  # Максимум сообщений в контексте

# Email константы
EMAIL_ESCALATION_SUBJECT = "🚨 Sulpak HelpDesk - Escalation Required"
EMAIL_FROM_NAME = "Sulpak AI HelpDesk"

# Таймауты (в секундах)
HTTP_TIMEOUT = 10.0
WEBHOOK_TIMEOUT = 5.0
AI_RESPONSE_TIMEOUT = 30.0

# Интервалы обновления (в миллисекундах для фронтенда)
TICKETS_UPDATE_INTERVAL = 5000
MESSAGES_UPDATE_INTERVAL = 3000

# UI константы для статусов (используется в Telegram Bot и Frontend)
STATUS_EMOJI = {
    STATUS_NEW: '🆕',
    STATUS_AI_PROCESSING: '🤖',
    STATUS_RESOLVED: '✅',
    STATUS_ESCALATED: '🚨',
    STATUS_CLOSED: '🔒'
}

STATUS_TEXT_RU = {
    STATUS_NEW: 'Новый',
    STATUS_AI_PROCESSING: 'AI обрабатывает',
    STATUS_RESOLVED: 'Решен',
    STATUS_ESCALATED: 'Эскалирован',
    STATUS_CLOSED: 'Закрыт'
}

# UI цвета (для нового дизайна)
COLOR_BLACK = '#000000'
COLOR_NEON_GREEN = '#00FF41'
COLOR_ORANGE = '#FF6B35'
COLOR_DARK_GRAY = '#1A1A1A'
COLOR_LIGHT_GRAY = '#2A2A2A'

