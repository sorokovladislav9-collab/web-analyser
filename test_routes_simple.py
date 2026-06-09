#!/usr/bin/env python3
"""
Простая проверка роутов
"""
import urllib.request
import urllib.parse

def test_routes():
    """Тестирование роутов"""
    base_url = "http://localhost:5000"
    
    print("🧪 Тестирование роутов...")
    
    routes_to_test = [
        ("/", "Главная страница"),
        ("/dashboard", "Дашборд"),
        ("/websites", "Сайты"),
        ("/analysis/quick-analyze", "Анализ"),
        ("/analysis/compare-websites", "Сравнение"),
    ]
    
    for route, description in routes_to_test:
        try:
            with urllib.request.urlopen(f"{base_url}{route}", timeout=10) as response:
                if response.getcode() == 200:
                    print(f"✅ {route} - {description} работает")
                else:
                    print(f"❌ {route} - {description} не работает (статус: {response.getcode()})")
        except Exception as e:
            print(f"❌ {route} - {description} ошибка: {e}")
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    test_routes()
