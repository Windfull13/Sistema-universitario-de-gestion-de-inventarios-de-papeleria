#!/usr/bin/env python
"""
Sistema de Gestión de Inventario - Papelería Universitaria
Production-grade Flask application with modular architecture
"""
import os
import logging
from flask import Flask

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)


# ============================================================================
# APPLICATION FACTORY
# ============================================================================
def create_app():
    """Application factory function"""
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
    
    # Configure session
    from core.middleware import configure_session
    configure_session(app)
    
    # Initialize database
    from core.initialization import init_database, init_mail, create_tables_and_seed
    db, db_available = init_database(app)
    mail = init_mail(app)
    
    # Store in app for access in routes
    app.db = db
    app.db_available = db_available
    app.mail = mail
    
    # Create tables and seed data
    if db_available:
        create_tables_and_seed(app, db)
    
    # Register middleware
    from core.middleware import register_middleware
    register_middleware(app, db_available)
    
    # Register public routes
    from core.public_routes import public_bp
    app.register_blueprint(public_bp)
    
    # Register application blueprints (admin, student, auth, api, nfc)
    try:
        from routes import register_blueprints
        register_blueprints(app)
        logger.info("Blueprints registered successfully")
    except Exception as e:
        logger.warning(f"Could not register blueprints: {e}")
    
    return app


# ============================================================================
# CREATE AND CONFIGURE APP
# ============================================================================
app = create_app()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.debug
    )
