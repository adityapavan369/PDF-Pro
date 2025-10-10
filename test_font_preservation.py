"""Test script for font preservation in PDF editing"""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
from utils.editor import edit_pdf_text
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import sys

def create_multi_font_pdf(output_path):
    """Create a test PDF with multiple fonts"""
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Register fonts
    fonts_to_test = [
        ("Helvetica", "Regular text in Helvetica"),
        ("Times-Roman", "Serif text in Times Roman"),
        ("Courier", "Monospace text in Courier"),
        ("Helvetica-Bold", "Bold text in Helvetica"),
        ("Times-Italic", "Italic text in Times"),
    ]
    
    y_position = height - 100
    for font_name, text in fonts_to_test:
        c.setFont(font_name, 14)
        c.drawString(100, y_position, text)
        y_position -= 50
    
    c.save()
    return output_path

def test_font_preservation():
    """Test font preservation during text editing"""
    # Create test directory
    test_dir = "font_test_outputs"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create test PDF with different fonts
    test_pdf = os.path.join(test_dir, "multi_font_test.pdf")
    create_multi_font_pdf(test_pdf)
    print(f"\nCreated test PDF with multiple fonts: {test_pdf}")
    
    # Test editing text in different fonts
    test_cases = [
        ("Regular text in Helvetica", "Updated Helvetica Text"),
        ("Serif text in Times Roman", "Updated Times Roman Text"),
        ("Monospace text in Courier", "Updated Courier Text"),
        ("Bold text in Helvetica", "Updated Bold Text"),
        ("Italic text in Times", "Updated Italic Text")
    ]
    
    for i, (old_text, new_text) in enumerate(test_cases, 1):
        output_pdf = os.path.join(test_dir, f"edited_font_{i}.pdf")
        edit_pdf_text(test_pdf, output_pdf, 1, old_text, new_text)
        print(f"✓ Edited {old_text} -> {new_text}")
        print(f"  Output saved to: {output_pdf}")

if __name__ == "__main__":
    test_font_preservation()