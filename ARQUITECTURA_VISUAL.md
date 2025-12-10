# 🏗️ DIAGRAMA DE ARQUITECTURA COMPLETO

## ARQUITECTURA GENERAL (VISTA DE CAPAS)

```
┌────────────────────────────────────────────────────────────────┐
│                     NAVEGADOR DEL USUARIO                       │
│                  (HTML, CSS, JavaScript)                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTP/HTTPS
                             ↓
┌────────────────────────────────────────────────────────────────┐
│                    SERVIDOR FLASK (app.py)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             APPLICATION FACTORY (create_app)              │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │ 1. Inicializar Flask                               │  │  │
│  │  │ 2. Cargar configuración (config.py)                │  │  │
│  │  │ 3. Inicializar BD (initialization.py)              │  │  │
│  │  │ 4. Registrar middleware (middleware.py)            │  │  │
│  │  │ 5. Registrar blueprints (routes/)                  │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────┬────────────────┘
             │ Procesa routes                     │ Maneja sesiones
             ↓                                    ↓
┌──────────────────────┐              ┌──────────────────────┐
│   ROUTES (5 módulos) │              │  MIDDLEWARE          │
├──────────────────────┤              ├──────────────────────┤
│ 1. auth.py           │              │ before_request()     │
│    - login           │              │ after_request()      │
│    - logout          │              │ error handlers       │
│    - register        │              │ inject_globals()     │
│                      │              └──────────────────────┘
│ 2. admin.py          │
│    - dashboard       │              ┌──────────────────────┐
│    - items (CRUD)    │              │  CORE (4 módulos)    │
│    - analytics       │              ├──────────────────────┤
│                      │              │ 1. initialization.py │
│ 3. student.py        │              │    - crear tablas    │
│    - rentals         │              │    - seed data       │
│    - statistics      │              │                      │
│                      │              │ 2. middleware.py     │
│ 4. api.py            │              │    - request/response│
│    - JSON endpoints  │              │                      │
│                      │              │ 3. public_routes.py  │
│ 5. nfc.py            │              │    - home, items     │
│    - QR codes        │              │                      │
└──────────┬───────────┘              │ 4. styles.py         │
           │                          │    - colores         │
           ↓                          └──────────────────────┘
┌──────────────────────────────────────────────────────────────┐
│                    TEMPLATES (views)                          │
│  templates/                                                   │
│  ├── base.html          (herencia de templates)              │
│  ├── admin/             (26 archivos HTML)                   │
│  ├── student/                                                │
│  └── ...                                                     │
└──────────┬───────────────────────────────────────────────────┘
           │ Render HTML
           ↓
┌──────────────────────────────────────────────────────────────┐
│                    STATIC (assets)                           │
│  ├── style.css         (diseño responsivo)                   │
│  ├── script.js         (interactividad)                      │
│  └── uploads/          (imágenes, QRs)                       │
└──────────┬───────────────────────────────────────────────────┘
           │ Query/Actualizar
           ↓
┌──────────────────────────────────────────────────────────────┐
│                   MODELS (orm)                               │
│  ├── User                                                    │
│  ├── Item                                                    │
│  ├── Transaction                                             │
│  ├── Supplier                                                │
│  ├── LoginAttempt                                            │
│  └── ...                                                     │
└──────────┬───────────────────────────────────────────────────┘
           │ SQL queries
           ↓
┌──────────────────────────────────────────────────────────────┐
│                  BASE DE DATOS                               │
│  DESARROLLO: SQLite (inventory.db)                           │
│  PRODUCCIÓN: PostgreSQL (Render)                             │
│                                                              │
│  Tables:                                                     │
│  ├── user              (usuarios admin/estudiantes)          │
│  ├── item              (productos)                           │
│  ├── transaction       (compras/rentas)                      │
│  ├── supplier          (proveedores)                         │
│  ├── purchase_order    (órdenes de compra)                   │
│  ├── login_attempt     (intentos fallidos)                   │
│  └── ...                                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## FLUJO DE UNA PETICIÓN HTTP

```
CLIENTE                          SERVIDOR                        BD
  │                               │                              │
  │─────GET /item/42───────────→  │                              │
  │                               │ 1. before_request()          │
  │                               │    - Cargar g.user           │
  │                               │    - Verificar sesión        │
  │                               │                              │
  │                               │ 2. Buscar ruta               │
  │                               │    public_routes.py          │
  │                               │    → item_detail(42)         │
  │                               │                              │
  │                               │ 3. Query a BD                │
  │                               │                              │
  │                               │    SELECT * FROM item        │
  │                               │    WHERE id = 42             │
  │                               ├─────────────────────────────→│
  │                               │                              │
  │                               │←─────────┐ Item #42: "Libro" │
  │                               │          │ price=50, stock=10│
  │                               │          │                  │
  │                               │ 4. Generar imagen            │
  │                               │    PIL: crear PNG            │
  │                               │                              │
  │                               │ 5. Render template           │
  │                               │    item.html + data          │
  │                               │                              │
  │                               │ 6. after_request()           │
  │                               │    - Agregar headers         │
  │                               │                              │
  │←──────200 OK + HTML───────────│                              │
  │  (página renderizada)         │                              │
  │                               │                              │
  └─ Navegador renderiza ─────────┘
