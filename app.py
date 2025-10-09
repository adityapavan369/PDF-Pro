from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
import pypdf
import fitz  # PyMuPDF
from docx import Document
from openpyxl import Workbook
from PIL import Image
import io
import tempfile
from pdf_api import pdf_api

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Register PDF editing API blueprint
app.register_blueprint(pdf_api, url_prefix='/api/pdf')

# Configuration
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx', 'doc', 'xlsx', 'pptx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload and converted directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_text_to_pdf(text_file_path, output_path):
    """Convert text file to PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        with open(text_file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Simple text to PDF conversion
        lines = text.split('\n')
        y = height - 50
        
        for line in lines:
            if y < 50:  # Start new page
                c.showPage()
                y = height - 50
            c.drawString(50, y, line[:80])  # Limit line length
            y -= 20
        
        c.save()
        return True
    except Exception as e:
        print(f"Error converting text to PDF: {e}")
        return False

def convert_image_to_pdf(image_path, output_path):
    """Convert image to PDF"""
    try:
        image = Image.open(image_path)
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(output_path, 'PDF')
        return True
    except Exception as e:
        print(f"Error converting image to PDF: {e}")
        return False

def convert_docx_to_pdf(docx_path, output_path):
    """Convert DOCX to PDF using advanced optimization for single-page output when possible"""
    try:
        # Import the advanced converter
        from advanced_docx_converter import convert_docx_to_pdf_advanced
        
        # Use the advanced conversion method
        success = convert_docx_to_pdf_advanced(docx_path, output_path)
        
        if success:
            return True
        else:
            print("Advanced conversion failed, falling back to basic LibreOffice conversion")
            # Fallback to basic LibreOffice conversion
            return convert_docx_to_pdf_basic(docx_path, output_path)
            
    except Exception as e:
        print(f"Error with advanced DOCX conversion: {e}")
        # Fallback to basic conversion
        return convert_docx_to_pdf_basic(docx_path, output_path)

def convert_docx_to_pdf_basic(docx_path, output_path):
    """Basic DOCX to PDF conversion using LibreOffice (fallback method)"""
    try:
        import subprocess
        import os
        
        # Use LibreOffice headless mode for conversion
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', os.path.dirname(output_path),
            docx_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # LibreOffice creates the PDF with the same base name as the input file
            base_name = os.path.splitext(os.path.basename(docx_path))[0]
            temp_pdf_path = os.path.join(os.path.dirname(output_path), f"{base_name}.pdf")
            
            # Rename to the expected output path
            if os.path.exists(temp_pdf_path):
                os.rename(temp_pdf_path, output_path)
                return True
            else:
                print(f"LibreOffice conversion succeeded but PDF not found at {temp_pdf_path}")
                return False
        else:
            print(f"LibreOffice conversion failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("LibreOffice conversion timed out")
        return False
    except Exception as e:
        print(f"Error converting DOCX to PDF with LibreOffice: {e}")
        return False

def convert_doc_to_pdf(doc_path, output_path):
    """Convert DOC to PDF using docx2txt and reportlab"""
    try:
        import docx2txt
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        # Extract text from .doc file
        text = docx2txt.process(doc_path)
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        y = height - 50
        
        # Split text into paragraphs
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():
                if y < 50:  # Start new page
                    c.showPage()
                    y = height - 50
                
                # Simple text wrapping
                words = paragraph.split()
                line = ""
                
                for word in words:
                    test_line = line + " " + word if line else word
                    if len(test_line) > 80:  # Approximate character limit
                        c.drawString(50, y, line)
                        y -= 20
                        line = word
                        if y < 50:
                            c.showPage()
                            y = height - 50
                    else:
                        line = test_line
                
                if line:
                    c.drawString(50, y, line)
                    y -= 20
                
                y -= 10  # Extra space between paragraphs
        
        c.save()
        return True
    except Exception as e:
        print(f"Error converting DOC to PDF: {e}")
        return False

def convert_xlsx_to_pdf(xlsx_path, output_path):
    """Convert XLSX to PDF"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, landscape
        from openpyxl import load_workbook
        
        wb = load_workbook(xlsx_path)
        ws = wb.active
        
        c = canvas.Canvas(output_path, pagesize=landscape(letter))
        width, height = landscape(letter)
        
        y = height - 50
        
        for row in ws.iter_rows(values_only=True):
            if y < 50:
                c.showPage()
                y = height - 50
            
            row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
            c.drawString(50, y, row_text[:100])  # Limit line length
            y -= 20
        
        c.save()
        return True
    except Exception as e:
        print(f"Error converting XLSX to PDF: {e}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Convert to PDF
        file_extension = filename.rsplit('.', 1)[1].lower()
        output_filename = f"{os.path.splitext(filename)[0]}_{str(uuid.uuid4())[:8]}.pdf"
        output_path = os.path.join(app.config['CONVERTED_FOLDER'], output_filename)
        
        success = False
        
        if file_extension == 'pdf':
            # Already a PDF, just copy
            import shutil
            shutil.copy2(file_path, output_path)
            success = True
        elif file_extension == 'txt':
            success = convert_text_to_pdf(file_path, output_path)
        elif file_extension in ['png', 'jpg', 'jpeg', 'gif']:
            success = convert_image_to_pdf(file_path, output_path)
        elif file_extension == 'docx':
            success = convert_docx_to_pdf(file_path, output_path)
        elif file_extension == 'doc':
            success = convert_doc_to_pdf(file_path, output_path)
        elif file_extension == 'xlsx':
            success = convert_xlsx_to_pdf(file_path, output_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if success:
            return jsonify({
                'message': 'File converted successfully',
                'filename': output_filename,
                'download_url': f'/download/{output_filename}'
            })
        else:
            return jsonify({'error': 'Conversion failed'}), 500
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(
            os.path.join(app.config['CONVERTED_FOLDER'], filename),
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/pdf-info/<filename>')
def pdf_info(filename):
    """Get PDF information like page count"""
    try:
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], filename)
        with open(file_path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            return jsonify({
                'pages': len(reader.pages),
                'filename': filename
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/download-split/<split_dir>/<filename>')
def download_split_file(split_dir, filename):
    """Download files from split operations"""
    try:
        file_path = os.path.join(app.config['CONVERTED_FOLDER'], split_dir, filename)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

