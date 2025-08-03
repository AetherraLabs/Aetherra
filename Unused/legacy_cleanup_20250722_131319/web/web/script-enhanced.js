// Enhanced Aetherra Project Website JavaScript
// Advanced interactive features for the AI-native development environment showcase

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all enhanced features
    initializeNavigation();
    initializeHeroAnimations();
    initializeDemoWindows();
    initializeLyrixaChat();
    initializeParticleSystem();
    initializeScrollAnimations();
    initializeInteractiveElements();
    initializeServiceWorker();

    console.log('🚀 Aetherra Enhanced Website Loaded');
});

// ============================================================================
// NAVIGATION & SCROLL HANDLING
// ============================================================================

function initializeNavigation() {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    let lastScrollY = window.scrollY;

    // Scroll-based navbar styling
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }

        // Hide/show navbar on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            navbar.classList.add('navbar-hidden');
        } else {
            navbar.classList.remove('navbar-hidden');
        }

        lastScrollY = currentScrollY;
    });

    // Mobile navigation toggle
    navToggle?.addEventListener('click', () => {
        navLinks.classList.toggle('nav-links-active');
        navToggle.classList.toggle('nav-toggle-active');
    });

    // Smooth scrolling for navigation links
    document.querySelectorAll('.nav-link[href^="#"]').forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                navLinks.classList.remove('nav-links-active');
                navToggle.classList.remove('nav-toggle-active');
            }
        });
    });
}

// ============================================================================
// HERO SECTION ANIMATIONS
// ============================================================================

function initializeHeroAnimations() {
    // Typing animation for hero tagline
    const heroTagline = document.querySelector('.title-tagline');
    if (heroTagline) {
        const text = heroTagline.textContent;
        heroTagline.textContent = '';
        heroTagline.style.borderRight = '2px solid var(--primary)';

        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTagline.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                setTimeout(() => {
                    heroTagline.style.borderRight = 'none';
                }, 1000);
            }
        };

        setTimeout(typeWriter, 2000);
    }

    // Animated counters for stats
    const statNumbers = document.querySelectorAll('.stat-number');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });

    statNumbers.forEach(stat => observer.observe(stat));
}

function animateCounter(element) {
    const target = parseInt(element.textContent);
    const duration = 2000;
    const steps = 60;
    const stepTime = duration / steps;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        element.textContent = Math.round(current);

        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        }
    }, stepTime);
}

// ============================================================================
// DEMO WINDOWS & TERMINAL SIMULATION
// ============================================================================

function initializeDemoWindows() {
    // Launcher demo animation
    const launcherDemo = document.querySelector('.launcher-demo');
    if (launcherDemo) {
        animateLauncherStartup();
    }

    // Lyrixa chat demo
    const lyrixaDemo = document.querySelector('.lyrixa-demo');
    if (lyrixaDemo) {
        setTimeout(() => animateLyrixaResponse(), 3000);
    }
}

function animateLauncherStartup() {
    const statusLines = document.querySelectorAll('.launcher-demo .status-line');

    statusLines.forEach((line, index) => {
        setTimeout(() => {
            line.style.opacity = '0';
            line.style.transform = 'translateX(-10px)';
            line.style.transition = 'all 0.3s ease';

            setTimeout(() => {
                line.style.opacity = '1';
                line.style.transform = 'translateX(0)';
            }, 50);
        }, index * 800);
    });
}

function animateLyrixaResponse() {
    const typingIndicator = document.querySelector('.typing-indicator');
    const dots = document.querySelectorAll('.typing-indicator .dots span');

    if (typingIndicator && dots.length > 0) {
        // Animate typing dots
        let dotIndex = 0;
        const animateDots = setInterval(() => {
            dots.forEach(dot => dot.style.opacity = '0.3');
            dots[dotIndex].style.opacity = '1';
            dotIndex = (dotIndex + 1) % dots.length;
        }, 500);

        // Show response after typing
        setTimeout(() => {
            clearInterval(animateDots);
            showLyrixaCodeResponse();
        }, 3000);
    }
}

