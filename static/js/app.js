// Global variables
let currentStep = 1;
let originalPrompt = '';
let currentSession = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadSessions();
});

function initializeApp() {
    // Set initial step
    goToStep(1);
}

function setupEventListeners() {
    // File input listeners
    document.getElementById('rfpFileInput').addEventListener('change', handleRFPUpload);
    document.getElementById('orgFileInput').addEventListener('change', handleOrgUpload);
    
    // Drag and drop listeners
    setupDragAndDrop('rfpUploadArea', 'rfpFileInput');
    setupDragAndDrop('orgUploadArea', 'orgFileInput');
}

function setupDragAndDrop(areaId, inputId) {
    const area = document.getElementById(areaId);
    const input = document.getElementById(inputId);
    
    area.addEventListener('dragover', function(e) {
        e.preventDefault();
        area.classList.add('drag-over');
    });
    
    area.addEventListener('dragleave', function(e) {
        e.preventDefault();
        area.classList.remove('drag-over');
    });
    
    area.addEventListener('drop', function(e) {
        e.preventDefault();
        area.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            input.dispatchEvent(new Event('change'));
        }
    });
    
    area.addEventListener('click', function() {
        input.click();
    });
}

function handleRFPUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!isValidFileType(file)) {
        showError('Please select a valid file type (PDF, TXT, or DOCX)');
        return;
    }
    
    uploadRFP(file);
}

function handleOrgUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!isValidFileType(file)) {
        showError('Please select a valid file type (PDF, TXT, or DOCX)');
        return;
    }
    
    uploadOrg(file);
}

function isValidFileType(file) {
    const validTypes = [
        'application/pdf',
        'text/plain',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];
    return validTypes.includes(file.type) || 
           file.name.toLowerCase().endsWith('.pdf') ||
           file.name.toLowerCase().endsWith('.txt') ||
           file.name.toLowerCase().endsWith('.docx');
}

