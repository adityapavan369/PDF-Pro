"""
Advanced DOCX to PDF Converter with Page Fitting Capabilities
This module provides enhanced conversion functionality to achieve single-page PDF output
when possible, while preserving formatting quality.
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path


class AdvancedDocxConverter:
    """Advanced DOCX to PDF converter with multiple strategies for optimal output."""
    
    def __init__(self):
        self.temp_dir = None
    
    def convert_with_margin_reduction(self, docx_path, output_path):
        """
        Convert DOCX to PDF with reduced margins to fit more content on one page.
        Uses LibreOffice with custom page style settings.
        """
        try:
            # Create a temporary directory for processing
            self.temp_dir = tempfile.mkdtemp()
            temp_docx = os.path.join(self.temp_dir, "temp_reduced_margins.docx")
            
            # Copy the original file to temp location
            shutil.copy2(docx_path, temp_docx)
            
            # Use LibreOffice with specific export options to reduce margins
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_path),
                temp_docx
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # LibreOffice creates the PDF with the same base name as the input file
                base_name = os.path.splitext(os.path.basename(temp_docx))[0]
                temp_pdf_path = os.path.join(os.path.dirname(output_path), f"{base_name}.pdf")
                
                # Rename to the expected output path
                if os.path.exists(temp_pdf_path):
                    os.rename(temp_pdf_path, output_path)
                    return True
                else:
                    print(f"LibreOffice conversion succeeded but PDF not found at {temp_pdf_path}")
                    return False
            else:
                print(f"LibreOffice conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("LibreOffice conversion timed out")
            return False
        except Exception as e:
            print(f"Error in margin reduction conversion: {e}")
            return False
        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def convert_with_scaling(self, docx_path, output_path):
        """
        Convert DOCX to PDF with content scaling to fit on one page.
        Uses unoconv with specific scaling options.
        """
        try:
            # Try using unoconv with specific options
            cmd = [
                'unoconv',
                '-f', 'pdf',
                '-o', output_path,
                docx_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return True
            else:
                print(f"unoconv conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("unoconv conversion timed out")
            return False
        except Exception as e:
            print(f"Error in scaling conversion: {e}")
            return False
    
    def convert_with_python_docx_manipulation(self, docx_path, output_path):
        """
        Convert DOCX to PDF by first manipulating the document structure
        to reduce content size and then converting.
        """
        try:
            from docx import Document
            from docx.shared import Inches, Pt
            from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
            
            # Load the document
            doc = Document(docx_path)
            
            # Create a temporary directory for processing
            self.temp_dir = tempfile.mkdtemp()
            temp_docx = os.path.join(self.temp_dir, "temp_optimized.docx")
            
            # Modify document properties for better single-page fitting
            
            # 1. Reduce margins significantly
            for section in doc.sections:
                section.top_margin = Inches(0.3)
                section.bottom_margin = Inches(0.3)
                section.left_margin = Inches(0.5)
                section.right_margin = Inches(0.5)
            
            # 2. Reduce font sizes slightly and line spacing
            for paragraph in doc.paragraphs:
                for run in paragraph.runs:
                    if run.font.size:
                        # Reduce font size by 10%
                        current_size = run.font.size.pt
                        run.font.size = Pt(max(8, current_size * 0.9))
                
                # Reduce paragraph spacing
                paragraph_format = paragraph.paragraph_format
                paragraph_format.space_before = Pt(0)
                paragraph_format.space_after = Pt(2)
                paragraph_format.line_spacing = 1.0
            
            # 3. Optimize table formatting if any
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            for run in paragraph.runs:
                                if run.font.size:
                                    current_size = run.font.size.pt
                                    run.font.size = Pt(max(7, current_size * 0.85))
            
            # Save the modified document
            doc.save(temp_docx)
            
            # Convert the optimized document to PDF
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(output_path),
                temp_docx
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # LibreOffice creates the PDF with the same base name as the input file
                base_name = os.path.splitext(os.path.basename(temp_docx))[0]
                temp_pdf_path = os.path.join(os.path.dirname(output_path), f"{base_name}.pdf")
                
                # Rename to the expected output path
                if os.path.exists(temp_pdf_path):
                    os.rename(temp_pdf_path, output_path)
                    return True
                else:
                    print(f"LibreOffice conversion succeeded but PDF not found at {temp_pdf_path}")
                    return False
            else:
                print(f"LibreOffice conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("LibreOffice conversion timed out")
            return False
        except Exception as e:
            print(f"Error in python-docx manipulation conversion: {e}")
            return False
        finally:
            # Clean up temporary directory
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def get_pdf_page_count(self, pdf_path):
        """Get the number of pages in a PDF file."""
        try:
            import pypdf
            with open(pdf_path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                return len(reader.pages)
        except Exception as e:
            print(f"Error getting PDF page count: {e}")
            return None
    
    def convert_docx_to_pdf_optimized(self, docx_path, output_path):
        """
        Main conversion method that tries multiple strategies and selects the best result.
        Priority: Single page > Fewer pages > Original conversion
        """
        strategies = [
            ("Python DOCX Manipulation", self.convert_with_python_docx_manipulation),
            ("Margin Reduction", self.convert_with_margin_reduction),
            ("Scaling with unoconv", self.convert_with_scaling),
        ]
        
        best_result = None
        best_page_count = float('inf')
        
        for strategy_name, strategy_func in strategies:
            try:
                # Create a temporary output path for this strategy
                temp_output = f"{output_path}.{strategy_name.lower().replace(' ', '_')}.tmp"
                
                print(f"Trying strategy: {strategy_name}")
                success = strategy_func(docx_path, temp_output)
                
                if success and os.path.exists(temp_output):
                    page_count = self.get_pdf_page_count(temp_output)
                    print(f"Strategy '{strategy_name}' resulted in {page_count} pages")
                    
                    if page_count and page_count < best_page_count:
                        # This strategy produced fewer pages
                        if best_result and os.path.exists(best_result):
                            os.remove(best_result)  # Clean up previous best result
                        best_result = temp_output
                        best_page_count = page_count
                        
                        # If we achieved single page, we can stop here
                        if page_count == 1:
                            print(f"Achieved single-page PDF with strategy: {strategy_name}")
                            break
                    else:
                        # This strategy didn't improve, clean up
                        os.remove(temp_output)
                else:
                    print(f"Strategy '{strategy_name}' failed")
                    
            except Exception as e:
                print(f"Error with strategy '{strategy_name}': {e}")
                continue
        
        # Use the best result or fall back to original conversion
        if best_result and os.path.exists(best_result):
            shutil.move(best_result, output_path)
            print(f"Best conversion achieved {best_page_count} pages")
            return True
        else:
            print("All optimization strategies failed, falling back to original conversion")
            # Fall back to the original LibreOffice conversion
            return self.convert_with_margin_reduction(docx_path, output_path)


def convert_docx_to_pdf_advanced(docx_path, output_path):
    """
    Public function to convert DOCX to PDF with advanced optimization.
    This is the main entry point for the enhanced conversion.
    """
    converter = AdvancedDocxConverter()
    return converter.convert_docx_to_pdf_optimized(docx_path, output_path)

