# 📋 EXPLICACIÓN DE VARIABLES DE ENTORNO EN RENDER

## ¿Qué son las variables de entorno?

Son **valores de configuración** que tu aplicación necesita para funcionar, pero **no deben estar en el código** (por seguridad). Se guardan en Render y se pasan automáticamente a la app cuando se ejecuta.

---

## 🔐 LAS 7 VARIABLES EN TU PROYECTO

### 1️⃣ **DATABASE_URL**
```
Valor: postgresql://user:password@host/database_name
```

**¿Qué es?**
- Es la **dirección de conexión** a la base de datos PostgreSQL en Render
- Contiene: usuario, contraseña, host y nombre de la BD

**¿Por qué es secreto?**
- Si alguien ve esta URL, puede acceder a tu base de datos
- Contiene la contraseña del usuario de BD

**¿Cómo la usa tu app?**
```python
# En config.py:
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
# Render la proporciona automáticamente

# Flask usa esto para conectar a PostgreSQL:
# - Crea la tabla de usuarios
# - Crea la tabla de productos
# - Guarda/lee datos
```

**Ejemplo real:**
```
postgresql://papidb_user:abc123xyz@dpg-ch2h3kd91234.postgres.render.com/papidb
           ^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^
           usuario:contraseña         servidor de BD                    nombre BD
```

---

### 2️⃣ **FLASK_ENV**
```
Valor: production
```

**¿Qué es?**
- Le dice a Flask **cómo comportarse**: en modo desarrollo o producción

**Valores posibles:**
```
development  → Debug ON, errores detallados, recarga automática
production   → Debug OFF, errores ocultos, sin recarga automática
```

**¿Por qué es importante?**
- En **producción** (Render), necesitas:
  - `DEBUG = False` → Los usuarios no ven errores internos
  - `SESSION_COOKIE_SECURE = True` → Solo HTTPS
  - Optimizaciones de seguridad

**¿Cómo lo usa tu app?**
```python
# En config.py:
if os.getenv('FLASK_ENV') == 'production':
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
else:
    DEBUG = True
    SESSION_COOKIE_SECURE = False
```

---

### 3️⃣ **SECRET_KEY**
```
Valor: (un string largo aleatorio, ej: "abc123xyz789...")
```

**¿Qué es?**
- Es la **clave maestra** para encriptar datos sensibles en tu app

**¿Qué encripta?**
- **Sesiones de usuario** → `session['user_id']` está encriptada
- **CSRF tokens** → Para proteger formularios
- **Cookies** → No se pueden modificar sin esta clave

**¿Por qué es secreto?**
- Si alguien la conoce, puede:
  - Falsificar sesiones
  - Hacerse pasar por otro usuario
  - Acceder a cuentas ajenas

**¿Cómo lo usa tu app?**
```python
# En config.py:
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Cuando haces login:
session['user_id'] = user.id  # ← Se encripta con SECRET_KEY

# Cuando el navegador te envía la cookie:
# Flask la desencripta con SECRET_KEY
# Si alguien la modificó, la rechaza
```

**Ejemplo:**
```
Sin SECRET_KEY: Cookie = "user_id=42" (cualquiera puede editarla)
Con SECRET_KEY:  Cookie = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." (encriptada)
```

---

### 4️⃣ **JWT_SECRET_KEY**
```
Valor: (otro string largo aleatorio)
```

**¿Qué es?**
- Similar a `SECRET_KEY`, pero específicamente para **tokens JWT**
- JWT = JSON Web Token (usado en APIs modernas)

**¿Por qué es diferente a SECRET_KEY?**
- `SECRET_KEY` → Para sesiones tradicionales (servidor guarda sesión)
- `JWT_SECRET_KEY` → Para APIs (token contiene datos, sin sesión en servidor)

**¿Cómo lo usa tu app?**
```python
# En routes/api.py (si usas autenticación con JWT):
from flask_jwt_extended import create_access_token

# Cuando un cliente se autentica en la API:
token = create_access_token(identity=user.id)
# Usa JWT_SECRET_KEY para firmar el token

# El cliente envía el token en cada request:
# Authorization: Bearer eyJhbGciOiJIUzI1NiI...
# Flask verifica el token con JWT_SECRET_KEY
```

**Caso práctico:**
```javascript
// Cliente (frontend/app móvil)
fetch('/api/items', {
    headers: {
        'Authorization': 'Bearer eyJhbGc...'  // JWT Token
    }
})

// Servidor (Flask)
// Verifica: ¿Este token es válido? ¿Lo firmamos nosotros?
// Usa JWT_SECRET_KEY para verificar
```

