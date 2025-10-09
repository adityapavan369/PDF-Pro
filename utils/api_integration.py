"""External API integration for advanced PDF operations"""
import requests
import os


class PDFAPIClient:
    """Client for external PDF processing API"""
    
    def __init__(self, api_key, api_url):
        """Initialize API client
        
        Args:
            api_key: API authentication key
            api_url: Base URL for the API
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
    
    def ocr_pdf(self, pdf_path, output_path):
        """Perform OCR on a PDF using external API
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to save OCR result
            
        Returns:
            dict: OCR results
        """
        try:
            # This is a template - actual implementation depends on the API
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{self.api_url}/ocr",
                    headers={'x-api-key': self.api_key},
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                
                # Save result if output path provided
                if output_path:
                    with open(output_path, 'w') as f:
                        f.write(result.get('text', ''))
                
                return result
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def compress_pdf(self, pdf_path, output_path, compression_level='medium'):
        """Compress a PDF using external API
        
        Args:
            pdf_path: Path to input PDF file
            output_path: Path to save compressed PDF
            compression_level: Compression level (low, medium, high)
            
        Returns:
            str: Path to compressed PDF
        """
        try:
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                data = {'compression_level': compression_level}
                response = requests.post(
                    f"{self.api_url}/compress",
                    headers={'x-api-key': self.api_key},
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return output_path
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def pdf_to_images(self, pdf_path, output_dir, format='png', dpi=150):
        """Convert PDF pages to images using external API
        
        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory to save images
            format: Image format (png, jpg)
            dpi: Resolution in DPI
            
        Returns:
            list: Paths to generated images
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with open(pdf_path, 'rb') as f:
                files = {'file': f}
                data = {'format': format, 'dpi': dpi}
                response = requests.post(
                    f"{self.api_url}/pdf-to-images",
                    headers={'x-api-key': self.api_key},
                    files=files,
                    data=data,
                    timeout=120
                )
            
            if response.status_code == 200:
                result = response.json()
                image_urls = result.get('images', [])
                
                # Download images
                image_paths = []
                for i, url in enumerate(image_urls):
                    img_response = requests.get(url)
                    if img_response.status_code == 200:
                        img_path = os.path.join(output_dir, f"page_{i+1}.{format}")
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        image_paths.append(img_path)
                
                return image_paths
            else:
                raise Exception(f"API error: {response.status_code} - {response.text}")
        
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")


def get_api_client(api_key=None, api_url=None):
    """Get an instance of the API client
    
    Args:
        api_key: API key (uses env variable if not provided)
        api_url: API URL (uses env variable if not provided)
        
    Returns:
        PDFAPIClient: Instance of API client or None if no credentials
    """
    api_key = api_key or os.environ.get('PDF_API_KEY')
    api_url = api_url or os.environ.get('PDF_API_URL', 'https://api.pdf.co/v1')
    
    if api_key:
        return PDFAPIClient(api_key, api_url)
    return None
