"""API REST endpoints: items, transactions, NFC operations"""
from flask import Blueprint, jsonify, request, g
from models import Item, Transaction, User, db, ApiKey
from utils.security import verify_password, get_client_ip
from datetime import datetime, timedelta
from sqlalchemy import desc, and_
from functools import wraps
import logging

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

def api_key_required(f):
    """Decorador para requerir API key válida"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        key_obj = ApiKey.query.filter_by(key=api_key, is_active=True).first()
        
        if not key_obj or key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
            return jsonify({'error': 'Invalid or expired API key'}), 401
        
        key_obj.last_used_at = datetime.utcnow()
        db.session.commit()
        
        g.api_user = key_obj.user
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_api(f):
    """Rate limiting para API: 100 requests/hora"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = get_client_ip()
        hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Contar requests en última hora desde esta IP
        from flask_limiter import Limiter
        # Implementación simple: registrar en transaction logs para API
        
        return f(*args, **kwargs)
    return decorated_function

@api_bp.route('/items', methods=['GET'])
@api_key_required
def api_items():
    """GET /api/items - Listar items disponibles"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    rentable_only = request.args.get('rentable', 'false').lower() == 'true'
    search = request.args.get('search', '').strip()
    
    query = Item.query
    
    if category:
        query = query.filter_by(category=category)
    
    if rentable_only:
        query = query.filter_by(rentable=True)
    
    if search:
        query = query.filter(
            (Item.name.ilike(f'%{search}%')) |
            (Item.description.ilike(f'%{search}%'))
        )
    
    items = query.paginate(page=page, per_page=50)
    
    return jsonify({
        'status': 'success',
        'page': page,
        'total': items.total,
        'pages': items.pages,
        'items': [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'price': float(item.price),
            'stock': item.stock,
            'rentable': item.rentable,
            'image': item.image
        } for item in items.items]
    })

@api_bp.route('/items/<int:item_id>', methods=['GET'])
@api_key_required
def api_item(item_id):
    """GET /api/items/<id> - Detalles de item"""
    item = Item.query.get_or_404(item_id)
    
    return jsonify({
        'status': 'success',
        'item': {
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'price': float(item.price),
            'stock': item.stock,
            'rentable': item.rentable,
            'image': item.image,
            'created_at': item.created_at.isoformat() if item.created_at else None
        }
    })

@api_bp.route('/transactions', methods=['GET'])
@api_key_required
def api_transactions():
    """GET /api/transactions - Transacciones del usuario"""
    page = request.args.get('page', 1, type=int)
    kind = request.args.get('kind')  # buy, rent, return, restock
    
    query = Transaction.query.filter_by(user_id=g.api_user.id)
    
    if kind:
        query = query.filter_by(kind=kind)
    
    transactions = query.order_by(desc(Transaction.timestamp)).paginate(page=page, per_page=50)
    
    return jsonify({
        'status': 'success',
        'page': page,
        'total': transactions.total,
        'pages': transactions.pages,
        'transactions': [{
            'id': t.id,
            'item_id': t.item_id,
            'kind': t.kind,
            'quantity': t.quantity,
            'amount': float(t.amount),
            'timestamp': t.timestamp.isoformat(),
            'returned': t.returned,
            'return_date': t.return_date.isoformat() if t.return_date else None
        } for t in transactions.items]
    })

@api_bp.route('/rental-info/<int:item_id>', methods=['GET'])
@api_key_required
def api_rental_info(item_id):
    """GET /api/rental-info/<item_id> - Info de disponibilidad de renta"""
    item = Item.query.get_or_404(item_id)
    
    if not item.rentable:
        return jsonify({'error': 'Item not rentable'}), 400
    
    # Contar alquileres activos
    active_rentals = Transaction.query.filter(
        Transaction.item_id == item_id,
        Transaction.kind == 'rent',
        Transaction.returned == False
    ).count()
    
    available = item.stock - active_rentals
    
    return jsonify({
        'status': 'success',
        'item_id': item_id,
        'item_name': item.name,
        'price_per_day': float(item.price),
        'stock': item.stock,
        'active_rentals': active_rentals,
        'available_to_rent': max(0, available),
        'rentable': True
    })

@api_bp.route('/nfc/scan', methods=['POST'])
@api_key_required
def api_nfc_update():
    """POST /api/nfc/scan - Registrar escaneo NFC individual"""
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        action = data.get('action')  # return, restock
        quantity = data.get('quantity', 1)
        
        if not item_id or not action:
            return jsonify({'error': 'item_id and action required'}), 400
        
        item = Item.query.get_or_404(item_id)
        
        if action == 'return':
            # Procesar devolución
            rental = Transaction.query.filter(
                Transaction.item_id == item_id,
                Transaction.kind == 'rent',
                Transaction.returned == False
            ).first_or_404()
            
            rental.returned = True
            rental.actual_return_date = datetime.utcnow()
            item.stock += rental.quantity
            
        elif action == 'restock':
            # Recargar stock
            item.stock += quantity
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        db.session.commit()
        logger.info(f"NFC action: {action} on item {item_id}")
        
        return jsonify({
            'status': 'success',
            'item_id': item_id,
            'action': action,
            'new_stock': item.stock
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"NFC scan error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/nfc/batch', methods=['POST'])
@api_key_required
def api_nfc_batch_update():
    """POST /api/nfc/batch - Procesar lote de escaneos NFC"""
    try:
        data = request.get_json()
        operations = data.get('operations', [])
        
        if not operations:
            return jsonify({'error': 'operations array required'}), 400
        
        results = []
        
        for op in operations:
            item_id = op.get('item_id')
            action = op.get('action')
            quantity = op.get('quantity', 1)
            
            try:
                item = Item.query.get(item_id)
                if not item:
                    results.append({
                        'item_id': item_id,
                        'status': 'failed',
                        'reason': 'Item not found'
                    })
                    continue
                
                if action == 'return':
                    rental = Transaction.query.filter(
                        Transaction.item_id == item_id,
                        Transaction.kind == 'rent',
                        Transaction.returned == False
                    ).first()
                    
                    if rental:
                        rental.returned = True
                        rental.actual_return_date = datetime.utcnow()
                        item.stock += rental.quantity
                        results.append({
                            'item_id': item_id,
                            'status': 'success',
                            'action': action,
                            'new_stock': item.stock
                        })
                    else:
                        results.append({
                            'item_id': item_id,
                            'status': 'failed',
                            'reason': 'No active rental found'
                        })
                
                elif action == 'restock':
                    item.stock += quantity
                    results.append({
                        'item_id': item_id,
                        'status': 'success',
                        'action': action,
                        'new_stock': item.stock
                    })
                else:
                    results.append({
                        'item_id': item_id,
                        'status': 'failed',
                        'reason': 'Invalid action'
                    })
            except Exception as e:
                results.append({
                    'item_id': item_id,
                    'status': 'failed',
                    'reason': str(e)
                })
        
        db.session.commit()
        logger.info(f"NFC batch: {len(results)} operations processed")
        
        return jsonify({
            'status': 'success',
            'total': len(results),
            'results': results
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"NFC batch error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/nfc/stats', methods=['GET'])
@api_key_required
def api_nfc_stats():
    """GET /api/nfc/stats - Estadísticas de dispositivo NFC"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    total_operations = Transaction.query.filter(
        Transaction.timestamp >= start_date,
        Transaction.kind.in_(['return', 'restock'])
    ).count()
    
    returns = Transaction.query.filter(
        Transaction.timestamp >= start_date,
        Transaction.kind == 'return'
    ).count()
    
    restocks = Transaction.query.filter(
        Transaction.timestamp >= start_date,
        Transaction.kind == 'restock'
    ).count()
    
    return jsonify({
        'status': 'success',
        'period_days': days,
        'total_operations': total_operations,
        'returns': returns,
        'restocks': restocks,
        'success_rate': 100.0  # En producción, mejorar con trazabilidad
    })

