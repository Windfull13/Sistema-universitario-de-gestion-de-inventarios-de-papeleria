# 📚 Papelería Universitaria - Sistema de Gestión Integral

**Sistema profesional de gestión de inventario, rentas y análisis con IA integrada**

Aplicación web Flask completa con panel administrativo avanzado, autenticación segura, análisis predictivo y sistema de inteligencia de proveedores.

---

## ✨ Características Principales

### 🛍️ Catálogo de Productos
- **200+ productos** de papelería universitaria
- Organización por categorías
- Búsqueda y filtros
- Información detallada (precio, descripción, stock)
- Badges de estado (En stock, Bajo stock, Rentable)

### 💰 Sistema de Rentales
- Rentales con selección de fechas
- Extensión de rentales aprobada por admin
- Seguimiento de rentales activas
- Historial de transacciones
- Notificaciones automáticas

### 👥 Autenticación Segura
- Login de administrador (usuario/contraseña)
- Login de estudiante (email/contraseña)
- Autenticación de dos factores (2FA)
- Rate limiting (protección contra fuerza bruta)
- Registro de intentos fallidos
- Sesiones activas

### 📊 Panel Administrativo
- Dashboard con métricas
- Gestión de inventario (agregar/editar/eliminar)
- Análisis de rentales
- Gestión de extensiones
- Registro de seguridad (auditoría)
- Gestión de API keys

### 🎨 Interfaz Moderna
- Diseño responsivo (móvil, tablet, desktop)
- Tema profesional azul + ámbar
- Componentes visuales pulidos
- Animaciones suaves
- Iconos Bootstrap Icons integrados
- Completamente en Español

---

## 🚀 Características Técnicas

### Backend (Python/Flask)
- Arquitectura modular con blueprints
- SQLAlchemy ORM para persistencia
- Middleware de seguridad
- Análisis predictivo con ML
- Sistema de logging estructurado
- Gestión de sesiones seguras

### Frontend (HTML/CSS/Bootstrap)
- Bootstrap 5.3 para UI responsiva
- CSS personalizado con gradientes
- Animaciones suaves
- Formularios validados
- Mensajes de notificación

### Base de Datos
- SQLite para desarrollo
- PostgreSQL para producción
- Migraciones automáticas
- Índices optimizados

---

## 📋 Requisitos

```
Python 3.8+
Flask 2.2+
SQLAlchemy 3.0+
PostgreSQL (producción)
```

Ver `requirements.txt` para la lista completa.

---

## ⚙️ Instalación

### 1. Clonar Repositorio
```bash
git clone https://github.com/Windfull13/Sistema-universitario-de-gestion-de-inventarios-de-papeleria.git
cd Sistema-universitario-de-gestion-de-inventarios-de-papeleria
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### 5. Inicializar Base de Datos
```bash
python app.py
```

---

## 🔑 Usuarios Por Defecto

### Admin
- **Usuario:** admin
- **Contraseña:** admin123
- **URL:** http://localhost:5000/admin

### Estudiante
- **Email:** student@example.com
- **Contraseña:** student123
- **URL:** http://localhost:5000/student

---

## 🎯 Funcionalidades Principales

### Para Estudiantes
- ✅ Ver catálogo de productos
- ✅ Comprar productos
- ✅ Rentar productos (si disponibles)
- ✅ Solicitar extensiones de renta
- ✅ Ver historial de transacciones
- ✅ Estadísticas personales
- ✅ Gestión de cuenta

### Para Administradores
- ✅ Dashboard con análisis
- ✅ Gestión completa de inventario
- ✅ Aprobar/Rechazar extensiones
- ✅ Análisis de demanda estacional
- ✅ Inteligencia de proveedores
- ✅ Predictiva de faltantes
- ✅ Registro de seguridad (auditoría)
- ✅ Gestión de API keys

---

## 🔐 Seguridad

- ✅ Autenticación robusta
- ✅ Cifrado de contraseñas (Argon2)
- ✅ Protección CSRF
- ✅ Rate limiting
- ✅ Validación de entrada
- ✅ Registro de auditoría completo
- ✅ Autenticación de dos factores (2FA)
- ✅ Gestión de sesiones activas

---

## 📊 Base de Datos

### Modelos Principales
- **User** - Usuarios (Admin, Estudiantes)
- **Item** - Productos del catálogo
- **Transaction** - Compras, rentas y devoluciones
- **ActiveSession** - Sesiones activas para seguridad
- **LoginAttempt** - Registro de intentos de login
- **ApiKey** - Claves para API externa

---

## 🚀 Despliegue

### Render.com
1. Conectar repositorio GitHub
2. Configurar variables de entorno
3. Establecer comando de inicio: `gunicorn -c gunicorn_config.py app:app`
4. Deploy automático en cada push

### Heroku (Alternativa)
1. Instalar Heroku CLI
2. Ejecutar: `heroku create`
3. Agregar base de datos PostgreSQL
4. Hacer push: `git push heroku master`

---

## 📝 Estructura del Proyecto

```
project/
├── app.py                 # Aplicación principal
├── config.py              # Configuración
├── models.py              # Modelos ORM
├── requirements.txt       # Dependencias
├── Procfile               # Configuración Heroku/Render
├── runtime.txt            # Versión Python
├── gunicorn_config.py     # Config web server
├── core/
│   ├── initialization.py  # Setup inicial
│   ├── middleware.py      # Middleware de seguridad
│   ├── public_routes.py   # Rutas públicas
│   └── styles.py          # Estilos dinámicos
├── routes/
│   ├── admin.py           # Rutas de admin
│   ├── auth.py            # Autenticación
│   ├── student.py         # Rutas de estudiante
│   ├── api.py             # API REST
│   └── nfc.py             # NFC/QR
├── templates/             # Templates HTML
├── static/                # CSS, JS, imágenes
└── utils/
    ├── analytics.py       # Análisis y ML
    └── security.py        # Utilidades de seguridad
```

---

## 🐛 Troubleshooting

### Error 500 en extensiones
- ✅ Arreglado: Se corrigió la comparación de tipos Date/DateTime

### Error 404 en compra
- ✅ Arreglado: Se agregaron rutas `/api/buy` y `/api/rent`

### Base de datos vacía
- Ejecutar: `python app.py` para seed automático

---

## 📞 Soporte

Para reportar bugs o sugerir mejoras, abre un issue en GitHub.

---

## 📄 Licencia

Proyecto educativo de Sistema de Gestión de Inventarios para Papelería Universitaria.

---

**Último actualizado:** Diciembre 2025
