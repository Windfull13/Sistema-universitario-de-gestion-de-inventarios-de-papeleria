# 🎯 RESUMEN VISUAL PARA ENTENDER RÁPIDO

## ¿QUÉ HACE CADA ARCHIVO?

### 📱 PUNTO DE ENTRADA
```
app.py (55 líneas)
└─ Inicia Flask
└─ Carga configuración
└─ Inicializa base de datos
└─ Registra módulos (blueprints)
```

### 🗄️ BASE DE DATOS
```
models.py (254 líneas)
├─ User        → Usuarios (admin, estudiantes)
├─ Item        → Productos de papelería
├─ Transaction → Compras y rentas
├─ Supplier    → Proveedores
├─ LoginAttempt→ Intentos de login
└─ ApiKey      → Claves de API
```

### ⚙️ CONFIGURACIÓN
```
config.py (92 líneas)
├─ DATABASE_URL    → SQLite (desarrollo) o PostgreSQL (producción)
├─ SECRET_KEY      → Encripción de sesiones
├─ SESSION_COOKIE_* → Seguridad de cookies
└─ APP_URL         → URL para QRs y emails
```

---

## NÚCLEO (CORE/) - 4 MÓDULOS

### 1️⃣ initialization.py (278 líneas)
**¿Qué hace?**
- Crea las tablas de base de datos
- Carga 200+ productos desde `seed_products.py`
- Genera imágenes PNG automáticamente
- Crea usuarios de prueba
- Siembra datos de ejemplo

**Equivalente en SQL:**
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE item (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price FLOAT,
    stock INTEGER
);

INSERT INTO item VALUES (1, 'Papel A4', 'Papeles', 5.00, 100);
INSERT INTO item VALUES (2, 'Lapicero', 'Escritura', 1.50, 500);
-- ... 200+ productos más
```

### 2️⃣ middleware.py (90 líneas)
**¿Qué hace?**
- Ejecuta código ANTES de cada request (cargar usuario)
- Ejecuta código DESPUÉS de cada request (agregar headers)
- Maneja errores 404, 500, etc.
- Agrega variables globales a templates

**Flujo:**
```
Request HTTP
    ↓
[BEFORE_REQUEST] ← middleware.py carga g.user
    ↓
Ejecutar ruta (routes/)
    ↓
[AFTER_REQUEST] ← middleware.py agrega headers
    ↓