```

---

## PATRÓN MVC APLICADO

```
┌─────────────────────────────────────────────────┐
│                   ARQUITECTURA MVC               │
└─────────────────────────────────────────────────┘

                        URL REQUEST
                            │
                            ↓
                    ┌───────────────┐
                    │  CONTROLLER   │
                    │  (routes/)    │
                    └───────┬───────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ↓                ↓                ↓
      Query BD        Logic Negocio    Template
           │                │                │
           ↓                ↓                ↓
      ┌─────────┐  ┌──────────────┐  ┌─────────┐
      │ MODEL   │  │ CONTROLLER   │  │ VIEW    │
      │ (ORM)   │  │ (Lógica)     │  │ (HTML)  │
      └────┬────┘  └──────┬───────┘  └────┬────┘
           │               │               │
      ├─ User       ├─ admin.py       ├─ admin/*.html
      ├─ Item       ├─ student.py     ├─ student/*.html
      ├─ Transaction├─ auth.py        ├─ base.html
      └─ Supplier   └─ api.py         └─ index.html
```

---

## MÓDULOS CORE - INTERCONEXIÓN

```
app.py (55 líneas - Application Factory)
    │
    ├─→ config.py (92 líneas)
    │   └─ Carga configuración por entorno
    │
    ├─→ core/initialization.py (278 líneas)
    │   ├─ init_database()
    │   ├─ init_mail()
    │   └─ create_tables_and_seed()
    │
    ├─→ core/middleware.py (90 líneas)
    │   ├─ before_request()
    │   ├─ after_request()
    │   ├─ error handlers (404, 500, etc)
    │   └─ configure_session()
    │
    ├─→ core/public_routes.py (118 líneas)
    │   ├─ /health
    │   ├─ / (index)
    │   ├─ /item/<id>
    │   └─ /api/item/<id>/image
    │
    ├─→ core/styles.py (34 líneas)
    │   ├─ CATEGORY_COLORS
    │   ├─ hex_to_rgb()
    │   └─ get_category_color()
    │
    ├─→ models.py (254 líneas)
    │   └─ Definiciones de modelos ORM
    │
    ├─→ routes/auth.py
    │   ├─ login/logout/register
    │   └─ 2FA setup
    │
    ├─→ routes/admin.py
    │   ├─ CRUD de items
    │   ├─ analytics
    │   └─ predictive
    │
    ├─→ routes/student.py
    │   ├─ dashboard
    │   ├─ rentals
    │   └─ statistics
    │
    ├─→ routes/api.py
    │   └─ JSON endpoints
    │
    └─→ routes/nfc.py
        └─ QR codes
```

---

## FLUJO DE INICIALIZACIÓN (app startup)

```
$ python app.py

1. Importar Flask
   └─ from flask import Flask

2. Ejecutar app = create_app()
   └─ app.py → create_app() function

3. config.py carga configuración
   ├─ FLASK_ENV = 'development'
   ├─ DATABASE_URL = 'sqlite:///inventory.db'
   └─ SECRET_KEY = 'dev-secret'

4. core/initialization.py
   ├─ init_database(app)
   │  └─ db.init_app(app)
   ├─ init_mail(app)
   │  └─ Mail(app) si credenciales
   └─ create_tables_and_seed(app, db)
      ├─ db.create_all()
      │  ├─ CREATE TABLE user
      │  ├─ CREATE TABLE item
      │  ├─ CREATE TABLE transaction
      │  └─ ... (8 tablas más)
      ├─ _create_admin_user()
      │  └─ INSERT INTO user VALUES ('admin', hash('admin123'), 'admin')
      ├─ _seed_products()
      │  └─ INSERT 200+ items desde seed_products.py
      ├─ _generate_placeholder_images()
      │  └─ Generar PNG para cada item
      └─ _seed_example_data()
         ├─ INSERT 4 suppliers
         ├─ INSERT 4 students
         ├─ INSERT 20 transactions
         └─ INSERT 15 purchase orders

5. core/middleware.py
   ├─ register_middleware()
   ├─ before_request hook
   ├─ after_request hook
   └─ error handlers

6. routes/ (Blueprints)
   ├─ register_blueprints(app)
   ├─ app.register_blueprint(auth_bp)
   ├─ app.register_blueprint(admin_bp)
   ├─ app.register_blueprint(student_bp)
   ├─ app.register_blueprint(api_bp)
   └─ app.register_blueprint(nfc_bp)

7. Servidor escuchando
   └─ 127.0.0.1:5000 (development)
      o 0.0.0.0:5000 (producción)

✅ App lista para requests
```

---

## SEGURIDAD - CAPAS

```
┌────────────────────────────────────────────┐
│              USUARIO HTTP                   │
└─────────────────────┬──────────────────────┘
                      │
              ┌───────▼────────┐
              │  FLASK ROUTING │
              │ (Verificar URL)│
              └───────┬────────┘
                      │
          ┌───────────▼───────────┐
          │ AUTHENTICATION CHECK  │
          │ (@login_required)     │
          │ if not g.user: login  │
          └───────┬───────────────┘
                  │
        ┌─────────▼──────────┐
        │ RATE LIMITING      │
        │ Max 5 intentos     │
        │ en 15 minutos      │
        └─────────┬──────────┘
                  │
    ┌─────────────▼───────────────┐
    │ VALIDAR CSRF TOKEN          │
    │ En formularios POST          │
    └─────────────┬───────────────┘
                  │
   ┌──────────────▼──────────────┐
   │ SANITIZAR INPUTS            │
   │ Evitar SQL injection        │
   │ ORM escapa automáticamente  │
   └──────────────┬──────────────┘
                  │
   ┌──────────────▼──────────────┐
   │ EJECUTAR RUTA               │
   │ (Controller/Business Logic) │
   └──────────────┬──────────────┘
                  │
   ┌──────────────▼──────────────┐
   │ QUERY BD                    │
   │ (Parameterized queries)     │
   └──────────────┬──────────────┘
                  │
   ┌──────────────▼──────────────┐
   │ AGREGA HEADERS DE SEGURIDAD │
   │ - X-Content-Type-Options    │
   │ - Set-Cookie flags          │
   └──────────────┬──────────────┘
                  │
        ┌─────────▼──────────┐
        │ RETORNA RESPONSE   │
        │ (Encriptado si HTTPS)
        └──────────────────────┘
```

---

## ESTRUCTURA BD (MODELOS & RELACIONES)

```
                    USER
                   (id) ◄──────────────┐
                    │                  │
        ┌───────────┼──────┬───────┐   │
        │           │      │       │   │
        ▼           ▼      ▼       ▼   │
   LoginAttempt Transaction ApiKey     │
                        │               │
                        ├─────┬────────┘ FOREIGN KEY
                        │     │
                        ▼     ▼
                       ITEM   SUPPLIER
                        │
                        │
                        ▼
                PURCHASE_ORDER
```

---

## DESPLIEGUE EN PRODUCCIÓN (RENDER)

```
┌──────────────┐
│  GitHub Repo │
│ (push code)  │
└──────┬───────┘
       │ git push origin master
       ▼
┌─────────────────────────────┐
│  Render (detecta cambios)   │
│  1. Pull from GitHub        │
│  2. pip install requirements│
│  3. python app.py (startup) │
│  4. gunicorn app:app        │
└──────┬──────────────────────┘
       │ Connect
       ▼
┌─────────────────────────────┐
│  Render PostgreSQL Database │
│  (replaces SQLite)          │
│  DATABASE_URL=postgres://..│
└─────────────────────────────┘

URLS:
- Web:  https://mi-app.onrender.com/
- API:  https://mi-app.onrender.com/api/items
- BD:   dpg-xxxxx.onrender.com:5432
```

---

## COMPARATIVA: LOCAL vs PRODUCCIÓN

```
DESARROLLO (Local)
├─ python app.py
├─ SQLite (inventory.db)
├─ http://localhost:5000
├─ SQLALCHEMY_ECHO = True (debug)
└─ DEBUG = True (hot reload)

PRODUCCIÓN (Render)
├─ gunicorn app:app
├─ PostgreSQL (Render Cloud)
├─ https://mi-app.onrender.com/
├─ SQLALCHEMY_ECHO = False (performance)
├─ DEBUG = False (seguridad)
└─ Connection pooling optimizado
```

---

## ESTADÍSTICAS FINALES

```
PROYECTO v2.0
│
├─ CÓDIGO
│  ├─ Python: 2,500+ líneas
│  ├─ HTML/Templates: 1,200 líneas
│  ├─ CSS: 1,200 líneas
│  └─ Total: ~4,900 líneas
│
├─ MODELOS
│  └─ 6 tablas BD:
│     ├─ user (usuarios)
│     ├─ item (productos)
│     ├─ transaction (compras/rentas)
│     ├─ supplier (proveedores)
│     ├─ login_attempt (auditoría)
│     └─ api_key (APIs)
│
├─ RUTAS
│  ├─ 6 públicas (core/public_routes.py)
│  ├─ 20+ admin (routes/admin.py)
│  ├─ 5+ student (routes/student.py)
│  ├─ 10+ API (routes/api.py)
│  └─ 5+ auth (routes/auth.py)
│  └─ Total: 48 rutas
│
├─ DATOS DE PRUEBA
│  ├─ 200+ productos
│  ├─ 4 proveedores
│  ├─ 4 estudiantes
│  ├─ 1 admin
│  └─ 20+ transacciones demo
│
└─ SEGURIDAD
   ├─ Password hashing (PBKDF2-SHA256)
   ├─ 2FA (TOTP)
   ├─ Rate limiting (fuerza bruta)
   ├─ CSRF protection
   ├─ SQL injection prevention (ORM)
   ├─ XSS protection
   ├─ Auditoría completa
   └─ Logs de seguridad
```

---

**Esta arquitectura es ESCALABLE, SEGURA y MANTENIBLE.**
