/**
 * 🎙️ Aetherra Lyrixa Effects - Phase 1
 * ====================================
 *
 * JavaScript effects and interactions for web panels
 * - QWebChannel integration for Python ↔ JS communication
 * - Smooth animations and transitions
 * - Real-time data updates
 * - Interactive elements with Aetherra styling
 */

// === GLOBAL VARIABLES ===
let pybridge = null;
let currentPanel = null;
let animationFrameId = null;

// === COMPATIBILITY FUNCTIONS ===
/**
 * Cross-browser compatible element matching
 */
function elementMatches(element, selector) {
    if (!element || !selector) return false;

    // Modern browsers
    if (element.matches) {
        return element.matches(selector);
    }

    // Fallback for older browsers
    if (element.matchesSelector) {
        return element.matchesSelector(selector);
    }

    if (element.webkitMatchesSelector) {
        return element.webkitMatchesSelector(selector);
    }

    if (element.mozMatchesSelector) {
        return element.mozMatchesSelector(selector);
    }

    if (element.msMatchesSelector) {
        return element.msMatchesSelector(selector);
    }

    // Manual fallback with null checks
    try {
        const doc = element.document || element.ownerDocument;
        if (!doc) return false;

        const matches = doc.querySelectorAll(selector);
        if (!matches) return false;

        let i = matches.length;
        while (--i >= 0 && matches.item(i) !== element) { }
        return i > -1;
    } catch (error) {
        console.debug('Element matching error:', error);
        return false;
    }
}

// === INITIALIZATION ===
document.addEventListener('DOMContentLoaded', function () {
    initializeWebChannel();
    initializePanel();
    setupEventListeners();
    startAnimationLoop();
});

/**
 * Initialize QWebChannel communication with Python
 */
function initializeWebChannel() {
    try {
        // Check if QWebChannel is available
        if (typeof QWebChannel === 'undefined') {
            console.warn('[WARN] QWebChannel not available, running in standalone mode');
            return;
        }

        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            new QWebChannel(qt.webChannelTransport, function (channel) {
                pybridge = channel.objects.pybridge;
                console.log('🌉 Phase 2: Live Context Bridge established');

                // === PHASE 2: Connect to all backend signals ===

                // Memory system updates
                if (pybridge && pybridge.memory_updated) {
                    pybridge.memory_updated.connect(function (jsonData) {
                        handleMemoryUpdate(JSON.parse(jsonData));
                    });
                }

                // Plugin system updates
                if (pybridge && pybridge.plugin_updated) {
                    pybridge.plugin_updated.connect(function (jsonData) {
                        handlePluginUpdate(JSON.parse(jsonData));
                    });
                }

                // Agent system updates
                if (pybridge && pybridge.agent_updated) {
                    pybridge.agent_updated.connect(function (jsonData) {
                        handleAgentUpdate(JSON.parse(jsonData));
                    });
                }

                // System metrics updates
                if (pybridge && pybridge.metrics_updated) {
                    pybridge.metrics_updated.connect(function (jsonData) {
                        handleMetricsUpdate(JSON.parse(jsonData));
                    });
                }

                // System notifications
                if (pybridge && pybridge.notification_sent) {
                    pybridge.notification_sent.connect(function (jsonData) {
                        handleNotification(JSON.parse(jsonData));
                    });
                }

                // Request initial data
                requestAllData();
            });
        } else {
            console.log('[WARN] QWebChannel not available - running in standalone mode');
            // Initialize with mock data for standalone testing
            initializeMockData();
        }
    } catch (error) {
        console.error('❌ WebChannel initialization error:', error);
        initializeMockData();
    }
}

/**
 * Initialize the current panel based on data-panel attribute
 */
function initializePanel() {
    const panelContainer = document.querySelector('[data-panel]');
    if (panelContainer) {
        currentPanel = panelContainer.getAttribute('data-panel');
        console.log(`🎯 Initializing ${currentPanel} panel`);

        // Apply fade-in animation
        panelContainer.classList.add('fade-in');

        // Initialize panel-specific features
        switch (currentPanel) {
            case 'dashboard':
                initializeDashboard();
                break;
            case 'plugins':
                initializePlugins();
                break;
            case 'memory':
                initializeMemory();
                break;
            case 'metrics':
                initializeMetrics();
                break;
            default:
                initializeDefault();
        }
    }
}

/**
 * Setup event listeners for interactive elements
 */
