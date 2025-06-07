#!/bin/bash

echo "========================================"
echo " Telegram Bot Web Manager - Docker"
echo "========================================"
echo

# Создаем директории если их нет
mkdir -p session_data
mkdir -p data

echo "🐳 Сборка Docker образа..."
docker-compose build pl-web

echo
echo "🚀 Запуск веб интерфейса..."
echo "🌐 Откройте в браузере: http://localhost:8000"
echo

docker-compose --profile web up pl-web 