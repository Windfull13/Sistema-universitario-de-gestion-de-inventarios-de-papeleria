#!/usr/bin/env python
"""
Script para limpiar la BD completamente y recrearla
Ejecutar solo una vez en producción
"""
import os
import sys
from app import app, db

def clear_and_recreate_db():
    """Drop all tables and recreate them"""
    with app.app_context():
        print("=" * 70)
        print("LIMPIANDO Y RECREANDO BASE DE DATOS")
        print("=" * 70)
        
        try:
            # Drop all
            print("\n[1/2] Eliminando todas las tablas...")
            db.drop_all()
            print("✓ Tablas eliminadas")
            
            # Create all
            print("\n[2/2] Recreando tablas...")
            db.create_all()
            print("✓ Tablas recreadas")
            
            print("\n" + "=" * 70)
            print("✓ BASE DE DATOS COMPLETAMENTE RENOVADA")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = clear_and_recreate_db()
    sys.exit(0 if success else 1)
