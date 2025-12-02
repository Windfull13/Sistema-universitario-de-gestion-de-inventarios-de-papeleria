"""Modelos de base de datos"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import uuid
import io
import csv

db = SQLAlchemy()

class User(db.Model):
    """Modelo de usuario con campos de seguridad"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin o student
    
    # Security fields
    two_fa_enabled = db.Column(db.Boolean, default=False)
    two_fa_secret = db.Column(db.String(32), nullable=True)
    last_login_ip = db.Column(db.String(45), nullable=True)
    last_login_time = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    api_keys = db.relationship('ApiKey', backref='user', lazy=True, cascade='all, delete-orphan')
    login_attempts = db.relationship('LoginAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    active_sessions = db.relationship('ActiveSession', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user_obj', lazy=True, cascade='all, delete-orphan')


class LoginAttempt(db.Model):
    """Registra intentos de login para detección de ataques"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    username = db.Column(db.String(80), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    success = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_agent = db.Column(db.String(500), nullable=True)
    
    @classmethod
    def check_rate_limit(cls, ip_address, minutes=15, max_attempts=5):
        """Verifica si una IP excedió límite de intentos fallidos"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        failed_attempts = cls.query.filter(
            cls.ip_address == ip_address,
            cls.success == False,
            cls.timestamp >= cutoff_time
        ).count()
        return failed_attempts >= max_attempts
    
    @classmethod
    def log_attempt(cls, username, ip_address, success, user_agent=None, user_id=None):
        """Registra un intento de login"""
        attempt = cls(
            username=username,
            ip_address=ip_address,
            success=success,
            user_agent=user_agent,
            user_id=user_id
        )
        db.session.add(attempt)
        db.session.commit()


class ActiveSession(db.Model):
    """Mantiene registro de sesiones activas"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(128), unique=True, nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    is_active = db.Column(db.Boolean, default=True)
    
    @classmethod
    def create_session(cls, user_id, ip_address, user_agent=None):
        """Crea una nueva sesión activa"""
        session_token = str(uuid.uuid4())
        new_session = cls(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(new_session)
        db.session.commit()
        return session_token
    
    @classmethod
    def validate_session(cls, user_id, session_token, current_ip):
        """Valida sesión y verifica cambios de IP"""
        session = cls.query.filter_by(
            user_id=user_id,
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session:
            return False
        
        ip_changed = session.ip_address != current_ip
        session.last_activity = datetime.utcnow()
        db.session.commit()
        
        return not ip_changed  # Return True if IP is OK, False if changed


class ApiKey(db.Model):
    """API Keys para acceso programático"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)


class Supplier(db.Model):
    """Proveedores de productos"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    contact = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    city = db.Column(db.String(80), nullable=True)
    
    # Campos de desempeño (auto-calculados)
    avg_delivery_days = db.Column(db.Float, default=0)
    last_delivery_date = db.Column(db.DateTime, nullable=True)
    total_orders = db.Column(db.Integer, default=0)
    on_time_deliveries = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('Item', backref='supplier', lazy=True)
    purchase_orders = db.relationship('PurchaseOrder', backref='supplier', lazy=True, cascade='all, delete-orphan')


class PurchaseOrder(db.Model):
    """Órdenes de compra a proveedores"""
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_delivery_date = db.Column(db.DateTime, nullable=True)
    actual_delivery_date = db.Column(db.DateTime, nullable=True)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, default=0)
    
    status = db.Column(db.String(20), default='pending')  # pending, delivered, cancelled, delayed
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Item', backref='purchase_orders', lazy=True)
    
    def is_overdue(self):
        """Verifica si la orden está retrasada"""
        if self.status != 'pending' or not self.expected_delivery_date:
            return False
        return datetime.utcnow() > self.expected_delivery_date


class Item(db.Model):
    """Productos del inventario"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(80), nullable=True)
    price = db.Column(db.Float, default=0.0)
    stock = db.Column(db.Integer, default=0)
    total_stock = db.Column(db.Integer)
    rentable = db.Column(db.Boolean, default=False)
    image_filename = db.Column(db.String(255), nullable=True)
    
    # Campo de proveedor principal
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    
    # Métricas de rotación
    rotation_score = db.Column(db.Float, default=0)  # 0-100 (qué tan rápido se vende)
    last_sale_date = db.Column(db.DateTime, nullable=True)
    sales_velocity = db.Column(db.Float, default=0)  # items/día
    
    transactions = db.relationship('Transaction', backref='item', lazy=True, cascade='all, delete-orphan')


class Transaction(db.Model):
    """Registro de compras, rentas y devoluciones"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    kind = db.Column(db.String(10))  # buy | rent | return | restock
    qty = db.Column(db.Integer, default=1)
    rent_days = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    rent_start_date = db.Column(db.Date, nullable=True)
    rent_due_date = db.Column(db.Date, nullable=True)
    returned = db.Column(db.Boolean, default=False)
    return_date = db.Column(db.DateTime, nullable=True)
    
    # Extensiones de renta
    extension_requested = db.Column(db.Boolean, default=False)
    extension_days = db.Column(db.Integer, nullable=True)
    extension_approved = db.Column(db.Boolean, default=False)
    extension_approved_at = db.Column(db.DateTime, nullable=True)

    @classmethod
    def search(cls, page=1, per_page=10, kind=None, returned=None, overdue=None):
        """Buscar transacciones con filtros"""
        query = cls.query.join(Item).order_by(cls.timestamp.desc())

        if kind:
            query = query.filter(cls.kind == kind)
        if returned is not None:
            query = query.filter(cls.returned == returned)
        if overdue:
            today = datetime.utcnow().date()
            query = query.filter(
                cls.kind == 'rent',
                cls.returned == False,
                cls.rent_due_date < today
            )

        return query.paginate(page=page, per_page=per_page)

    @classmethod
    def to_csv(cls, transactions):
        """Exportar transacciones a CSV"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Item', 'Tipo', 'Cantidad', 'Días', 'Fecha', 'Inicio', 'Vencimiento', 'Devuelto'])
        for tx in transactions:
            writer.writerow([
                tx.id,
                tx.item.name if tx.item else '',
                tx.kind,
                tx.qty,
                tx.rent_days or '',
                tx.timestamp.strftime('%Y-%m-%d %H:%M:%S') if tx.timestamp else '',
                tx.rent_start_date.strftime('%Y-%m-%d') if tx.rent_start_date else '',
                tx.rent_due_date.strftime('%Y-%m-%d') if tx.rent_due_date else '',
                'Sí' if tx.returned else 'No'
            ])
        return output.getvalue()
