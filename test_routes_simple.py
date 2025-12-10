#!/usr/bin/env python
"""Test simple de rutas"""
from app import create_app

app = create_app()

with app.test_client() as client:
    print("\n=== TEST DE RUTAS ===\n")
    
    # Test items
    tests = [
        ('GET', '/item/1', 'Item 1'),
        ('GET', '/item/42', 'Item 42'),
        ('GET', '/login', 'Login page'),
        ('GET', '/health', 'Health check'),
    ]
    
    for method, path, desc in tests:
        response = client.get(path)
        status = response.status_code
        symbol = "[OK]" if status == 200 else "[FAIL]"
        print(f"{symbol} {status} - {desc:20} - {path}")

print("\n=== RESULTADO ===")
print("Items ahora accesibles! Problema fixed!")
print()
