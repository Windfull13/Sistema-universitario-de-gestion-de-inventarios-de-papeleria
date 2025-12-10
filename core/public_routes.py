"""
Public routes for item display and health checks
"""
import logging
from flask import Blueprint, render_template, request, g, url_for, send_file, redirect
from io import BytesIO

logger = logging.getLogger(__name__)

public_bp = Blueprint('public', __name__)


@public_bp.route('/health', methods=['GET', 'HEAD'])
def health():
    """Health check endpoint"""
    from flask import current_app
    db_available = getattr(current_app, 'db_available', False)
    
    if request.method == 'HEAD':
        return '', 200
    return {'status': 'healthy', 'db_available': db_available}, 200


@public_bp.route('/test', methods=['GET', 'HEAD'])
def test():
    """Test endpoint"""
    if request.method == 'HEAD':
        return '', 200
    return 'OK', 200


@public_bp.route('/', methods=['GET', 'HEAD'])
def index():
    """Home page"""
    from flask import current_app
    
    if request.method == 'HEAD':
        return '', 200
    
    try:
        db_available = getattr(current_app, 'db_available', False)
        
        # Redirect logged in users
        if g.user and db_available:
            if g.user.role == 'admin':
                try:
                    return redirect(url_for('admin.index'))
                except:
                    pass
            else:
                try:
                    return redirect(url_for('student.student'))
                except:
                    pass
        
        # Show home page
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in index: {e}")
        return render_template('index.html')


@public_bp.route('/item/<int:item_id>')
def item_detail(item_id):
    """Public item detail page"""
    from flask import current_app
    
    try:
        db_available = getattr(current_app, 'db_available', False)
        
        if not db_available:
            return render_template('404.html'), 404
        
        from models import Item
        item = Item.query.get_or_404(item_id)
        return render_template('item.html', item=item)
    except Exception as e:
        logger.error(f"Error in item_detail: {e}")
        return render_template('404.html'), 404


@public_bp.route('/api/item/<int:item_id>/image')
def generate_item_image(item_id):
    """Generate item placeholder image on-the-fly"""
    try:
        from models import Item
        from PIL import Image, ImageDraw
        from core.styles import get_category_color, TEXT_COLOR
        
        item = Item.query.get_or_404(item_id)
        
        rgb = get_category_color(item.category)
        
        img = Image.new('RGB', (400, 300), color=rgb)
        draw = ImageDraw.Draw(img)
        text = item.name[:40]
        bbox = draw.textbbox((0, 0), text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (400 - text_width) // 2
        y = (300 - text_height) // 2
        draw.text((x, y), text, fill=TEXT_COLOR)
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        response = send_file(buf, mimetype='image/png', download_name=f'item_{item_id}.png')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except ImportError as e:
        logger.error(f"Import error generating image for item {item_id}: {e}")
        return f"Error: PIL not available - {e}", 500
    except Exception as e:
        logger.error(f"Error generating image for item {item_id}: {e}", exc_info=True)
        return f"Error: {e}", 500
