import urllib.request
import json

def test_routes():
    """Простая проверка роутов"""
    base_url = "http://localhost:5000"
    
    print("🧪 Проверка роутов...")
    
    routes_to_test = [
        ("/", "Главная страница"),
        ("/dashboard", "Дашборд"),
        ("/websites", "Сайты"),
        ("/analysis/quick-analyze", "Анализ"),
        ("/analysis/compare-websites", "Сравнение"),
    ]
    
    results = {}
    
    for route, description in routes_to_test:
        try:
            req = urllib.request.Request(base_url + route)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    status = "✅"
                    print(f"{status} {route} - {description} работает")
                else:
                    status = "❌"
                    print(f"{status} {route} - {description} не работает (статус: {response.getcode()})")
                results[route] = {"status": response.getcode(), "working": response.getcode() == 200}
        except Exception as e:
            status = "❌"
            print(f"❌ {route} - {description} ошибка: {e}")
            results[route] = {"status": 500, "working": False, "error": str(e)}
    
    print(f"\n📊 Результаты:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Проверка POST роутов
    print("\n🧪 Проверка POST роутов...")
    
    post_routes = [
        ("/start-analysis/1", "Запуск анализа", {"website_id": 1}),
        ("/analysis/analyze-website/1", "Анализ сайта", {"website_id": 1}),
    ]
    
    for route, description, data in post_routes:
        try:
            req = urllib.request.Request(base_url + route, method="POST", data=json.dumps(data).encode())
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() in [200, 302, 303]:
                    status = "✅"
                    print(f"{status} {route} - {description} работает")
                else:
                    status = "❌"
                    print(f"{status} {route} - {description} не работает (статус: {response.getcode()})")
                results[route] = {"status": response.getcode(), "working": response.getcode() in [200, 302, 303], "data": data}
        except Exception as e:
            status = "❌"
            print(f"❌ {route} - {description} ошибка: {e}")
            results[route] = {"status": 500, "working": False, "error": str(e)}
    
    print(f"\n📊 Результаты POST:")
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_routes()
