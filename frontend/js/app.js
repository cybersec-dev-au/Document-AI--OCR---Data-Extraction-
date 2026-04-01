const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const loadingOverlay = document.getElementById('loading-overlay');
const resultsPlaceholder = document.getElementById('results-placeholder');
const extractedView = document.getElementById('extracted-view');

// Result fields
const resVendor = document.getElementById('res-vendor');
const resDate = document.getElementById('res-date');
const resTotal = document.getElementById('res-total');
const resItems = document.getElementById('res-items');
const resRaw = document.getElementById('res-raw');

// API Configuration (Change to your backend URL if different)
const API_BASE_URL = 'http://127.0.0.1:8000';

// Trigger Browse on click
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Highlight drop zone on drag
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('dragover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        processFile(e.target.files[0]);
    }
});

async function processFile(file) {
    if (!file) return;

    // Show loading state
    loadingOverlay.style.display = 'flex';
    resultsPlaceholder.style.display = 'none';
    extractedView.style.display = 'none';

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch(`${API_BASE_URL}/process_document`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errResult = await response.json();
            throw new Error(errResult.details || errResult.error || 'Server responded with an error');
        }

        const result = await response.json();
        displayResults(result);

    } catch (error) {
        console.error('Extraction Error:', error);
        alert('An error occurred during processing: ' + error.message);
        resultsPlaceholder.style.display = 'flex';
    } finally {
        loadingOverlay.style.display = 'none';
    }
}

function displayResults(result) {
    const data = result.data;
    
    // Update simple fields
    resVendor.textContent = data.vendor || 'Unknown Merchant';
    resDate.textContent = data.date || 'Not detected';
    
    // Format total (handle missing or non-numeric values gracefully)
    if (typeof data.total_amount === 'number') {
        resTotal.textContent = `₱ ${data.total_amount.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
    } else {
        resTotal.textContent = data.total_amount || 'Not detected';
    }

    // Update items list
    resItems.innerHTML = '';
    if (data.items && data.items.length > 0) {
        data.items.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `<i class="fas fa-check-circle" style="color: var(--accent-color); margin-right: 10px;"></i> ${item}`;
            resItems.appendChild(li);
        });
    } else {
        resItems.innerHTML = '<li>No specific items detected clearly.</li>';
    }

    // Update raw text
    resRaw.value = data.raw_text || 'No text extracted.';

    // Show result view with a slight animation
    extractedView.style.display = 'block';
    extractedView.style.opacity = 0;
    setTimeout(() => {
        extractedView.style.transition = 'opacity 0.5s ease-in';
        extractedView.style.opacity = 1;
    }, 50);
}

// Copy to Clipboard feature
document.getElementById('btn-copy').addEventListener('click', () => {
    const dataToCopy = {
        vendor: resVendor.textContent,
        date: resDate.textContent,
        total: resTotal.textContent,
        raw: resRaw.value
    };
    navigator.clipboard.writeText(JSON.stringify(dataToCopy, null, 2)).then(() => {
        alert('Copied extracted data to clipboard!');
    });
});

// Export feature placeholder
document.getElementById('btn-download').addEventListener('click', () => {
    alert('Export to Excel logic can be connected here via the backend /export endpoint.');
});