function setupEventListeners() {
    // Button click effects
    document.addEventListener('click', function (e) {
        if (elementMatches(e.target, '.btn') || e.target.closest('.btn')) {
            createRippleEffect(e);
            handleButtonClick(e);
        }
    });

    // Remove hover event listeners - let CSS handle hover effects to avoid conflicts
    // This prevents blur artifacts caused by JavaScript and CSS both handling hover

    // Prevent context menu on production
    document.addEventListener('contextmenu', function (e) {
        e.preventDefault();
    });
}

/**
 * Start the main animation loop
 */
function startAnimationLoop() {
    function animate() {
        updateAnimations();
        animationFrameId = requestAnimationFrame(animate);
    }
    animate();
}

/**
 * Handle data updates from Python backend
 */
function handleDataUpdate(data) {
    console.log('📊 Received data update:', data);

    // Update metrics if available
    if (data.metrics) {
        updateMetricsDisplay(data.metrics);
    }

    // Update plugin data if available
    if (data.plugins) {
        updatePluginsDisplay(data.plugins);
    }

    // Update memory data if available
    if (data.memory) {
        updateMemoryDisplay(data.memory);
    }
}

// === PHASE 2: SPECIALIZED UPDATE HANDLERS ===

/**
 * Handle memory system updates
 */
function handleMemoryUpdate(memoryData) {
    console.log('🧠 Memory system update:', memoryData);
    updateMemoryDisplay(memoryData);
    updateMemoryIndicators(memoryData);
}

/**
 * Handle plugin system updates
 */
function handlePluginUpdate(pluginData) {
    console.log('🔌 Plugin system update:', pluginData);
    updatePluginsDisplay(pluginData);
    updatePluginIndicators(pluginData);
}

/**
 * Handle agent system updates
 */
function handleAgentUpdate(agentData) {
    console.log('🤖 Agent system update:', agentData);
    updateAgentDisplay(agentData);
    updateAgentIndicators(agentData);
}

/**
 * Handle system metrics updates
 */
function handleMetricsUpdate(metricsData) {
    console.log('📊 Metrics update:', metricsData);
    updateMetricsDisplay(metricsData);
    updateSystemIndicators(metricsData);
}

/**
 * Handle system notifications
 */
function handleNotification(notification) {
    console.log('🔔 Notification:', notification);
    showNotification(notification.level, notification.message);
}

/**
 * Send command to Python backend (Phase 2: Enhanced Commands)
 */
function sendCommand(type, payload = {}) {
    if (pybridge && pybridge.handlePanelCommand) {
        const command = JSON.stringify({ type, payload });
        pybridge.handlePanelCommand(command);
        console.log('📤 Sent command to Python:', { type, payload });
    } else {
        console.log('[WARN] Python bridge not available');
    }
}

/**
 * Send message to Python backend (Phase 1 compatibility)
 */
function sendToPython(type, payload = {}) {
    // Use Phase 2 command system
    sendCommand(type, payload);
}

/**
 * Request initial data from Python (Phase 2: All Categories)
 */
function requestAllData() {
    if (pybridge && pybridge.getAllData) {
        pybridge.getAllData().then(data => {
            if (data) {
                const allData = JSON.parse(data);
                console.log('[DISC] Received all initial data:', allData);

                // Update all displays with initial data
                if (allData.memory) handleMemoryUpdate(allData.memory);
                if (allData.plugins) handlePluginUpdate(allData.plugins);
                if (allData.agents) handleAgentUpdate(allData.agents);
                if (allData.metrics) handleMetricsUpdate(allData.metrics);
            }
        }).catch(error => {
            console.warn('[WARN] Failed to get initial data:', error);
        });
    }
}

/**
 * Request initial data from Python (Phase 1 compatibility)
 */
function requestInitialData() {
    requestAllData();
}

/**
 * Initialize mock data for standalone testing
 */
function initializeMockData() {
    setTimeout(() => {
        const mockData = {
            metrics: {
                memory_load: 45,
                cpu_usage: 23,
                agents_active: 7,
                plugins_loaded: 12
            },
            plugins: [
                { name: 'Memory Manager', status: 'active', version: '1.0.0' },
                { name: 'Analytics Engine', status: 'active', version: '2.1.0' },
                { name: 'Chat Handler', status: 'loaded', version: '1.5.2' }
            ]
        };
        handleDataUpdate(mockData);
    }, 1000);
}

