# Структура проекта Sulpak HelpDesk

## 📂 Корневая директория

```
sulpakHelpDeskHelper/
├── backend/                    # Backend приложение
├── frontend/                   # Frontend приложение
├── .dockerignore              # Исключения для Docker
├── .env.example               # Пример переменных окружения
├── .gitignore                 # Исключения для Git
├── docker-compose.yml         # Docker Compose конфигурация
├── Dockerfile.backend         # Docker образ для backend
├── Dockerfile.frontend        # Docker образ для frontend
├── nginx.conf                 # Nginx конфигурация для production
├── QUICKSTART.md             # Быстрый старт
├── README.md                  # Основная документация
└── start-all.bat             # Скрипт запуска для Windows
```

## 📂 Backend (Python + FastAPI + PostgreSQL)

```
backend/
├── server.py                 # FastAPI REST API сервер
├── bot.py                    # Telegram Bot (python-telegram-bot)
├── webhook.py                # Webhook сервер для отправки сообщений
├── create_db.py              # Скрипт инициализации БД
├── run_all.py                # Запуск всех сервисов
├── requirements.txt          # Python зависимости
└── .env                      # Переменные окружения (НЕ В GIT!)
```

### Основные компоненты Backend:

**server.py** - FastAPI REST API сервер:
- REST API endpoints для работы с тикетами
- Async подключение к PostgreSQL (asyncpg)
- CORS настройки
- Webhook интеграция с Telegram
- Порт: 3001

**bot.py** - Telegram Bot:
- Обработка команд от пользователей (python-telegram-bot)
- Управление сессиями
- Inline клавиатуры
- Интеграция с Backend API через httpx

**webhook.py** - Webhook сервер:
- FastAPI сервер для отправки сообщений в Telegram
- Endpoint для менеджеров
- Порт: 3002

**create_db.py** - Инициализация базы данных:
- Создание базы данных sulpak_helpdesk
- Psycopg2 для работы с PostgreSQL

**run_all.py** - Запуск всех сервисов:
- Одновременный запуск server.py, webhook.py, bot.py
- Управление процессами

## 📂 Frontend (React + Vite + Tailwind CSS)

```
frontend/
├── public/                    # Статические файлы
│   └── vite.svg
├── src/                      # Исходный код
│   ├── assets/              # Изображения и медиа
│   │   └── react.svg
│   ├── App.jsx              # Главный компонент приложения
│   ├── main.jsx             # Entry point
│   └── index.css            # Tailwind CSS стили
├── index.html               # HTML template
├── package.json             # Зависимости frontend
├── vite.config.js          # Конфигурация Vite
├── tailwind.config.js      # Конфигурация Tailwind
├── postcss.config.js       # PostCSS конфигурация
└── .eslintrc.cjs           # ESLint правила
```

### Основные компоненты Frontend:

**App.jsx** - Главный компонент:
- Панель управления тикетами
- Список тикетов (левая панель)
- Чат с клиентом (правая панель)
- Управление статусами

**main.jsx** - Entry point:
- Инициализация React приложения
- Подключение стилей

**index.css** - Стили:
- Tailwind CSS базовые стили
- Кастомные стили компонентов

## 🗄️ База данных (PostgreSQL)

### Таблицы:

**tickets** - Обращения клиентов:
- id (PK)
- ticket_number (уникальный номер)
- telegram_user_id
- telegram_username
- status (new, in_progress, resolved, closed)
- assigned_manager_id
- created_at, updated_at

**messages** - Сообщения в тикетах:
- id (PK)
- ticket_id (FK)
- sender_type (user/manager)
- sender_id
- content
- media_type (photo/video)
- media_url (Telegram file URL)
- media_file_id (Telegram file_id)
- created_at

**managers** - Менеджеры поддержки:
- id (PK)
- name
- telegram_id
- active

## 🐳 Docker конфигурация

### docker-compose.yml
Orchestration трех сервисов:
- **postgres** - База данных PostgreSQL 16
- **backend** - Node.js сервер + Telegram Bot
- **frontend** - React приложение с Nginx

### Dockerfile.backend
- Base: node:18-alpine
- Запускает server.js и bot.js параллельно
- Порты: 3001, 3002

### Dockerfile.frontend
- Multi-stage build
- Stage 1: Сборка React приложения (node:18-alpine)
- Stage 2: Nginx для раздачи статики (nginx:alpine)
- Порт: 80

### nginx.conf
- Раздача статических файлов
- Proxy API запросов к backend
- SPA routing (try_files)

## 🔧 Конфигурационные файлы

**.env.example** - Шаблон переменных окружения
**.dockerignore** - Исключения для Docker build
**.gitignore** - Исключения для Git (node_modules, .env, logs)
**start-all.bat** - Windows скрипт для запуска всех сервисов

## 📝 Документация

**README.md** - Основная документация:
- Архитектура системы
- Инструкции по установке
- Локальный запуск и Docker
- API документация
- Troubleshooting

**QUICKSTART.md** - Быстрый старт для разработчиков

## 🔐 Безопасность

**Файлы не в Git:**
- `.env` - токены и пароли
- `node_modules/` - зависимости
- `*.log` - логи
- `.idea/` - IDE настройки

## 🚀 Порты

- **3001** - Backend API
- **3002** - Telegram Webhook
- **5173** - Frontend Dev Server (Vite)
- **80** - Frontend Production (Nginx)
- **5432** - PostgreSQL

## 📊 Технологический стек

**Backend:**
- Python 3.11+
- FastAPI 0.109
- PostgreSQL 16
- asyncpg (async PostgreSQL driver)
- python-telegram-bot 20.7
- httpx (async HTTP client)
- pydantic, uvicorn

**Frontend:**
- React 18
- Vite 4
- Tailwind CSS 3

**DevOps:**
- Docker & Docker Compose
- Nginx

