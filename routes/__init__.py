"""Blueprint registration and initialization"""
from .auth import auth_bp
from .admin import admin_bp
from .student import student_bp
from .api import api_bp
from .nfc import nfc_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(nfc_bp)

__all__ = [
    'auth_bp',
    'admin_bp', 
    'student_bp',
    'api_bp',
    'nfc_bp',
    'register_blueprints'
]
