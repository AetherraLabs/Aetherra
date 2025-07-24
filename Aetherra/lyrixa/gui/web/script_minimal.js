// Lyrixa Web Interface - Minimal Compatible Version
var LyrixaInterface = {
    init: function () {
        console.log('Initializing Lyrixa Interface...');
        this.setupChat();
        this.setupBridge();
    },

    setupChat: function () {
        var sendBtn = document.getElementById('send-button');
        var chatInput = document.getElementById('chat-input');

        if (sendBtn) {
            sendBtn.onclick = function () {
                LyrixaInterface.sendMessage();
            };
        }

        if (chatInput) {
            chatInput.onkeypress = function (e) {
                if (e.keyCode === 13) {
                    LyrixaInterface.sendMessage();
                }
            };
        }
    },

    setupBridge: function () {
        console.log('Setting up bridge...');
        // Qt bridge setup will be handled by Qt WebChannel
    },

    sendMessage: function () {
        var input = document.getElementById('chat-input');
        if (!input || !input.value.trim()) return;

        var message = input.value.trim();
        this.addMessage('User', message, 'user');
        input.value = '';

        // Simulate response
        setTimeout(function () {
            LyrixaInterface.addMessage('Lyrixa', 'Processing your message...', 'lyrixa');
        }, 1000);
    },

    addMessage: function (sender, content, type) {
        var chat = document.getElementById('chat-display');
        if (!chat) return;

        var div = document.createElement('div');
        div.className = 'message ' + type + '-message';

        var time = new Date();
        var timeStr = time.getHours() + ':' + (time.getMinutes() < 10 ? '0' : '') + time.getMinutes();

        div.innerHTML = '<div class="message-header">' +
            '<span class="sender">' + sender + '</span>' +
            '<span class="timestamp">' + timeStr + '</span>' +
            '</div>' +
            '<div class="message-content">' + content + '</div>';

        chat.appendChild(div);
        chat.scrollTop = chat.scrollHeight;
    },

    // Methods expected by Qt interface
    setStatus: function (status, message) {
        console.log('Status:', status, message);
    },

    updateStats: function (data) {
        console.log('Stats update:', data);
    },

    updateReflectionPanel: function (data) {
        console.log('Reflection update:', data);
    },

    sendChatResponse: function (sender, message) {
        this.addMessage(sender, message, 'lyrixa');
    },

    updateMemoryGraph: function (data) {
        console.log('Memory graph update:', data);
    },

    updateThoughtLog: function (data) {
        console.log('Thought log update:', data);
    },

    updateImprovementFeed: function (data) {
        console.log('Improvement feed update:', data);
    },

    executeJavaScript: function (script) {
        try {
            eval(script);
        } catch (e) {
            console.error('Script error:', e);
        }
    },

    reloadInterface: function () {
        window.location.reload();
    }
};

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
        LyrixaInterface.init();
        window.lyrixaInterface = LyrixaInterface;
    });
} else {
    LyrixaInterface.init();
    window.lyrixaInterface = LyrixaInterface;
}
