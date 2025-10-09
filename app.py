"""PDF-Pro Flask Application"""
import os
from flask import Flask, render_template, request, send_file, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from config import Config
from utils.converter import image_to_pdf, docx_to_pdf, images_to_pdf
from utils.editor import rotate_pdf, add_watermark, extract_pages, delete_pages
from utils.splitter import split_pdf_by_pages, split_pdf_by_range, split_pdf_into_single_pages
from utils.merger import merge_pdfs, append_pdfs
from utils.api_integration import get_api_client
from utils.validators import allowed_file, validate_pdf, get_safe_filename, ensure_unique_filename
import uuid
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/convert', methods=['GET', 'POST'])
def convert():
    """Convert files to PDF"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Save uploaded file
            filename = get_safe_filename(file.filename)
            filename = ensure_unique_filename(app.config['UPLOAD_FOLDER'], filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Generate output filename
            output_filename = f"{os.path.splitext(filename)[0]}_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Convert based on file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            
            if file_ext in ['png', 'jpg', 'jpeg']:
                image_to_pdf(input_path, output_path)
            elif file_ext == 'docx':
                docx_to_pdf(input_path, output_path)
            else:
                return jsonify({'error': 'Unsupported conversion'}), 400
            
            # Clean up input file
            os.remove(input_path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('convert.html')


@app.route('/merge', methods=['GET', 'POST'])
def merge():
    """Merge multiple PDFs"""
    if request.method == 'POST':
        try:
            if 'files' not in request.files:
                return jsonify({'error': 'No files provided'}), 400
            
            files = request.files.getlist('files')
            if len(files) < 2:
                return jsonify({'error': 'At least 2 files required'}), 400
            
            # Save uploaded files
            input_paths = []
            for file in files:
                if file.filename == '':
                    continue
                
                if not allowed_file(file.filename, {'pdf'}):
                    return jsonify({'error': f'Invalid file: {file.filename}'}), 400
                
                filename = get_safe_filename(file.filename)
                filename = ensure_unique_filename(app.config['UPLOAD_FOLDER'], filename)
                input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(input_path)
                
                # Validate PDF
                if not validate_pdf(input_path):
                    os.remove(input_path)
                    return jsonify({'error': f'Invalid PDF: {file.filename}'}), 400
                
                input_paths.append(input_path)
            
            if len(input_paths) < 2:
                return jsonify({'error': 'At least 2 valid PDFs required'}), 400
            
            # Generate output filename
            output_filename = f"merged_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Merge PDFs
            merge_pdfs(input_paths, output_path)
            
            # Clean up input files
            for path in input_paths:
                os.remove(path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('merge.html')


@app.route('/split', methods=['GET', 'POST'])
def split():
    """Split PDF into multiple files"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, {'pdf'}):
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Save uploaded file
            filename = get_safe_filename(file.filename)
            filename = ensure_unique_filename(app.config['UPLOAD_FOLDER'], filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Validate PDF
            if not validate_pdf(input_path):
                os.remove(input_path)
                return jsonify({'error': 'Invalid PDF file'}), 400
            
            # Get split options
            split_type = request.form.get('split_type', 'pages')
            
            # Create output directory
            output_dir = os.path.join(app.config['OUTPUT_FOLDER'], f"split_{uuid.uuid4().hex[:8]}")
            os.makedirs(output_dir, exist_ok=True)
            
            # Split based on type
            if split_type == 'single':
                output_files = split_pdf_into_single_pages(input_path, output_dir)
            else:
                pages_per_file = int(request.form.get('pages_per_file', 1))
                output_files = split_pdf_by_pages(input_path, output_dir, pages_per_file)
            
            # Clean up input file
            os.remove(input_path)
            
            # For simplicity, return the first split file
            # In production, you'd want to zip and return all files
            if output_files:
                return send_file(output_files[0], as_attachment=True)
            else:
                return jsonify({'error': 'No files generated'}), 500
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('split.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    """Edit PDF (rotate, watermark, etc.)"""
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not allowed_file(file.filename, {'pdf'}):
                return jsonify({'error': 'Invalid file type'}), 400
            
            # Save uploaded file
            filename = get_safe_filename(file.filename)
            filename = ensure_unique_filename(app.config['UPLOAD_FOLDER'], filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Validate PDF
            if not validate_pdf(input_path):
                os.remove(input_path)
                return jsonify({'error': 'Invalid PDF file'}), 400
            
            # Get edit operation
            operation = request.form.get('operation', 'rotate')
            
            # Generate output filename
            output_filename = f"{operation}_{uuid.uuid4().hex[:8]}.pdf"
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            
            # Perform operation
            if operation == 'rotate':
                rotation = int(request.form.get('rotation', 90))
                rotate_pdf(input_path, output_path, rotation)
            elif operation == 'watermark':
                watermark_text = request.form.get('watermark_text', 'CONFIDENTIAL')
                add_watermark(input_path, output_path, watermark_text)
            else:
                return jsonify({'error': 'Invalid operation'}), 400
            
            # Clean up input file
            os.remove(input_path)
            
            return send_file(output_path, as_attachment=True, download_name=output_filename)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('edit.html')


@app.route('/api/info')
def api_info():
    """API information endpoint"""
    api_client = get_api_client()
    return jsonify({
        'status': 'online',
        'features': [
            'convert',
            'merge',
            'split',
            'edit'
        ],
        'external_api_enabled': api_client is not None
    })


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