async function uploadRFP(file) {
    showLoading('Analyzing RFP requirements...');
    
    const formData = new FormData();
    formData.append('rfp_file', file);
    
    try {
        const response = await fetch('/upload_rfp', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayRFPAnalysis(result.requirements);
            showSuccess('RFP analyzed successfully!');
            loadSessions(); // Refresh sessions
        } else {
            showError(result.error || 'Failed to analyze RFP');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function uploadOrg(file) {
    showLoading('Analyzing organization details...');
    
    const formData = new FormData();
    formData.append('org_file', file);
    
    try {
        const response = await fetch('/upload_org', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayOrgAnalysis(result.org_analysis, result.matching_table);
            originalPrompt = result.response_prompt;
            document.getElementById('responsePrompt').value = originalPrompt;
            showSuccess('Organization analyzed successfully!');
            loadSessions(); // Refresh sessions
        } else {
            showError(result.error || 'Failed to analyze organization');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayRFPAnalysis(requirements) {
    const analysisDiv = document.getElementById('rfpAnalysis');
    const requirementsDiv = document.getElementById('rfpRequirements');
    
    requirementsDiv.textContent = requirements;
    analysisDiv.classList.remove('hidden');
}

function displayOrgAnalysis(analysis, matchingTable) {
    const analysisDiv = document.getElementById('orgAnalysis');
    const capabilitiesDiv = document.getElementById('orgCapabilities');
    const matchingDiv = document.getElementById('matchingTable');
    
    capabilitiesDiv.textContent = analysis;
    
    // Display matching table
    matchingDiv.innerHTML = '';
    matchingTable.forEach(match => {
        const matchItem = document.createElement('div');
        matchItem.className = 'match-item';
        
        const strengthClass = `match-${match.match.toLowerCase()}`;
        
        matchItem.innerHTML = `
            <div class="match-requirement">Requirement: ${match.requirement}</div>
            <div class="match-capability">Capability: ${match.capability}</div>
            <div class="match-strength ${strengthClass}">${match.match} Match</div>
            ${match.notes ? `<div class="match-notes">Notes: ${match.notes}</div>` : ''}
        `;
        
        matchingDiv.appendChild(matchItem);
    });
    
    analysisDiv.classList.remove('hidden');
}

async function generateDocument() {
    const prompt = document.getElementById('responsePrompt').value;
    
    if (!prompt.trim()) {
        showError('Please enter a response prompt');
        return;
    }
    
    showLoading('Generating DOCX document...');
    
    try {
        const response = await fetch('/generate_document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showDownloadSection(result.download_url);
            showSuccess('Document generated successfully!');
            loadSessions(); // Refresh sessions
        } else {
            showError(result.error || 'Failed to generate document');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

function showDownloadSection(downloadUrl) {
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');
    
    downloadBtn.onclick = function() {
        window.open(downloadUrl, '_blank');
    };
    
    downloadSection.classList.remove('hidden');
}

function resetPrompt() {
    if (originalPrompt) {
        document.getElementById('responsePrompt').value = originalPrompt;
        showSuccess('Prompt reset to original');
    } else {
        showError('No original prompt available');
    }
}

function goToStep(step) {
    // Update progress steps
    document.querySelectorAll('.progress-step').forEach((el, index) => {
        el.classList.toggle('active', index + 1 <= step);
    });
    
    // Update content sections
    document.querySelectorAll('.content-section').forEach((el, index) => {
        el.classList.toggle('active', index + 1 === step);
    });
    
    currentStep = step;
}

async function loadSessions() {
    try {
        const response = await fetch('/get_sessions');
        const sessions = await response.json();
        
        displaySessions(sessions);
    } catch (error) {
        console.error('Failed to load sessions:', error);
    }
}

function displaySessions(sessions) {
    const sessionsList = document.getElementById('sessionsList');
    sessionsList.innerHTML = '';
    
    if (sessions.length === 0) {
        sessionsList.innerHTML = '<div style="color: #bbb; text-align: center; padding: 20px;">No sessions yet</div>';
        return;
    }
    
    sessions.forEach((session, index) => {
        const sessionItem = document.createElement('div');
        sessionItem.className = 'session-item';
        if (index === 0) sessionItem.classList.add('active');
        
        const date = new Date(session.created_at).toLocaleDateString();
        const time = new Date(session.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const status = session.output_filename ? 'Completed' : 'In Progress';
        
        sessionItem.innerHTML = `
            <div class="session-title">${session.rfp_filename || 'Untitled RFP'}</div>
            <div class="session-meta">${date} ${time}</div>
            <div class="session-meta">Status: ${status}</div>
        `;
        
        sessionItem.addEventListener('click', () => loadSession(session));
        sessionsList.appendChild(sessionItem);
    });
}

function loadSession(session) {
    // Update active session in sidebar
    document.querySelectorAll('.session-item').forEach(item => {
        item.classList.remove('active');
    });
    event.currentTarget.classList.add('active');
    
    currentSession = session;
    
    // Load session data into UI
    if (session.rfp_requirements) {
        displayRFPAnalysis(session.rfp_requirements);
        goToStep(2);
    }
    
    if (session.org_analysis && session.matching_table) {
        displayOrgAnalysis(session.org_analysis, session.matching_table);
        goToStep(3);
    }
    
    if (session.response_prompt) {
        originalPrompt = session.response_prompt;
        document.getElementById('responsePrompt').value = originalPrompt;
    }
    
    if (session.output_filename) {
        showDownloadSection(`/download/${session.output_filename}`);
    }
}

// Utility functions
function showLoading(message = 'Processing...') {
    document.getElementById('loadingText').textContent = message;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showError(message) {
    document.getElementById('errorText').textContent = message;
    document.getElementById('errorMessage').classList.remove('hidden');
    
    // Auto hide after 5 seconds
    setTimeout(hideError, 5000);
}

function hideError() {
    document.getElementById('errorMessage').classList.add('hidden');
}

function showSuccess(message) {
    document.getElementById('successText').textContent = message;
    document.getElementById('successMessage').classList.remove('hidden');
    
    // Auto hide after 3 seconds
    setTimeout(hideSuccess, 3000);
}

function hideSuccess() {
    document.getElementById('successMessage').classList.add('hidden');
}
