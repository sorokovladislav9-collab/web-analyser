#!/usr/bin/env python3
"""
Простой тест роутов
"""
import requests
import json

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
        ("/api/", "API"),
        ("/start-analysis/1", "Запуск анализа (POST)"),
        ("/analysis/analyze-website/1", "Анализ сайта (POST)"),
    ]
    
    for route, description in routes_to_test:
        try:
            response = requests.get(f"{base_url}{route}")
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {route} - {description} (Статус: {response.status_code})")
        except Exception as e:
            print(f"❌ {route} - {description} (Ошибка: {e})")
    
    print("\n🎯 Тестирование POST роутов с параметрами...")
    
    # Тест POST роутов
    post_routes = [
        ("/start-analysis/1", "Запуск анализа", {"website_id": 1}),
        ("/analysis/analyze-website/1", "Анализ сайта", {"website_id": 1}),
    ]
    
    for route, description, data in post_routes:
        try:
            response = requests.post(f"{base_url}{route}", data=data)
            status = "✅" if response.status_code in [200, 302, 303] else "❌"
            print(f"{status} {route} - {description} (Статус: {response.status_code})")
        except Exception as e:
            print(f"❌ {route} - {description} (Ошибка: {e})")
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    test_routes()
