"""
Main Flask application entry point
Simplified to only handle initialization, configuration, and blueprint registration
"""
import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, session, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

# Configuration
from config import config

# Database models and utilities
from models import db, User, ActiveSession, Transaction, Item
from utils.security import get_client_ip
from routes import register_blueprints

# Logging setup
logging.basicConfig(
    level=logging.WARNING,  # Solo WARNING y ERROR para reducir ruido
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)
# Reducir verbosity de librerías terceras
logging.getLogger('werkzeug').setLevel(logging.ERROR)
logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
logging.getLogger('apscheduler').setLevel(logging.ERROR)

# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config.get(config_name, config['development']))

# Initialize extensions
db.init_app(app)

# Configurar Mail solo si tenemos credenciales
MAIL_CONFIG = {
    'MAIL_SERVER': os.getenv('MAIL_SERVER'),
    'MAIL_PORT': os.getenv('MAIL_PORT'),
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
}

# Solo inicializar Mail si tenemos credenciales
if all(MAIL_CONFIG.values()):
    try:
        mail = Mail(app)
    except Exception as e:
        logger.warning(f"Mail initialization failed: {e}")
        mail = None
else:
    mail = None
# Limiter deshabilitado temporalmente para debugging
# limiter = Limiter(
#     app=app,
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"]
# )

# Initialize database automatically on startup
def init_database():
    """Initialize database tables - very defensive with logging"""
    try:
        with app.app_context():
            try:
                # Try to create all tables
                db.create_all()
                logger.info("Database tables created/verified successfully")
            except Exception as create_error:
                # Try to check if table exists
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(db.engine)
                    tables = inspector.get_table_names()
                    logger.info(f"Existing tables: {tables}")
                except:
                    pass
                logger.warning(f"Could not create tables: {create_error}")
            return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        # No lancemos excepción - la app debe iniciarse aunque la BD falle
        return False

# Ejecutar inicialización
try:
    db_initialized = init_database()
    logger.info(f"Database initialization result: {db_initialized}")
except Exception as e:
    logger.error(f"Unexpected error during init: {e}")
    db_initialized = False

