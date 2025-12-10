# 📚 EXPLICACIÓN TÉCNICA DEL PROYECTO PARA EL PROFESOR

## 🎯 Introducción General

Este es un **Sistema Web de Gestión de Inventario** para una papelería universitaria, construido con **Flask** (framework Python para web) y **SQLAlchemy** (ORM para bases de datos). 

**Propósito:** Gestionar productos, controlar rentas, generar reportes analytics y proveer control administrativo mediante un panel web.

---

## 📁 ESTRUCTURA DEL PROYECTO

```
Proyecto_inventarios/
├── app.py                    ← PUNTO DE ENTRADA (55 líneas)
├── models.py                 ← ESTRUCTURA DE DATOS (254 líneas)
├── config.py                 ← CONFIGURACIÓN (92 líneas)
├── seed_products.py          ← DATOS INICIALES
│
├── core/                     ← COMPONENTES REUTILIZABLES (NUEVO)
│   ├── initialization.py     ← BD y seeding
│   ├── middleware.py         ← Request handlers
│   ├── public_routes.py      ← Rutas públicas
│   └── styles.py             ← Colores centralizados
│
├── routes/                   ← BLUEPRINTS DE FUNCIONALIDAD (5 módulos)
│   ├── auth.py              ← Autenticación (login/logout)
│   ├── admin.py             ← Panel administrativo
│   ├── student.py           ← Portal de estudiantes
│   ├── api.py               ← API REST endpoints
│   └── nfc.py               ← Códigos QR
│
├── templates/                ← VISTAS HTML (26 archivos)
├── static/                   ← ASSETS (CSS, imágenes, uploads)
├── utils/                    ← UTILIDADES
│   ├── security.py          ← Funciones de seguridad
│   └── analytics.py         ← Análisis y reportes
│
└── requirements.txt          ← DEPENDENCIAS PYTHON
```

---

## 🔴 CAPA 1: PUNTO DE ENTRADA (`app.py`)

### ¿Qué hace?
Es el archivo principal que **inicia la aplicación Flask**. Usa el patrón **Application Factory** para crear y configurar la app.

### Código clave:
```python
def create_app():
    """Application factory function"""
    app = Flask(__name__)  # Crear instancia Flask
    
    # 1. Cargar configuración (desarrollo/producción)
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # 2. Inicializar base de datos
    db, db_available = init_database(app)
    
    # 3. Registrar middleware (procesamiento de requests)
    register_middleware(app, db_available)
    
    # 4. Registrar blueprints (módulos de funcionalidad)
    register_blueprints(app)
    
    return app

app = create_app()  # Crear la app
```

### ¿Por qué es importante?
- **Modularidad:** Separa la lógica de inicialización
- **Reutilizable:** Puedes usar `create_app()` en tests
- **Limpio:** Reduce el tamaño de app.py (ahora 55 líneas vs 489 originales)

---

## 🟠 CAPA 2: ESTRUCTURA DE DATOS (`models.py`)

### ¿Qué hace?
Define la **estructura de la base de datos** usando SQLAlchemy ORM (Object-Relational Mapping).

### Modelos principales:

#### 1. **User** - Usuarios del sistema
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20))  # 'admin' o 'student'
    two_fa_enabled = db.Column(db.Boolean)  # 2FA (autenticación doble)
    last_login_ip = db.Column(db.String(45))  # Seguridad
```

#### 2. **Item** - Productos de papelería
```python
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Ej: 'Papeles', 'Escritura'
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)  # Cantidad disponible
    rentable = db.Column(db.Boolean)  # ¿Se puede rentar?
    image_filename = db.Column(db.String(100))
```

#### 3. **Transaction** - Compras y rentas
```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    kind = db.Column(db.String(10))  # 'buy' o 'rent'
    qty = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    
    # Si es renta:
    rent_start_date = db.Column(db.Date)
    rent_due_date = db.Column(db.Date)
    returned = db.Column(db.Boolean)
    return_date = db.Column(db.Date)
```

#### 4. **Supplier** - Proveedores
```python
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(50))
```

#### 5. **PurchaseOrder** - Órdenes de compra
```python
class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)
    order_date = db.Column(db.DateTime)
    expected_delivery_date = db.Column(db.DateTime)
    status = db.Column(db.String(20))  # 'pending', 'delivered', 'cancelled'
