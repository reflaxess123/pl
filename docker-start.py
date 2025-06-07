#!/usr/bin/env python3
"""
Скрипт для запуска веб интерфейса в Docker контейнере
"""

import argparse
from pl.web_interface import run_web_interface

def main():
    """Главная функция для Docker"""
    parser = argparse.ArgumentParser(description="Запуск веб интерфейса в Docker")
    parser.add_argument("--host", default="0.0.0.0", help="IP адрес для привязки сервера (по умолчанию: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Порт для сервера (по умолчанию: 8000)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🐳 Telegram Bot Web Manager - Docker Version")
    print("=" * 60)
    print(f"🌐 Веб интерфейс доступен на: http://localhost:{args.port}")
    print("📋 Функции:")
    print("  - Запуск/остановка бота с автоответом")
    print("  - Управление диалогами для автоответа")
    print("  - Мониторинг логов и статистики")
    print("  - Тестирование GPT")
    print("  - Настройки параметров")
    print("=" * 60)
    
    try:
        # В Docker используем 0.0.0.0 для доступа снаружи контейнера
        run_web_interface(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\n👋 Веб интерфейс остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    main() 