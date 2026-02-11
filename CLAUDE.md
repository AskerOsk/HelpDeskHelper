# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sulpak HelpDesk System** - A customer support ticketing system with Telegram integration and a manager panel.

- **Backend**: Python FastAPI + Telegram Bot + PostgreSQL
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Database**: PostgreSQL 16
- **Deployment**: Docker Compose or local development

## Development Commands

### Initial Setup

**Local setup:**
```bash
# Install all dependencies (Windows)
.\install-all.bat

# Or install individually:
.\install-backend.bat  # Creates venv, installs Python deps
.\install-frontend.bat # Installs npm dependencies

# Initialize database (required before first run)
cd backend && python create_db.py && cd ..

# Configure environment
copy .env.example backend\.env
# Edit backend\.env and add TELEGRAM_BOT_TOKEN
```

**Docker setup:**
```bash
copy .env.example .env
# Edit .env and add TELEGRAM_BOT_TOKEN
docker-compose up -d
```

### Running the Application

**Local development:**
```bash
# Start all backend services at once
cd backend && python run_all.py

# Or start services individually (in separate terminals):
cd backend
python server.py   # API server on port 3001
python webhook.py  # Webhook server on port 3002
python bot.py      # Telegram bot

# Start frontend (separate terminal)
cd frontend
npm run dev        # Dev server on port 5173
```

**Docker:**
```bash
docker-compose up -d                    # Start all services
docker-compose logs -f backend          # View backend logs
docker-compose down                     # Stop all services
```

### Frontend Commands

```bash
cd frontend
npm run dev        # Start dev server (port 5173)
npm run build      # Build for production
npm run preview    # Preview production build
npm run lint       # Run ESLint
```

### Backend Commands

```bash
cd backend
python create_db.py           # Initialize/reset database
python run_all.py             # Start all backend services
python server.py              # Start API server only
python bot.py                 # Start Telegram bot only
python webhook.py             # Start webhook server only
```

## Architecture

### Three-Service Backend Architecture

The backend consists of three independent Python services that run concurrently:

1. **API Server** (`server.py`, port 3001)
   - FastAPI REST API for ticket and message management
   - Async PostgreSQL connection pool (asyncpg)
   - CORS enabled for frontend communication
   - Endpoints: `/api/tickets`, `/api/tickets/{id}`, `/api/tickets/{id}/messages`, etc.
   - Auto-initializes database tables on startup

2. **Webhook Server** (`webhook.py`, port 3002)
   - Separate FastAPI server for sending messages to Telegram users
   - Called by API server when manager sends a message
   - Uses Telegram Bot API to deliver messages
   - Handles both text and media (photos/videos)

3. **Telegram Bot** (`bot.py`)
   - Handles user interactions via Telegram
   - Manages user sessions and inline keyboards
   - Creates tickets and messages via API server (httpx)
   - Supports photo/video uploads from users

**Communication Flow:**
- User → Telegram Bot → API Server → Database
- Manager (Frontend) → API Server → Webhook Server → Telegram Bot → User
- Frontend polls API Server every 5s for tickets, 3s for messages

### Frontend Architecture

Single-page React application (`frontend/src/App.jsx`):
- Left panel: ticket list with filters and status badges
- Right panel: message thread with send functionality
- Real-time updates via polling (configurable intervals)
- Tailwind CSS for styling
- Direct API calls to backend (no state management library)

### Database Schema

**tickets table:**
- `id` (PK), `ticket_number` (unique), `telegram_user_id`, `telegram_username`
- `status` (new/in_progress/resolved/closed)
- `assigned_manager_id`, `created_at`, `updated_at`

**messages table:**
- `id` (PK), `ticket_id` (FK), `sender_type` (client/manager), `sender_id`, `content`
- `media_type` (photo/video/null), `media_url`, `media_file_id` (Telegram)
- `created_at`

**managers table:**
- `id` (PK), `name`, `telegram_id`, `active`

## Key Files and Their Roles

### Backend
- **constants.py** - Shared constants (statuses, sender types, timeouts, media types). Import from here, don't hardcode strings.
- **server.py** - Main REST API server with database connection pool management
- **bot.py** - Telegram bot with user session management and inline keyboard UI
- **webhook.py** - Webhook endpoint for delivering manager messages to Telegram
- **run_all.py** - Process manager that launches all three backend services in separate consoles (Windows)
- **create_db.py** - Database initialization script using psycopg2 (sync)

