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
    try:
        # Create Flask app
        app = Flask(__name__)
        logger.info("Flask app created")
        
        # Load configuration
        config_name = os.getenv('FLASK_ENV', 'development')
        logger.info(f"Loading config for environment: {config_name}")
        
        try:
            from config import config
            app.config.from_object(config.get(config_name, config['development']))
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise
        
        # Configure session
        try:
            from core.middleware import configure_session
            configure_session(app)
            logger.info("Session configured")
        except Exception as e:
            logger.error(f"Failed to configure session: {e}")
            raise
        
        # Initialize database
        try:
            from core.initialization import init_database, init_mail, create_tables_and_seed
            db, db_available = init_database(app)
            mail = init_mail(app)
            logger.info(f"Database initialized. Available: {db_available}")
            
            # Store in app for access in routes
            app.db = db
            app.db_available = db_available
            app.mail = mail
            
            # Create tables and seed data
            if db_available:
                try:
                    create_tables_and_seed(app, db)
                    logger.info("Tables and seed data created")
                except Exception as e:
                    logger.error(f"Failed to create tables/seed data: {e}")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            app.db_available = False
        
        # Register middleware
        try:
            from core.middleware import register_middleware
            register_middleware(app, getattr(app, 'db_available', False))
            logger.info("Middleware registered")
        except Exception as e:
            logger.error(f"Failed to register middleware: {e}")
            raise
        
        # Register public routes
        try:
            from core.public_routes import public_bp
            app.register_blueprint(public_bp)
            logger.info("Public blueprint registered")
        except Exception as e:
            logger.error(f"Failed to register public blueprint: {e}")
        
        # Register application blueprints (admin, student, auth, api, nfc)
        try:
            from routes import register_blueprints
            register_blueprints(app)
            logger.info("Application blueprints registered successfully")
        except Exception as e:
            logger.warning(f"Could not register blueprints: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info("App creation completed successfully")
        return app
    
    except Exception as e:
        logger.error(f"Critical error during app creation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise


# ============================================================================
# CREATE AND CONFIGURE APP
# ============================================================================
try:
    app = create_app()
    logger.info("Application started successfully")
except Exception as e:
    logger.critical(f"Failed to create app: {e}")
    raise

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=app.debug
    )

