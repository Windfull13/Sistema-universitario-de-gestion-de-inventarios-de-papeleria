#!/usr/bin/env python
"""
Add placeholder images to all items based on their category
"""
from app import app, db
from models import Item
from PIL import Image, ImageDraw
import os

def generate_placeholder_images():
    """Generate placeholder images for items"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed, installing...")
        os.system(".venv\\Scripts\\python.exe -m pip install Pillow")
        from PIL import Image, ImageDraw, ImageFont
    
    # Create uploads directory
    img_dir = 'static/uploads'
    os.makedirs(img_dir, exist_ok=True)
    
    # Color mapping for categories
    colors = {
        'Papeles': '#E8F5E9',
        'Escritura': '#F3E5F5',
        'Cuadernos y libretas': '#E3F2FD',
        'Organización y archivo': '#FFF3E0',
        'Corte, pegado y fijación': '#FCE4EC',
        'Arte y manualidades': '#F1F8E9',
        'Instrumentos de geometría': '#E0F2F1',
        'Tecnología ligera': '#ECE7FF',
        'Impresión': '#F8F5FF',
        'Oficina': '#FFF8E1',
        'Escolares': '#E8EAF6',
        'Otros productos': '#F5F5F5'
    }
    
    with app.app_context():
        items = Item.query.all()
        print(f"\nGenerating placeholder images for {len(items)} items...\n")
        
        for i, item in enumerate(items, 1):
            try:
                # Get color for category
                color = colors.get(item.category, '#F5F5F5')
                
                # Convert hex to RGB
                hex_color = color.lstrip('#')
                rgb = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
                
                # Create image
                img = Image.new('RGB', (400, 300), color=rgb)
                draw = ImageDraw.Draw(img)
                
                # Add text (item name)
                text = item.name[:40]  # Truncate if too long
                bbox = draw.textbbox((0, 0), text)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Center text
                x = (400 - text_width) // 2
                y = (300 - text_height) // 2
                
                draw.text((x, y), text, fill=(64, 64, 64))
                
                # Save image
                filename = f"{img_dir}/item_{item.id}.png"
                img.save(filename)
                
                # Update item with filename
                item.image_filename = f"item_{item.id}.png"
                db.session.add(item)
                
                if i % 20 == 0:
                    print(f"  OK {i}/156 placeholder images...")
                
            except Exception as e:
                print(f"  ERROR generating image for item {item.id}: {e}")
        
        db.session.commit()
        print(f"\nOK All {len(items)} placeholder images generated and assigned!")
        return True

if __name__ == '__main__':
    generate_placeholder_images()
