#!/usr/bin/env python
"""
Generate QR codes for all items
"""
import os
from app import app, db
from models import Item

def generate_qr_codes():
    """Generate QR codes for all items"""
    try:
        import segno
        HAS_SEGNO = True
    except ImportError:
        print("ERROR: segno not installed. Installing...")
        os.system("pip install segno")
        import segno
        HAS_SEGNO = True
    
    # Create QR directory if doesn't exist
    qr_dir = 'static/uploads/qr'
    os.makedirs(qr_dir, exist_ok=True)
    
    with app.app_context():
        items = Item.query.all()
        print(f"\nGenerating QR codes for {len(items)} items...\n")
        
        for i, item in enumerate(items, 1):
            try:
                # URL for the item
                url = f"https://sistema-universitario-de-gestion-de.onrender.com/item/{item.id}"
                
                # Generate QR (using regular QR, not micro)
                qr = segno.make(url, error='L', micro=False)
                
                # Save as PNG
                filename = f"{qr_dir}/item_{item.id}.png"
                qr.save(filename, kind='png', scale=5)
                
                if i % 20 == 0:
                    print(f"  ✓ Generated {i}/156 QR codes...")
                
            except Exception as e:
                print(f"  ERROR generating QR for item {item.id}: {e}")
        
        print(f"\nOK All {len(items)} QR codes generated!")
        return True

if __name__ == '__main__':
    generate_qr_codes()
