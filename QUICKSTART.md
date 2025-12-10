# 🚀 GUÍA RÁPIDA - Sistema de Gestión de Inventario

## Inicialización Rápida

### Credenciales por defecto:
- **Admin**: usuario `admin` / contraseña `admin123`
- **Estudiante**: usuario `juan.perez` / contraseña `student123`

### Acceso:
```
URL: http://localhost:5000
Admin Dashboard: http://localhost:5000/admin
```

---

## 📁 Estructura del Proyecto

```
Proyecto_inventarios/
├── app.py                 # Aplicación Flask (modularizada)
├── models.py              # Modelos de base de datos
├── config.py              # Configuración de entornos
├── core/                  # Componentes reutilizables
│   ├── initialization.py  # Inicialización de DB y extensiones
│   ├── middleware.py      # Request handlers y error handlers
│   └── public_routes.py   # Rutas públicas (home, items, health)
├── routes/                # Blueprints de aplicación
│   ├── admin.py           # Panel administrativo
│   ├── student.py         # Portal de estudiantes
│   ├── auth.py            # Autenticación
│   ├── api.py             # API endpoints
│   └── nfc.py             # Control NFC y QR
├── templates/             # Templates HTML (Jinja2)
├── static/                # Assets CSS, JS, imágenes
├── utils/                 # Utilidades (seguridad, analytics)
├── seed_products.py       # Datos iniciales de productos
└── requirements.txt       # Dependencias Python
```

---

## 🔧 Desarrollo Local

### 1. Configurar entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # macOS/Linux
```

### 2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación:
```bash
python app.py
```

---

## 📊 Características Principales

- ✅ Gestión completa de inventario
- ✅ Sistema de rentales con extensiones
- ✅ Panel administrativo avanzado
- ✅ Autenticación segura con 2FA
- ✅ Análisis predictivo de demanda
- ✅ Generación dinámica de QR
- ✅ API REST integrada
- ✅ Auditoría de seguridad

---

## 🌐 Despliegue en Render

Ver `DEPLOYMENT_RENDER.md` para instrucciones completas de despliegue.

Variables de entorno requeridas:
```
DATABASE_URL=postgresql://...
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta
```

---

## 🐛 Troubleshooting

### "Database not available"
- Verificar que PostgreSQL está ejecutándose
- Revisar variable `DATABASE_URL`
- Usar `python config.py` para diagnosticar

### Imágenes no se generan
- Asegurar que Pillow está instalado: `pip install Pillow`
- Carpeta `static/uploads` existe y tiene permisos

### 2FA no funciona
- Verificar variables de MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD
- En desarrollo, se generan códigos en consola

---

## 📝 Notas Importantes

- El archivo `app.py` ha sido modularizado en `core/` para mayor mantenibilidad
- Todos los datos de prueba se generan automáticamente al iniciar
- El sistema es resistente a fallos de base de datos (modo degradado)
- Las imágenes de items se generan dinámicamente bajo demanda

---

**Versión**: 2.0 (Modularizada)
**Última actualización**: Diciembre 2025
