// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Character counter for textareas
    var textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        var maxLength = textarea.getAttribute('maxlength');
        var counter = document.createElement('small');
        counter.className = 'text-muted';
        counter.style.float = 'right';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            var remaining = maxLength - textarea.value.length;
            counter.textContent = remaining + ' characters remaining';
            if (remaining < 50) {
                counter.className = 'text-warning';
            } else if (remaining < 10) {
                counter.className = 'text-danger';
            } else {
                counter.className = 'text-muted';
            }
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // Dynamic search functionality
    var searchInput = document.querySelector('#search-input');
    if (searchInput) {
        var searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(function() {
                performSearch(searchInput.value);
            }, 300);
        });
    }

    // Quiz timer functionality
    var timerElement = document.querySelector('.timer');
    if (timerElement) {
        var timeLimit = parseInt(timerElement.dataset.timeLimit) * 60; // Convert to seconds
        var startTime = Date.now();
        
        function updateTimer() {
            var elapsed = Math.floor((Date.now() - startTime) / 1000);
            var remaining = timeLimit - elapsed;
            
            if (remaining <= 0) {
                // Time's up - submit the form
                document.querySelector('#quiz-form').submit();
                return;
            }
            
            var minutes = Math.floor(remaining / 60);
            var seconds = remaining % 60;
            
            timerElement.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
            
            // Add warning classes
            if (remaining <= 300) { // 5 minutes
                timerElement.classList.add('warning');
            }
            if (remaining <= 60) { // 1 minute
                timerElement.classList.remove('warning');
                timerElement.classList.add('danger');
            }
        }
        
        updateTimer();
        setInterval(updateTimer, 1000);
    }

    // Quiz question navigation
    var questionCards = document.querySelectorAll('.question-card');
    var currentQuestion = 0;
    
    if (questionCards.length > 0) {
        showQuestion(currentQuestion);
        
        // Create navigation buttons
        var navContainer = document.createElement('div');
        navContainer.className = 'quiz-navigation';
        
        var prevBtn = document.createElement('button');
        prevBtn.type = 'button';
        prevBtn.className = 'btn btn-secondary';
        prevBtn.innerHTML = '<i class="fas fa-arrow-left"></i> Previous';
        prevBtn.addEventListener('click', function() {
            if (currentQuestion > 0) {
                currentQuestion--;
                showQuestion(currentQuestion);
            }
        });
        
        var nextBtn = document.createElement('button');
        nextBtn.type = 'button';
        nextBtn.className = 'btn btn-primary';
        nextBtn.innerHTML = 'Next <i class="fas fa-arrow-right"></i>';
        nextBtn.addEventListener('click', function() {
            if (currentQuestion < questionCards.length - 1) {
                currentQuestion++;
                showQuestion(currentQuestion);
            }
        });
        
        var submitBtn = document.createElement('button');
        submitBtn.type = 'submit';
        submitBtn.className = 'btn btn-success';
        submitBtn.innerHTML = '<i class="fas fa-check"></i> Submit Quiz';
        submitBtn.style.display = 'none';
        
        navContainer.appendChild(prevBtn);
        navContainer.appendChild(nextBtn);
        navContainer.appendChild(submitBtn);
        
        var lastQuestion = questionCards[questionCards.length - 1];
        lastQuestion.appendChild(navContainer);
        
        // Create question indicator
        var indicator = document.createElement('div');
        indicator.className = 'question-indicator';
        
        for (var i = 0; i < questionCards.length; i++) {
            var dot = document.createElement('span');
            dot.className = 'question-dot';
            dot.dataset.question = i;
            dot.addEventListener('click', function() {
                currentQuestion = parseInt(this.dataset.question);
                showQuestion(currentQuestion);
            });
            indicator.appendChild(dot);
        }
        
        questionCards[0].parentNode.insertBefore(indicator, questionCards[0]);
        
        function showQuestion(index) {
            questionCards.forEach(function(card, i) {
                card.style.display = i === index ? 'block' : 'none';
            });
            
            // Update navigation buttons
            prevBtn.style.display = index === 0 ? 'none' : 'inline-block';
            nextBtn.style.display = index === questionCards.length - 1 ? 'none' : 'inline-block';
            submitBtn.style.display = index === questionCards.length - 1 ? 'inline-block' : 'none';
            
            // Update indicator
            var dots = document.querySelectorAll('.question-dot');
            dots.forEach(function(dot, i) {
                dot.classList.remove('current');
                if (i === index) {
                    dot.classList.add('current');
                }
            });
        }
    }

    // Progress bar for quiz
    var progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        var totalQuestions = questionCards.length;
        var answeredQuestions = 0;
        
        function updateProgress() {
            var percentage = (answeredQuestions / totalQuestions) * 100;
            progressBar.style.width = percentage + '%';
            progressBar.setAttribute('aria-valuenow', percentage);
        }
        
        // Listen for answer changes
        var inputs = document.querySelectorAll('input[type="radio"], input[type="checkbox"]');
        inputs.forEach(function(input) {
            input.addEventListener('change', function() {
                var questionId = this.name.split('_')[1];
                var questionAnswered = document.querySelector('input[name="' + this.name + '"]:checked');
                
                if (questionAnswered) {
                    var dot = document.querySelector('.question-dot[data-question="' + (parseInt(questionId) - 1) + '"]');
                    if (dot && !dot.classList.contains('answered')) {
                        dot.classList.add('answered');
                        answeredQuestions++;
                        updateProgress();
                    }
                }
            });
        });
    }

    // Confirmation dialogs
    var deleteButtons = document.querySelectorAll('.btn-danger[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            var message = this.dataset.confirm || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-save functionality for forms
    var autoSaveForms = document.querySelectorAll('.auto-save');
    autoSaveForms.forEach(function(form) {
        var inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(function(input) {
            input.addEventListener('input', function() {
                var formData = new FormData(form);
                localStorage.setItem('autosave_' + form.id, JSON.stringify(Object.fromEntries(formData)));
            });
        });
        
        // Load saved data on page load
        var savedData = localStorage.getItem('autosave_' + form.id);
        if (savedData) {
            var data = JSON.parse(savedData);
            Object.keys(data).forEach(function(key) {
                var input = form.querySelector('[name="' + key + '"]');
                if (input) {
                    input.value = data[key];
                }
            });
        }
    });

    // Lazy loading for images
    var lazyImages = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Mobile navigation enhancement
    var navToggle = document.querySelector('.navbar-toggler');
    if (navToggle) {
        navToggle.addEventListener('click', function() {
            var navCollapse = document.querySelector('.navbar-collapse');
            if (navCollapse.classList.contains('show')) {
                navCollapse.classList.remove('show');
            } else {
                navCollapse.classList.add('show');
            }
        });
    }
});

// Utility functions
function performSearch(query) {
    if (query.length < 2) return;
    
    fetch('/search-creators/?q=' + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            var resultsContainer = document.querySelector('#search-results');
            if (resultsContainer) {
                resultsContainer.innerHTML = '';
                data.creators.forEach(function(creator) {
                    var item = document.createElement('div');
                    item.className = 'list-group-item';
                    item.textContent = creator.username;
                    item.addEventListener('click', function() {
                        document.querySelector('#search-input').value = creator.username;
                        resultsContainer.innerHTML = '';
                    });
                    resultsContainer.appendChild(item);
                });
            }
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function showNotification(message, type = 'info') {
    var notification = document.createElement('div');
    notification.className = 'alert alert-' + type + ' alert-dismissible fade show';
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, 5000);
}

function formatTime(seconds) {
    var minutes = Math.floor(seconds / 60);
    var remainingSeconds = seconds % 60;
    return minutes + ':' + (remainingSeconds < 10 ? '0' : '') + remainingSeconds;
}

function debounce(func, wait) {
    var timeout;
    return function executedFunction(...args) {
        var later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
