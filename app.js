class PDFApp {
    constructor() {
        this.currentFile = null;
        this.currentPage = 0;
        this.totalPages = 0;
        this.uploadedFiles = [];
        this.isSelecting = false;
        this.selectionStart = null;
        this.selectionEnd = null;
        this.currentTool = null;
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File upload
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Tool buttons
        document.getElementById('addTextBtn').addEventListener('click', () => this.activateTool('text'));
        document.getElementById('highlightBtn').addEventListener('click', () => this.activateTool('highlight'));
        document.getElementById('addNoteBtn').addEventListener('click', () => this.activateTool('note'));
        document.getElementById('rotateBtn').addEventListener('click', () => this.rotatePage());
        document.getElementById('cropBtn').addEventListener('click', () => this.activateTool('crop'));
        document.getElementById('deletePageBtn').addEventListener('click', () => this.deletePage());
        document.getElementById('mergeBtn').addEventListener('click', () => this.showMergeModal());
        document.getElementById('splitBtn').addEventListener('click', () => this.showSplitModal());
        document.getElementById('downloadBtn').addEventListener('click', () => this.downloadFile());
        
        // Page navigation
        document.getElementById('prevPageBtn').addEventListener('click', () => this.previousPage());
        document.getElementById('nextPageBtn').addEventListener('click', () => this.nextPage());
        
        // Modal controls
        this.initializeModals();
        
        // PDF viewer interactions
        document.getElementById('pageContainer').addEventListener('click', (e) => this.handlePageClick(e));
        document.getElementById('pageContainer').addEventListener('mousedown', (e) => this.handleMouseDown(e));
        document.getElementById('pageContainer').addEventListener('mousemove', (e) => this.handleMouseMove(e));
        document.getElementById('pageContainer').addEventListener('mouseup', (e) => this.handleMouseUp(e));
    }

    initializeModals() {
        // Close modal functionality
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', (e) => {
                e.target.closest('.modal').style.display = 'none';
            });
        });
        
        // Click outside modal to close
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
        
        // Modal confirm buttons
        document.getElementById('addTextConfirm').addEventListener('click', () => this.confirmAddText());
        document.getElementById('addNoteConfirm').addEventListener('click', () => this.confirmAddNote());
        document.getElementById('mergeConfirm').addEventListener('click', () => this.confirmMerge());
        document.getElementById('splitConfirm').addEventListener('click', () => this.confirmSplit());
    }

    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        const files = e.dataTransfer.files;
        this.processFiles(files);
    }

    handleFileSelect(e) {
        const files = e.target.files;
        this.processFiles(files);
    }

    async processFiles(files) {
        for (let file of files) {
            await this.uploadFile(file);
        }
    }

    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        this.showLoading();
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.addFileToList(file.name, result.filename, result.download_url);
                this.uploadedFiles.push(result.filename);
                this.showNotification('File converted successfully!', 'success');
            } else {
                this.showNotification(result.error || 'Upload failed', 'error');
            }
        } catch (error) {
            this.showNotification('Upload failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    addFileToList(originalName, convertedName, downloadUrl) {
        const fileList = document.getElementById('fileList');
        
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item fade-in';
        fileItem.innerHTML = `
            <div class="file-info">
                <i class="fas fa-file-pdf file-icon"></i>
                <div class="file-details">
                    <h4>${originalName}</h4>
                    <p>Converted to PDF</p>
                </div>
            </div>
            <div class="file-actions">
                <button class="btn btn-primary" onclick="app.editFile('${convertedName}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <button class="btn btn-success" onclick="app.downloadFile('${convertedName}')">
                    <i class="fas fa-download"></i> Download
                </button>
            </div>
        `;
        
        fileList.appendChild(fileItem);
    }

    async editFile(filename) {
        this.currentFile = filename;
        
        try {
            // Get PDF info
            const response = await fetch(`/pdf-info/${filename}`);
            const info = await response.json();
            
            if (response.ok) {
                this.totalPages = info.pages;
                this.currentPage = 0;
                
                document.getElementById('editorSection').style.display = 'block';
                document.getElementById('editorSection').scrollIntoView({ behavior: 'smooth' });
                
                await this.loadPage(0);
                this.updatePageNavigation();
            } else {
                this.showNotification(info.error || 'Failed to load PDF info', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to load PDF: ' + error.message, 'error');
        }
    }

    async loadPage(pageNum) {
        if (!this.currentFile) return;
        
        try {
            const response = await fetch(`/api/pdf/page-image/${this.currentFile}/${pageNum}`);
            const result = await response.json();
            
            if (response.ok) {
                const pageContainer = document.getElementById('pageContainer');
                pageContainer.innerHTML = `<img src="${result.image}" alt="Page ${pageNum + 1}">`;
            } else {
                this.showNotification(result.error || 'Failed to load page', 'error');
            }
        } catch (error) {
            this.showNotification('Failed to load page: ' + error.message, 'error');
        }
    }

    updatePageNavigation() {
        document.getElementById('pageInfo').textContent = `Page ${this.currentPage + 1} of ${this.totalPages}`;
        document.getElementById('prevPageBtn').disabled = this.currentPage === 0;
        document.getElementById('nextPageBtn').disabled = this.currentPage === this.totalPages - 1;
    }

    previousPage() {
        if (this.currentPage > 0) {
            this.currentPage--;
            this.loadPage(this.currentPage);
            this.updatePageNavigation();
        }
    }

    nextPage() {
        if (this.currentPage < this.totalPages - 1) {
            this.currentPage++;
            this.loadPage(this.currentPage);
            this.updatePageNavigation();
        }
    }

    activateTool(tool) {
        // Deactivate all tools
        document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
        
        // Activate selected tool
        this.currentTool = tool;
        
        switch (tool) {
            case 'text':
                document.getElementById('addTextBtn').classList.add('active');
                break;
            case 'highlight':
                document.getElementById('highlightBtn').classList.add('active');
                break;
            case 'note':
                document.getElementById('addNoteBtn').classList.add('active');
                break;
            case 'crop':
                document.getElementById('cropBtn').classList.add('active');
                break;
        }
        
        this.showNotification(`${tool.charAt(0).toUpperCase() + tool.slice(1)} tool activated. Click on the PDF to use.`, 'info');
    }

    handlePageClick(e) {
        if (!this.currentTool || !this.currentFile) return;
        
        const rect = e.target.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Convert to PDF coordinates (approximate)
        const pdfX = (x / rect.width) * 595; // A4 width in points
        const pdfY = (y / rect.height) * 842; // A4 height in points
        
        switch (this.currentTool) {
            case 'text':
                this.showTextModal(pdfX, pdfY);
                break;
            case 'note':
                this.showNoteModal(pdfX, pdfY);
                break;
        }
    }

    handleMouseDown(e) {
        if (this.currentTool === 'highlight' || this.currentTool === 'crop') {
            this.isSelecting = true;
            const rect = e.target.getBoundingClientRect();
            this.selectionStart = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
        }
    }

    handleMouseMove(e) {
        if (this.isSelecting && this.selectionStart) {
            const rect = e.target.getBoundingClientRect();
            this.selectionEnd = {
                x: e.clientX - rect.left,
                y: e.clientY - rect.top
            };
            
            this.updateSelectionBox();
        }
    }

    handleMouseUp(e) {
        if (this.isSelecting && this.selectionStart && this.selectionEnd) {
            const rect = e.target.getBoundingClientRect();
            
            // Convert to PDF coordinates
            const x1 = (this.selectionStart.x / rect.width) * 595;
            const y1 = (this.selectionStart.y / rect.height) * 842;
            const x2 = (this.selectionEnd.x / rect.width) * 595;
            const y2 = (this.selectionEnd.y / rect.height) * 842;
            
            if (this.currentTool === 'highlight') {
                this.addHighlight(Math.min(x1, x2), Math.min(y1, y2), Math.max(x1, x2), Math.max(y1, y2));
            } else if (this.currentTool === 'crop') {
                this.cropPage(Math.min(x1, x2), Math.min(y1, y2), Math.max(x1, x2), Math.max(y1, y2));
            }
        }
        
        this.isSelecting = false;
        this.selectionStart = null;
        this.selectionEnd = null;
        this.removeSelectionBox();
    }

    updateSelectionBox() {
        this.removeSelectionBox();
        
        const pageContainer = document.getElementById('pageContainer');
        const selectionBox = document.createElement('div');
        selectionBox.className = 'selection-box';
        selectionBox.id = 'selectionBox';
        
        const left = Math.min(this.selectionStart.x, this.selectionEnd.x);
        const top = Math.min(this.selectionStart.y, this.selectionEnd.y);
        const width = Math.abs(this.selectionEnd.x - this.selectionStart.x);
        const height = Math.abs(this.selectionEnd.y - this.selectionStart.y);
        
        selectionBox.style.left = left + 'px';
        selectionBox.style.top = top + 'px';
        selectionBox.style.width = width + 'px';
        selectionBox.style.height = height + 'px';
        
        pageContainer.appendChild(selectionBox);
    }

    removeSelectionBox() {
        const existingBox = document.getElementById('selectionBox');
        if (existingBox) {
            existingBox.remove();
        }
    }

    showTextModal(x, y) {
        this.pendingAction = { type: 'text', x, y };
        document.getElementById('textModal').style.display = 'block';
        document.getElementById('textInput').focus();
    }

    showNoteModal(x, y) {
        this.pendingAction = { type: 'note', x, y };
        document.getElementById('noteModal').style.display = 'block';
        document.getElementById('noteInput').focus();
    }

    async confirmAddText() {
        const text = document.getElementById('textInput').value;
        const fontSize = document.getElementById('fontSize').value;
        
        if (!text.trim()) {
            this.showNotification('Please enter some text', 'warning');
            return;
        }
        
        await this.addText(text, this.pendingAction.x, this.pendingAction.y, parseInt(fontSize));
        document.getElementById('textModal').style.display = 'none';
        document.getElementById('textInput').value = '';
    }

    async confirmAddNote() {
        const content = document.getElementById('noteInput').value;
        
        if (!content.trim()) {
            this.showNotification('Please enter note content', 'warning');
            return;
        }
        
        await this.addNote(content, this.pendingAction.x, this.pendingAction.y);
        document.getElementById('noteModal').style.display = 'none';
        document.getElementById('noteInput').value = '';
    }

    async addText(text, x, y, fontSize = 12) {
        await this.performEdit('/api/pdf/edit/add-text', {
            filename: this.currentFile,
            page_num: this.currentPage,
            text: text,
            x: x,
            y: y,
            font_size: fontSize
        });
    }

    async addHighlight(x1, y1, x2, y2) {
        await this.performEdit('/api/pdf/edit/highlight', {
            filename: this.currentFile,
            page_num: this.currentPage,
            x1: x1,
            y1: y1,
            x2: x2,
            y2: y2
        });
    }

    async addNote(content, x, y) {
        await this.performEdit('/api/pdf/edit/note', {
            filename: this.currentFile,
            page_num: this.currentPage,
            content: content,
            x: x,
            y: y
        });
    }

    async rotatePage() {
        await this.performEdit('/api/pdf/edit/rotate', {
            filename: this.currentFile,
            page_num: this.currentPage,
            angle: 90
        });
    }

    async cropPage(x1, y1, x2, y2) {
        await this.performEdit('/api/pdf/edit/crop', {
            filename: this.currentFile,
            page_num: this.currentPage,
            x1: x1,
            y1: y1,
            x2: x2,
            y2: y2
        });
    }

    async deletePage() {
        if (confirm('Are you sure you want to delete this page?')) {
            await this.performEdit('/api/pdf/edit/delete-page', {
                filename: this.currentFile,
                page_num: this.currentPage
            });
            
            // Adjust current page if necessary
            if (this.currentPage >= this.totalPages - 1 && this.currentPage > 0) {
                this.currentPage--;
            }
            this.totalPages--;
        }
    }

    async performEdit(endpoint, data) {
        this.showLoading();
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.currentFile = result.filename;
                await this.loadPage(this.currentPage);
                this.updatePageNavigation();
                this.showNotification(result.message, 'success');
                this.currentTool = null;
                document.querySelectorAll('.tool-btn').forEach(btn => btn.classList.remove('active'));
            } else {
                this.showNotification(result.error || 'Operation failed', 'error');
            }
        } catch (error) {
            this.showNotification('Operation failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showMergeModal() {
        const modal = document.getElementById('mergeModal');
        const fileList = document.getElementById('mergeFileList');
        
        fileList.innerHTML = '';
        this.uploadedFiles.forEach(filename => {
            const item = document.createElement('div');
            item.innerHTML = `
                <label>
                    <input type="checkbox" value="${filename}"> ${filename}
                </label>
            `;
            fileList.appendChild(item);
        });
        
        modal.style.display = 'block';
    }

    async confirmMerge() {
        const checkboxes = document.querySelectorAll('#mergeFileList input[type="checkbox"]:checked');
        const filenames = Array.from(checkboxes).map(cb => cb.value);
        
        if (filenames.length < 2) {
            this.showNotification('Please select at least 2 files to merge', 'warning');
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/pdf/merge', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ filenames: filenames })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.uploadedFiles.push(result.filename);
                this.addFileToList('Merged PDF', result.filename, result.download_url);
                this.showNotification(result.message, 'success');
                document.getElementById('mergeModal').style.display = 'none';
            } else {
                this.showNotification(result.error || 'Merge failed', 'error');
            }
        } catch (error) {
            this.showNotification('Merge failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    showSplitModal() {
        if (!this.currentFile) {
            this.showNotification('Please select a PDF to split', 'warning');
            return;
        }
        
        document.getElementById('splitModal').style.display = 'block';
        document.getElementById('pageRanges').focus();
    }

    async confirmSplit() {
        const rangesText = document.getElementById('pageRanges').value;
        
        if (!rangesText.trim()) {
            this.showNotification('Please enter page ranges', 'warning');
            return;
        }
        
        // Parse page ranges (e.g., "1-3, 5-7" -> [[0,2], [4,6]])
        const ranges = rangesText.split(',').map(range => {
            const [start, end] = range.trim().split('-').map(n => parseInt(n) - 1);
            return [start, end || start];
        });
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/pdf/split', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: this.currentFile,
                    page_ranges: ranges
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showNotification(result.message, 'success');
                document.getElementById('splitModal').style.display = 'none';
                document.getElementById('pageRanges').value = '';
                
                // Add split files to the list
                result.files.forEach((filename, index) => {
                    this.addFileToList(`Split ${index + 1}`, filename, result.download_urls[index]);
                });
            } else {
                this.showNotification(result.error || 'Split failed', 'error');
            }
        } catch (error) {
            this.showNotification('Split failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    downloadFile(filename = null) {
        const file = filename || this.currentFile;
        if (file) {
            window.open(`/download/${file}`, '_blank');
        } else {
            this.showNotification('No file selected for download', 'warning');
        }
    }

    showLoading() {
        document.getElementById('loadingOverlay').style.display = 'flex';
    }

    hideLoading() {
        document.getElementById('loadingOverlay').style.display = 'none';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 600;
            z-index: 10000;
            max-width: 300px;
            animation: slideIn 0.3s ease;
        `;
        
        // Set background color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        notification.style.backgroundColor = colors[type] || colors.info;
        
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 5000);
    }
}

// Initialize the app when the page loads
const app = new PDFApp();

