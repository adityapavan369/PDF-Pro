"""PDF editing utilities"""
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from PIL import Image
from io import BytesIO
import fitz  # PyMuPDF for text editing


def rotate_pdf(input_path, output_path, rotation=90):
    """Rotate all pages in a PDF by specified degrees
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        rotation: Rotation angle (90, 180, 270)
        
    Returns:
        str: Path to rotated PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.rotate(rotation)
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error rotating PDF: {str(e)}")


def get_font_details(page, span):
    """Extract detailed font information from a text span"""
    font_info = {
        'name': span.get("font", "helv"),
        'size': span.get("size", 11),
        'color': span.get("color", (0, 0, 0)),
        'flags': span.get("flags", 0),
        'style': 'regular'
    }
    
    # Analyze font name for style information
    name = font_info['name'].lower()
    if 'bold' in name or 'black' in name or 'heavy' in name:
        font_info['style'] = 'bold'
    elif 'italic' in name or 'oblique' in name:
        font_info['style'] = 'italic'
    elif 'light' in name:
        font_info['style'] = 'light'
    
    # Check font flags for additional properties
    flags = font_info['flags']
    if flags & 2**0:  # Usually indicates serif font
        font_info['serif'] = True
    if flags & 2**1:  # Usually indicates fixed-width
        font_info['monospace'] = True
    if flags & 2**2:  # Usually indicates italic
        font_info['style'] = 'italic'
    if flags & 2**3:  # Usually indicates bold
        font_info['style'] = 'bold'
    
    return font_info

def match_system_font(font_name):
    """Match PDF font to system font"""
    system_fonts = {
        'times': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
        'helvetica': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        'courier': '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
        'lucida': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Fallback for Lucida
        'arial': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    }
    
    # Try to find a match
    font_lower = font_name.lower()
    for key, path in system_fonts.items():
        if key in font_lower:
            return path
            
    # Return default font if no match found
    return system_fonts['helvetica']

def get_font_details(page, span):
    """Extract detailed font information from a text span"""
    font_info = {
        'name': span.get("font", "helv"),
        'size': span.get("size", 11),
        'color': span.get("color", (0, 0, 0)),
        'flags': span.get("flags", 0),
        'style': 'regular'
    }
    
    # Analyze font name for style information
    name = font_info['name'].lower()
    if 'bold' in name or 'black' in name or 'heavy' in name:
        font_info['style'] = 'bold'
    elif 'italic' in name or 'oblique' in name:
        font_info['style'] = 'italic'
    elif 'light' in name:
        font_info['style'] = 'light'
    
    # Check font flags for additional properties
    flags = font_info['flags']
    if flags & 2**0:  # Usually indicates serif font
        font_info['serif'] = True
    if flags & 2**1:  # Usually indicates fixed-width
        font_info['monospace'] = True
    if flags & 2**2:  # Usually indicates italic
        font_info['style'] = 'italic'
    if flags & 2**3:  # Usually indicates bold
        font_info['style'] = 'bold'
    
    return font_info

def match_system_font(font_name):
    """Match PDF font to system font"""
    system_fonts = {
        'times': '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
        'helvetica': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        'courier': '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
        'lucida': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',  # Fallback for Lucida
        'arial': '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    }
    
    # Try to find a match
    font_lower = font_name.lower()
    for key, path in system_fonts.items():
        if key in font_lower:
            return path
            
    # Return default font if no match found
    return system_fonts['helvetica']

def edit_pdf_text(input_path, output_path, page_number, old_text, new_text):
    """Edit text in a PDF file while preserving exact formatting and calligraphy
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        page_number: Page number to edit (1-based)
        old_text: Text to replace
        new_text: New text to insert
        
    Returns:
        str: Path to edited PDF file
    """
    try:
        # Open the PDF with PyMuPDF
        doc = fitz.open(input_path)
        page = doc[page_number - 1]
        
        # Find text instances and get their formatting
        text_instances = page.search_for(old_text)
        
        for inst in text_instances:
            # Get detailed text properties with exact font information
            font_info = page.get_text("dict", clip=inst)
            
            if "blocks" in font_info and font_info["blocks"]:
                for block in font_info["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            if "spans" in line:
                                for span in line["spans"]:
                                    if old_text in span.get("text", ""):
                                        # Get detailed font information
                                        font_details = get_font_details(page, span)
                                        
                                        # Match with system font
                                        font_path = match_system_font(font_details['name'])
                                        
                                        # Remove old text
                                        page.add_redact_annot(inst)
                                        page.apply_redactions()
                                        
                                        # Insert new text with matched font
                                        try:
                                            # Try to use exact font
                                            page.insert_text(
                                                inst[:2],  # Position
                                                new_text,
                                                fontfile=font_path,  # Use matched system font
                                                fontname=font_details['name'],
                                                fontsize=font_details['size'],
                                                color=font_details['color']
                                            )
                                        except Exception:
                                            # Fallback to standard font while preserving other properties
                                            page.insert_text(
                                                inst[:2],
                                                new_text,
                                                fontname=font_details['name'],
                                                fontsize=font_details['size'],
                                                color=font_details['color']
                                            )
        
        # Save with optimization for better quality
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        return output_path
    except Exception as e:
        raise Exception(f"Error editing PDF text: {str(e)}")


def add_signature(input_path, output_path, signature_path, page_number, x, y, width=None, height=None):
    """Add a signature image to a PDF
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        signature_path: Path to signature image file
        page_number: Page number to add signature (1-based)
        x: X coordinate for signature placement
        y: Y coordinate for signature placement
        width: Optional width to resize signature
        height: Optional height to resize signature
        
    Returns:
        str: Path to PDF with signature
    """
    try:
        # Open the PDF
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Copy all pages
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            if i == page_number - 1:
                # Create a new PDF with the signature
                packet = BytesIO()
                sig_canvas = canvas.Canvas(packet, pagesize=letter)
                
                # Load and resize signature if needed
                if width and height:
                    sig_canvas.drawImage(signature_path, x, y, width=width, height=height)
                else:
                    sig_canvas.drawImage(signature_path, x, y)
                
                sig_canvas.save()
                packet.seek(0)
                
                # Create PDF from signature
                signature_pdf = PdfReader(packet)
                signature_page = signature_pdf.pages[0]
                
                # Merge signature with the page
                page.merge_page(signature_page)
            
            writer.add_page(page)
        
        # Save the result
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error adding signature: {str(e)}")


def add_watermark(input_path, output_path, watermark_text):
    """Add text watermark to all pages in a PDF
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        watermark_text: Text to use as watermark
        
    Returns:
        str: Path to watermarked PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Create watermark
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFont("Helvetica", 60)
        can.setFillColorRGB(0.5, 0.5, 0.5, 0.3)
        can.saveState()
        can.translate(300, 400)
        can.rotate(45)
        can.drawString(0, 0, watermark_text)
        can.restoreState()
        can.save()
        
        packet.seek(0)
        watermark = PdfReader(packet)
        watermark_page = watermark.pages[0]
        
        # Apply watermark to each page
        for page in reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error adding watermark: {str(e)}")


def extract_pages(input_path, output_path, page_numbers):
    """Extract specific pages from a PDF
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        page_numbers: List of page numbers to extract (1-indexed)
        
    Returns:
        str: Path to extracted PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page_num in page_numbers:
            # Convert to 0-indexed
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error extracting pages: {str(e)}")


def delete_pages(input_path, output_path, page_numbers):
    """Delete specific pages from a PDF
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        page_numbers: List of page numbers to delete (1-indexed)
        
    Returns:
        str: Path to modified PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for i, page in enumerate(reader.pages):
            # Keep pages that are not in the delete list
            if (i + 1) not in page_numbers:
                writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error deleting pages: {str(e)}")
