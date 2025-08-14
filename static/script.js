// Global variables
let currentIndex = 0;
let allResults = [];
let filteredResults = [];
let isSearching = false;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Get all result cards
    const cards = document.querySelectorAll('.result-card');
    allResults = Array.from(cards);
    filteredResults = [...allResults];
    
    updateNavigation();
});

// Navigation functions
function navigate(direction) {
    const results = isSearching ? filteredResults : allResults;
    
    if (results.length === 0) return;
    
    // Hide current card
    if (results[currentIndex]) {
        results[currentIndex].style.display = 'none';
    }
    
    // Update index
    currentIndex += direction;
    
    // Wrap around
    if (currentIndex < 0) {
        currentIndex = results.length - 1;
    } else if (currentIndex >= results.length) {
        currentIndex = 0;
    }
    
    // Show new card
    if (results[currentIndex]) {
        results[currentIndex].style.display = 'block';
        results[currentIndex].scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    updateNavigation();
}

function updateNavigation() {
    const results = isSearching ? filteredResults : allResults;
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const position = document.getElementById('current-position');
    
    if (results.length === 0) {
        position.textContent = '0 / 0';
        prevBtn.disabled = true;
        nextBtn.disabled = true;
        return;
    }
    
    position.textContent = `${currentIndex + 1} / ${results.length}`;
    
    // Enable/disable buttons
    prevBtn.disabled = results.length <= 1;
    nextBtn.disabled = results.length <= 1;
}

// Search functionality
function searchResults() {
    const searchInput = document.getElementById('search-input');
    const query = searchInput.value.toLowerCase().trim();
    const searchSummary = document.getElementById('search-summary');
    const searchCount = document.getElementById('search-count');
    
    if (!query) {
        clearSearch();
        return;
    }
    
    isSearching = true;
    
    // Hide all cards first
    allResults.forEach(card => {
        card.style.display = 'none';
    });
    
    // Filter results based on search query
    filteredResults = allResults.filter(card => {
        const text = card.textContent.toLowerCase();
        return text.includes(query);
    });
    
    // Reset to first result
    currentIndex = 0;
    
    // Show first filtered result
    if (filteredResults.length > 0) {
        filteredResults[0].style.display = 'block';
        searchSummary.style.display = 'flex';
        searchCount.textContent = filteredResults.length;
    } else {
        searchSummary.style.display = 'flex';
        searchCount.textContent = '0';
    }
    
    updateNavigation();
}

function clearSearch() {
    const searchInput = document.getElementById('search-input');
    const searchSummary = document.getElementById('search-summary');
    
    searchInput.value = '';
    searchSummary.style.display = 'none';
    isSearching = false;
    
    // Hide all cards
    allResults.forEach(card => {
        card.style.display = 'none';
    });
    
    // Reset filtered results
    filteredResults = [...allResults];
    currentIndex = 0;
    
    // Show first card
    if (allResults.length > 0) {
        allResults[0].style.display = 'block';
    }
    
    updateNavigation();
}

// File loading
function loadFile(filename) {
    if (!filename) return;
    window.location.href = `/load/${filename}`;
}

// Refresh file list
async function refreshFiles() {
    const refreshBtn = document.querySelector('.refresh-btn');
    const fileSelect = document.getElementById('file-select');
    
    // Add spinning animation
    refreshBtn.classList.add('spinning');
    
    try {
        // Fetch updated file list
        const response = await fetch('/api/files');
        const files = await response.json();
        
        if (files.length > 0) {
            // Check if there's a new file
            const currentFirstOption = fileSelect.options[0]?.value;
            const newestFile = files[0].filename;
            
            // Update the select options
            fileSelect.innerHTML = '';
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file.filename;
                option.textContent = `${file.timestamp} (${(file.size / 1024).toFixed(1)} KB)`;
                fileSelect.appendChild(option);
            });
            
            // If there's a new file, load it
            if (currentFirstOption !== newestFile) {
                // Show notification
                showNotification('Neue Datei gefunden! Lade...');
                setTimeout(() => {
                    window.location.href = `/load/${newestFile}`;
                }, 1500);
            } else {
                showNotification('Keine neuen Dateien gefunden');
            }
        } else {
            showNotification('Keine Dateien gefunden');
        }
    } catch (error) {
        console.error('Error refreshing files:', error);
        showNotification('Fehler beim Aktualisieren');
    } finally {
        // Stop spinning
        setTimeout(() => {
            refreshBtn.classList.remove('spinning');
        }, 1000);
    }
}

