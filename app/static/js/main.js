// Main JavaScript for Form Validation App

document.addEventListener('DOMContentLoaded', function() {
    // File input preview functionality
    const fileInput = document.getElementById('form_file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                const fileName = e.target.files[0].name;
                // Update file input text
                const fileInputLabel = document.querySelector('.form-text');
                fileInputLabel.textContent = `Selected file: ${fileName}`;
                
                // Create a badge for the selected file
                const filePreview = document.createElement('div');
                filePreview.className = 'alert alert-info mt-2';
                filePreview.innerHTML = `
                    <strong>File selected:</strong> ${fileName}
                    <button type="button" class="btn-close float-end" aria-label="Close"></button>
                `;
                
                // Remove any existing file preview
                const existingPreview = document.querySelector('.alert-info');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                // Add new preview after the file input
                fileInput.parentNode.appendChild(filePreview);
                
                // Add clear functionality
                const clearButton = filePreview.querySelector('.btn-close');
                clearButton.addEventListener('click', function() {
                    fileInput.value = '';
                    filePreview.remove();
                    fileInputLabel.textContent = 'Upload your form file or use test mode below';
                });
            }
        });
    }
    
    // Toggle between test mode and file upload
    const testModeCheckbox = document.getElementById('test_mode');
    if (testModeCheckbox) {
        testModeCheckbox.addEventListener('change', function() {
            const fileInputContainer = document.getElementById('form_file').parentNode;
            
            if (this.checked) {
                fileInputContainer.classList.add('disabled');
                fileInputContainer.querySelector('.form-text').textContent = 'File upload disabled in test mode';
            } else {
                fileInputContainer.classList.remove('disabled');
                fileInputContainer.querySelector('.form-text').textContent = 'Upload your form file or use test mode below';
            }
        });
    }
    
    // Format JSON data in pre tags for better readability
    const jsonElements = document.querySelectorAll('pre.json-data');
    jsonElements.forEach(function(element) {
        try {
            const jsonText = element.textContent;
            const jsonObj = JSON.parse(jsonText);
            element.textContent = JSON.stringify(jsonObj, null, 2);
        } catch (e) {
            console.error('Error formatting JSON:', e);
        }
    });
    
    // Animate validation rules on results page
    const validationRules = document.querySelectorAll('.validation-rule');
    validationRules.forEach(function(rule, index) {
        setTimeout(function() {
            rule.classList.add('fade-in');
        }, index * 100);
    });
});

// Add fade-in animation for validation rules
document.addEventListener('DOMContentLoaded', function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .validation-rule {
            opacity: 0;
        }
        
        .fade-in {
            animation: fadeIn 0.5s forwards;
        }
    `;
    document.head.appendChild(style);
});