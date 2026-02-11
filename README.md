# Sulpak HelpDesk System

Система обработки обращений клиентов через Telegram с панелью управления для менеджеров.

## 📚 Документация

- **[docs/START_HERE.md](docs/START_HERE.md)** ⭐ - Начните отсюда! Быстрый старт за 3 шага
- **[docs/MEDIA_SUPPORT.md](docs/MEDIA_SUPPORT.md)** 📸 - Поддержка фото и видео (НОВОЕ!)
- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** - Детальная инструкция по установке
- **[docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Подробная структура проекта
- **[docs/FAQ.md](docs/FAQ.md)** - Часто задаваемые вопросы и решение проблем

---

## 🏗️ Архитектура

**Backend** (Python + FastAPI + PostgreSQL)
- REST API для управления тикетами (FastAPI)
- Telegram Bot для взаимодействия с клиентами (python-telegram-bot)
- Поддержка фото и видео от пользователей 📸
- PostgreSQL для хранения данных
- Порты: 3001 (API), 3002 (Webhook)

**Frontend** (React + Vite + Tailwind CSS)
- Панель менеджера для работы с обращениями
- Real-time чат с клиентами
- Управление статусами тикетов
- Порт: 5173 (dev), 80 (production)

**База данных** (PostgreSQL)
- Таблицы: tickets, messages, managers
- Автоматическая инициализация при первом запуске

---

## 🚀 Быстрый запуск

### Локально (3 команды):

```bash
# 1. Установка
.\install-all.bat

# 2. Настройка .env
copy .env.example backend\.env
# Откройте backend\.env и добавьте TELEGRAM_BOT_TOKEN

# 3. Запуск
cd backend && python create_db.py && cd .. && .\start-all.bat
```

### Docker (2 команды):

```bash
# 1. Настройка
copy .env.example .env
# Откройте .env и добавьте TELEGRAM_BOT_TOKEN

# 2. Запуск
docker-compose up -d
```

---

## 🌐 Доступ к приложению

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:5173 | Панель менеджера |
| Backend API | http://localhost:3001 | REST API |
| API Docs | http://localhost:3001/docs | Swagger UI |
| Telegram Bot | @ваш_бот | Поиск в Telegram |

---

## 🔧 Требования

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 16**

Или просто **Docker Desktop** 🐳

---

## 📦 Структура проекта

```
sulpakHelpDeskHelper/
├── backend/          # Python FastAPI + Telegram Bot
├── frontend/         # React + Vite
├── docs/            # 📚 Документация
├── start-all.bat    # 🚀 Запуск всего
└── README.md        # 📖 Этот файл
```

---

## 🛠️ Технологический стек

**Backend:** Python 3.11, FastAPI, python-telegram-bot, PostgreSQL (asyncpg)  
**Frontend:** React 18, Vite 4, Tailwind CSS 3  
**DevOps:** Docker, Docker Compose, Nginx

---

## 🐛 Проблемы?

Смотрите [docs/FAQ.md](docs/FAQ.md) или создайте issue.

---

## 📄 Лицензия

MIT License

