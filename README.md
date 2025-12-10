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

## 🚀 Inicio Rápido

Ver [QUICKSTART.md](QUICKSTART.md) para guía detallada.

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
python app.py
```

Accede a: `http://localhost:5000`

### Credenciales de Prueba
- **Admin**: usuario `admin` / contraseña `admin123`
- **Estudiante**: usuario `juan.perez` / contraseña `student123`

---

## 📁 Estructura del Proyecto (Modularizada v2.0)

```
Proyecto_inventarios/
├── app.py                 # Application factory (limpio y modular)
├── models.py              # Modelos SQLAlchemy
├── config.py              # Configuración por entorno
│
├── core/                  # Componentes reutilizables
│   ├── initialization.py  # DB setup, seeding automático
│   ├── middleware.py      # Request handlers, error handlers
│   ├── public_routes.py   # Rutas públicas (home, items, health)
│   └── styles.py          # Colores y estilos centralizados
│
├── routes/                # Blueprints de aplicación
│   ├── auth.py           # Autenticación
│   ├── admin.py          # Panel admin
│   ├── student.py        # Panel estudiante
│   ├── api.py            # API REST
│   └── nfc.py            # Control NFC/QR
│
├── templates/             # 26 templates HTML
├── static/                # CSS + uploads
├── utils/                 # Seguridad, analytics
├── seed_products.py       # Datos iniciales
└── requirements.txt       # Dependencias
```

### Cambios v2.0
✅ **Modularización**: Separación de concerns en `core/`
✅ **Eliminados**: 10+ scripts de configuración antigua
✅ **Centralizado**: Colores, estilos, configuración
✅ **Documentación**: Solo 3 archivos esenciales (README, QUICKSTART, DEPLOYMENT)
✅ **Seeding automático**: Integrado en initialization.py

---

## 📚 Documentación

- **[README.md](README.md)** - Este archivo (descripción general)
- **[QUICKSTART.md](QUICKSTART.md)** - Guía de inicio rápido
- **[DEPLOYMENT_RENDER.md](DEPLOYMENT_RENDER.md)** - Despliegue en Render

---

## 🔒 Características de Seguridad

✅ Tokens de sesión con validación de IP
✅ Timeout automático (8 horas inactividad)
✅ 2FA opcional (TOTP/Authenticator)
✅ Contraseñas hasheadas (PBKDF2)
✅ CSRF protection
✅ Rate limiting
✅ Registro de auditoría

---

## 📊 Estadísticas Actuales

| Métrica | Valor |
|---------|-------|
| **Productos** | 200+ |
| **Categorías** | 12 |
| **Precios** | $800 - $10,000 COP |
| **Templates** | 26 |
| **Líneas de código** | ~2,500 (optimizado) |

---

## 🔗 Rutas Principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página de inicio |
| `/login` | Login administrador |
| `/student/login` | Login estudiante |
| `/admin/` | Dashboard administrativo |
| `/student/dashboard` | Dashboard estudiante |

---

## 📦 Requisitos

- Python 3.8+
- pip (gestor de paquetes)
- Navegador moderno (Chrome, Firefox, Safari, Edge)

**Dependencias principales:**
- Flask 2.3+
- SQLAlchemy 2.0+
- Flask-Limiter
- pyotp (2FA)
- Pillow (generación de imágenes)

Ver `requirements.txt` para lista completa.

---

## 📝 Notas

- Aplicación lista para producción
- Interfaz 100% responsiva
- Arquitectura modular y mantenible
- Todos los datos de prueba se generan automáticamente
- Sistema resistente a fallos de base de datos

---

**Última actualización**: Diciembre 2025  
**Versión**: 2.0 (Modularizada)  
**Estado**: ✅ Producción (100% Funcional)  

Desarrollado con ❤️ para Papelería Universitaria
