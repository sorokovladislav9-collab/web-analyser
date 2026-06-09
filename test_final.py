#!/usr/bin/env python3
"""
Финальный тест роутов
"""
import socket
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
    
    results = {}
    
    for route, description in routes_to_test:
        try:
            # Создаем сокет
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            # Подключаемся к серверу
            sock.connect(("localhost", 5000))
            
            # Отправляем HTTP запрос
            request = f"GET {route} HTTP/1.1\r\nHost: localhost:5000\r\n\r\n"
            sock.sendall(request.encode())
            
            # Получаем ответ
            response = sock.recv(4096).decode()
            
            if "200 OK" in response:
                status = "✅"
                print(f"{status} {route} - {description} работает")
                results[route] = {"status": 200, "working": True}
            else:
                status = "❌"
                print(f"{status} {route} - {description} не работает")
                results[route] = {"status": 500, "working": False}
            
            sock.close()
            
        except Exception as e:
            status = "❌"
            print(f"❌ {route} - {description} ошибка: {e}")
            results[route] = {"status": 500, "working": False, "error": str(e)}
    
    print(f"\n📊 Результаты:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Тест POST роутов
    print("\n🧪 Тестирование POST роутов...")
    
    post_routes = [
        ("/start-analysis/1", "Запуск анализа", {"website_id": 1}),
        ("/analysis/analyze-website/1", "Анализ сайта", {"website_id": 1}),
    ]
    
    for route, description, data in post_routes:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(("localhost", 5000))
            
            # Формируем POST запрос
            post_data = json.dumps(data)
            request = f"POST {route} HTTP/1.1\r\nHost: localhost:5000\r\nContent-Type: application/json\r\nContent-Length: {len(post_data)}\r\n\r\n{post_data}"
            
            sock.sendall(request.encode())
            
            # Получаем ответ
            response = sock.recv(4096).decode()
            
            if "302 Found" in response or "303 See Other" in response:
                status = "✅"
                print(f"{status} {route} - {description} перенаправляет")
                results[f"POST_{route}"] = {"status": 302, "working": True}
            else:
                status = "❌"
                print(f"{status} {route} - {description} не работает")
                results[f"POST_{route}"] = {"status": 500, "working": False}
            
            sock.close()
            
        except Exception as e:
            status = "❌"
            print(f"❌ {route} - {description} ошибка: {e}")
            results[f"POST_{route}"] = {"status": 500, "working": False, "error": str(e)}
    
    print(f"\n📊 Результаты POST:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    print("\n🎯 Тестирование завершено!")

if __name__ == "__main__":
    test_routes()
