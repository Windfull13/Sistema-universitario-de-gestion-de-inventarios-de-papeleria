#!/usr/bin/env python
"""Check if Render database is empty"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn_string = 'postgresql://db_sistema_inventarios_56hg_user:m1W0vZPRU8pACWLMsffoQwro0BXWCNhR@dpg-d4rl4r3e5dus73d6du9g-a/db_sistema_inventarios_56hg'

try:
    print("Conectando a la base de datos...")
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    
    print("Obteniendo lista de tablas...")
    # Get all tables
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cur.fetchall()
    
    if not tables:
        print('\n✓ BASE DE DATOS ESTÁ COMPLETAMENTE VACÍA')
    else:
        print(f'\n✓ ENCONTRADAS {len(tables)} TABLA(S):')
        for table in tables:
            table_name = table[0]
            print(f'\n  - {table_name}')
            
            # Count rows in each table
            cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            count = cur.fetchone()[0]
            print(f'    Filas: {count}')
    
    cur.close()
    conn.close()
    print('\n✓ Conexión exitosa')
    
except Exception as e:
    print(f'✗ ERROR: {e}')
    import traceback
    traceback.print_exc()
