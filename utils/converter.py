"""PDF conversion utilities"""
import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
import platform


def image_to_pdf(image_path, output_path):
    """Convert an image file to PDF
    
    Args:
        image_path: Path to input image file
        output_path: Path to output PDF file
        
    Returns:
        str: Path to converted PDF file
    """
    try:
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Get image dimensions
        img_width, img_height = img.size
        
        # Create PDF with appropriate page size
        c = canvas.Canvas(output_path, pagesize=(img_width, img_height))
        
        # Draw image on PDF
        c.drawImage(image_path, 0, 0, width=img_width, height=img_height)
        c.save()
        
        return output_path
    except Exception as e:
        raise Exception(f"Error converting image to PDF: {str(e)}")


def docx_to_pdf(docx_path, output_path):
    """Convert a DOCX file to PDF
    
    Args:
        docx_path: Path to input DOCX file
        output_path: Path to output PDF file
        
    Returns:
        str: Path to converted PDF file
    """
    try:
        # Check platform - docx2pdf only works on Windows/MacOS with MS Word
        system = platform.system()
        
        if system == 'Windows' or system == 'Darwin':
            # Use docx2pdf on Windows/MacOS
            from docx2pdf import convert
            convert(docx_path, output_path)
        else:
            # For Linux, use python-docx with reportlab as fallback
            from docx import Document
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            
            doc = Document(docx_path)
            pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            for para in doc.paragraphs:
                if para.text.strip():
                    p = Paragraph(para.text, styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 12))
            
            pdf_doc.build(story)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error converting DOCX to PDF: {str(e)}")


def images_to_pdf(image_paths, output_path):
    """Convert multiple images to a single PDF
    
    Args:
        image_paths: List of paths to input image files
        output_path: Path to output PDF file
        
    Returns:
        str: Path to converted PDF file
    """
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        
        for image_path in image_paths:
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Scale image to fit page if needed
            page_width, page_height = A4
            aspect = img_height / float(img_width)
            
            if img_width > page_width:
                img_width = page_width
                img_height = img_width * aspect
            
            if img_height > page_height:
                img_height = page_height
                img_width = img_height / aspect
            
            # Center image on page
            x = (page_width - img_width) / 2
            y = (page_height - img_height) / 2
            
            c.drawImage(image_path, x, y, width=img_width, height=img_height)
            c.showPage()
        
        c.save()
        return output_path
    except Exception as e:
        raise Exception(f"Error converting images to PDF: {str(e)}")
