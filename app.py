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

def csrf_protect(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not _validate_csrf_token(token):
                flash('Invalid CSRF token', 'error')
                return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

app.jinja_env.globals['csrf_token'] = _generate_csrf_token

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(csrf_token=_generate_csrf_token())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
@csrf_protect
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filename = ensure_unique_filename(Config.UPLOAD_FOLDER, filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        conversion_type = request.form.get('conversion_type')
        output_filename = None
        
        if conversion_type == 'image_to_pdf':
            output_filename = image_to_pdf(filepath, Config.OUTPUT_FOLDER)
        elif conversion_type == 'docx_to_pdf':
            output_filename = docx_to_pdf(filepath, Config.OUTPUT_FOLDER)
        else:
            return jsonify({'error': 'Invalid conversion type'}), 400
        
        if output_filename:
            return jsonify({
                'success': True,
                'message': 'File converted successfully',
                'download_url': url_for('download', filename=output_filename)
            })
        else:
            return jsonify({'error': 'Conversion failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/merge', methods=['POST'])
@csrf_protect
def merge():
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify({'error': 'At least 2 files required for merging'}), 400
    
    temp_files = []
    try:
        for file in files:
            if file.filename == '':
                continue
            if not allowed_file(file.filename) or not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'All files must be PDFs'}), 400
            
            filename = secure_filename(file.filename)
            filename = ensure_unique_filename(Config.UPLOAD_FOLDER, filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            temp_files.append(filepath)
        
        output_filename = merge_pdfs(temp_files, Config.OUTPUT_FOLDER)
        
        if output_filename:
            return jsonify({
                'success': True,
                'message': 'PDFs merged successfully',
                'download_url': url_for('download', filename=output_filename)
            })
        else:
            return jsonify({'error': 'Merge failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        for filepath in temp_files:
            if os.path.exists(filepath):
                os.remove(filepath)

@app.route('/split', methods=['POST'])
@csrf_protect
def split():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid PDF file'}), 400
    
    filename = secure_filename(file.filename)
    filename = ensure_unique_filename(Config.UPLOAD_FOLDER, filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        split_type = request.form.get('split_type')
        
        if split_type == 'single':
            output_files = split_pdf_into_single_pages(filepath, Config.OUTPUT_FOLDER)
        elif split_type == 'range':
            page_range = request.form.get('page_range', '')
            output_files = split_pdf_by_range(filepath, page_range, Config.OUTPUT_FOLDER)
        else:
            return jsonify({'error': 'Invalid split type'}), 400
        
        if output_files:
            return jsonify({
                'success': True,
                'message': 'PDF split successfully',
                'files': [url_for('download', filename=f) for f in output_files]
            })
        else:
            return jsonify({'error': 'Split failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/edit', methods=['POST'])
@csrf_protect
def edit():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Invalid PDF file'}), 400
    
    filename = secure_filename(file.filename)
    filename = ensure_unique_filename(Config.UPLOAD_FOLDER, filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    try:
        edit_type = request.form.get('edit_type')
        output_filename = None
        
        if edit_type == 'rotate':
            angle = int(request.form.get('angle', 90))
            output_filename = rotate_pdf(filepath, angle, Config.OUTPUT_FOLDER)
        elif edit_type == 'watermark':
            watermark_text = request.form.get('watermark_text', 'CONFIDENTIAL')
            output_filename = add_watermark(filepath, watermark_text, Config.OUTPUT_FOLDER)
        elif edit_type == 'extract':
            page_range = request.form.get('page_range', '')
            output_filename = extract_pages(filepath, page_range, Config.OUTPUT_FOLDER)
        elif edit_type == 'delete':
            page_range = request.form.get('page_range', '')
            output_filename = delete_pages(filepath, page_range, Config.OUTPUT_FOLDER)
        else:
            return jsonify({'error': 'Invalid edit type'}), 400
        
        if output_filename:
            return jsonify({
                'success': True,
                'message': 'PDF edited successfully',
                'download_url': url_for('download', filename=output_filename)
            })
        else:
            return jsonify({'error': 'Edit failed'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_logs'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
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

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join(Config.OUTPUT_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/info')
def api_info():
    return jsonify({'status': 'online'}), 200

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