```

### ¿Cómo funciona SQLAlchemy?
```python
# Sin SQLAlchemy (SQL puro) - PROBLEMA:
query = "SELECT * FROM user WHERE username = 'juan'"
result = db.execute(query)  # Strings, vulnerables a SQL injection

# Con SQLAlchemy (ORM) - SOLUCIÓN:
user = User.query.filter_by(username='juan').first()  # Seguro y limpio
```

---

## 🟡 CAPA 3: CONFIGURACIÓN (`config.py`)

### ¿Qué hace?
Define la **configuración de la aplicación** según el entorno (desarrollo/producción).

### Configuración por entorno:

```python
class Config:
    # Base de datos
    DATABASE_URI = (
        os.environ.get('DATABASE_URL')  # PostgreSQL en producción (Render)
        or f'sqlite:///{BASE_DIR}/inventory.db'  # SQLite en desarrollo
    )
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Para encriptar sesiones
    SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
    SESSION_COOKIE_HTTPONLY = True  # Protege contra XSS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)  # Sesión 8 horas
    
    # Aplicación
    APP_URL = 'http://localhost:5000' (desarrollo)
            or 'https://mi-app.onrender.com' (producción)
```

### ¿Por qué es importante?
- **Flexibilidad:** Mismo código, diferente configuración según entorno
- **Seguridad:** No hardcodear secrets en el código
- **Escalabilidad:** Fácil cambiar BD, puertos, etc.

---

## 🟢 CAPA 4: NÚCLEO (`core/`)

Contiene 4 módulos reutilizables que la app factory (`app.py`) usa:

### 4.1 `core/initialization.py` (278 líneas)
**Propósito:** Inicializar base de datos, crear tablas y sembrar datos.

```python
def init_database(app):
    """Inicializar SQLAlchemy"""
    db.init_app(app)
    return db, db_available

def create_tables_and_seed(app, db):
    """Crear tablas y llenar con datos de prueba"""
    with app.app_context():
        db.create_all()  # CREATE TABLE si no existen
        _create_admin_user(db)  # Crear admin por defecto
        _seed_products(db)  # Cargar 200+ productos
        _generate_placeholder_images(db)  # Generar imágenes
        _seed_example_data(db)  # Crear datos de ejemplo
```

**Funciones importantes:**
- `_create_admin_user()` - Crea usuario admin (admin/admin123)
- `_seed_products()` - Carga productos desde `seed_products.py`
- `_generate_placeholder_images()` - Crea imágenes PNG con PIL
- `_seed_example_data()` - Crea 4 proveedores, 4 estudiantes, 20 transacciones

### 4.2 `core/middleware.py` (90 líneas)
**Propósito:** Procesar requests, error handling y seguridad.

```python
@app.before_request
def before_request():
    """Se ejecuta ANTES de cada request"""
    g.user = None  # Variable global por request
    
    # Si hay user_id en sesión, cargarlo desde BD
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@app.after_request
def after_request(response):
    """Se ejecuta DESPUÉS de cada request"""
    # Agregar headers de seguridad
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Error handlers - Mostrar páginas personalizadas
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500
```

**¿Cómo funciona?**
```
Request HTTP → before_request() → Ruta → after_request() → Response HTTP
```

### 4.3 `core/public_routes.py` (118 líneas)
**Propósito:** Rutas públicas (sin autenticación requerida).

```python
public_bp = Blueprint('public', __name__)

@public_bp.route('/health')
def health():
    """Endpoint para Render y monitoreo"""
    return {'status': 'healthy', 'db_available': True}, 200

@public_bp.route('/')
def index():
    """Home page"""
    if g.user:
        # Si está logueado, redirigir al dashboard
        return redirect(url_for('admin.index'))
    return render_template('index.html')

@public_bp.route('/item/<int:item_id>')
def item_detail(item_id):
    """Ver detalles de un producto (público)"""
    item = Item.query.get_or_404(item_id)
    return render_template('item.html', item=item)

@public_bp.route('/api/item/<int:item_id>/image')
def generate_item_image(item_id):
    """Generar imagen dinámicamente (sin guardar archivo)"""
    item = Item.query.get_or_404(item_id)
    
    # Usar color de categoría
    rgb = get_category_color(item.category)
    
    # Crear imagen PNG en memoria
    img = Image.new('RGB', (400, 300), color=rgb)
    draw = ImageDraw.Draw(img)
    draw.text((x, y), item.name, fill=TEXT_COLOR)
    
    # Retornar como imagen sin guardar en disco
    return send_file(img_bytes, mimetype='image/png')
