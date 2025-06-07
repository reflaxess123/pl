# 🔧 Исправление для Coolify

## Проблема

Coolify показывал ошибку:

```
tee: /data/coolify/applications/.../env: Is a directory
```

## Решение ✅

Добавлены в Dockerfile пустые файлы для совместимости:

```dockerfile
# Создаем пустой .env файл для совместимости с load_dotenv()
RUN touch .env

# Создаем пустой session.session файл (будет заменен volume в Coolify)
RUN touch session.session
```

## Результат

- ✅ Образ совместим с переменными окружения Coolify
- ✅ Не требует .env файла в Git репозитории
- ✅ session.session монтируется как volume в Coolify
- ✅ Протестировано и работает

## Для деплоя на Coolify:

1. **Переменные окружения** - добавьте в панели Coolify
2. **Storage для session.session** - File mount в `/app/session.session`
3. **Start Command:** `python -m pl.cli telegram`

Готово к деплою! 🚀
