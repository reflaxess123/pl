"""
Веб интерфейс для управления Telegram ботом через FastAPI
"""

import os
import asyncio
import json
from typing import Optional, Dict, List
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

from .telegram_client import TelegramUserBotWithAutoReply
from .proxy_api import ProxyAPIClient

load_dotenv()

app = FastAPI(title="Telegram Bot Manager", description="Веб интерфейс для управления Telegram ботом")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")

# Глобальные переменные для состояния бота
bot_instance: Optional[TelegramUserBotWithAutoReply] = None
bot_task: Optional[asyncio.Task] = None
is_bot_running = False
bot_logs: List[Dict] = []

# Состояние настроек
bot_settings = {
    "temperature": 0.7,
    "max_tokens": 500,
    "system_prompt_normal": "",
    "system_prompt_hide": "",
}

def add_log(level: str, message: str):
    """Добавить запись в лог"""
    global bot_logs
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "level": level,
        "message": message
    }
    bot_logs.append(log_entry)
    
    # Ограничиваем количество логов
    if len(bot_logs) > 100:
        bot_logs = bot_logs[-100:]

@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    """Главная страница веб интерфейса"""
    try:
        # Получаем информацию о балансе
        proxy_client = ProxyAPIClient()
        balance = proxy_client.get_balance()
        balance_info = f"{balance:.2f} ₽"
    except Exception as e:
        balance_info = f"Ошибка: {str(e)}"
    
    # Получаем информацию об автоответах
    auto_reply_chats = []
    auto_reply_settings = {}
    if bot_instance:
        auto_reply_chats = [
            {
                "chat_id": chat_id,
                "name": info["name"],
                "enabled": info["enabled"]
            }
            for chat_id, info in bot_instance.get_auto_reply_chats().items()
        ]
        auto_reply_settings = bot_instance.get_auto_reply_settings()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "is_bot_running": is_bot_running,
        "balance": balance_info,
        "bot_logs": bot_logs[-10:],  # Последние 10 записей
        "settings": bot_settings,
        "auto_reply_chats": auto_reply_chats,
        "auto_reply_settings": auto_reply_settings
    })

@app.post("/bot/start")
async def start_bot(background_tasks: BackgroundTasks):
    """Запуск бота"""
    global bot_instance, bot_task, is_bot_running
    
    if is_bot_running:
        return JSONResponse({"status": "error", "message": "Бот уже запущен"})
    
    try:
        bot_instance = TelegramUserBotWithAutoReply()
        add_log("INFO", "Создан экземпляр бота с автоответом")
        
        # Запускаем бота в фоновой задаче
        async def run_bot():
            global is_bot_running
            try:
                is_bot_running = True
                add_log("INFO", "Бот запускается...")
                await bot_instance.start()
            except Exception as e:
                add_log("ERROR", f"Ошибка при работе бота: {str(e)}")
                is_bot_running = False
        
        bot_task = asyncio.create_task(run_bot())
        add_log("INFO", "Бот успешно запущен")
        
        return JSONResponse({"status": "success", "message": "Бот запущен"})
    
    except Exception as e:
        add_log("ERROR", f"Ошибка запуска бота: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/bot/stop")
async def stop_bot():
    """Остановка бота"""
    global bot_instance, bot_task, is_bot_running
    
    if not is_bot_running:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        is_bot_running = False
        
        if bot_instance:
            await bot_instance.stop()
            add_log("INFO", "Бот остановлен")
        
        if bot_task and not bot_task.done():
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                pass
        
        bot_instance = None
        bot_task = None
        
        return JSONResponse({"status": "success", "message": "Бот остановлен"})
    
    except Exception as e:
        add_log("ERROR", f"Ошибка остановки бота: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/bot/status")
async def bot_status():
    """Получить статус бота"""
    return JSONResponse({
        "is_running": is_bot_running,
        "logs_count": len(bot_logs)
    })

@app.get("/api/balance")
async def get_balance():
    """Получить баланс ProxyAPI"""
    try:
        proxy_client = ProxyAPIClient()
        balance = proxy_client.get_balance()
        return JSONResponse({"status": "success", "balance": balance})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/test-gpt")
async def test_gpt(request: Request):
    """Тестирование GPT запроса"""
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        
        if not prompt:
            return JSONResponse({"status": "error", "message": "Не указан prompt"})
        
        proxy_client = ProxyAPIClient()
        response = proxy_client.generate_text(
            prompt,
            temperature=bot_settings.get("temperature", 0.7),
            max_tokens=bot_settings.get("max_tokens", 500)
        )
        
        add_log("INFO", f"Тест GPT: {prompt[:50]}...")
        return JSONResponse({"status": "success", "response": response})
        
    except Exception as e:
        add_log("ERROR", f"Ошибка тестирования GPT: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/api/logs")
async def get_logs():
    """Получить логи"""
    return JSONResponse({"logs": bot_logs})

