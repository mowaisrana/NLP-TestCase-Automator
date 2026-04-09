document.addEventListener('DOMContentLoaded', () => {
    
    // --- DOM Elements ---
    const form = document.getElementById('testForm');
    const loadingDiv = document.getElementById('loading');
    const resultsDiv = document.getElementById('results');
    const errorDiv = document.getElementById('errorDiv');
    const summaryDiv = document.getElementById('orchestrationSummary');
    const tableDiv = document.getElementById('testCasesTable');
    
    // Theme & Example
    const themeToggle = document.getElementById('themeToggle');
    const btnFillExample = document.getElementById('btnFillExample');
    const inputText = document.getElementById('inputText');
    
    // --- 🟢 NEW: DYNAMIC PLACEHOLDER LOGIC ---
    const inputRadios = document.querySelectorAll('input[name="input_type"]');
    
    const placeholders = {
        code: `Paste your Python / Java / JS function here...\n\nExample:\ndef login(username, password):\n    if not username:\n        return False\n    ...`,
        ui: `Describe the UI elements to test:\n\nExample:\n- Login Screen\n- Email input (required, valid email format)\n- Password field (min 8 chars)\n- "Remember Me" checkbox\n- Submit button`
    };

    function updatePlaceholder() {
        // Find which radio is currently checked
        const selectedType = document.querySelector('input[name="input_type"]:checked').value;
        
        // Update the textarea placeholder text
        inputText.placeholder = placeholders[selectedType];
    }

    // 1. Listen for changes on the radio buttons
    inputRadios.forEach(radio => {
        radio.addEventListener('change', updatePlaceholder);
    });

    // 2. Run once on page load to set the initial state
    updatePlaceholder();

    // Download
    const mainDownloadBtn = document.getElementById('mainDownloadBtn');
    const dlRadioButtons = document.querySelectorAll('input[name="dl_format"]');
    let currentDownloadUrls = {};

// --- TABS LOGIC ---
    const tabGenerator = document.getElementById('tabGenerator');
    const tabHistory = document.getElementById('tabHistory');
    const viewGenerator = document.getElementById('viewGenerator');
    const viewHistory = document.getElementById('viewHistory');
    const historyList = document.getElementById('historyList');

    tabGenerator.addEventListener('click', () => switchTab('generator'));
    tabHistory.addEventListener('click', () => {
        switchTab('history');
        loadHistory(); // Fetch data when clicking tab
    });

    function switchTab(tab) {
        if (tab === 'generator') {
            tabGenerator.classList.add('active');
            tabGenerator.style.borderBottomColor = 'var(--color-primary)';
            tabGenerator.style.color = 'var(--color-primary)';
            
            tabHistory.classList.remove('active');
            tabHistory.style.borderBottomColor = 'transparent';
            tabHistory.style.color = 'var(--color-text-secondary)';
            
            viewGenerator.classList.remove('hidden');
            viewHistory.classList.add('hidden');
        } 
        else {
            tabHistory.classList.add('active');
            tabHistory.style.borderBottomColor = 'var(--color-primary)';
            tabHistory.style.color = 'var(--color-primary)';
            
            tabGenerator.classList.remove('active');
            tabGenerator.style.borderBottomColor = 'transparent';
            tabGenerator.style.color = 'var(--color-text-secondary)';
            
            viewHistory.classList.remove('hidden');
            viewGenerator.classList.add('hidden');
        }
    }

    // --- HISTORY FETCH LOGIC ---
    async function loadHistory() {
        try {
            const response = await fetch('/history');
            const history = await response.json();
            
            if (history.length === 0) {
                historyList.innerHTML = '<p style="text-align:center; padding: 20px;">No history found yet. Generate some tests!</p>';
                return;
            }

            historyList.innerHTML = history.map(item => `
                <div class="card" style="margin-bottom: 15px; padding: 15px; border-left: 4px solid ${item.input_type === 'code' ? 'var(--color-primary)' : 'var(--color-warning)'};">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <div style="font-size: 12px; color: var(--color-text-secondary); margin-bottom: 5px;">
                                ${item.timestamp} • <strong>${item.input_type.toUpperCase()}</strong>
                            </div>
                            <h4 style="margin: 0 0 5px 0; font-size: 16px;">Generated ${item.count} Test Cases</h4>
                            <p style="font-size: 14px; color: var(--color-text-secondary); font-family: monospace; background: var(--color-secondary); padding: 5px; border-radius: 4px;">
                                ${item.input_preview}
                            </p>
                        </div>
                        <div style="display: flex; gap: 5px;">
                            <a href="${item.download_urls.csv}" class="btn btn--sm btn--outline" download>CSV</a>
                            <a href="${item.download_urls.xlsx}" class="btn btn--sm btn--outline" download>Excel</a>
                            <button class="btn btn--sm btn--primary" onclick="restoreSession('${item.id}')">View</button>
                        </div>
                    </div>
                </div>
            `).join('');

            // Add click handlers for the "View" buttons
            // (We attach this to window so the HTML string can call it)
            window.restoreSession = (id) => {
                const record = history.find(r => r.id === id);
                if (record) {
                    // Switch back to generator tab
                    switchTab('generator');
                    // Fill the table with old data
                    displayResults({
                        test_cases: record.test_cases,
                        orchestration_summary: { 
                            test_types: ['Restored from History'], 
                            test_cases_generated: record.count 
                        }
                    });
                    // Restore download links
                    currentDownloadUrls = record.download_urls;
                    updateDownloadLink('csv'); // Default
                    
                    // Show results div
                    document.getElementById('results').classList.remove('hidden');
                    document.getElementById('loading').classList.add('hidden');
                }
            };

        } catch (error) {
            historyList.innerHTML = `<p style="color: red;">Failed to load history: ${error.message}</p>`;
        }
    }

    // --- 1. THEME TOGGLE LOGIC ---
    // Check local storage or system preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-color-scheme', savedTheme);
    updateThemeIcon(savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-color-scheme');
        const next = current === 'light' ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-color-scheme', next);
        localStorage.setItem('theme', next);
        updateThemeIcon(next);
    });

    function updateThemeIcon(theme) {
        const sun = document.querySelector('.icon-sun');
        const moon = document.querySelector('.icon-moon');
        if (theme === 'dark') {
            sun.classList.remove('hidden');
            moon.classList.add('hidden');
        } else {
            sun.classList.add('hidden');
            moon.classList.remove('hidden');
        }
    }

    // --- 2. EXAMPLE BUTTON LOGIC ---
    btnFillExample.addEventListener('click', () => {
        const exampleCode = `def calculate_discount(price, is_member):
    """Calculates final price with discount."""
    if price < 0:
        raise ValueError("Price cannot be negative")
    
    discount = 0
    if is_member:
        discount = 0.10  # 10% for members
    
    if price > 100:
        discount += 0.05  # Extra 5% for expensive items
        
    return price * (1 - discount)`;
        
        inputText.value = exampleCode;
        // Auto-select "Code" radio
        document.querySelector('input[value="code"]').checked = true;
    });

    // --- 3. FORM SUBMISSION & PROGRESS BAR ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset UI
        loadingDiv.classList.remove('hidden');
        resultsDiv.classList.add('hidden');
        errorDiv.classList.add('hidden');
        tableDiv.innerHTML = '';
        
        // Start Simulated Progress
        resetProgress();
        const progressInterval = startSimulatedProgress();

        const formData = new FormData(form);

        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) throw new Error(data.detail || 'Error generating test cases');
            
            // Success! Complete the progress bar
            clearInterval(progressInterval);
            completeProgress();
            
            // Wait a moment for "100%" animation before showing results
            setTimeout(() => {
                loadingDiv.classList.add('hidden');
                displayResults(data);
                
                // Save URLs and Set Download
                currentDownloadUrls = data.download_urls;
                const selectedFormat = document.querySelector('input[name="dl_format"]:checked').value;
                updateDownloadLink(selectedFormat);
                
                resultsDiv.classList.remove('hidden');
                resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 800);
            
        } catch (error) {
            clearInterval(progressInterval);
            loadingDiv.classList.add('hidden');
            showError(error.message);
        }
    });

    // --- PROGRESS BAR FUNCTIONS ---
    function resetProgress() {
        document.querySelectorAll('.step').forEach(s => {
            s.classList.remove('active', 'completed');
        });
        document.querySelectorAll('.line').forEach(l => l.classList.remove('active'));
    }

    function startSimulatedProgress() {
        let step = 1;
        updateStep(step); // Start at 1
        
        // Advance every 2.5 seconds until step 4 (Generating), then wait there
        return setInterval(() => {
            if (step < 4) {
                step++;
                updateStep(step);
            }
        }, 2500);
    }

    function completeProgress() {
        updateStep(5); // Jump to finish
    }

    function updateStep(currentStep) {
        document.querySelectorAll('.step').forEach(s => {
            const stepNum = parseInt(s.dataset.step);
            if (stepNum < currentStep) {
                s.classList.add('completed');
                s.classList.remove('active');
            } else if (stepNum === currentStep) {
                s.classList.add('active');
                s.classList.remove('completed');
            } else {
                s.classList.remove('active', 'completed');
            }
        });
        
        // Update lines
        const lines = document.querySelectorAll('.line');
        lines.forEach((l, index) => {
            if (index + 1 < currentStep) l.classList.add('active');
        });
    }

    // --- DOWNLOAD LOGIC ---
    dlRadioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => updateDownloadLink(e.target.value));
    });

    function updateDownloadLink(format) {
        if (currentDownloadUrls && currentDownloadUrls[format]) {
            const url = currentDownloadUrls[format];
            mainDownloadBtn.href = url;
            const filename = url.split('/').pop();
            mainDownloadBtn.setAttribute('download', filename);
        }
    }

    // --- RENDER FUNCTIONS ---
    function displayResults(data) {
        const summary = data.orchestration_summary || {};
        const testTypes = summary.test_types ? summary.test_types.join(', ') : 'Standard';
        
        summaryDiv.innerHTML = `
            <div class="summary-card" style="padding: 15px; background: var(--color-surface); border: 1px solid var(--color-border); border-radius: 8px; margin-bottom: 20px;">
                <p><strong>Status:</strong> ✅ Success</p>
                <p><strong>Generated:</strong> ${data.test_cases.length} Cases</p>
                <p><strong>Types:</strong> ${testTypes}</p>
            </div>
        `;
        
        if (!data.test_cases || data.test_cases.length === 0) {
            tableDiv.innerHTML = '<p>No test cases generated.</p>';
            return;
        }

        const tableHtml = `
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Description</th>
                            <th>Input</th>
                            <th>Expected Output</th>
                            <th>Type</th>
                            <th>Feedback</th> </tr>
                    </thead>
                    <tbody>
                        ${data.test_cases.map(tc => `
                            <tr id="row-${tc['Test Case ID'] || tc['id']}">
                                <td>${tc['Test Case ID'] || tc['id']}</td>
                                <td title="${tc['Description']}">${tc['Description']}</td>
                                <td title="${tc['Input']}"><code>${tc['Input']}</code></td>
                                <td title="${tc['Expected Output']}">${tc['Expected Output']}</td>
                                <td><span class="status status--info">${tc['Test Type']}</span></td>
                                
                                <td>
                                    <div class="feedback-buttons">
                                        <button onclick="sendFeedback('${tc['Test Case ID'] || tc['id']}', '${(tc['Description']||'').replace(/'/g, "\\'")}', 'useful')" class="btn-icon" title="Useful">👍</button>
                                        <button onclick="sendFeedback('${tc['Test Case ID'] || tc['id']}', '${(tc['Description']||'').replace(/'/g, "\\'")}', 'useless')" class="btn-icon" title="Not Useful">👎</button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        tableDiv.innerHTML = tableHtml;
    }

    // --- 🟢 NEW: FEEDBACK LOGIC ---
    // We attach this to 'window' so the HTML onclick="" can find it!
    window.sendFeedback = async (id, desc, rating) => {
        try {
            // 1. GRAB THE CURRENT INPUT TEXT (Context)
            // This is crucial so the AI knows WHICH code this feedback belongs to.
            const currentInputContext = document.getElementById('inputText').value;

            // 2. Visual Feedback immediately (UI Polish)
            const row = document.getElementById(`row-${id}`);
            if (row) {
                // Flash color based on rating
                row.style.transition = "background 0.3s";
                row.style.background = rating === 'useful' 
                    ? 'rgba(33, 150, 83, 0.2)'  // Green tint
                    : 'rgba(235, 87, 87, 0.2)'; // Red tint
                
                // Replace buttons with status text
                const btnContainer = row.querySelector('.feedback-buttons');
                if(btnContainer) {
                    btnContainer.innerHTML = rating === 'useful' 
                        ? '<span style="color:var(--color-success)">✅ Saved</span>' 
                        : '<span style="color:var(--color-error)">❌ Marked</span>';
                }
            }

            // 3. Send to Backend WITH CONTEXT
            await fetch('/feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_case_id: id,
                    description: desc,
                    rating: rating,
                    input_context: currentInputContext // <--- NEW: Sending the code too!
                })
            });
            
        } catch (err) {
            console.error("Feedback Error:", err);
            alert("Failed to save feedback");
        }
    };

    function showError(message) {
        errorDiv.textContent = '❌ ' + message;
        errorDiv.classList.remove('hidden');
    }
});