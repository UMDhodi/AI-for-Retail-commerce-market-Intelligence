// BharatSignal Decision Board JavaScript functionality

let demoScenarios = [];

document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const fileInput = document.getElementById('csv-upload');
    const fileLabel = document.querySelector('.file-text');
    
    if (fileInput && fileLabel) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'Choose CSV file...';
            fileLabel.textContent = fileName;
        });
    }
    
    // Form submission handling
    const form = document.getElementById('bharatsignal-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('csv-upload');
            const loadingOverlay = document.getElementById('loading-overlay');
            const uploadStatus = document.getElementById('upload-status');
            const statusText = document.getElementById('status-text');
            
            if (!fileInput.files[0]) {
                e.preventDefault();
                alert('Please select a CSV file to upload.');
                return;
            }
            
            // Show upload status
            if (uploadStatus) {
                uploadStatus.style.display = 'block';
                statusText.textContent = 'Reading CSV file...';
                
                // Update status messages
                setTimeout(() => {
                    statusText.textContent = 'Analyzing your sales data...';
                }, 1000);
                
                setTimeout(() => {
                    statusText.textContent = 'Generating AI recommendations...';
                }, 2000);
            }
            
            // Show loading overlay
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        });
    }
    
    // Load demo scenarios
    loadDemoScenarios();
    
    // Initialize decision board if on results page
    if (document.getElementById('recommendations-section')) {
        initializeDecisionBoard();
    }
});

// ===== NEW DECISION BOARD FUNCTIONS =====

function initializeDecisionBoard() {
    // Set up keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            askAIQuestion();
        }
    });
    
    // Auto-focus on question input
    const questionInput = document.getElementById('ai-question-input');
    if (questionInput) {
        questionInput.focus();
    }
}

function askSuggestedQuestion(question) {
    const questionInput = document.getElementById('ai-question-input');
    if (questionInput) {
        questionInput.value = question;
    }
    askAIQuestion();
}

function selectQuestion(question) {
    askSuggestedQuestion(question);
}

function askAIQuestion() {
    const questionInput = document.getElementById('ai-question-input');
    const question = questionInput.value.trim();
    
    if (!question) {
        alert('Please enter your question about the business.');
        questionInput.focus();
        return;
    }
    
    // Update question context header
    const currentQuestionElement = document.getElementById('current-question');
    if (currentQuestionElement) {
        currentQuestionElement.textContent = `"${question}"`;
    }
    
    // Show loading state
    showLoadingState();
    
    // Send question to server
    console.log('Sending question:', question);
    console.log('Sales data count:', window.salesData ? window.salesData.length : 0);
    console.log('Context data:', window.contextData);
    if (window.salesData && window.salesData.length > 0) {
        console.log('Sample sales data:', window.salesData.slice(0, 3));
    }
    
    fetch('/ask_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            question: question,
            sales_data: window.salesData || [],
            context: window.contextData || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingState();
        
        if (data.success && data.answer) {
            updateRecommendationCards(data.answer);
            updateSuggestedQuestions(data.answer);
        } else {
            // Use fallback answer
            const fallback = data.fallback_answer || {
                primary_decision: {
                    decision: 'Yes, but be careful with quantities.',
                    item: 'General Business',
                    action: 'Check last week\'s top 3 items and increase stock by 10% only.',
                    why: 'When data is limited, small increases on fast-moving items reduce risk.',
                    confidence: 'Low',
                    based_on: ['Limited data available']
                },
                suggested_questions: [
                    'Which items are selling slowly?',
                    'What should I reduce this week?',
                    'What about weather impact?'
                ]
            };
            updateRecommendationCards(fallback);
            updateSuggestedQuestions(fallback);
        }
        
        // Clear input
        questionInput.value = '';
    })
    .catch(error => {
        console.error('Error asking question:', error);
        hideLoadingState();
        
        // Show error fallback
        const errorFallback = {
            primary_decision: {
                decision: 'Yes, but use conservative approach.',
                item: 'Service Error',
                action: 'Focus on your best-selling items and increase by 10% maximum.',
                why: 'When AI service is unavailable, stick to proven sellers with small increases.',
                confidence: 'Low',
                based_on: ['Conservative business practices']
            },
            suggested_questions: [
                'Which items are selling slowly?',
                'What should I reduce this week?',
                'What about weather impact?'
            ]
        };
        updateRecommendationCards(errorFallback);
    });
}

