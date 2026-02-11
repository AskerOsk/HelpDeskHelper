@echo off
echo ================================
echo Установка Frontend зависимостей
echo ================================
echo.

cd frontend

echo Проверка Node.js...
node --version
if %errorlevel% neq 0 (
    echo ОШИБКА: Node.js не установлен!
    echo Скачайте Node.js 18+ с https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo Установка зависимостей...
npm install

echo.
echo ================================
echo Установка завершена успешно!
echo ================================
echo.
echo Для запуска: npm run dev
echo.
pause

