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

**Para una guía detallada, ver [GETTING_STARTED.md](GETTING_STARTED.md)**

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar aplicación
python app.py
```

Accede a: `http://localhost:5000`

### Credenciales de Prueba
- **Admin**: usuario `admin` / contraseña `admin123`
- **Estudiante**: email `student@example.com` / contraseña `student123`

---

## 📁 Estructura del Proyecto

```
Proyecto_programación_web/
├── app.py               # Aplicación Flask principal
├── config.py           # Configuración
├── models.py           # Modelos SQLAlchemy
├── inventory.db        # Base de datos SQLite
│
├── routes/             # Rutas Flask
│   ├── auth.py        # Autenticación
│   ├── admin.py       # Panel admin
│   ├── student.py     # Panel estudiante
│   ├── api.py         # API REST
│   └── nfc.py         # Control NFC/QR
│
├── templates/          # 26 templates HTML
├── static/             # CSS + uploads
└── utils/              # Utilidades
```

---

## 📚 Documentación

- **[README.md](README.md)** - Este archivo (descripción general)
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Guía de inicio rápido
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Sistema de diseño y componentes

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
| **Rentales activos** | Variable |

---

## 🆘 Solución Rápida de Problemas

**Puerto ocupado:**
```bash
# Cambiar puerto en app.py
app.run(port=5001)
```

**Base de datos corrupta:**
```bash
rm inventory.db
python app.py  # Se recrea automáticamente
```

**Más ayuda:** Ver [GETTING_STARTED.md](GETTING_STARTED.md#-solucionar-problemas)

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

Ver `requirements.txt` para lista completa.

---

## 📝 Notas

- Aplicación lista para producción
- Interfaz 100% responsiva
- 1,200+ líneas de CSS personalizado
- 26 templates HTML profesionales
- Completa en Español

---

**Última actualización**: 24 de noviembre de 2025  
**Versión**: 2.0  
**Estado**: ✅ Producción (100% Funcional)  
**Pruebas**: ✅ 5/5 Pasadas  

Desarrollado con ❤️ para Papelería Universitaria
