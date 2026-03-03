// Configuration for MathJax
// We check if MathJax is already defined to avoid overwriting the library if it loaded first.
window.MathJax = {
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
        displayMath: [['$$', '$$'], ['\\[', '\\]']]
    },
    chtml: {
        scale: 1.2
    },
    startup: {
        typeset: false
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const pasteBtn = document.getElementById('paste-btn');
    const copyBtn = document.getElementById('copy-btn');
    const latexOutput = document.getElementById('latex-output');
    const mathJaxOutput = document.getElementById('mathjax-output');
    const loading = document.getElementById('loading');

    // Helper to toggle loading spinner
    const setLoading = (isLoading) => {
        if (isLoading) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    };

    // Helper to process image data (base64)
    const processImage = async (base64Data) => {
        if (!window.pywebview || !window.pywebview.api) {
            console.error('pywebview API not available');
            alert('Error: Backend API not connected.');
            return;
        }

        setLoading(true);
        latexOutput.value = '';
        mathJaxOutput.innerHTML = '';

        try {
            // Remove header if present (e.g. "data:image/png;base64,")
            // The python backend handles the split, but we can clean it here too if needed.
            // Based on api.py, it splits on comma.
            
            const result = await window.pywebview.api.process_image_data(base64Data);
            
            if (result && result.startsWith('Error')) {
                alert(result);
            } else {
                latexOutput.value = result;
                renderMath(result);
            }
        } catch (err) {
            console.error(err);
            alert('An error occurred while processing the image.');
        } finally {
            setLoading(false);
        }
    };

    // Helper to render MathJax
    const renderMath = (latex) => {
        // Wrap in display math delimiters for preview
        mathJaxOutput.innerHTML = `$$${latex}$$`;
        if (window.MathJax) {
            window.MathJax.typesetPromise([mathJaxOutput]).catch((err) => console.log(err));
        }
    };

    // Helper to read file as base64
    const readFile = (file) => {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            processImage(e.target.result);
        };
        reader.readAsDataURL(file);
    };

    // File Input Change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            readFile(e.target.files[0]);
        }
    });

    // Drop Zone Events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    dropZone.addEventListener('dragover', () => {
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        dropZone.classList.remove('dragover');
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            readFile(files[0]);
        }
    });

    // Paste Button
    pasteBtn.addEventListener('click', async () => {
        if (!window.pywebview || !window.pywebview.api) {
            alert('API not available');
            return;
        }
        
        try {
            const result = await window.pywebview.api.get_clipboard_image();
            if (result.startsWith('Error')) {
                alert(result);
            } else {
                // result is base64 string
                processImage(result);
            }
        } catch (err) {
            console.error(err);
            alert('Failed to get clipboard image.');
        }
    });

    // Document Paste (Ctrl+V)
    document.addEventListener('paste', (e) => {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (let index in items) {
            const item = items[index];
            if (item.kind === 'file' && item.type.startsWith('image/')) {
                const blob = item.getAsFile();
                readFile(blob);
                return; // Stop after finding an image
            }
        }
    });

    // Copy Button
    copyBtn.addEventListener('click', async () => {
        const text = latexOutput.value;
        if (!text) return;

        try {
            if (window.pywebview && window.pywebview.api && window.pywebview.api.copy_text) {
                await window.pywebview.api.copy_text(text);
                // Feedback?
                const originalText = copyBtn.innerText;
                copyBtn.innerText = 'Copied!';
                setTimeout(() => copyBtn.innerText = originalText, 2000);
            } else {
                // Fallback to browser API
                await navigator.clipboard.writeText(text);
                const originalText = copyBtn.innerText;
                copyBtn.innerText = 'Copied!';
                setTimeout(() => copyBtn.innerText = originalText, 2000);
            }
        } catch (err) {
            console.error('Failed to copy: ', err);
            alert('Failed to copy to clipboard.');
        }
    });
});
