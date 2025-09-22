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
    
    // Add click listeners for requirement sections (collapsible)
    document.addEventListener('click', function(e) {
        if (e.target.closest('.requirement-header')) {
            const section = e.target.closest('.requirement-section');
            section.classList.toggle('expanded');
        }
    });
}

function setupDragAndDrop(areaId, inputId) {
    const area = document.getElementById(areaId);
    const input = document.getElementById(inputId);
    
    area.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.stopPropagation();
        area.classList.add('drag-over');
    });
    
    area.addEventListener('dragleave', function(e) {
        e.preventDefault();
        e.stopPropagation();
        area.classList.remove('drag-over');
    });
    
    area.addEventListener('drop', function(e) {
        e.preventDefault();
        e.stopPropagation();
        area.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]);
            input.files = dataTransfer.files;
            input.dispatchEvent(new Event('change'));
        }
    });
    
    // Only add click listener to the area, not the button
    area.addEventListener('click', function(e) {
        // Don't trigger if clicking the button inside
        if (!e.target.classList.contains('btn')) {
            input.click();
        }
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
    
    // Parse and format requirements into visual sections
    const formattedRequirements = formatRequirementsVisually(requirements);
    requirementsDiv.innerHTML = formattedRequirements;
    
    analysisDiv.classList.remove('hidden');
}

function formatRequirementsVisually(requirements) {
    // Split requirements into sections
    const sections = requirements.split(/\n(?=\d+\.|[A-Z][a-zA-Z\s]+:|\*\*[A-Z])/);
    let formattedHTML = '';
    
    sections.forEach(section => {
        const trimmedSection = section.trim();
        if (!trimmedSection) return;
        
        // Check if it's a main heading (numbered or bolded)
        if (trimmedSection.match(/^\d+\.\s*[A-Z]/) || trimmedSection.match(/^\*\*[A-Z]/)) {
            const title = trimmedSection.split('\n')[0].replace(/^\d+\.\s*|\*\*/g, '');
            const content = trimmedSection.split('\n').slice(1).join('\n').trim();
            
            formattedHTML += `
                <div class="requirement-section">
                    <div class="requirement-header">
                        <i class="fas fa-chevron-right requirement-icon"></i>
                        <h4>${title}</h4>
                    </div>
                    <div class="requirement-content">
                        ${formatRequirementContent(content)}
                    </div>
                </div>
            `;
        } else {
            // Regular content section
            formattedHTML += `
                <div class="requirement-section">
                    <div class="requirement-content">
                        ${formatRequirementContent(trimmedSection)}
                    </div>
                </div>
            `;
        }
    });
    
    return formattedHTML || `<div class="requirement-content">${requirements}</div>`;
}

function formatRequirementContent(content) {
    if (!content) return '';
    
    // Convert bullet points to HTML lists
    let formatted = content
        .replace(/^[-•*]\s+(.+)$/gm, '<li>$1</li>')
        .replace(/^(\d+)\.\s+(.+)$/gm, '<li>$2</li>');
    
    // Wrap consecutive <li> elements in <ul>
    formatted = formatted.replace(/(<li>.*<\/li>(?:\s*<li>.*<\/li>)*)/gs, '<ul>$1</ul>');
    
    // Convert remaining line breaks to <br> for paragraphs
    formatted = formatted.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags if no other block elements
    if (!formatted.includes('<ul>') && !formatted.includes('<li>')) {
        formatted = `<p>${formatted}</p>`;
    }
    
    return formatted;
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
            <div class="session-content">
                <div class="session-title">${session.rfp_filename || 'Untitled RFP'}</div>
                <div class="session-meta">${date} ${time}</div>
                <div class="session-meta">Status: ${status}</div>
            </div>
            <div class="session-actions">
                <button class="delete-session-btn" onclick="deleteSession(event, ${session.id})">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </div>
        `;
        
        // Add click listener for session content (not delete button)
        sessionItem.querySelector('.session-content').addEventListener('click', () => loadSession(session));
        sessionsList.appendChild(sessionItem);
    });
}

async function deleteSession(event, sessionId) {
    event.stopPropagation(); // Prevent triggering session load
    
    if (!confirm('Are you sure you want to delete this session? This action cannot be undone.')) {
        return;
    }
    
    try {
        showLoading('Deleting session...');
        
        const response = await fetch(`/delete_session/${sessionId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Session deleted successfully!');
            await loadSessions(); // Refresh sessions list
            
            // If we deleted the current session, reset to step 1
            if (currentSession && currentSession.id === sessionId) {
                currentSession = null;
                resetToInitialState();
            }
        } else {
            showError(result.error || 'Failed to delete session');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoading();
    }
}

function resetToInitialState() {
    // Clear all form data and go back to step 1
    document.getElementById('rfpFileInput').value = '';
    document.getElementById('orgFileInput').value = '';
    document.getElementById('responsePrompt').value = '';
    originalPrompt = '';
    
    // Hide all analysis results
    document.getElementById('rfpAnalysis').classList.add('hidden');
    document.getElementById('orgAnalysis').classList.add('hidden');
    document.getElementById('downloadSection').classList.add('hidden');
    
    // Go back to step 1
    goToStep(1);
}

function loadSession(session) {
    // Update active session in sidebar
    document.querySelectorAll('.session-item').forEach(item => {
        item.classList.remove('active');
    });
    
    // Find the session item that was clicked and mark it active
    const sessionItems = document.querySelectorAll('.session-item');
    sessionItems.forEach(item => {
        const title = item.querySelector('.session-title').textContent;
        if (title === (session.rfp_filename || 'Untitled RFP')) {
            item.classList.add('active');
        }
    });
    
    currentSession = session;
    
    // Reset UI first
    resetToInitialState();
    
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