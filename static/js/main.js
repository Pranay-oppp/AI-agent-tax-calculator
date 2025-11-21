// File input handling
const fileInput = document.getElementById('fileInput');
const fileNames = document.getElementById('fileNames');
const processBtn = document.getElementById('processBtn');
const calculateBtn = document.getElementById('calculateBtn');
const downloadBtn = document.getElementById('downloadBtn');
const statusMessage = document.getElementById('statusMessage');
const parseResults = document.getElementById('parseResults');
const summaryResults = document.getElementById('summaryResults');
const loadingOverlay = document.getElementById('loadingOverlay');
const downloadSection = document.getElementById('downloadSection');

// Update file names display
fileInput.addEventListener('change', function() {
    if (this.files.length > 0) {
        const names = Array.from(this.files).map(f => f.name).join(', ');
        fileNames.textContent = names;
    } else {
        fileNames.textContent = 'No files chosen';
    }
});

// Process documents
processBtn.addEventListener('click', async function() {
    // Validate form
    const form = document.getElementById('taxForm');
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Check files
    if (fileInput.files.length === 0) {
        showStatus('error', 'Please select at least one PDF file.');
        return;
    }

    // Show loading
    showLoading(true);

    // Prepare form data
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('ssn', document.getElementById('ssn').value);
    formData.append('address', document.getElementById('address').value);
    formData.append('filing_status', document.getElementById('filing_status').value);

    // Add files
    for (let file of fileInput.files) {
        formData.append('files[]', file);
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            showStatus('success', data.message);
            displayParseResults(data.results);
            calculateBtn.disabled = false;
        } else {
            showStatus('error', data.error);
            if (data.results) {
                displayParseResults(data.results);
            }
        }
    } catch (error) {
        showStatus('error', 'Error processing documents: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Calculate tax return
calculateBtn.addEventListener('click', async function() {
    showLoading(true);

    try {
        const response = await fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success) {
            displayTaxSummary(data.summary, data.tax_data);
            downloadSection.style.display = 'block';
        } else {
            showStatus('error', data.error);
        }
    } catch (error) {
        showStatus('error', 'Error calculating return: ' + error.message);
    } finally {
        showLoading(false);
    }
});

// Download form
downloadBtn.addEventListener('click', function() {
    window.location.href = '/download';
});

// Helper functions
function showStatus(type, message) {
    statusMessage.className = `status-message ${type}`;
    statusMessage.textContent = message;
    statusMessage.style.display = 'block';
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.add('show');
    } else {
        loadingOverlay.classList.remove('show');
    }
}

function displayParseResults(results) {
    parseResults.innerHTML = '<h3>📄 Parsed Documents:</h3>';

    results.forEach(result => {
        const div = document.createElement('div');
        div.className = `document-result ${result.status}`;

        let html = `<h4>${result.filename}</h4>`;

        if (result.status === 'success') {
            html += `<p><strong>Type:</strong> ${result.type}</p>`;
            html += '<div class="document-data">';

            if (result.data) {
                for (let [key, value] of Object.entries(result.data)) {
                    html += `<p><strong>${key}:</strong> ${value}</p>`;
                }
            }

            html += '</div>';
        } else {
            html += `<p class="error">Error: ${result.message}</p>`;
        }

        div.innerHTML = html;
        parseResults.appendChild(div);
    });
}

function displayTaxSummary(summary, taxData) {
    summaryResults.innerHTML = `
        <div class="tax-summary">
            <h3>📊 Tax Calculation Summary</h3>
            <pre>${summary}</pre>
        </div>

        <div class="tax-info-grid">
            <div class="tax-info-item">
                <h4>Total Income</h4>
                <p>${taxData.total_income}</p>
            </div>
            <div class="tax-info-item">
                <h4>Taxable Income</h4>
                <p>${taxData.taxable_income}</p>
            </div>
            <div class="tax-info-item">
                <h4>Federal Tax</h4>
                <p>${taxData.total_tax}</p>
            </div>
            <div class="tax-info-item">
                <h4>Tax Withheld</h4>
                <p>${taxData.federal_withheld}</p>
            </div>
            <div class="tax-info-item">
                <h4>Effective Rate</h4>
                <p>${taxData.effective_rate}</p>
            </div>
            <div class="tax-info-item ${taxData.refund_status === 'REFUND' ? 'refund' : 'owed'}">
                <h4>${taxData.refund_status === 'REFUND' ? 'Refund Amount' : 'Amount Owed'}</h4>
                <p>${taxData.refund_amount}</p>
            </div>
        </div>
    `;
}