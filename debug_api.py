"""
Отладочный скрипт для проверки ответа ProxyAPI
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PROXY_API_KEY')
print(f"API ключ: {api_key[:10]}...")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Тестовый запрос
url = "https://api.proxyapi.ru/google/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent"

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Привет! Ответь одним словом: да"}
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.7,
        "maxOutputTokens": 300,
        "topP": 0.95
    }
}

print("Отправляем запрос...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    print(f"\nСтатус ответа: {response.status_code}")
    print(f"Заголовки ответа: {dict(response.headers)}")
    
    try:
        response_json = response.json()
        print(f"\nТело ответа (JSON):")
        print(json.dumps(response_json, ensure_ascii=False, indent=2))
    except:
        print(f"\nТело ответа (текст):")
        print(response.text)
        
    if response.status_code != 200:
        print(f"\n❌ Ошибка HTTP: {response.status_code}")
    
except Exception as e:
    print(f"❌ Ошибка запроса: {e}") 