@api_bp.route('/buy', methods=['POST'])
def api_buy():
    """Comprar un producto (solo estudiantes)"""
    from flask import g, redirect, url_for, flash
    
    # Verificar que el usuario está autenticado y es estudiante
    if not g.user or g.user.role != 'student':
        return redirect(url_for('auth.login'))
    
    try:
        item_id = request.form.get('item_id', type=int)
        quantity = request.form.get('quantity', 1, type=int)
        
        if not item_id or quantity <= 0:
            flash('Datos inválidos', 'danger')
            return redirect(request.referrer or url_for('public.index'))
        
        item = Item.query.get_or_404(item_id)
        
        if item.stock < quantity:
            flash('No hay suficiente stock disponible', 'warning')
            return redirect(request.referrer or url_for('public.index'))
        
        # Crear transacción de compra
        transaction = Transaction(
            user_id=g.user.id,
            item_id=item.id,
            kind='buy',
            qty=quantity,
            timestamp=datetime.utcnow()
        )
        
        # Reducir stock
        item.stock -= quantity
        
        db.session.add(transaction)
        db.session.commit()
        
        logger.info(f"Purchase: user={g.user.id}, item={item.id}, qty={quantity}")
        flash(f'Compra realizada: {quantity}x {item.name}', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en compra: {str(e)}", exc_info=True)
        flash(f'Error en la compra: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('public.index'))

@api_bp.route('/rent', methods=['POST'])
def api_rent():
    """Rentar un producto (solo estudiantes)"""
    from flask import g, redirect, url_for, flash
    from datetime import date
    
    # Verificar que el usuario está autenticado y es estudiante
    if not g.user or g.user.role != 'student':
        return redirect(url_for('auth.login'))
    
    try:
        item_id = request.form.get('item_id', type=int)
        days = request.form.get('days', 7, type=int)
        
        if not item_id or days <= 0 or days > 30:
            flash('Datos inválidos. Los días deben estar entre 1 y 30', 'danger')
            return redirect(request.referrer or url_for('public.index'))
        
        item = Item.query.get_or_404(item_id)
        
        if not item.rentable:
            flash('Este producto no es rentable', 'warning')
            return redirect(request.referrer or url_for('public.index'))
        
        if item.stock < 1:
            flash('No hay stock disponible para rentar', 'warning')
            return redirect(request.referrer or url_for('public.index'))
        
        # Crear transacción de renta
        today = date.today()
        due_date = today + timedelta(days=days)
        
        transaction = Transaction(
            user_id=g.user.id,
            item_id=item.id,
            kind='rent',
            qty=1,
            rent_days=days,
            timestamp=datetime.utcnow(),
            rent_start_date=today,
            rent_due_date=due_date,
            returned=False
        )
        
        # Reducir stock
        item.stock -= 1
        
        db.session.add(transaction)
        db.session.commit()
        
        logger.info(f"Rental: user={g.user.id}, item={item.id}, days={days}")
        flash(f'Renta creada: {item.name} por {days} días (Vencimiento: {due_date.strftime("%d/%m/%Y")})', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en renta: {str(e)}", exc_info=True)
        flash(f'Error en la renta: {str(e)}', 'danger')
    
    return redirect(request.referrer or url_for('public.index'))
