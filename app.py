#!/usr/bin/env python
"""
Ultra-safe Flask app that works even if database is unavailable
This is the production version that runs on Render
"""
import os
import sys
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, g, redirect, url_for

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
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Inventarios</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f5f5f5; }
                h1 { color: #333; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <h1>Sistema de Inventarios Universitario</h1>
            <p>Inicializando sistema...</p>
            <p><small>Por favor recarga la página en unos momentos</small></p>
        </body>
        </html>
        ''', 200

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