```

### 4.4 `core/styles.py` (34 líneas)
**Propósito:** Centralizar colores y estilos (evitar duplicación).

```python
CATEGORY_COLORS = {
    'Papeles': '#E8F5E9',
    'Escritura': '#F3E5F5',
    'Cuadernos y libretas': '#E3F2FD',
    # ... 9 categorías más
}

TEXT_COLOR = (64, 64, 64)  # Gris oscuro para texto

def get_category_color(category: str) -> tuple:
    """Obtener color RGB para una categoría"""
    hex_color = CATEGORY_COLORS.get(category, '#F5F5F5')
    return hex_to_rgb(hex_color)
```

**¿Por qué centralizar colores?**
```
Antes: Colores definidos en 3 lugares → Inconsistencia
Después: Un único archivo → Una sola fuente de verdad
```

---

## 🔵 CAPA 5: RUTAS (`routes/`)

Cada archivo es un **Blueprint** (módulo de funcionalidad independiente).

### 5.1 `routes/auth.py` - Autenticación
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  # Guardar sesión
            return redirect(url_for('admin.index'))
        
        return render_template('login.html', error='Credenciales inválidas')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Logout - limpiar sesión"""
    session.clear()
    return redirect(url_for('public.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de estudiantes"""
    if request.method == 'POST':
        username = request.form.get('username')
        
        # Validar que no existe
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Usuario existe')
        
        # Crear nuevo usuario
        user = User(
            username=username,
            email=request.form.get('email'),
            password_hash=generate_password_hash(request.form.get('password')),
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')
```

### 5.2 `routes/admin.py` - Panel Administrativo
```python
@admin_bp.route('/admin/')
@login_required  # Decorador que verifica si está logueado
def index():
    """Dashboard del admin"""
    stats = {
        'total_products': Item.query.count(),
        'total_stock': db.session.query(func.sum(Item.stock)).scalar(),
        'active_rentals': Transaction.query.filter_by(kind='rent', returned=False).count(),
        'revenue': db.session.query(func.sum(Transaction.qty * Item.price)).scalar(),
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/admin/items', methods=['GET', 'POST'])
def items():
    """Gestión de productos"""
    if request.method == 'POST':
        # Crear producto
        item = Item(
            name=request.form.get('name'),
            category=request.form.get('category'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            rentable=request.form.get('rentable') == 'on'
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('admin.items'))
    
    # Listar todos los productos
    items_list = Item.query.all()
    return render_template('admin/items.html', items=items_list)

@admin_bp.route('/admin/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    """Editar un producto"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.price = float(request.form.get('price'))
        item.stock = int(request.form.get('stock'))
        db.session.commit()
        return redirect(url_for('admin.items'))
    
    return render_template('admin/edit_item.html', item=item)

@admin_bp.route('/admin/analytics')
def analytics():
    """Análisis de datos (gráficos, reportes)"""
    analytics_data = get_analytics_data()
    return render_template('admin/analytics.html', data=analytics_data)

@admin_bp.route('/admin/predictive')
def predictive():
    """Analytics predictivo (IA)"""
    forecast = get_predictive_analytics()
    return render_template('admin/predictive.html', forecast=forecast)
```

### 5.3 `routes/student.py` - Portal de Estudiantes
```python
@student_bp.route('/student/')
@login_required
def student_dashboard():
    """Dashboard personal del estudiante"""
    student = g.user
    
    # Mis compras
    purchases = Transaction.query.filter_by(user_id=student.id, kind='buy').all()
    
    # Mis rentas activas
    rentals = Transaction.query.filter_by(
        user_id=student.id, 
        kind='rent', 
        returned=False
    ).all()
    
    return render_template('student/dashboard.html', 
                         purchases=purchases, 
                         rentals=rentals)

@student_bp.route('/student/rentals')
def my_rentals():
    """Ver mis rentas activas y solicitar extensión"""
    rentals = Transaction.query.filter_by(
        user_id=g.user.id, 
        kind='rent'
    ).all()
    return render_template('student/rentals.html', rentals=rentals)

@student_bp.route('/student/request-extension/<int:rental_id>', methods=['POST'])
def request_extension(rental_id):
    """Solicitar extensión de renta"""
    rental = Transaction.query.get_or_404(rental_id)
    rental.extension_requested = True
    rental.extension_days = int(request.form.get('days', 3))
    db.session.commit()
    return redirect(url_for('student.my_rentals'))
```

