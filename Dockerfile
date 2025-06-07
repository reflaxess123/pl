# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы конфигурации Poetry
COPY pyproject.toml poetry.lock ./

# Настраиваем Poetry чтобы не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Устанавливаем зависимости
RUN poetry install --only=main --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY pl/ ./pl/

# ВАЖНО: session.session будет смонтирован как volume в Coolify
# .env файл НЕ копируем - используем переменные окружения Coolify

# Копируем дополнительные файлы если они есть
COPY example.py debug_api.py ./

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Устанавливаем переменную окружения для Python
ENV PYTHONPATH=/app

# Порт по умолчанию (если приложение использует веб-сервер)
EXPOSE 8000

# Команда по умолчанию - показать help
CMD ["python", "-m", "pl.cli", "--help"] 