# Session configuration for security
app.config.update(
    SESSION_COOKIE_SECURE=not app.debug,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

def init_db():
    """Initialize database - deprecated, kept for backward compatibility"""
    # La inicialización ahora se hace automáticamente en init_database()
    pass

@app.before_request
def before_request():
    """Load user from session before each request"""
    g.user = None
    
    # Ignorar completamente HEAD requests
    if request.method == 'HEAD':
        return
    
    # Si la BD no está inicializada, no procesar sesiones complejas
    if not db_initialized:
        return
    
    try:
        if 'user_id' in session:
            try:
                g.user = User.query.get(session['user_id'])
            except Exception as e:
                session.clear()
                return
            
            if g.user:
                session_token = session.get('session_token')
                
                if not session_token:
                    session.clear()
                    g.user = None
                    return
                
                try:
                    client_ip = get_client_ip()
                    active_session = ActiveSession.query.filter_by(
                        user_id=g.user.id,
                        session_token=session_token,
                        is_active=True
                    ).first()
                    
                    if not active_session:
                        session.clear()
                        g.user = None
                        return
                    
                    if not active_session.validate_session(g.user.id, session_token, client_ip):
                        session.clear()
                        g.user = None
                        return redirect(url_for('auth.login'))
                except Exception as e:
                    session.clear()
                    g.user = None
            else:
                session.clear()
    except Exception as e:
        g.user = None

@app.context_processor
def inject_globals():
    """Make common variables available to templates"""
    return {
        'current_user': g.user,
        'datetime': datetime
    }

@app.after_request
def after_request(response):
    """Add security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Manejo simple de errores 500"""
    try:
        return render_template('500.html'), 500
    except:
        return {'error': 'Internal server error'}, 500

@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(405)
def method_not_allowed(error):
    """Maneja solicitudes con métodos no permitidos (ej: HEAD)"""
    # Si es HEAD, tratarlo como GET
    if request.method == 'HEAD':
        # Redirigir a GET silenciosamente
        return '', 200
    logger.warning(f"Method not allowed: {request.method} {request.path}")
    return {'error': 'Method not allowed'}, 405

# Health check endpoint
@app.route('/health', methods=['GET', 'HEAD'])
def health_check():
    """Health check endpoint para Render y monitoreo"""
    # Para HEAD requests, retornar inmediatamente
    if request.method == 'HEAD':
        return '', 200
    
    return {
        'status': 'healthy',
        'app_initialized': db_initialized
    }, 200

# Simple test route
@app.route('/test')
def test():
    """Test route - returns plain text"""
    return 'OK', 200

# Simple public pages
@app.route('/', methods=['GET', 'HEAD'])
def index():
    """Home page - Ultra defensive"""
    # Para HEAD requests, retornar inmediatamente
    if request.method == 'HEAD':
        return '', 200
    
    try:
        # Primero, check si el usuario está logueado
        if 'user_id' in session and g.user:
            if g.user.role == 'admin':
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('student.student'))
        
        # Intentar cargar el template
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index(): {e}")
        # Fallback a HTML simple
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema de Inventarios</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                h1 { color: #333; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <h1>Sistema de Inventarios Universitario</h1>
            <p>Inicializando sistema...</p>
            <p><small>Recarga la página en unos segundos</small></p>
        </body>
        </html>
        ''', 200

@app.route('/item/<int:item_id>', methods=['GET', 'POST', 'HEAD'])
def view_item(item_id):
    """Ver detalles de un item y procesarcompras/rentas"""
    # Para HEAD requests, retornar inmediatamente
    if request.method == 'HEAD':
        return '', 200
    
    item = Item.query.get_or_404(item_id)
    
    if request.method == 'POST':
        if not g.user:
            return redirect(url_for('auth.login'))
        
        action = request.form.get('action')
        qty = int(request.form.get('qty', 1))
        
        if action == 'buy':
            # Procesar compra
            if item.stock < qty:
                return render_template('item.html', item=item, error='Stock insuficiente'), 400
            
            tx = Transaction(
                item_id=item.id,
                user_id=g.user.id,
                kind='buy',
                qty=qty,
                timestamp=datetime.utcnow()
            )
            item.stock -= qty
            db.session.add(tx)
            db.session.commit()
            
            return render_template('item.html', item=item, success='Compra realizada exitosamente')
        
        elif action == 'rent':
            # Procesar renta
            if not item.rentable:
                return render_template('item.html', item=item, error='Este item no es rentable'), 400
            
            if item.stock < qty:
                return render_template('item.html', item=item, error='Stock insuficiente'), 400
            
            days = int(request.form.get('days', 1))
            start_date = request.form.get('start_date')
            
            from datetime import datetime as dt
            start_date = dt.strptime(start_date, '%Y-%m-%d').date() if start_date else datetime.utcnow().date()
            due_date = start_date + timedelta(days=days)
            
            tx = Transaction(
                item_id=item.id,
                user_id=g.user.id,
                kind='rent',
                qty=qty,
                timestamp=datetime.utcnow(),
                rent_start_date=start_date,
                rent_due_date=due_date,
                rent_days=days,
                returned=False
            )
            item.stock -= qty
            db.session.add(tx)
            db.session.commit()
            
            return render_template('item.html', item=item, success=f'Renta realizada. Vencimiento: {due_date}')
    
    return render_template('item.html', item=item)



@app.route('/nfc-control', methods=['GET', 'POST'])
def nfc_control_alias():
    """Alias para /nfc/control - redirige sin cambiar el path visible"""
    from flask import request as flask_request
    from routes.nfc import nfc_control as nfc_control_func
    
    # Llamar directamente a la función sin redirigir
    return nfc_control_func()

# Register all blueprints
try:
    register_blueprints(app)
except Exception as e:
    logger.error(f"Error registering blueprints: {e}")

# Background scheduler for periodic tasks
def check_overdue_rentals():
    """Check for overdue rentals every hour"""
    try:
        with app.app_context():
            overdue = Transaction.query.filter(
                Transaction.kind == 'rent',
                Transaction.rent_due_date < datetime.utcnow().date(),
                Transaction.returned == False
            ).all()
            
            if overdue:
                logger.info(f"Found {len(overdue)} overdue rentals")
            
    except Exception as e:
        logger.error(f"Error checking overdue rentals: {e}")

def cleanup_expired_sessions():
    """Clean up expired sessions every hour"""
    try:
        with app.app_context():
            expired = ActiveSession.query.filter(
                ActiveSession.expires_at < datetime.utcnow()
            ).delete()
            db.session.commit()
            
            if expired:
                logger.info(f"Cleaned up {expired} expired sessions")
                
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Run Flask development server
    try:
        app.run(
            host='0.0.0.0',
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=app.debug
        )
    except Exception as e:
        logger.error(f"Failed to start app: {e}")
