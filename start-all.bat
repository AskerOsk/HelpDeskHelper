@echo off
echo ===============================================
echo   Sulpak HelpDesk - Starting All Services (Python)
echo ===============================================
echo.

REM Check Python dependencies
echo [0/5] Checking Python dependencies...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [!] Python dependencies not installed!
    echo.
    echo Installing dependencies...
    cd backend
    python -m pip install -r requirements.txt --quiet
    cd ..
    echo [+] Dependencies installed
    echo.
)

REM Kill existing processes
echo [1/5] Stopping existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3001" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3002" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
timeout /t 1 /nobreak >nul

echo [2/5] Starting Backend API Server...
cd backend
start "Backend API" cmd /k "python server.py"
cd ..

timeout /t 3 /nobreak >nul

echo [3/5] Starting Webhook Server...
cd backend
start "Webhook Server" cmd /k "python webhook.py"
cd ..

timeout /t 2 /nobreak >nul

echo [4/5] Starting Telegram Bot...
cd backend
start "Telegram Bot" cmd /k "python bot.py"
cd ..

timeout /t 2 /nobreak >nul

echo [5/5] Starting Frontend...
cd frontend
start "Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===============================================
echo   All Services Started Successfully!
echo ===============================================
echo.
echo   Backend API:    http://localhost:3001
echo   Bot Webhook:    http://localhost:3002
echo   Frontend UI:    http://localhost:5173
echo.
echo   Press Ctrl+C in each window to stop services
echo ===============================================
echo.
pause

