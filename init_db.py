#!/usr/bin/env python
"""
Database initialization script
Ejecutar una sola vez para crear todas las tablas
"""
import os
import sys
from app import app, db
from models import User, LoginAttempt, ActiveSession, ApiKey, Item, Transaction, Supplier, PurchaseOrder

def init_database():
    """Create all database tables"""
    with app.app_context():
        print("=" * 70)
        print("INICIANDO CREACIÓN DE TABLAS DE BASE DE DATOS")
        print("=" * 70)
        
        try:
            # Drop all tables first (development only)
            print("\n[1/3] Eliminando tablas existentes...")
            db.drop_all()
            print("✓ Tablas eliminadas")
            
            # Create all tables
            print("\n[2/3] Creando tablas...")
            db.create_all()
            print("✓ Tablas creadas exitosamente")
            
            # Verify tables exist
            print("\n[3/3] Verificando tablas...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'user', 
                'login_attempt', 
                'active_session', 
                'api_key', 
                'item', 
                'transaction', 
                'supplier', 
                'purchase_order'
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"✗ FALTA: {', '.join(missing_tables)}")
                return False
            
            print(f"✓ Todas las tablas existen: {', '.join(tables)}")
            
            print("\n" + "=" * 70)
            print("✓ BASE DE DATOS INICIALIZADA CORRECTAMENTE")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"\n✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
