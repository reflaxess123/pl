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
        
        # Системный промпт для Telegram
        telegram_system_prompt = (
            "Ты - персональный ассистент пользователя в Telegram. "
            "Ты работаешь от имени пользователя и помогаешь ему с различными задачами. "
            "Пользователь отправляет команды через специальные сообщения, а ты их выполняешь. "
            "Твоя цель - выполнять команды точно и качественно, писать естественно от имени пользователя. "
            "Отвечай кратко и по делу, избегай лишних объяснений и фраз вроде 'как ИИ-ассистент'. "
            "Пиши так, как писал бы сам пользователь."
        )
        
        # ProxyAPI клиент
        self.proxy_client = ProxyAPIClient(system_prompt=telegram_system_prompt)
        
        # Паттерн для команд
        self.command_pattern = re.compile(r'^@gpt-(.+)', re.IGNORECASE | re.DOTALL)
        
    async def start(self):
        """Запуск userbot"""
        print("🚀 Запуск Telegram UserBot...")
        
        await self.client.start(phone=self.phone)
        
        me = await self.client.get_me()
        print(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        print("📱 UserBot активен! Используйте @gpt-[ваша команда] в любом чате")
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
            
            # Проверяем, является ли сообщение командой @gpt
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
            # Команды с контекстом: @gpt-context50-open-rewrite текст
            'context_open': re.compile(r'^@gpt-context(\d+)-open-(.+)', re.IGNORECASE | re.DOTALL),
            # Команды с контекстом: @gpt-context50-rewrite текст  
            'context': re.compile(r'^@gpt-context(\d+)-(.+)', re.IGNORECASE | re.DOTALL),
            # Обычные команды с open: @gpt-open-rewrite текст
            'open': re.compile(r'^@gpt-open-(.+)', re.IGNORECASE | re.DOTALL),
            # Обычные команды
            'rewrite': re.compile(r'^@gpt-rewrite\s+(.+)', re.IGNORECASE | re.DOTALL),
            'translate': re.compile(r'^@gpt-translate\s+(.+)', re.IGNORECASE | re.DOTALL),
            'explain': re.compile(r'^@gpt-explain\s+(.+)', re.IGNORECASE | re.DOTALL),
            'fix': re.compile(r'^@gpt-fix\s+(.+)', re.IGNORECASE | re.DOTALL),
            'short': re.compile(r'^@gpt-short\s+(.+)', re.IGNORECASE | re.DOTALL),
            'general': re.compile(r'^@gpt-(.+)', re.IGNORECASE | re.DOTALL),
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
                    
                    if command_type == 'context_open':
                        # Обрабатываем команду с контекстом и флагом open
                        context_count = int(match.group(1))
                        command_text = match.group(2).strip()
                        await self._handle_context_command(event, context_count, command_text, open_mode=True)
                    elif command_type == 'context':
                        # Обрабатываем команду с контекстом
                        context_count = int(match.group(1))
                        command_text = match.group(2).strip()
                        await self._handle_context_command(event, context_count, command_text, open_mode=False)
                    elif command_type == 'open':
                        # Обрабатываем команду с флагом open
                        command_text = match.group(1).strip()
                        await self._handle_open_command(event, command_text)
                    else:
                        # Обычная команда без контекста
                        await self._handle_command(event, command_type, match.group(1).strip())
                    return
            
            print(f"⚠️ Команда не распознана: {message_text[:50]}...")
                    
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")
    
    async def _get_context_messages(self, event, limit: int = 5) -> str:
        """Получение контекста из предыдущих сообщений"""
        if limit <= 0:
            return ""
        
        try:
            # Получаем предыдущие сообщения
            messages = []
            async for message in self.client.iter_messages(
                event.chat_id, 
                limit=limit + 1,  # +1 чтобы исключить текущее сообщение
                reverse=True
            ):
                # Пропускаем текущее сообщение
                if message.id == event.message.id:
                    continue
                    
                # Берем только текстовые сообщения
                if message.message:
                    # Определяем отправителя
                    if message.out:
                        sender = "Вы"
                    else:
                        sender_user = await message.get_sender()
                        if sender_user:
                            sender = getattr(sender_user, 'first_name', 'Собеседник') or 'Собеседник'
                        else:
                            sender = 'Собеседник'
                    
                    messages.append(f"{sender}: {message.message}")
            
            if messages:
                context = "Контекст беседы:\n" + "\n".join(reversed(messages[-limit:])) + "\n\n"
                print(f"📚 Добавлен контекст из {len(messages)} сообщений")
                return context
            
            return ""
            
        except Exception as e:
            print(f"⚠️ Ошибка получения контекста: {e}")
            return ""
    
    async def _handle_context_command(self, event, context_count: int, command_text: str, open_mode: bool = False):
        """Обработка команды с контекстом"""
        mode_text = "open " if open_mode else ""
        print(f"\n📝 Команда с контекстом [{context_count}] {mode_text}: {command_text[:50]}...")
        
        # Ограничиваем контекст разумными пределами
        context_limit = max(0, min(context_count, 50))
        
        # Получаем контекст
        context = await self._get_context_messages(event, context_limit)
        
        # Определяем тип команды из текста команды
        command_type = 'general'
        content = command_text
        
        # Проверяем, начинается ли с известной команды
        if command_text.startswith('rewrite '):
            command_type = 'rewrite'
            content = command_text[8:].strip()
        elif command_text.startswith('translate '):
            command_type = 'translate'
            content = command_text[10:].strip()
        elif command_text.startswith('explain '):
            command_type = 'explain'
            content = command_text[8:].strip()
        elif command_text.startswith('fix '):
            command_type = 'fix'
            content = command_text[4:].strip()
        elif command_text.startswith('short '):
            command_type = 'short'
            content = command_text[6:].strip()
        
        # Формируем промпт
        prompts = {
            'rewrite': f"Переформулируй этот текст, чтобы он звучал более естественно и грамотно:\n\n{content}",
            'translate': f"Переведи этот текст на русский язык:\n\n{content}",
            'explain': f"Объясни простыми словами:\n\n{content}",
            'fix': f"Исправь ошибки в этом тексте:\n\n{content}",
            'short': f"Сократи этот текст, сохранив основную мысль:\n\n{content}",
            'general': content
        }
        
        base_prompt = prompts.get(command_type, content)
        final_prompt = context + base_prompt if context else base_prompt
        
        # Показываем индикатор набора текста
        async with self.client.action(event.chat_id, 'typing'):
            try:
                response = self.proxy_client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1200,  # Больше токенов для контекста
                    top_p=0.9
                )
                
                # Редактируем или дополняем сообщение в зависимости от режима
                if open_mode:
                    # Режим open: сохраняем исходный текст + добавляем ответ
                    original_text = event.message.message
                    full_response = f"{original_text}\n\nОтвет GPT:\n{response}"
                    await event.edit(full_response)
                    print(f"✅ Ответ с контекстом (open режим) отправлен: {response[:100]}...")
                else:
                    # Обычный режим: заменяем сообщение ответом
                    await event.edit(response)
                    print(f"✅ Ответ с контекстом отправлен: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                await event.edit(error_msg)
                print(f"❌ Ошибка: {e}")
    
    async def _handle_open_command(self, event, command_text: str):
        """Обработка команды с флагом open (без контекста)"""
        print(f"\n📝 Open команда: {command_text[:50]}...")
        
        # Определяем тип команды из текста команды
        command_type = 'general'
        content = command_text
        
        # Проверяем, начинается ли с известной команды
        if command_text.startswith('rewrite '):
            command_type = 'rewrite'
            content = command_text[8:].strip()
        elif command_text.startswith('translate '):
            command_type = 'translate'
            content = command_text[10:].strip()
        elif command_text.startswith('explain '):
            command_type = 'explain'
            content = command_text[8:].strip()
        elif command_text.startswith('fix '):
            command_type = 'fix'
            content = command_text[4:].strip()
        elif command_text.startswith('short '):
            command_type = 'short'
            content = command_text[6:].strip()
        
        # Формируем промпт
        prompts = {
            'rewrite': f"Переформулируй этот текст, чтобы он звучал более естественно и грамотно:\n\n{content}",
            'translate': f"Переведи этот текст на русский язык:\n\n{content}",
            'explain': f"Объясни простыми словами:\n\n{content}",
            'fix': f"Исправь ошибки в этом тексте:\n\n{content}",
            'short': f"Сократи этот текст, сохранив основную мысль:\n\n{content}",
            'general': content
        }
        
        final_prompt = prompts.get(command_type, content)
        
        # Показываем индикатор набора текста
        async with self.client.action(event.chat_id, 'typing'):
            try:
                response = self.proxy_client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=0.9
                )
                
                # Режим open: сохраняем исходный текст + добавляем ответ
                original_text = event.message.message
                full_response = f"{original_text}\n\nОтвет GPT:\n{response}"
                await event.edit(full_response)
                print(f"✅ Ответ (open режим) отправлен: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                await event.edit(error_msg)
                print(f"❌ Ошибка: {e}")
    
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
        
        # Формируем промпт (без контекста для обычных команд)
        final_prompt = prompts.get(command_type, content)
        
        # Показываем индикатор набора текста
        async with self.client.action(event.chat_id, 'typing'):
            try:
                response = self.proxy_client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1000,  # Увеличиваем лимит для контекста
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