#!/usr/bin/env python
"""
Ultra-safe Flask app that works even if database is unavailable
This is the production version that runs on Render
"""
import os
import sys
import logging
import random
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, g, redirect, url_for, send_file

# Logging setup
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    from config import config
    app.config.from_object(config['production'])
else:
    from config import config
    app.config.from_object(config.get(config_name, config['development']))

# Initialize database ONLY if DATABASE_URL exists and is valid
db = None
db_available = False

try:
    from flask_sqlalchemy import SQLAlchemy
    from models import db, User, ActiveSession
    db.init_app(app)
    db_available = True
    logger.info("Database initialized")
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")
    db_available = False

# Initialize Mail (optional)
mail = None
try:
    from flask_mail import Mail
    if all([os.getenv('MAIL_SERVER'), os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD')]):
        mail = Mail(app)
        logger.info("Mail initialized")
except Exception as e:
    logger.warning(f"Mail initialization failed: {e}")

# Session configuration
app.config.update(
    SESSION_COOKIE_SECURE=not app.debug,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# Create tables if DB is available
if db_available:
    try:
        with app.app_context():
            db.create_all()
            logger.info("Database tables created/verified")
            
            # Initialize admin user if doesn't exist
            from werkzeug.security import generate_password_hash
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                try:
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
            
            # Seed products if database is empty
            from models import Item
            if Item.query.count() == 0:
                try:
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
            
            # Generate placeholder images if not exists (check both DB and filesystem)
            try:
                from PIL import Image, ImageDraw
                import os
                
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
                
                img_dir = 'static/uploads'
                os.makedirs(img_dir, exist_ok=True)
                
                # Get all items that either have no filename or whose file doesn't exist
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
                            color = colors.get(item.category, '#F5F5F5')
                            hex_color = color.lstrip('#')
                            rgb = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
                            
                            img = Image.new('RGB', (400, 300), color=rgb)
                            draw = ImageDraw.Draw(img)
                            text = item.name[:40]
                            bbox = draw.textbbox((0, 0), text)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                            x = (400 - text_width) // 2
                            y = (300 - text_height) // 2
                            draw.text((x, y), text, fill=(64, 64, 64))
                            
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
            
            # Seed example data (suppliers, transactions, purchase orders, extensions)
            from models import Supplier
            if Supplier.query.count() == 0:
                try:
                    import random
                    from models import Transaction, PurchaseOrder
                    
                    # Create suppliers
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
                    
                    # Create students
                    students_data = [
                        {'username': 'juan.perez', 'email': 'juan@university.edu'},
                        {'username': 'maria.garcia', 'email': 'maria@university.edu'},
                        {'username': 'carlos.lopez', 'email': 'carlos@university.edu'},
                        {'username': 'ana.rodriguez', 'email': 'ana@university.edu'},
                    ]
                    for std_data in students_data:
                        existing = User.query.filter_by(username=std_data['username']).first()
                        if not existing:
                            from werkzeug.security import generate_password_hash
                            student = User(
                                username=std_data['username'],
                                email=std_data['email'],
                                password_hash=generate_password_hash('student123'),
                                role='student'
                            )
                            db.session.add(student)
                    db.session.commit()
                    logger.info(f"Seeded {len(students_data)} students")
                    
                    # Create transactions and purchase orders
                    items = Item.query.all()
                    suppliers = Supplier.query.all()
                    students = User.query.filter_by(role='student').all()
                    
                    if items and suppliers and students:
                        # 20 transactions
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
                        
                        # 15 purchase orders
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
                        
                        # Create rental extensions
                        rentals = Transaction.query.filter_by(kind='rent').limit(8).all()
                        for rental in rentals:
                            rental.extension_requested = True
                            rental.extension_days = random.randint(3, 7)
                            rental.extension_approved = True
                            rental.extension_approved_at = datetime.utcnow() - timedelta(days=random.randint(1, 5))
                        db.session.commit()
                        logger.info(f"Seeded 8 rental extensions")
                    
                except Exception as e:
                    logger.warning(f"Could not seed example data: {e}")
                    
    except Exception as e:
        logger.warning(f"Could not create tables: {e}")
        db_available = False

@app.before_request
def before_request():
    """Load user from session - ultra defensive"""
    g.user = None
    
    # Skip for HEAD requests
    if request.method == 'HEAD':
        return
    
    # Skip for health check endpoints
    if request.path in ['/test', '/health']:
        return
    
    # Only try DB access if DB is available
    if not db_available:
        return
    
    try:
        if 'user_id' in session:
            try:
                g.user = User.query.get(session.get('user_id'))
            except:
                session.clear()
    except:
        pass

@app.context_processor
def inject_globals():
    """Template globals"""
    return {'current_user': g.user, 'datetime': datetime}

@app.after_request
def after_request(response):
    """Add security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    try:
        return render_template('404.html'), 404
    except:
        return {'error': 'Not found'}, 404

@app.errorhandler(500)
def server_error(error):
    try:
        return render_template('500.html'), 500
    except:
        return {'error': 'Internal server error'}, 500

@app.errorhandler(403)
def forbidden(error):
    try:
        return render_template('403.html'), 403
    except:
        return {'error': 'Forbidden'}, 403

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle HEAD requests"""
    if request.method == 'HEAD':
        return '', 200
    return {'error': 'Method not allowed'}, 405

# Health check
@app.route('/health', methods=['GET', 'HEAD'])
def health():
    """Health check endpoint"""
    if request.method == 'HEAD':
        return '', 200
    return {'status': 'healthy', 'db_available': db_available}, 200

# Test endpoint
@app.route('/test', methods=['GET', 'HEAD'])
def test():
    """Test endpoint"""
    if request.method == 'HEAD':
        return '', 200
    return 'OK', 200

# Home page
@app.route('/', methods=['GET', 'HEAD'])
def index():
    """Home page"""
    if request.method == 'HEAD':
        return '', 200
    
    try:
        # Redirect logged in users
        if g.user and db_available:
            if g.user.role == 'admin':
                try:
                    return redirect(url_for('admin.index'))
                except:
                    pass
            else:
                try:
                    return redirect(url_for('student.student'))
                except:
                    pass
        
        # Show home page
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index: {e}")
        return render_template('index.html')

# Item detail page
@app.route('/item/<int:item_id>')
def item_detail(item_id):
    """Public item detail page"""
    try:
        if not db_available:
            return render_template('404.html'), 404
        
        from models import Item
        item = Item.query.get_or_404(item_id)
        return render_template('item.html', item=item)
    except Exception as e:
        logger.error(f"Error in item_detail: {e}")
        return render_template('404.html'), 404

# Dynamic image generation route
@app.route('/api/item/<int:item_id>/image')
def generate_item_image(item_id):
    """Generate item placeholder image on-the-fly"""
    try:
        from models import Item
        from PIL import Image, ImageDraw
        from io import BytesIO
        
        item = Item.query.get_or_404(item_id)
        
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
        
        color = colors.get(item.category, '#F5F5F5')
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[j:j+2], 16) for j in (0, 2, 4))
        
        img = Image.new('RGB', (400, 300), color=rgb)
        draw = ImageDraw.Draw(img)
        text = item.name[:40]
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        draw.text((x, y), text, fill=(64, 64, 64))
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        response = send_file(buf, mimetype='image/png', download_name=f'item_{item_id}.png')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except ImportError as e:
        logger.error(f"Import error generating image for item {item_id}: {e}")
        # Return error image in plain text for debugging
        return f"Error: PIL not available - {e}", 500
    except Exception as e:
        logger.error(f"Error generating image for item {item_id}: {e}", exc_info=True)
        return f"Error: {e}", 500


# Register blueprints if possible
try:
    from routes import register_blueprints
    register_blueprints(app)
    logger.info("Blueprints registered")
except Exception as e:
    logger.warning(f"Could not register blueprints: {e}")

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.debug
    )
