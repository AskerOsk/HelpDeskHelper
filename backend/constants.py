"""
Константы приложения
"""

# Валидация сообщений
MIN_MESSAGE_LENGTH = 10  # Минимальная длина сообщения для создания тикета

# Категории тикетов
CATEGORY_APP = 'приложение'
CATEGORY_DELIVERY = 'доставка'
CATEGORY_PAYMENT = 'оплата'
CATEGORY_PRODUCT = 'товар'
CATEGORY_GENERAL = 'general'

# Статусы тикетов
STATUS_NEW = 'new'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_RESOLVED = 'resolved'
STATUS_CLOSED = 'closed'

# Типы отправителей
SENDER_CLIENT = 'client'
SENDER_MANAGER = 'manager'

# Типы медиа
MEDIA_PHOTO = 'photo'
MEDIA_VIDEO = 'video'

# Таймауты (в секундах)
HTTP_TIMEOUT = 10.0
WEBHOOK_TIMEOUT = 5.0

# Интервалы обновления (в миллисекундах для фронтенда)
TICKETS_UPDATE_INTERVAL = 5000
MESSAGES_UPDATE_INTERVAL = 3000

# UI константы для статусов (используется в Telegram Bot и Frontend)
STATUS_EMOJI = {
    STATUS_NEW: '🆕',
    STATUS_IN_PROGRESS: '⏳',
    STATUS_RESOLVED: '✅',
    STATUS_CLOSED: '🔒'
}

STATUS_TEXT_RU = {
    STATUS_NEW: 'Новый',
    STATUS_IN_PROGRESS: 'В работе',
    STATUS_RESOLVED: 'Решен',
    STATUS_CLOSED: 'Закрыт'
}

