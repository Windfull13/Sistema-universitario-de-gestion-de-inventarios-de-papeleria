#!/usr/bin/env python
"""
Script de diagnóstico - Verificar qué está fallando en startup
"""
import sys
import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("DIAGNÓSTICO DE STARTUP - SISTEMA DE INVENTARIOS")
print("=" * 80)

# Test 1: Importar Flask
print("\n[1/10] Importando Flask...")
try:
    from flask import Flask
    print("✅ Flask importado correctamente")
except Exception as e:
    print(f"❌ Error importando Flask: {e}")
    sys.exit(1)

# Test 2: Importar config
print("\n[2/10] Importando configuración...")
try:
    from config import config
    print(f"✅ Configuración importada. Entornos: {list(config.keys())}")
except Exception as e:
    print(f"❌ Error importando config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Crear app básica
print("\n[3/10] Creando app Flask...")
try:
    app = Flask(__name__)
    print("✅ App Flask creada")
except Exception as e:
    print(f"❌ Error creando app: {e}")
    sys.exit(1)

# Test 4: Cargar configuración
print("\n[4/10] Cargando configuración en app...")
try:
    app.config.from_object(config['development'])
    print("✅ Configuración cargada")
except Exception as e:
    print(f"❌ Error cargando config: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Inicializar BD
print("\n[5/10] Inicializando base de datos...")
try:
    from core.initialization import init_database, init_mail
    db, db_available = init_database(app)
    print(f"✅ BD inicializada. Disponible: {db_available}")
except Exception as e:
    print(f"❌ Error inicializando BD: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Mail
print("\n[6/10] Inicializando Mail...")
try:
    mail = init_mail(app)
    print(f"✅ Mail inicializado. Disponible: {mail is not None}")
except Exception as e:
    print(f"❌ Error inicializando Mail: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Session
print("\n[7/10] Configurando sesiones...")
try:
    from core.middleware import configure_session
    configure_session(app)
    print("✅ Sesiones configuradas")
except Exception as e:
    print(f"❌ Error configurando sesiones: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Middleware
print("\n[8/10] Registrando middleware...")
try:
    from core.middleware import register_middleware
    register_middleware(app, db_available)
    print("✅ Middleware registrado")
except Exception as e:
    print(f"❌ Error registrando middleware: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 9: Public routes
print("\n[9/10] Registrando rutas públicas...")
try:
    from core.public_routes import public_bp
    app.register_blueprint(public_bp)
    print("✅ Rutas públicas registradas")
except Exception as e:
    print(f"❌ Error registrando rutas públicas: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 10: Blueprints
print("\n[10/10] Registrando blueprints...")
try:
    from routes import register_blueprints
    register_blueprints(app)
    print("✅ Blueprints registrados")
except Exception as e:
    print(f"❌ Error registrando blueprints: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ TODOS LOS TESTS PASARON - APP LISTA PARA EJECUTAR")
print("=" * 80)

# Ver rutas registradas
print("\n📋 RUTAS REGISTRADAS:")
routes = {}
for rule in app.url_map.iter_rules():
    if rule.endpoint != 'static':
        method = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        routes[rule.rule] = f"{method} → {rule.endpoint}"

for route, info in sorted(routes.items()):
    print(f"  {route:40} {info}")

print(f"\nTotal rutas: {len(routes)}")