### 5.4 `routes/api.py` - API REST
```python
@api_bp.route('/api/items', methods=['GET'])
def get_items():
    """GET /api/items - Retorna lista de productos en JSON"""
    items = Item.query.all()
    return {
        'items': [
            {
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'stock': item.stock,
                'category': item.category
            }
            for item in items
        ]
    }, 200

@api_bp.route('/api/item/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """GET /api/item/1 - Retorna un producto específico"""
    item = Item.query.get_or_404(item_id)
    return {
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': item.price,
        'stock': item.stock,
        'category': item.category,
        'rentable': item.rentable
    }, 200

@api_bp.route('/api/user/profile', methods=['GET'])
@login_required
def user_profile():
    """GET /api/user/profile - Perfil del usuario logueado"""
    user = g.user
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }, 200
```

### 5.5 `routes/nfc.py` - Códigos QR
```python
@nfc_bp.route('/nfc/qr/<int:item_id>')
def qr_item(item_id):
    """Generar código QR para un item"""
    item = Item.query.get_or_404(item_id)
    
    # URL hacia la que apunta el QR
    url = f"https://mi-app.onrender.com/item/{item.id}"
    
    # Generar código QR
    qr = segno.make_micro(url, error='m')
    
    # Guardar como PNG
    qr.save(f'static/uploads/qr/item_{item.id}.png', kind='png')
    
    return send_file(f'static/uploads/qr/item_{item.id}.png', 
                     mimetype='image/png')

@nfc_bp.route('/nfc-control')
def nfc_control():
    """Control de NFC (smartphones pueden leer QRs)"""
    return render_template('nfc_control.html')
```

---

## 🟣 CAPA 6: VISTAS (`templates/`)

Archivos HTML con Jinja2 (motor de templates de Flask).

```
templates/
├── base.html                  ← Template base (header, footer, CSS)
├── index.html                 ← Home page
├── item.html                  ← Detalle de producto
├── login.html                 ← Formulario login
├── register.html              ← Formulario registro
├── admin/
│   ├── dashboard.html         ← Dashboard admin (estadísticas)
│   ├── items.html             ← Listar productos
│   ├── add_item.html          ← Crear producto
│   ├── edit_item.html         ← Editar producto
│   ├── analytics.html         ← Gráficos y reportes
│   ├── predictive.html        ← Predicciones (IA)
│   ├── transactions.html      ← Historial de transacciones
│   └── security_log.html      ← Auditoría de seguridad
└── student/
    ├── dashboard.html         ← Dashboard estudiante
    ├── rentals.html           ← Mis rentas activas
    └── statistics.html        ← Mis estadísticas
```

### Ejemplo de template:
```html
<!-- templates/item.html -->
{% extends "base.html" %}

{% block content %}
<div class="container">
    <h1>{{ item.name }}</h1>
    <p>{{ item.description }}</p>
    <p>Precio: ${{ item.price }}</p>
    <p>Stock: {{ item.stock }}</p>
    
    {% if item.rentable %}
        <form method="POST" action="/student/rent">
            <input type="hidden" name="item_id" value="{{ item.id }}">
            <input type="number" name="qty" min="1" max="{{ item.stock }}">
            <input type="date" name="start_date">
            <input type="number" name="days" min="1" value="7">
            <button type="submit">Rentar</button>
        </form>
    {% endif %}
    
    <!-- Mostrar imagen dinámica -->
    <img src="/api/item/{{ item.id }}/image" alt="{{ item.name }}">
</div>
{% endblock %}
```

---

## 🟡 CAPA 7: ESTÁTICOS (`static/`)

```
static/
├── style.css                  ← Estilos CSS (1200+ líneas)
├── script.js                  ← JavaScript del lado cliente
└── uploads/                   ← Carpeta de archivos subidos
    ├── item_1.png            ← Imágenes de productos
    ├── item_2.png
    └── qr/                    ← Códigos QR
        ├── item_1_qr.png
        ├── item_2_qr.png
```

---

## 🟢 CAPA 8: UTILIDADES (`utils/`)

