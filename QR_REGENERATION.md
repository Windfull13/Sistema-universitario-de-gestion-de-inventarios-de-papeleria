# 🔄 Regeneración de Códigos QR para Render

## ¿Qué cambió?

Los códigos QR ahora se generan **dinámicamente** con URLs que apuntan correctamente a:
- ✅ `http://localhost:5000/item/{id}` en desarrollo
- ✅ `https://tu-proyecto.onrender.com/item/{id}` en producción

**No necesitas regenerar los 156 QRs manualmente.** Los QRs se generan al vuelo cuando se accede a las rutas.

---

## 📋 Pasos para desplegar en Render

### 1️⃣ **Actualizar variable de entorno en Render**

Una vez que Render te asigne una URL (ej: `https://sistema-universitario-de-gestion-de-inventarios-de-papeleria.onrender.com`):

1. En Render Dashboard → Tu servicio
2. Ir a **"Environment"**
3. Buscar o crear la variable `APP_URL`
4. Establecer el valor a tu URL completa:
   ```
   https://sistema-universitario-de-gestion-de-inventarios-de-papeleria.onrender.com
   ```
5. Hacer deploy

### 2️⃣ **Confirmar que los QRs funcionan**

Accede a cualquier producto en tu app y escanea el QR. Debería redirigir a:
```
https://sistema-universitario-de-gestion-de-inventarios-de-papeleria.onrender.com/item/{id}
```

---

## 🔧 Cómo funciona internamente

**Ruta donde se generan los QRs:**
```
GET /nfc/qr/<item_id>
```

**Código actualizado:**
```python
from utils.security import get_item_url

@nfc_bp.route('/qr/<int:item_id>')
def qr_item(item_id):
    url = get_item_url(item_id)  # Automáticamente usa APP_URL en prod
    qr = segno.make_micro(url, error='m')
    # ... generar imagen PNG
```

---

## ✅ Checklist antes de desplegar

- [ ] Código actualizado con `get_item_url()` (ya hecho)
- [ ] Variable `APP_URL` configurada en Render
- [ ] Base de datos PostgreSQL conectada
- [ ] Archivo `.gitignore` excluyendo carpeta QR
- [ ] `requirements.txt` actualizado con `gunicorn` y `psycopg2-binary`
- [ ] Procfile configurado
- [ ] Variables de entorno de email y seguridad configuradas

---

## 🚨 Solución de problemas

### Los QRs siguen apuntando a localhost
1. Verificar que `APP_URL` esté configurada en Render
2. Hacer deploy nuevamente (Render necesita releer las variables)
3. Limpiar caché del navegador (Ctrl+F5)

### Los QRs no se generan
- Verificar que `segno` esté en `requirements.txt`
- Ver logs en Render: **Logs** → **Live tail**

### La URL en el QR es incorrecta
- Verificar el valor exacto de `APP_URL` en Render
- Confirmar que NO tiene slash al final

---

## 📝 Nota importante

**Los QRs impresos anteriormente NO funcionarán hasta actualizar `APP_URL` en Render.**

Una vez configurado correctamente, todos los QRs generados apuntarán automáticamente a la URL correcta sin necesidad de imprimir nuevamente.

---

## 🎯 Resultado final

Cuando alguien escanee un QR impreso:
1. ✅ Se abre la app en Render
2. ✅ Accede directamente a `/item/{id}`
3. ✅ Ve los detalles del producto
4. ✅ Puede proceder con la compra/renta

¡Listo para producción! 🚀
