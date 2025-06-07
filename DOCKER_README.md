# Docker инструкция для PL Telegram Bot

## Быстрый старт

### 1. Сборка образа

```bash
docker build -t pl-bot .
```

### 2. Запуск с помощью Docker Compose

#### Для продакшена (автоматический запуск бота):

```bash
docker-compose --profile production up -d
```

#### Для разработки (интерактивный режим):

```bash
docker-compose --profile dev up -it
```

### 3. Прямой запуск Docker контейнера

#### Запуск Telegram бота:

```bash
docker run -it --rm \
  --env-file .env \
  -v "%cd%\session_data:/app/session_data" \
  pl-bot
```

#### Интерактивный чат:

```bash
docker run -it --rm \
  --env-file .env \
  pl-bot python -m pl.cli chat
```

#### Проверка баланса:

```bash
docker run -it --rm \
  --env-file .env \
  pl-bot python -m pl.cli balance
```

#### Одиночный запрос:

```bash
docker run -it --rm \
  --env-file .env \
  pl-bot python -m pl.cli ask "Привет, как дела?"
```

## Команды управления

### Просмотр логов:

```bash
docker-compose --profile production logs -f pl-bot
```

### Остановка контейнеров:

```bash
docker-compose --profile production down
```

### Перезапуск:

```bash
docker-compose --profile production restart pl-bot
```

### Очистка всех контейнеров и образов:

```bash
docker-compose down --rmi all --volumes --remove-orphans
```

## Полезные команды

### Подключение к работающему контейнеру:

```bash
docker exec -it pl-telegram-bot /bin/bash
```

### Просмотр статуса контейнеров:

```bash
docker ps
```

### Просмотр использования ресурсов:

```bash
docker stats pl-telegram-bot
```

## Переменные окружения

Убедитесь, что файл `.env` содержит все необходимые переменные:

- `PROXY_API_KEY` - API ключ для ProxyAPI
- `TELEGRAM_API_ID` - ID приложения Telegram
- `TELEGRAM_API_HASH` - Hash приложения Telegram
- `TELEGRAM_PHONE` - Номер телефона для Telegram
- `SYSTEM_PROMPT` - Системный промпт для ботa

## Примечания

1. При первом запуске Telegram бота вам может потребоваться ввести код подтверждения
2. Сессионные данные сохраняются в папке `session_data/`
3. Контейнер автоматически перезапускается при сбоях (restart: unless-stopped)
4. Для Windows используйте `"%cd%"` вместо `$(pwd)` в командах Docker
