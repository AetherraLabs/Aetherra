// Lyrixa Web Interface JavaScript - ES5 Compatible Version
function LyrixaWebInterface() {
    console.log('Initializing Lyrixa Web Interface...');
    this.qtBridge = null;
    this.setupEventListeners();
    this.initializeAnimations();
    this.setupQtBridge();
    this.startUpdateLoop();
}

LyrixaWebInterface.prototype.setupEventListeners = function () {
    var self = this;
    var chatInput = document.getElementById('chat-input');
    var sendButton = document.getElementById('send-button');

    if (sendButton) {
        sendButton.addEventListener('click', function () {
            self.sendMessage();
        });
    }

    if (chatInput) {
        chatInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                self.sendMessage();
            }
        });
        chatInput.focus();
    }
};

LyrixaWebInterface.prototype.setupQtBridge = function () {
    var self = this;
    console.log('Setting up Qt bridge...');
    this.qtBridge = null;

    if (typeof qt !== 'undefined' && qt.webChannelTransport) {
        console.log('Qt WebChannel transport detected');

        function initBridge() {
            if (typeof QWebChannel !== 'undefined') {
                try {
                    new QWebChannel(qt.webChannelTransport, function (channel) {
                        console.log('WebChannel connected');
                        if (channel.objects.bridge) {
                            self.qtBridge = channel.objects.bridge;
                            console.log('Qt bridge connected successfully');
                        } else {
                            console.warn('Bridge object not found in channel');
                        }
                    });
                } catch (e) {
                    console.error('Error setting up Qt bridge:', e);
                    self.qtBridge = null;
                }
            } else {
                console.log('QWebChannel not ready, retrying...');
                setTimeout(initBridge, 100);
            }
        }

        initBridge();
    } else {
        console.log('Qt WebChannel not available, running in standalone mode');
    }
};

LyrixaWebInterface.prototype.sendMessage = function () {
    var chatInput = document.getElementById('chat-input');
    if (!chatInput) return;

    var message = chatInput.value.trim();
    if (!message) return;

    this.addChatMessage('User', message, 'user');
    chatInput.value = '';

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
};

LyrixaWebInterface.prototype.simulateResponse = function (message) {
    var self = this;
    setTimeout(function () {
        self.addChatMessage('Lyrixa', self.generateResponse(message), 'lyrixa');
    }, 1000);
};

LyrixaWebInterface.prototype.generateResponse = function (message) {
    var responses = [
        "I'm processing that through my cognitive systems...",
        "Interesting perspective! Let me analyze that...",
        "I'm integrating that with my knowledge base...",
        "That's a fascinating question to explore...",
        "Processing through my neural networks..."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
};

LyrixaWebInterface.prototype.addChatMessage = function (sender, content, type) {
    var chatDisplay = document.getElementById('chat-display');
    if (!chatDisplay) return;

    var messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + type + '-message fade-in';

    var timestamp = new Date().toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit'
    });

    messageDiv.innerHTML =
        '<div class="message-header">' +
        '<span class="sender">' + sender + '</span>' +
        '<span class="timestamp">' + timestamp + '</span>' +
        '</div>' +
        '<div class="message-content">' + content + '</div>';

    chatDisplay.appendChild(messageDiv);
    chatDisplay.scrollTop = chatDisplay.scrollHeight;
};

