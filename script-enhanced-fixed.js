// Enhanced Aetherra Website - Fixed JavaScript
// Comprehensive fixes for all interactive elements

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all features
    initializeNavigation();
    initializeHeroAnimations();
    initializeDemoWindows();
    initializeLyrixaChat();
    initializeInteractiveDemo();
    initializeParticleSystem();
    initializeScrollAnimations();
    initializeServiceWorker();

    console.log('🚀 Aetherra Enhanced Website Loaded - All Features Fixed');
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

        lastScrollY = currentScrollY;
    });

    // Mobile navigation toggle
    navToggle?.addEventListener('click', () => {
        navLinks.classList.toggle('nav-open');
        navToggle.classList.toggle('nav-toggle-open');
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
                navLinks.classList.remove('nav-open');
                navToggle.classList.remove('nav-toggle-open');
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

        setTimeout(typeWriter, 1000);
    }

    // Animated stats counter
    const statNumbers = document.querySelectorAll('.stat-number');
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px'
    };

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                statsObserver.unobserve(entry.target);
            }
        });
    }, observerOptions);

    statNumbers.forEach(stat => statsObserver.observe(stat));
}

function animateCounter(element) {
    const target = parseInt(element.textContent.replace(/[^\d]/g, ''));
    const increment = target / 50;
    let current = 0;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            element.textContent = element.textContent.replace(/[\d,]+/, target.toLocaleString());
            clearInterval(timer);
        } else {
            element.textContent = element.textContent.replace(/[\d,]+/, Math.floor(current).toLocaleString());
        }
    }, 40);
}

// ============================================================================
// FIXED LYRIXA CHAT SYSTEM
// ============================================================================

function initializeLyrixaChat() {
    const chatInput = document.getElementById('lyrixaChatInput');
    const chatMessages = document.getElementById('lyrixaChat');
    const sendButton = chatMessages?.parentElement?.querySelector('.chat-send-btn');

    if (!chatInput || !chatMessages) return;

    // Initialize with welcome message
    addChatMessage('assistant', 'Hello! I\'m Lyrixa, your AI programming companion. Ask me anything about coding, and I\'ll help you build amazing software! 🚀');

    // Handle send button click
    sendButton?.addEventListener('click', () => sendLyrixaMessage());

    // Handle Enter key in chat input
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendLyrixaMessage();
        }
    });

    // Auto-focus chat input when clicking in chat area
    chatMessages.addEventListener('click', () => {
        chatInput.focus();
    });
}

function sendLyrixaMessage() {
    const chatInput = document.getElementById('lyrixaChatInput');
    const chatMessages = document.getElementById('lyrixaChat');
    
    if (!chatInput || !chatMessages) return;

    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage('user', message);
    chatInput.value = '';

    // Show typing indicator
    addTypingIndicator();

    // Simulate AI response after delay
    setTimeout(() => {
        removeTypingIndicator();
        const response = generateLyrixaResponse(message);
        addChatMessage('assistant', response);
    }, 1500 + Math.random() * 1000);
}

function addChatMessage(sender, message) {
    const chatMessages = document.getElementById('lyrixaChat');
    if (!chatMessages) return;

    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🧠';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);
    
    // Auto-scroll to bottom with smooth behavior
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function addTypingIndicator() {
    const chatMessages = document.getElementById('lyrixaChat');
    if (!chatMessages) return;

    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message assistant typing-indicator';
    typingDiv.id = 'typing-indicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🧠';
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.innerHTML = '<div class="dots"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(content);
    chatMessages.appendChild(typingDiv);
    
    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function generateLyrixaResponse(userMessage) {
    const responses = [
        "Great question! Let me help you with that. Here's what I'd suggest...",
        "I can definitely help you build that! Here's a step-by-step approach...",
        "That's an interesting challenge! Let me break this down for you...",
        "Perfect! I love working on projects like this. Here's how we can tackle it...",
        "Excellent idea! I can help you implement that efficiently. Let's start with...",
        "I understand what you're looking for. Here's a clean solution...",
        "That's a common pattern in modern development! Here's the best approach..."
    ];

    const codeResponses = [
        "```python\ndef hello_world():\n    print('Hello from Lyrixa!')\n    return 'AI-powered coding!'\n```",
        "```javascript\nconst aiAssistant = {\n    name: 'Lyrixa',\n    capabilities: ['coding', 'debugging', 'optimization'],\n    status: 'ready to help!'\n};\n```",
        "```python\nclass LyrixaAI:\n    def __init__(self):\n        self.ready = True\n        self.memory = {}\n    \n    def assist(self, task):\n        return f'Helping with: {task}'\n```"
    ];

    if (userMessage.toLowerCase().includes('code') || userMessage.toLowerCase().includes('function')) {
        return responses[Math.floor(Math.random() * responses.length)] + '\n\n' + 
               codeResponses[Math.floor(Math.random() * codeResponses.length)];
    }

    return responses[Math.floor(Math.random() * responses.length)];
}

// ============================================================================
// FIXED INTERACTIVE DEMO SYSTEM
// ============================================================================

function initializeInteractiveDemo() {
    // Initialize demo tabs
    const demoTabs = document.querySelectorAll('.demo-tab');
    const demoPanels = document.querySelectorAll('.demo-panel');

    demoTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Update active tab
            demoTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active panel
            demoPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `${targetTab}-demo`) {
                    panel.classList.add('active');
                }
            });
            
            // Initialize specific demo
            initializeSpecificDemo(targetTab);
        });
    });

    // Initialize the default demo
    initializeSpecificDemo('launcher');
}

