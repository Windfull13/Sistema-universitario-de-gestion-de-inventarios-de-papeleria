#!/usr/bin/env python
from app import app

with app.test_client() as client:
    response = client.get('/item/42')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("SUCCESS: /item/42 works!")
    else:
        print(f"Error: {response.data[:300]}")
