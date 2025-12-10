#!/usr/bin/env python
"""
Test de rutas - Simular requests a las rutas problemáticas
"""
import sys
import os

# Crear app
from app import create_app

app = create_app()

# Context para testear
with app.test_client() as client:
    print("=" * 80)
    print("TEST DE RUTAS")
    print("=" * 80)
    
    # Test 1: Health
    print("\n[1] Testing /health endpoint...")
    response = client.get('/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json}")
    
    # Test 2: Index
    print("\n[2] Testing / (index)...")
    response = client.get('/')
    print(f"Status: {response.status_code}")
    print(f"First 200 chars: {response.data[:200]}")
    
    # Test 3: Item detail
    print("\n[3] Testing /item/1...")
    response = client.get('/item/1')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Item 1 found!")
        print(f"First 200 chars: {response.data[:200]}")
    else:
        print(f"❌ Item 1 returned {response.status_code}")
        print(f"Response: {response.data[:200]}")
    
    # Test 4: Login page
    print("\n[4] Testing /login...")
    response = client.get('/login')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Login page loaded!")
    else:
        print(f"❌ Login page returned {response.status_code}")
    
    # Test 5: Item 42
    print("\n[5] Testing /item/42 (specific item)...")
    response = client.get('/item/42')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Item 42 found!")
    else:
        print(f"❌ Item 42 returned {response.status_code}")
    
    # Test 6: API item endpoint
    print("\n[6] Testing /api/items/1...")
    response = client.get('/api/items/1')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ API endpoint works!")
        print(f"Response: {response.json}")
    else:
        print(f"❌ API returned {response.status_code}")
        if response.is_json:
            print(f"Response: {response.json}")

print("\n" + "=" * 80)
print("TESTS COMPLETADOS")
print("=" * 80)
