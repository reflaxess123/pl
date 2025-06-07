"""
Telegram userbot для работы с ProxyAPI GPT-4o mini
"""

import os
import re
import asyncio
from typing import Optional
from telethon import TelegramClient, events
from telethon.tl.types import Message
from dotenv import load_dotenv

from .proxy_api import ProxyAPIClient

load_dotenv()


class TelegramUserBot:
    """Telegram userbot для обработки команд @pl"""
    
    def __init__(self):
        """Инициализация userbot"""
        # Telegram API credentials
        self.api_id = os.getenv('TELEGRAM_API_ID')
        self.api_hash = os.getenv('TELEGRAM_API_HASH')
        self.phone = os.getenv('TELEGRAM_PHONE')
        
        if not all([self.api_id, self.api_hash]):
            raise ValueError(
                "Не найдены TELEGRAM_API_ID и TELEGRAM_API_HASH в переменных окружения. "
                "Получите их на https://my.telegram.org"
            )
        
        # Создаем Telegram клиент
        self.client = TelegramClient('session', int(self.api_id), self.api_hash)
        
        # ProxyAPI клиент
        self.proxy_client = ProxyAPIClient()
        
        # Паттерн для команд
        self.command_pattern = re.compile(r'^@pl-(.+)', re.IGNORECASE | re.DOTALL)
        
    async def start(self):
        """Запуск userbot"""
        print("🚀 Запуск Telegram UserBot...")
        
        await self.client.start(phone=self.phone)
        
        me = await self.client.get_me()
        print(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        print("📱 UserBot активен! Используйте @pl-[ваша команда] в любом чате")
        print("🛑 Для остановки нажмите Ctrl+C")
        
        # Регистрируем обработчик сообщений
        @self.client.on(events.NewMessage(outgoing=True))
        async def handle_message(event):
            await self._process_message(event)
        
        # Запускаем клиент
        await self.client.run_until_disconnected()
    
    async def _process_message(self, event):
        """Обработка входящих сообщений"""
        try:
            message_text = event.message.message
            if not message_text:
                return
            
            # Проверяем, является ли сообщение командой @pl
            match = self.command_pattern.match(message_text.strip())
            if not match:
                return
            
            command = match.group(1).strip()
            if not command:
                return
            
            print(f"\n📝 Получена команда: {command}")
            
            # Показываем индикатор набора текста
            async with self.client.action(event.chat_id, 'typing'):
                # Отправляем запрос к GPT
                try:
                    response = self.proxy_client.generate_text(
                        command,
                        temperature=0.7,
                        max_tokens=500,
                        top_p=0.9
                    )
                    
                    # Редактируем сообщение с ответом
                    await event.edit(response)
                    print(f"✅ Ответ отправлен: {response[:100]}...")
                    
                except Exception as e:
                    error_msg = f"❌ Ошибка GPT: {str(e)}"
                    await event.edit(error_msg)
                    print(f"❌ Ошибка: {e}")
                    
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    async def stop(self):
        """Остановка userbot"""
        if self.client.is_connected():
            await self.client.disconnect()
            print("🛑 UserBot остановлен")


class TelegramUserBotAdvanced(TelegramUserBot):
    """Расширенная версия userbot с дополнительными командами"""
    
    def __init__(self):
        super().__init__()
        
        # Расширенные паттерны команд
        self.patterns = {
            'rewrite': re.compile(r'^@pl-rewrite\s+(.+)', re.IGNORECASE | re.DOTALL),
            'translate': re.compile(r'^@pl-translate\s+(.+)', re.IGNORECASE | re.DOTALL),
            'explain': re.compile(r'^@pl-explain\s+(.+)', re.IGNORECASE | re.DOTALL),
            'fix': re.compile(r'^@pl-fix\s+(.+)', re.IGNORECASE | re.DOTALL),
            'short': re.compile(r'^@pl-short\s+(.+)', re.IGNORECASE | re.DOTALL),
            'general': re.compile(r'^@pl-(.+)', re.IGNORECASE | re.DOTALL),
        }
    
    async def _process_message(self, event):
        """Обработка входящих сообщений с расширенными командами"""
        try:
            message_text = event.message.message
            if not message_text:
                return
            
            # Проверяем специфичные команды
            for command_type, pattern in self.patterns.items():
                match = pattern.match(message_text.strip())
                if match:
                    print(f"🔍 Найдена команда типа: {command_type}")
                    await self._handle_command(event, command_type, match.group(1).strip())
                    return
            
            print(f"⚠️ Команда не распознана: {message_text[:50]}...")
                    
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    async def _handle_command(self, event, command_type: str, content: str):
        """Обработка конкретной команды"""
        if not content:
            return
        
        print(f"\n📝 Команда [{command_type}]: {content[:50]}...")
        
        # Формируем промпт в зависимости от типа команды
        prompts = {
            'rewrite': f"Переформулируй этот текст, чтобы он звучал более естественно и грамотно:\n\n{content}",
            'translate': f"Переведи этот текст на русский язык:\n\n{content}",
            'explain': f"Объясни простыми словами:\n\n{content}",
            'fix': f"Исправь ошибки в этом тексте:\n\n{content}",
            'short': f"Сократи этот текст, сохранив основную мысль:\n\n{content}",
            'general': content
        }
        
        prompt = prompts.get(command_type, content)
        
        # Показываем индикатор набора текста
        async with self.client.action(event.chat_id, 'typing'):
            try:
                response = self.proxy_client.generate_text(
                    prompt,
                    temperature=0.7,
                    max_tokens=800,
                    top_p=0.9
                )
                
                # Редактируем сообщение с ответом
                await event.edit(response)
                print(f"✅ Ответ отправлен: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                await event.edit(error_msg)
                print(f"❌ Ошибка: {e}")


async def main():
    """Основная функция для запуска userbot"""
    try:
        # Можно выбрать обычную или расширенную версию
        # bot = TelegramUserBot()  # Простая версия
        bot = TelegramUserBotAdvanced()  # Расширенная версия
        
        await bot.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        if 'bot' in locals():
            await bot.stop()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 