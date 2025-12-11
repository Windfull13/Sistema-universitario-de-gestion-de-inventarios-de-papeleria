"""Rutas de administrador: dashboard, CRUD productos, seguridad"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, g
from models import User, Item, Transaction, LoginAttempt, ActiveSession, db
from utils.analytics import get_analytics_data, calculate_seasonal_demand, get_predictive_analytics, get_supplier_intelligence
from utils.security import get_client_ip
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import logging
import os

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para requerir rol admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import g
        if not g.user or g.user.role != 'admin':
            flash('Acceso denegado', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def index():
    """Dashboard de administrador"""
    try:
        analytics = get_analytics_data()
        seasonal = calculate_seasonal_demand()
        
        # Todas los items
        items = Item.query.all()
        
        # Últimas transacciones
        recent_transactions = Transaction.query.order_by(desc(Transaction.timestamp)).limit(10).all()
        
        # Items bajos en stock
        low_stock = Item.query.filter(Item.stock <= 2).all()
        
        logger.info(f"Admin dashboard loaded: {len(items)} items, analytics: {analytics['general']['total_items']}")
        
        return render_template('admin.html',
                             analytics=analytics,
                             seasonal=seasonal,
                             items=items,
                             recent_transactions=recent_transactions,
                             low_stock=low_stock)
    except Exception as e:
        logger.error(f"Error en admin dashboard: {str(e)}", exc_info=True)
        flash(f'Error: {str(e)}', 'danger')
        # Proporcionar datos mínimos en caso de error
        empty_analytics = {
            'general': {'total_items': 0, 'total_stock': 0, 'low_stock_count': 0, 'active_rentals': 0, 'overdue_count': 0},
            'reorder_recommendation': [],
            'category_distribution': []
        }
        return render_template('admin.html',
                             analytics=empty_analytics,
                             seasonal={},
                             items=[],
                             recent_transactions=[],
                             low_stock=[])

@admin_bp.route('/items')
@admin_required
def admin_items():
    """Listar todos los productos"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    
    query = Item.query
    if category:
        query = query.filter_by(category=category)
    
    # Ordenar por categoría y luego por nombre (para mantener orden consistente)
    items = query.order_by(Item.category, Item.name).paginate(page=page, per_page=20)
    categories = db.session.query(Item.category).distinct().all()
    
    return render_template('admin_items.html', 
                         items=items, 
                         categories=[c[0] for c in categories],
                         selected_category=category)

