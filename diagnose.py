#!/usr/bin/env python
"""
Diagnóstico rápido de la aplicación - útil para debugging en Render
Uso: python diagnose.py
"""
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def diagnose():
    """Ejecuta diagnósticos de la aplicación"""
    logger.info("=" * 80)
    logger.info("DIAGNÓSTICO DEL SISTEMA - Sistema de Inventarios")
    logger.info("=" * 80)
    
    # 1. Verificar environment variables
    logger.info("\n📋 VARIABLES DE ENTORNO:")
    critical_vars = [
        'FLASK_ENV',
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DATABASE_URL',
        'APP_URL',
        'MAIL_USERNAME'
    ]
    
    for var in critical_vars:
        value = os.environ.get(var)
        if var == 'DATABASE_URL':
            # No mostrar URL completa por seguridad
            if value:
                logger.info(f"  ✅ {var}: Configurada (primeros 50 chars: {value[:50]}...)")
            else:
                logger.warning(f"  ❌ {var}: NO configurada")
        elif var in ['SECRET_KEY', 'JWT_SECRET_KEY']:
            if value:
                logger.info(f"  ✅ {var}: Configurada")
            else:
                logger.warning(f"  ❌ {var}: NO configurada")
        else:
            if value:
                logger.info(f"  ✅ {var}: {value}")
            else:
                logger.warning(f"  ❌ {var}: NO configurada")
    
    # 2. Verificar Python
    logger.info(f"\n🐍 PYTHON:")
    logger.info(f"  Version: {sys.version}")
    logger.info(f"  Executable: {sys.executable}")
    
    # 3. Verificar importaciones críticas
    logger.info(f"\n📦 IMPORTACIONES CRÍTICAS:")
    critical_imports = [
        ('Flask', 'flask'),
        ('Flask-SQLAlchemy', 'flask_sqlalchemy'),
        ('psycopg2', 'psycopg2'),
        ('Gunicorn', 'gunicorn'),
    ]
    
    for name, module in critical_imports:
        try:
            __import__(module)
            logger.info(f"  ✅ {name}: Instalado")
        except ImportError:
            logger.error(f"  ❌ {name}: NO instalado")
    
    # 4. Verificar conexión a BD
    logger.info(f"\n🗄️  BASE DE DATOS:")
    try:
        from app import app
        with app.app_context():
            from models import db
            try:
                result = db.session.execute('SELECT 1')
                logger.info(f"  ✅ Conexión exitosa a BD")
            except Exception as e:
                logger.error(f"  ❌ Error conectando a BD: {e}")
    except Exception as e:
        logger.error(f"  ❌ Error importando app: {e}")
        import traceback
        logger.error(f"  Traceback: {traceback.format_exc()}")
    
    # 5. Verificar estructura de directorios
    logger.info(f"\n📁 ESTRUCTURA DE DIRECTORIOS:")
    critical_dirs = [
        'templates',
        'static',
        'routes',
        'utils'
    ]
    
    for dir_name in critical_dirs:
        dir_path = os.path.join(os.getcwd(), dir_name)
        if os.path.exists(dir_path):
            logger.info(f"  ✅ {dir_name}/: Existe")
        else:
            logger.error(f"  ❌ {dir_name}/: NO existe")
    
    # 6. Verificar archivos críticos
    logger.info(f"\n📄 ARCHIVOS CRÍTICOS:")
    critical_files = [
        'app.py',
        'config.py',
        'models.py',
        'requirements.txt',
        'Procfile'
    ]
    
    for file_name in critical_files:
        file_path = os.path.join(os.getcwd(), file_name)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            logger.info(f"  ✅ {file_name}: Existe ({size} bytes)")
        else:
            logger.error(f"  ❌ {file_name}: NO existe")
    
    logger.info("\n" + "=" * 80)
    logger.info("DIAGNÓSTICO COMPLETADO")
    logger.info("=" * 80)

if __name__ == '__main__':
    diagnose()
