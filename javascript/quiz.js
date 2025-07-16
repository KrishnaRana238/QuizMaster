// JavaScript for quiz functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize quiz creation form
    initializeQuizCreation();
    
    // Initialize question adding functionality
    initializeQuestionAdding();
    
    // Initialize quiz taking functionality
    initializeQuizTaking();
    
    // Initialize search functionality
    initializeSearch();
});

function initializeQuizCreation() {
    const createQuizForm = document.querySelector('#create-quiz-form');
    if (createQuizForm) {
        createQuizForm.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
            submitButton.disabled = true;
        });
    }
}

function initializeQuestionAdding() {
    const questionTypeSelect = document.querySelector('#question-type-select');
    const choicesContainer = document.querySelector('#choices-container');
    const tfContainer = document.querySelector('#tf-container');
    
    if (questionTypeSelect) {
        questionTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            
            // Hide all containers first
            if (choicesContainer) choicesContainer.style.display = 'none';
            if (tfContainer) tfContainer.style.display = 'none';
            
            // Show appropriate container
            if (selectedType === 'mc' && choicesContainer) {
                choicesContainer.style.display = 'block';
            } else if (selectedType === 'tf' && tfContainer) {
                tfContainer.style.display = 'block';
            }
        });
        
        // Trigger change event on page load
        questionTypeSelect.dispatchEvent(new Event('change'));
    }
}

function initializeQuizTaking() {
    const quizForm = document.querySelector('#quiz-form');
    const timerElement = document.querySelector('.timer');
    
    if (quizForm && timerElement) {
        const timeLimit = parseInt(timerElement.dataset.timeLimit) * 60;
        let timeRemaining = timeLimit;
        
        // Timer functionality
        const timerInterval = setInterval(() => {
            if (timeRemaining <= 0) {
                clearInterval(timerInterval);
                alert('Time is up! The quiz will be submitted automatically.');
                quizForm.submit();
                return;
            }
            
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = timeRemaining % 60;
            timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Add warning classes
            if (timeRemaining <= 300) { // 5 minutes
                timerElement.classList.add('warning');
            }
            if (timeRemaining <= 60) { // 1 minute
                timerElement.classList.remove('warning');
                timerElement.classList.add('danger');
            }
            
            timeRemaining--;
        }, 1000);
        
        // Form submission handling
        quizForm.addEventListener('submit', function(e) {
            clearInterval(timerInterval);
            
            const submitButton = this.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
            submitButton.disabled = true;
            
            // Optional confirmation
            const unansweredQuestions = this.querySelectorAll('.question-card:not([data-answered])').length;
            if (unansweredQuestions > 0) {
                if (!confirm(`You have ${unansweredQuestions} unanswered question(s). Are you sure you want to submit?`)) {
                    e.preventDefault();
                    submitButton.innerHTML = '<i class="fas fa-paper-plane"></i> Submit Quiz';
                    submitButton.disabled = false;
                    return;
                }
            }
        });
        
        // Choice selection handling
        const choiceOptions = document.querySelectorAll('.choice-option');
        choiceOptions.forEach(option => {
            option.addEventListener('click', function() {
                const input = this.querySelector('input[type="radio"]');
                if (input) {
                    input.checked = true;
                    
                    // Update visual selection
                    const questionCard = this.closest('.question-card');
                    const allChoices = questionCard.querySelectorAll('.choice-option');
                    allChoices.forEach(choice => choice.classList.remove('selected'));
                    this.classList.add('selected');
                    
                    // Mark question as answered
                    questionCard.dataset.answered = 'true';
                    
                    // Update progress
                    updateQuizProgress();
                }
            });
        });
        
        // Prevent accidental page leave
        window.addEventListener('beforeunload', function(e) {
            e.preventDefault();
            e.returnValue = '';
        });
    }
}

function updateQuizProgress() {
    const progressBar = document.querySelector('.progress-bar');
    const progressText = document.querySelector('#progress-text');
    
    if (progressBar && progressText) {
        const totalQuestions = document.querySelectorAll('.question-card').length;
        const answeredQuestions = document.querySelectorAll('.question-card[data-answered]').length;
        const percentage = (answeredQuestions / totalQuestions) * 100;
        
        progressBar.style.width = percentage + '%';
        progressBar.setAttribute('aria-valuenow', percentage);
        progressText.textContent = `${answeredQuestions} / ${totalQuestions}`;
    }
}