Response HTTP al navegador
```

### 3️⃣ public_routes.py (118 líneas)
**¿Qué hace?**
- Rutas sin autenticación requerida
- `/health` → Verificar que app está viva (para Render)
- `/` → Home page
- `/item/<id>` → Ver detalles de un producto
- `/api/item/<id>/image` → Generar imagen dinámicamente

**Ejemplo:**
```
GET http://localhost:5000/item/42
├─ Query: SELECT * FROM item WHERE id = 42
├─ Generate: Crear imagen PNG desde PIL
└─ Response: Mostrar template item.html
```

### 4️⃣ styles.py (34 líneas)
**¿Qué hace?**
- Define 12 colores para categorías de productos
- Convierte hexadecimal (#E8F5E9) a RGB (232, 245, 233)
- Usado por initialization.py e public_routes.py

**Ejemplo:**
```python
get_category_color('Papeles')  # #E8F5E9 (verde pastel)
get_category_color('Escritura')  # #F3E5F5 (púrpura pastel)
```

---

## RUTAS (ROUTES/) - 5 MÓDULOS

### 1️⃣ auth.py - AUTENTICACIÓN
```python
POST /login              → Loguear usuario
GET  /logout             → Cerrar sesión
POST /register           → Registrar nuevo estudiante
POST /forgot-password    → Recuperar contraseña
POST /setup-2fa          → Activar 2FA
```

**¿Cómo funciona?**
```
1. Usuario entra password
2. Comparar con hash en BD: check_password_hash(hash_bd, password_usuario)
3. Si coincide, guardar en sesión: session['user_id'] = user.id
4. En próximos requests, middleware carga g.user desde sesión
```

### 2️⃣ admin.py - PANEL ADMINISTRATIVO
```python
GET  /admin/                    → Dashboard (estadísticas)
GET  /admin/items               → Listar productos
POST /admin/items               → Crear producto
GET  /admin/edit/<id>           → Formulario de edición
POST /admin/edit/<id>           → Guardar cambios
GET  /admin/delete/<id>         → Eliminar producto
GET  /admin/analytics           → Gráficos y reportes
GET  /admin/predictive          → Predicción con IA
GET  /admin/transactions        → Historial
GET  /admin/security-log        → Auditoría
GET  /admin/settings            → Configuración
```

**Funcionalidades:**
- CRUD de productos (Create, Read, Update, Delete)
- Estadísticas en dashboard
- Análisis predictivo
- Auditoría de seguridad

### 3️⃣ student.py - PORTAL DE ESTUDIANTES
```python
GET  /student/                  → Mi dashboard
GET  /student/rentals           → Mis rentas activas
POST /student/request-extension → Pedir extensión de renta
GET  /student/statistics        → Mis estadísticas
GET  /student/purchase-history  → Historial de compras
```

**Funcionalidades:**
- Ver rentas activas
- Solicitar extensión
- Ver historial

### 4️⃣ api.py - API REST (JSON)
```python
GET  /api/items                 → Lista de productos
GET  /api/item/<id>             → Detalles de un producto
GET  /api/user/profile          → Perfil del usuario
POST /api/item/<id>/buy         → Comprar producto
POST /api/item/<id>/rent        → Rentar producto
```

**Respuesta JSON:**
```json
GET /api/items
{
  "items": [
    {
      "id": 1,
      "name": "Papel A4",
      "category": "Papeles",
      "price": 5.00,
      "stock": 100,
      "rentable": false
    }
  ]
}
```

### 5️⃣ nfc.py - CÓDIGOS QR
```python
GET /nfc/qr/<id>                → Generar código QR
POST /nfc/scan                  → Procesar escaneo
GET /nfc-control                → Control panel
```

**¿Cómo funciona?**
```
1. Admin genera QR para producto #42
2. Se codifica URL: https://mi-app.onrender.com/item/42
3. Se genera imagen PNG con código QR
4. Estudiante escanea con smartphone
5. Se abre: /item/42 (detalle del producto)
```

---

## VISTAS (TEMPLATES/) - 26 ARCHIVOS HTML

### Estructura:
```
templates/
├── base.html                    ← Template base (header, footer, nav)
│   └─ Todos los otros templates heredan de este
│
├── index.html                   ← Home page
├── item.html                    ← Detalle de producto (público)
├── login.html                   ← Login
├── register.html                ← Registro de estudiantes
│
├── admin/
│   ├── dashboard.html           ← Estadísticas principales
│   ├── items.html               ← Listar productos
│   ├── add_item.html            ← Formulario crear producto
│   ├── edit_item.html           ← Formulario editar producto
│   ├── analytics.html           ← Gráficos (Chart.js)
│   ├── predictive.html          ← Predicciones con IA
│   ├── transactions.html        ← Historial de compras/rentas
│   ├── security_log.html        ← Registro de auditoría
│   ├── rental_extensions.html   ← Solicitudes de extensión
│   ├── suppliers.html           ← Gestión de proveedores
│   ├── api_keys.html            ← Control de API keys
│   └── settings.html            ← Configuración de la app
│
└── student/
    ├── dashboard.html           ← Mi dashboard
    ├── rentals.html             ← Mis rentas activas
    ├── statistics.html          ← Mis estadísticas
    └── purchase_history.html    ← Historial de compras
```

### ¿Cómo funcionan?

**Template example:**
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}Papelería Universitaria{% endblock %}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        {% if current_user %}
            Logueado como: {{ current_user.username }}
            <a href="/logout">Logout</a>
        {% else %}
            <a href="/login">Login</a>
        {% endif %}
    </nav>
    
    {% block content %}{% endblock %}
</body>
</html>
```

**Template heredado:**
```html
<!-- templates/item.html -->
{% extends "base.html" %}

{% block title %}{{ item.name }} - Papelería{% endblock %}

{% block content %}
<h1>{{ item.name }}</h1>
<p>{{ item.description }}</p>
<p>Precio: ${{ item.price }}</p>
<p>Stock: {{ item.stock }}</p>

<!-- Mostrar imagen generada dinámicamente -->
<img src="/api/item/{{ item.id }}/image" alt="{{ item.name }}">

{% if item.rentable %}
    <form method="POST" action="/student/rent">
        <input type="hidden" name="item_id" value="{{ item.id }}">
        <input type="text" name="qty" placeholder="Cantidad">
        <input type="date" name="start_date">
        <input type="number" name="days" value="7">
        <button>Rentar</button>
    </form>
{% endif %}
{% endblock %}
```

---

## ESTÁTICOS (STATIC/) - CSS, JS, IMÁGENES

