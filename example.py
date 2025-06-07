"""
Пример использования ProxyAPI утилиты
"""

from pl.proxy_api import ProxyAPIClient
import os

def main():
    # Вариант 1: API ключ через переменную окружения (рекомендуется)
    # Создайте файл .env и добавьте туда: PROXY_API_KEY=ваш_ключ
    
    # Вариант 2: API ключ напрямую (НЕ рекомендуется для продакшн)
    # client = ProxyAPIClient(api_key="ваш_api_ключ_здесь")
    
    try:
        # Создаем клиент (ключ из .env файла)
        client = ProxyAPIClient()
        
        # Проверяем баланс
        print("Проверяем баланс...")
        balance = client.get_balance()
        print(f"💰 Баланс: {balance:.2f} ₽")
        
        # Простой запрос
        print("\nЗадаем вопрос...")
        response = client.generate_text(
            "Объясни простыми словами, что такое машинное обучение?",
            max_tokens=200
        )
        print(f"\n🤖 Ответ: {response}")
        
        # Запрос с настройками
        print("\nЗапрос с повышенной креативностью...")
        creative_response = client.generate_text(
            "Напиши короткую смешную историю про кота-программиста",
            temperature=0.9,
            max_tokens=300
        )
        print(f"\n🤖 Креативный ответ: {creative_response}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\n📝 Убедитесь что:")
        print("1. Создан файл .env с вашим API ключом")
        print("2. Формат: PROXY_API_KEY=ваш_ключ")
        print("3. На балансе достаточно средств")


if __name__ == "__main__":
    main() 