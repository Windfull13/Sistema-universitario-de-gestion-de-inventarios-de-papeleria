"""
Request handling middleware and error handlers
"""
import logging
from flask import Flask, render_template, request, session, g
from datetime import timedelta

logger = logging.getLogger(__name__)


def register_middleware(app: Flask, db_available: bool):
    """Register all request middleware and error handlers"""
    
    @app.before_request
    def before_request():
        """Load user from session - ultra defensive"""
        g.user = None
        
        # Skip for HEAD requests
        if request.method == 'HEAD':
            return
        
        # Skip for health check endpoints
        if request.path in ['/test', '/health']:
            return
        
        # Only try DB access if DB is available
        if not db_available:
            return
        
        try:
            if 'user_id' in session:
                try:
                    from models import User
                    g.user = User.query.get(session.get('user_id'))
                except:
                    session.clear()
        except:
            pass
    
    @app.context_processor
    def inject_globals():
        """Template globals"""
        from datetime import datetime
        return {'current_user': g.user, 'datetime': datetime}
    
    @app.after_request
    def after_request(response):
        """Add security headers"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        try:
            return render_template('404.html'), 404
        except Exception as e:
            logger.error(f"Error rendering 404 template: {e}")
            return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        """Handle 500 errors - ultra defensive"""
        logger.error(f"500 Error: {error}", exc_info=True)
        try:
            return render_template('500.html'), 500
        except Exception as e:
            logger.error(f"Error rendering 500 template: {e}")
            return {'error': 'Internal server error', 'details': str(error)}, 500
    
    @app.errorhandler(403)
    def forbidden(error):
        try:
            return render_template('403.html'), 403
        except Exception as e:
            logger.error(f"Error rendering 403 template: {e}")
            return {'error': 'Forbidden'}, 403
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle HEAD requests"""
        if request.method == 'HEAD':
            return '', 200
        return {'error': 'Method not allowed'}, 405
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Catch-all for unhandled exceptions"""
        logger.error(f"Unhandled exception: {error}", exc_info=True)
        try:
            return render_template('500.html'), 500
        except:
            return {'error': 'Internal server error'}, 500


def configure_session(app: Flask):
    """Configure session settings"""
    app.config.update(
        SESSION_COOKIE_SECURE=not app.debug,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
    )
