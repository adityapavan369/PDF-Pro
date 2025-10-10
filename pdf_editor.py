import pypdf
import fitz  # PyMuPDF
import io
import os
from PIL import Image

class PDFEditor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf_document = fitz.open(pdf_path)
    
    def get_page_count(self):
        """Get the number of pages in the PDF"""
        return len(self.pdf_document)
    
    def extract_text(self, page_num):
        """Extract text from a specific page"""
        try:
            page = self.pdf_document[page_num]
            return page.get_text()
        except Exception as e:
            return f"Error extracting text: {e}"
    
    def rotate_page(self, page_num, angle):
        """Rotate a page by the specified angle (90, 180, 270)"""
        try:
            page = self.pdf_document[page_num]
            page.set_rotation(angle)
            return True
        except Exception as e:
            print(f"Error rotating page: {e}")
            return False
    
    def delete_page(self, page_num):
        """Delete a specific page"""
        try:
            self.pdf_document.delete_pages(page_num)
            return True
        except Exception as e:
            print(f"Error deleting page: {e}")
            return False
    
    def add_text(self, page_num, text, position, fontsize=12, color=(0, 0, 0)):
        """Add text to a specific page, matching detected font if possible"""
        try:
            page = self.pdf_document[page_num]
            
            # Detect existing fonts on the page
            detected_font = None
            try:
                text_instances = page.get_text("dict")["blocks"]
                for block in text_instances:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if "font" in span:
                                    detected_font = span["font"]
                                    break
                            if detected_font:
                                break
                    if detected_font:
                        break
            except:
                pass
            
            # Use detected font or fallback to default
            font = detected_font if detected_font else "helv"
            
            # Insert text with detected or default font
            page.insert_text(
                position,
                text,
                fontsize=fontsize,
                color=color,
                fontname=font
            )
            return True
        except Exception as e:
            print(f"Error adding text: {e}")
            return False
    
    def add_image(self, page_num, image_path, position, width=None, height=None):
        """Add an image to a specific page"""
        try:
            page = self.pdf_document[page_num]
            rect = fitz.Rect(position[0], position[1], 
                           position[0] + (width or 100), 
                           position[1] + (height or 100))
            page.insert_image(rect, filename=image_path)
            return True
        except Exception as e:
            print(f"Error adding image: {e}")
            return False
    
    def save(self, output_path):
        """Save the edited PDF"""
        try:
            self.pdf_document.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False
    
    def close(self):
        """Close the PDF document"""
        self.pdf_document.close()

def parse_page_ranges(range_string):
    """Parse custom page ranges for splitting PDFs.
    
    Args:
        range_string: String with page ranges like '1-3,5,7-9'
    
    Returns:
        List of tuples with (start, end) page numbers (0-indexed)
        Returns None if invalid format
    """
    if not range_string or not range_string.strip():
        return None
    
    try:
        ranges = []
        parts = range_string.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip()) - 1  # Convert to 0-indexed
                end = int(end.strip()) - 1
                if start < 0 or end < 0 or start > end:
                    return None
                ranges.append((start, end))
            else:
                page = int(part.strip()) - 1  # Convert to 0-indexed
                if page < 0:
                    return None
                ranges.append((page, page))
        
        return ranges
    except (ValueError, AttributeError):
        return None
