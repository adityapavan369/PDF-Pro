"""
Simple tests for PDF-Pro application
Run with: python test_app.py
"""
import os
import sys
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader

# Import application
from app import app
from utils.converter import image_to_pdf, images_to_pdf
from utils.merger import merge_pdfs
from utils.splitter import split_pdf_into_single_pages
from utils.editor import rotate_pdf, add_watermark


def test_image_conversion():
    """Test image to PDF conversion"""
    print("Testing image to PDF conversion...")
    test_dir = '/tmp/test_pdf_pro'
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test image
    img_path = os.path.join(test_dir, 'test.png')
    img = Image.new('RGB', (400, 300), color='blue')
    img.save(img_path)
    
    # Convert to PDF
    pdf_path = os.path.join(test_dir, 'converted.pdf')
    image_to_pdf(img_path, pdf_path)
    
    # Verify
    reader = PdfReader(pdf_path)
    assert len(reader.pages) == 1, "Expected 1 page"
    print("✓ Image conversion test passed")


def test_pdf_merge():
    """Test PDF merging"""
    print("Testing PDF merge...")
    test_dir = '/tmp/test_pdf_pro'
    
    # Create test PDFs
    pdf1 = os.path.join(test_dir, 'merge1.pdf')
    pdf2 = os.path.join(test_dir, 'merge2.pdf')
    
    c = canvas.Canvas(pdf1, pagesize=letter)
    c.drawString(100, 750, "PDF 1")
    c.save()
    
    c = canvas.Canvas(pdf2, pagesize=letter)
    c.drawString(100, 750, "PDF 2")
    c.save()
    
    # Merge
    merged = os.path.join(test_dir, 'merged.pdf')
    merge_pdfs([pdf1, pdf2], merged)
    
    # Verify
    reader = PdfReader(merged)
    assert len(reader.pages) == 2, "Expected 2 pages"
    print("✓ PDF merge test passed")


def test_pdf_split():
    """Test PDF splitting"""
    print("Testing PDF split...")
    test_dir = '/tmp/test_pdf_pro'
    
    # Create multi-page PDF
    pdf_path = os.path.join(test_dir, 'multi.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Page 1")
    c.showPage()
    c.drawString(100, 750, "Page 2")
    c.save()
    
    # Split
    split_dir = os.path.join(test_dir, 'split')
    files = split_pdf_into_single_pages(pdf_path, split_dir)
    
    assert len(files) == 2, "Expected 2 split files"
    print("✓ PDF split test passed")


def test_pdf_edit():
    """Test PDF editing"""
    print("Testing PDF edit operations...")
    test_dir = '/tmp/test_pdf_pro'
    
    # Create test PDF
    pdf_path = os.path.join(test_dir, 'edit.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, "Test Page")
    c.save()
    
    # Test rotation
    rotated = os.path.join(test_dir, 'rotated.pdf')
    rotate_pdf(pdf_path, rotated, 90)
    assert os.path.exists(rotated), "Rotated PDF not created"
    
    # Test watermark
    watermarked = os.path.join(test_dir, 'watermarked.pdf')
    add_watermark(pdf_path, watermarked, "TEST")
    assert os.path.exists(watermarked), "Watermarked PDF not created"
    
    print("✓ PDF edit test passed")


def test_flask_routes():
    """Test Flask application routes"""
    print("Testing Flask routes...")
    
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        assert response.status_code == 200, "Home page failed"
        
        # Test convert page
        response = client.get('/convert')
        assert response.status_code == 200, "Convert page failed"
        
        # Test merge page
        response = client.get('/merge')
        assert response.status_code == 200, "Merge page failed"
        
        # Test split page
        response = client.get('/split')
        assert response.status_code == 200, "Split page failed"
        
        # Test edit page
        response = client.get('/edit')
        assert response.status_code == 200, "Edit page failed"
        
        # Test API
        response = client.get('/api/info')
        assert response.status_code == 200, "API info failed"
        data = response.get_json()
        assert data['status'] == 'online', "API status incorrect"
        
    print("✓ Flask routes test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Running PDF-Pro Tests")
    print("=" * 50)
    
    try:
        test_image_conversion()
        test_pdf_merge()
        test_pdf_split()
        test_pdf_edit()
        test_flask_routes()
        test_acceptance_advanced_docx()
        
        print("=" * 50)
        print("✓ All tests passed successfully!")
        print("=" * 50)
        return 0
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def test_acceptance_advanced_docx():
    """Acceptance test for advanced DOCX converter (if available)."""
    print("Testing advanced DOCX converter acceptance...")
    test_dir = '/tmp/test_pdf_pro'
    os.makedirs(test_dir, exist_ok=True)
    src = '/workspaces/PDF-Pro/uploads/Aditya_Senior_Test_Engineer_Fidelity.docx'
    if not os.path.exists(src):
        print('No sample docx found for acceptance test; skipping')
        return
    out = os.path.join(test_dir, 'advanced_converted.pdf')
    from utils.converter import docx_to_pdf
    docx_to_pdf(src, out)
    assert os.path.exists(out), 'Advanced conversion did not produce output'
    from PyPDF2 import PdfReader
    reader = PdfReader(out)
    assert len(reader.pages) >= 1, 'Converted PDF has no pages'
    print('✓ Advanced DOCX acceptance test passed')


if __name__ == '__main__':
    sys.exit(run_all_tests())
