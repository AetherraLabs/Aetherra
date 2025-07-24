// Lyrixa Web Interface JavaScript
class LyrixaWebInterface {
    constructor() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupQtBridge();
        this.startUpdateLoop();
    }

    setupEventListeners() {
        // Chat input handling
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');

        sendButton.addEventListener('click', () => this.sendMessage());
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Focus chat input on load
        chatInput.focus();
    }

    setupQtBridge() {
        // Setup Qt WebChannel for communication with Qt application
        console.log('Setting up Qt bridge...');

        // Initialize bridge as null first
        this.qtBridge = null;

        // Check if we're running in a Qt WebEngine context
        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            console.log('Qt WebChannel transport detected');

            // Wait for QWebChannel to be available
            const initBridge = () => {
                if (typeof QWebChannel !== 'undefined') {
                    try {
                        new QWebChannel(qt.webChannelTransport, (channel) => {
                            console.log('WebChannel objects:', Object.keys(channel.objects));

                            if (channel.objects.bridge) {
                                this.qtBridge = channel.objects.bridge;
                                console.log('Qt bridge connected successfully');

                                // Test if bridge methods exist
                                if (typeof this.qtBridge.send_message === 'function') {
                                    console.log('Bridge methods available');
                                } else {
                                    console.warn('Bridge methods not found');
                                }
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

        // Add typing indicator
        this.showTypingIndicator();
    }

    simulateResponse(message) {
        // Fallback: simulate response
        setTimeout(() => {
            this.addChatMessage('Lyrixa', this.generateResponse(message), 'lyrixa');
        }, 1000);
    }

    addChatMessage(sender, content, type) {
        const chatDisplay = document.getElementById('chat-display');
        const timestamp = new Date().toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit'
        });

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message fade-in`;
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">${sender}</span>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="message-content">${content}</div>
        `;

        chatDisplay.appendChild(messageDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        // Remove typing indicator if it exists
        this.removeTypingIndicator();
    }

    showTypingIndicator() {
        const chatDisplay = document.getElementById('chat-display');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message lyrixa-message typing-indicator';
        typingDiv.innerHTML = `
            <div class="message-header">
                <span class="sender">Lyrixa</span>
                <span class="timestamp">typing...</span>
            </div>
            <div class="message-content">
                <span class="typing-dots">●●●</span>
            </div>
        `;

        chatDisplay.appendChild(typingDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        // Animate typing dots
        const dots = typingDiv.querySelector('.typing-dots');
        if (dots) {
            dots.style.animation = 'pulse 1.5s infinite';
        }
    }

    removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    generateResponse(message) {
        // Fallback responses for demo
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

    handleQtMessage(message) {
        // Handle messages from Qt backend
        try {
            const data = JSON.parse(message);

            if (data.type === 'chat_response') {
                this.addChatMessage('Lyrixa', data.content, 'lyrixa');
            } else if (data.type === 'system_update') {
                this.updateSystemData(data.content);
            }
        } catch (e) {
            console.error('Error handling Qt message:', e);
        }
    }

    handleDataUpdate(dataType, data) {
        // Handle data updates from Qt backend
        switch (dataType) {
            case 'stats':
                this.updateStats(data);
                break;
            case 'thoughts':
                this.updateThoughtLog(data);
                break;
            case 'improvements':
                this.updateImprovementFeed(data);
                break;
            case 'reflection':
                this.updateReflectionPanel(data);
                break;
        }
    }

    updateStats(data) {
        // Update dashboard stats
        const statsContainer = document.querySelector('.stats-container');
        if (!statsContainer) return;

        // Update memory usage
        const memoryProgress = statsContainer.querySelector('.progress-fill');
        if (memoryProgress && data.memory_usage) {
            memoryProgress.style.width = `${data.memory_usage}%`;
        }

        // Update other stats
        const statValues = statsContainer.querySelectorAll('.stat-value');
        statValues.forEach(value => {
            const label = value.previousElementSibling.textContent;
            if (label.includes('Plugins') && data.plugins_active) {
                value.textContent = data.plugins_active;
            } else if (label.includes('CPU') && data.cpu_load) {
                value.textContent = `${data.cpu_load}%`;
            } else if (label.includes('Coherence') && data.coherence) {
                value.textContent = `${data.coherence}%`;
            }
        });
    }

    updateThoughtLog(thoughts) {
        const thoughtLog = document.getElementById('thought-log');
        if (!thoughtLog) return;

        // Clear existing thoughts
        thoughtLog.innerHTML = '';

        // Add new thoughts
        thoughts.slice(-10).forEach(thought => {
            const thoughtDiv = document.createElement('div');
            thoughtDiv.className = 'thought-entry fade-in';
            thoughtDiv.innerHTML = `
                <span class="thought-time">${thought.timestamp}</span>
                <span class="thought-content">${thought.content}</span>
            `;
            thoughtLog.appendChild(thoughtDiv);
        });

        thoughtLog.scrollTop = thoughtLog.scrollHeight;
    }

    updateImprovementFeed(improvements) {
        const feed = document.getElementById('improvement-feed');
        if (!feed) return;

        // Clear existing items
        feed.innerHTML = '';

        // Add new improvements
        improvements.slice(-5).forEach(improvement => {
            const itemDiv = document.createElement('div');
            itemDiv.className = 'improvement-item fade-in';
            itemDiv.innerHTML = `
                <div class="improvement-type">${improvement.type}</div>
                <div class="improvement-desc">${improvement.description}</div>
                <div class="improvement-time">${improvement.time}</div>
            `;
            feed.appendChild(itemDiv);
        });
    }

    updateReflectionPanel(data) {
        const content = document.getElementById('reflection-content');
        if (!content) return;

        // Update stats
        const statValues = content.querySelectorAll('.stat-value');
        statValues.forEach(value => {
            const label = value.previousElementSibling.textContent;
            if (label.includes('Insight') && data.insight_quality) {
                value.textContent = `${data.insight_quality}%`;
            } else if (label.includes('Self-Awareness') && data.self_awareness) {
                value.textContent = `${data.self_awareness}%`;
            }
        });

        // Update insights list
        const insightsList = content.querySelector('.insights-list');
        if (insightsList && data.insights) {
            insightsList.innerHTML = '';
            data.insights.slice(-3).forEach(insight => {
                const li = document.createElement('li');
                li.textContent = insight;
                li.className = 'fade-in';
                insightsList.appendChild(li);
            });
        }
    }

    updateMemoryGraph(graphData) {
        // ✅ 3. Memory Graph Panel Integration - Hook: lyrixa_memory_engine.get_graph_data()
        console.log('Updating memory graph with data:', graphData);

        // Find the memory graph container (could be in dashboard or dedicated panel)
        const graphContainer = document.querySelector('.memory-graph') ||
            document.querySelector('.dashboard-component:nth-child(3)');

        if (!graphContainer) {
            console.warn('Memory graph container not found');
            return;
        }

        // Clear existing content
        graphContainer.innerHTML = '<h3>🧠 Memory Network</h3>';

        // Create simple visualization
        const networkDiv = document.createElement('div');
        networkDiv.className = 'memory-network';
        networkDiv.style.cssText = `
            position: relative;
            height: 200px;
            background: linear-gradient(45deg, #001122, #002233);
            border-radius: 10px;
            padding: 10px;
            overflow: hidden;
        `;

        // Add nodes
        if (graphData.nodes) {
            graphData.nodes.forEach((node, index) => {
                const nodeEl = document.createElement('div');
                nodeEl.className = 'memory-node';
                nodeEl.textContent = node.label || node.id;
                nodeEl.style.cssText = `
                    position: absolute;
                    background: ${node.type === 'core' ? '#00ff88' : '#0088ff'};
                    color: black;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 12px;
                    font-weight: bold;
                    left: ${20 + (index * 80)}px;
                    top: ${50 + (index % 2) * 60}px;
                    transition: all 0.3s ease;
                `;

                // Add hover effect
                nodeEl.addEventListener('mouseenter', () => {
                    nodeEl.style.transform = 'scale(1.1)';
                    nodeEl.style.boxShadow = '0 0 20px rgba(0, 255, 136, 0.6)';
                });

                nodeEl.addEventListener('mouseleave', () => {
                    nodeEl.style.transform = 'scale(1)';
                    nodeEl.style.boxShadow = 'none';
                });

                networkDiv.appendChild(nodeEl);
            });
        }

        // Add network stats
        const statsDiv = document.createElement('div');
        statsDiv.className = 'network-stats';
        statsDiv.style.cssText = `
            position: absolute;
            bottom: 10px;
            right: 10px;
            color: #00ff88;
            font-size: 11px;
        `;

        const nodeCount = graphData.nodes ? graphData.nodes.length : 0;
        const edgeCount = graphData.edges ? graphData.edges.length : 0;
        statsDiv.innerHTML = `Nodes: ${nodeCount} | Connections: ${edgeCount}`;

        networkDiv.appendChild(statsDiv);
        graphContainer.appendChild(networkDiv);
    }

    initializeAnimations() {
        // Add fade-in animation to all components
        const components = document.querySelectorAll('.component-card');
        components.forEach((component, index) => {
            component.style.animationDelay = `${index * 0.1}s`;
            component.classList.add('fade-in');
        });

        // Start background animations
        this.startBackgroundAnimations();
    }

    startBackgroundAnimations() {
        // Subtle pulsing effect on status dot
        const statusDot = document.querySelector('.status-dot');
        if (statusDot) {
            statusDot.classList.add('active');
        }

        // Random thought updates for demo
        if (!this.qtBridge) {
            this.startDemoMode();
        }
    }

    startDemoMode() {
        // Demo mode: simulate data updates
        const demoThoughts = [
            "Processing user interaction patterns...",
            "Memory consolidation in progress",
            "Ethical framework validation complete",
            "Pattern recognition enhancement active",
            "Cognitive coherence optimization running",
            "Learning from conversation context",
            "Identity matrix stabilization ongoing",
            "Self-improvement metrics analysis",
            "Neural pathway optimization detected",
            "Consciousness integration successful"
        ];

        setInterval(() => {
            const timestamp = new Date().toLocaleTimeString('en-US', {
                hour12: false,
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });

            const randomThought = demoThoughts[Math.floor(Math.random() * demoThoughts.length)];

            this.updateThoughtLog([{
                timestamp: timestamp,
                content: randomThought
            }]);
        }, 3000);

        // Update stats periodically
        setInterval(() => {
            this.updateStats({
                memory_usage: 70 + Math.random() * 10,
                cpu_load: 20 + Math.random() * 15,
                coherence: 85 + Math.random() * 10,
                plugins_active: 12 + Math.floor(Math.random() * 5)
            });
        }, 5000);
    }

    startUpdateLoop() {
        // Request animation frame for smooth updates
        const update = () => {
            // Any per-frame updates can go here
            requestAnimationFrame(update);
        };
        requestAnimationFrame(update);
    }

    // Public API for Qt integration
    receiveMessage(sender, content) {
        this.addChatMessage(sender, content, sender.toLowerCase());
    }

    updateData(type, data) {
        this.handleDataUpdate(type, data);
    }

    setStatus(status, message) {
        const statusText = document.querySelector('.status-text');
        const statusInfo = document.querySelector('.status-info');

        if (statusText) statusText.textContent = `System Status: ${status}`;
        if (statusInfo) statusInfo.textContent = message;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.lyrixaInterface = new LyrixaWebInterface();
    console.log('Lyrixa web interface initialized');
});

// Qt WebChannel bridge functions
window.qt = window.qt || {};
window.sendToQt = function (message) {
    if (window.lyrixaInterface && window.lyrixaInterface.qtBridge) {
        window.lyrixaInterface.qtBridge.sendMessage(message);
    }
};

// Expose interface for Qt integration
window.addChatMessage = function (sender, content, type) {
    if (window.lyrixaInterface) {
        window.lyrixaInterface.addChatMessage(sender, content, type || 'system');
    }
};

window.updateStats = function (data) {
    if (window.lyrixaInterface) {
        window.lyrixaInterface.updateStats(data);
    }
};
