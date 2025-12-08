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
    sys.exit(0 if success else 1)