function updateRecommendationCards(responseData) {
    const decision = responseData.primary_decision || responseData;
    
    // Update primary decision card
    const primaryDecisionElement = document.getElementById('primary-decision');
    const primaryActionElement = document.getElementById('primary-action');
    const primaryWhyElement = document.getElementById('primary-why');
    const primaryConfidenceElement = document.getElementById('primary-confidence');
    const primaryBasedOnElement = document.getElementById('primary-based-on');
    
    if (primaryDecisionElement) {
        primaryDecisionElement.textContent = decision.decision || 'Decision pending';
        primaryDecisionElement.className = 'decision-text-bold';
    }
    
    if (primaryActionElement) {
        primaryActionElement.textContent = decision.action || 'No specific action';
    }
    
    if (primaryWhyElement) {
        primaryWhyElement.textContent = decision.why || 'Analysis in progress';
    }
    
    if (primaryConfidenceElement) {
        primaryConfidenceElement.textContent = decision.confidence || 'Medium';
        primaryConfidenceElement.className = `confidence-${(decision.confidence || 'medium').toLowerCase().replace(/[^a-z]/g, '')}`;
    }
    
    if (primaryBasedOnElement) {
        const basedOnText = decision.based_on ? 
            (Array.isArray(decision.based_on) ? decision.based_on.join(', ') : decision.based_on) : 
            'Available data';
        primaryBasedOnElement.textContent = basedOnText;
    }
    
    // Update sales summary points
    const salesSummaryElement = document.getElementById('sales-summary-points');
    if (salesSummaryElement && decision.recent_sales_summary) {
        salesSummaryElement.innerHTML = '';
        decision.recent_sales_summary.forEach(point => {
            const li = document.createElement('li');
            li.textContent = point;
            salesSummaryElement.appendChild(li);
        });
    }
    
    // Update supporting signals
    const supportingSignalsElement = document.getElementById('supporting-signals-list');
    if (supportingSignalsElement && responseData.supporting_signals) {
        supportingSignalsElement.innerHTML = '';
        responseData.supporting_signals.forEach(signal => {
            const li = document.createElement('li');
            li.textContent = signal;
            supportingSignalsElement.appendChild(li);
        });
    }
    
    // Update risk and safety
    const riskSafetyElement = document.getElementById('risk-safety-list');
    if (riskSafetyElement && responseData.risk_and_safety) {
        riskSafetyElement.innerHTML = '';
        responseData.risk_and_safety.forEach(risk => {
            const li = document.createElement('li');
            li.textContent = risk;
            riskSafetyElement.appendChild(li);
        });
    }
    
    // Add visual feedback
    const cards = document.querySelectorAll('.recommendation-card');
    cards.forEach(card => {
        card.style.transform = 'scale(1.02)';
        card.style.transition = 'transform 0.3s ease';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 300);
    });
}

function updateSuggestedQuestions(responseData) {
    const suggestedChipsContainer = document.getElementById('suggested-questions-chips');
    if (!suggestedChipsContainer) return;
    
    // Use suggested questions from the response
    let suggestions = responseData.suggested_questions || [];
    
    // Fallback suggestions if none provided
    if (suggestions.length === 0) {
        const decision = responseData.primary_decision || responseData;
        const item = decision.item ? decision.item.toLowerCase() : '';
        
        if (item.includes('rice')) {
            suggestions = [
                'Should I stock more oil for cooking?',
                'What about dal and spices?',
                'Should I reduce rice prices?'
            ];
        } else if (item.includes('oil')) {
            suggestions = [
                'Should I increase rice stock too?',
                'What about ghee for festival?',
                'Should I stock more spices?'
            ];
        } else if (item.includes('stock overview')) {
            suggestions = [
                'Which items should I restock first?',
                'What items are moving slowly?',
                'Should I reduce any stock to save money?'
            ];
        } else {
            suggestions = [
                'Which items are selling slowly?',
                'What should I reduce this week?',
                'Tell me about my stock'
            ];
        }
    }
    
    // Update suggestion chips
    suggestedChipsContainer.innerHTML = '';
    suggestions.slice(0, 5).forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'question-chip';
        chip.textContent = suggestion;
        chip.onclick = () => askSuggestedQuestion(suggestion);
        suggestedChipsContainer.appendChild(chip);
    });
}

