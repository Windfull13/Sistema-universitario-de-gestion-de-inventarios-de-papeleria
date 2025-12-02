"""Funciones de seguridad: hashing, 2FA, IP, URLs"""
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, current_app
import logging
import os

try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False

logger = logging.getLogger(__name__)

def get_client_ip():
    """Obtiene IP real del cliente (maneja proxies)"""
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        return request.environ.get('HTTP_X_FORWARDED_FOR').split(',')[0]
    return request.environ.get('REMOTE_ADDR')

def hash_password(password):
    """Hashea contraseña con PBKDF2:SHA256"""
    return generate_password_hash(password, method='pbkdf2:sha256')

def verify_password(password_hash, password):
    """Verifica contraseña hasheada"""
    return check_password_hash(password_hash, password)

def generate_2fa_secret():
    """Genera secreto TOTP para 2FA"""
    if not PYOTP_AVAILABLE:
        return None
    return pyotp.random_base32()

def verify_2fa_token(secret, token):
    """Verifica token TOTP"""
    if not PYOTP_AVAILABLE or not secret or not token:
        return False
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token)
    except Exception:
        return False

def get_2fa_qr_url(user_email, secret):
    """Genera URL de QR para 2FA"""
    if not PYOTP_AVAILABLE:
        return None
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(
        name=user_email,
        issuer_name='Sistema Inventario'
    )

def get_base_url():
    """Obtiene URL base de la aplicación (localhost en dev, Render en prod)"""
    # Usar variable de entorno APP_URL si está configurada
    app_url = current_app.config.get('APP_URL', '').rstrip('/')
    if app_url and app_url != 'http://localhost:5000':
        return app_url
    # Fallback: usar request.host_url
    return request.host_url.rstrip('/')

def get_item_url(item_id):
    """Genera URL completa a la página del producto
    Uso en QRs para que funcione tanto en localhost como en Render"""
    base_url = get_base_url()
    return f"{base_url}/item/{item_id}"
