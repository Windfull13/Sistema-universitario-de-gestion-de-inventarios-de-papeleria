#!/usr/bin/env python
"""
Script para limpiar la BD completamente y recrearla
Ejecutar en phase 'release' de Render
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_and_recreate_db():
    """Drop all tables and recreate them"""
    logger.info("=" * 70)
    logger.info("LIMPIANDO Y RECREANDO BASE DE DATOS")
    logger.info("=" * 70)
    
    try:
        # Import here so we use the current app.py
        logger.info("Importing Flask app...")
        from app import app, db
        logger.info("✓ App imported")
        
        with app.app_context():
            # Drop all
            logger.info("[1/2] Eliminando todas las tablas...")
            try:
                db.drop_all()
                logger.info("✓ Tablas eliminadas")
            except Exception as e:
                logger.warning(f"Drop failed (might be empty): {e}")
            
            # Create all
            logger.info("[2/2] Recreando tablas...")
            db.create_all()
            logger.info("✓ Tablas recreadas")
            
            # List tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Tablas creadas: {tables}")
        
        logger.info("=" * 70)
        logger.info("✓ BASE DE DATOS COMPLETAMENTE RENOVADA")
        logger.info("=" * 70)
        return True
        
    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = clear_and_recreate_db()
    sys.exit(0 if success else 1)