function updateRecommendations(responseData) {
    const recommendationsSection = document.getElementById('recommendations-section');
    const cards = recommendationsSection.querySelectorAll('.recommendation-card');
    
    // If we have multiple cards, update the first one
    // In a full implementation, you might want to update all or create new ones
    const targetCard = cards[0];
    
    if (!targetCard) {
        // Create a new card if none exist
        createNewRecommendationCard(responseData);
        return;
    }
    
    // Fade out old content
    targetCard.style.opacity = '0.5';
    targetCard.style.transition = 'opacity 0.3s ease';
    
    setTimeout(() => {
        // Update card content with new JSON structure
        const productElement = targetCard.querySelector('.rec-product');
        const salesSummaryElement = targetCard.querySelector('.sales-summary-text');
        const decisionElement = targetCard.querySelector('.decision-text-bold');
        const actionElement = targetCard.querySelector('.action-text');
        const whyElement = targetCard.querySelector('.why-text');
        const confidenceElement = targetCard.querySelector('.confidence-text');
        const basedOnElement = targetCard.querySelector('.based-on-text');
        
        // Extract data from new JSON structure
        const decision = responseData.primary_decision || responseData;
        
        if (productElement) productElement.textContent = decision.item || responseData.title || 'Business Decision';
        if (salesSummaryElement) {
            const summaryText = decision.recent_sales_summary ? 
                decision.recent_sales_summary.join(' | ') : 
                'Analysis updated based on your question';
            salesSummaryElement.textContent = summaryText;
        }
        if (decisionElement) decisionElement.textContent = decision.decision || 'Decision pending';
        if (actionElement) actionElement.textContent = decision.action || 'No specific action';
        if (whyElement) whyElement.textContent = decision.why || 'Analysis in progress';
        if (confidenceElement) {
            confidenceElement.textContent = decision.confidence || 'Medium';
            confidenceElement.className = `confidence-text confidence-${(decision.confidence || 'medium').toLowerCase().replace(/[^a-z]/g, '')}`;
        }
        if (basedOnElement) {
            const basedOnText = decision.based_on ? 
                (Array.isArray(decision.based_on) ? decision.based_on.join(', ') : decision.based_on) : 
                'Available data';
            basedOnElement.textContent = basedOnText;
        }
        
        // Fade in new content
        targetCard.style.opacity = '1';
        
        // Add updated indicator
        addUpdatedIndicator(targetCard);
        
    }, 300);
}

function createNewRecommendationCard(responseData) {
    const recommendationsSection = document.getElementById('recommendations-section');
    const decision = responseData.primary_decision || responseData;
    
    const cardHTML = `
        <div class="recommendation-card updated-card" data-card-index="0">
            <div class="rec-header">
                <span class="rec-icon">🎯</span>
                <h3 class="rec-product">${decision.item || responseData.title || 'Business Decision'}</h3>
                <span class="updated-badge">Updated</span>
            </div>
            
            <div class="rec-sales-summary">
                <strong>Recent Sales:</strong> <span class="sales-summary-text">${decision.recent_sales_summary ? decision.recent_sales_summary.join(' | ') : 'Analysis updated based on your question'}</span>
            </div>
            
            <div class="rec-decision decision-field-highlight">
                <strong>Decision:</strong> <span class="decision-text-bold">${decision.decision || 'Decision pending'}</span>
            </div>
            
            <div class="rec-action">
                <strong>Action:</strong> <span class="action-text">${decision.action || 'No specific action'}</span>
            </div>
            
            <div class="rec-explanation">
                <strong>Why:</strong> <span class="why-text">${decision.why || 'Analysis in progress'}</span>
            </div>
            
            <div class="rec-confidence">
                <strong>Confidence:</strong> <span class="confidence-text confidence-${(decision.confidence || 'medium').toLowerCase().replace(/[^a-z]/g, '')}">${decision.confidence || 'Medium'}</span>
            </div>
            
            <div class="rec-based-on">
                <strong>Based on:</strong> <span class="based-on-text">${decision.based_on ? (Array.isArray(decision.based_on) ? decision.based_on.join(', ') : decision.based_on) : 'Available data'}</span>
            </div>
        </div>
    `;
    
    recommendationsSection.innerHTML = cardHTML;
}

