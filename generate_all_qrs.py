#!/usr/bin/env python
"""Generate QR codes for all 156 items and save them to static folder"""

import os
from app import app
from models import Item, db
import segno
from io import BytesIO

# Ensure static/uploads/qr directory exists
qr_dir = 'static/uploads/qr'
os.makedirs(qr_dir, exist_ok=True)

with app.app_context():
    # Get all items
    items = Item.query.all()
    print(f"Found {len(items)} items. Generating QR codes...")
    
    success_count = 0
    error_count = 0
    
    for item in items:
        try:
            # Build the URL for this item
            with app.test_request_context():
                from flask import url_for
                item_url = f"https://sistema-universitario-de-gestion-de.onrender.com/item/{item.id}"
            
            # Generate QR code
            qr = segno.make(item_url, error='L', micro=False)
            
            # Save to file
            qr_filename = f'item_{item.id}_qr.png'
            qr_filepath = os.path.join(qr_dir, qr_filename)
            qr.save(qr_filepath, kind='png', scale=5)
            
            success_count += 1
            if success_count % 20 == 0:
                print(f"  Generated {success_count}/{len(items)} QR codes...")
        
        except Exception as e:
            print(f"  ERROR generating QR for item {item.id}: {e}")
            error_count += 1
    
    print(f"\n✓ Successfully generated {success_count} QR codes")
    if error_count > 0:
        print(f"✗ Failed to generate {error_count} QR codes")
    
    # List generated files
    qr_files = os.listdir(qr_dir)
    print(f"\nTotal QR files in {qr_dir}: {len(qr_files)}")