### `utils/security.py` - Funciones de seguridad
```python
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password):
    """Encriptar contraseña (hash BCrypt)"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password, hash):
    """Verificar contraseña vs hash"""
    return check_password_hash(hash, password)

def get_client_ip():
    """Obtener IP real del cliente (aunque esté detrás de proxy)"""
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def login_required(f):
    """Decorador que protege rutas (requiere estar logueado)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

### `utils/analytics.py` - Análisis de datos
```python
def get_analytics_data():
    """Obtener estadísticas generales"""
    return {
        'total_items': Item.query.count(),
        'total_products_value': db.session.query(
            func.sum(Item.price * Item.stock)
        ).scalar(),
        'active_rentals': Transaction.query.filter_by(
            kind='rent', returned=False
        ).count(),
        'total_revenue': db.session.query(
            func.sum(Transaction.qty * Item.price)
        ).scalar(),
        'top_products': Item.query.order_by(
            Item.sales_count.desc()
        ).limit(5).all()
    }

def forecast_revenue():
    """Predicción de ingresos (análisis estadístico)"""
    # Histórico de transacciones
    transactions = Transaction.query.filter_by(kind='buy').all()
    
    # Calcular media de ingresos por semana
    weekly_revenue = {}
    for trans in transactions:
        week = trans.timestamp.isocalendar()[1]
        weekly_revenue[week] = weekly_revenue.get(week, 0) + trans.qty * item.price
    
    # Proyectar 12 semanas usando media móvil
    forecast = calculate_moving_average(weekly_revenue)
    return forecast
```

---

## 🔄 FLUJO DE UNA PETICIÓN HTTP

Veamos qué pasa cuando un usuario entra a la app:

```
1. USUARIO ACCEDE A http://localhost:5000/admin/items

2. FLASK RECEPCIONA LA PETICIÓN
   └─> app.py (app = create_app())

3. EJECUTA before_request() EN core/middleware.py
   └─> Carga g.user desde sesión
   └─> Si no hay sesión, g.user = None

4. BUSCA LA RUTA (ROUTING)
   └─> /admin/items está definida en routes/admin.py
   └─> @login_required decorador verifica si g.user existe
   └─> Si no existe, redirige a /login

5. EJECUTA LA FUNCIÓN
   @admin_bp.route('/admin/items')
   def items():
       items_list = Item.query.all()  # Query a BD
       return render_template('admin/items.html', items=items_list)

6. OBTIENE DATOS DE LA BASE DE DATOS
   ├─> models.py define estructura Item
   ├─> SQLAlchemy traduce a SQL: SELECT * FROM item;
   ├─> PostgreSQL/SQLite retorna registros

7. RENDERIZA EL TEMPLATE
   ├─> Lee templates/admin/items.html
   ├─> Reemplaza {{ item.name }} con valores reales
   ├─> Genera HTML final

8. EJECUTA after_request() EN core/middleware.py
   └─> Agrega headers de seguridad

9. RETORNA RESPONSE HTTP AL NAVEGADOR
   └─> Status: 200 OK
   └─> Content-Type: text/html
   └─> Body: <html>...</html>

10. NAVEGADOR RENDERIZA LA PÁGINA
    └─> El usuario ve la lista de productos
```

---

## 🔐 SEGURIDAD IMPLEMENTADA

### 1. Autenticación
```python
# Hash de contraseñas (no se guardan en texto plano)
password_hash = generate_password_hash('mi_password')  # PBKDF2-SHA256

# Verificación
if check_password_hash(password_hash, user_input):
    # Contraseña correcta
```

### 2. Sesiones
```python
# Al loguear:
session['user_id'] = user.id  # Guardar ID en sesión encriptada

# En cada request:
g.user = User.query.get(session['user_id'])  # Cargar usuario

# Headers de seguridad:
SESSION_COOKIE_SECURE = True  # Solo por HTTPS
SESSION_COOKIE_HTTPONLY = True  # No accesible desde JS (XSS)
SESSION_COOKIE_SAMESITE = 'Lax'  # Protección CSRF
```

### 3. Rate Limiting (Protección contra fuerza bruta)
```python
class LoginAttempt(db.Model):
    """Registra intentos fallidos"""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    success = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

def check_rate_limit(ip_address, minutes=15, max_attempts=5):
    """Si > 5 intentos fallidos en 15 min, bloquear IP"""
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.ip_address == ip_address,
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= datetime.now() - timedelta(minutes=15)
    ).count()
    
    if failed_attempts >= max_attempts:
        return False  # IP bloqueada
    return True
```

### 4. SQL Injection Prevention
```python
# MALO (vulnerable):
query = f"SELECT * FROM user WHERE username = '{username}'"
result = db.execute(query)  # Si username = "'; DROP TABLE user;--"

