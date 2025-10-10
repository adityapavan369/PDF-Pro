"""PDF conversion utilities

This module provides higher-fidelity conversion helpers:
- Images: use Pillow's built-in PDF saving which preserves DPI and embedding.
- DOCX: on Linux try LibreOffice/soffice headless (best fidelity). Fall back to
  docx2pdf on Windows/macOS or a ReportLab-based simple fallback when
  necessary.
"""
import os
import subprocess
import shutil
from PIL import Image
import platform

# Try to use advanced converter if present in workspace
try:
    from advanced_docx_converter import convert_docx_to_pdf_advanced
    _HAS_ADVANCED_CONVERTER = True
except Exception:
    _HAS_ADVANCED_CONVERTER = False


def image_to_pdf(image_path, output_path):
    """Convert an image file to PDF using Pillow's PDF writer.

    This preserves image DPI and results in an embedded image PDF page.
    """
    try:
        img = Image.open(image_path)

        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            img = img.convert('RGB')

        # Attempt to preserve DPI if present
        dpi = img.info.get('dpi', (72, 72))

        # For multi-frame images (animated GIF), only the first frame is used
        if getattr(img, 'is_animated', False):
            img = Image.new('RGB', img.size)

        # Pillow can save directly to PDF
        img.save(output_path, "PDF", resolution=dpi[0])
        # write engine metadata
        try:
            with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                ef.write('pillow')
        except Exception:
            pass
        return output_path
    except Exception as e:
        raise Exception(f"Error converting image to PDF: {str(e)}")


def images_to_pdf(image_paths, output_path):
    """Convert multiple images to a single PDF using Pillow.

    All images are normalized to RGB and saved as a multi-page PDF.
    """
    try:
        pil_images = []
        for p in image_paths:
            img = Image.open(p)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            pil_images.append(img)

        if not pil_images:
            raise Exception('No images provided')

        first, rest = pil_images[0], pil_images[1:]
        first.save(output_path, "PDF", resolution=first.info.get('dpi', (72, 72))[0], save_all=True, append_images=rest)
        # write engine metadata
        try:
            with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                ef.write('pillow')
        except Exception:
            pass
        # close images
        for im in pil_images:
            try:
                im.close()
            except Exception:
                pass
        return output_path
    except Exception as e:
        raise Exception(f"Error converting images to PDF: {str(e)}")


def _soffice_available():
    """Return True if soffice (LibreOffice) is available on PATH."""
    return shutil.which('soffice') is not None


def docx_to_pdf(docx_path, output_path):
    """Convert a DOCX file to PDF.

    Strategy:
    - On Windows/macOS: try docx2pdf (uses MS Word for best fidelity).
    - On Linux: try LibreOffice/soffice headless for best fidelity.
    - Fallback: a minimal python-docx -> ReportLab fallback (low fidelity).

    Note: LibreOffice must be installed for best results on Linux.
    """
    try:
        system = platform.system()

        # If an advanced converter is available in the repo, prefer it first.
        if _HAS_ADVANCED_CONVERTER:
            try:
                success = convert_docx_to_pdf_advanced(docx_path, output_path)
                if success:
                    # write engine metadata
                    try:
                        with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                            ef.write('advanced')
                    except Exception:
                        pass
                    return output_path
            except Exception:
                # fallthrough to other strategies
                pass

        # Windows/macOS - prefer docx2pdf if available
        if system in ('Windows', 'Darwin'):
            try:
                from docx2pdf import convert
                convert(docx_path, output_path)
                # write engine metadata
                try:
                    with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                        ef.write('docx2pdf')
                except Exception:
                    pass
                return output_path
            except Exception:
                # Fall through to fallback
                pass

        # On Linux, prefer using LibreOffice (soffice) headless
        if system == 'Linux' and _soffice_available():
            # soffice will write to the specified output directory
            out_dir = os.path.dirname(os.path.abspath(output_path)) or '.'
            cmd = [
                'soffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', out_dir,
                docx_path,
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if proc.returncode != 0:
                raise Exception(f"soffice failed: {proc.stderr.decode('utf-8', errors='ignore')}")

            # LibreOffice names the output file with same basename but .pdf
            generated = os.path.join(out_dir, os.path.splitext(os.path.basename(docx_path))[0] + '.pdf')
            if not os.path.exists(generated):
                raise Exception('LibreOffice reported success but output PDF not found')

            # Move/rename to desired output_path
            if os.path.abspath(generated) != os.path.abspath(output_path):
                os.replace(generated, output_path)

            # write engine metadata
            try:
                with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                    ef.write('soffice')
            except Exception:
                pass

            return output_path

        # Last resort fallback: very simple conversion using python-docx -> ReportLab
        from docx import Document
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

        doc = Document(docx_path)
        from reportlab.lib.pagesizes import A4
        pdf_doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for para in doc.paragraphs:
            if para.text.strip():
                p = Paragraph(para.text, styles['Normal'])
                story.append(p)
                story.append(Spacer(1, 12))

        pdf_doc.build(story)
        # write engine metadata for fallback
        try:
            with open(f"{output_path}.engine", 'w', encoding='utf-8') as ef:
                ef.write('fallback')
        except Exception:
            pass
        return output_path
    except Exception as e:
        raise Exception(f"Error converting DOCX to PDF: {str(e)}")