function addUpdatedIndicator(card) {
    // Remove existing updated indicators
    const existingBadge = card.querySelector('.updated-badge');
    if (existingBadge) {
        existingBadge.remove();
    }
    
    // Add updated badge
    const header = card.querySelector('.rec-header');
    const badge = document.createElement('span');
    badge.className = 'updated-badge';
    badge.textContent = 'Updated';
    header.appendChild(badge);
    
    // Remove badge after 5 seconds
    setTimeout(() => {
        if (badge.parentNode) {
            badge.remove();
        }
    }, 5000);
}

function showLoadingState() {
    const loadingState = document.getElementById('loading-state');
    const askBtn = document.getElementById('ask-ai-btn');
    
    if (loadingState) {
        loadingState.style.display = 'flex';
    }
    
    if (askBtn) {
        askBtn.disabled = true;
        askBtn.textContent = 'Analyzing...';
    }
    
    // Blur recommendation cards
    const cards = document.querySelectorAll('.recommendation-card');
    cards.forEach(card => {
        card.style.filter = 'blur(2px)';
        card.style.opacity = '0.7';
    });
}

function hideLoadingState() {
    const loadingState = document.getElementById('loading-state');
    const askBtn = document.getElementById('ask-ai-btn');
    
    if (loadingState) {
        loadingState.style.display = 'none';
    }
    
    if (askBtn) {
        askBtn.disabled = false;
        askBtn.textContent = 'Ask AI';
    }
    
    // Unblur recommendation cards
    const cards = document.querySelectorAll('.recommendation-card');
    cards.forEach(card => {
        card.style.filter = 'none';
        card.style.opacity = '1';
    });
}

function generateSuggestedQuestions(responseData) {
    const suggestedSection = document.getElementById('suggested-questions-section');
    const chipsContainer = document.getElementById('suggestion-chips');
    
    if (!suggestedSection || !chipsContainer) return;
    
    // Use suggested questions from the response
    let suggestions = responseData.suggested_questions || [];
    
    // Fallback suggestions if none provided
    if (suggestions.length === 0) {
        const decision = responseData.primary_decision || responseData;
        const item = decision.item ? decision.item.toLowerCase() : '';
        const responseText = (decision.decision + ' ' + decision.action + ' ' + decision.why).toLowerCase();
        
        if (item.includes('rice') || responseText.includes('rice')) {
            suggestions = [
                'Should I stock more oil for cooking?',
                'What about dal and spices?',
                'Should I reduce rice prices?'
            ];
        } else if (item.includes('oil') || responseText.includes('oil')) {
            suggestions = [
                'Should I increase rice stock too?',
                'What about ghee for festival?',
                'Should I stock more spices?'
            ];
        } else if (item.includes('tea') || responseText.includes('tea')) {
            suggestions = [
                'Should I reduce cold drinks?',
                'What about biscuits and snacks?',
                'Should I stock more milk?'
            ];
        } else {
            suggestions = [
                'Which items are selling slowly?',
                'What should I reduce this week?',
                'What about weather impact?'
            ];
        }
    }
    
    // Create suggestion chips
    chipsContainer.innerHTML = '';
    suggestions.slice(0, 3).forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.onclick = () => {
            document.getElementById('ai-question-input').value = suggestion;
            askAIQuestion();
        };
        chipsContainer.appendChild(chip);
    });
    
    // Show the section
    suggestedSection.style.display = 'block';
}

// ===== DEMO SCENARIOS FUNCTIONALITY =====

async function loadDemoScenarios() {
    try {
        const response = await fetch('/demo/scenarios');
        const data = await response.json();
        
        if (data.success && data.scenarios) {
            demoScenarios = data.scenarios;
            populateScenarioSelector(data.scenarios);
        } else {
            console.error('Failed to load demo scenarios:', data.error);
            populateScenarioSelector([]);
        }
    } catch (error) {
        console.error('Error loading demo scenarios:', error);
        populateScenarioSelector([]);
    }
}

function populateScenarioSelector(scenarios) {
    const selector = document.getElementById('scenario-select');
    if (!selector) return;
    
    selector.innerHTML = '';
    
    if (scenarios.length === 0) {
        selector.innerHTML = '<option value="">No demo scenarios available</option>';
        return;
    }
    
    // Add default option
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Select a scenario...';
    selector.appendChild(defaultOption);
    
    // Add scenario options
    scenarios.forEach(scenario => {
        const option = document.createElement('option');
        option.value = scenario.name;
        option.textContent = scenario.name;
        selector.appendChild(option);
    });
}

