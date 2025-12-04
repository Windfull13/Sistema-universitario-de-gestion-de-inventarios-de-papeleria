"""Configuración centralizada de la aplicación"""
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    """Configuración por defecto"""
    # Database
    # En producción, usar PostgreSQL; en desarrollo, SQLite
    if os.environ.get('DATABASE_URL'):
        # Para Render y otros servicios en la nube
        DATABASE_URL = os.environ.get('DATABASE_URL')
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
        # Opciones optimizadas para PostgreSQL en Render (free tier)
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,             # Recicla cada 5 minutos
            'pool_size': 2,                  # Mínimo pool size para free tier
            'max_overflow': 0,               # Sin overflow
            'echo': False,
            'connect_args': {
                'connect_timeout': 5,
            }
        }
    else:
        # Desarrollo local
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "inventory.db")}'
        # Opciones para SQLite
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {'timeout': 30},
            'pool_pre_ping': True,
        }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Application URL (para QRs y URLs en emails)
    APP_URL = os.environ.get('APP_URL', 'http://localhost:5000')
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-for-demo')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # True en producción con HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_REFRESH_EACH_REQUEST = True
    
    # Upload files
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB
    
    # Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'Sistema de Inventario <no-reply@example.com>')
    
    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = "memory://"
    API_LIMIT = "100 per hour"
    ADMIN_API_LIMIT = "200 per hour"

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Configuración para testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Seleccionar configuración según el ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
