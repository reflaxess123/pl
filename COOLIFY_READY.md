# ✅ Проект готов для Coolify!

## 📋 Что готово:

### Основные файлы

- ✅ `Dockerfile` - оптимизирован для Coolify
- ✅ `docker-compose.yml` - для локального тестирования
- ✅ `.dockerignore` - исключает секретные файлы
- ✅ `.env.example` - пример переменных окружения

### Протестировано

- ✅ Docker образ собирается успешно
- ✅ GPT запросы работают
- ✅ Telegram бот запускается

## 🚀 Деплой на Coolify

### 1. Создайте приложение в Coolify

- **Build Pack:** Dockerfile
- **Start Command:** `python -m pl.cli telegram`

### 2. Добавьте переменные окружения:

```
PROXY_API_KEY = [ваш ключ]
TELEGRAM_API_ID = [ваш ID]
TELEGRAM_API_HASH = [ваш hash]
TELEGRAM_PHONE = [ваш телефон]
SYSTEM_PROMPT = Ты - персональный ассистент пользователя в Telegram. Работай от его имени, отвечай кратко и по делу.
```

### 3. Настройте хранилище для session.session:

- **Storage Type:** File
- **Mount Path:** `/app/session.session`
- **Upload your session.session file**

### 4. Деплой

Нажмите "Deploy" и следите за логами!

## 📁 Файлы для загрузки в Git

Убедитесь что в репозитории есть:

- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `.env.example`
- `pyproject.toml`
- `poetry.lock`
- `pl/` (папка с кодом)
- `COOLIFY_DEPLOY.md` (подробная инструкция)

**❌ НЕ загружайте:**

- `.env` (реальные ключи)
- `session.session` (загрузите отдельно в Coolify)

## 🔧 Команды для тестирования

Для тестирования можете запустить:

```bash
# Обычный режим
python -m pl.cli telegram

# Расширенный режим
python -m pl.cli telegram --advanced

# Проверка баланса
python -m pl.cli balance

# Простой запрос
python -m pl.cli ask "Привет!"
```

**Готово! Можно деплоить на Coolify! 🎉**
