# 🚀 Быстрый старт - 3 шага

## ⚡ Установка за 3 минуты

### Шаг 1: Установите всё
```bash
.\install-all.bat
```

### Шаг 2: Настройте .env
```bash
copy .env.example backend\.env
```
Откройте `backend\.env` и добавьте ваш `TELEGRAM_BOT_TOKEN`

### Шаг 3: Создайте БД и запустите
```bash
cd backend
python create_db.py
cd ..
.\start-all.bat
```

## 🎉 Готово!

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:3001
- **API Docs:** http://localhost:3001/docs

---

## 📚 Полная документация

- [README.md](../README.md) - Главная страница проекта
- [QUICKSTART.md](QUICKSTART.md) - Детальная инструкция
- [FAQ.md](FAQ.md) - Решение проблем
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Архитектура проекта

---

## 🔧 Требования

- Python 3.11+
- Node.js 18+
- PostgreSQL 16

---

## 🐳 Docker (альтернатива)

```bash
docker-compose up -d
```

Всё запустится автоматически!

