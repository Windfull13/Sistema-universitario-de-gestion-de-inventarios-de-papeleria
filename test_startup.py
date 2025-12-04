#!/usr/bin/env python
"""
Test if the Flask app can start
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("Testing Flask App Startup")
print("=" * 80)

try:
    print("\n[1/5] Importing Flask...")
    from flask import Flask
    print("✓ Flask imported")
except Exception as e:
    print(f"✗ Error importing Flask: {e}")
    sys.exit(1)

try:
    print("\n[2/5] Importing models...")
    from models import db
    print("✓ Models imported")
except Exception as e:
    print(f"✗ Error importing models: {e}")
    sys.exit(1)

try:
    print("\n[3/5] Importing config...")
    from config import config
    print("✓ Config imported")
except Exception as e:
    print(f"✗ Error importing config: {e}")
    sys.exit(1)

try:
    print("\n[4/5] Importing routes...")
    from routes import register_blueprints
    print("✓ Routes imported")
except Exception as e:
    print(f"✗ Error importing routes: {e}")
    sys.exit(1)

try:
    print("\n[5/5] Creating Flask app instance...")
    from app import app
    print("✓ Flask app created")
except Exception as e:
    print(f"✗ Error creating Flask app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✓ ALL TESTS PASSED - App can start successfully!")
print("=" * 80)