async function loadSelectedScenario() {
    const selector = document.getElementById('scenario-select');
    const scenarioName = selector.value;
    
    if (!scenarioName) {
        alert('Please select a demo scenario first.');
        return;
    }
    
    try {
        // Show loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
        }
        
        // Load scenario context first
        const contextResponse = await fetch(`/demo/context/${encodeURIComponent(scenarioName)}`);
        const contextData = await contextResponse.json();
        
        if (contextData.success) {
            // Populate context field
            const contextInput = document.getElementById('context-input');
            if (contextInput) {
                contextInput.value = contextData.context;
            }
            
            // Update file label to indicate demo mode
            const fileLabel = document.querySelector('.file-text');
            if (fileLabel) {
                fileLabel.textContent = `Demo: ${scenarioName} (sample data will be used)`;
            }
            
            // Load the demo scenario and get recommendations
            const response = await fetch(`/demo/load/${encodeURIComponent(scenarioName)}`, {
                method: 'POST'
            });
            
            if (response.ok) {
                // Redirect to results page
                const resultHtml = await response.text();
                document.open();
                document.write(resultHtml);
                document.close();
            } else {
                throw new Error('Failed to load demo scenario');
            }
        } else {
            throw new Error(contextData.error || 'Failed to load scenario context');
        }
        
    } catch (error) {
        console.error('Error loading demo scenario:', error);
        alert('Failed to load demo scenario. Please try again.');
        
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
}

function downloadSampleCSV() {
    const selector = document.getElementById('scenario-select');
    const scenarioName = selector.value || 'Regular Business Days';
    
    // Create CSV content based on scenario
    let csvContent = '';
    
    if (scenarioName.includes('Festival') || scenarioName.includes('Diwali')) {
        csvContent = `date,item,quantity,price
2024-10-15,Rice 5kg,25,220.00
2024-10-15,Dal Toor 1kg,18,125.00
2024-10-15,Ghee 500ml,12,280.00
2024-10-15,Sugar 1kg,20,45.00
2024-10-15,Oil 1L,15,155.00
2024-10-15,Sweets Mix 500g,30,180.00
2024-10-15,Dry Fruits 250g,8,450.00
2024-10-15,Candles Pack,25,35.00
2024-10-15,Incense Sticks,40,15.00
2024-10-16,Rice 5kg,22,220.00
2024-10-16,Flour 5kg,18,190.00
2024-10-16,Milk 1L,35,55.00
2024-10-16,Sweets Mix 500g,28,180.00
2024-10-16,Oil 1L,20,155.00
2024-10-16,Decorative Items,15,85.00`;
    } else if (scenarioName.includes('Monsoon')) {
        csvContent = `date,item,quantity,price
2024-07-15,Tea 250g,25,88.00
2024-07-15,Biscuits Pack,35,26.00
2024-07-15,Instant Noodles,20,15.00
2024-07-15,Bread,18,24.00
2024-07-15,Milk 500ml,30,29.00
2024-07-15,Ginger 100g,8,45.00
2024-07-15,Honey 250ml,5,185.00
2024-07-16,Tea 250g,28,88.00
2024-07-16,Coffee 100g,12,165.00
2024-07-16,Biscuits Pack,40,26.00
2024-07-16,Instant Noodles,25,15.00
2024-07-16,Hot Snacks Mix,15,45.00`;
    } else {
        csvContent = `date,item,quantity,price
2024-03-15,Rice 1kg,12,46.00
2024-03-15,Dal Toor 1kg,8,122.00
2024-03-15,Oil 1L,6,152.00
2024-03-15,Sugar 1kg,10,43.00
2024-03-15,Tea 250g,15,86.00
2024-03-15,Milk 500ml,25,28.50
2024-03-15,Bread,12,23.00
2024-03-15,Biscuits Pack,18,25.50
2024-03-15,Onion 1kg,20,38.00
2024-03-15,Potato 1kg,18,32.00`;
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sample_${scenarioName.toLowerCase().replace(/\s+/g, '_')}_sales.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    showSuccess(`Downloaded sample CSV for: ${scenarioName}`);
}

// ===== UTILITY FUNCTIONS =====

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        z-index: 1001;
        max-width: 300px;
    `;
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        document.body.removeChild(errorDiv);
    }, 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        z-index: 1001;
        max-width: 300px;
    `;
    successDiv.textContent = message;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        document.body.removeChild(successDiv);
    }, 3000);
}

function tryAnotherScenario() {
    window.location.href = '/';
}