function showLyrixaCodeResponse() {
    const messageContent = document.querySelector('.lyrixa-demo .message-content');
    if (messageContent) {
        messageContent.innerHTML = `
            <div class="code-generation">
                <div class="code-header">
                    <span class="code-icon">💡</span>
                    <span>Generating web server with authentication...</span>
                </div>
                <div class="code-preview">
                    <pre><code>from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/auth', methods=['POST'])
def authenticate():
    username = request.json.get('username')
    password = request.json.get('password')
    # Authentication logic here
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

if __name__ == '__main__':
    app.run(debug=True)</code></pre>
                </div>
                <div class="code-actions">
                    <button class="code-btn">💾 Save to Project</button>
                    <button class="code-btn">🚀 Run Server</button>
                    <button class="code-btn">📝 Explain Code</button>
                </div>
            </div>
        `;
    }
}

// ============================================================================
// LYRIXA INTERACTIVE CHAT
// ============================================================================

function initializeLyrixaChat() {
    // This will be used for the live demo section
    window.showLyrixaDemo = function () {
        createLyrixaModal();
    };
}

function createLyrixaModal() {
    const modal = document.createElement('div');
    modal.className = 'lyrixa-modal';
    modal.innerHTML = `
        <div class="lyrixa-modal-content">
            <div class="lyrixa-modal-header">
                <div class="lyrixa-avatar">🧠</div>
                <div class="lyrixa-info">
                    <h3>Lyrixa AI Assistant</h3>
                    <p>Live Demo - Ask me anything about code!</p>
                </div>
                <button class="lyrixa-close" onclick="closeLyrixaModal()">&times;</button>
            </div>
            <div class="lyrixa-chat-container">
                <div class="lyrixa-messages" id="lyrixaMessages">
                    <div class="lyrixa-message assistant">
                        <div class="message-avatar">🧠</div>
                        <div class="message-text">
                            Hello! I'm Lyrixa, your AI programming assistant. I can help you with:
                            <ul>
                                <li>[TOOL] Code generation and debugging</li>
                                <li>🏗️ Architecture design</li>
                                <li>📚 Documentation writing</li>
                                <li>🧪 Test creation</li>
                                <li>🚀 Deployment strategies</li>
                            </ul>
                            What would you like to build today?
                        </div>
                    </div>
                </div>
                <div class="lyrixa-input-container">
                    <input type="text" id="lyrixaInput" placeholder="Ask Lyrixa anything..."
                           onkeypress="handleLyrixaInput(event)">
                    <button onclick="sendLyrixaMessage()">Send</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Add CSS for modal if not already present
    if (!document.getElementById('lyrixa-modal-styles')) {
        const styles = document.createElement('style');
        styles.id = 'lyrixa-modal-styles';
        styles.textContent = `
            .lyrixa-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            }

            .lyrixa-modal-content {
                background: var(--bg-card);
                border-radius: var(--radius-xl);
                width: 90%;
                max-width: 600px;
                height: 70vh;
                display: flex;
                flex-direction: column;
                box-shadow: var(--shadow-2xl);
                border: 1px solid var(--border-primary);
            }

            .lyrixa-modal-header {
                display: flex;
                align-items: center;
                padding: var(--space-4);
                border-bottom: 1px solid var(--border-primary);
                gap: var(--space-3);
            }

            .lyrixa-avatar {
                font-size: 2rem;
                width: 50px;
                height: 50px;
                background: var(--gradient-primary);
                border-radius: var(--radius-full);
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .lyrixa-info h3 {
                color: var(--text-primary);
                margin-bottom: var(--space-1);
            }

            .lyrixa-info p {
                color: var(--text-muted);
                font-size: var(--text-sm);
            }

            .lyrixa-close {
                margin-left: auto;
                background: none;
                border: none;
                color: var(--text-muted);
                font-size: 1.5rem;
                cursor: pointer;
                padding: var(--space-2);
                border-radius: var(--radius-md);
                transition: all 0.2s ease;
            }

            .lyrixa-close:hover {
                background: var(--bg-hover);
                color: var(--text-primary);
            }

            .lyrixa-chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
            }

            .lyrixa-messages {
                flex: 1;
                padding: var(--space-4);
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: var(--space-4);
            }

            .lyrixa-message {
                display: flex;
                gap: var(--space-3);
                animation: slideIn 0.3s ease;
            }

            .lyrixa-message .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: var(--radius-full);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.2rem;
                flex-shrink: 0;
            }

            .lyrixa-message.assistant .message-avatar {
                background: var(--gradient-primary);
            }

            .lyrixa-message.user .message-avatar {
                background: var(--gradient-secondary);
            }

            .lyrixa-message .message-text {
                background: var(--bg-tertiary);
                padding: var(--space-3);
                border-radius: var(--radius-lg);
                color: var(--text-primary);
                flex: 1;
            }

            .lyrixa-message .message-text ul {
                margin: var(--space-2) 0;
                padding-left: var(--space-4);
            }

            .lyrixa-message .message-text li {
                margin: var(--space-1) 0;
                color: var(--text-secondary);
            }

            .lyrixa-input-container {
                padding: var(--space-4);
                border-top: 1px solid var(--border-primary);
                display: flex;
                gap: var(--space-2);
            }

            .lyrixa-input-container input {
                flex: 1;
                background: var(--bg-tertiary);
                border: 1px solid var(--border-primary);
                border-radius: var(--radius-lg);
                padding: var(--space-3);
                color: var(--text-primary);
                font-family: var(--font-family);
            }

            .lyrixa-input-container input:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 2px var(--primary)20;
            }

            .lyrixa-input-container button {
                background: var(--gradient-primary);
                border: none;
                border-radius: var(--radius-lg);
                padding: var(--space-3) var(--space-5);
                color: white;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .lyrixa-input-container button:hover {
                transform: translateY(-1px);
                box-shadow: var(--shadow-lg);
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes slideIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        `;
        document.head.appendChild(styles);
    }

    // Focus input
    setTimeout(() => {
        document.getElementById('lyrixaInput')?.focus();
    }, 100);
}

window.closeLyrixaModal = function () {
    const modal = document.querySelector('.lyrixa-modal');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    }
};

window.handleLyrixaInput = function (event) {
    if (event.key === 'Enter') {
        sendLyrixaMessage();
    }
};

window.sendLyrixaMessage = function () {
    const input = document.getElementById('lyrixaInput');
    const messages = document.getElementById('lyrixaMessages');

    if (!input || !messages || !input.value.trim()) return;

    const userMessage = input.value.trim();
    input.value = '';

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'lyrixa-message user';
    userDiv.innerHTML = `
        <div class="message-avatar">👤</div>
        <div class="message-text">${userMessage}</div>
    `;
    messages.appendChild(userDiv);

    // Scroll to bottom
    messages.scrollTop = messages.scrollHeight;

    // Simulate AI response
    setTimeout(() => {
        const response = generateLyrixaResponse(userMessage);
        const assistantDiv = document.createElement('div');
        assistantDiv.className = 'lyrixa-message assistant';
        assistantDiv.innerHTML = `
            <div class="message-avatar">🧠</div>
            <div class="message-text">${response}</div>
        `;
        messages.appendChild(assistantDiv);
        messages.scrollTop = messages.scrollHeight;
    }, 1000);
};

function generateLyrixaResponse(userMessage) {
    const message = userMessage.toLowerCase();

    if (message.includes('web') || message.includes('server')) {
        return `I'll help you create a web server! Here's a modern Flask setup with authentication:

<pre><code>from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

@app.route('/api/data')
def get_data():
    return jsonify({"status": "success", "data": []})

if __name__ == '__main__':
    app.run(debug=True)</code></pre>

Would you like me to add database integration or API endpoints?`;
    }

    if (message.includes('react') || message.includes('frontend')) {
        return `Great choice! Here's a modern React component with hooks:

<pre><code>import React, { useState, useEffect } from 'react';

const Dashboard = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const response = await fetch('/api/data');
            const result = await response.json();
            setData(result.data);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            {loading ? <Spinner /> : <DataTable data={data} />}
        </div>
    );
};

