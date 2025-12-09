#!/usr/bin/env python
"""
Create default admin user for testing
"""
import os
import sys
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create a default admin user"""
    with app.app_context():
        print("=" * 70)
        print("CREANDO USUARIO ADMIN DE PRUEBA")
        print("=" * 70)
        
        try:
            # Check if admin already exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print("✓ Usuario admin ya existe")
                return True
            
            # Create admin user
            print("\nCreando usuario admin...")
            admin = User(
                username='admin',
                email='admin@sistema.local',
                password_hash=generate_password_hash('admin123'),
                role='admin'
            )
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Usuario admin creado exitosamente")
            print("\nCredenciales de prueba:")
            print("  Usuario: admin")
            print("  Contraseña: admin123")
            print("\n⚠️  CAMBIA ESTAS CREDENCIALES EN PRODUCCIÓN")
            
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1)
