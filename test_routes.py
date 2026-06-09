#!/usr/bin/env python3
"""
Тестовый скрипт для проверки роутов
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

def test_routes():
    """Тестирование всех роутов"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Тестирование роутов...")
        
        # Тест главной страницы
        print("\n1. Тест главной страницы:")
        try:
            response = client.get('/')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Главная страница работает")
            else:
                print("   ❌ Ошибка главной страницы")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест дашборда
        print("\n2. Тест дашборда:")
        try:
            response = client.get('/dashboard')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Дашборд работает")
            else:
                print("   ❌ Ошибка дашборда")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест страницы сайтов
        print("\n3. Тест страницы сайтов:")
        try:
            response = client.get('/websites')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Страница сайтов работает")
            else:
                print("   ❌ Ошибка страницы сайтов")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест роута анализа
        print("\n4. Тест роута анализа:")
        try:
            response = client.get('/analysis/quick-analyze')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Страница анализа работает")
            else:
                print("   ❌ Ошибка страницы анализа")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест роута сравнения
        print("\n5. Тест роута сравнения:")
        try:
            response = client.get('/analysis/compare-websites')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Страница сравнения работает")
            else:
                print("   ❌ Ошибка страницы сравнения")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест API
        print("\n6. Тест API endpoints:")
        try:
            response = client.get('/api/')
            print(f"   Статус: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ API работает")
            else:
                print("   ❌ Ошибка API")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Проверка роутов с параметрами
        print("\n7. Тест роутов с параметрами:")
        
        # Тест роута start_analysis
        print("\n7.1 Тест роута start_analysis:")
        try:
            response = client.post('/start-analysis/1', data={})
            print(f"   Статус: {response.status_code}")
            if response.status_code in [302, 303]:
                print("   ✅ Перенаправление работает")
            else:
                print("   ❌ Ошибка перенаправления")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        # Тест роута analyze_website_start
        print("\n7.2 Тест роута analyze_website_start:")
        try:
            response = client.post('/analysis/analyze-website/1', data={})
            print(f"   Статус: {response.status_code}")
            if response.status_code in [302, 303]:
                print("   ✅ Перенаправление работает")
            else:
                print("   ❌ Ошибка перенаправления")
        except Exception as e:
            print(f"   ❌ Исключение: {e}")
        
        print("\n🎯 Тестирование завершено!")

if __name__ == '__main__':
    test_routes()