// Show notification
function showNotification(message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        notification.style.animationFillMode = 'forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Tab switching
function switchTab(event, resultIndex, tabName) {
    // Get the parent tabs container
    const tabsContainer = event.target.closest('.tabs');
    
    // Remove active class from all buttons in this container
    tabsContainer.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active class to clicked button
    event.target.classList.add('active');
    
    // Hide all tab panes for this result
    document.getElementById(`original-${resultIndex}`).classList.remove('active');
    document.getElementById(`ai-${resultIndex}`).classList.remove('active');
    
    // Show the selected tab pane
    document.getElementById(`${tabName}-${resultIndex}`).classList.add('active');
}

// Convert Markdown to HTML with proper formatting
function convertMarkdownToHTML(markdown) {
    if (!markdown) return '';
    
    let html = markdown;
    
    // Preserve line breaks by converting them to <br> temporarily
    html = html.replace(/\n/g, '___NEWLINE___');
    
    // Convert headers (h3, h2, h1)
    html = html.replace(/___NEWLINE___### (.*?)___NEWLINE___/g, '___NEWLINE___<h3>$1</h3>___NEWLINE___');
    html = html.replace(/___NEWLINE___## (.*?)___NEWLINE___/g, '___NEWLINE___<h2>$1</h2>___NEWLINE___');
    html = html.replace(/___NEWLINE___# (.*?)___NEWLINE___/g, '___NEWLINE___<h1>$1</h1>___NEWLINE___');
    
    // Convert bold and italic
    html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert inline code
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    
    // Convert tables (improved detection)
    // First, find all potential table blocks
    const lines = html.split('___NEWLINE___');
    let inTable = false;
    let tableLines = [];
    let newLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // Check if this looks like a table line (contains pipes)
        if (line.includes('|')) {
            // Check if next line is a separator (contains dashes and pipes)
            const nextLine = lines[i + 1] ? lines[i + 1].trim() : '';
            const isTableStart = !inTable && nextLine && /^\|?[\s\-:|]+\|?$/.test(nextLine);
            
            if (isTableStart) {
                // Start of a table
                inTable = true;
                tableLines = [line];
            } else if (inTable) {
                // Continuation of table
                tableLines.push(line);
            } else if (/^\|?[\s\-:|]+\|?$/.test(line)) {
                // This is a separator line, skip it if we're in a table
                if (inTable && tableLines.length > 0) {
                    // Already have header, this is the separator
                    continue;
                }
            } else {
                // Single line with pipes, not a table
                newLines.push(line);
            }
        } else {
            // Not a table line
            if (inTable && tableLines.length > 1) {
                // End of table, process it
                newLines.push(createTableHTML(tableLines));
                tableLines = [];
                inTable = false;
            } else if (inTable) {
                // False alarm, wasn't a table
                newLines = newLines.concat(tableLines);
                tableLines = [];
                inTable = false;
            }
            newLines.push(line);
        }
    }
    
    // Process any remaining table
    if (inTable && tableLines.length > 1) {
        newLines.push(createTableHTML(tableLines));
    }
    
    html = newLines.join('___NEWLINE___');
    
    // Helper function to create table HTML
    function createTableHTML(lines) {
        if (lines.length < 2) return lines.join('___NEWLINE___');
        
        let table = '<table class="markdown-table">';
        
        // First line is header
        const headerCells = lines[0].split('|').map(cell => cell.trim()).filter(cell => cell);
        table += '<thead><tr>';
        headerCells.forEach(cell => {
            table += `<th>${cell}</th>`;
        });
        table += '</tr></thead><tbody>';
        
        // Rest are body rows (skip separator if present)
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            // Skip separator lines
            if (/^\|?[\s\-:|]+\|?$/.test(line)) continue;
            
            const cells = line.split('|').map(cell => cell.trim()).filter(cell => cell);
            if (cells.length > 0) {
                table += '<tr>';
                cells.forEach(cell => {
                    table += `<td>${cell}</td>`;
                });
                table += '</tr>';
            }
        }
        
        table += '</tbody></table>';
        return table;
    }
    
    // Convert bullet lists
    const bulletListItems = [];
    html = html.replace(/___NEWLINE___[\*\-\+] (.*?)(?=___NEWLINE___|$)/g, function(match, item) {
        bulletListItems.push(`<li>${item}</li>`);
        return '___BULLET_ITEM___';
    });
    
    // Group consecutive bullet items into lists
    html = html.replace(/(___BULLET_ITEM___)+/g, function(match) {
        const count = match.split('___BULLET_ITEM___').length - 1;
        const items = bulletListItems.splice(0, count).join('');
        return `<ul>${items}</ul>`;
    });
    
    // Convert numbered lists
    const numberedListItems = [];
    html = html.replace(/___NEWLINE___\d+\. (.*?)(?=___NEWLINE___|$)/g, function(match, item) {
        numberedListItems.push(`<li>${item}</li>`);
        return '___NUMBERED_ITEM___';
    });
    
    // Group consecutive numbered items into lists
    html = html.replace(/(___NUMBERED_ITEM___)+/g, function(match) {
        const count = match.split('___NUMBERED_ITEM___').length - 1;
        const items = numberedListItems.splice(0, count).join('');
        return `<ol>${items}</ol>`;
    });
    
    // Convert blockquotes
    html = html.replace(/___NEWLINE___> (.*?)___NEWLINE___/g, '___NEWLINE___<blockquote>$1</blockquote>___NEWLINE___');
    
    // Convert horizontal rules
    html = html.replace(/___NEWLINE___---___NEWLINE___/g, '___NEWLINE___<hr>___NEWLINE___');
    html = html.replace(/___NEWLINE___\*\*\*___NEWLINE___/g, '___NEWLINE___<hr>___NEWLINE___');
    
    // Convert remaining newlines to proper HTML
    // Double newlines become paragraph breaks
    html = html.replace(/___NEWLINE______NEWLINE___/g, '</p><p>');
    // Single newlines become line breaks
    html = html.replace(/___NEWLINE___/g, '<br>');
    
    // Wrap in paragraph tags if not already wrapped
    if (!html.startsWith('<')) {
        html = '<p>' + html + '</p>';
    }
    
    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p><br><\/p>/g, '');
    
    return html;
}

// Generate AI Summary
async function generateSummary(filename, index, force = false) {
    const placeholderDiv = document.getElementById(`ai-placeholder-${index}`);
    const loadingDiv = document.getElementById(`ai-loading-${index}`);
    const summaryDiv = document.getElementById(`ai-summary-${index}`);
    
    // Show loading - hide everything else first
    if (placeholderDiv) placeholderDiv.style.display = 'none';
    if (summaryDiv) summaryDiv.style.display = 'none';
    
    // Make sure loading div exists and show it
    if (loadingDiv) {
        loadingDiv.style.display = 'block';
    } else {
        console.error('Loading div not found for index:', index);
        showNotification('Fehler: Loading-Element nicht gefunden');
        return;
    }
    
    try {
        const response = await fetch(`/api/generate-summary/${filename}/${index}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ force: force })
        });
        
        const data = await response.json();
        
        if (data.status === 'success' || data.status === 'exists') {
            // Hide loading, show summary
            loadingDiv.style.display = 'none';
            summaryDiv.style.display = 'block';
            
            // Convert markdown to HTML with proper formatting
            let htmlContent = convertMarkdownToHTML(data.summary);
            
            summaryDiv.innerHTML = htmlContent;
            
            // Update the button in the header to show regenerate
            const actionsDiv = document.querySelector(`#ai-summary-${index}`).closest('.ai-section').querySelector('.ai-actions');
            if (actionsDiv) {
                actionsDiv.innerHTML = `
                    <button class="btn-action regenerate" onclick="generateSummary('${filename}', ${index}, true)" title="Zusammenfassung neu generieren">
                        🔄 Neu generieren
                    </button>
                `;
            }
            
            showNotification(force ? 'AI-Zusammenfassung neu generiert!' : 'AI-Zusammenfassung generiert!');
        } else {
            // Show error
            loadingDiv.style.display = 'none';
            // If we were regenerating (force=true), show the summary again, otherwise show placeholder
            if (force && summaryDiv && summaryDiv.innerHTML) {
                summaryDiv.style.display = 'block';
            } else if (placeholderDiv) {
                placeholderDiv.style.display = 'block';
            }
            showNotification(`Fehler: ${data.message || 'Unbekannter Fehler'}`);
        }
    } catch (error) {
        console.error('Error generating summary:', error);
        loadingDiv.style.display = 'none';
        // If we were regenerating (force=true), show the summary again, otherwise show placeholder
        if (force && summaryDiv && summaryDiv.innerHTML) {
            summaryDiv.style.display = 'block';
        } else if (placeholderDiv) {
            placeholderDiv.style.display = 'block';
        }
        showNotification('Fehler beim Generieren der Zusammenfassung');
    }
}

// Test Ollama connection on page load
async function testOllamaConnection() {
    try {
        const response = await fetch('/api/test-ollama');
        const data = await response.json();
        
        if (data.status === 'connected') {
            console.log('Ollama connected. Available models:', data.models);
        } else {
            console.warn('Ollama not connected:', data.message);
        }
    } catch (error) {
        console.error('Error testing Ollama connection:', error);
    }
}

// Settings Management
let currentSettings = {};
const defaultPrompt = `Du bist ein Experte für öffentliche Ausschreibungen in Deutschland. 
Bitte erstelle eine präzise und gut strukturierte Zusammenfassung der folgenden Ausschreibungsbeschreibung.
{context}
Originalbeschreibung:
{text}

Erstelle eine klare Zusammenfassung auf Deutsch mit folgender Struktur:
1. **Hauptleistung**: Was wird ausgeschrieben?
2. **Umfang**: Welche konkreten Arbeiten/Lieferungen sind enthalten?
3. **Besonderheiten**: Wichtige technische Anforderungen oder Bedingungen

Formatiere die Antwort mit Markdown für bessere Lesbarkeit.
Halte dich kurz und präzise (maximal 150 Wörter).
Fokussiere dich auf die wichtigsten Informationen für potenzielle Bieter.`;

async function openSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.add('show');
    
    // Load current settings
    try {
        const response = await fetch('/api/settings');
        currentSettings = await response.json();
        
        // Populate form
        document.getElementById('server-url').value = currentSettings.ollama.base_url || 'http://localhost:11434';
        document.getElementById('temperature-slider').value = currentSettings.ollama.temperature;
        document.getElementById('temperature-value').textContent = currentSettings.ollama.temperature;
        document.getElementById('max-tokens').value = currentSettings.ollama.max_tokens;
        document.getElementById('prompt-template').value = currentSettings.ollama.prompt_template;
        
        // Set reasoning effort if available
        if (currentSettings.ollama.reasoning_effort) {
            document.getElementById('reasoning-effort').value = currentSettings.ollama.reasoning_effort;
        }
        
        // Load available models
        await loadModels();
        
        // Set current model
        document.getElementById('model-select').value = currentSettings.ollama.model;
        
        // Show/hide reasoning effort based on model
        toggleReasoningField(currentSettings.ollama.model);
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

async function loadModels() {
    const modelSelect = document.getElementById('model-select');
    const serverUrl = document.getElementById('server-url').value || 'http://localhost:11434';
    
    modelSelect.innerHTML = '<option value="">Lade Modelle...</option>';
    
    try {
        const response = await fetch('/api/test-ollama', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ base_url: serverUrl })
        });
        const data = await response.json();
        
        if (data.status === 'connected') {
            modelSelect.innerHTML = '';
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
            showNotification('✅ Verbindung zu Ollama Server erfolgreich');
        } else {
            modelSelect.innerHTML = '<option value="">Keine Modelle verfügbar</option>';
            showNotification('❌ Keine Verbindung zum Ollama Server');
        }
    } catch (error) {
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Fehler beim Laden der Modelle</option>';
        showNotification('❌ Fehler beim Verbinden mit Ollama Server');
    }
}

function closeSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.remove('show');
}

function toggleReasoningField(model) {
    const reasoningGroup = document.getElementById('reasoning-group');
    // Show reasoning effort field only for gpt-oss models
    if (model && model.includes('gpt-oss')) {
        reasoningGroup.style.display = 'block';
    } else {
        reasoningGroup.style.display = 'none';
    }
}

async function saveSettings() {
    // Gather settings
    const modelSelect = document.getElementById('model-select');
    const model = modelSelect.value;
    
    const settings = {
        ollama: {
            base_url: document.getElementById('server-url').value || 'http://localhost:11434',
            model: model,
            temperature: parseFloat(document.getElementById('temperature-slider').value),
            max_tokens: parseInt(document.getElementById('max-tokens').value),
            prompt_template: document.getElementById('prompt-template').value
        }
    };
    
    // Add reasoning effort only for gpt-oss models
    if (model && model.includes('gpt-oss')) {
        settings.ollama.reasoning_effort = document.getElementById('reasoning-effort').value;
    }
    
    try {
        const response = await fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Einstellungen gespeichert!');
            closeSettings();
        } else {
            showNotification('Fehler beim Speichern: ' + data.message);
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showNotification('Fehler beim Speichern der Einstellungen');
    }
}

function resetSettings() {
    // Reset to defaults
    document.getElementById('temperature-slider').value = 0.3;
    document.getElementById('temperature-value').textContent = '0.3';
    document.getElementById('max-tokens').value = 300;
    document.getElementById('prompt-template').value = defaultPrompt;
    
    // Select first model if available
    const modelSelect = document.getElementById('model-select');
    if (modelSelect.options.length > 0) {
        modelSelect.selectedIndex = 0;
    }
}

