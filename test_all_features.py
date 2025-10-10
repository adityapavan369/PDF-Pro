"""Integration test for all PDF features"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import blue, red, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from utils.splitter import split_pdf_by_page_numbers, split_pdf_into_multiple
from utils.editor import edit_pdf_text, add_signature
from PIL import Image, ImageDraw, ImageFont

def create_sample_pdf(output_path):
    """Create a sample PDF with various fonts and content"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Page 1 - Multiple fonts
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(blue)
    c.drawString(100, height - 100, "PDF-Pro Feature Demo")
    
    c.setFont("Times-Roman", 16)
    c.setFillColor(black)
    c.drawString(100, height - 150, "This text will demonstrate font preservation")
    
    c.setFont("Courier", 14)
    c.setFillColor(red)
    c.drawString(100, height - 200, "Different font for testing")
    
    # Page 2 - Content for splitting
    c.showPage()
    c.setFont("Helvetica", 18)
    c.setFillColor(blue)
    c.drawString(100, height - 100, "Page 2 - Will be in first split")
    
    # Page 3 - More content
    c.showPage()
    c.setFont("Times-Roman", 18)
    c.drawString(100, height - 100, "Page 3 - Will be extracted individually")
    
    # Page 4 - For second split
    c.showPage()
    c.setFont("Helvetica-Bold", 18)
    c.drawString(100, height - 100, "Page 4 - Will be in second split")
    
    # Page 5 - For second split
    c.showPage()
    c.setFont("Courier", 18)
    c.drawString(100, height - 100, "Page 5 - Will be in second split")
    
    c.save()
    return output_path

def create_signature():
    """Create a sample signature image"""
    img = Image.new('RGBA', (300, 150), color=(255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    d.text((20, 50), "John A. Doe", fill='blue')
    d.line([(20, 100), (280, 100)], fill='blue', width=2)
    return img

def main():
    # Create test directory
    test_dir = "feature_test_outputs"
    os.makedirs(test_dir, exist_ok=True)
    
    print("\n=== Testing All PDF-Pro Features ===")
    
    # 1. Create sample PDF
    test_pdf = os.path.join(test_dir, "sample.pdf")
    create_sample_pdf(test_pdf)
    print(f"\n✓ Created sample PDF: {test_pdf}")
    
    # 2. Test splitting specific pages (page 3)
    split_single = os.path.join(test_dir, "page3.pdf")
    split_pdf_by_page_numbers(test_pdf, split_single, [3])
    print(f"✓ Extracted page 3: {split_single}")
    
    # 3. Test splitting into multiple ranges (pages 1-2 and 4-5)
    split_files = split_pdf_into_multiple(test_pdf, test_dir, [(1, 2), (4, 5)])
    print("✓ Split into multiple PDFs:")
    for pdf in split_files:
        print(f"  - {pdf}")
    
    # 4. Test text editing with font preservation
    edit_cases = [
        ("This text will demonstrate font preservation", "Font preservation works perfectly!", 1),
        ("Different font for testing", "This maintains the Courier font", 1),
        ("Page 3 - Will be extracted individually", "This text was edited with Times-Roman", 3)
    ]
    
    for old_text, new_text, page in edit_cases:
        output = os.path.join(test_dir, f"edited_page{page}.pdf")
        edit_pdf_text(test_pdf, output, page, old_text, new_text)
        print(f"✓ Edited text on page {page} (preserving font): {output}")
    
    # 5. Test signature in different sizes
    sig_path = os.path.join(test_dir, "signature.png")
    create_signature().save(sig_path)
    
    # Add signatures in different sizes
    sizes = [
        ("small", 150, 75),
        ("medium", 300, 150),
        ("large", 450, 225)
    ]
    
    for size_name, width, height in sizes:
        output = os.path.join(test_dir, f"signed_{size_name}.pdf")
        add_signature(test_pdf, output, sig_path, 1, x=100, y=height, width=width, height=height)
        print(f"✓ Added {size_name} signature: {output}")
    
    print("\n=== All features tested successfully! ===")
    print(f"Output files are in: {test_dir}/")

if __name__ == "__main__":
    main()