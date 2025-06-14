# ProxyAPI GPT-4o mini Утилита

Простая утилита для работы с OpenAI GPT-4o mini через ProxyAPI. Позволяет отправлять текстовые запросы, проверять баланс и вести интерактивный диалог с ИИ.

## Возможности

- 🤖 Генерация текста с помощью GPT-4o mini
- 💰 Проверка баланса аккаунта
- 💬 Интерактивный чат режим
- 📱 **Telegram UserBot** - интеграция с личным аккаунтом Telegram
- 🌐 **Веб интерфейс** - удобное управление ботом через браузер
- ⚙️ Настройка параметров генерации (температура, токены, top-p)
- 🔐 Безопасное хранение API ключа через переменные окружения

## Установка

1. Клонируйте проект и установите зависимости:

```bash
poetry install
```

2. Скопируйте файл с примером переменных окружения:

```bash
copy .env.example .env
```

3. Настройте переменные окружения в файле `.env`:

```env
# ProxyAPI ключ - получите на https://proxyapi.ru
PROXY_API_KEY=your_api_key_here

# Telegram API credentials (для UserBot) - получите на https://my.telegram.org
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE=your_phone_number_here

# Системный промпт (опционально)
SYSTEM_PROMPT=Ты - персональный ассистент пользователя в Telegram. Работай от его имени, отвечай кратко и по делу.
```

### Настройка системного промпта

По умолчанию используется базовый системный промпт для работы в качестве персонального ассистента. Вы можете настроить его:

1. **Через переменную окружения** - установите `SYSTEM_PROMPT` в файле `.env`
2. **Программно** - передайте параметр `system_prompt` при создании `ProxyAPIClient`

Хороший системный промпт должен:

- Объяснять роль ассистента
- Указывать стиль общения
- Требовать краткости и естественности ответов

## Использование

### Интерактивный чат

```bash
poetry run python -m pl.cli chat
```

### Проверка баланса

```bash
poetry run python -m pl.cli balance
```

### Одиночный запрос

```bash
poetry run python -m pl.cli ask "Объясни, что такое Python?"
```

### Запрос с настройками

```bash
poetry run python -m pl.cli ask "Напиши стихотворение" --temperature 0.9 --max-tokens 500
```

### Веб интерфейс (FastAPI)

Удобный веб интерфейс для управления ботом через браузер:

```bash
# Запуск веб интерфейса
python -m pl.web_main

# С настройкой хоста и порта
python -m pl.web_main --host 0.0.0.0 --port 8080
```

**Возможности веб интерфейса:**

- 🎮 Запуск/остановка бота одной кнопкой
- 📊 Мониторинг статуса в реальном времени
- 📋 Просмотр логов работы
- 🧠 Тестирование GPT запросов
- ⚙️ Настройка параметров (temperature, max_tokens)
- 💰 Проверка баланса ProxyAPI
- 🤖 **Управление автоответом** - настройка автоматических ответов в диалогах
- 💬 **Управление диалогами** - добавление/удаление чатов для автоответа с галочками включения/выключения

Откройте в браузере: **http://127.0.0.1:8000**

### 🐳 Запуск в Docker (рекомендуется)

Самый простой способ запуска с изолированной средой:

**Windows:**

```cmd
run-web-docker.bat
```

**Linux/Mac:**

```bash
./run-web-docker.sh
```

**Ручной запуск:**

```bash
docker-compose --profile web up pl-web
```

Откройте в браузере: **http://localhost:8000**

📋 [Подробная инструкция по Docker](DOCKER_README.md)

### Telegram UserBot

```bash
# Простая версия
python pl/cli.py telegram

# Расширенная версия с дополнительными командами
python pl/cli.py telegram --advanced
```

**Использование в Telegram:**

**Обычные команды (показывают "Запрос → Ответ GPT"):**

- `@gpt Переформулируй этот текст` - любой запрос
- `@gpt explain что такое Python` - объяснить простыми словами
- `@gpt rewrite Текст` - переформулировать
- `@gpt translate Text` - перевести на русский
- `@gpt fix Текст с ашибками` - исправить ошибки
- `@gpt short Длинный текст` - сократить

**Hide команды (ответ от лица пользователя):**

- `@gpt-hide explain что такое AI` - объяснить от лица пользователя
- `@gpt-hide rewrite Текст` - переформулировать от лица пользователя

**Команды с контекстом (анализируют предыдущие сообщения):**

- `@gpt-context15 объясни о чем мы говорили` - с контекстом 15 сообщений
- `@gpt-context50-hide найди информацию` - с контекстом, ответить как пользователь

**Режимы работы:**

- **Обычный режим:** Показывает "Запрос → Ответ GPT", ИИ работает как ассистент и объясняет собеседникам
- **Hide режим:** ИИ отвечает от первого лица, как будто сам пользователь пишет в чате (скрывает участие ИИ)

📋 [Подробная инструкция по настройке Telegram](TELEGRAM_SETUP.md)

### Программное использование

```python
from pl.proxy_api import ProxyAPIClient

# Создание клиента
client = ProxyAPIClient()  # API ключ из .env

# Проверка баланса
balance = client.get_balance()
print(f"Баланс: {balance:.2f} ₽")

# Генерация текста
response = client.generate_text(
    "Привет! Как дела?",
    temperature=0.7,
    max_tokens=250
)
print(response)
```

## Параметры генерации

- **temperature** (0.0-1.0) - креативность ответа (по умолчанию 0.7)
- **max_tokens** - максимальное количество токенов в ответе (по умолчанию 250)
- **top_p** - контроль разнообразия ответа (по умолчанию 0.95)

## Примерная стоимость

При балансе 200 ₽ можно сделать примерно:

- 10,000-12,000 коротких запросов (100 токенов запрос + 250 токенов ответ)
- Стоимость одного запроса: ~0.015-0.02 ₽

## Активация виртуального окружения

```bash
poetry shell
```
