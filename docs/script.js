// aetherra Website JavaScript

document.addEventListener('DOMContentLoaded', function () {
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
        html = html.replace(/\b(AI_SYSTEM|CONSCIOUSNESS|MEMORY|GOALS|ENVIRONMENT|TASK|INPUT|OUTPUT|PROCESS|PERSISTENT|IDENTITY|VOICE|PERSONALITY|AWARENESS|PRIMARY|LEARNING|ADAPTATION)\b/g,
            '<span class="keyword">$1</span>');

        // Strings
        html = html.replace(/"([^"]*)"/g, '<span class="string">"$1"</span>');

        // Comments
        html = html.replace(/(#.*$)/gm, '<span class="comment">$1</span>');

        // Numbers
        html = html.replace(/\b(\d+)\b/g, '<span class="number">$1</span>');

        // Functions
        html = html.replace(/\b(\w+)(?=\()/g, '<span class="function">$1</span>');

        block.innerHTML = html;
    }

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

// External link tracking
document.addEventListener('click', function (e) {
    const link = e.target.closest('a');
    if (link && link.target === '_blank') {
        console.log(`External link clicked: ${link.href}`);
        // Add analytics tracking here
    }
});

// Error handling
window.addEventListener('error', function (e) {
    console.error('JavaScript error:', e.error);
    // Add error tracking here
});

// Performance monitoring
window.addEventListener('load', function () {
    const perfData = performance.getEntriesByType('navigation')[0];
    console.log(`Page load time: ${perfData.loadEventEnd - perfData.fetchStart}ms`);
    // Add performance tracking here
});
