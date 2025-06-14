# Используем официальный Python образ как базовый
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry==1.8.3

# Настраиваем Poetry - не создавать виртуальное окружение
RUN poetry config virtualenvs.create false

# Копируем файлы конфигурации Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN poetry install --no-dev --no-interaction --no-ansi

# Копируем исходный код приложения
COPY pl/ ./pl/
COPY templates/ ./templates/
COPY start_web.py ./
COPY docker-start.py ./
COPY .env ./
COPY session.session ./

# Создаем директорию для данных
RUN mkdir -p /app/data

# Создаем пользователя для безопасности (не root)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Указываем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Открываем порт для веб интерфейса
EXPOSE 8000

# Точка входа по умолчанию - веб интерфейс
CMD ["python", "docker-start.py"] 