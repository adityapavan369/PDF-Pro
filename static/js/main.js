// Main JavaScript for PDF-Pro

// File size validation
function validateFileSize(file, maxSizeMB = 16) {
    const maxSize = maxSizeMB * 1024 * 1024; // Convert to bytes
    if (file.size > maxSize) {
        alert(`File size exceeds ${maxSizeMB}MB limit`);
        return false;
    }
    return true;
}

// Add file size validation to all file inputs
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            let valid = true;
            
            for (let file of files) {
                if (!validateFileSize(file)) {
                    e.target.value = '';
                    valid = false;
                    break;
                }
            }
            
            if (valid && files.length > 0) {
                console.log(`Selected ${files.length} file(s)`);
            }
        });
    });
});

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
