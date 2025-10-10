"""Real-world example test for PDF-Pro features"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import blue, red, black, green
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from utils.splitter import split_pdf_by_page_numbers, split_pdf_into_multiple
from utils.editor import edit_pdf_text, add_signature
from PIL import Image, ImageDraw, ImageFont

def create_business_document(output_path):
    """Create a sample business document with various sections"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Page 1 - Cover Page
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(blue)
    c.drawString(100, height - 100, "Annual Report 2025")
    
    c.setFont("Times-Roman", 16)
    c.setFillColor(black)
    c.drawString(100, height - 150, "Confidential Document")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 200, "This section will be edited later")
    
    # Page 2 - Executive Summary
    c.showPage()
    c.setFont("Times-Roman", 18)
    c.drawString(100, height - 100, "Executive Summary")
    c.setFont("Times-Roman", 12)
    c.drawString(100, height - 150, "Summary text that will be extracted")
    
    # Page 3 - Financial Data
    c.showPage()
    c.setFont("Courier", 18)
    c.drawString(100, height - 100, "Financial Data")
    c.setFont("Courier", 12)
    for i, item in enumerate(["Revenue: $1M", "Expenses: $700K", "Profit: $300K"], 1):
        c.drawString(100, height - 100 - (i * 30), item)
    
    # Page 4 - Future Plans
    c.showPage()
    c.setFont("Helvetica", 18)
    c.drawString(100, height - 100, "Future Plans")
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "Strategic initiatives for next year")
    
    # Page 5 - Approval Page
    c.showPage()
    c.setFont("Times-Roman", 18)
    c.drawString(100, height - 100, "Approval Page")
    c.setFont("Times-Roman", 12)
    c.drawString(100, height - 150, "Signature required here")
    
    c.save()
    return output_path

def create_professional_signature():
    """Create a professional-looking signature"""
    img = Image.new('RGBA', (400, 200), color=(255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    # Draw signature text
    d.text((20, 50), "Sarah Johnson", fill='blue')
    d.text((20, 80), "Chief Executive Officer", fill='black')
    
    # Draw signature line
    d.line([(20, 150), (380, 150)], fill='blue', width=3)
    
    return img

def test_real_world_scenario():
    """Test PDF-Pro features with a business document scenario"""
    # Create test directory
    test_dir = "business_doc_test"
    os.makedirs(test_dir, exist_ok=True)
    
    print("\n=== Testing PDF-Pro with Business Document ===")
    
    # 1. Create sample business document
    doc_path = os.path.join(test_dir, "annual_report.pdf")
    create_business_document(doc_path)
    print(f"\n✓ Created business document: {doc_path}")
    
    # 2. Extract Executive Summary (Page 2)
    summary_path = os.path.join(test_dir, "executive_summary.pdf")
    split_pdf_by_page_numbers(doc_path, summary_path, [2])
    print(f"✓ Extracted Executive Summary: {summary_path}")
    
    # 3. Extract Financial Section (Page 3)
    financial_path = os.path.join(test_dir, "financial_data.pdf")
    split_pdf_by_page_numbers(doc_path, financial_path, [3])
    print(f"✓ Extracted Financial Data: {financial_path}")
    
    # 4. Create document sets
    # Set 1: Cover + Executive Summary
    # Set 2: Financial + Future Plans
    split_files = split_pdf_into_multiple(doc_path, test_dir, [(1, 2), (3, 4)])
    print("✓ Created document sets:")
    for pdf in split_files:
        print(f"  - {pdf}")
    
    # 5. Edit text while preserving formatting
    edit_cases = [
        ("This section will be edited later", 
         "Updated: October 10, 2025", 1),
        ("Strategic initiatives for next year",
         "Strategic Initiatives 2026-2027", 4)
    ]
    
    for old_text, new_text, page in edit_cases:
        output = os.path.join(test_dir, f"edited_page{page}.pdf")
        edit_pdf_text(doc_path, output, page, old_text, new_text)
        print(f"✓ Updated text on page {page}: {output}")
    
    # 6. Add signature to approval page
    sig_path = os.path.join(test_dir, "signature.png")
    create_professional_signature().save(sig_path)
    
    # Add signature in different positions
    positions = [
        ("centered", 200, 300),
        ("bottom", 100, 200),
        ("custom", 150, 250)
    ]
    
    for pos_name, x, y in positions:
        output = os.path.join(test_dir, f"signed_{pos_name}.pdf")
        add_signature(doc_path, output, sig_path, 5, x=x, y=y, width=200, height=100)
        print(f"✓ Added signature ({pos_name} position): {output}")
    
    print("\n=== Business Document Processing Complete! ===")
    print(f"All processed files are in: {test_dir}/")

if __name__ == "__main__":
    test_real_world_scenario()