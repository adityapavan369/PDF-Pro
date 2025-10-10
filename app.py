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
        token = request.form.get('csrf_token')
        if not _validate_csrf_token(token):
            return jsonify({'error': 'CSRF token validation failed'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Admin authentication decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if request.method == 'POST':
        # Handle login logic here (e.g., validate credentials)
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Placeholder for actual authentication
        # In a real application, verify credentials against a database
        if username and password:
            session['user_logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')

@app.route('/convert', methods=['GET', 'POST'])
@csrf_required
def convert():
    if request.method == 'POST':
        conversion_type = request.form.get('conversion_type')
        files = request.files.getlist('files')
        
        if not files:
            return jsonify({'error': 'No files provided'}), 400
        
        output_files = []
        
        try:
            for file in files:
                if not file or not allowed_file(file.filename, ['png', 'jpg', 'jpeg', 'docx']):
                    continue
                    
                filename = secure_filename(file.filename)
                input_path = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(input_path)
                
                # Generate output filename
                output_filename = os.path.splitext(filename)[0] + '.pdf'
                output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
                
                # Perform conversion based on file type
                if conversion_type == 'image_to_pdf':
                    image_to_pdf(input_path, output_path)
                elif conversion_type == 'docx_to_pdf':
                    docx_to_pdf(input_path, output_path)
                
                output_files.append(output_filename)
            
            return jsonify({'files': output_files}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('convert.html')

@app.route('/merge', methods=['GET', 'POST'])
@csrf_required
def merge():
    if request.method == 'POST':
        files = request.files.getlist('files')
        
        if len(files) < 2:
            return jsonify({'error': 'At least 2 PDFs required for merging'}), 400
        
        try:
            pdf_paths = []
            for file in files:
                if not file or not allowed_file(file.filename, ['pdf']):
                    continue
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                pdf_paths.append(filepath)
            
            output_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            merge_pdfs(pdf_paths, output_path)
            
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('merge.html')

@app.route('/split', methods=['GET', 'POST'])
@csrf_required
def split():
    if request.method == 'POST':
        file = request.files.get('file')
        split_type = request.form.get('split_type')
        
        if not file or not allowed_file(file.filename, ['pdf']):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(input_path)
            
            output_files = []
            
            if split_type == 'single':
                # Split into single pages
                output_files = split_pdf_into_single_pages(input_path, Config.OUTPUT_FOLDER)
            elif split_type == 'pages':
                # Split by page numbers (expects comma-separated list)
                pages = request.form.get('pages', '')
                page_list = [int(p.strip()) for p in pages.split(',') if p.strip().isdigit()]
                output_files = split_pdf_by_pages(input_path, page_list, Config.OUTPUT_FOLDER)
            elif split_type == 'custom':
                # Split by custom ranges using parse_page_ranges
                custom_ranges = request.form.get('custom_ranges', '')
                
                if not custom_ranges:
                    return jsonify({'error': 'Custom ranges not provided'}), 400
                
                # Parse the custom ranges
                parsed_ranges = parse_page_ranges(custom_ranges)
                
                if parsed_ranges is None:
                    return jsonify({'error': 'Invalid page range format. Use format like "1-3,5,7-9"'}), 400
                
                # Split using the parsed ranges
                output_files = []
                for i, (start, end) in enumerate(parsed_ranges):
                    output_filename = f"{os.path.splitext(filename)[0]}_range_{i+1}.pdf"
                    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
                    # Use split_pdf_by_range to extract the pages
                    split_pdf_by_range(input_path, start, end, output_path)
                    output_files.append(output_filename)
            else:
                return jsonify({'error': 'Invalid split type'}), 400
            
            return jsonify({'files': output_files}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('split.html')

@app.route('/edit', methods=['GET', 'POST'])
@csrf_required
def edit():
    if request.method == 'POST':
        file = request.files.get('file')
        edit_type = request.form.get('edit_type')
        
        if not file or not allowed_file(file.filename, ['pdf']):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        try:
            filename = secure_filename(file.filename)
            input_path = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(input_path)
            
            output_filename = f"edited_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            if edit_type == 'rotate':
                angle = int(request.form.get('angle', 90))
                page_num = int(request.form.get('page_num', 0))
                rotate_pdf(input_path, output_path, page_num, angle)
            elif edit_type == 'watermark':
                watermark_text = request.form.get('watermark_text', 'WATERMARK')
                add_watermark(input_path, output_path, watermark_text)
            elif edit_type == 'extract':
                pages = request.form.get('pages', '')
                page_list = [int(p.strip()) for p in pages.split(',') if p.strip().isdigit()]
                extract_pages(input_path, output_path, page_list)
            elif edit_type == 'delete':
                pages = request.form.get('pages', '')
                page_list = [int(p.strip()) for p in pages.split(',') if p.strip().isdigit()]
                delete_pages(input_path, output_path, page_list)
            else:
                return jsonify({'error': 'Invalid edit type'}), 400
            
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('edit.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check admin credentials (in production, use secure storage)
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
    """API health check and information endpoint"""
    return jsonify({
        'status': 'online',
        'version': Config.VERSION,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'environment': Config.ENVIRONMENT
    }), 200

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
