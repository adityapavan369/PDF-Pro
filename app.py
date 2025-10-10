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
        # Only require CSRF for POST requests, not GET
        if request.method == 'POST':
            token = request.form.get('csrf_token')
            if not _validate_csrf_token(token):
                return jsonify({'error': 'CSRF token validation failed'}), 403
        return f(*args, **kwargs)
    return decorated_function

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin access required', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['GET', 'POST'])
@csrf_required
def convert():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                
                # Determine conversion type based on file extension
                file_ext = filename.rsplit('.', 1)[1].lower()
                
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
                    # Image to PDF conversion
                    output_filename = f"{filename.rsplit('.', 1)[0]}.pdf"
                    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
                    image_to_pdf(filepath, output_path)
                    
                elif file_ext in ['docx']:
                    # DOCX to PDF conversion
                    output_filename = f"{filename.rsplit('.', 1)[0]}.pdf"
                    output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
                    docx_to_pdf(filepath, output_path)
                    
                else:
                    return jsonify({'error': 'Unsupported file type'}), 400
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'message': 'File converted successfully',
                    'download_url': url_for('download', filename=output_filename)
                })
                
            except Exception as e:
                return jsonify({'error': f'Conversion failed: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    
    return render_template('convert.html')

@app.route('/edit', methods=['GET', 'POST'])
@csrf_required
def edit():
    if request.method == 'POST':
        # Handle PDF editing operations
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        operation = request.form.get('operation')
        
        if file.filename == '' or not validate_pdf(file):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            output_filename = f"edited_{filename}"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            if operation == 'rotate':
                angle = int(request.form.get('angle', 0))
                rotate_pdf(filepath, output_path, angle)
                
            elif operation == 'watermark':
                watermark_text = request.form.get('watermark_text', '')
                add_watermark(filepath, output_path, watermark_text)
                
            elif operation == 'extract':
                page_ranges = request.form.get('page_ranges', '')
                pages = parse_page_ranges(page_ranges)
                extract_pages(filepath, output_path, pages)
                
            elif operation == 'delete':
                page_ranges = request.form.get('page_ranges', '')
                pages = parse_page_ranges(page_ranges)
                delete_pages(filepath, output_path, pages)
                
            else:
                return jsonify({'error': 'Invalid operation'}), 400
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': 'PDF edited successfully',
                'download_url': url_for('download', filename=output_filename)
            })
            
        except Exception as e:
            return jsonify({'error': f'Edit operation failed: {str(e)}'}), 500
    
    return render_template('edit.html')

@app.route('/split', methods=['GET', 'POST'])
@csrf_required
def split():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        split_type = request.form.get('split_type')
        
        if file.filename == '' or not validate_pdf(file):
            return jsonify({'error': 'Invalid PDF file'}), 400
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            base_filename = filename.rsplit('.', 1)[0]
            
            if split_type == 'pages':
                pages_per_split = int(request.form.get('pages_per_split', 1))
                output_files = split_pdf_by_pages(filepath, Config.OUTPUT_FOLDER, base_filename, pages_per_split)
                
            elif split_type == 'range':
                page_ranges = request.form.get('page_ranges', '')
                ranges = parse_page_ranges(page_ranges)
                output_files = split_pdf_by_range(filepath, Config.OUTPUT_FOLDER, base_filename, ranges)
                
            elif split_type == 'single':
                output_files = split_pdf_into_single_pages(filepath, Config.OUTPUT_FOLDER, base_filename)
                
            else:
                return jsonify({'error': 'Invalid split type'}), 400
            
            # Clean up uploaded file
            os.remove(filepath)
            
            download_urls = [url_for('download', filename=os.path.basename(f)) for f in output_files]
            
            return jsonify({
                'success': True,
                'message': f'PDF split into {len(output_files)} files',
                'download_urls': download_urls
            })
            
        except Exception as e:
            return jsonify({'error': f'Split operation failed: {str(e)}'}), 500
    
    return render_template('split.html')

@app.route('/merge', methods=['GET', 'POST'])
@csrf_required
def merge():
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        merge_type = request.form.get('merge_type', 'merge')
        
        if not files or len(files) < 2:
            return jsonify({'error': 'At least 2 PDF files are required'}), 400
        
        try:
            filepaths = []
            for file in files:
                if file.filename == '' or not validate_pdf(file):
                    return jsonify({'error': f'Invalid PDF file: {file.filename}'}), 400
                
                filename = secure_filename(file.filename)
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                filepaths.append(filepath)
            
            output_filename = "merged_document.pdf"
            output_path = os.path.join(Config.OUTPUT_FOLDER, output_filename)
            
            if merge_type == 'merge':
                merge_pdfs(filepaths, output_path)
            elif merge_type == 'append':
                append_pdfs(filepaths, output_path)
            else:
                return jsonify({'error': 'Invalid merge type'}), 400
            
            # Clean up uploaded files
            for filepath in filepaths:
                os.remove(filepath)
            
            return jsonify({
                'success': True,
                'message': 'PDFs merged successfully',
                'download_url': url_for('download', filename=output_filename)
            })
            
        except Exception as e:
            return jsonify({'error': f'Merge operation failed: {str(e)}'}), 500
    
    return render_template('merge.html')

@app.route('/admin')
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_logs'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple hardcoded check (in production, use proper authentication)
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Logged in successfully', 'success')
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
