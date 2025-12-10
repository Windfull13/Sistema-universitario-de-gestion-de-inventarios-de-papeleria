"""Rutas de autenticación: login, register, logout, 2FA"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import User, LoginAttempt, ActiveSession, db
from utils.security import hash_password, verify_password, get_client_ip, get_2fa_qr_url, verify_2fa_token, generate_2fa_secret
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

# ============ HELPER FUNCTIONS (Funciones auxiliares sin duplicación) ============

def _validate_login(identifier, password, identifier_field='username'):
    """Valida credenciales de usuario. identifier_field: 'username' o 'email'"""
    user = User.query.filter(getattr(User, identifier_field) == identifier).first()
    return user if user and verify_password(user.password_hash, password) else None

def _create_session_for_user(user, client_ip, user_agent):
    """Crea sesión y activa token para usuario"""
    session['user_id'] = user.id
    session['_session_created_at'] = datetime.utcnow().timestamp()
    user.last_login_ip = client_ip
    user.last_login_time = datetime.utcnow()
    
    session_token = ActiveSession.create_session(user.id, client_ip, user_agent)
    session['session_token'] = session_token
    db.session.commit()
    return session_token

def _validate_registration(username=None, email=None, password=None, password_confirm=None):
    """Valida datos de registro. Retorna (es_válido, mensaje_error)"""
    if not password or not password_confirm:
        return False, 'Contraseña requerida'
    
    if len(password) < 6:
        return False, 'Contraseña debe tener al menos 6 caracteres'
    
    if password != password_confirm:
        return False, 'Las contraseñas no coinciden'
    
    if username and User.query.filter_by(username=username).first():
        return False, 'Usuario ya existe'
    
    if email and User.query.filter_by(email=email).first():
        return False, 'Correo ya registrado'
    
    return True, None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login admin con rate limiting, detección de IP y 2FA"""
    if g.user:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        totp_token = request.form.get('totp_token', '').strip()
        
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        # Rate limiting
        if LoginAttempt.check_rate_limit(client_ip):
            flash('Demasiados intentos. Intenta nuevamente en 15 minutos.', 'danger')
            return render_template('login.html')
        
        if not username or not password:
            flash('Usuario y contraseña requeridos', 'danger')
            return render_template('login.html')

        user = _validate_login(username, password, 'username')
        
        if not user:
            LoginAttempt.log_attempt(username, client_ip, False, user_agent)
            logger.warning(f"Failed login for {username} from {client_ip}")
            flash('Usuario o contraseña incorrectos', 'danger')
            return render_template('login.html', require_2fa=False)
        
        # Verificar 2FA si está habilitado
        if user.two_fa_enabled:
            if not totp_token or not verify_2fa_token(user.two_fa_secret, totp_token):
                flash('Código 2FA incorrecto', 'danger')
                return render_template('login.html', username=username, require_2fa=True, password=password)
        
        # Login exitoso
        _create_session_for_user(user, client_ip, user_agent)
        LoginAttempt.log_attempt(username, client_ip, True, user_agent, user.id)
        
        logger.info(f"Successful login for {username} from {client_ip}")
        flash('Sesión iniciada correctamente', 'success')
        
        return redirect(request.args.get('next', url_for('public.index')))
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de administrador"""
    if g.user:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        
        if not username:
            flash('Usuario requerido', 'danger')
            return render_template('register.html')
        
        is_valid, error_msg = _validate_registration(username=username, password=password, password_confirm=password_confirm)
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('register.html')
        
        try:
            new_user = User(
                username=username,
                password_hash=hash_password(password),
                role='admin'
            )
            db.session.add(new_user)
            db.session.commit()
            
            client_ip = get_client_ip()
            user_agent = request.headers.get('User-Agent', '')[:500]
            _create_session_for_user(new_user, client_ip, user_agent)
            
            flash('Cuenta creada exitosamente', 'success')
            return redirect(url_for('public.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register.html')

@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    """Login para estudiantes"""
    if g.user:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        client_ip = get_client_ip()
        user_agent = request.headers.get('User-Agent', '')[:500]
        
        if LoginAttempt.check_rate_limit(client_ip):
            flash('Demasiados intentos. Intenta nuevamente en 15 minutos.', 'danger')
            return render_template('student_login.html')
        
        if not email or not password:
            flash('Correo y contraseña requeridos', 'danger')
            return render_template('student_login.html')

        user = _validate_login(email, password, 'email')
        
        if not user:
            LoginAttempt.log_attempt(email, client_ip, False, user_agent)
            flash('Correo o contraseña incorrectos', 'danger')
            return render_template('student_login.html')
        
        # Login exitoso
        _create_session_for_user(user, client_ip, user_agent)
        LoginAttempt.log_attempt(email, client_ip, True, user_agent, user.id)
        
        logger.info(f"Student login: {email} from {client_ip}")
        flash('Sesión iniciada correctamente', 'success')
        
        return redirect(request.args.get('next', url_for('public.index')))
    
    return render_template('student_login.html')

@auth_bp.route('/register_student', methods=['GET', 'POST'])
def register_student():
    """Registro de estudiante"""
    if g.user:
        return redirect(url_for('public.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        
        if not email:
            flash('Correo requerido', 'danger')
            return render_template('register_student.html')
        
        is_valid, error_msg = _validate_registration(email=email, password=password, password_confirm=password_confirm)
        if not is_valid:
            flash(error_msg, 'danger')
            return render_template('register_student.html')
        
        try:
            username = email.split('@')[0] + '_' + str(uuid.uuid4())[:8]
            
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                role='student'
            )
            db.session.add(new_user)
            db.session.commit()
            
            client_ip = get_client_ip()
            user_agent = request.headers.get('User-Agent', '')[:500]
            _create_session_for_user(new_user, client_ip, user_agent)
            
            flash('Cuenta creada exitosamente', 'success')
            return redirect(url_for('public.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('register_student.html')


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión"""
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/setup-2fa', methods=['GET', 'POST'])
def setup_2fa():
    """Configurar/deshabilitar 2FA"""
    if not g.user:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'enable':
            secret = generate_2fa_secret()
            session['2fa_temp_secret'] = secret
            qr_url = get_2fa_qr_url(g.user.email or g.user.username, secret)
            return render_template('setup_2fa.html', step=2, qr_url=qr_url, secret=secret)
        
        elif action == 'verify':
            token = request.form.get('token', '').strip()
            secret = session.get('2fa_temp_secret')
            
            if not secret or not verify_2fa_token(secret, token):
                flash('Código incorrecto', 'danger')
                return render_template('setup_2fa.html', step=1)
            
            g.user.two_fa_secret = secret
            g.user.two_fa_enabled = True
            db.session.commit()
            session.pop('2fa_temp_secret', None)
            
            flash('2FA habilitado correctamente', 'success')
            return redirect(url_for('public.index'))
        
        elif action == 'disable':
            password = request.form.get('password', '').strip()
            if not verify_password(g.user.password_hash, password):
                flash('Contraseña incorrecta', 'danger')
                return render_template('setup_2fa.html', step=1)
            
            g.user.two_fa_enabled = False
            g.user.two_fa_secret = None
            db.session.commit()
            flash('2FA deshabilitado', 'info')
            return redirect(url_for('public.index'))
    
    return render_template('setup_2fa.html', step=1)