// === PANEL-SPECIFIC INITIALIZERS ===

function initializeDashboard() {
    console.log('🧠 Initializing Neural Interface dashboard');

    // Create floating particles effect
    createParticleEffect();

    // Setup pulsing effects for the main orb
    const glowOrb = document.querySelector('.glow-orb');
    if (glowOrb) {
        setupOrbInteraction(glowOrb);
    }
}

function initializePlugins() {
    console.log('🔌 Initializing Plugin Manager');
    // Plugin-specific initialization will be added in Phase 2
}

function initializeMemory() {
    console.log('💭 Initializing Memory panel');
    // Memory-specific initialization will be added in Phase 2
}

function initializeMetrics() {
    console.log('📈 Initializing Metrics panel');
    // Metrics-specific initialization will be added in Phase 2
}

function initializeDefault() {
    console.log('✨ Initializing default panel');
}

// === ANIMATION FUNCTIONS ===

/**
 * Create ripple effect on button click
 */
function createRippleEffect(event) {
    const button = event.target.closest('.btn');
    if (!button) return;

    const rect = button.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    const ripple = document.createElement('div');
    ripple.style.cssText = `
        position: absolute;
        border-radius: 50%;
        background: rgba(0, 255, 136, 0.6);
        transform: scale(0);
        animation: ripple 0.6s linear;
        left: ${x - 10}px;
        top: ${y - 10}px;
        width: 20px;
        height: 20px;
        pointer-events: none;
    `;

    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Animate card hover effects
 */
function animateCardHover(card, isEntering) {
    if (isEntering) {
        // Match the CSS hover styles exactly to avoid conflicts
        card.style.transform = 'translateY(-2px)';
        card.style.boxShadow = 'var(--glow-green)';
        card.style.borderColor = 'var(--aetherra-green-dim)';
    } else {
        // Reset to original state
        card.style.transform = '';
        card.style.boxShadow = '';
        card.style.borderColor = '';
    }
}

/**
 * Setup orb interaction effects
 */
function setupOrbInteraction(orb) {
    orb.addEventListener('click', function () {
        // Create pulsing effect on click
        orb.style.animation = 'none';
        orb.style.transform = 'scale(1.3)';
        orb.style.opacity = '1';

        setTimeout(() => {
            orb.style.animation = 'pulse-glow 3s ease-in-out infinite alternate';
            orb.style.transform = '';
            orb.style.opacity = '';
        }, 200);

        // Send interaction to Python
        sendToPython('orb_interaction', { panel: currentPanel });
    });
}

/**
 * Create floating particle effect
 */
function createParticleEffect() {
    const particleContainer = document.createElement('div');
    particleContainer.className = 'particle-container';
    particleContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
    `;

    document.body.appendChild(particleContainer);

    // Create individual particles
    for (let i = 0; i < 20; i++) {
        setTimeout(() => createParticle(particleContainer), i * 200);
    }
}

/**
 * Create individual floating particle
 */
function createParticle(container) {
    const particle = document.createElement('div');
    particle.style.cssText = `
        position: absolute;
        width: 2px;
        height: 2px;
        background: rgba(0, 255, 136, 0.6);
        border-radius: 50%;
        pointer-events: none;
    `;

    // Random starting position
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';

    container.appendChild(particle);

    // Animate particle
    animateParticle(particle);
}

/**
 * Animate individual particle movement
 */
function animateParticle(particle) {
    let x = parseFloat(particle.style.left);
    let y = parseFloat(particle.style.top);
    let vx = (Math.random() - 0.5) * 0.5;
    let vy = (Math.random() - 0.5) * 0.5;
    let opacity = 0.6;

    function updateParticle() {
        x += vx;
        y += vy;

        // Bounce off edges
        if (x <= 0 || x >= 100) vx *= -1;
        if (y <= 0 || y >= 100) vy *= -1;

        // Pulse opacity
        opacity = 0.3 + 0.3 * Math.sin(Date.now() * 0.003);

        particle.style.left = x + '%';
        particle.style.top = y + '%';
        particle.style.opacity = opacity;

        requestAnimationFrame(updateParticle);
    }

    updateParticle();
}

/**
 * Handle button clicks (Phase 2: Enhanced Commands)
 */
function handleButtonClick(event) {
    const button = event.target.closest('.btn');
    if (!button) return;

    const action = button.getAttribute('data-action');
    const plugin = button.getAttribute('data-plugin');
    const goal = button.getAttribute('data-goal');

    if (action) {
        // Determine command type based on context
        let commandType = 'system_command';
        let payload = { action, panel: currentPanel };

        if (plugin) {
            commandType = 'plugin_action';
            payload.plugin = plugin;
        } else if (goal) {
            commandType = 'agent_command';
            payload.goal = goal;
        } else if (action.startsWith('memory_')) {
            commandType = 'memory_query';
        }

        sendCommand(commandType, payload);
    }
}

/**
 * Update animations (called in animation loop)
 */
function updateAnimations() {
    // Update any time-based animations here
    try {
        const glowOrbs = document.querySelectorAll('.glow-orb');
        if (glowOrbs && glowOrbs.length > 0) {
            glowOrbs.forEach(orb => {
                // Add subtle random variations to the glow
                const intensity = 0.7 + 0.3 * Math.sin(Date.now() * 0.002);
                orb.style.filter = `brightness(${intensity})`;
            });
        }
    } catch (error) {
        // Silently handle any DOM errors
        console.debug('Animation update error:', error);
    }
}

/**
 * Update status display
 */
function updateStatus(status) {
    console.log('📱 Status update:', status);
    // Status update logic will be expanded in Phase 2
}

/**
 * Update metrics display
 */
function updateMetricsDisplay(metrics) {
    console.log('📊 Updating metrics:', metrics);

    // Update metric values if elements exist
    Object.entries(metrics).forEach(([key, value]) => {
        const element = document.querySelector(`[data-metric="${key}"]`);
        if (element) {
            animateValueChange(element, value);
        }
    });
}

/**
 * Update plugins display (Phase 2)
 */
function updatePluginsDisplay(pluginData) {
    console.log('🔌 Updating plugins display:', pluginData);

    // Update plugin count indicators
    const activeCountEl = document.querySelector('[data-metric="plugins_active"]');
    if (activeCountEl && pluginData.active_count !== undefined) {
        animateValueChange(activeCountEl, pluginData.active_count);
    }

    const totalCountEl = document.querySelector('[data-metric="plugins_total"]');
    if (totalCountEl && pluginData.total_count !== undefined) {
        animateValueChange(totalCountEl, pluginData.total_count);
    }

    // Update plugin list if container exists
    const pluginList = document.querySelector('.plugin-list');
    if (pluginList && pluginData.loaded_plugins) {
        updatePluginList(pluginList, pluginData.loaded_plugins);
    }
}

/**
 * Update memory display (Phase 2)
 */
function updateMemoryDisplay(memoryData) {
    console.log('🧠 Updating memory display:', memoryData);

    // Update memory metrics
    const memoryLoadEl = document.querySelector('[data-metric="memory_load"]');
    if (memoryLoadEl && memoryData.memory_load !== undefined) {
        animateValueChange(memoryLoadEl, memoryData.memory_load);
    }

    const totalMemoriesEl = document.querySelector('[data-metric="total_memories"]');
    if (totalMemoriesEl && memoryData.total_memories !== undefined) {
        animateValueChange(totalMemoriesEl, memoryData.total_memories);
    }
}

/**
 * Update agent display (Phase 2)
 */
function updateAgentDisplay(agentData) {
    console.log('🤖 Updating agent display:', agentData);

    // Update agent count
    const activeAgentsEl = document.querySelector('[data-metric="agents_active"]');
    if (activeAgentsEl && agentData.active_agents !== undefined) {
        animateValueChange(activeAgentsEl, agentData.active_agents);
    }

    // Update current goals list
    const goalsList = document.querySelector('.goals-list');
    if (goalsList && agentData.current_goals) {
        updateGoalsList(goalsList, agentData.current_goals);
    }
}

/**
 * Update system indicators (Phase 2)
 */
function updateSystemIndicators(metricsData) {
    // Update status indicators based on metrics
    updateStatusIndicator('cpu', metricsData.cpu_usage);
    updateStatusIndicator('memory', metricsData.memory_usage);
}

/**
 * Update plugin indicators (Phase 2)
 */
function updatePluginIndicators(pluginData) {
    const statusEl = document.querySelector('.plugin-status');
    if (statusEl) {
        statusEl.textContent = pluginData.status || 'Unknown';
        statusEl.className = `plugin-status status-${pluginData.status}`;
    }
}

/**
 * Update memory indicators (Phase 2)
 */
function updateMemoryIndicators(memoryData) {
    const statusEl = document.querySelector('.memory-status');
    if (statusEl) {
        statusEl.textContent = memoryData.status || 'Unknown';
        statusEl.className = `memory-status status-${memoryData.status}`;
    }
}

/**
 * Update agent indicators (Phase 2)
 */
function updateAgentIndicators(agentData) {
    const statusEl = document.querySelector('.agent-status');
    if (statusEl) {
        statusEl.textContent = agentData.status || 'Unknown';
        statusEl.className = `agent-status status-${agentData.status}`;
    }
}

/**
 * Show notification (Phase 2)
 */
function showNotification(level, message) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${level}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(level)}</span>
            <span class="notification-message">${message}</span>
        </div>
    `;

    // Add to document
    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);

    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Helper functions for Phase 2
 */
function getNotificationIcon(level) {
    const icons = {
        'info': 'ℹ️',
        'success': '✅',
        'warning': '[WARN]',
        'error': '❌'
    };
    return icons[level] || 'ℹ️';
}

function updateStatusIndicator(type, value) {
    const indicator = document.querySelector(`[data-indicator="${type}"]`);
    if (indicator) {
        let status = 'normal';
        if (value > 80) status = 'high';
        else if (value > 60) status = 'medium';

        indicator.className = `status-indicator status-${status}`;
    }
}

function updatePluginList(container, plugins) {
    container.innerHTML = plugins.map(plugin => `
        <div class="plugin-item status-${plugin.status}">
            <span class="plugin-name">${plugin.name}</span>
            <span class="plugin-version">v${plugin.version}</span>
            <span class="plugin-status">${plugin.status}</span>
        </div>
    `).join('');
}

function updateGoalsList(container, goals) {
    container.innerHTML = goals.map(goal => `
        <div class="goal-item">
            <span class="goal-text">${goal}</span>
        </div>
    `).join('');
}

/**
 * Animate value changes in metric displays
 */
function animateValueChange(element, newValue) {
    const oldValue = parseFloat(element.textContent) || 0;
    const duration = 1000;
    const startTime = performance.now();

    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function for smooth animation
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const currentValue = oldValue + (newValue - oldValue) * easeOut;

        element.textContent = Math.round(currentValue);

        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }

    requestAnimationFrame(updateValue);
}

