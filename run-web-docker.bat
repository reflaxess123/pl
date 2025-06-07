@echo off
echo ========================================
echo  Telegram Bot Web Manager - Docker
echo ========================================
echo.

REM Создаем директории если их нет
if not exist "session_data" mkdir session_data
if not exist "data" mkdir data

echo 🐳 Сборка Docker образа...
docker-compose build pl-web

echo.
echo 🚀 Запуск веб интерфейса...
echo 🌐 Откройте в браузере: http://localhost:8000
echo.

docker-compose --profile web up pl-web

pause 