"""Rutas NFC/QR: generación de códigos QR y control de dispositivos"""
from flask import Blueprint, render_template, request, send_file, jsonify, g
from models import Item, Transaction, db
from utils.security import get_item_url
from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import desc, func
import logging

logger = logging.getLogger(__name__)
nfc_bp = Blueprint('nfc', __name__, url_prefix='/nfc')

try:
    import qrcode
    import segno
    HAS_QR = True
except ImportError:
    HAS_QR = False

@nfc_bp.route('/qr/home')
def qr_home():
    """GET /nfc/qr/home - Generar código QR para página principal"""
    
    if not HAS_QR:
        return jsonify({'error': 'QR library not installed'}), 500
    
    try:
        # URL de la página principal
        url = 'https://sistema-universitario-de-gestion-de.onrender.com/'
        
        # Generar QR con segno
        qr = segno.make(url, error='L', micro=False)
        
        # Convertir a PNG
        buf = BytesIO()
        qr.save(buf, kind='png', scale=5)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.error(f"QR home generation error: {e}")
        return jsonify({'error': str(e)}), 500

@nfc_bp.route('/qr/<int:item_id>')
def qr_item(item_id):
    """GET /nfc/qr/<item_id> - Generar código QR para item (enlace)"""
    item = Item.query.get_or_404(item_id)
    
    if not HAS_QR:
        return jsonify({'error': 'QR library not installed'}), 500
    
    try:
        # URL que apunta al detalle del item (funciona en localhost y en Render)
        url = get_item_url(item_id)
        
        # Generar QR con segno (usar make en lugar de make_micro para URLs largas)
        qr = segno.make(url, error='L', micro=False)
        
        # Convertir a PNG
        buf = BytesIO()
        qr.save(buf, kind='png', scale=5)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        logger.error(f"QR generation error: {e}")
        return jsonify({'error': str(e)}), 500

@nfc_bp.route('/generate/<int:item_id>')
def generate_nfc_qr(item_id):
    """GET /nfc/generate/<item_id> - Generar QR para etiqueta NFC"""
    item = Item.query.get_or_404(item_id)
    
    if not HAS_QR:
        return jsonify({'error': 'QR library not installed'}), 500
    
    try:
        # Datos para la etiqueta: item_id + timestamp
        label_data = f"ITEM:{item_id}|{datetime.utcnow().isoformat()}|{item.name}"
        
        qr = segno.make_micro(label_data, error='m')
        buf = BytesIO()
        qr.save(buf, kind='png', scale=5)
        buf.seek(0)
        
        return send_file(buf, mimetype='image/png', 
                        download_name=f'nfc_label_item_{item_id}.png')
    except Exception as e:
        logger.error(f"NFC QR generation error: {e}")
        return jsonify({'error': str(e)}), 500