### Frontend
- **App.jsx** - Single component containing all UI and API logic
- **main.jsx** - React app entry point
- **index.css** - Tailwind base styles
- **vite.config.js** - Vite configuration (no special proxy needed)

## Important Patterns

### Backend Patterns

**Database connections:**
- API server uses async connection pool (`asyncpg.Pool`) stored in global `db_pool`
- Always use `async with db_pool.acquire() as conn` to get connections
- create_db.py uses sync `psycopg2` for initialization only

**Constants usage:**
```python
from constants import STATUS_NEW, SENDER_CLIENT, MIN_MESSAGE_LENGTH
# Never hardcode 'new', 'client', etc.
```

**Telegram Bot sessions:**
- User sessions stored in-memory dict `user_sessions[user_id]`
- Each session tracks `active_ticket_id`, `awaiting_clarification`, `original_message`

**Media handling:**
- Photos: `message.photo[-1]` (highest resolution)
- Videos: `message.video`
- Get file: `await context.bot.get_file(file_id)`
- Store: `media_type`, `media_url` (Telegram URL), `media_file_id` (for re-sending)

### Frontend Patterns

**Backend URL:**
```javascript
const BACKEND_URL = 'http://localhost:3001';
// Hardcoded in App.jsx, change here if needed
```

**Polling intervals:**
- Tickets: 5s (fetchTickets)
- Messages: 3s (fetchMessages)
- Intervals are cleared on unmount/dependency change

**API calls:**
```javascript
// Always use try/catch and console.error
try {
  const response = await fetch(`${BACKEND_URL}/api/...`);
  const data = await response.json();
} catch (error) {
  console.error('Error ...:', error);
}
```

## Environment Variables

Required in `backend/.env`:
```
TELEGRAM_BOT_TOKEN=<your_bot_token>    # Required
DB_USER=postgres                        # Default: postgres
DB_HOST=127.0.0.1                      # Default: 127.0.0.1
DB_NAME=sulpak_helpdesk                # Default: sulpak_helpdesk
DB_PASSWORD=postgres                    # Default: postgres
DB_PORT=5432                           # Default: 5432
BACKEND_URL=http://localhost:3001      # Default: http://localhost:3001
WEBHOOK_PORT=3002                      # Default: 3002
PORT=3001                              # API server port
```

## Service Ports

- **3001** - Backend API server (FastAPI)
- **3002** - Webhook server (FastAPI)
- **5173** - Frontend dev server (Vite)
- **5432** - PostgreSQL database
- **80** - Frontend production (Nginx in Docker)

## Testing the System

1. Start all services (backend + frontend)
2. Open http://localhost:5173 for manager panel
3. Open Telegram and message your bot
4. Create a ticket by sending a message (10+ characters)
5. See the ticket appear in manager panel
6. Reply from manager panel
7. Verify message arrives in Telegram

## Common Development Scenarios

**Adding a new ticket status:**
1. Add constant to `backend/constants.py`
2. Update status validation in `server.py` endpoints
3. Add status emoji/badge in `bot.py` and `App.jsx`

**Adding a new API endpoint:**
1. Add route to `server.py` with `@app.get/post/patch`
2. Use async/await with `async with db_pool.acquire()`
3. Return Pydantic models or plain dicts
4. Update CORS if needed (currently allows all origins)

**Modifying database schema:**
1. Update table creation in `server.py` `init_db()` function
2. Run `python create_db.py` to recreate tables
3. Update queries in affected endpoints
4. Consider adding migration script for production

**Adding Telegram bot commands:**
1. Add handler in `bot.py` (CommandHandler, MessageHandler, CallbackQueryHandler)
2. Register in `main()` function
3. Update inline keyboards if needed
4. Test in Telegram before deploying

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running on port 5432
- Verify credentials in `backend/.env`
- Run `python create_db.py` if tables don't exist

**Telegram bot not responding:**
- Check TELEGRAM_BOT_TOKEN in `.env`
- Verify bot is running (`python bot.py`)
- Check bot.py logs for errors

**Frontend can't connect to backend:**
- Ensure backend is running on port 3001
- Check CORS settings in `server.py`
- Verify BACKEND_URL in `App.jsx`

**Services won't start:**
- Check port conflicts (3001, 3002, 5173, 5432)
- On Windows, use individual Python terminals if `run_all.py` fails
- Check `backend/server.log` for errors