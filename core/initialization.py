"""
Database and extension initialization module
"""
import os
import logging
from datetime import datetime, timedelta
from flask import Flask

logger = logging.getLogger(__name__)


def init_database(app: Flask):
    """Initialize database and create tables"""
    try:
        from flask_sqlalchemy import SQLAlchemy
        from models import db, User, Item, Supplier, Transaction, PurchaseOrder
        
        db.init_app(app)
        db_available = True
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        db_available = False
        db = None
    
    return db, db_available


def init_mail(app: Flask):
    """Initialize Flask-Mail if credentials are available"""
    mail = None
    try:
        from flask_mail import Mail
        if all([os.getenv('MAIL_SERVER'), os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD')]):
            mail = Mail(app)
            logger.info("Mail initialized")
    except Exception as e:
        logger.warning(f"Mail initialization failed: {e}")
    
    return mail


def create_tables_and_seed(app: Flask, db):
    """Create database tables and seed initial data"""
    if not db:
        return
    
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created/verified")
            
            # Create admin user
            _create_admin_user(db)
            
            # Seed products
            _seed_products(db)
            
            # Generate placeholder images
            _generate_placeholder_images(db)
            
            # Seed example data
            _seed_example_data(db)
            
    except Exception as e:
        logger.warning(f"Could not create tables: {e}")


def _create_admin_user(db):
    """Create default admin user if doesn't exist"""
    try:
        from models import User
        from werkzeug.security import generate_password_hash
        
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@sistema.local',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created (admin/admin123)")
    except Exception as e:
        logger.warning(f"Could not create admin: {e}")


def _seed_products(db):
    """Seed initial products if database is empty"""
    try:
        from models import Item
        
        if Item.query.count() == 0:
            from seed_products import PRODUCTS
            total = 0
            for category, products in PRODUCTS.items():
                for product in products:
                    item = Item(
                        name=product['name'],
                        description=product.get('description', ''),
                        category=category,
                        price=product['price'],
                        stock=product['stock'],
                        rentable=product['rentable']
                    )
                    db.session.add(item)
                    total += 1
            db.session.commit()
            logger.info(f"Seeded {total} products from seed_products.py")
    except Exception as e:
        logger.warning(f"Could not seed products: {e}")


def _generate_placeholder_images(db):
    """Generate placeholder images for items"""
    try:
        from PIL import Image, ImageDraw
        from models import Item
        from core.styles import get_category_color, TEXT_COLOR
        
        img_dir = 'static/uploads'
        os.makedirs(img_dir, exist_ok=True)
        
        # Get items that need images
        all_items = Item.query.all()
        items_to_generate = []
        for item in all_items:
            if not item.image_filename:
                items_to_generate.append(item)
            else:
                img_path = f"{img_dir}/{item.image_filename}"
                if not os.path.exists(img_path):
                    items_to_generate.append(item)
        
        if items_to_generate:
            logger.info(f"Generating images for {len(items_to_generate)} items...")
            for item in items_to_generate:
                try:
                    rgb = get_category_color(item.category)
                    
                    img = Image.new('RGB', (400, 300), color=rgb)
                    draw = ImageDraw.Draw(img)
                    text = item.name[:40]
                    bbox = draw.textbbox((0, 0), text)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = (400 - text_width) // 2
                    y = (300 - text_height) // 2
                    draw.text((x, y), text, fill=TEXT_COLOR)
                    
                    filename = f"item_{item.id}.png"
                    img_path = f"{img_dir}/{filename}"
                    img.save(img_path)
                    
                    if not item.image_filename:
                        item.image_filename = filename
                        db.session.add(item)
                except Exception as e:
                    logger.warning(f"Could not generate image for item {item.id}: {e}")
            db.session.commit()
            logger.info(f"Generated {len(items_to_generate)} placeholder images")
    except ImportError:
        logger.warning("Pillow not available, skipping image generation")
    except Exception as e:
        logger.warning(f"Could not generate placeholder images: {e}")


def _seed_example_data(db):
    """Seed example suppliers, transactions, and purchase orders"""
    try:
        from models import Supplier, User, Item, Transaction, PurchaseOrder
        from werkzeug.security import generate_password_hash
        import random
        
        # Seed suppliers
        if Supplier.query.count() == 0:
            suppliers_data = [
                {'name': 'Papelera Central', 'email': 'ventas@paperacentral.com', 'phone': '+57 301 1234567', 'city': 'Bogotá', 'contact': 'Juan Pérez'},
                {'name': 'Distribuidora El Lápiz', 'email': 'contacto@lapiz.com', 'phone': '+57 312 9876543', 'city': 'Medellín', 'contact': 'María García'},
                {'name': 'Importadora Escolar', 'email': 'import@escolar.co', 'phone': '+57 321 5555555', 'city': 'Cali', 'contact': 'Carlos López'},
                {'name': 'Artículos de Oficina Premium', 'email': 'premium@oficina.co', 'phone': '+57 310 7777777', 'city': 'Barranquilla', 'contact': 'Ana Rodríguez'}
            ]
            for sup_data in suppliers_data:
                supplier = Supplier(**sup_data)
                db.session.add(supplier)
            db.session.commit()
            logger.info(f"Seeded {len(suppliers_data)} suppliers")
        
        # Seed students
        students_data = [
            {'username': 'juan.perez', 'email': 'juan@university.edu'},
            {'username': 'maria.garcia', 'email': 'maria@university.edu'},
            {'username': 'carlos.lopez', 'email': 'carlos@university.edu'},
            {'username': 'ana.rodriguez', 'email': 'ana@university.edu'},
        ]
        for std_data in students_data:
            existing = User.query.filter_by(username=std_data['username']).first()
            if not existing:
                student = User(
                    username=std_data['username'],
                    email=std_data['email'],
                    password_hash=generate_password_hash('student123'),
                    role='student'
                )
                db.session.add(student)
        db.session.commit()
        logger.info(f"Seeded students")
        
        # Create transactions and purchase orders
        items = Item.query.all()
        suppliers = Supplier.query.all()
        students = User.query.filter_by(role='student').all()
        
        if items and suppliers and students:
            # Transactions
            existing_transactions = Transaction.query.count()
            if existing_transactions == 0:
                for i in range(20):
                    random_item = random.choice(items)
                    random_student = random.choice(students)
                    is_rental = random.choice([True, False])
                    days_ago = random.randint(0, 60)
                    trans_date = datetime.utcnow() - timedelta(days=days_ago)
                    
                    transaction = Transaction(
                        user_id=random_student.id,
                        item_id=random_item.id,
                        kind='rent' if is_rental else 'buy',
                        qty=random.randint(1, 3),
                        timestamp=trans_date
                    )
                    
                    if is_rental:
                        transaction.rent_start_date = trans_date.date()
                        transaction.rent_days = random.randint(3, 14)
                        transaction.rent_due_date = (trans_date + timedelta(days=transaction.rent_days)).date()
                        transaction.returned = random.choice([True, False])
                        if transaction.returned:
                            transaction.return_date = trans_date + timedelta(days=random.randint(2, 15))
                    
                    db.session.add(transaction)
                
                # Purchase orders
                for i in range(15):
                    random_supplier = random.choice(suppliers)
                    random_item = random.choice(items)
                    days_ago = random.randint(0, 90)
                    po_date = datetime.utcnow() - timedelta(days=days_ago)
                    
                    purchase_order = PurchaseOrder(
                        supplier_id=random_supplier.id,
                        item_id=random_item.id,
                        quantity=random.randint(10, 100),
                        unit_price=random_item.price * 0.7,
                        order_date=po_date,
                        expected_delivery_date=po_date + timedelta(days=random.randint(5, 30)),
                        status=random.choice(['pending', 'delivered', 'cancelled'])
                    )
                    purchase_order.total_cost = purchase_order.quantity * purchase_order.unit_price
                    db.session.add(purchase_order)
                
                db.session.commit()
                logger.info("Seeded 20 transactions and 15 purchase orders")
                
                # Rental extensions
                rentals = Transaction.query.filter_by(kind='rent').limit(8).all()
                for rental in rentals:
                    rental.extension_requested = True
                    rental.extension_days = random.randint(3, 7)
                    rental.extension_approved = True
                    rental.extension_approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                db.session.commit()
                logger.info(f"Seeded rental extensions")
                
    except Exception as e:
        logger.warning(f"Could not seed example data: {e}")
