# 📄 PDF-Pro

> A comprehensive, modern PDF toolkit for seamless document manipulation and conversion

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🌟 Overview

**PDF-Pro** is a powerful, user-friendly PDF toolkit designed for developers, professionals, and end-users who need robust document management capabilities. Whether you're converting office documents to PDF, merging multiple files, extracting data, or automating batch operations, PDF-Pro provides an elegant solution with both command-line and GUI interfaces.

Built with performance and usability in mind, PDF-Pro streamlines complex PDF operations into simple, intuitive workflows.

---

## ✨ Features

### 🔄 **Document Conversion**
- **DOCX to PDF**: Convert Microsoft Word documents with formatting preservation
- **TXT to PDF**: Transform plain text files into professionally formatted PDFs
- **PPTX to PDF**: Export PowerPoint presentations to PDF format
- **Image to PDF**: Batch convert images (JPG, PNG, BMP) to PDF documents
- **Excel to PDF**: Convert spreadsheets while maintaining layouts

### 🛠️ **PDF Manipulation**
- **Merge PDFs**: Combine multiple PDF files into a single document
- **Split PDFs**: Extract specific pages or split into multiple files
- **Rotate Pages**: Adjust page orientation (90°, 180°, 270°)
- **Reorder Pages**: Reorganize page sequences effortlessly
- **Delete Pages**: Remove unwanted pages from documents

### 📝 **Editing & Metadata**
- **Metadata Editor**: Update title, author, subject, keywords, and creation date
- **Watermarking**: Add text or image watermarks with customization
- **Encryption**: Password-protect PDFs with user and owner permissions
- **Compression**: Reduce file size while maintaining quality

### 🔍 **Data Extraction**
- **Text Extraction**: Extract plain text from PDF documents
- **Image Extraction**: Export embedded images from PDFs
- **Table Extraction**: Parse and export table data to CSV/Excel
- **Form Data**: Extract information from fillable PDF forms

### ⚡ **Advanced Features**
- **Batch Processing**: Process multiple files simultaneously
- **RESTful API**: Integrate PDF operations into your applications
- **Command-Line Interface**: Automate tasks with powerful CLI tools
- **Cross-Platform**: Works seamlessly on Windows, macOS, and Linux
- **Template Support**: Create PDFs from predefined templates

---

## 🚀 Tech Stack

### **Core Technologies**
- **Python 3.8+**: Primary programming language
- **PyPDF2**: PDF reading, writing, and manipulation
- **PDFMiner.six**: Advanced text and layout extraction
- **ReportLab**: PDF generation and rendering
- **python-docx**: DOCX file processing
- **Pillow (PIL)**: Image processing and conversion

### **Backend & API**
- **FastAPI**: High-performance REST API framework
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and settings management

### **Frontend & UI**
- **Electron**: Cross-platform desktop application framework
- **React**: Modern, responsive user interface
- **Bootstrap 5**: Professional UI components

### **Additional Libraries**
- **pdf2image**: PDF to image conversion
- **python-pptx**: PowerPoint file handling
- **openpyxl**: Excel file operations
- **cryptography**: Security and encryption features

---

## 📦 Installation

### **Option 1: Install via pip (Recommended)**

```bash
# Clone the repository
git clone https://github.com/adityapavan369/PDF-Pro.git
cd PDF-Pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install PDF-Pro
pip install -e .
```

### **Option 2: Using Docker**

```bash
# Build Docker image
docker build -t pdf-pro:latest .

# Run container
docker run -p 8000:8000 pdf-pro:latest
```

### **Option 3: Download Binaries**

