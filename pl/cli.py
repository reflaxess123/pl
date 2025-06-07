"""
CLI интерфейс для ProxyAPI утилиты
"""

import argparse
import sys
from pl.proxy_api import ProxyAPIClient


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Утилита для работы с ProxyAPI GPT-4o mini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python -m pl.cli chat                           # Интерактивный чат
  python -m pl.cli balance                        # Проверить баланс
  python -m pl.cli ask "Привет, как дела?"        # Одиночный запрос
  python -m pl.cli ask "Объясни квантовую физику" --max-tokens 500
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='API ключ ProxyAPI (можно также задать через переменную окружения PROXY_API_KEY)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Доступные команды')
    
    # Команда chat
    chat_parser = subparsers.add_parser('chat', help='Интерактивный чат с GPT-4o mini')
    
    # Команда balance
    balance_parser = subparsers.add_parser('balance', help='Проверить баланс аккаунта')
    
    # Команда ask
    ask_parser = subparsers.add_parser('ask', help='Задать одиночный вопрос')
    ask_parser.add_argument('question', help='Текст вопроса')
    ask_parser.add_argument('--temperature', type=float, default=0.7, 
                           help='Степень креативности (0.0-1.0, по умолчанию 0.7)')
    ask_parser.add_argument('--max-tokens', type=int, default=300,
                           help='Максимальное количество токенов в ответе (по умолчанию 300)')
    ask_parser.add_argument('--top-p', type=float, default=0.95,
                           help='Контроль разнообразия ответа (по умолчанию 0.95)')
    
    # Команда telegram
    telegram_parser = subparsers.add_parser('telegram', help='Запуск Telegram UserBot')
    telegram_parser.add_argument('--advanced', action='store_true',
                                help='Использовать расширенную версию с дополнительными командами')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # Создаем клиент
        client = ProxyAPIClient(api_key=args.api_key)
        
        if args.command == 'chat':
            client.chat()
            
        elif args.command == 'balance':
            balance = client.get_balance()
            print(f"💰 Баланс: {balance:.2f} ₽")
            
        elif args.command == 'ask':
            print("🤖 GPT-4o mini думает...")
            response = client.generate_text(
                args.question,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                top_p=args.top_p
            )
            print(f"\n🤖 Ответ: {response}")
            
        elif args.command == 'telegram':
            import asyncio
            from pl.telegram_client import TelegramUserBot, TelegramUserBotAdvanced
            
            async def run_telegram():
                if args.advanced:
                    bot = TelegramUserBotAdvanced()
                else:
                    bot = TelegramUserBot()
                
                try:
                    await bot.start()
                except KeyboardInterrupt:
                    print("\n🛑 Получен сигнал остановки...")
                    await bot.stop()
            
            asyncio.run(run_telegram())
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 