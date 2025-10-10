"""PDF splitting utilities"""
import os
from PyPDF2 import PdfReader, PdfWriter


def split_pdf_by_page_numbers(input_path, output_path, page_numbers):
    """Split a PDF by extracting specific pages
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to save the output PDF file
        page_numbers: List of page numbers to extract (1-based indexing)
        
    Returns:
        str: Path to output PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Convert 1-based page numbers to 0-based indices
        for page_num in sorted(page_numbers):
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error splitting PDF: {str(e)}")

def split_pdf_into_multiple(input_path, output_dir, page_ranges):
    """Split a PDF into multiple files based on page ranges
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save the output PDF files
        page_ranges: List of tuples containing (start_page, end_page) for each split
        
    Returns:
        list: List of paths to split PDF files
    """
    try:
        reader = PdfReader(input_path)
        output_files = []
        
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        for idx, (start, end) in enumerate(page_ranges, 1):
            if 1 <= start <= len(reader.pages) and 1 <= end <= len(reader.pages):
                writer = PdfWriter()
                
                # Convert 1-based page numbers to 0-based indices
                for page_num in range(start - 1, end):
                    writer.add_page(reader.pages[page_num])
                
                output_path = os.path.join(output_dir, f"{base_name}_split{idx}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                
                output_files.append(output_path)
        
        return output_files
    except Exception as e:
        raise Exception(f"Error splitting PDF: {str(e)}")

def split_pdf_by_pages(input_path, output_dir, pages_per_file=1):
    """Split a PDF into multiple files
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save split PDF files
        pages_per_file: Number of pages per output file
        
    Returns:
        list: List of paths to split PDF files
    """
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        output_files = []
        
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        file_num = 1
        for i in range(0, total_pages, pages_per_file):
            writer = PdfWriter()
            
            # Add pages to this split
            for j in range(i, min(i + pages_per_file, total_pages)):
                writer.add_page(reader.pages[j])
            
            # Save split file
            output_path = os.path.join(output_dir, f"{base_name}_part{file_num}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            output_files.append(output_path)
            file_num += 1
        
        return output_files
    except Exception as e:
        raise Exception(f"Error splitting PDF: {str(e)}")


def split_pdf_by_range(input_path, output_path, start_page, end_page):
    """Split a PDF by extracting a range of pages
    
    Args:
        input_path: Path to input PDF file
        output_path: Path to output PDF file
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (1-indexed)
        
    Returns:
        str: Path to split PDF file
    """
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # Convert to 0-indexed and validate range
        start_idx = max(0, start_page - 1)
        end_idx = min(len(reader.pages), end_page)
        
        for i in range(start_idx, end_idx):
            writer.add_page(reader.pages[i])
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return output_path
    except Exception as e:
        raise Exception(f"Error splitting PDF by range: {str(e)}")


def split_pdf_into_single_pages(input_path, output_dir):
    """Split a PDF into individual page files
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save individual page files
        
    Returns:
        list: List of paths to individual page files
    """
    return split_pdf_by_pages(input_path, output_dir, pages_per_file=1)