Pre-built executables for Windows, macOS, and Linux are available on the [Releases](https://github.com/adityapavan369/PDF-Pro/releases) page.

### **System Requirements**
- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB available disk space

---

## 💻 Usage

### **Command-Line Interface**

#### Convert DOCX to PDF
```bash
pdf-pro convert --input document.docx --output document.pdf
```

#### Merge Multiple PDFs
```bash
pdf-pro merge --inputs file1.pdf file2.pdf file3.pdf --output merged.pdf
```

#### Split PDF
```bash
# Split by page range
pdf-pro split --input document.pdf --pages 1-5 --output section1.pdf

# Split into individual pages
pdf-pro split --input document.pdf --mode pages --output-dir ./pages/
```

#### Extract Text
```bash
pdf-pro extract text --input document.pdf --output extracted.txt
```

#### Add Watermark
```bash
pdf-pro watermark --input document.pdf --text "CONFIDENTIAL" --output watermarked.pdf
```

#### Batch Processing
```bash
pdf-pro batch convert --input-dir ./docs/ --format pdf --output-dir ./pdfs/
```

### **Python API Usage**

```python
from pdfpro import PDFConverter, PDFMerger, PDFEditor

# Convert DOCX to PDF
converter = PDFConverter()
converter.docx_to_pdf("input.docx", "output.pdf")

# Merge PDFs
merger = PDFMerger()
merger.add_files(["file1.pdf", "file2.pdf", "file3.pdf"])
merger.save("merged.pdf")

# Edit metadata
editor = PDFEditor("document.pdf")
editor.set_metadata(title="My Document", author="John Doe")
editor.save("updated.pdf")
```

### **REST API**

Start the API server:
```bash
pdf-pro serve --host 0.0.0.0 --port 8000
```

API endpoints:
```bash
# Convert document
curl -X POST http://localhost:8000/api/convert \
  -F "file=@document.docx" \
  -F "format=pdf"

# Merge PDFs
curl -X POST http://localhost:8000/api/merge \
  -F "files=@file1.pdf" \
  -F "files=@file2.pdf"

# Extract text
curl -X POST http://localhost:8000/api/extract/text \
  -F "file=@document.pdf"
```

### **Desktop GUI Application**

Launch the graphical interface:
```bash
pdf-pro gui
```

The GUI provides an intuitive drag-and-drop interface for all PDF operations.

---

## 📸 Screenshots

### Desktop Application Interface
*Coming Soon: Screenshots of the GUI application will be added here*

### API Documentation
*Interactive API docs available at `/docs` endpoint when running the server*

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### **Getting Started**

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Run tests**
   ```bash
   pytest tests/
   ```
5. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

### **Contribution Guidelines**

- Follow PEP 8 coding standards
- Write unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR
- Keep commits atomic and well-described

### **Development Setup**

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Check code style
flake8 pdfpro/
black pdfpro/

# Type checking
mypy pdfpro/
```

### **Report Issues**

Found a bug or have a feature request? Please [open an issue](https://github.com/adityapavan369/PDF-Pro/issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Aditya Pavan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 📞 Contact & Support

### **Maintainer**
- **Name**: Aditya Pavan
- **GitHub**: [@adityapavan369](https://github.com/adityapavan369)
- **Project Repository**: [PDF-Pro](https://github.com/adityapavan369/PDF-Pro)

### **Support Channels**
- **Issues**: [GitHub Issues](https://github.com/adityapavan369/PDF-Pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/adityapavan369/PDF-Pro/discussions)
- **Email**: Open an issue for direct contact

### **Documentation**
- **Wiki**: [Project Wiki](https://github.com/adityapavan369/PDF-Pro/wiki)
- **API Docs**: Available at `/docs` endpoint when running the server

---

## 🌟 Acknowledgments

- Built with Python and modern open-source libraries
- Inspired by the need for accessible, powerful PDF tools
- Special thanks to all contributors and users

---

## 🗺️ Roadmap

### **Upcoming Features**
- [ ] OCR support for scanned documents
- [ ] Digital signature integration
- [ ] Cloud storage integration (Google Drive, Dropbox)
- [ ] Advanced form creation tools
- [ ] Multi-language support
- [ ] Mobile application (iOS/Android)
- [ ] PDF comparison and diff tools
- [ ] Collaborative editing features

---

## ⭐ Show Your Support

If you find PDF-Pro helpful, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs
- 💡 Suggesting new features
- 🤝 Contributing code
- 📢 Sharing with others

---

<div align="center">

**Made with ❤️ by Aditya Pavan**

[⬆ Back to Top](#-pdf-pro)

</div>
