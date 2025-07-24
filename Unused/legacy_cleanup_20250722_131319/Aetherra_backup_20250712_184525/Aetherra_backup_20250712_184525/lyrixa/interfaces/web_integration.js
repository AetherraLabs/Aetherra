/**
 * Lyrixa Integration Script
 * Replaces the old static chat modal with intelligent AI assistant
 */

// Initialize Lyrixa when the page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 Initializing Lyrixa AI Assistant...");
    
    // Initialize Lyrixa Core
    window.lyrixaInstance = new LyrixaCore();
    
    // Replace the old showLyrixaDemo function
    window.showLyrixaDemo = showIntelligentLyrixa;
    
    console.log("✅ Lyrixa AI Assistant ready!");
});

/**
 * New Intelligent Lyrixa Chat Function
 * Replaces the old static suggestion buttons with real AI
 */
async function showIntelligentLyrixa() {
    const modal = document.getElementById('lyrixaModal');
    const chatContainer = document.getElementById('chatContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    
    // Clear old content and show modal
    chatContainer.innerHTML = '';
    modal.style.display = 'block';
    modal.classList.add('show');
    
    // Add welcome message with personality info
    const personality = window.lyrixaInstance.personality.getCurrentPersonality();
    await addMessage('ai', `Hello! I'm Lyrixa, your AI assistant. I'm currently in ${personality.name} mode. ${personality.greeting}`);
    
    // Add personality selector
    addPersonalitySelector();
    
    // Setup message handling
    setupMessageHandling();
    
    // Focus on input
    messageInput.focus();
}

/**
 * Add a message to the chat
 */
async function addMessage(sender, text, options = {}) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    if (sender === 'ai') {
        messageDiv.innerHTML = `
            <div class="ai-avatar">🧠</div>
            <div class="message-content">
                <div class="message-text">${text}</div>
                ${options.suggestedActions ? createSuggestedActions(options.suggestedActions) : ''}
                ${options.personality ? `<div class="personality-tag">${options.personality}</div>` : ''}
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${text}</div>
            </div>
            <div class="user-avatar">👤</div>
        `;
    }
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Add typing animation for AI messages
    if (sender === 'ai') {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 100);
    }
}

/**
 * Create suggested action buttons
 */
function createSuggestedActions(actions) {
    if (!actions || actions.length === 0) return '';
    
    const actionsHtml = actions.map(action => 
        `<button class="suggested-action" onclick="handleSuggestedAction('${action}')">${action}</button>`
    ).join('');
    
    return `<div class="suggested-actions">${actionsHtml}</div>`;
}

/**
 * Handle suggested action clicks
 */
async function handleSuggestedAction(action) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = action;
    await sendMessage();
}

/**
 * Add personality selector to chat
 */
function addPersonalitySelector() {
    const chatContainer = document.getElementById('chatContainer');
    const personalities = window.lyrixaInstance.personality.getAvailablePersonalities();
    
    const selectorDiv = document.createElement('div');
    selectorDiv.className = 'personality-selector';
    selectorDiv.innerHTML = `
        <div class="selector-label">🎭 Choose Personality:</div>
        <div class="personality-buttons">
            ${personalities.map(p => `
                <button class="personality-btn ${p.id === 'default' ? 'active' : ''}" 
                        onclick="switchPersonality('${p.id}')" 
                        title="${p.description}">
                    ${p.name}
                </button>
            `).join('')}
        </div>
    `;
    
    chatContainer.appendChild(selectorDiv);
}

/**
 * Switch personality
 */
async function switchPersonality(personalityId) {
    const response = await window.lyrixaInstance.switchPersonality(personalityId);
    await addMessage('ai', response.text, { personality: personalityId });
    
    // Update active button
    document.querySelectorAll('.personality-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[onclick="switchPersonality('${personalityId}')"]`).classList.add('active');
}

/**
 * Setup message input and sending
 */
function setupMessageHandling() {
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendMessage');
    
    // Send message function
    window.sendMessage = async function() {
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Add user message
        await addMessage('user', message);
        messageInput.value = '';
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="ai-avatar">🧠</div>
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        document.getElementById('chatContainer').appendChild(typingDiv);
        
        try {
            // Get AI response
            const response = await window.lyrixaInstance.processMessage(message);
            
            // Remove typing indicator
            typingDiv.remove();
            
            // Add AI response
            await addMessage('ai', response.text, {
                suggestedActions: response.suggestedActions,
                personality: response.personality
            });
            
        } catch (error) {
            console.error('Error getting AI response:', error);
            typingDiv.remove();
            await addMessage('ai', 'I apologize, but I encountered an error. Please try again.');
        }
    };
    
    // Event listeners
    sendButton.onclick = sendMessage;
    messageInput.onkeypress = function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };
}

/**
 * Enhanced modal close with memory save
 */
function closeLyrixaModal() {
    const modal = document.getElementById('lyrixaModal');
    modal.classList.remove('show');
    
    setTimeout(() => {
        modal.style.display = 'none';
        
        // Show memory summary in console
        const memoryCount = window.lyrixaInstance.memory.getCount();
        console.log(`💾 Conversation saved. Memory: ${memoryCount.total} interactions`);
        
    }, 300);
}

// Add styles for new features
const lyrixaStyles = `
.personality-selector {
    margin: 15px 0;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.selector-label {
    color: #64ffda;
    font-size: 14px;
    margin-bottom: 10px;
    font-weight: 500;
}

.personality-buttons {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.personality-btn {
    padding: 6px 12px;
    border: 1px solid rgba(100, 255, 218, 0.3);
    background: rgba(100, 255, 218, 0.1);
    color: #64ffda;
    border-radius: 15px;
    cursor: pointer;
    font-size: 12px;
    transition: all 0.3s ease;
}

.personality-btn:hover {
    background: rgba(100, 255, 218, 0.2);
    transform: translateY(-1px);
}

.personality-btn.active {
    background: #64ffda;
    color: #1a1a1a;
    font-weight: 600;
}

.suggested-actions {
    margin-top: 10px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.suggested-action {
    padding: 5px 10px;
    border: 1px solid rgba(100, 255, 218, 0.5);
    background: transparent;
    color: #64ffda;
    border-radius: 12px;
    cursor: pointer;
    font-size: 11px;
    transition: all 0.2s ease;
}

.suggested-action:hover {
    background: rgba(100, 255, 218, 0.1);
}

.personality-tag {
    font-size: 10px;
    color: rgba(100, 255, 218, 0.7);
    margin-top: 5px;
    font-style: italic;
}

.typing-indicator {
    display: flex;
    align-items: center;
    margin: 15px 0;
    opacity: 0.7;
}

.typing-dots {
    display: flex;
    gap: 4px;
    margin-left: 10px;
}

.typing-dots span {
    width: 6px;
    height: 6px;
    background: #64ffda;
    border-radius: 50%;
    animation: typing 1.5s infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}

.ai-message {
    animation: slideInLeft 0.3s ease;
}

.user-message {
    animation: slideInRight 0.3s ease;
}

@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}
`;

// Add styles to document
if (!document.getElementById('lyrixa-ai-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'lyrixa-ai-styles';
    styleSheet.textContent = lyrixaStyles;
    document.head.appendChild(styleSheet);
}

console.log("🎉 Lyrixa Integration Script loaded - AI assistant ready!");
