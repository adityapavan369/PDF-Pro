"""PDF-Pro Flask Application"""
import os
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for, session
from markupsafe import Markup
from secrets import token_urlsafe
from werkzeug.utils import secure_filename
from config import Config
from utils.converter import image_to_pdf, docx_to_pdf, images_to_pdf
from utils.editor import rotate_pdf, add_watermark, extract_pages, delete_pages
from utils.splitter import split_pdf_by_pages, split_pdf_by_range, split_pdf_into_single_pages
from utils.merger import merge_pdfs, append_pdfs
from utils.api_integration import get_api_client
from utils.validators import allowed_file, validate_pdf, get_safe_filename, ensure_unique_filename
from pdf_editor import parse_page_ranges
import uuid
import shutil
from datetime import datetime
from functools import wraps
from base64 import b64decode

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)

# Lightweight CSRF protection for forms (avoids adding Flask-WTF which
# has compatibility issues with Flask 3.x in some environments).
def _generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = token_urlsafe(32)
    return session['_csrf_token']

def _validate_csrf_token(token: str) -> bool:
    if not token:
        return False
    return token == session.get('_csrf_token')

# Jinja helper to render a hidden CSRF field
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=_generate_csrf_token)

def csrf_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only validate CSRF for non-GET requests
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token')
            if not _validate_csrf_token(token):
                return jsonify({'error': 'CSRF token validation failed'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple admin check - in production, implement proper authentication
        if not session.get('is_admin'):
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/admin/logs')
@admin_required
def admin_logs():
    # Read and display logs
    log_file = os.path.join(Config.LOG_FOLDER, 'app.log')
    logs = []
    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            logs = f.readlines()[-100:]  # Get last 100 lines
    
    return render_template('admin_logs.html', logs=logs)

@app.route('/api/info')
def api_info():
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'environment': os.getenv('FLASK_ENV', 'production')
    }), 200

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(Config.OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(Config.LOG_FOLDER, exist_ok=True)
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