---

### 5️⃣ **MAIL_DEFAULT_SENDER**
```
Valor: noreply@tupapeleria.com (o similar)
```

**¿Qué es?**
- El **email desde el cual tu app envía correos**
- Es el "remitente" de notificaciones automáticas

**¿Qué correos envía tu app?**
- Email de confirmación (cuando se registra un usuario)
- Notificación de stock bajo
- Recordatorio de renta vencida
- Confirmación de compra

**¿Cómo lo usa tu app?**
```python
# En utils/mail.py o routes/auth.py:
from flask_mail import Mail, Message

# Cuando un usuario se registra:
msg = Message(
    subject='Bienvenido a Papelería',
    sender=os.environ.get('MAIL_DEFAULT_SENDER'),  # ← Esta variable
    recipients=[user.email]
)
mail.send(msg)

# El usuario recibe un email de: noreply@tupapeleria.com
```

---

### 6️⃣ **MAIL_USERNAME**
```
Valor: tu_email@gmail.com (o el email del servidor SMTP)
```

**¿Qué es?**
- El **usuario/email para autenticarse** en el servidor SMTP (correo)
- Es diferente de `MAIL_DEFAULT_SENDER`

**¿Por qué dos variables diferentes?**
```
MAIL_DEFAULT_SENDER = noreply@papeleria.com
                      (lo que VE el usuario)

MAIL_USERNAME = cuenta@gmail.com
                (credencial para conectar a Gmail/servidor)
```

**Ejemplo real:**
```
Tu app usa Gmail para enviar correos:
- Te conectas a SMTP de Gmail como: cuenta@gmail.com (MAIL_USERNAME)
- Pero el email que recibe el usuario es de: noreply@papeleria.com (MAIL_DEFAULT_SENDER)
```

**¿Cómo lo usa tu app?**
```python
# En config.py:
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # ← Gmail login
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # ← Gmail password

# Flask se conecta a Gmail usando estas credenciales
```

---

### 7️⃣ **MAIL_PASSWORD**
```
Valor: (contraseña de Gmail o servidor SMTP)
```

**¿Qué es?**
- La **contraseña** para conectar a la cuenta de correo (SMTP)
- Generalmente es una "contraseña de aplicación" en Gmail, no la contraseña real

**¿Por qué no es la contraseña real?**
- Por seguridad, Gmail y otros servicios permiten crear "contraseñas de aplicación"
- Son contraseñas especiales solo para apps, se pueden revocar sin cambiar contraseña real

**¿Por qué es secreto?**
- Si alguien la obtiene, puede enviar correos usando tu cuenta
- Podría enviar spam o phishing

**¿Cómo se genera en Gmail?**
```
1. Ir a: myaccount.google.com/apppasswords
2. Seleccionar: Correo → Windows / Mac / Linux (según tu sistema)
3. Gmail genera una contraseña de 16 caracteres
4. Guardarla en Render como MAIL_PASSWORD
```

---

## 🔄 FLUJO COMPLETO: UN USUARIO SE REGISTRA

```
┌─ USUARIO ─────────────────────┐
│ Entra a:                       │
│ https://mi-app.onrender.com   │
│ Llena formulario de registro  │
│ Email: juan@gmail.com         │
│ Contraseña: mi123             │
└─────────────────────────────────┘
              ↓
┌─ RENDER RECIBE REQUEST ────────┐
│ POST /register                 │
│ Render carga variables:        │
│ - DATABASE_URL                 │
│ - SECRET_KEY                   │
│ - MAIL_USERNAME                │
│ - MAIL_PASSWORD                │
│ - MAIL_DEFAULT_SENDER          │
└────────────────────────────────┘
              ↓
┌─ FLASK PROCESA ────────────────┐
│ 1. Crea hash de contraseña:    │
│    hash = PBKDF2(mi123)        │
│ 2. Guarda en BD:               │
│    INSERT INTO user...         │
│    usa DATABASE_URL            │
│ 3. Crea sesión encriptada:     │
│    session['user_id'] = 42     │
│    encripta con SECRET_KEY     │
└────────────────────────────────┘
              ↓
┌─ ENVÍA CORREO ─────────────────┐
│ 1. Conecta a Gmail SMTP        │
│    usuario: MAIL_USERNAME      │
│    contraseña: MAIL_PASSWORD   │
│ 2. Envía email:                │
│    From: MAIL_DEFAULT_SENDER   │
│    To: juan@gmail.com          │
│    Mensaje: "Bienvenido!"      │
└────────────────────────────────┘
              ↓
┌─ USUARIO RECIBE ───────────────┐
│ Email de: noreply@papeleria.com │
│ Mensaje: "Tu cuenta creada"     │
└────────────────────────────────┘
```

