# 🚀 Guía de Despliegue en Render

## Pasos para desplegar tu Sistema de Inventarios en Render

### 1. **Preparar tu repositorio GitHub**

```powershell
# Inicializar Git (si no lo has hecho)
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Proyecto listo para despliegue"

# Crear repositorio en GitHub y hacer push
git push origin main
```

### 2. **Crear cuenta en Render**

1. Ve a [https://render.com](https://render.com)
2. Regístrate con tu cuenta de GitHub
3. Autoriza a Render acceder a tus repositorios

### 3. **Crear un nuevo servicio web en Render**

1. En el dashboard de Render, haz clic en **"+ New"**
2. Selecciona **"Web Service"**
3. Conecta tu repositorio: busca `Proyecto_inventarios`
4. Completa los detalles:
   - **Name**: `proyecto-inventarios` (o el que prefieras)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (inicialmente)

### 4. **Configurar variables de entorno**

En Render, ve a la sección **"Environment"** y añade estas variables:

```
FLASK_ENV=production
SECRET_KEY=generar-una-clave-muy-segura-aqui
JWT_SECRET_KEY=generar-otra-clave-segura
MAIL_USERNAME=tu_email@gmail.com
MAIL_PASSWORD=tu_contraseña_o_app_password
MAIL_DEFAULT_SENDER=Sistema de Inventario <tu_email@gmail.com>
```

### 5. **Crear base de datos PostgreSQL (Render Database)**

1. Desde tu dashboard de Render, haz clic en **"+ New"**
2. Selecciona **"PostgreSQL"**
3. Completa los detalles:
   - **Name**: `proyecto-inventarios-db`
   - **Database**: `inventarios`
   - **User**: `inventarios`
   - **Plan**: Free

4. Una vez creada, copia la **Internal Database URL** y agrégala como variable en tu Web Service:
   - **Variable name**: `DATABASE_URL`
   - **Value**: (la URL que copiaste)

### 6. **Inicializar la base de datos**

Después del primer despliegue:

```powershell
# Conectarte a la consola de Render
# O ejecutar manualmente:
python migrate_db.py
```

### 7. **Tu URL pública**

Una vez desplegado, tu app estará disponible en:

```
https://proyecto-inventarios.onrender.com
```

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError"
- Asegúrate de que `requirements.txt` esté actualizado
- Verifica que todas las importaciones estén disponibles

### Error: "Database connection error"
- Verifica que `DATABASE_URL` esté configurada correctamente
- Asegúrate de que la base de datos PostgreSQL esté creada

### Error: "Email not sending"
- Usa contraseña de aplicación de Gmail (no tu contraseña de cuenta)
- Activa acceso de apps menos seguras si es necesario

---

## 📝 Notas importantes

- El plan **Free** de Render tiene limitaciones (se pausa si no recibe tráfico)
- Para producción real, considera plan **Starter** ($7/mes)
- Las variables de entorno se configuran en Render, NO en `.env`
- El archivo `.gitignore` evita subir datos sensibles
- La base de datos PostgreSQL es más confiable que SQLite para producción

---

## 🔒 Seguridad

Antes de desplegar:

1. ✅ Cambia `SECRET_KEY` por una clave aleatoria fuerte
2. ✅ Cambia `JWT_SECRET_KEY` por una nueva
3. ✅ Usa credenciales seguras de email
4. ✅ Configura `SESSION_COOKIE_SECURE = True` en producción (ya hecho)
5. ✅ Configura `DEBUG = False` (ya está configurado)

---

## 🎯 Próximos pasos

- Configurar dominio personalizado (opcional)
- Añadir SSL (Render lo hace automáticamente)
- Monitorear logs en Render dashboard
- Configurar auto-deploy en cada push a main
