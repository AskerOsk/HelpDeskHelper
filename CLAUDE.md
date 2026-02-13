# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Sulpak AI HelpDesk System** - An AI-powered customer support system with Telegram integration and monitoring dashboard.

- **Backend**: Python FastAPI + Telegram Bot + Claude AI + PostgreSQL + Email notifications
- **Frontend**: React 18 + Vite + Tailwind CSS (Modern dark theme: Black, Neon Green, Orange)
- **Database**: PostgreSQL 16
- **Deployment**: Docker Compose or local development

## Core Logic (NEW ARCHITECTURE)

### AI-First Approach

**User Flow:**
1. User sends message via Telegram Bot
2. Message stored in database and displayed in monitoring UI
3. **Claude AI** (via Anthropic API) processes the request and provides assistance
4. Full conversation history maintained between User ↔ AI
5. When conversation reaches resolution point, AI generates structured email summary
6. Email sent to managers (currently: asker.kaudinov's Claude account email)

**Key Changes from Previous Version:**
- ❌ No manager chat interface - removed manual manager responses
- ✅ AI handles all user interactions autonomously
- ✅ UI becomes read-only monitoring dashboard (not chat interface)
- ✅ Email notifications replace manual manager involvement
- ✅ AI decides when to escalate (sends email with full context)

### Email Integration

**When AI sends email:**
- Conversation deemed complete or requires human escalation
- Email template includes: ticket number, user info, full chat history, AI summary
- Recipient: Manager email (configurable in `.env`)
- Format: HTML email with styled ticket information

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
# Edit backend\.env and add:
# - TELEGRAM_BOT_TOKEN (from @BotFather)
# - USE_OLLAMA=true (for local AI)
# - SMTP credentials (for email notifications)

# Install and setup Ollama (for local AI)
# See docs/OLLAMA_SETUP.md for detailed instructions
# Quick start:
#   1. Download from https://ollama.com/download
#   2. Install Ollama
#   3. Run: ollama pull llama3.2:latest
#   4. Verify: ollama ps
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

### AI-Powered Backend Architecture

The backend consists of four independent Python services:

1. **API Server** (`server.py`, port 3001)
   - FastAPI REST API for ticket and message management
   - Async PostgreSQL connection pool (asyncpg)
   - CORS enabled for frontend communication
   - **Claude AI Integration** - processes user messages and generates responses
   - **Email Service** - sends notifications to managers
   - Endpoints: `/api/v1/tickets`, `/api/v1/ai/respond`, `/api/v1/notify`, etc.
   - Auto-initializes database tables on startup

2. **Webhook Server** (`webhook.py`, port 3002)
   - Separate FastAPI server for sending AI responses to Telegram users
   - Called by API server after AI generates response
   - Uses Telegram Bot API to deliver messages
   - Handles both text and media (photos/videos)

3. **Telegram Bot** (`bot.py`)
   - Handles user interactions via Telegram
   - Manages user sessions and inline keyboards
   - Creates tickets and forwards to AI via API server (httpx)
   - Supports photo/video uploads from users
   - No manual manager interaction - all responses from AI

4. **AI Service** (integrated in `server.py` or separate `ai_service.py`)
   - Uses Anthropic Claude API for intelligent responses
   - Context-aware: reads full conversation history
   - Generates responses in Russian for Sulpak customers
   - Decides when to escalate (trigger email notification)
   - Maintains conversation state and context

**Communication Flow (NEW):**
- User → Telegram Bot → API Server → Database → AI Service → Webhook → User
- AI Service → Email Service → Manager (when escalation needed)
- Frontend (read-only) ← API Server ← Database (monitoring only)

### Frontend Architecture (NEW DESIGN)

**Monitoring Dashboard** (`frontend/src/App.jsx`):
- **Modern Dark Theme**: Black (#000000), Neon Green (#00FF41), Orange (#FF6B35)
- **Read-only interface** - no message sending, only monitoring
- **Left panel**: Ticket list with status indicators and AI activity badges
- **Right panel**: Full conversation history (User ↔ AI)
- Real-time updates via polling (5s for tickets, 3s for messages)
- No authentication required (monitoring dashboard)
- Glassmorphism effects, gradients, and modern UI components
- Direct API calls to backend (no state management library)

### Database Schema

**tickets table:**
- `id` (PK), `ticket_number` (unique), `telegram_user_id`, `telegram_username`
- `status` (new/ai_processing/resolved/escalated)
- `ai_summary` TEXT - AI-generated summary of conversation
- `escalated_at` TIMESTAMP - when email was sent to manager
- `created_at`, `updated_at`

**messages table:**
- `id` (PK), `ticket_id` (FK), `sender_type` (user/ai), `sender_id`, `content`
- `media_type` (photo/video/null), `media_url`, `media_file_id` (Telegram)
- `ai_confidence` FLOAT - AI confidence score (0-1)
- `created_at`

**managers table:** (kept for email configuration)
- `id` (PK), `name`, `email`, `active`
- Note: No telegram_id needed, managers use email only

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
# Telegram
TELEGRAM_BOT_TOKEN=<your_bot_token>    # Required

# Claude AI
ANTHROPIC_API_KEY=<your_api_key>       # Required for AI responses
CLAUDE_MODEL=claude-sonnet-4-5-20250929 # Default model

# Email (for manager notifications)
SMTP_HOST=smtp.gmail.com               # SMTP server
SMTP_PORT=587                          # SMTP port
SMTP_USERNAME=<your_email>             # Sender email
SMTP_PASSWORD=<your_app_password>      # App-specific password
MANAGER_EMAIL=asker.kaudinov@anthropic.com # Recipient for escalations

# Database
DB_USER=postgres                        # Default: postgres
DB_HOST=127.0.0.1                      # Default: 127.0.0.1
DB_NAME=sulpak_helpdesk                # Default: sulpak_helpdesk
DB_PASSWORD=postgres                    # Default: postgres
DB_PORT=5432                           # Default: 5432

# Backend
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

**AI not responding:**
- Check ANTHROPIC_API_KEY in `.env`
- Verify API key is valid at console.anthropic.com
- Check rate limits and usage quota
- Review `server.log` for AI service errors

**Email notifications not working:**
- Verify SMTP credentials in `.env`
- For Gmail: enable 2FA and create App Password
- Check SMTP_PORT (587 for TLS, 465 for SSL)
- Test email sending with Python SMTP test script

---

## Development Roadmap

### Phase 1: AI Integration ✅ (Current)

**Goal:** Replace manual manager responses with AI-powered assistance

- ✅ Integrate Anthropic Claude API
- ✅ AI processes user messages and generates responses
- ✅ Full conversation context maintained
- ✅ Email notifications when escalation needed
- ✅ Update UI to read-only monitoring dashboard
- ✅ Modern dark theme (Black, Neon Green, Orange)

**Deliverables:**
- AI service integrated in backend
- Email notification system
- New monitoring UI design
- Updated database schema (`sender_type: ai`, `status: escalated`)

---

### Phase 2: Enhanced AI Capabilities (Next Priority)

**Goal:** Improve AI intelligence and decision-making

**2.1 Smart Categorization & Routing**
- [ ] AI auto-categorizes tickets (delivery, payment, product, technical)
- [ ] Priority detection (urgent/high/medium/low) based on sentiment
- [ ] Auto-tagging system (refund, warranty, order_status, etc.)
- [ ] Smart routing to appropriate manager email based on category

**2.2 Context-Aware Responses**
- [ ] Knowledge base integration (FAQ, product info, policies)
- [ ] Order lookup from database (integrate with Sulpak ERP/1C)
- [ ] User history analysis (previous tickets, purchases)
- [ ] Personalized responses based on customer profile

**2.3 Sentiment Analysis**
- [ ] Detect frustrated/angry customers → auto-escalate immediately
- [ ] Track sentiment throughout conversation
- [ ] Alert managers when sentiment drops below threshold
- [ ] Generate empathy-enhanced responses for negative sentiment

**2.4 Quality Assurance**
- [ ] AI confidence scoring (low confidence → escalate)
- [ ] Response quality metrics (helpfulness, clarity, accuracy)
- [ ] A/B testing different AI prompts
- [ ] Manager feedback loop (mark responses as good/bad)

**Deliverables:**
- Enhanced AI prompt templates
- Knowledge base database table
- Sentiment analysis module
- Analytics dashboard for AI performance

---

### Phase 3: Omnichannel Expansion

**Goal:** Support multiple communication channels

**3.1 WhatsApp Integration**
- [ ] WhatsApp Business API setup
- [ ] Unified message handling (Telegram + WhatsApp)
- [ ] Same AI handles both channels
- [ ] Channel indicator in monitoring UI

**3.2 Email Support**
- [ ] Receive tickets via email
- [ ] AI responds via email thread
- [ ] Parse email content and attachments
- [ ] Maintain email formatting in responses

**3.3 Website Chat Widget**
- [ ] Embeddable widget for sulpak.kz
- [ ] WebSocket real-time communication
- [ ] Same backend, different frontend
- [ ] Session persistence across page navigation

**3.4 Instagram Direct Messages**
- [ ] Instagram Graph API integration
- [ ] Handle DMs and comments
- [ ] Auto-respond to common queries
- [ ] Escalate complex issues

**Deliverables:**
- Multi-channel message broker
- Unified ticket interface (channel-agnostic)
- Channel-specific adapters (Telegram, WhatsApp, Email, Web, Instagram)
- Updated monitoring UI with channel filters

---

### Phase 4: Analytics & Business Intelligence

**Goal:** Data-driven insights for management

**4.1 Real-Time Dashboard**
- [ ] KPI cards: active tickets, resolution time, AI success rate
- [ ] Live conversation stream
- [ ] Sentiment heatmap (hourly/daily)
- [ ] Category distribution charts

**4.2 Manager Performance Reports**
- [ ] Average resolution time per manager
- [ ] Escalation rate trends
- [ ] Customer satisfaction scores (CSAT)
- [ ] AI vs Human performance comparison

**4.3 Customer Insights**
- [ ] Most common issues (word cloud)
- [ ] Peak support hours
- [ ] User satisfaction trends
- [ ] Product-specific complaint analysis

**4.4 Predictive Analytics**
- [ ] Predict ticket volume based on time/season
- [ ] Identify potential churn customers
- [ ] Suggest proactive outreach
- [ ] Forecast staffing needs

**Deliverables:**
- Analytics backend service
- Chart.js / D3.js visualizations
- Export reports (CSV, PDF)
- Email digest for managers (daily/weekly summary)

---

### Phase 5: Advanced Automation

**Goal:** Maximum efficiency through intelligent automation

**5.1 Automated Workflows**
- [ ] Auto-close tickets after X days of inactivity
- [ ] Follow-up messages (e.g., "Is your issue resolved?")
- [ ] Scheduled reminders for pending actions
- [ ] Bulk operations (close all resolved tickets)

**5.2 Self-Service Portal**
- [ ] Customer web portal (check ticket status)
- [ ] FAQ database with AI-powered search
- [ ] Order tracking integration
- [ ] Submit tickets via web form

**5.3 Voice Support**
- [ ] Telegram voice message transcription (Whisper API)
- [ ] AI responds to transcribed voice
- [ ] Text-to-speech for AI responses (optional)

**5.4 Proactive Support**
- [ ] Monitor Sulpak website for out-of-stock products → notify users
- [ ] Delivery delays → auto-notify customers with apology
- [ ] Order status updates → proactive messages
- [ ] Birthday greetings with discount codes

**Deliverables:**
- Task scheduler (Celery + Redis)
- Voice transcription service
- Customer portal frontend
- Proactive notification engine

---

### Phase 6: Enterprise Features

**Goal:** Scale to full enterprise support system

**6.1 Authentication & RBAC**
- [ ] JWT-based authentication for managers
- [ ] Role-based access control (admin, manager, viewer)
- [ ] Manager assignment per ticket
- [ ] Audit log (who did what, when)

**6.2 Integration Ecosystem**
- [ ] 1C / ERP integration (order data, inventory)
- [ ] CRM integration (customer profiles, purchase history)
- [ ] Payment gateway (refund processing)
- [ ] Loyalty program (bonus points lookup)

**6.3 Multi-Language Support**
- [ ] Kazakh language support
- [ ] Auto-detect user language
- [ ] AI responds in user's language
- [ ] UI language switcher

**6.4 Mobile App for Managers**
- [ ] React Native app (iOS + Android)
- [ ] Push notifications for urgent tickets
- [ ] Quick response templates
- [ ] Offline mode (draft responses)

**6.5 SLA Management**
- [ ] Define SLA rules per category (respond in 5min, resolve in 24h)
- [ ] Auto-escalate if SLA breached
- [ ] SLA compliance dashboard
- [ ] Penalty alerts for management

**Deliverables:**
- JWT authentication service
- Integration API layer
- Mobile app (React Native)
- SLA monitoring engine

---

### Phase 7: AI Evolution

**Goal:** Cutting-edge AI capabilities

**7.1 Multi-Modal AI**
- [ ] Image recognition (identify products from photos)
- [ ] Video analysis (detect damaged products)
- [ ] Audio sentiment analysis (from voice messages)
- [ ] OCR for documents (receipts, invoices)

**7.2 Advanced NLP**
- [ ] Intent detection (return, complaint, question, praise)
- [ ] Entity extraction (order number, product name, date)
- [ ] Conversation summarization (auto-generate ticket summary)
- [ ] Multi-turn dialogue management

**7.3 Continuous Learning**
- [ ] Fine-tune Claude on Sulpak-specific data
- [ ] Learn from manager corrections
- [ ] A/B test different response strategies
- [ ] Reinforcement learning from customer feedback

**7.4 AI Copilot Mode (Hybrid)**
- [ ] AI drafts response, manager approves/edits
- [ ] Suggested actions for managers
- [ ] Auto-complete for manager typing
- [ ] Smart reply suggestions

**Deliverables:**
- Multi-modal AI pipeline
- Fine-tuning data pipeline
- Hybrid UI (AI + Human collaboration)
- ML model versioning and deployment

---

## Prioritized Implementation Order

### 🔴 **P0 - Critical (Do First)**
1. Phase 1: AI Integration ← **CURRENT**
2. Phase 2.1: Smart Categorization
3. Phase 2.2: Context-Aware Responses
4. Phase 4.1: Real-Time Dashboard

### 🟡 **P1 - High Priority (Next 3 Months)**
5. Phase 2.3: Sentiment Analysis
6. Phase 3.1: WhatsApp Integration
7. Phase 4.2: Manager Performance Reports
8. Phase 5.1: Automated Workflows

### 🟢 **P2 - Medium Priority (Next 6 Months)**
9. Phase 3.3: Website Chat Widget
10. Phase 5.2: Self-Service Portal
11. Phase 6.1: Authentication & RBAC
12. Phase 6.2: ERP/CRM Integration

### 🔵 **P3 - Low Priority (Future)**
13. Phase 3.2: Email Support
14. Phase 3.4: Instagram DMs
15. Phase 5.3: Voice Support
16. Phase 6.4: Mobile App
17. Phase 7: Advanced AI Capabilities

---

## Success Metrics

**Current Baseline (Manual System):**
- Average response time: ~10 minutes (during business hours)
- Resolution rate: ~70% (30% require escalation)
- Manager capacity: ~20 tickets/day per manager
- Customer satisfaction: Unknown (no tracking)

**Target with AI (Phase 1-2):**
- Average response time: <30 seconds (AI instant response)
- Resolution rate: ~85% (AI handles common issues)
- Manager capacity: ~50 tickets/day (only escalated cases)
- Customer satisfaction: >4.0/5.0 (CSAT tracking)

**Long-Term Goals (Phase 3-7):**
- 24/7 availability across all channels
- 95% resolution rate (AI + automation)
- <1 minute average response time
- Customer satisfaction: >4.5/5.0
- 80% reduction in manager workload
- Support cost per ticket: -60%

---

## Technology Stack Evolution

**Current (Phase 1):**
```
Backend: FastAPI + PostgreSQL + Anthropic Claude + SMTP
Frontend: React + Vite + Tailwind CSS
Bot: python-telegram-bot
Deployment: Docker Compose
```

**Future (Phase 7):**
```
Backend: FastAPI + PostgreSQL + Redis + Celery + Kafka
AI: Anthropic Claude + Whisper + Fine-tuned models
Frontend: React + WebSocket + Chart.js + Next.js
Mobile: React Native
Integrations: 1C API + CRM + Payment gateways
Monitoring: Prometheus + Grafana + Sentry
Deployment: Kubernetes + CI/CD (GitHub Actions)
```

---

## Contributing Guidelines

When adding new features:

1. **Update CLAUDE.md** - Document new endpoints, environment variables, patterns
2. **Add to constants.py** - Never hardcode strings, use constants
3. **Database migrations** - Use Alembic migrations (don't recreate tables)
4. **AI prompts** - Store in separate `prompts/` directory, version controlled
5. **Tests** - Add unit tests (pytest) and integration tests
6. **Logging** - Use structured logging (JSON format for production)
7. **Error handling** - Always catch exceptions, log, and return friendly errors
8. **API versioning** - Use `/api/v1/`, `/api/v2/` for breaking changes
9. **Documentation** - Update README.md, add JSDoc/docstrings
10. **Code review** - Run ESLint, Black formatter, type checks before commit

---

## Notes

- Manager email is currently set to: `asker.kaudinov@anthropic.com` (configurable in `.env`)
- AI uses Russian language for responses by default (Sulpak customer base)
- Modern UI color scheme: Black (#000000), Neon Green (#00FF41), Orange (#FF6B35)
- Frontend is read-only monitoring dashboard (no message sending from UI)
- All user interactions handled by AI autonomously
- Managers only receive email notifications for escalated cases