---

## 🛡️ SEGURIDAD: ¿DÓNDE SE GUARDAN?

**NO debes guardarlas en:**
```
❌ En el código (app.py, config.py, .py files)
❌ En git/GitHub
❌ En archivos .env que subes a GitHub
❌ En comentarios o documentación pública
```

**DEBES guardarlas en:**
```
✅ En Render → Environment variables (lo que ves en la captura)
✅ En variables de entorno del sistema
✅ En un archivo .env LOCAL (no versionado)
```

**Ejemplo de .env local (desarrollo):**
```bash
# .env (gitignore, nunca subir a GitHub)
DATABASE_URL=sqlite:///inventory.db
FLASK_ENV=development
SECRET_KEY=mi_clave_super_secreta_local_123
JWT_SECRET_KEY=otra_clave_local_456
MAIL_USERNAME=mi_email@gmail.com
MAIL_PASSWORD=abcd efgh ijkl mnop
MAIL_DEFAULT_SENDER=noreply@local.test
```

---

## 📊 TABLA RESUMEN

| Variable | Qué es | Quién la usa | Secreto |
|----------|--------|-------------|---------|
| DATABASE_URL | Conexión a PostgreSQL | SQLAlchemy | ⭐⭐⭐ CRÍTICO |
| FLASK_ENV | Modo dev/prod | Flask config | ⭐ No es secreto |
| SECRET_KEY | Clave para encriptar sesiones | Flask session | ⭐⭐⭐ CRÍTICO |
| JWT_SECRET_KEY | Clave para tokens API | Flask-JWT | ⭐⭐⭐ CRÍTICO |
| MAIL_DEFAULT_SENDER | Email del remitente | Flask-Mail | ⭐ No es secreto |
| MAIL_USERNAME | Usuario SMTP | Flask-Mail | ⭐⭐⭐ CRÍTICO |
| MAIL_PASSWORD | Contraseña SMTP | Flask-Mail | ⭐⭐⭐ CRÍTICO |

---

## ⚙️ CÓMO USARLAS EN TU CÓDIGO

### En desarrollo (local):
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Lee variables de .env

class Config:
    # BD
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
        or 'sqlite:///inventory.db'
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') \
        or 'dev-key-change-in-production'
    
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
```

### En producción (Render):
```
Render proporciona automáticamente:
- DATABASE_URL (BD que creó para ti)
- Las demás variables que configuraste en el panel
↓
Flask lee os.environ.get() y obtiene esos valores
↓
Tu app funciona con la configuración de producción
```

---

## 🚀 CÓMO AGREGAR MÁS VARIABLES (si necesitas)

En Render:
1. Ve a tu proyecto
2. Settings → Environment
3. Haz click en "Add Variable"
4. Nombre: `MI_NUEVA_VARIABLE`
5. Valor: `mi_valor_secreto`
6. Save

En tu código:
```python
mi_valor = os.environ.get('MI_NUEVA_VARIABLE')
```

---

## ✅ CHECKLIST: Variables correctamente configuradas

- ✅ DATABASE_URL → Conecta a PostgreSQL
- ✅ FLASK_ENV → production
- ✅ SECRET_KEY → String largo aleatorio
- ✅ JWT_SECRET_KEY → String largo aleatorio (diferente a SECRET_KEY)
- ✅ MAIL_USERNAME → Email de Gmail
- ✅ MAIL_PASSWORD → Contraseña de aplicación de Gmail
- ✅ MAIL_DEFAULT_SENDER → Email desde el que envía

**Si alguna falta:** Tu app no funcionará correctamente en Render.

---

## 🎓 CONCEPTO CLAVE

> **Variables de entorno = Configuración que cambia según dónde corre la app**
>
> - **Desarrollo (local):** SQLite, DEBUG=True, keys locales
> - **Producción (Render):** PostgreSQL, DEBUG=False, keys reales y secretas

No son hardcodeadas = la app es **flexible y reutilizable**.
