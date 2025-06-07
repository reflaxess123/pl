# 🐳 Запуск в Docker

Подробная инструкция по запуску Telegram Bot Web Manager в Docker контейнере.

## 🚀 Быстрый старт

### Windows:

```cmd
run-web-docker.bat
```

### Linux/Mac:

```bash
./run-web-docker.sh
```

После запуска откройте браузер: **http://localhost:8000**

## 📋 Ручной запуск

### 1. Подготовка

Убедитесь, что у вас есть файл `.env` с настройками:

```env
# ProxyAPI ключ
PROXY_API_KEY=your_api_key_here

# Telegram API credentials
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here

# Системный промпт (опционально)
SYSTEM_PROMPT=Твой системный промпт
```

### 2. Создание директорий

```bash
mkdir -p session_data
mkdir -p data
```

### 3. Сборка образа

```bash
docker-compose build pl-web
```

### 4. Запуск веб интерфейса

```bash
docker-compose --profile web up pl-web
```

### 5. Остановка

```bash
docker-compose --profile web down
```

## 🛠️ Доступные профили

### Веб интерфейс (рекомендуется):

```bash
docker-compose --profile web up pl-web
```

- Веб интерфейс на http://localhost:8000
- Управление ботом через браузер
- Автоответ и управление диалогами

### Только командная строка:

```bash
docker-compose --profile cli up pl-bot
```

- Только Telegram бот без веб интерфейса
- Команды @gpt в Telegram

### Режим разработки:

```bash
docker-compose --profile dev up pl-dev
```

- Интерактивный bash в контейнере
- Все файлы монтированы для разработки

## 📁 Структура данных

```
pl/
├── session_data/          # Сессии Telegram (сохраняются)
├── data/                  # Данные приложения (сохраняются)
├── .env                   # Настройки (обязательно)
└── session.session        # Основная сессия
```

## 🔧 Настройка портов

По умолчанию веб интерфейс доступен на порту 8000. Для изменения:

```bash
# Изменить в docker-compose.yml
ports:
  - "8080:8000"  # Внешний:Внутренний
```

Или через переменную окружения:

```bash
export WEB_PORT=8080
docker-compose --profile web up pl-web
```

## 🐛 Устранение проблем

### Порт уже занят:

```bash
# Проверить что использует порт 8000
netstat -tulpn | grep :8000

# Изменить порт в docker-compose.yml
```

### Проблемы с сессией:

```bash
# Удалить старые сессии
rm -rf session_data/*
rm session.session
```

### Проблемы с правами:

```bash
# Дать права на директории
sudo chown -R 1000:1000 session_data/
sudo chown -R 1000:1000 data/
```

### Логи контейнера:

```bash
# Просмотр логов
docker-compose logs pl-web

# Следить за логами в реальном времени
docker-compose logs -f pl-web
```

## 📊 Мониторинг

### Статус контейнера:

```bash
docker-compose ps
```

### Ресурсы:

```bash
docker stats pl-web-interface
```

### Войти в контейнер:

```bash
docker-compose exec pl-web bash
```

## 🔄 Обновление

```bash
# Остановить
docker-compose --profile web down

# Пересобрать образ
docker-compose build pl-web

# Запустить снова
docker-compose --profile web up pl-web
```

## 🌐 Доступ из сети

Для доступа с других устройств в сети измените в `docker-compose.yml`:

```yaml
ports:
  - "0.0.0.0:8000:8000"
```

Затем веб интерфейс будет доступен по IP сервера: `http://192.168.1.100:8000`

## 🔐 Безопасность

- Контейнер запускается от непривилегированного пользователя
- Порты открыты только локально по умолчанию
- Сессии и данные сохраняются в отдельных томах
- Нет лишних пакетов в образе

## 📝 Примеры команд

```bash
# Полный цикл
docker-compose build pl-web
docker-compose --profile web up -d pl-web
docker-compose logs -f pl-web

# Остановка и очистка
docker-compose --profile web down
docker system prune -f

# Бэкап данных
tar -czf backup.tar.gz session_data/ data/ .env
```
