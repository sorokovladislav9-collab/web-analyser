#!/usr/bin/env python3
"""
Проверка роутов без кодировочных проблем
"""
import requests

def check_routes():
    """Простая проверка роутов"""
    base_url = "http://localhost:5000"
    
    print("🧪 Проверка роутов...")
    
    # Проверка основных роутов
    routes = [
        ("/", "Главная страница"),
        ("/dashboard", "Дашборд"),
        ("/websites", "Сайты"),
        ("/analysis/quick-analyze", "Анализ"),
        ("/analysis/compare-websites", "Сравнение"),
    ]
    
    for route, description in routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {route} - {description} работает")
            else:
                print(f"❌ {route} - {description} не работает (статус: {response.status_code})")
        except Exception as e:
            print(f"❌ {route} - {description} ошибка: {e}")
    
    print("\n🎯 Проверка завершена!")

if __name__ == "__main__":
    check_routes()
