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
def _csrf_field():
    token = _generate_csrf_token()
    return Markup(f'<input type="hidden" name="csrf_token" value="{token}">')

app.jinja_env.globals['csrf_token'] = _csrf_field


# Admin auth helpers (basic HTTP auth)
def _check_admin_auth():
    # First check session
    if session.get('is_admin'):
        return True
    auth = request.headers.get('Authorization')
    if not auth or not auth.startswith('Basic '):
        return False
    try:
        cred = b64decode(auth.split(' ', 1)[1]).decode('utf-8')
        user, passwd = cred.split(':', 1)
        return user == app.config.get('ADMIN_USER') and passwd == app.config.get('ADMIN_PASS')
    except Exception:
        return False


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not _check_admin_auth():
            return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Admin Area"'})
        return f(*args, **kwargs)
    return decorated


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # CSRF validation
        if not _validate_csrf_token(request.form.get('csrf_token')):
            flash('Invalid CSRF token', 'error')
            return render_template('admin_login.html')

        user = request.form.get('user')
        pwd = request.form.get('pass')
        if user == app.config.get('ADMIN_USER') and pwd == app.config.get('ADMIN_PASS'):
            session['is_admin'] = True
            return redirect(url_for('admin_logs'))
        flash('Invalid credentials', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@app.route('/admin/logs')
@admin_required
def admin_logs():
    log_path = os.path.join(app.config['OUTPUT_FOLDER'], 'conversions.log')
    logs = []
    if os.path.exists(log_path):
        try:
            with open(log_path, 'r', encoding='utf-8') as lf:
                for line in lf.readlines()[-500:][::-1]:
                    parts = line.strip().split('\t')
                    if len(parts) >= 5:
                        timestamp, engine, inp, outp, duration = parts[:5]
                        logs.append({'timestamp': timestamp, 'engine': engine, 'input': inp, 'output': outp, 'duration': duration})
        except Exception:
            logs = []
    return render_template('admin_logs.html', logs=logs)


@app.route('/admin/download-logs')
@admin_required
def download_logs():
    log_path = os.path.join(app.config['OUTPUT_FOLDER'], 'conversions.log')
    if not os.path.exists(log_path):
        return jsonify({'error': 'No logs'}), 404
    return send_file(log_path, as_attachment=True, download_name='conversions.log')


@app.route('/admin/visual-compare', methods=['GET', 'POST'])
@admin_required
def admin_visual_compare():
    if request.method == 'POST':
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({'error': 'Two PDF files required'}), 400
        f1 = request.files['file1']
        f2 = request.files['file2']
        if f1.filename == '' or f2.filename == '':
            return jsonify({'error': 'Files not selected'}), 400
        # Save temporarily
        tmpdir = os.path.join(app.config['UPLOAD_FOLDER'], 'visual_tmp')
        os.makedirs(tmpdir, exist_ok=True)
        p1 = os.path.join(tmpdir, secure_filename(f1.filename))
        p2 = os.path.join(tmpdir, secure_filename(f2.filename))
        f1.save(p1)
        f2.save(p2)

        # Try to import visual libs (optional)
        try:
            import fitz  # PyMuPDF
            from PIL import Image, ImageChops
        except Exception:
            # PyMuPDF / Pillow not installed in this environment; inform admin
            return render_template('visual_compare.html', message='Server missing visual compare libraries (PyMuPDF/Pillow).'), 200

        # Render first pages for quick check
        try:
            doc1 = fitz.open(p1)
            doc2 = fitz.open(p2)
            pages = min(len(doc1), len(doc2))
            diffs = []
            out_dir = os.path.join(app.config['OUTPUT_FOLDER'], 'visual_diffs')
            os.makedirs(out_dir, exist_ok=True)
            for i in range(pages):
                pix1 = doc1.load_page(i).get_pixmap(dpi=150)
                pix2 = doc2.load_page(i).get_pixmap(dpi=150)
                im1 = Image.frombytes('RGB', [pix1.width, pix1.height], pix1.samples)
                im2 = Image.frombytes('RGB', [pix2.width, pix2.height], pix2.samples)
                # compute difference
                diff = ImageChops.difference(im1, im2)
                bbox = diff.getbbox()
                different = bbox is not None
                diffs.append({'page': i+1, 'different': different, 'diff_image': None})
                if different:
                    diff_path = os.path.join(out_dir, f'diff_page_{i+1}_{uuid.uuid4().hex[:8]}.png')
                    diff.save(diff_path)
                    diffs[-1]['diff_image'] = os.path.relpath(diff_path, app.config['OUTPUT_FOLDER'])
            # convert diff_image paths to URLs
            for d in diffs:
                if d.get('diff_image'):
                    d['diff_url'] = url_for('serve_visual_diff', filename=d['diff_image'])
            return render_template('visual_compare.html', diffs=diffs)
        except Exception as e:
            return render_template('visual_compare.html', message=f'Visual compare failed: {e}'), 200

    return render_template('visual_compare.html')



@app.route('/outputs/visual_diffs/<path:filename>')
@admin_required
def serve_visual_diff(filename):
    path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    if not os.path.exists(path):
        return jsonify({'error': 'Not found'}), 404
    return send_file(path, as_attachment=False)



@app.route('/admin/rerun', methods=['POST'])
def admin_rerun():
    # CSRF validation
    if not _validate_csrf_token(request.form.get('csrf_token')):
        return jsonify({'error': 'Invalid CSRF token'}), 400

    input_name = request.form.get('input')
    if not input_name:
        return jsonify({'error': 'No input specified'}), 400
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_name)
    if not os.path.exists(input_path):
        return jsonify({'error': 'Input not found in uploads'}), 404

    # Only support DOCX re-run for now
    if not input_name.lower().endswith('.docx'):
        return jsonify({'error': 'Rerun only supported for DOCX in this UI'}), 400

    # Generate output
    output_filename = f"rerun_{os.path.splitext(input_name)[0]}_{uuid.uuid4().hex[:8]}.pdf"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    try:
        start = datetime.utcnow()
        from utils.converter import docx_to_pdf
        docx_to_pdf(input_path, output_path)
        duration = (datetime.utcnow() - start).total_seconds()
        # read engine
        engine = 'unknown'
        try:
            with open(f"{output_path}.engine", 'r', encoding='utf-8') as ef:
                engine = ef.read().strip() or engine
        except Exception:
            pass
        _log_conversion(engine, input_name, output_filename, duration)
        return send_file_with_engine(output_path, download_name=output_filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def send_file_with_engine(path, **send_file_kwargs):
    """Send a file and, if an engine metadata file exists, include it as a response header.

    The engine file is expected at path + '.engine' and contains a short string
    identifying the converter used (e.g., 'soffice', 'docx2pdf', 'pillow', 'fallback').
    """
    response = send_file(path, **send_file_kwargs)
    try:
        engine_file = f"{path}.engine"
        if os.path.exists(engine_file):
            with open(engine_file, 'r', encoding='utf-8') as ef:
                engine = ef.read().strip()
            if engine:
                response.headers['X-Converter-Engine'] = engine
    except Exception:
        # don't fail on header attachment
        pass
    return response


def _log_conversion(engine: str, input_name: str, output_name: str, duration_sec: float):
    try:
        log_dir = app.config.get('OUTPUT_FOLDER')
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, 'conversions.log')
        with open(log_path, 'a', encoding='utf-8') as lf:
            lf.write(f"{datetime.utcnow().isoformat()}Z\t{engine}\t{input_name}\t{output_name}\t{duration_sec:.2f}s\n")
    except Exception:
        pass





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
            start_ts = datetime.utcnow()
            if file_ext in ['png', 'jpg', 'jpeg']:
                image_to_pdf(input_path, output_path)
            elif file_ext == 'docx':
                docx_to_pdf(input_path, output_path)
            else:
                return jsonify({'error': 'Unsupported conversion'}), 400
            duration = (datetime.utcnow() - start_ts).total_seconds()

            # Determine engine used from metadata file and log conversion
            engine = 'unknown'
            try:
                eng_file = f"{output_path}.engine"
                if os.path.exists(eng_file):
                    with open(eng_file, 'r', encoding='utf-8') as ef:
                        engine = ef.read().strip() or engine
            except Exception:
                pass
            _log_conversion(engine, filename, output_filename, duration)
            
            # Clean up input file
            os.remove(input_path)
            
            # return file with engine header when available
            return send_file_with_engine(output_path, download_name=output_filename)
        
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
            
            return send_file_with_engine(output_path, download_name=output_filename)
        
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
                return send_file_with_engine(output_files[0])
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
            
            return send_file_with_engine(output_path, download_name=output_filename)
        
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
        'external_api_enabled': api_client is not None,
        # indicate whether LibreOffice/soffice is available for high-fidelity conversions
        'soffice_available': shutil.which('soffice') is not None
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
