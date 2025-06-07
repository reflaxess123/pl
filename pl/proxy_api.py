"""
Утилита для работы с ProxyAPI GPT-4o mini
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class ProxyAPIClient:
    """Клиент для работы с ProxyAPI GPT-4o mini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            api_key: API ключ. Если не указан, берется из переменной окружения PROXY_API_KEY
        """
        self.api_key = api_key or os.getenv('PROXY_API_KEY')
        if not self.api_key:
            raise ValueError("API ключ не найден. Укажите его в параметре или в переменной окружения PROXY_API_KEY")
        
        self.base_url = "https://api.proxyapi.ru"
        self.model = "gpt-4o-mini"
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def get_balance(self) -> float:
        """
        Получение баланса аккаунта
        
        Returns:
            Баланс в рублях
        """
        url = f"{self.base_url}/proxyapi/balance"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('balance', 0.0)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка получения баланса: {e}")
    
    def generate_text(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 300,
        top_p: float = 0.95
    ) -> str:
        """
        Генерация текста с помощью GPT-4o mini
        
        Args:
            prompt: Текст запроса
            temperature: Степень креативности (0.0-1.0)
            max_tokens: Максимальное количество токенов в ответе
            top_p: Контроль разнообразия ответа
            
        Returns:
            Сгенерированный текст
        """
        url = f"{self.base_url}/openai/v1/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # Извлекаем текст из ответа OpenAI
            if 'choices' in data and len(data['choices']) > 0:
                choice = data['choices'][0]
                
                # Проверяем причину завершения
                finish_reason = choice.get('finish_reason', '')
                if finish_reason == 'length':
                    raise Exception("Достигнут лимит токенов. Увеличьте max_tokens или сократите запрос.")
                
                if 'message' in choice and 'content' in choice['message']:
                    content = choice['message']['content']
                    if content:
                        return content.strip()
            
            # Отладочная информация если не удалось извлечь текст
            print(f"Отладка: полный ответ API = {json.dumps(data, ensure_ascii=False, indent=2)}")
            raise Exception("Не удалось извлечь текст из ответа API")
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 402:
                raise Exception("Недостаточно средств на балансе")
            raise Exception(f"Ошибка API запроса: {e}")
    
    def chat(self):
        """Интерактивный чат с GPT-4o mini"""
        print("=== ProxyAPI GPT-4o mini Chat ===")
        print("Введите 'exit' для выхода, 'balance' для проверки баланса")
        print("-" * 40)
        
        try:
            balance = self.get_balance()
            print(f"💰 Баланс: {balance:.2f} ₽")
        except Exception as e:
            print(f"⚠️ Не удалось получить баланс: {e}")
        
        print("-" * 40)
        
        while True:
            try:
                user_input = input("\n👤 Вы: ").strip()
                
                if user_input.lower() == 'exit':
                    print("👋 До свидания!")
                    break
                
                if user_input.lower() == 'balance':
                    try:
                        balance = self.get_balance()
                        print(f"💰 Баланс: {balance:.2f} ₽")
                    except Exception as e:
                        print(f"⚠️ Ошибка получения баланса: {e}")
                    continue
                
                if not user_input:
                    continue
                
                print("\n🤖 GPT-4o mini думает...")
                response = self.generate_text(user_input)
                print(f"\n🤖 GPT-4o mini: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")


def main():
    """Основная функция для запуска утилиты"""
    try:
        client = ProxyAPIClient()
        client.chat()
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")


if __name__ == "__main__":
    main() 