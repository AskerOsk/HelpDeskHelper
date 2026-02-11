@echo off
echo ================================
echo Установка Python зависимостей
echo ================================
echo.

cd backend

echo Проверка Python...
python --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Python не установлен!
    echo Скачайте Python 3.11+ с https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Установка зависимостей (системное окружение)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ================================
echo Установка завершена успешно!
echo ================================
echo.
echo Следующие шаги:
echo 1. Настройте .env файл (добавьте TELEGRAM_BOT_TOKEN)
echo 2. Инициализируйте БД: python create_db.py
echo 3. Запустите проект: ..\start-all.bat
echo.
echo Примечание: Зависимости установлены в системное окружение Python.
echo Если хотите использовать виртуальное окружение, см. README.md
echo.
pause

