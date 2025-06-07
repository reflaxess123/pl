# Развертывание ProxyAPI GPT утилиты в Docker

## Подготовка

Убедитесь, что у вас есть:

- Docker и Docker Compose установлены
- Файл `session.session` в корне проекта
- Настроенный файл `.env` с вашими API ключами

## Быстрый запуск

### 1. Сборка образа

```bash
docker build -t pl-app .
```

### 2. Запуск Telegram бота (по умолчанию)

```bash
docker-compose up -d
```

## Различные режимы запуска

### Telegram Bot (обычный)

```bash
# Через Docker Compose
docker-compose up -d

# Или напрямую через Docker
docker run -d --name pl-telegram \
  -v $(pwd)/session.session:/app/session.session \
  -v $(pwd)/.env:/app/.env \
  pl-app python -m pl.cli telegram
```

### Telegram Bot (расширенный)

```bash
# Измените команду в docker-compose.yml:
# command: ["python", "-m", "pl.cli", "telegram", "--advanced"]

docker-compose up -d
```

### Интерактивный чат

```bash
# Через Docker Compose профиль
docker-compose --profile interactive up pl-interactive

# Или напрямую
docker run -it --rm \
  -v $(pwd)/session.session:/app/session.session \
  -v $(pwd)/.env:/app/.env \
  pl-app python -m pl.cli chat
```

### Проверка баланса

```bash
docker run --rm \
  -v $(pwd)/.env:/app/.env \
  pl-app python -m pl.cli balance
```

### Одиночный запрос

```bash
docker run --rm \
  -v $(pwd)/.env:/app/.env \
  pl-app python -m pl.cli ask "Объясни что такое Docker"
```

## Управление контейнерами

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Логи в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs pl-app
```

### Остановка и запуск

```bash
# Остановить
docker-compose down

# Запустить заново
docker-compose up -d

# Перезапустить
docker-compose restart
```

### Вход в контейнер для отладки

```bash
docker exec -it pl_application /bin/bash
```

## Обновление

### 1. Остановить контейнеры

```bash
docker-compose down
```

### 2. Пересобрать образ

```bash
docker build -t pl-app . --no-cache
```

### 3. Запустить заново

```bash
docker-compose up -d
```

## Мониторинг

### Проверка статуса

```bash
docker-compose ps
```

### Использование ресурсов

```bash
docker stats pl_application
```

## Особенности работы с session.session

Файл `session.session` монтируется как volume, что позволяет:

- Сохранять сессию между перезапусками контейнера
- Обновлять сессию без пересборки образа
- Делиться сессией между несколькими контейнерами

**Важно:** Убедитесь, что файл `session.session` существует перед запуском, иначе контейнер может не запуститься или Telegram бот потребует повторной авторизации.

## Переменные окружения

Основные переменные в `.env`:

- `PROXY_API_KEY` - ключ ProxyAPI
- `TELEGRAM_API_ID` - ID приложения Telegram
- `TELEGRAM_API_HASH` - хеш приложения Telegram
- `TELEGRAM_PHONE` - номер телефона
- `SYSTEM_PROMPT` - системный промпт для GPT

## Решение проблем

### Контейнер не запускается

1. Проверьте существование файлов `session.session` и `.env`
2. Проверьте права доступа к файлам
3. Убедитесь, что порты не заняты

### Проблемы с Telegram

1. Проверьте корректность данных в `.env`
2. Убедитесь, что файл `session.session` актуален
3. При необходимости удалите `session.session` для повторной авторизации

### Ошибки API

1. Проверьте баланс аккаунта ProxyAPI
2. Убедитесь в корректности API ключа
3. Проверьте доступность интернета в контейнере
