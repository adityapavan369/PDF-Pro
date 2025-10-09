"""PDF merging utilities"""
from PyPDF2 import PdfReader, PdfWriter


def merge_pdfs(input_paths, output_path):
    """Merge multiple PDF files into a single file
    
    Args:
        input_paths: List of paths to input PDF files
        output_path: Path to output merged PDF file
        
    Returns:
        str: Path to merged PDF file
    """
    try:
        writer = PdfWriter()
        
        for input_path in input_paths:
            reader = PdfReader(input_path)
            for page in reader.pages:
                writer.add_page(page)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error merging PDFs: {str(e)}")


def merge_pdfs_with_pages(pdf_configs, output_path):
    """Merge specific pages from multiple PDF files
    
    Args:
        pdf_configs: List of dicts with 'path' and 'pages' keys
                    e.g., [{'path': 'file1.pdf', 'pages': [1, 2]}, ...]
        output_path: Path to output merged PDF file
        
    Returns:
        str: Path to merged PDF file
    """
    try:
        writer = PdfWriter()
        
        for config in pdf_configs:
            reader = PdfReader(config['path'])
            pages = config.get('pages', list(range(1, len(reader.pages) + 1)))
            
            for page_num in pages:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error merging PDFs with pages: {str(e)}")


def append_pdfs(base_path, append_path, output_path):
    """Append one PDF to another
    
    Args:
        base_path: Path to base PDF file
        append_path: Path to PDF file to append
        output_path: Path to output PDF file
        
    Returns:
        str: Path to output PDF file
    """
    return merge_pdfs([base_path, append_path], output_path)
