#!/usr/bin/env python
from app import app

with app.test_client() as client:
    response = client.get('/item/42')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        if b'Cuaderno cosido' in response.data:
            print("OK: Item loaded")
        if b'item_42.png' in response.data or b'/static/uploads/item_42.png' in response.data:
            print("OK: Image reference found in HTML")
        else:
            print("ERROR: No image reference in HTML")
        if b'/nfc/qr/42' in response.data:
            print("OK: QR reference found")
        else:
            print("ERROR: No QR reference")
    else:
        print(f"ERROR: Status {response.status_code}")
