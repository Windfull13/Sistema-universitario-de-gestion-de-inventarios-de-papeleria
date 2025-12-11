# ✨ MEJORAS A LA PÁGINA DE EXTENSIONES DE PRÉSTAMOS

## ¿Qué se agregó?

La página `/admin/rental-extensions` ahora muestra:

### 📋 TAB 1: "Solicitudes Pendientes" (Alquileres Vencidos)
Muestra todos los alquileres que han superado su fecha de devolución.

**Información mostrada por cada alquiler:**
- ✅ **Estudiante** - Email y nombre de usuario
- ✅ **Item Alquilado** - Nombre del producto y cantidad
- ✅ **Fecha de Vencimiento** - Cuándo debería haber devuelto
- ✅ **Días de Retraso** - Cuántos días vencido (ej: 5 días)
- ✅ **Acciones** - Campo para ingresar días + botón "Extender"

**Ejemplo real:**
```
Estudiante:    juan@gmail.com (juan_abc123)
Item:          Cuaderno cosido (Cantidad: 1)
Vencimiento:   15/12/2025
Retraso:       5 días
Acción:        [7] Extender → Extiende 7 días más
```

### 📊 TAB 2: "Historial de Extensiones" (Alquileres Activos)
Muestra los últimos 10 alquileres activos para monitoreo.

**Información mostrada por cada alquiler:**
- ✅ **Estudiante** - Email y usuario
- ✅ **Item** - Producto alquilado y cantidad
- ✅ **Inicio de Alquiler** - Cuándo comenzó (ej: 01/12/2025)
- ✅ **Vencimiento** - Cuándo debe devolver (ej: 15/12/2025)
- ✅ **Días Restantes** - Con código de color:
  - 🟢 Verde: Más de 3 días (normal)
  - 🟡 Amarillo: 1-3 días (próximo a vencer)
  - 🔴 Rojo: Vencido (necesita extensión)
- ✅ **Estado** - Activo / Vencido / Devuelto

---

## 🎨 Mejoras de UX (Experiencia del Usuario)

### Alertas Informativas
```
⚠️ 5 alquiler(es) vencido(s) - Los estudiantes pueden solicitar extensión...
```
Explica qué significan los datos.

### Código de Colores
```
Fila roja   = Alquiler vencido (requiere acción)
Badge rojo  = Vencido hace X días
Badge amarillo = Próximo a vencer
Badge verde = Tiempo disponible
Badge azul  = Activo
```

### Paginación
Si hay más de 20 alquileres vencidos, muestra páginas:
```
Primera | Anterior | 1 2 3 | Siguiente | Última
```

---

## 📌 Cómo Usar Esta Página

### Proceso: Extender un Alquiler Vencido

1. **Abre la página** → `/admin/rental-extensions`
2. **Ve la Tab "Solicitudes Pendientes"**
3. **Encuentra el estudiante que necesita extensión**
4. **Ingresa los días** en el campo (ej: 7 días)
5. **Haz click en "Extender"**
6. **Listo!** - El vencimiento se actualizó automáticamente

### Ejemplo:
```
Juan vencía el 10/12/2025 y hoy es 15/12/2025 (5 días de retraso)

Admin ingresa: 7 días
↓
Nuevo vencimiento: 22/12/2025 (7 días más)
↓
Juan ahora puede devolver el 22/12/2025
```

---

## 🔧 Cambios Técnicos

### En `routes/admin.py`:
```python
@admin_bp.route('/rental-extensions')
def admin_rental_extensions():
    # 1. Obtiene rentals vencidos
    pending_extensions = Transaction.query.filter(
        kind='rent',
        rent_due_date < ahora,
        returned=False
    )
    
    # 2. Obtiene rentals activos (historial)
    approved_extensions = Transaction.query.filter(
        kind='rent',
        returned=False
    ).limit(10)
    
    # 3. Pasa datos + fecha/hora actual al template
    return render_template(..., 
                         pending_extensions=pending_extensions,
                         approved_extensions=approved_extensions,
                         now=datetime.utcnow())
```

### En `templates/admin_rental_extensions.html`:
```html
<!-- Muestra lista de vencidos -->
{% for rental in pending_extensions.items %}
  <tr>
    <td>{{ rental.user.email }}</td>
    <td>{{ rental.item.name }}</td>
    <td>{{ rental.rent_due_date.strftime('%d/%m/%Y') }}</td>
    <td>
      {% set dias = (now.date() - rental.rent_due_date.date()).days %}
      {{ dias }} días
    </td>
    <td>
      <form method="post" action="/admin/rental-extensions/{{ rental.id }}/extend">
        <input type="number" name="days" value="7" min="1" max="30">
        <button type="submit">Extender</button>
      </form>
    </td>
  </tr>
{% endfor %}
```

---

## 📊 Datos Usados en Ejemplos

Cuando **NO hay datos reales**, la página muestra mensajes útiles:

```
✓ ¡Excelente! No hay alquileres vencidos. 
Todos los estudiantes han devuelto o extendido sus alquileres.
```

```
No hay alquileres activos en el sistema.
```

Esto es NORMAL en un sistema vacío. Los datos se llenan cuando:
1. Los estudiantes alquilan items
2. Llegan a las fechas de vencimiento
3. No devuelven a tiempo

---

## 🚀 Próximas Mejoras Posibles

- [ ] Enviar notificación por email al estudiante cuando se extienda
- [ ] Historial completo de extensiones (cuántas veces se extendió)
- [ ] Multa por retraso (calcular automáticamente)
- [ ] Reporte de estudiantes con muchas extensiones
- [ ] Restricción: máximo 2 extensiones por alquiler
- [ ] Botón para marcar como "devuelto" desde aquí

---

## 🎓 Concepto: Alquileres (Rentals)

En el sistema, un **alquiler (rental)** es:

```
Usuario alquila → Item por X días → Vencimiento (rent_due_date)
                ↓
        Si vence, puede → Extender (agregar días)
                ↓
        Eventualmente → Devuelve (returned=True)
```

**Estados posibles:**
```
En proceso (activo)
  - Alquilado y dentro del plazo
Vencido (overdue)
  - Pasó la fecha pero no devolvió
Devuelto (completed)
  - Ya devolvió el item
```

---

## ✅ Checklist de Funcionalidad

- ✅ Muestra alquileres vencidos
- ✅ Muestra historial de activos
- ✅ Permite extender con un número de días
- ✅ Actualiza automáticamente la BD
- ✅ Código de colores por estado
- ✅ Paginación si hay muchos
- ✅ Mensajes si no hay datos
- ✅ Responsive (funciona en móvil)

---

**Versión:** 1.0
**Fecha:** 10/12/2025
**Commit:** feat: improve rental extensions page with better data display
