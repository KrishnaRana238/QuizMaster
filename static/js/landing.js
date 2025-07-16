// Landing Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Animate statistics counters
    animateCounters();
    
    // Initialize intersection observer for animations
    initializeScrollAnimations();
    
    // Add floating effect to hero elements
    initializeFloatingEffects();
    
    // Initialize typing effect
    initializeTypingEffect();
    
    // Add particles effect
    initializeParticles();
});

function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.dataset.count);
                const duration = 2000; // 2 seconds
                const step = target / (duration / 16); // 60 FPS
                let current = 0;
                
                const timer = setInterval(() => {
                    current += step;
                    if (current >= target) {
                        counter.textContent = target.toLocaleString();
                        clearInterval(timer);
                    } else {
                        counter.textContent = Math.floor(current).toLocaleString();
                    }
                }, 16);
                
                observer.unobserve(counter);
            }
        });
    }, observerOptions);
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

function initializeScrollAnimations() {
    const animatedElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    // Add classes to elements that should be animated
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach((card, index) => {
        card.classList.add('fade-in-up');
        card.style.animationDelay = `${index * 0.2}s`;
    });
}

function initializeFloatingEffects() {
    const floatingElements = document.querySelectorAll('.floating-quiz, .feature-icon');
    
    floatingElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 0.5}s`;
        
        // Add mouse interaction
        element.addEventListener('mouseenter', () => {
            element.style.animationPlayState = 'paused';
            element.style.transform = 'translateY(-10px) scale(1.05)';
        });
        
        element.addEventListener('mouseleave', () => {
            element.style.animationPlayState = 'running';
            element.style.transform = '';
        });
    });
}

function initializeTypingEffect() {
    const typingElement = document.querySelector('.typing-text');
    if (!typingElement) return;
    
    const texts = [
        'Create Amazing Quizzes',
        'Challenge Your Knowledge',
        'Compete with Friends',
        'Track Your Progress'
    ];
    
    let textIndex = 0;
    let charIndex = 0;
    let isDeleting = false;
    
    function type() {
        const currentText = texts[textIndex];
        
        if (isDeleting) {
            typingElement.textContent = currentText.substring(0, charIndex - 1);
            charIndex--;
        } else {
            typingElement.textContent = currentText.substring(0, charIndex + 1);
            charIndex++;
        }
        
        if (!isDeleting && charIndex === currentText.length) {
            setTimeout(() => {
                isDeleting = true;
            }, 2000);
        } else if (isDeleting && charIndex === 0) {
            isDeleting = false;
            textIndex = (textIndex + 1) % texts.length;
        }
        
        const speed = isDeleting ? 50 : 100;
        setTimeout(type, speed);
    }
    
    type();
}

function initializeParticles() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const heroSection = document.querySelector('.hero-section');
    
    if (!heroSection) return;
    
    canvas.style.position = 'absolute';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '1';
    
    heroSection.appendChild(canvas);
    
    let particles = [];
    const particleCount = 50;
    
    function resizeCanvas() {
        canvas.width = heroSection.offsetWidth;
        canvas.height = heroSection.offsetHeight;
    }
    
    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            radius: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.3
        };
    }
    
    function initParticles() {
        particles = [];
        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle());
        }
    }
    
    function updateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > canvas.width) {
                particle.vx = -particle.vx;
            }
            if (particle.y < 0 || particle.y > canvas.height) {
                particle.vy = -particle.vy;
            }
        });
    }
    
    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(255, 255, 255, ${particle.opacity})`;
            ctx.fill();
        });
        
        // Draw connections between nearby particles
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 * (1 - distance / 100)})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            });
        });
    }
    
    function animate() {
        updateParticles();
        drawParticles();
        requestAnimationFrame(animate);
    }
    
    resizeCanvas();
    initParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });
}

// Smooth scrolling for CTA buttons
document.querySelectorAll('.cta-buttons a').forEach(button => {
    button.addEventListener('click', function(e) {
        if (this.getAttribute('href').startsWith('#')) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    });
});

// Interactive quiz demo
document.addEventListener('DOMContentLoaded', function() {
    const quizDemo = document.querySelector('.quiz-card');
    if (quizDemo) {
        const options = quizDemo.querySelectorAll('.option');
        const correctOption = quizDemo.querySelector('.option.correct');
        
        options.forEach(option => {
            option.addEventListener('click', function() {
                // Remove previous selections
                options.forEach(opt => opt.classList.remove('selected', 'show-correct'));
                
                // Add selection
                this.classList.add('selected');
                
                // Show correct answer after a delay
                setTimeout(() => {
                    correctOption.classList.add('show-correct');
                    options.forEach(opt => {
                        if (opt !== correctOption) {
                            opt.style.opacity = '0.5';
                        }
                    });
                }, 500);
                
                // Reset after 2 seconds
                setTimeout(() => {
                    options.forEach(opt => {
                        opt.classList.remove('selected', 'show-correct');
                        opt.style.opacity = '1';
                    });
                }, 2500);
            });
        });
    }
});

// Parallax effect for hero section
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        const rate = scrolled * -0.5;
        heroSection.style.transform = `translateY(${rate}px)`;
    }
});

// Add loading animation
function showLoading() {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.innerHTML = `
        <div class="loading-spinner-container">
            <div class="loading-spinner"></div>
            <p>Loading...</p>
        </div>
    `;
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        flex-direction: column;
    `;
    
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.getElementById('loading-overlay');
    if (loading) {
        loading.remove();
    }
}

// Performance optimization
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimized scroll handler
const optimizedScrollHandler = debounce(function() {
    const scrolled = window.pageYOffset;
    const heroSection = document.querySelector('.hero-section');
    
    if (heroSection) {
        const rate = scrolled * -0.5;
        heroSection.style.transform = `translateY(${rate}px)`;
    }
}, 16);

window.addEventListener('scroll', optimizedScrollHandler);

// Add CSS for new elements
const style = document.createElement('style');
style.textContent = `
    .loading-spinner-container {
        text-align: center;
        color: #667eea;
    }
    
    .loading-spinner-container p {
        margin-top: 20px;
        font-size: 1.2rem;
        font-weight: 500;
    }
    
    .option.selected {
        background: rgba(13, 110, 253, 0.2);
        border-color: #0d6efd;
        transform: scale(1.02);
    }
    
    .option.show-correct {
        background: rgba(40, 167, 69, 0.3);
        border-color: #28a745;
        animation: correctPulse 0.5s ease-in-out;
    }
    
    @keyframes correctPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);
