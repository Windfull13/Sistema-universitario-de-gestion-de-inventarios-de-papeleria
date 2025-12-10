"""Rutas de estudiante: dashboard, rentals, estadísticas"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from models import Item, Transaction, User, db
from datetime import datetime, timedelta
from sqlalchemy import and_, desc
from functools import wraps
import logging

logger = logging.getLogger(__name__)
student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    """Decorador para requerir rol student"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user or g.user.role != 'student':
            flash('Acceso denegado', 'danger')
            return redirect(url_for('auth.student_login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/')
@student_required
def student():
    """Dashboard de estudiante con productos disponibles"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    
    query = Item.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            (Item.name.ilike(f'%{search}%')) |
            (Item.description.ilike(f'%{search}%'))
        )
    
    items = query.paginate(page=page, per_page=20)
    
    # Obtener categorías con items
    categories_list = []
    categories = db.session.query(Item.category).distinct().all()
    for cat in categories:
        cat_name = cat[0]
        cat_items = Item.query.filter_by(category=cat_name).all()
        categories_list.append((cat_name, cat_items))
    
    # Alertas de rentas vencidas
    overdue = Transaction.query.filter(
        Transaction.user_id == g.user.id,
        Transaction.kind == 'rent',
        Transaction.return_date < datetime.utcnow(),
        Transaction.returned == False
    ).all()
    
    return render_template('student_dashboard.html',
                         items=items,
                         categories=categories_list,
                         search=search,
                         selected_category=category,
                         overdue=overdue)

@student_bp.route('/rentals')
@student_required
def student_rentals():
    """Gestionar alquileres activos y historial"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'active')  # active, overdue, returned
    
    query = Transaction.query.filter_by(user_id=g.user.id)
    
    if status == 'active':
        query = query.filter(
            and_(
                Transaction.kind == 'rent',
                Transaction.returned == False,
                Transaction.return_date >= datetime.utcnow()
            )
        )
    elif status == 'overdue':
        query = query.filter(
            and_(
                Transaction.kind == 'rent',
                Transaction.returned == False,
                Transaction.return_date < datetime.utcnow()
            )
        )
    elif status == 'returned':
        query = query.filter(
            and_(
                Transaction.kind == 'rent',
                Transaction.returned == True
            )
        )
    else:
        query = query.filter_by(kind='rent')
    
    rentals = query.order_by(desc(Transaction.timestamp)).paginate(page=page, per_page=20)
    
    return render_template('student_rentals.html',
                         rentals=rentals,
                         status=status)

@student_bp.route('/rentals/<int:transaction_id>/return', methods=['POST'])
@student_required
def return_rental(transaction_id):
    """Devolver artículo alquilado"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.user_id != g.user.id:
        flash('No tienes permiso para esta acción', 'danger')
        return redirect(url_for('student.student_rentals'))
    
    if transaction.returned:
        flash('Este artículo ya fue devuelto', 'info')
        return redirect(url_for('student.student_rentals'))
    
    try:
        transaction.returned = True
        transaction.actual_return_date = datetime.utcnow()
        
        # Restaurar stock
        item = Item.query.get(transaction.item_id)
        if item:
            item.stock += transaction.quantity
        
        db.session.commit()
        logger.info(f"Student {g.user.id} returned rental: {transaction.id}")
        flash('Artículo devuelto exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error returning rental: {e}")
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('student.student_rentals'))

@student_bp.route('/rentals/<int:transaction_id>/request-extension', methods=['POST'])
@student_required
def request_extension(transaction_id):
    """Solicitar extensión de alquiler"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.user_id != g.user.id:
        flash('No tienes permiso para esta acción', 'danger')
        return redirect(url_for('student.student_rentals'))
    
    if transaction.returned:
        flash('No puedes extender una renta devuelta', 'danger')
        return redirect(url_for('student.student_rentals'))
    
    # Guardar nota de extensión solicitada
    try:
        transaction.extension_requested = True
        transaction.extension_request_date = datetime.utcnow()
        db.session.commit()
        logger.info(f"Student {g.user.id} requested extension for rental: {transaction.id}")
        flash('Solicitud de extensión enviada al administrador', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
    
    return redirect(url_for('student.student_rentals'))

@student_bp.route('/statistics')
@student_required
def student_statistics():
    """Estadísticas personales de estudiante"""
    user_id = g.user.id
    
    # Transacciones totales
    total_transactions = Transaction.query.filter_by(user_id=user_id).count()
    
    # Compras totales
    total_purchases = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.kind == 'buy'
    ).count()
    
    # Alquileres totales
    total_rentals = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.kind == 'rent'
    ).count()
    
    # Gasto total
    total_spent = db.session.query(db.func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.kind.in_(['buy', 'rent'])
    ).scalar() or 0
    
    # Alquileres activos
    active_rentals = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.kind == 'rent',
        Transaction.returned == False
    ).count()
    
    # Alquileres vencidos
    overdue_rentals = Transaction.query.filter(
        Transaction.user_id == user_id,
        Transaction.kind == 'rent',
        Transaction.return_date < datetime.utcnow(),
        Transaction.returned == False
    ).count()
    
    # Productos más alquilados
    popular_items = db.session.query(
        Item,
        db.func.count(Transaction.id).label('count')
    ).join(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.kind == 'rent'
    ).group_by(Item.id).order_by(desc(db.func.count(Transaction.id))).limit(5).all()
    
    # Historial reciente
    recent = Transaction.query.filter_by(user_id=user_id).order_by(
        desc(Transaction.timestamp)
    ).limit(10).all()
    
    stats = {
        'total_transactions': total_transactions,
        'total_purchases': total_purchases,
        'total_rentals': total_rentals,
        'total_spent': float(total_spent),
        'active_rentals': active_rentals,
        'overdue_rentals': overdue_rentals,
        'popular_items': popular_items,
        'recent': recent
    }
    
    return render_template('student_statistics.html', stats=stats)

@student_bp.route('/settings', methods=['GET', 'POST'])
@student_required
def student_settings():
    """Configuración de perfil de estudiante"""
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
                logger.info(f"Student {g.user.id} changed password")
                flash('Contraseña actualizada', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('student_settings.html')
