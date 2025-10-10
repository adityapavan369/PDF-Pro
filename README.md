# PDF-Pro
A full-featured PDF toolkit for converting, editing, merging, and splitting PDF files. Built with Python Flask and integrates with advanced APIs. Supports DOCX to PDF conversion, image to PDF conversion, and various PDF manipulation operations.

## Features

- **Convert to PDF**
  - Convert images (PNG, JPG, JPEG) to PDF
  - Convert DOCX documents to PDF
  - Convert multiple images to a single PDF

- **Merge PDFs**
  - Combine multiple PDF files into one document
  - Maintain page order and quality

- **Split PDFs**
  - Split into individual pages
  - Split by number of pages per file
  - Extract specific page ranges

- **Edit PDFs**
  - Rotate pages (90°, 180°, 270°)
  - Add text watermarks
  - Extract specific pages
  - Delete pages

- **External API Integration**
  - OCR capabilities (with external API)
  - PDF compression (with external API)
  - PDF to images conversion (with external API)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/adityapavan369/PDF-Pro.git
cd PDF-Pro
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional):
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage

### Running the Application

Start the Flask development server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Web Interface

1. **Home Page**: Navigate to `http://localhost:5000` to see all available features
2. **Convert**: Upload images or DOCX files to convert them to PDF
3. **Merge**: Select multiple PDF files to merge them into one
4. **Split**: Upload a PDF and choose how to split it
5. **Edit**: Upload a PDF to rotate pages or add watermarks

### API Endpoints

The application also provides API endpoints:

- `GET /api/info` - Get API status and available features

## Configuration

Configuration options can be set in `config.py` or through environment variables:

- `SECRET_KEY`: Flask secret key for session management
- `MAX_CONTENT_LENGTH`: Maximum file upload size (default: 16MB)
- `UPLOAD_FOLDER`: Directory for uploaded files
- `OUTPUT_FOLDER`: Directory for processed files
- `PDF_API_KEY`: API key for external PDF processing service (optional)
- `PDF_API_URL`: URL for external PDF processing service (optional)

## Project Structure

```
PDF-Pro/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── converter.py       # PDF conversion utilities
│   ├── editor.py          # PDF editing utilities
│   ├── splitter.py        # PDF splitting utilities
│   ├── merger.py          # PDF merging utilities
│   ├── api_integration.py # External API integration
│   └── validators.py      # File validation utilities
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── convert.html
│   ├── merge.html
│   ├── split.html
│   ├── edit.html
│   └── 404.html
└── static/                # Static files
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Dependencies

- Flask 3.0.0 - Web framework
- PyPDF2 3.0.1 - PDF manipulation
- ReportLab 4.0.7 - PDF generation
- Pillow 10.1.0 - Image processing
- python-docx 1.1.0 - DOCX file handling
- docx2pdf 0.1.8 - DOCX to PDF conversion
- requests 2.31.0 - HTTP library for API calls
- python-dotenv 1.0.0 - Environment variable management

## Notes

- Maximum file size is 16MB by default
- DOCX to PDF conversion works best on Windows/MacOS with Microsoft Word installed
- On Linux, a fallback method using python-docx and reportlab is used for DOCX conversion
- External API features require valid API credentials

## Host setup for high-fidelity conversions (LibreOffice + visual diffs)

To enable the best DOCX → PDF fidelity on Linux and the visual-diff feature, install LibreOffice and the Python imaging libraries on the host or CI runner. A helper script is provided at `scripts/install_host_deps.sh`.

Run on an Ubuntu host (requires sudo):

```bash
bash scripts/install_host_deps.sh
```

This installs LibreOffice, poppler utilities, and required Python packages including `pymupdf` and `Pillow`.

## Continuous Integration (Acceptance tests)

A GitHub Actions workflow is included at `.github/workflows/acceptance.yml`. It runs on pushes and pull requests to `main`, installs LibreOffice and Python dependencies on an `ubuntu-latest` runner, runs the test script, and uploads the `outputs/` folder as an artifact for inspection.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Adityapavanarvapalli