```
static/
├── style.css                    ← 1200+ líneas CSS (diseño)
├── script.js                    ← JavaScript del cliente
├── img/                         ← Imágenes de interfaz
│   ├── logo.png
│   └── icons/
│
└── uploads/                     ← Archivos subidos
    ├── item_1.png              ← Imagen auto-generada de producto
    ├── item_2.png
    └── qr/
        ├── item_1_qr.png       ← Código QR
        └── item_2_qr.png
```

---

## UTILIDADES (UTILS/)

### security.py
```python
hash_password('mi_pass')        → Encriptar contraseña
verify_password('mi_pass', hash)→ Verificar contraseña
get_client_ip()                 → Obtener IP del usuario
login_required (decorador)      → Proteger rutas
```

### analytics.py
```python
get_analytics_data()            → Estadísticas generales
forecast_revenue()              → Predicción de ingresos
get_predictive_analytics()      → IA para análisis
get_supplier_intelligence()     → Análisis de proveedores
```

---

## DATOS INICIALES (SEED_PRODUCTS.PY)

```python
PRODUCTS = {
    'Papeles': [
        {'name': 'Papel A4 (resma)', 'price': 5.00, 'stock': 100, 'rentable': False},
        {'name': 'Papel bond', 'price': 3.50, 'stock': 80, 'rentable': False},
        # ... 20 productos más
    ],
    'Escritura': [
        {'name': 'Lapicero azul', 'price': 1.50, 'stock': 500, 'rentable': False},
        {'name': 'Lápiz grafito', 'price': 0.80, 'stock': 300, 'rentable': False},
        # ... 15 productos más
    ],
    # ... 10 categorías más, total 200+ productos
}
```

Al ejecutar `python app.py`:
1. initialization.py lee PRODUCTS
2. Itera cada producto
3. Crea registro en tabla `item`
4. Genera imagen PNG automáticamente

---

## FLUJO COMPLETO DE UNA COMPRA

```
1. USUARIO ACCEDE
   Usuario: http://localhost:5000/item/42

2. FLASK RECEPCIONA
   app.py → create_app() → routing

3. MIDDLEWARE EJECUTA before_request()
   Carga g.user desde sesión (si existe)

4. BUSCA LA RUTA
   /item/<int:item_id> está en public_routes.py
   → item_detail(item_id)

5. OBTIENE DATOS
   item = Item.query.get_or_404(42)
   SQL: SELECT * FROM item WHERE id = 42;

6. GENERA IMAGEN
   image_url = get_category_color(item.category)
   genera PNG en memoria

7. RENDERIZA TEMPLATE
   render_template('item.html', item=item)
   Reemplaza {{ item.name }} → "Cuaderno cosido"

8. MIDDLEWARE EJECUTA after_request()
   Agrega headers de seguridad

9. RETORNA AL NAVEGADOR
   Status 200 OK
   Body: <html>...</html>

10. USUARIO VE LA PÁGINA
    Con imagen, descripción, botón "Rentar"

11. USUARIO HACE CLIC EN "RENTAR"
    POST /student/rent (del formulario)

12. FLASK PROCESA RENTA
    - student.py → request_extension()
    - Crea Transaction en BD
    - Reduce Item.stock
    - Guarda fechas de renta

13. BD ACTUALIZA
    INSERT INTO transaction
        (user_id, item_id, kind, rent_start_date, rent_due_date)
    VALUES (5, 42, 'rent', '2025-12-10', '2025-12-17');
    
    UPDATE item SET stock = stock - 1 WHERE id = 42;

14. REDIRIGE AL DASHBOARD
    Mensaje: "Renta registrada hasta 2025-12-17"
```

---

## VENTAJAS DE LA ARQUITECTURA

| Aspecto | Ventaja |
|--------|---------|
| **Modularidad** | Código en modules/blueprints reutilizables |
| **Testabilidad** | Cada componente se puede probar independientemente |
| **Mantenibilidad** | Cambios en una carpeta no afectan otras |
| **Escalabilidad** | Fácil agregar nuevas rutas y módulos |
| **Seguridad** | Patrones de seguridad aplicados consistentemente |
| **Performance** | ORM con pooling de conexiones optimizado |

---

## COMANDOS ÚTILES PARA EXPLICAR

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor (desarrollo)
python app.py

# Acceder
http://localhost:5000

# Credenciales de prueba
Usuario: admin
Contraseña: admin123

# Ver logs
# En development, Flask muestra logs en consola

# Ver estructura BD
# En SQLite: db browser
# En PostgreSQL: pgAdmin o psql
```

---

**Este documento explica COMPLETAMENTE qué hace cada parte del proyecto.**
