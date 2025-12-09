#!/usr/bin/env python
"""
Script para limpiar la BD completamente y recrearla
Ejecutar en phase 'release' de Render
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def check_database_status():
    """Check what tables exist in the database"""
    try:
        from sqlalchemy import inspect, create_engine
        from config import config
        
        logger.info("=" * 70)
        logger.info("VERIFICANDO ESTADO DE LA BASE DE DATOS")
        logger.info("=" * 70)
        
        config_name = os.getenv('FLASK_ENV', 'development')
        cfg = config.get(config_name, config['development'])
        
        logger.info(f"Conectando a: {cfg.get('SQLALCHEMY_DATABASE_URI', 'unknown')[:50]}...")
        
        engine = create_engine(cfg.get('SQLALCHEMY_DATABASE_URI', ''))
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("✓ Base de datos VACÍA (sin tablas)")
        else:
            logger.info(f"✓ Base de datos tiene {len(tables)} tabla(s):")
            for table in tables:
                logger.info(f"  - {table}")
        
        return tables
        
    except Exception as e:
        logger.warning(f"Could not inspect database: {e}")
        return []

def clear_and_recreate_db():
    """Drop all tables and recreate them"""
    logger.info("=" * 70)
    logger.info("LIMPIANDO Y RECREANDO BASE DE DATOS")
    logger.info("=" * 70)
    
    try:
        # Import here so we use the current app.py
        logger.info("Importando Flask app...")
        from app import app, db
        logger.info("✓ App importada")
        
        with app.app_context():
            # Drop all
            logger.info("[1/3] Eliminando todas las tablas...")
            try:
                db.drop_all()
                logger.info("✓ Tablas eliminadas")
            except Exception as e:
                logger.warning(f"Drop failed (might be empty): {e}")
            
            # Create all
            logger.info("[2/3] Recreando tablas...")
            db.create_all()
            logger.info("✓ Tablas recreadas")
            
            # List tables
            logger.info("[3/3] Verificando tablas creadas...")
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if tables:
                logger.info(f"✓ Tablas creadas: {', '.join(tables)}")
            else:
                logger.error("✗ ERROR: No se crearon las tablas!")
                return False
        
        logger.info("=" * 70)
        logger.info("✓ BASE DE DATOS COMPLETAMENTE RENOVADA")
        logger.info("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"ERROR CRITICO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # First check status
    check_database_status()
    
    # Then clean and recreate
    success = clear_and_recreate_db()
    
    if success:
        # Create default admin user
        logger.info("=" * 70)
        logger.info("CREANDO USUARIO ADMIN DE PRUEBA")
        logger.info("=" * 70)
        try:
            from app import app, db
            from models import User
            from werkzeug.security import generate_password_hash
            
            with app.app_context():
                # Check if admin already exists
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    logger.info("✓ Usuario admin ya existe")
                else:
                    # Create admin user
                    admin = User(
                        username='admin',
                        email='admin@sistema.local',
                        password_hash=generate_password_hash('admin123'),
                        role='admin'
                    )
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("✓ Usuario admin creado")
                    logger.info("  Usuario: admin")
                    logger.info("  Contraseña: admin123")
                    
        except Exception as e:
            logger.warning(f"Could not create admin user: {e}")
        
        # Now seed products
        logger.info("=" * 70)
        logger.info("AGREGANDO PRODUCTOS A LA BASE DE DATOS")
        logger.info("=" * 70)
        try:
            from app import app, db
            from models import Item
            
            with app.app_context():
                # Check if products already exist
                existing = Item.query.first()
                if existing:
                    count = Item.query.count()
                    logger.info(f"✓ Base de datos ya tiene {count} productos")
                else:
                    # Import products list
                    from seed_products import PRODUCTS
                    
                    total_added = 0
                    for category, products in PRODUCTS.items():
                        logger.info(f"📂 Categoría: {category}")
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
                            total_added += 1
                        
                        db.session.commit()
                    
                    logger.info(f"✓ {total_added} PRODUCTOS AGREGADOS EXITOSAMENTE")
                    
        except Exception as e:
            logger.warning(f"Could not seed products: {e}")
    
    sys.exit(0 if success else 1)
