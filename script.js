// aetherra Website JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Particle background animation
    createParticleBackground();

    // Interactive terminal demo
    initializeInteractiveTerminal();

    // Floating AI assistant preview
    initializeAIAssistantPreview();

    // Navigation scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;

    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;

        if (currentScrollY > 100) {
            navbar.style.background = 'rgba(15, 15, 35, 0.98)';
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(15, 15, 35, 0.95)';
            navbar.style.boxShadow = 'none';
        }

        lastScrollY = currentScrollY;
    });

    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-link[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed navbar
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Mobile navigation toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navLinksContainer = document.querySelector('.nav-links');

    if (navToggle && navLinksContainer) {
        navToggle.addEventListener('click', () => {
            navLinksContainer.classList.toggle('nav-open');
            navToggle.classList.toggle('nav-toggle-open');
        });
    }

    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for scroll animations
    const animatedElements = document.querySelectorAll('.feature-card, .doc-link, .start-card');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(el);
    });

    // Terminal typing effect
    const terminalCommands = document.querySelectorAll('.terminal-command');
    terminalCommands.forEach((command, index) => {
        const text = command.textContent;
        command.textContent = '';

        setTimeout(() => {
            typeText(command, text, 50);
        }, index * 2000);
    });

    function typeText(element, text, speed) {
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    }

    // Code syntax highlighting (simple version)
    const codeBlocks = document.querySelectorAll('code.language-neuro');
    codeBlocks.forEach(block => {
        highlightaetherra(block);
    });

    function highlightaetherra(block) {
        let html = block.innerHTML;

        // Keywords
        html = html.replace(/\b(AI_SYSTEM|CONSCIOUSNESS|MEMORY|GOALS|ENVIRONMENT|TASK|INPUT|OUTPUT|PROCESS|PERSISTENT|IDENTITY|VOICE|PERSONALITY|AWARENESS|PRIMARY|LEARNING|ADAPTATION|SECONDARY)\b/g,
            '<span class="keyword">$1</span>');

        // Strings
        html = html.replace(/"([^"]*)"/g, '<span class="string">"$1"</span>');

        // Comments
        html = html.replace(/(\/\/.*$)/gm, '<span class="comment">$1</span>');
        html = html.replace(/(\/\*[\s\S]*?\*\/)/g, '<span class="comment">$1</span>');

        // Numbers
        html = html.replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="number">$1</span>');

        // Functions
        html = html.replace(/\b(\w+)(?=\()/g, '<span class="function">$1</span>');

        // Operators
        html = html.replace(/([+\-*\/=<>!&|]+)/g, '<span class="operator">$1</span>');

        block.innerHTML = html;
    }

    // Enhanced syntax highlighting for demo code
    function highlightAetherraDemo() {
        const demoCode = document.querySelector('.language-aetherra');
        if (demoCode) {
            highlightaetherra(demoCode);

            // Add typing animation
            const lines = demoCode.innerHTML.split('\n');
            demoCode.innerHTML = '';

            lines.forEach((line, index) => {
                setTimeout(() => {
                    const lineDiv = document.createElement('div');
                    lineDiv.innerHTML = line;
                    demoCode.appendChild(lineDiv);

                    // Scroll to bottom
                    const codeWindow = demoCode.closest('.code-window');
                    if (codeWindow) {
                        codeWindow.scrollTop = codeWindow.scrollHeight;
                    }
                }, index * 200);
            });
        }
    }

    // Initialize demo animations
    setTimeout(highlightAetherraDemo, 2000);

    // Copy code functionality
    const codeWindows = document.querySelectorAll('.code-window');
    codeWindows.forEach(window => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '📋';
        copyBtn.title = 'Copy code';

        const header = window.querySelector('.code-header');
        header.appendChild(copyBtn);

        copyBtn.addEventListener('click', () => {
            const code = window.querySelector('code');
            const text = code.textContent;

            navigator.clipboard.writeText(text).then(() => {
                copyBtn.innerHTML = '✅';
                setTimeout(() => {
                    copyBtn.innerHTML = '📋';
                }, 2000);
            });
        });
    });

    // Feature card hover effects
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Plugin terminal simulation
    const pluginTerminal = document.querySelector('.plugin-terminal .terminal-content');
    if (pluginTerminal) {
        // Add blinking cursor effect
        const cursor = document.createElement('span');
        cursor.className = 'terminal-cursor';
        cursor.textContent = '█';
        cursor.style.animation = 'blink 1s infinite';

        // Add cursor CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes blink {
                0%, 50% { opacity: 1; }
                51%, 100% { opacity: 0; }
            }
            .terminal-cursor {
                color: var(--success-color);
            }
        `;
        document.head.appendChild(style);

        pluginTerminal.appendChild(cursor);
    }

    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            hero.style.transform = `translateY(${rate}px)`;
        });
    }

    // Analytics and performance monitoring
    function trackPageView() {
        // Add analytics code here when ready
        console.log('Page view tracked');
    }

    function trackButtonClick(buttonName) {
        console.log(`Button clicked: ${buttonName}`);
        // Add analytics code here when ready
    }

    // Add click tracking to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const buttonText = btn.textContent.trim();
            trackButtonClick(buttonText);
        });
    });

    // Track page view
    trackPageView();

    // Service worker registration for PWA capabilities
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered: ', registration);
                })
                .catch(registrationError => {
                    console.log('SW registration failed: ', registrationError);
                });
        });
    }
});

// Particle background animation
function createParticleBackground() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particle-canvas';
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-1';
    canvas.style.opacity = '0.3';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 100;

    class Particle {
        constructor() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 2 + 1;
            this.color = Math.random() > 0.5 ? '#0891b2' : '#22c55e';
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
            if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = this.color;
            ctx.fill();
        }
    }

    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        // Draw connections
        particles.forEach((particle, i) => {
            particles.slice(i + 1).forEach(otherParticle => {
                const dx = particle.x - otherParticle.x;
                const dy = particle.y - otherParticle.y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < 100) {
                    ctx.beginPath();
                    ctx.moveTo(particle.x, particle.y);
                    ctx.lineTo(otherParticle.x, otherParticle.y);
                    ctx.strokeStyle = `rgba(8, 145, 178, ${0.1 * (1 - distance / 100)})`;
                    ctx.stroke();
                }
            });
        });

        requestAnimationFrame(animate);
    }

    animate();

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Interactive terminal demo
function initializeInteractiveTerminal() {
    const terminal = document.querySelector('.interactive-terminal');
    if (!terminal) return;

    const input = terminal.querySelector('.terminal-input');
    const output = terminal.querySelector('.terminal-output');

    const commands = {
        'help': 'Available commands: help, clear, about, features, lyrixa, demo, install',
        'clear': () => { output.innerHTML = ''; return ''; },
        'about': 'Aetherra is an AI-native development environment with Lyrixa assistant.',
        'features': 'Key features: AI-powered coding, natural language programming, intelligent debugging',
        'lyrixa': 'Lyrixa is your AI programming companion with advanced cognitive capabilities.',
        'demo': 'Try: "Create a web server in Python" or "Debug this function"',
        'install': 'pip install aetherra-dev && aetherra init'
    };

    function addOutput(text, isCommand = false) {
        const line = document.createElement('div');
        line.className = isCommand ? 'terminal-command-line' : 'terminal-response';
        line.innerHTML = isCommand ? `<span class="terminal-prompt">aetherra$</span> ${text}` : text;
        output.appendChild(line);
        terminal.scrollTop = terminal.scrollHeight;
    }

    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const command = input.value.trim();
            addOutput(command, true);

            if (commands[command]) {
                const response = typeof commands[command] === 'function' ? commands[command]() : commands[command];
                if (response) addOutput(response);
            } else if (command) {
                addOutput(`Command not found: ${command}. Type 'help' for available commands.`);
            }

            input.value = '';
        }
    });

    // Auto-demo
    setTimeout(() => {
        addOutput('help', true);
        addOutput(commands.help);
    }, 1000);
}

// Floating AI assistant preview
function initializeAIAssistantPreview() {
    const assistantButton = document.createElement('div');
    assistantButton.className = 'ai-assistant-preview';
    assistantButton.innerHTML = `
        <div class="ai-avatar">
            <div class="ai-pulse"></div>
            🧠
        </div>
        <div class="ai-tooltip">
            <p>Meet Lyrixa</p>
            <small>Your AI coding companion</small>
        </div>
    `;

    document.body.appendChild(assistantButton);

    let isExpanded = false;
    assistantButton.addEventListener('click', () => {
        if (!isExpanded) {
            showAIDemo();
            isExpanded = true;
        }
    });
}

function showAIDemo() {
    const modal = document.createElement('div');
    modal.className = 'ai-demo-modal';
    modal.innerHTML = `
        <div class="ai-demo-content">
            <div class="ai-demo-header">
                <h3>🧠 Lyrixa AI Assistant</h3>
                <button class="ai-demo-close">&times;</button>
            </div>
            <div class="ai-chat-demo">
                <div class="ai-message ai-message-assistant">
                    <div class="ai-avatar-small">🧠</div>
                    <p>Hello! I'm Lyrixa, your AI programming companion. I can help you write code, debug issues, and learn new concepts. What would you like to work on today?</p>
                </div>
                <div class="ai-message ai-message-user">
                    <p>Can you help me create a REST API?</p>
                </div>
                <div class="ai-message ai-message-assistant">
                    <div class="ai-avatar-small">🧠</div>
                    <p>Absolutely! I'll help you create a REST API. What technology would you prefer?</p>
                    <div class="ai-suggestions">
                        <button class="ai-suggestion">Python + FastAPI</button>
                        <button class="ai-suggestion">Node.js + Express</button>
                        <button class="ai-suggestion">Python + Flask</button>
                    </div>
                </div>
            </div>
            <div class="ai-demo-input">
                <input type="text" placeholder="Try asking Lyrixa something..." disabled>
                <button disabled>Send</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    modal.querySelector('.ai-demo-close').addEventListener('click', () => {
        modal.remove();
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}
