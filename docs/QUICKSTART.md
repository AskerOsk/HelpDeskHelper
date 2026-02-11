# Быстрый старт

## ⚠️ Важно: Перед использованием Docker

Убедитесь, что **Docker Desktop запущен**:
1. Откройте Docker Desktop из меню Пуск
2. Дождитесь, пока иконка Docker в системном трее станет зелёной
3. Проверьте статус: `Get-Service com.docker.service` (должен быть "Running")

---

## Локальный запуск

1. **Установите PostgreSQL 16** и создайте базу данных:
   ```bash
   psql -U postgres
   CREATE DATABASE sulpak_helpdesk;
   \q
   ```

2. **Настройте переменные окружения:**
   ```bash
   copy .env.example backend\.env
   ```
   Откройте `backend\.env` и добавьте токен Telegram бота.

3. **Установите зависимости:**
   ```bash
   # Backend
   cd backend
   python -m pip install -r requirements.txt
   cd ..
   
   # Frontend
   cd frontend
   npm install
   cd ..
   ```
   
   Или используйте скрипт автоматической установки:
   ```bash
   .\install-all.bat
   ```

4. **Инициализируйте базу данных:**
   ```bash
   cd backend
   python create_db.py
   ```

5. **Запустите проект:**
   ```bash
   .\start-all.bat
   ```

Откроется 4 терминала. Готово!

---

## Запуск через Docker

1. **Настройте переменные окружения:**
   ```bash
   copy .env.example .env
   ```
   Откройте `.env` и добавьте токен Telegram бота.

2. **Запустите Docker:**
   ```bash
   docker-compose up -d
   ```

Все сервисы запустятся автоматически!

---

## Доступ

- **Frontend (панель менеджера):** http://localhost:5173 (dev) или http://localhost (docker)
- **Backend API:** http://localhost:3001
- **Telegram Bot:** Найдите в Telegram и отправьте `/start`

---

Подробная документация в [README.md](../README.md)

