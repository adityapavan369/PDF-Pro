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
            self.pdf_document.delete_page(page_num)
            return True
        except Exception as e:
            print(f"Error deleting page: {e}")
            return False
    
    def add_text(self, page_num, text, x, y, font_size=12):
        """Add text to a specific page at given coordinates"""
        try:
            page = self.pdf_document[page_num]
            point = fitz.Point(x, y)
            page.insert_text(point, text, fontsize=font_size)
            return True
        except Exception as e:
            print(f"Error adding text: {e}")
            return False
    
    def add_highlight(self, page_num, x1, y1, x2, y2):
        """Add highlight annotation to a rectangular area"""
        try:
            page = self.pdf_document[page_num]
            rect = fitz.Rect(x1, y1, x2, y2)
            highlight = page.add_highlight_annot(rect)
            highlight.set_colors(stroke=[1, 1, 0])  # Yellow highlight
            highlight.update()
            return True
        except Exception as e:
            print(f"Error adding highlight: {e}")
            return False
    
    def add_note(self, page_num, x, y, content):
        """Add a text note annotation"""
        try:
            page = self.pdf_document[page_num]
            point = fitz.Point(x, y)
            note = page.add_text_annot(point, content)
            note.set_info(content=content)
            note.update()
            return True
        except Exception as e:
            print(f"Error adding note: {e}")
            return False
    
    def crop_page(self, page_num, x1, y1, x2, y2):
        """Crop a page to the specified rectangle"""
        try:
            page = self.pdf_document[page_num]
            rect = fitz.Rect(x1, y1, x2, y2)
            page.set_cropbox(rect)
            return True
        except Exception as e:
            print(f"Error cropping page: {e}")
            return False
    
    def insert_image(self, page_num, image_path, x, y, width, height):
        """Insert an image into the PDF"""
        try:
            page = self.pdf_document[page_num]
            rect = fitz.Rect(x, y, x + width, y + height)
            page.insert_image(rect, filename=image_path)
            return True
        except Exception as e:
            print(f"Error inserting image: {e}")
            return False
    
    def get_page_as_image(self, page_num, zoom=1.0):
        """Convert a page to an image for display"""
        try:
            page = self.pdf_document[page_num]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            return img_data
        except Exception as e:
            print(f"Error converting page to image: {e}")
            return None
    
    def save(self, output_path=None):
        """Save the modified PDF"""
        try:
            if output_path is None:
                output_path = self.pdf_path
            self.pdf_document.save(output_path)
            return True
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False
    
    def close(self):
        """Close the PDF document"""
        self.pdf_document.close()

class PDFMerger:
    @staticmethod
    def merge_pdfs(pdf_paths, output_path):
        """Merge multiple PDFs into one"""
        try:
            merger = pypdf.PdfWriter()
            
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        merger.add_page(page)
            
            with open(output_path, 'wb') as f:
                merger.write(f)
            
            return True
        except Exception as e:
            print(f"Error merging PDFs: {e}")
            return False
    
    @staticmethod
    def split_pdf(pdf_path, output_dir, page_ranges):
        """Split PDF into multiple files based on page ranges"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                
                for i, (start, end) in enumerate(page_ranges):
                    writer = pypdf.PdfWriter()
                    
                    for page_num in range(start, min(end + 1, len(reader.pages))):
                        writer.add_page(reader.pages[page_num])
                    
                    output_filename = f"split_{i+1}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
            
            return True
        except Exception as e:
            print(f"Error splitting PDF: {e}")
            return False

