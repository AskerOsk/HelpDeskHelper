@echo off
echo ===============================================
echo  Sulpak HelpDesk - Полная установка проекта
echo ===============================================
echo.

echo [1/3] Проверка требований...
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python не установлен!
    echo     Скачайте Python 3.11+ с https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
) else (
    python --version
    echo [+] Python установлен
)

REM Проверка Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Node.js не установлен!
    echo     Скачайте Node.js 18+ с https://nodejs.org/
    echo.
    pause
    exit /b 1
) else (
    node --version
    echo [+] Node.js установлен
)

REM Проверка PostgreSQL
psql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] PostgreSQL не найден в PATH
    echo     Убедитесь, что PostgreSQL 16 установлен
) else (
    psql --version
    echo [+] PostgreSQL установлен
)

echo.
echo [2/3] Установка Backend (Python)...
echo.
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
cd ..
echo [+] Backend зависимости установлены

echo.
echo [3/3] Установка Frontend (Node.js)...
echo.
cd frontend
call npm install --silent
cd ..
echo [+] Frontend зависимости установлены

echo.
echo ===============================================
echo  Уст��новка завершена успешно!
echo ===============================================
echo.
echo Следующие шаги:
echo.
echo 1. Настройте .env файл:
echo    copy .env.example backend\.env
echo    Добавьте TELEGRAM_BOT_TOKEN
echo.
echo 2. Инициализируйте базу данных:
echo    cd backend
echo    python create_db.py
echo.
echo 3. Запустите проект:
echo    .\start-all.bat
echo.
echo ===============================================
pause