// Temperature slider update
document.addEventListener('DOMContentLoaded', function() {
    const tempSlider = document.getElementById('temperature-slider');
    const tempValue = document.getElementById('temperature-value');
    
    if (tempSlider && tempValue) {
        tempSlider.addEventListener('input', function() {
            tempValue.textContent = this.value;
        });
    }
    
    // Model select change listener
    const modelSelect = document.getElementById('model-select');
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            toggleReasoningField(this.value);
        });
    }
    
    testOllamaConnection();
});

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('settings-modal');
    if (event.target == modal) {
        closeSettings();
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', function() {
    testOllamaConnection();
});

// Generate summaries for all results
async function generateAllSummaries(forceRegenerate = false) {
    const fileSelect = document.getElementById('file-select');
    const filename = fileSelect ? fileSelect.value : null;
    
    if (!filename) {
        showNotification('Keine Datei ausgewählt');
        return;
    }
    
    // Get confirmation from user
    const message = forceRegenerate 
        ? 'Möchten Sie wirklich ALLE AI-Zusammenfassungen neu generieren? Dies wird alle existierenden Zusammenfassungen überschreiben und kann einige Zeit dauern.'
        : 'Möchten Sie wirklich AI-Zusammenfassungen für alle Ergebnisse ohne Zusammenfassung generieren? Dies kann einige Zeit dauern.';
    
    if (!confirm(message)) {
        return;
    }
    
    const button = forceRegenerate 
        ? document.querySelector('.btn-regenerate-all') 
        : document.querySelector('.btn-generate-all');
    const otherButton = forceRegenerate 
        ? document.querySelector('.btn-generate-all')
        : document.querySelector('.btn-regenerate-all');
    const progressDiv = document.getElementById('batch-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    
    // Disable both buttons and show progress
    button.disabled = true;
    if (otherButton) otherButton.disabled = true;
    progressDiv.style.display = 'block';
    
    try {
        // Start batch generation
        const response = await fetch(`/api/generate-all-summaries/${filename}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ force: forceRegenerate })
        });
        
        const data = await response.json();
        
        if (data.status === 'started') {
            const totalCount = data.total;
            let processed = 0;
            
            // Poll for progress
            const pollInterval = setInterval(async () => {
                try {
                    const progressResponse = await fetch(`/api/batch-progress/${filename}`);
                    const progressData = await progressResponse.json();
                    
                    processed = progressData.processed;
                    const percentage = (processed / totalCount) * 100;
                    
                    // Update progress bar
                    progressFill.style.width = percentage + '%';
                    progressText.textContent = `${processed} / ${totalCount}`;
                    
                    // Check if complete
                    if (progressData.status === 'completed' || processed >= totalCount) {
                        clearInterval(pollInterval);
                        button.disabled = false;
                        if (otherButton) otherButton.disabled = false;
                        showNotification(`✅ Alle ${processed} Zusammenfassungen wurden generiert!`);
                        
                        // Reload page after 2 seconds to show new summaries
                        setTimeout(() => {
                            window.location.reload();
                        }, 2000);
                    } else if (progressData.status === 'error') {
                        clearInterval(pollInterval);
                        button.disabled = false;
                        showNotification('❌ Fehler bei der Batch-Generierung');
                    }
                } catch (error) {
                    console.error('Error polling progress:', error);
                    clearInterval(pollInterval);
                    button.disabled = false;
                }
            }, 2000); // Poll every 2 seconds
        } else {
            button.disabled = false;
            showNotification('Fehler beim Starten der Batch-Generierung');
        }
    } catch (error) {
        console.error('Error starting batch generation:', error);
        button.disabled = false;
        progressDiv.style.display = 'none';
        showNotification('Fehler bei der Batch-Generierung');
    }
}

// Auto-refresh every 30 seconds (optional)
let autoRefreshInterval = null;

function toggleAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        showNotification('Auto-Refresh deaktiviert');
    } else {
        autoRefreshInterval = setInterval(() => {
            refreshFiles();
        }, 30000); // 30 seconds
        showNotification('Auto-Refresh aktiviert (30s)');
    }
}

// Keyboard navigation
document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT') return;
    
    switch(e.key) {
        case 'ArrowLeft':
            navigate(-1);
            break;
        case 'ArrowRight':
            navigate(1);
            break;
        case 'Escape':
            clearSearch();
            break;
        case '/':
            e.preventDefault();
            document.getElementById('search-input').focus();
            break;
    }
});

// Search on Enter key
document.getElementById('search-input')?.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        searchResults();
    }
});

// Run Scraper Function
async function runScraper() {
    const scraperBtn = document.getElementById('scraper-btn');
    const statusDiv = document.getElementById('scraper-status');
    const scraperText = scraperBtn.querySelector('.scraper-text');
    const scraperSpinner = scraperBtn.querySelector('.scraper-spinner');
    
    // Check if already running
    if (scraperBtn.classList.contains('running')) {
        alert('Der Scraper läuft bereits!');
        return;
    }
    
    // Update button state
    scraperBtn.classList.add('running');
    scraperText.style.display = 'none';
    scraperSpinner.style.display = 'inline-block';
    
    // Show status indicator
    statusDiv.classList.add('active');
    
    try {
        const response = await fetch('/run-scraper', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.status === 'started') {
            // Poll for status
            checkScraperStatus();
        } else if (data.status === 'error') {
            alert('Fehler beim Starten des Scrapers: ' + (data.message || 'Unbekannter Fehler'));
            resetScraperButton();
        }
    } catch (error) {
        console.error('Error starting scraper:', error);
        alert('Fehler beim Starten des Scrapers');
        resetScraperButton();
    }
}

// Check scraper status
async function checkScraperStatus() {
    const scraperBtn = document.getElementById('scraper-btn');
    const statusDiv = document.getElementById('scraper-status');
    const statusText = statusDiv.querySelector('.scraper-status-text');
    
    const checkInterval = setInterval(async () => {
        try {
            const response = await fetch('/scraper-status');
            const data = await response.json();
            
            if (data.status === 'completed') {
                clearInterval(checkInterval);
                statusText.textContent = 'Scraper abgeschlossen!';
                
                // Refresh files after completion
                setTimeout(() => {
                    resetScraperButton();
                    refreshFiles();
                }, 2000);
            } else if (data.status === 'error') {
                clearInterval(checkInterval);
                statusText.textContent = 'Fehler beim Scraping!';
                setTimeout(() => {
                    resetScraperButton();
                }, 3000);
            } else if (data.status === 'running') {
                // Update status text with progress if available
                if (data.progress) {
                    statusText.textContent = `Scraper läuft... ${data.progress}`;
                }
            }
        } catch (error) {
            console.error('Error checking scraper status:', error);
        }
    }, 2000); // Check every 2 seconds
}

// Reset scraper button to initial state
function resetScraperButton() {
    const scraperBtn = document.getElementById('scraper-btn');
    const statusDiv = document.getElementById('scraper-status');
    const scraperText = scraperBtn.querySelector('.scraper-text');
    const scraperSpinner = scraperBtn.querySelector('.scraper-spinner');
    
    scraperBtn.classList.remove('running');
    scraperText.style.display = 'inline';
    scraperSpinner.style.display = 'none';
    statusDiv.classList.remove('active');
}