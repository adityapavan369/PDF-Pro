from flask import Blueprint, request, jsonify, send_file
import os
import uuid
import base64
from pdf_editor import PDFEditor, PDFMerger
import tempfile

pdf_api = Blueprint('pdf_api', __name__)

@pdf_api.route('/edit/rotate', methods=['POST'])
def rotate_page():
    """Rotate a page in the PDF"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    angle = data.get('angle', 90)
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.rotate_page(page_num, angle)
        if success:
            # Save with new filename to preserve original
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Page rotated successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to rotate page'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/edit/delete-page', methods=['POST'])
def delete_page():
    """Delete a page from the PDF"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.delete_page(page_num)
        if success:
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Page deleted successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to delete page'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/edit/add-text', methods=['POST'])
def add_text():
    """Add text to a PDF page"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    text = data.get('text', '')
    x = data.get('x', 100)
    y = data.get('y', 100)
    font_size = data.get('font_size', 12)
    
    if not filename or not text:
        return jsonify({'error': 'Filename and text required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.add_text(page_num, text, x, y, font_size)
        if success:
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Text added successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to add text'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/edit/highlight', methods=['POST'])
def add_highlight():
    """Add highlight annotation to PDF"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    x1 = data.get('x1', 0)
    y1 = data.get('y1', 0)
    x2 = data.get('x2', 100)
    y2 = data.get('y2', 20)
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.add_highlight(page_num, x1, y1, x2, y2)
        if success:
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Highlight added successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to add highlight'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/edit/note', methods=['POST'])
def add_note():
    """Add note annotation to PDF"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    x = data.get('x', 100)
    y = data.get('y', 100)
    content = data.get('content', '')
    
    if not filename or not content:
        return jsonify({'error': 'Filename and content required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.add_note(page_num, x, y, content)
        if success:
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Note added successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to add note'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/edit/crop', methods=['POST'])
def crop_page():
    """Crop a page in the PDF"""
    data = request.get_json()
    filename = data.get('filename')
    page_num = data.get('page_num', 0)
    x1 = data.get('x1', 0)
    y1 = data.get('y1', 0)
    x2 = data.get('x2', 500)
    y2 = data.get('y2', 700)
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        editor = PDFEditor(file_path)
        
        success = editor.crop_page(page_num, x1, y1, x2, y2)
        if success:
            new_filename = f"edited_{uuid.uuid4()}_{filename}"
            new_path = os.path.join('converted', new_filename)
            editor.save(new_path)
            editor.close()
            
            return jsonify({
                'message': 'Page cropped successfully',
                'filename': new_filename,
                'download_url': f'/download/{new_filename}'
            })
        else:
            editor.close()
            return jsonify({'error': 'Failed to crop page'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDFs"""
    data = request.get_json()
    filenames = data.get('filenames', [])
    
    if not filenames or len(filenames) < 2:
        return jsonify({'error': 'At least 2 filenames required'}), 400
    
    try:
        pdf_paths = [os.path.join('converted', filename) for filename in filenames]
        
        # Check if all files exist
        for path in pdf_paths:
            if not os.path.exists(path):
                return jsonify({'error': f'File not found: {os.path.basename(path)}'}), 404
        
        merged_filename = f"merged_{uuid.uuid4()}.pdf"
        merged_path = os.path.join('converted', merged_filename)
        
        success = PDFMerger.merge_pdfs(pdf_paths, merged_path)
        if success:
            return jsonify({
                'message': 'PDFs merged successfully',
                'filename': merged_filename,
                'download_url': f'/download/{merged_filename}'
            })
        else:
            return jsonify({'error': 'Failed to merge PDFs'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/split', methods=['POST'])
def split_pdf():
    """Split PDF into multiple files"""
    data = request.get_json()
    filename = data.get('filename')
    page_ranges = data.get('page_ranges', [])  # List of [start, end] pairs
    
    if not filename or not page_ranges:
        return jsonify({'error': 'Filename and page_ranges required'}), 400
    
    try:
        file_path = os.path.join('converted', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Create temporary directory for split files
        split_dir = os.path.join('converted', f"split_{uuid.uuid4()}")
        os.makedirs(split_dir, exist_ok=True)
        
        success = PDFMerger.split_pdf(file_path, split_dir, page_ranges)
        if success:
            # List the created files
            split_files = os.listdir(split_dir)
            download_urls = [f'/download-split/{os.path.basename(split_dir)}/{f}' for f in split_files]
            
            return jsonify({
                'message': 'PDF split successfully',
                'files': split_files,
                'download_urls': download_urls,
                'split_dir': os.path.basename(split_dir)
            })
        else:
            return jsonify({'error': 'Failed to split PDF'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/page-image/<filename>/<int:page_num>')
def get_page_image(filename, page_num):
    """Get a page as an image for preview"""
    try:
        file_path = os.path.join('converted', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        editor = PDFEditor(file_path)
        img_data = editor.get_page_as_image(page_num, zoom=1.5)
        editor.close()
        
        if img_data:
            # Return image as base64 encoded string
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            return jsonify({
                'image': f"data:image/png;base64,{img_base64}"
            })
        else:
            return jsonify({'error': 'Failed to generate page image'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pdf_api.route('/extract-text/<filename>/<int:page_num>')
def extract_text(filename, page_num):
    """Extract text from a specific page"""
    try:
        file_path = os.path.join('converted', filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        editor = PDFEditor(file_path)
        text = editor.extract_text(page_num)
        editor.close()
        
        return jsonify({
            'text': text,
            'page_num': page_num
        })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

