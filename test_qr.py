#!/usr/bin/env python
"""Quick test of QR code functionality"""

from app import app

client = app.test_client()

# Test item page
print("Testing /item/42...")
r = client.get('/item/42')
print(f"  Status: {r.status_code}")

# Check for QR image reference
import re
match = re.search(r'src="([^"]*item_42_qr\.png[^"]*)"', r.data.decode())
if match:
    print(f"  ✓ QR image path found: {match.group(1)}")
    
    # Test the QR file exists
    qr_response = client.get(match.group(1))
    print(f"  ✓ QR file status: {qr_response.status_code}")
else:
    print("  ✗ QR image path NOT found in HTML")

print("\nTesting /item/80...")
r = client.get('/item/80')
print(f"  Status: {r.status_code}")

match = re.search(r'src="([^"]*item_80_qr\.png[^"]*)"', r.data.decode())
if match:
    print(f"  ✓ QR image path found: {match.group(1)}")
    qr_response = client.get(match.group(1))
    print(f"  ✓ QR file status: {qr_response.status_code}")
else:
    print("  ✗ QR image path NOT found in HTML")