@admin_bp.route('/items/add', methods=['GET', 'POST'])
@admin_required
def admin_add_item():
    """Agregar producto"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            price = float(request.form.get('price', 0))
            stock = int(request.form.get('stock', 0))
            rentable = request.form.get('rentable') == 'on'
            
            if not name or not category or price <= 0 or stock < 0:
                flash('Datos incompletos o inválidos', 'danger')
                return render_template('admin_add_item.html')
            
            # Manejo de imagen
            image = 'default.jpg'
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    import secrets
                    filename = secrets.token_hex(8) + '.jpg'
                    os.makedirs('static/uploads', exist_ok=True)
                    file.save(f'static/uploads/{filename}')
                    image = filename
            
            new_item = Item(
                name=name,
                description=description,
                category=category,
                price=price,
                stock=stock,
                rentable=rentable,
                image_filename=image
            )
            db.session.add(new_item)
            db.session.commit()
            
            logger.info(f"Admin {request.remote_addr} added item: {name}")
            flash('Producto agregado exitosamente', 'success')
            return redirect(url_for('admin.admin_items'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding item: {e}")
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin_add_item.html')

@admin_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_item(item_id):
    """Editar producto"""
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        try:
            item.name = request.form.get('name', '').strip()
            item.description = request.form.get('description', '').strip()
            item.category = request.form.get('category', '').strip()
            item.price = float(request.form.get('price', 0))
            item.stock = int(request.form.get('stock', 0))
            item.rentable = request.form.get('rentable') == 'on'
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    import secrets
                    filename = secrets.token_hex(8) + '.jpg'
                    os.makedirs('static/uploads', exist_ok=True)
                    file.save(f'static/uploads/{filename}')
                    item.image_filename = filename
            
            db.session.commit()
            logger.info(f"Admin edited item: {item.name}")
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('admin.admin_items'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin_edit_item.html', item=item)

@admin_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@admin_required
def admin_delete_item(item_id):
    """Eliminar producto"""
    item = Item.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Admin deleted item: {item.name}")
        flash('Producto eliminado', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_items'))

@admin_bp.route('/transactions')
@admin_required
def admin_transactions():
    """Ver transacciones"""
    page = request.args.get('page', 1, type=int)
    kind = request.args.get('kind', '')
    returned = request.args.get('returned', '')
    overdue = request.args.get('overdue', '')
    
    query = Transaction.query
    if kind:
        query = query.filter_by(kind=kind)
    if returned:
        query = query.filter_by(returned=(returned.lower() == 'true'))
    if overdue:
        query = Transaction.search(overdue=True)
    
    pagination = query.order_by(desc(Transaction.timestamp)).paginate(page=page, per_page=30)
    transactions = pagination.items
    
    return render_template('admin_transactions.html', 
                         transactions=transactions, 
                         pagination=pagination,
                         kind=kind,
                         returned=returned,
                         overdue=overdue)

@admin_bp.route('/analytics')
@admin_required
def admin_analytics():
    """Dashboard de análisis"""
    try:
        analytics = get_analytics_data()
        seasonal = calculate_seasonal_demand()
        
        # Gráficos de datos
        daily_data = db.session.query(
            func.date(Transaction.timestamp).label('date'),
            func.count(Transaction.id).label('count')
        ).filter(
            Transaction.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).group_by(func.date(Transaction.timestamp)).all()
        
        dates = [str(d[0]) for d in daily_data]
        counts = [d[1] for d in daily_data]
        
        return render_template('admin_analytics.html',
                             analytics=analytics,
                             seasonal=seasonal,
                             dates=dates,
                             counts=counts)
    except Exception as e:
        logger.error(f"Error in analytics: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin_analytics.html')

@admin_bp.route('/predictive')
@admin_required
def admin_predictive():
    """Panel Predictivo - Forecast de ingresos y productos trending"""
    try:
        predictive_data = get_predictive_analytics()
        
        return render_template('admin_predictive.html',
                             predictive=predictive_data)
    except Exception as e:
        logger.error(f"Error in predictive analytics: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin_predictive.html', predictive={'error': str(e)})

@admin_bp.route('/suppliers')
@admin_required
def admin_suppliers():
    """Panel de Análisis de Proveedores - Detección de lentos e inseguros"""
    try:
        supplier_data = get_supplier_intelligence()
        
        return render_template('admin_suppliers.html',
                             supplier=supplier_data)
    except Exception as e:
        logger.error(f"Error in supplier analytics: {e}")
        flash(f'Error: {str(e)}', 'danger')
        return render_template('admin_suppliers.html', supplier={'error': str(e)})

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    """Configuración de administrador"""
    from flask import g
    
    if request.method == 'POST':
        try:
            old_password = request.form.get('old_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            from utils.security import verify_password, hash_password
            
            if not verify_password(g.user.password_hash, old_password):
                flash('Contraseña actual incorrecta', 'danger')
            elif len(new_password) < 6:
                flash('Nueva contraseña debe tener al menos 6 caracteres', 'danger')
            elif new_password != confirm_password:
                flash('Las contraseñas no coinciden', 'danger')
            else:
                g.user.password_hash = hash_password(new_password)
                db.session.commit()
                logger.info(f"Admin {g.user.username} changed password")
                flash('Contraseña actualizada', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin_settings.html', user=g.user)

@admin_bp.route('/security')
@admin_required
def security_dashboard():
    """Dashboard de seguridad"""
    # Intentos fallidos en últimas 24 horas
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24),
        LoginAttempt.success == False
    ).order_by(desc(LoginAttempt.timestamp)).limit(50).all()
    
    # IPs sospechosas (5+ intentos fallidos)
    suspicious_ips = db.session.query(
        LoginAttempt.client_ip,
        func.count(LoginAttempt.id).label('count')
    ).filter(
        LoginAttempt.success == False,
        LoginAttempt.timestamp >= datetime.utcnow() - timedelta(hours=24)
    ).group_by(LoginAttempt.client_ip).having(
        func.count(LoginAttempt.id) >= 5
    ).all()
    
    # Sesiones activas
    active_sessions = ActiveSession.query.filter(
        ActiveSession.expires_at > datetime.utcnow()
    ).all()
    
    return render_template('security_dashboard.html',
                         failed_attempts=failed_attempts,
                         suspicious_ips=suspicious_ips,
                         active_sessions=active_sessions)

@admin_bp.route('/security-log')
@admin_required
def admin_security_log():
    """Registro de intentos de login"""
    page = request.args.get('page', 1, type=int)
    
    logs = LoginAttempt.query.order_by(desc(LoginAttempt.timestamp)).paginate(page=page, per_page=50)
    
    return render_template('admin_security_log.html', logs=logs)

@admin_bp.route('/rental-extensions')
@admin_required
def admin_rental_extensions():
    """Gestionar solicitudes de extensión de alquiler"""
    from datetime import datetime, date
    
    page = request.args.get('page', 1, type=int)
    
    try:
        # Rentals pendientes de extensión (vencidas pero no devueltas)
        pending_extensions = db.session.query(Transaction).filter(
            Transaction.kind == 'rent',
            Transaction.rent_due_date < date.today(),
            Transaction.returned == False
        ).order_by(desc(Transaction.rent_due_date)).paginate(page=page, per_page=20)
        
        # Rentals con extensiones aprobadas (no devueltas aún)
        approved_extensions = db.session.query(Transaction).filter(
            Transaction.kind == 'rent',
            Transaction.extension_approved == True,
            Transaction.returned == False
        ).order_by(desc(Transaction.rent_due_date)).all()
        
        return render_template('admin_rental_extensions.html', 
                             pending_extensions=pending_extensions,
                             approved_extensions=approved_extensions,
                             today=date.today())
    except Exception as e:
        logger.error(f"Error en admin_rental_extensions: {str(e)}", exc_info=True)
        flash(f'Error cargando extensiones: {str(e)}', 'danger')
        # Retornar paginación vacía
        empty_query = db.session.query(Transaction).filter(Transaction.id == -1).paginate(page=1, per_page=20)
        return render_template('admin_rental_extensions.html',
                             pending_extensions=empty_query,
                             approved_extensions=[],
                             today=date.today())

@admin_bp.route('/rental-extensions/<int:transaction_id>/extend', methods=['POST'])
@admin_required
def extend_rental(transaction_id):
    """Extender período de alquiler"""
    from datetime import date, timedelta as td
    
    transaction = Transaction.query.get_or_404(transaction_id)
    days = request.form.get('days', 7, type=int)
    
    try:
        # Extender la fecha de devolución esperada
        if transaction.rent_due_date:
            transaction.rent_due_date = transaction.rent_due_date + td(days=days)
        
        # Marcar extensión como aprobada
        transaction.extension_approved = True
        transaction.extension_days = days
        transaction.extension_approved_at = datetime.utcnow()
        
        db.session.commit()
        logger.info(f"Rental extended: {transaction.id}, {days} days")
        flash(f'Alquiler extendido {days} días', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error extending rental {transaction_id}: {str(e)}")
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_rental_extensions'))

@admin_bp.route('/nfc-control')
@admin_required
def nfc_control():
    """Control NFC/QR para admin"""
    try:
        items = Item.query.all()
        return render_template('nfc_control.html', items=items)
    except Exception as e:
        logger.error(f"Error en nfc_control: {e}")
        flash('Error cargando control NFC', 'danger')
        return redirect(url_for('admin.dashboard'))