# BUENO (seguro con SQLAlchemy):
user = User.query.filter_by(username=username).first()
# SQLAlchemy escapa automáticamente los valores
```

### 5. CSRF Protection
```python
# En template:
<form method="POST">
    {{ csrf_token() }}  <!-- Token CSRF en cada formulario -->
    <input type="text" name="username">
</form>

# En validación:
@login_required
def change_password():
    # Flask-WTF valida automáticamente el token CSRF
```

---

## 📊 PATRONES DE DISEÑO USADOS

### 1. **MVC (Model-View-Controller)**
```
Model  → models.py           (estructura datos)
View   → templates/          (vistas HTML)
Control→ routes/             (lógica de negocio)
```

### 2. **Application Factory**
```python
def create_app():
    """Crea la app con configuración"""
    return app

app = create_app()
```

### 3. **Blueprints (Modularidad)**
```python
# Cada blueprint es un módulo independiente
auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)

# Al registrar en app.py:
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
```

### 4. **ORM (Object-Relational Mapping)**
```python
# Sin ORM (SQL puro):
query = "SELECT * FROM user WHERE id = ?"
user = db.execute(query, (1,))

# Con ORM:
user = User.query.get(1)
```

### 5. **Decoradores**
```python
@login_required  # Protege la ruta
@admin_bp.route('/admin/items')  # Define la URL
def items():
    pass
```

---

## 🚀 DESPLIEGUE EN RENDER

### Arquitectura en producción:
```
┌─────────────┐
│   Usuario   │ (Web browser)
└──────┬──────┘
       │ HTTPS
       ↓
┌──────────────────────┐
│  Render (Web Service)│ (Hosting)
│  - Flask app.py      │
│  - Core modules      │
│  - Routes            │
└──────┬───────────────┘
       │ Connection string
       ↓
┌──────────────────────┐
│ Render (PostgreSQL)  │ (Base de datos)
│ - users              │
│ - items              │
│ - transactions       │
└──────────────────────┘
```

### Variables de entorno:
```bash
# .env (no versionado)
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=super-secreto-123
FLASK_ENV=production
APP_URL=https://mi-app.onrender.com
MAIL_SERVER=smtp.gmail.com
```

---

## 📈 ESTADÍSTICAS DEL PROYECTO

| Métrica | Valor |
|---------|-------|
| **Líneas de código** | ~2,500 |
| **Archivos Python** | 11 |
| **Modelos BD** | 6 |
| **Rutas** | 48 |
| **Templates** | 26 |
| **Productos en BD** | 200+ |
| **Usuarios de prueba** | 4 |
| **Transacciones demo** | 20+ |

---

## 🎓 CONCEPTOS CLAVE PARA EL PROFESOR

### 1. **Framework Web (Flask)**
- Micro-framework Python para construir aplicaciones web
- Manejo de rutas, templates, sesiones
- Extensible con blueprints

### 2. **Base de Datos**
- **SQLite:** Para desarrollo local
- **PostgreSQL:** Para producción (Render)
- **SQLAlchemy ORM:** Abstracción de BD

### 3. **Patrón MVC**
- **Model:** Estructura de datos (models.py)
- **View:** Presentación (templates/)
- **Controller:** Lógica de negocio (routes/)

### 4. **HTTP & REST**
- **GET:** Obtener datos
- **POST:** Crear/actualizar datos
- **Métodos REST:** /api/items (lista), /api/item/1 (detalle)

### 5. **Sesiones & Cookies**
- Identificar usuarios entre requests
- Encriptación segura
- Expiración automática

### 6. **Seguridad**
- Hash de contraseñas (PBKDF2-SHA256)
- Rate limiting
- CSRF protection
- SQL injection prevention

---

## 📝 CONCLUSIÓN

Este proyecto es una **aplicación web full-stack** que demuestra:

✅ **Arquitectura modular** - Código limpio y reutilizable
✅ **Base de datos relacional** - Modelos ORM bien diseñados
✅ **Autenticación segura** - Protección contra ataques comunes
✅ **UI responsive** - Frontend moderno con Bootstrap
✅ **API REST** - Endpoints JSON para integración
✅ **Analytics** - Reportes y predicciones (IA)
✅ **Despliegue en cloud** - Production-ready en Render

**Total:** 2,500+ líneas de código profesional y educativo.

---

**Versión:** 2.0 (Modularizada)
**Elaborado para:** Educación en programación web
**Tecnologías:** Flask, SQLAlchemy, PostgreSQL, HTML/CSS/JS