@nfc_bp.route('/control', methods=['GET', 'POST'])
def nfc_control():
    """GET/POST /nfc/control - Panel de control de dispositivos NFC"""
    if not g.user or g.user.role != 'admin':
        return render_template('403.html'), 403
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'test_scan':
            item_id = request.form.get('item_id')
            scan_action = request.form.get('scan_action')  # return, restock
            
            try:
                item = Item.query.get_or_404(item_id)
                
                if scan_action == 'return':
                    rental = Transaction.query.filter(
                        Transaction.item_id == item_id,
                        Transaction.kind == 'rent',
                        Transaction.returned == False
                    ).first()
                    
                    if rental:
                        rental.returned = True
                        rental.actual_return_date = datetime.utcnow()
                        item.stock += rental.quantity
                        db.session.commit()
                        return jsonify({
                            'status': 'success',
                            'message': f'Item {item.name} returned',
                            'new_stock': item.stock
                        })
                    else:
                        return jsonify({
                            'status': 'error',
                            'message': 'No active rental found'
                        }), 400
                
                elif scan_action == 'restock':
                    quantity = int(request.form.get('quantity', 1))
                    item.stock += quantity
                    db.session.commit()
                    return jsonify({
                        'status': 'success',
                        'message': f'{quantity} units added to {item.name}',
                        'new_stock': item.stock
                    })
            except Exception as e:
                db.session.rollback()
                logger.error(f"NFC test scan error: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500
    
    # Obtener items para mostrar en el formulario
    items = Item.query.all()
    return render_template('nfc_control.html', items=items)

@nfc_bp.route('/stats', methods=['GET'])
def nfc_stats():
    """GET /nfc/stats - Estadísticas de dispositivo NFC"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    try:
        # Transacciones de return/restock en período
        transactions = Transaction.query.filter(
            Transaction.timestamp >= start_date,
            Transaction.kind.in_(['return', 'restock'])
        ).all()
        
        returns = len([t for t in transactions if t.kind == 'return'])
        restocks = len([t for t in transactions if t.kind == 'restock'])
        
        return jsonify({
            'status': 'success',
            'period_days': days,
            'total_scans': len(transactions),
            'returns': returns,
            'restocks': restocks,
            'last_scan': max([t.timestamp for t in transactions]).isoformat() if transactions else None,
            'device_status': 'online'
        })
    except Exception as e:
        logger.error(f"NFC stats error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@nfc_bp.route('/label/<int:item_id>')
def nfc_label(item_id):
    """GET /nfc/label/<item_id> - Obtener etiqueta completa para imprimir"""
    item = Item.query.get_or_404(item_id)
    
    return render_template('nfc_label.html', item=item)

@nfc_bp.route('/api/scan', methods=['POST'])
def api_nfc_scan():
    """POST /nfc/api/scan - Registrar escaneo NFC (versión sin API key)"""
    if not g.user or g.user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin required'}), 403
    
    try:
        data = request.get_json()
        item_id = data.get('item_id')
        action = data.get('action')  # return, restock
        qty = data.get('qty', 1)
        
        if not item_id or not action:
            return jsonify({'success': False, 'message': 'item_id and action required'}), 400
        
        item = Item.query.get_or_404(item_id)
        
        if action == 'return':
            rental = Transaction.query.filter(
                Transaction.item_id == item_id,
                Transaction.kind == 'rent',
                Transaction.returned == False
            ).first()
            
            if rental:
                rental.returned = True
                rental.return_date = datetime.utcnow()
                item.stock += rental.qty
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Devolución registrada',
                    'new_stock': item.stock
                })
            else:
                return jsonify({'success': False, 'message': 'No rental found'}), 400
        
        elif action == 'restock':
            item.stock += qty
            db.session.commit()
            return jsonify({
                'success': True,
                'message': f'{qty} unidades agregadas',
                'new_stock': item.stock
            })
        
        else:
            return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"NFC scan error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@nfc_bp.route('/api/batch', methods=['POST'])
def api_nfc_batch():
    """POST /nfc/api/batch - Procesar lote NFC (versión sin API key)"""
    if not g.user or g.user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin required'}), 403
    
    try:
        data = request.get_json()
        operations = data.get('operations', [])
        
        if not operations:
            return jsonify({'success': False, 'message': 'operations required'}), 400
        
        results = []
        
        for op in operations:
            item_id = op.get('item_id')
            action = op.get('action')
            qty = op.get('qty', 1)
            
            try:
                item = Item.query.get(item_id)
                if not item:
                    results.append({
                        'item_id': item_id,
                        'success': False,
                        'message': 'Item not found'
                    })
                    continue
                
                if action == 'return':
                    rental = Transaction.query.filter(
                        Transaction.item_id == item_id,
                        Transaction.kind == 'rent',
                        Transaction.returned == False
                    ).first()
                    
                    if rental:
                        old_stock = item.stock
                        rental.returned = True
                        rental.return_date = datetime.utcnow()
                        item.stock += rental.qty
                        results.append({
                            'item_id': item_id,
                            'item_name': item.name,
                            'success': True,
                            'old_stock': old_stock,
                            'new_stock': item.stock
                        })
                    else:
                        results.append({
                            'item_id': item_id,
                            'success': False,
                            'message': 'No rental found'
                        })
                
                elif action == 'restock':
                    old_stock = item.stock
                    item.stock += qty
                    results.append({
                        'item_id': item_id,
                        'item_name': item.name,
                        'success': True,
                        'old_stock': old_stock,
                        'new_stock': item.stock
                    })
            
            except Exception as e:
                results.append({
                    'item_id': item_id,
                    'success': False,
                    'message': str(e)
                })
        
        db.session.commit()
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"NFC batch error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@nfc_bp.route('/api/stats', methods=['GET'])
def api_nfc_stats():
    """GET /nfc/api/stats - Estadísticas NFC (versión sin API key)"""
    if not g.user or g.user.role != 'admin':
        return jsonify({'success': False, 'message': 'Admin required'}), 403
    
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        transactions = Transaction.query.filter(
            Transaction.timestamp >= start_date,
            Transaction.kind.in_(['return', 'restock'])
        ).all()
        
        total = len(transactions)
        returns = len([t for t in transactions if t.kind == 'return'])
        restocks = len([t for t in transactions if t.kind == 'restock'])
        
        # Top items escaneados
        from sqlalchemy import func
        top_items = db.session.query(
            Item.name,
            func.count(Transaction.id).label('scans')
        ).join(Transaction).filter(
            Transaction.timestamp >= start_date,
            Transaction.kind.in_(['return', 'restock'])
        ).group_by(Item.id).order_by(desc(func.count(Transaction.id))).limit(5).all()
        
        return jsonify({
            'success': True,
            'total_nfc_transactions': total,
            'returns': returns,
            'restocks': restocks,
            'top_items': [{'name': t[0], 'scans': t[1]} for t in top_items]
        })
    except Exception as e:
        logger.error(f"NFC stats error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