function initializeSpecificDemo(demoType) {
    switch (demoType) {
        case 'launcher':
            initializeLauncherDemo();
            break;
        case 'lyrixa':
            initializeDemoChatDemo();
            break;
        case 'code':
            initializeCodeDemo();
            break;
        case 'memory':
            initializeMemoryDemo();
            break;
    }
}

function initializeLauncherDemo() {
    const launcherInput = document.getElementById('launcherInput');
    const launcherOutput = document.getElementById('launcherOutput');

    if (!launcherInput || !launcherOutput) return;

    launcherInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const command = launcherInput.value.trim();
            if (command) {
                executeLauncherCommand(command);
                launcherInput.value = '';
            }
        }
    });

    // Add initial status check
    setTimeout(() => {
        addLauncherOutput('[*] System Status Check Complete');
        addLauncherOutput('[+] All components operational');
        addLauncherOutput('[*] Ready for commands...');
    }, 1000);
}

function executeLauncherCommand(command) {
    addLauncherOutput(`$ ${command}`);
    
    setTimeout(() => {
        switch (command.toLowerCase()) {
            case '--gui':
                addLauncherOutput('[*] Launching GUI mode...');
                addLauncherOutput('[+] PySide6 interface initialized');
                addLauncherOutput('[+] Modern dark theme loaded');
                addLauncherOutput('[*] GUI ready for interaction');
                break;
            case '--test':
                addLauncherOutput('[*] Running test suite...');
                addLauncherOutput('[+] Phase 1 tests: PASSED (15/15)');
                addLauncherOutput('[+] Phase 2 tests: PASSED (12/12)');
                addLauncherOutput('[+] Integration tests: PASSED (8/8)');
                addLauncherOutput('[*] All tests completed successfully');
                break;
            case '--console':
                addLauncherOutput('[*] Starting console mode...');
                addLauncherOutput('[+] Lyrixa AI console active');
                addLauncherOutput('[*] Type "help" for available commands');
                break;
            case 'help':
                addLauncherOutput('[*] Available commands:');
                addLauncherOutput('  --gui     : Launch graphical interface');
                addLauncherOutput('  --test    : Run complete test suite');
                addLauncherOutput('  --console : Start console mode');
                addLauncherOutput('  status    : Show system status');
                break;
            case 'status':
                addLauncherOutput('[*] System Status:');
                addLauncherOutput('[+] Memory System: Active');
                addLauncherOutput('[+] Anticipation Engine: Running');
                addLauncherOutput('[+] GUI Components: Ready');
                addLauncherOutput('[+] Intelligence Layer: Online');
                break;
            default:
                addLauncherOutput(`[!] Unknown command: ${command}`);
                addLauncherOutput('[*] Type "help" for available commands');
        }
    }, 500);
}

function addLauncherOutput(text) {
    const output = document.getElementById('launcherOutput');
    if (!output) return;

    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `<span class="terminal-response">${text}</span>`;
    output.appendChild(line);

    // Auto-scroll
    output.scrollTop = output.scrollHeight;
}

// ============================================================================
// DEMO WINDOWS & TERMINAL ANIMATIONS
// ============================================================================

function initializeDemoWindows() {
    // Animate terminal lines on page load
    const terminalLines = document.querySelectorAll('.terminal-line');
    terminalLines.forEach((line, index) => {
        line.style.opacity = '0';
        line.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            line.style.transition = 'all 0.5s ease';
            line.style.opacity = '1';
            line.style.transform = 'translateX(0)';
        }, index * 200 + 500);
    });
}

// ============================================================================
// GLOBAL UTILITY FUNCTIONS
// ============================================================================

// Fixed Lyrixa Demo Modal
function showLyrixaDemo() {
    const modal = document.getElementById('lyrixaModal');
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus chat input
        const chatInput = modal.querySelector('.chat-input');
        if (chatInput) {
            setTimeout(() => chatInput.focus(), 100);
        }
    } else {
        // If modal doesn't exist, scroll to Lyrixa section
        const lyrixaSection = document.getElementById('lyrixa');
        if (lyrixaSection) {
            lyrixaSection.scrollIntoView({ behavior: 'smooth' });
            
            // Focus the main chat input
            setTimeout(() => {
                const mainChatInput = document.getElementById('lyrixaChatInput');
                if (mainChatInput) {
                    mainChatInput.focus();
                }
            }, 1000);
        }
    }
}

// Fixed Installation Guide
function openInstallationGuide() {
    const guidePage = 'https://github.com/Zyonic88/Aetherra/blob/main/README.md#installation';
    window.open(guidePage, '_blank', 'noopener,noreferrer');
}

// Close modal function
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }
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
    canvas.style.opacity = '0.3';
    
    document.querySelector('.background-particles').appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    
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
            size: Math.random() * 2 + 1,
            opacity: Math.random() * 0.5 + 0.2
        };
    }
    
    function initParticles() {
        particles = [];
        for (let i = 0; i < 50; i++) {
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
            ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(14, 165, 233, ${particle.opacity})`;
            ctx.fill();
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

// ============================================================================
// SCROLL ANIMATIONS
// ============================================================================

function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    // Observe elements for scroll animations
    document.querySelectorAll('.feature-card, .phase-card, .step-card, .doc-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'all 0.6s ease';
        observer.observe(el);
    });
}

// Add CSS for scroll animations
const style = document.createElement('style');
style.textContent = `
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
`;
document.head.appendChild(style);

// ============================================================================
// SERVICE WORKER
// ============================================================================

function initializeServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js')
            .then(() => console.log('✅ Service Worker registered'))
            .catch(err => console.log('❌ Service Worker registration failed:', err));
    }
}
