"""File validation utilities"""
import os
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def validate_pdf(filepath):
    """Validate that a file is a valid PDF
    
    Args:
        filepath: Path to the file
        
    Returns:
        bool: True if valid PDF
    """
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'
    except Exception:
        return False


def get_safe_filename(filename):
    """Get a safe version of filename
    
    Args:
        filename: Original filename
        
    Returns:
        str: Secure filename
    """
    return secure_filename(filename)


def ensure_unique_filename(directory, filename):
    """Ensure filename is unique in directory
    
    Args:
        directory: Target directory
        filename: Desired filename
        
    Returns:
        str: Unique filename
    """
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1
    
    return new_filename