@app.get("/api/auto-reply/stats")
async def get_auto_reply_stats():
    """Получить статистику автоответов"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        # Подсчитываем статистику из логов
        auto_reply_logs = [log for log in bot_logs if "автоответ" in log["message"].lower()]
        skip_logs = [log for log in bot_logs if "пропустить" in log["message"].lower()]
        sent_logs = [log for log in bot_logs if "автоответ отправлен" in log["message"].lower()]
        
        stats = {
            "total_auto_replies": len(auto_reply_logs),
            "skipped_messages": len(skip_logs),
            "sent_messages": len(sent_logs),
            "active_chats": len(bot_instance.get_auto_reply_chats()),
            "recent_activity": auto_reply_logs[-5:] if auto_reply_logs else []
        }
        
        return JSONResponse({"status": "success", "stats": stats})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/settings")
async def update_settings(request: Request):
    """Обновить настройки бота"""
    global bot_settings
    
    try:
        data = await request.json()
        
        # Обновляем настройки
        if "temperature" in data:
            bot_settings["temperature"] = float(data["temperature"])
        if "max_tokens" in data:
            bot_settings["max_tokens"] = int(data["max_tokens"])
        if "system_prompt_normal" in data:
            bot_settings["system_prompt_normal"] = data["system_prompt_normal"]
        if "system_prompt_hide" in data:
            bot_settings["system_prompt_hide"] = data["system_prompt_hide"]
        
        add_log("INFO", "Настройки обновлены")
        return JSONResponse({"status": "success", "message": "Настройки сохранены"})
        
    except Exception as e:
        add_log("ERROR", f"Ошибка обновления настроек: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/api/settings")
async def get_settings():
    """Получить текущие настройки"""
    return JSONResponse({"settings": bot_settings})

# === API для управления автоответами ===

@app.get("/api/auto-reply/chats")
async def get_auto_reply_chats():
    """Получить список чатов с автоответом"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        chats = bot_instance.get_auto_reply_chats()
        chats_list = [
            {
                "chat_id": chat_id,
                "name": info["name"],
                "enabled": info["enabled"],
                "last_activity": info.get("last_activity")
            }
            for chat_id, info in chats.items()
        ]
        return JSONResponse({"status": "success", "chats": chats_list})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/api/dialogs")
async def get_dialogs():
    """Получить список всех диалогов пользователя"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        dialogs = await bot_instance.get_dialogs_list(limit=100)
        return JSONResponse({"status": "success", "dialogs": dialogs})
    except Exception as e:
        add_log("ERROR", f"Ошибка получения диалогов: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/auto-reply/chats/add")
async def add_auto_reply_chat(request: Request):
    """Добавить чат для автоответа"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        data = await request.json()
        chat_id = int(data.get("chat_id", 0))
        chat_name = data.get("chat_name", f"Chat {chat_id}")
        
        if chat_id == 0:
            return JSONResponse({"status": "error", "message": "Неверный ID чата"})
        
        success = bot_instance.add_auto_reply_chat(chat_id, chat_name)
        
        if success:
            add_log("INFO", f"Добавлен чат для автоответа: {chat_name}")
            return JSONResponse({"status": "success", "message": "Чат добавлен"})
        else:
            return JSONResponse({"status": "error", "message": "Ошибка добавления чата"})
            
    except Exception as e:
        add_log("ERROR", f"Ошибка добавления чата: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/auto-reply/chats/remove")
async def remove_auto_reply_chat(request: Request):
    """Удалить чат из автоответа"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        data = await request.json()
        chat_id = int(data.get("chat_id", 0))
        
        success = bot_instance.remove_auto_reply_chat(chat_id)
        
        if success:
            add_log("INFO", f"Удален чат из автоответа: {chat_id}")
            return JSONResponse({"status": "success", "message": "Чат удален"})
        else:
            return JSONResponse({"status": "error", "message": "Чат не найден"})
            
    except Exception as e:
        add_log("ERROR", f"Ошибка удаления чата: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/auto-reply/chats/toggle")
async def toggle_auto_reply_chat(request: Request):
    """Переключить статус автоответа для чата"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        data = await request.json()
        chat_id = int(data.get("chat_id", 0))
        
        success = bot_instance.toggle_auto_reply_chat(chat_id)
        
        if success:
            chats = bot_instance.get_auto_reply_chats()
            status = "включен" if chats[chat_id]["enabled"] else "выключен"
            add_log("INFO", f"Автоответ для чата {chat_id}: {status}")
            return JSONResponse({"status": "success", "message": f"Автоответ {status}"})
        else:
            return JSONResponse({"status": "error", "message": "Чат не найден"})
            
    except Exception as e:
        add_log("ERROR", f"Ошибка переключения статуса: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

@app.get("/api/auto-reply/settings")
async def get_auto_reply_settings():
    """Получить настройки автоответа"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        settings = bot_instance.get_auto_reply_settings()
        return JSONResponse({"status": "success", "settings": settings})
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})

@app.post("/api/auto-reply/settings")
async def update_auto_reply_settings(request: Request):
    """Обновить настройки автоответа"""
    if not bot_instance:
        return JSONResponse({"status": "error", "message": "Бот не запущен"})
    
    try:
        data = await request.json()
        
        success = bot_instance.update_auto_reply_settings(data)
        
        if success:
            add_log("INFO", "Настройки автоответа обновлены")
            return JSONResponse({"status": "success", "message": "Настройки сохранены"})
        else:
            return JSONResponse({"status": "error", "message": "Ошибка обновления настроек"})
            
    except Exception as e:
        add_log("ERROR", f"Ошибка обновления настроек автоответа: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)})

def run_web_interface(host: str = "127.0.0.1", port: int = 8000):
    """Запуск веб интерфейса"""
    print(f"🌐 Запуск веб интерфейса на http://{host}:{port}")
    print("📱 Откройте браузер и перейдите по адресу выше")
    
    uvicorn.run(
        "pl.web_interface:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    run_web_interface() 