function initializeSearch() {
    const searchInput = document.querySelector('#search-input');
    const searchButton = document.querySelector('.btn-search');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performCreatorSearch(query);
                }, 300);
            } else {
                hideSearchResults();
            }
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                searchQuizzes();
            }
        });
    }
}

function performCreatorSearch(query) {
    fetch(`/search-creators/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showSearchResults(data.creators);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function showSearchResults(creators) {
    let resultsContainer = document.querySelector('#search-results');
    
    if (!resultsContainer) {
        resultsContainer = document.createElement('div');
        resultsContainer.id = 'search-results';
        resultsContainer.className = 'search-results';
        
        const searchInput = document.querySelector('#search-input');
        searchInput.parentNode.appendChild(resultsContainer);
    }
    
    resultsContainer.innerHTML = '';
    
    if (creators.length > 0) {
        const list = document.createElement('ul');
        list.className = 'list-group';
        
        creators.forEach(creator => {
            const item = document.createElement('li');
            item.className = 'list-group-item list-group-item-action';
            item.textContent = creator.username;
            item.addEventListener('click', function() {
                document.querySelector('#search-input').value = creator.username;
                hideSearchResults();
            });
            list.appendChild(item);
        });
        
        resultsContainer.appendChild(list);
        resultsContainer.style.display = 'block';
    } else {
        resultsContainer.style.display = 'none';
    }
}

function hideSearchResults() {
    const resultsContainer = document.querySelector('#search-results');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

function searchQuizzes() {
    const searchInput = document.querySelector('#search-input');
    const creator = searchInput.value.trim();
    
    if (creator) {
        window.location.href = `${window.location.pathname}?creator=${encodeURIComponent(creator)}`;
    } else {
        window.location.href = window.location.pathname;
    }
}

// Utility functions for quiz functionality
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Auto-save functionality for forms
function enableAutoSave(formId) {
    const form = document.querySelector(`#${formId}`);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            const formData = new FormData(form);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            localStorage.setItem(`autosave_${formId}`, JSON.stringify(data));
        });
    });
    
    // Load saved data on page load
    const savedData = localStorage.getItem(`autosave_${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && input.type !== 'radio') {
                input.value = data[key];
            }
        });
    }
}

// Clear auto-save data after successful submission
function clearAutoSave(formId) {
    localStorage.removeItem(`autosave_${formId}`);
}

// Add CSS for search results
const searchStyles = document.createElement('style');
searchStyles.textContent = `
    .search-results {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 0 0 8px 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
        display: none;
    }
    
    .search-results .list-group-item {
        border: none;
        cursor: pointer;
        padding: 10px 15px;
    }
    
    .search-results .list-group-item:hover {
        background-color: #f8f9fa;
    }
    
    .timer {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 10px 15px;
        border-radius: 5px;
        background: #28a745;
        color: white;
        transition: all 0.3s ease;
    }
    
    .timer.warning {
        background: #ffc107;
        color: #000;
    }
    
    .timer.danger {
        background: #dc3545;
        color: white;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.5; }
    }
    
    .choice-option {
        cursor: pointer;
        transition: all 0.2s ease;
        border: 2px solid transparent;
        border-radius: 8px;
        padding: 12px 15px;
        margin-bottom: 8px;
        background: #f8f9fa;
    }
    
    .choice-option:hover {
        background: #e9ecef;
        border-color: #007bff;
    }
    
    .choice-option.selected {
        background: #e7f3ff;
        border-color: #007bff;
    }
    
    .choice-option input[type="radio"] {
        margin-right: 10px;
    }
    
    .question-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .question-number {
        background: #007bff;
        color: white;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-right: 15px;
        flex-shrink: 0;
    }
    
    .quiz-progress {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .progress {
        height: 8px;
        border-radius: 4px;
        background: #e9ecef;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #007bff 0%, #28a745 100%);
        border-radius: 4px;
        transition: width 0.3s ease;
    }
`;
document.head.appendChild(searchStyles);
