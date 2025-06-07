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
        
        # Системные промпты для разных режимов
        self.normal_system_prompt = (
            "Ты - персональный ассистент пользователя в Telegram. "
            "Ты помогаешь пользователю объяснять информацию собеседникам в чате. "
            "ВАЖНО: Если в запросе есть 'Контекст беседы:', анализируй и используй эту информацию. "
            "Это реальные сообщения из чата. Отвечай так, как будто объясняешь двоим участникам беседы. "
            "Говори от третьего лица, объясняй ситуацию, суммируй информацию для присутствующих. "
            "Отвечай кратко и по делу, избегай фраз 'как ИИ-ассистент'."
        )
        
        self.hide_system_prompt = (
            "РЕЖИМ: ТЫ ПОЛЬЗОВАТЕЛЬ! Отвечай только от первого лица ('я', 'мне', 'мой')! "
            "Ты НЕ ассистент, НЕ помощник, а сам человек который пишет в чате. "
            "Если в запросе есть 'Контекст беседы:', используй эту информацию. "
            "Отвечай коротко, грубо если нужно, эмоционально, используй мат, сленг. "
            "Веди себя как настоящий человек, который раздражен или зол. "
            "ЗАПРЕЩЕНО говорить от третьего лица или как советчик!"
        )
        
        # ProxyAPI клиенты для разных режимов
        self.normal_client = ProxyAPIClient(system_prompt=self.normal_system_prompt)
        self.hide_client = ProxyAPIClient(system_prompt=self.hide_system_prompt)
        
        # Паттерн для команд
        self.command_pattern = re.compile(r'^@gpt\s+(.+)', re.IGNORECASE | re.DOTALL)
        
    async def start(self):
        """Запуск userbot"""
        print("🚀 Запуск Telegram UserBot...")
        
        await self.client.start(phone=self.phone)
        
        me = await self.client.get_me()
        print(f"✅ Авторизован как: {me.first_name} (@{me.username})")
        print("📱 UserBot активен! Используйте @gpt [ваша команда] в любом чате")
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
                    
                    # Показываем исходный запрос + ответ
                    original_text = event.message.message
                    full_response = f"{original_text}\n\nОтвет GPT:\n{response}"
                    await event.edit(full_response)
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
            # Команды с контекстом и hide: @gpt-context50-hide команда
            'context_hide': re.compile(r'^@gpt-context(\d+)-hide\s+(.+)', re.IGNORECASE | re.DOTALL),
            # Команды с контекстом: @gpt-context50 команда
            'context': re.compile(r'^@gpt-context(\d+)\s+(.+)', re.IGNORECASE | re.DOTALL),
            # Обычные команды с hide: @gpt-hide команда
            'hide': re.compile(r'^@gpt-hide\s+(.+)', re.IGNORECASE | re.DOTALL),
            # Обычные команды: @gpt команда
            'general': re.compile(r'^@gpt\s+(.+)', re.IGNORECASE | re.DOTALL),
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
                    
                    if command_type == 'context_hide':
                        # Обрабатываем команду с контекстом и флагом hide
                        context_count = int(match.group(1))
                        command_text = match.group(2).strip()
                        await self._handle_context_command(event, context_count, command_text, hide_mode=True)
                    elif command_type == 'context':
                        # Обрабатываем команду с контекстом (обычный режим)
                        context_count = int(match.group(1))
                        command_text = match.group(2).strip()
                        await self._handle_context_command(event, context_count, command_text, hide_mode=False)
                    elif command_type == 'hide':
                        # Обрабатываем команду с флагом hide
                        command_text = match.group(1).strip()
                        await self._handle_hide_command(event, command_text)
                    else:
                        # Обычная команда (показываем запрос + ответ)
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
            # Получаем больше сообщений, чтобы учесть фильтрацию
            fetch_limit = limit * 3  # Берем в 3 раза больше для фильтрации
            messages = []
            
            async for message in self.client.iter_messages(
                event.chat_id, 
                limit=fetch_limit,
                reverse=False  # Получаем в хронологическом порядке (новые сначала)
            ):
                # Пропускаем текущее сообщение
                if message.id == event.message.id:
                    continue
                    
                # Берем только текстовые сообщения
                if message.message and message.message.strip():
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
                    
                    # Останавливаемся, когда набрали нужное количество
                    if len(messages) >= limit:
                        break
            
            if messages:
                # Разворачиваем, чтобы показать в хронологическом порядке (старые сначала)
                context_messages = "\n".join(reversed(messages))
                context = f"Контекст беседы (последние {len(messages)} сообщений):\n{context_messages}\n\nОтветь на основе этого контекста:\n"
                
                if len(messages) < limit:
                    print(f"⚠️ Найдено только {len(messages)} сообщений из {limit} запрошенных (проверено: {fetch_limit})")
                else:
                    print(f"📚 Добавлен контекст из {len(messages)} сообщений (запрошено: {limit}, проверено: {fetch_limit})")
                return context
            
            return ""
            
        except Exception as e:
            print(f"⚠️ Ошибка получения контекста: {e}")
            return ""
    
    async def _handle_context_command(self, event, context_count: int, command_text: str, hide_mode: bool = False):
        """Обработка команды с контекстом"""
        mode_text = "hide " if hide_mode else ""
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
                # Выбираем правильный клиент в зависимости от режима
                client = self.hide_client if hide_mode else self.normal_client
                
                response = client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1200,  # Больше токенов для контекста
                    top_p=0.9
                )
                
                # В режиме hide заменяем сообщение только ответом
                if hide_mode:
                    await event.edit(response)
                    print(f"✅ Ответ с контекстом (hide режим) отправлен: {response[:100]}...")
                else:
                    # Обычный режим: сохраняем исходный текст + добавляем ответ  
                    original_text = event.message.message
                    full_response = f"{original_text}\n\nОтвет GPT:\n{response}"
                    await event.edit(full_response)
                    print(f"✅ Ответ с контекстом отправлен: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                await event.edit(error_msg)
                print(f"❌ Ошибка: {e}")
    
    async def _handle_hide_command(self, event, command_text: str):
        """Обработка команды с флагом hide (без контекста)"""
        print(f"\n📝 Hide команда: {command_text[:50]}...")
        
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
                response = self.hide_client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=0.9
                )
                
                # Режим hide: заменяем сообщение только ответом (от лица пользователя)
                await event.edit(response)
                print(f"✅ Ответ (hide режим) отправлен: {response[:100]}...")
                
            except Exception as e:
                error_msg = f"❌ Ошибка: {str(e)}"
                await event.edit(error_msg)
                print(f"❌ Ошибка: {e}")
    
    async def _handle_command(self, event, command_type: str, content: str):
        """Обработка конкретной команды"""
        if not content:
            return
        
        print(f"\n📝 Команда [{command_type}]: {content[:50]}...")
        
        # Для общих команд определяем подтип из содержимого
        actual_command_type = command_type
        actual_content = content
        
        if command_type == 'general':
            # Проверяем, начинается ли с известной подкоманды
            if content.startswith('rewrite '):
                actual_command_type = 'rewrite'
                actual_content = content[8:].strip()
            elif content.startswith('translate '):
                actual_command_type = 'translate'
                actual_content = content[10:].strip()
            elif content.startswith('explain '):
                actual_command_type = 'explain'
                actual_content = content[8:].strip()
            elif content.startswith('fix '):
                actual_command_type = 'fix'
                actual_content = content[4:].strip()
            elif content.startswith('short '):
                actual_command_type = 'short'
                actual_content = content[6:].strip()
        
        # Логируем результат разбора
        if actual_command_type != command_type:
            print(f"📋 Разобрано как: [{actual_command_type}] '{actual_content[:30]}...'")
        
        # Формируем промпт в зависимости от типа команды
        prompts = {
            'rewrite': f"Переформулируй этот текст, чтобы он звучал более естественно и грамотно:\n\n{actual_content}",
            'translate': f"Переведи этот текст на русский язык:\n\n{actual_content}",
            'explain': f"Объясни простыми словами:\n\n{actual_content}",
            'fix': f"Исправь ошибки в этом тексте:\n\n{actual_content}",
            'short': f"Сократи этот текст, сохранив основную мысль:\n\n{actual_content}",
            'general': actual_content
        }
        
        # Формируем промпт (без контекста для обычных команд)
        final_prompt = prompts.get(actual_command_type, actual_content)
        
        # Показываем индикатор набора текста
        async with self.client.action(event.chat_id, 'typing'):
            try:
                response = self.normal_client.generate_text(
                    final_prompt,
                    temperature=0.7,
                    max_tokens=1000,
                    top_p=0.9
                )
                
                # Обычный режим: показываем исходный запрос + ответ
                original_text = event.message.message
                full_response = f"{original_text}\n\nОтвет GPT:\n{response}"
                await event.edit(full_response)
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