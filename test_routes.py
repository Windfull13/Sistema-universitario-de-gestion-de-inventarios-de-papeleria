#!/usr/bin/env python
"""Test the item detail page"""

from app import app

client = app.test_client()

# Test item page loads
print("Testing /item/42...")
r = client.get('/item/42')
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    has_image_tag = b'<img src="/api/item/42/image"' in r.data
    has_qr_tag = b'url_for' in r.data or b'/nfc/qr/' in r.data
    print(f"  Has image tag: {has_image_tag}")
    print(f"  Has QR reference: {has_qr_tag}")
else:
    print(f"  Error: {r.data[:200]}")

# Test image generation
print("\nTesting /api/item/42/image...")
r = client.get('/api/item/42/image')
print(f"  Status: {r.status_code}")
print(f"  Content type: {r.content_type}")
print(f"  Response size: {len(r.data)} bytes")
if r.status_code == 200 and r.data[:4] == b'\x89PNG':
    print("  ✓ Valid PNG image!")
else:
    print(f"  Error: {r.data[:100]}")
