#!/usr/bin/env python
"""Quick test to verify app and routes"""

from app import app

print("✓ App imports successfully")

with app.test_request_context('/'):
    from flask import url_for
    print(f"✓ Image route: {url_for('generate_item_image', item_id=42)}")
    print(f"✓ Item detail route: {url_for('item_detail', item_id=42)}")
    print("✓ All checks passed")
