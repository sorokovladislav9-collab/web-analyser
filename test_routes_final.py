#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Чистый тест роутов
"""
import urllib.request
import json

def test_routes():
    base_url = "http://localhost:5000"
    
    print("Testing routes...")
    
    routes_to_test = [
        ("/", "Main page"),
        ("/dashboard", "Dashboard"),
        ("/websites", "Websites"),
        ("/analysis/quick-analyze", "Analysis"),
        ("/analysis/compare-websites", "Comparison"),
        ("/api/", "API"),
    ]
    
    results = {}
    
    for route, description in routes_to_test:
        try:
            response = urllib.request.urlopen(f"{base_url}{route}", timeout=10)
            if response.getcode() == 200:
                status = "OK"
                results[route] = {"status": 200, "working": True}
                print(f"OK {route} - {description}")
            else:
                status = "FAIL"
                results[route] = {"status": response.getcode(), "working": False}
                print(f"FAIL {route} - {description} (Status: {response.getcode()})")
        except Exception as e:
            status = "ERROR"
            results[route] = {"status": 500, "working": False, "error": str(e)}
            print(f"ERROR {route} - {description}: {e}")
    
    print("\nResults:")
    print(json.dumps(results, indent=2))
    
    # Test POST routes
    print("\nTesting POST routes...")
    
    post_routes = [
        ("/start-analysis/1", "Start analysis", {"website_id": 1}),
        ("/analysis/analyze-website/1", "Analyze website", {"website_id": 1}),
    ]
    
    for route, description, data in post_routes:
        try:
            post_data = json.dumps(data).encode()
            req = urllib.request.Request(f"{base_url}{route}", method="POST", data=post_data)
            response = urllib.request.urlopen(req, timeout=10)
            if response.getcode() in [200, 302, 303]:
                status = "OK"
                results[f"POST_{route}"] = {"status": response.getcode(), "working": True}
                print(f"OK {route} - {description}")
            else:
                status = "FAIL"
                results[f"POST_{route}"] = {"status": response.getcode(), "working": False}
                print(f"FAIL {route} - {description} (Status: {response.getcode()})")
        except Exception as e:
            status = "ERROR"
            results[f"POST_{route}"] = {"status": 500, "working": False, "error": str(e)}
            print(f"ERROR {route} - {description}: {e}")
    
    print("\nPOST Results:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    test_routes()
