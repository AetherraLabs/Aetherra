// Lyrixa Web Interface JavaScript - Fixed Version
class LyrixaWebInterface {
    constructor() {
        console.log('Initializing Lyrixa Web Interface...');
        this.qtBridge = null;
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupQtBridge();
        this.startUpdateLoop();
    }

    setupEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (chatInput) {
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            chatInput.focus();
        }
    }

    setupQtBridge() {
        console.log('Setting up Qt bridge...');
        this.qtBridge = null;

        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            console.log('Qt WebChannel transport detected');

            const initBridge = () => {
                if (typeof QWebChannel !== 'undefined') {
                    try {
                        new QWebChannel(qt.webChannelTransport, (channel) => {
                            console.log('WebChannel connected');

                            if (channel.objects.bridge) {
                                this.qtBridge = channel.objects.bridge;
                                console.log('Qt bridge connected successfully');
                            } else {
                                console.warn('Bridge object not found in channel');
                            }
                        });
                    } catch (e) {
                        console.error('Error setting up Qt bridge:', e);
                        this.qtBridge = null;
                    }
                } else {
                    console.log('QWebChannel not ready, retrying...');
                    setTimeout(initBridge, 100);
                }
            };

            initBridge();
        } else {
            console.log('Qt WebChannel not available, running in standalone mode');
        }
    }

    sendMessage() {
        const chatInput = document.getElementById('chat-input');
        if (!chatInput) return;

        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        this.addChatMessage('User', message, 'user');
        chatInput.value = '';

        // Send to Qt backend if bridge is available
        if (this.qtBridge && typeof this.qtBridge.send_message === 'function') {
            try {
                this.qtBridge.send_message(message);
                console.log('Message sent to Qt bridge:', message);
            } catch (e) {
                console.error('Error sending message to Qt:', e);
                this.simulateResponse(message);
            }
        } else {
            console.log('Qt bridge not available, simulating response');
            this.simulateResponse(message);
        }

        this.showTypingIndicator();
    }

    simulateResponse(message) {
        setTimeout(() => {
            this.addChatMessage('Lyrixa', this.generateResponse(message), 'lyrixa');
        }, 1000);
    }

    addChatMessage(sender, content, type) {
        const chatDisplay = document.getElementById('chat-display');
        if (!chatDisplay) return;

        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ' + type + '-message fade-in';
        messageDiv.innerHTML =
            '<div class="message-header">' +
            '<span class="sender">' + sender + '</span>' +
            '<span class="timestamp">' + timestamp + '</span>' +
            '</div>' +
            '<div class="message-content">' + content + '</div>';

        chatDisplay.appendChild(messageDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        this.removeTypingIndicator();
    }

    showTypingIndicator() {
        const chatDisplay = document.getElementById('chat-display');
        if (!chatDisplay) return;

        this.removeTypingIndicator(); // Remove any existing indicator

        const typingDiv = document.createElement('div');
        typingDiv.className = 'message lyrixa-message typing-indicator';
        typingDiv.innerHTML =
            '<div class="message-header">' +
            '<span class="sender">Lyrixa</span>' +
            '<span class="timestamp">typing...</span>' +
            '</div>' +
            '<div class="message-content">' +
            '<div class="typing-dots">●●●</div>' +
            '</div>';

        chatDisplay.appendChild(typingDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    generateResponse(message) {
        const responses = [
            "I understand your query. Let me process this through my cognitive frameworks...",
            "That's an interesting perspective. I'm analyzing the implications across multiple dimensions.",
            "I can see patterns in what you're describing. My memory system is finding relevant connections.",
            "Your input is triggering several reflection processes. I'm synthesizing insights from my experience.",
            "This relates to some concepts I've been exploring in my night cycle processing."
        ];

        return responses[Math.floor(Math.random() * responses.length)];
    }

    // Method called by Qt bridge to send messages to the web interface
    receiveMessage(sender, content) {
        this.removeTypingIndicator();
        this.addChatMessage(sender, content, 'lyrixa');
        console.log('Received message from Qt:', sender, content);
    }

    updateStats(data) {
        // Update memory progress bar
        const memoryProgress = document.querySelector('.progress-fill');
        if (memoryProgress && data.memory_usage) {
            memoryProgress.style.width = data.memory_usage + '%';
        }

        // Update stat values
        const statValues = document.querySelectorAll('.stat-value');
        statValues.forEach(value => {
            const label = value.previousElementSibling?.textContent || '';
            if (label.includes('CPU') && data.cpu_load) {
                value.textContent = data.cpu_load + '%';
            } else if (label.includes('Coherence') && data.coherence) {
                value.textContent = data.coherence + '%';
            }
        });
    }

    updateReflectionPanel(data) {
        const content = document.getElementById('reflection-content');
        if (!content) return;

        // Update stats
        const statValues = content.querySelectorAll('.stat-value');
        statValues.forEach(value => {
            const label = value.previousElementSibling?.textContent || '';
            if (label.includes('Insight') && data.insight_quality) {
                value.textContent = data.insight_quality + '%';
            } else if (label.includes('Self-Awareness') && data.self_awareness) {
                value.textContent = data.self_awareness + '%';
            }
        });

        // Update insights list
        const insightsList = content.querySelector('.insights-list');
        if (insightsList && data.insights) {
            insightsList.innerHTML = '';
            data.insights.forEach(insight => {
                const li = document.createElement('li');
                li.textContent = insight;
                insightsList.appendChild(li);
            });
        }
    }

    initializeAnimations() {
        // Simple background animation for the neural network
        const networkDivs = document.querySelectorAll('.neural-bg .network-node');
        networkDivs.forEach((node, index) => {
            if (node.style) {
                node.style.animationDelay = (index * 0.1) + 's';
            }
        });
    }

    startUpdateLoop() {
        // Update loop for animations and data refresh
        setInterval(() => {
            this.updateAnimations();
        }, 100);
    }

    updateAnimations() {
        // Update any ongoing animations
        const nodes = document.querySelectorAll('.network-node');
        nodes.forEach(node => {
            if (node.style && Math.random() < 0.01) {
                node.style.opacity = Math.random() * 0.5 + 0.5;
            }
        });
    }

    // Additional methods that Qt interface expects
    setStatus(status, message) {
        console.log('Status update:', status, message);
        const statusElement = document.querySelector('.status-text');
        if (statusElement) {
            statusElement.textContent = 'System Status: ' + status;
        }
    }

    updateStats(stats) {
        this.updateSystemStats(stats);
    }

    updateMemoryGraph(graphData) {
        console.log('Memory graph update:', graphData);
        // Simple implementation for memory graph
        const memoryContainer = document.querySelector('.memory-graph');
        if (memoryContainer && graphData) {
            // Update memory visualization
        }
    }

    updateReflectionPanel(data) {
        this.updateReflection(data);
    }

    sendChatResponse(sender, message) {
        this.addChatMessage(sender, message, 'lyrixa');
    }

    updateThoughtLog(thoughts) {
        console.log('Thought log update:', thoughts);
        // Implementation for thought log updates
    }

    updateImprovementFeed(improvements) {
        console.log('Improvement feed update:', improvements);
        // Implementation for improvement feed updates
    }

    executeJavaScript(script) {
        try {
            eval(script);
        } catch (e) {
            console.error('Error executing JavaScript:', e);
        }
    }

    reloadInterface() {
        window.location.reload();
    }
}

// Initialize the interface when the page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing Lyrixa interface...');
    window.lyrixaInterface = new LyrixaWebInterface();
});

// Fallback for Qt environments
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.lyrixaInterface) {
            window.lyrixaInterface = new LyrixaWebInterface();
        }
    });
} else {
    // Document already loaded
    if (!window.lyrixaInterface) {
        window.lyrixaInterface = new LyrixaWebInterface();
    }
}