LyrixaWebInterface.prototype.showTypingIndicator = function () {
    var self = this;
    var indicator = document.createElement('div');
    indicator.className = 'message lyrixa-message typing-indicator';
    indicator.innerHTML = '<div class="message-content">Lyrixa is thinking...</div>';

    var chatDisplay = document.getElementById('chat-display');
    if (chatDisplay) {
        chatDisplay.appendChild(indicator);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;

        setTimeout(function () {
            if (indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }, 2000);
    }
};

LyrixaWebInterface.prototype.updateSystemStats = function (data) {
    var memoryProgress = document.querySelector('.memory-progress');
    if (memoryProgress && data.memory_usage) {
        memoryProgress.style.width = data.memory_usage + '%';
    }

    var statValues = document.querySelectorAll('.stat-value');
    for (var i = 0; i < statValues.length; i++) {
        var value = statValues[i];
        var label = value.parentElement.textContent || '';

        if (label.includes('CPU') && data.cpu_load) {
            value.textContent = data.cpu_load + '%';
        } else if (label.includes('Coherence') && data.coherence) {
            value.textContent = data.coherence + '%';
        }
    }
};

LyrixaWebInterface.prototype.updateReflection = function (data) {
    var statValues = document.querySelectorAll('.reflection-panel .stat-value');
    for (var i = 0; i < statValues.length; i++) {
        var value = statValues[i];
        var label = value.parentElement.textContent || '';

        if (label.includes('Insight') && data.insight_quality) {
            value.textContent = data.insight_quality + '%';
        } else if (label.includes('Self-Awareness') && data.self_awareness) {
            value.textContent = data.self_awareness + '%';
        }
    }

    var insightsList = document.querySelector('.insights-list');
    if (insightsList && data.insights) {
        insightsList.innerHTML = '';
        for (var j = 0; j < data.insights.length; j++) {
            var li = document.createElement('li');
            li.textContent = data.insights[j];
            insightsList.appendChild(li);
        }
    }
};

LyrixaWebInterface.prototype.initializeAnimations = function () {
    var networkDivs = document.querySelectorAll('.neural-bg .network-node');
    for (var i = 0; i < networkDivs.length; i++) {
        var node = networkDivs[i];
        if (node.style) {
            node.style.animationDelay = (i * 0.1) + 's';
        }
    }
};

LyrixaWebInterface.prototype.startUpdateLoop = function () {
    var self = this;
    setInterval(function () {
        self.updateAnimations();
    }, 100);
};

LyrixaWebInterface.prototype.updateAnimations = function () {
    var nodes = document.querySelectorAll('.network-node');
    for (var i = 0; i < nodes.length; i++) {
        var node = nodes[i];
        if (node.style && Math.random() < 0.01) {
            node.style.opacity = Math.random() * 0.5 + 0.5;
        }
    }
};

// Additional methods that Qt interface expects
LyrixaWebInterface.prototype.setStatus = function (status, message) {
    console.log('Status update:', status, message);
    var statusElement = document.querySelector('.status-text');
    if (statusElement) {
        statusElement.textContent = 'System Status: ' + status;
    }
};

LyrixaWebInterface.prototype.updateStats = function (stats) {
    this.updateSystemStats(stats);
};

LyrixaWebInterface.prototype.updateMemoryGraph = function (graphData) {
    console.log('Memory graph update:', graphData);
    // Simple implementation for memory graph
    var memoryContainer = document.querySelector('.memory-graph');
    if (memoryContainer && graphData) {
        // Update memory visualization
    }
};

LyrixaWebInterface.prototype.updateReflectionPanel = function (data) {
    this.updateReflection(data);
};

LyrixaWebInterface.prototype.sendChatResponse = function (sender, message) {
    this.addChatMessage(sender, message, 'lyrixa');
};

LyrixaWebInterface.prototype.updateThoughtLog = function (thoughts) {
    console.log('Thought log update:', thoughts);
    // Implementation for thought log updates
};

LyrixaWebInterface.prototype.updateImprovementFeed = function (improvements) {
    console.log('Improvement feed update:', improvements);
    // Implementation for improvement feed updates
};

LyrixaWebInterface.prototype.executeJavaScript = function (script) {
    try {
        eval(script);
    } catch (e) {
        console.error('Error executing JavaScript:', e);
    }
};

LyrixaWebInterface.prototype.reloadInterface = function () {
    window.location.reload();
};

// Initialize the interface when the page loads
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM loaded, initializing Lyrixa interface...');
    window.lyrixaInterface = new LyrixaWebInterface();
});

// Fallback for Qt environments
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
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