// === CSS ANIMATIONS (injected dynamically) ===
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .particle-container {
        animation: fadeIn 2s ease-in;
    }

    /* Phase 2: Notification System */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(26, 26, 26, 0.95);
        border: 1px solid var(--aetherra-green-dim);
        border-radius: var(--radius-md);
        padding: 12px 16px;
        max-width: 300px;
        z-index: 1000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .notification.show {
        transform: translateX(0);
    }

    .notification-info { border-color: var(--aetherra-blue); }
    .notification-success { border-color: var(--aetherra-green); }
    .notification-warning { border-color: #f59e0b; }
    .notification-error { border-color: #ef4444; }

    .notification-content {
        display: flex;
        align-items: center;
        gap: 8px;
        color: white;
        font-size: 14px;
    }

    .notification-icon {
        font-size: 16px;
    }

    /* Status indicators */
    .status-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
    }

    .status-normal { background: var(--aetherra-green); }
    .status-medium { background: #f59e0b; }
    .status-high { background: #ef4444; }

    /* Plugin/Memory/Agent status */
    .plugin-status, .memory-status, .agent-status {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 12px;
        text-transform: uppercase;
        font-weight: bold;
    }

    .status-active, .status-operational, .status-thinking {
        background: rgba(0, 255, 136, 0.2);
        color: var(--aetherra-green);
    }

    .status-loaded, .status-idle {
        background: rgba(139, 92, 246, 0.2);
        color: var(--aetherra-purple);
    }

    .status-error, .status-offline {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
    }
`;
document.head.appendChild(style);

// === CLEANUP ===
window.addEventListener('beforeunload', function () {
    if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
    }
});

// === EXPORT FOR GLOBAL ACCESS ===
window.LyrixaEffects = {
    // Phase 1 functions
    sendToPython,
    createRippleEffect,
    animateValueChange,
    updateMetricsDisplay,

    // Phase 2 functions
    sendCommand,
    requestAllData,
    handleMemoryUpdate,
    handlePluginUpdate,
    handleAgentUpdate,
    handleMetricsUpdate,
    showNotification
};
