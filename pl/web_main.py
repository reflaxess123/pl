#!/usr/bin/env python3
"""
Точка входа для запуска веб интерфейса управления ботом
"""

import argparse
from .web_interface import run_web_interface

def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Запуск веб интерфейса для управления Telegram ботом")
    parser.add_argument("--host", default="127.0.0.1", help="IP адрес для привязки сервера (по умолчанию: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Порт для сервера (по умолчанию: 8000)")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🤖 Telegram Bot Web Manager")
    print("=" * 50)
    print(f"🌐 Сервер будет запущен на: http://{args.host}:{args.port}")
    print("📋 Функции веб интерфейса:")
    print("  - Запуск/остановка бота")
    print("  - Мониторинг статуса")
    print("  - Просмотр логов")
    print("  - Тестирование GPT")
    print("  - Настройка параметров")
    print("  - Проверка баланса ProxyAPI")
    print("=" * 50)
    
    try:
        run_web_interface(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 Веб интерфейс остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска веб интерфейса: {e}")

if __name__ == "__main__":
    main() 