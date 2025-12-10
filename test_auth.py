#!/usr/bin/env python
"""Test de login/logout"""
from app import create_app

app = create_app()

with app.test_client() as client:
    print("\n=== TEST LOGIN/LOGOUT ===\n")
    
    # Test 1: Login page
    print("[1] GET /login")
    resp = client.get('/login')
    print(f"Status: {resp.status_code} (esperado: 200)")
    
    # Test 2: Login POST (admin/admin123)
    print("\n[2] POST /login (credenciales admin)")
    resp = client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    print(f"Status: {resp.status_code} (esperado: 302 redirect)")
    if resp.status_code == 302:
        print(f"Redirect a: {resp.headers.get('Location')}")
    
    # Test 3: Student login page
    print("\n[3] GET /student/login")
    resp = client.get('/student/login')
    print(f"Status: {resp.status_code} (esperado: 200)")
    
    # Test 4: Logout
    print("\n[4] GET /logout")
    resp = client.get('/logout', follow_redirects=False)
    print(f"Status: {resp.status_code} (esperado: 302 redirect)")
    if resp.status_code == 302:
        print(f"Redirect a: {resp.headers.get('Location')}")

print("\n✅ Tests completados!")
