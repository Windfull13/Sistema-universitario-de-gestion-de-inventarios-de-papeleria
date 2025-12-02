#!/usr/bin/env python
"""Script para migrar la base de datos existente añadiendo columnas faltantes"""

import os
import sqlite3
from pathlib import Path

os.chdir(Path(__file__).parent)

def migrate_database():
    """Añadir columnas faltantes a la tabla item"""
    db_path = 'inventory.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Base de datos no encontrada: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración de base de datos...")
        
        # Obtener información de la tabla item
        cursor.execute("PRAGMA table_info(item)")
        columns = {row[1] for row in cursor.fetchall()}
        
        print(f"✅ Columnas actuales en 'item': {len(columns)}")
        
        # Columnas que necesitamos añadir
        new_columns = [
            ('supplier_id', 'INTEGER'),
            ('rotation_score', 'FLOAT'),
            ('last_sale_date', 'DATETIME'),
            ('sales_velocity', 'FLOAT'),
        ]
        
        columns_added = 0
        for col_name, col_type in new_columns:
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE item ADD COLUMN {col_name} {col_type}")
                    print(f"   ✅ Añadida columna: {col_name} ({col_type})")
                    columns_added += 1
                except sqlite3.OperationalError as e:
                    print(f"   ⚠️  Columna ya existe o error: {col_name}")
            else:
                print(f"   ✓ Columna ya existe: {col_name}")
        
        conn.commit()
        
        # Verificar que Supplier y PurchaseOrder existan
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='supplier'"
        )
        if not cursor.fetchone():
            print("   ⚠️  Tabla 'supplier' no existe - será creada por SQLAlchemy")
        else:
            print("   ✓ Tabla 'supplier' existe")
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='purchase_order'"
        )
        if not cursor.fetchone():
            print("   ⚠️  Tabla 'purchase_order' no existe - será creada por SQLAlchemy")
        else:
            print("   ✓ Tabla 'purchase_order' existe")
        
        conn.close()
        
        print(f"\n✅ Migración completada - {columns_added} columnas añadidas")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == '__main__':
    success = migrate_database()
    
    if success:
        # Ahora usar Flask para crear las tablas que falten
        print("\n🔄 Creando tablas faltantes con SQLAlchemy...")
        try:
            from app import app, db
            with app.app_context():
                db.create_all()
            print("✅ Todas las tablas están listas")
        except Exception as e:
            print(f"❌ Error al crear tablas: {e}")