export default Dashboard;</code></pre>

Need help with state management or API integration?`;
    }

    if (message.includes('python') || message.includes('script')) {
        return `Perfect! Here's a robust Python script template:

<pre><code>#!/usr/bin/env python3
"""
Advanced Python Script Template
"""
import argparse
import logging
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main():
    parser = argparse.ArgumentParser(description='Your script description')
    parser.add_argument('--input', required=True, help='Input file path')
    parser.add_argument('--output', help='Output file path')

    args = parser.parse_args()

    # Your logic here
    logging.info(f"Processing {args.input}")

if __name__ == '__main__':
    setup_logging()
    main()</code></pre>

What specific functionality would you like to add?`;
    }

    return `I'd be happy to help with that! Based on your request about "${userMessage}", I can assist with:

• Code generation and optimization
• Architecture recommendations
• Best practices and patterns
• Testing strategies
• Documentation

Could you provide more specific details about what you'd like to build? For example:
- What programming language?
- What type of application?
- Any specific requirements or constraints?

I'm here to help make your development process smoother! 🚀`;
}

// ============================================================================
// PARTICLE SYSTEM
// ============================================================================

function initializeParticleSystem() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particles-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.6';

    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    function createParticle() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            radius: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.1,
            color: Math.random() > 0.5 ? '#0891b2' : '#8b5cf6'
        };
    }

    function initParticles() {
        particles = [];
        const particleCount = Math.min(50, Math.floor(canvas.width * canvas.height / 15000));
        for (let i = 0; i < particleCount; i++) {
            particles.push(createParticle());
        }
    }

    function updateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;

            if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;
        });
    }

    function drawParticles() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            ctx.beginPath();
            ctx.arc(particle.x, particle.y, particle.radius, 0, Math.PI * 2);
            ctx.fillStyle = particle.color + Math.floor(particle.opacity * 255).toString(16).padStart(2, '0');
            ctx.fill();
        });

        // Draw connections
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const distance = Math.sqrt(
                    Math.pow(particle.x - otherParticle.x, 2) +
                    Math.pow(particle.y - otherParticle.y, 2)
                );

                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = `rgba(8, 145, 178, ${0.1 * (1 - distance / 100)})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            });
        });
    }

    function animate() {
        updateParticles();
        drawParticles();
        animationId = requestAnimationFrame(animate);
    }

    resizeCanvas();
    initParticles();
    animate();

    window.addEventListener('resize', () => {
        resizeCanvas();
        initParticles();
    });

    // Pause animation when page is not visible
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            cancelAnimationFrame(animationId);
        } else {
            animate();
        }
    });
}

// ============================================================================
// SCROLL ANIMATIONS
// ============================================================================

function initializeScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe all animatable elements
    document.querySelectorAll('.feature-card, .demo-window, .phase-card, .btn').forEach(el => {
        observer.observe(el);
    });
}

// ============================================================================
// INTERACTIVE ELEMENTS
// ============================================================================

function initializeInteractiveElements() {
    // Add click effects to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function (e) {
            const ripple = document.createElement('span');
            ripple.className = 'btn-ripple';

            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';

            this.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Add hover effects to feature cards
    document.querySelectorAll('.feature-card').forEach(card => {
        card.addEventListener('mouseenter', function () {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', function () {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
}

// ============================================================================
// SERVICE WORKER REGISTRATION
// ============================================================================

function initializeServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('✅ Service Worker registered:', registration);
                })
                .catch(error => {
                    console.log('❌ Service Worker registration failed:', error);
                });
        });
    }
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

// Throttle function for performance
function throttle(func, limit) {
    let inThrottle;
    return function () {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Debounce function for performance
function debounce(func, wait, immediate) {
    let timeout;
    return function () {
        const context = this, args = arguments;
        const later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Add CSS for animations and effects
const additionalStyles = document.createElement('style');
additionalStyles.textContent = `
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .btn-ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }

    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .navbar-scrolled {
        background: rgba(15, 15, 35, 0.98) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        backdrop-filter: blur(10px);
    }

    .navbar-hidden {
        transform: translateY(-100%);
        transition: transform 0.3s ease;
    }

    .feature-card, .demo-window {
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .feature-card:hover {
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    }

    /* Code syntax highlighting for demos */
    .code-preview pre {
        background: var(--bg-tertiary);
        border-radius: var(--radius-md);
        padding: var(--space-4);
        overflow-x: auto;
        font-family: var(--font-mono);
        font-size: var(--text-sm);
        line-height: 1.5;
    }

    .code-preview code {
        color: var(--text-primary);
    }

    /* Responsive improvements */
    @media (max-width: 768px) {
        .nav-links-active {
            display: flex !important;
            position: fixed;
            top: 70px;
            left: 0;
            width: 100%;
            background: var(--bg-secondary);
            flex-direction: column;
            padding: var(--space-4);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
        }

        .nav-toggle-active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }

        .nav-toggle-active span:nth-child(2) {
            opacity: 0;
        }

        .nav-toggle-active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
    }
`;

document.head.appendChild(additionalStyles);

// Export functions for global access
window.AetherraWebsite = {
    showLyrixaDemo,
    closeLyrixaModal,
    handleLyrixaInput,
    sendLyrixaMessage
};
