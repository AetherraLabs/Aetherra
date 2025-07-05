#!/usr/bin/env python3
"""
Lyrixa Phase 2 Testing Script
Tests the new intelligent plugin system and intent recognition
"""

import os
import webbrowser


def create_phase2_test_page():
    """Create an advanced test page for Phase 2 features"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lyrixa Phase 2 - Intelligence Layer Test</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(100, 255, 218, 0.1);
            border-radius: 15px;
            border: 1px solid rgba(100, 255, 218, 0.3);
        }}

        .header h1 {{
            color: #64ffda;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .phase-badge {{
            background: linear-gradient(45deg, #64ffda, #00acc1);
            color: #1a1a1a;
            padding: 8px 16px;
            border-radius: 25px;
            font-weight: 600;
            display: inline-block;
            margin: 10px 0;
        }}

        .test-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin: 20px 0;
            border: 1px solid rgba(100, 255, 218, 0.2);
        }}

        .test-section h2 {{
            color: #64ffda;
            margin-bottom: 15px;
            font-size: 1.5em;
        }}

        .test-buttons {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .test-btn {{
            background: linear-gradient(45deg, rgba(100, 255, 218, 0.2), rgba(100, 255, 218, 0.1));
            border: 2px solid rgba(100, 255, 218, 0.3);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            text-align: left;
        }}

        .test-btn:hover {{
            background: linear-gradient(45deg, rgba(100, 255, 218, 0.3), rgba(100, 255, 218, 0.2));
            border-color: #64ffda;
            transform: translateY(-2px);
        }}

        .test-btn strong {{
            color: #64ffda;
            display: block;
            margin-bottom: 5px;
        }}

        .chat-container {{
            background: rgba(0, 0, 0, 0.3);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid rgba(100, 255, 218, 0.2);
            min-height: 400px;
            display: flex;
            flex-direction: column;
        }}

        .chat-messages {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }}

        .chat-input-area {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}

        .chat-input {{
            flex: 1;
            padding: 15px;
            border: 2px solid rgba(100, 255, 218, 0.3);
            background: rgba(255, 255, 255, 0.05);
            color: white;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
        }}

        .chat-input:focus {{
            border-color: #64ffda;
        }}

        .send-btn {{
            background: #64ffda;
            color: #1a1a1a;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .send-btn:hover {{
            background: #4fd3b8;
            transform: scale(1.05);
        }}

        .message {{
            margin: 10px 0;
            padding: 12px 16px;
            border-radius: 18px;
            display: inline-block;
            max-width: 80%;
            word-wrap: break-word;
        }}

        .user-message {{
            background: rgba(100, 255, 218, 0.2);
            margin-left: auto;
            text-align: right;
            border: 1px solid rgba(100, 255, 218, 0.3);
        }}

        .ai-message {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }}

        .status-active {{
            background: #4caf50;
            box-shadow: 0 0 10px #4caf50;
        }}

        .status-loading {{
            background: #ff9800;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
            100% {{ opacity: 1; }}
        }}

        .feature-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}

        .feature-item {{
            background: rgba(100, 255, 218, 0.1);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(100, 255, 218, 0.2);
        }}

        .feature-item h3 {{
            color: #64ffda;
            margin-bottom: 8px;
        }}

        .debug-panel {{
            background: rgba(0, 0, 0, 0.8);
            border-radius: 10px;
            padding: 15px;
            margin: 20px 0;
            border: 1px solid rgba(100, 255, 218, 0.2);
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }}

        .debug-panel h3 {{
            color: #64ffda;
            margin-bottom: 10px;
            font-family: 'Segoe UI', sans-serif;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 Lyrixa AI Assistant</h1>
        <div class="phase-badge">Phase 2: Intelligence Layer</div>
        <p>Plugin System • Intent Recognition • Advanced AI Capabilities</p>
        <div style="margin-top: 15px;">
            <span class="status-indicator status-loading" id="statusIndicator"></span>
            <span id="statusText">Loading AI systems...</span>
        </div>
    </div>

    <div class="test-section">
        <h2>🎯 Intent Recognition Testing</h2>
        <p>Test Lyrixa's ability to understand different types of requests and route them to appropriate plugins.</p>

        <div class="test-buttons">
            <button class="test-btn" onclick="testIntent('Generate a FastAPI application with user authentication')">
                <strong>Code Generation</strong>
                "Generate a FastAPI app..."
            </button>

            <button class="test-btn" onclick="testIntent('Analyze this code for bugs and optimize it')">
                <strong>Code Analysis</strong>
                "Analyze this code..."
            </button>

            <button class="test-btn" onclick="testIntent('Explain how React hooks work')">
                <strong>Learning Assistant</strong>
                "Explain React hooks..."
            </button>

            <button class="test-btn" onclick="testIntent('What is the best project structure for a Node.js app?')">
                <strong>Project Advisor</strong>
                "Best project structure..."
            </button>

            <button class="test-btn" onclick="testIntent('Hello! How are you today?')">
                <strong>General Chat</strong>
                "Hello! How are you?"
            </button>

            <button class="test-btn" onclick="testIntent('Create a React component with state management')">
                <strong>Complex Request</strong>
                "React component..."
            </button>
        </div>
    </div>

    <div class="test-section">
        <h2>🧩 Active Plugin System</h2>
        <div class="feature-list">
            <div class="feature-item">
                <h3>🛠️ Code Generator</h3>
                <p>Generates intelligent code for Python, JavaScript, React, FastAPI, and more.</p>
            </div>
            <div class="feature-item">
                <h3>🔍 Code Analyzer</h3>
                <p>Analyzes code for bugs, optimization opportunities, and explanations.</p>
            </div>
            <div class="feature-item">
                <h3>📚 Learning Assistant</h3>
                <p>Provides educational explanations and learning guidance.</p>
            </div>
            <div class="feature-item">
                <h3>🏗️ Project Advisor</h3>
                <p>Offers architectural guidance and best practices.</p>
            </div>
        </div>
    </div>

    <div class="test-section">
        <h2>💬 Interactive AI Chat</h2>
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="message ai-message">
                    Hello! I'm Lyrixa with Phase 2 intelligence. I now have advanced plugin capabilities and intent recognition. Try asking me to generate code, analyze problems, explain concepts, or provide project guidance!
                </div>
            </div>
            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput"
                       placeholder="Ask me to generate code, analyze problems, explain concepts, or anything else..."
                       onkeypress="if(event.key==='Enter') sendMessage()">
                <button class="send-btn" onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <div class="test-section">
        <h2>🔬 Debug Panel</h2>
        <div class="debug-panel" id="debugPanel">
            <h3>System Logs</h3>
            <div id="debugLog">Initializing debug panel...</div>
        </div>
    </div>

    <!-- Load Lyrixa Phase 2 Systems -->
    <script src="lyrixa/intelligence/intent_recognition.js"></script>
    <script src="lyrixa/plugins/plugin_manager.js"></script>
    <script src="lyrixa/core/personality.js"></script>
    <script src="lyrixa/core/lyrixa_engine.js"></script>

    <script>
        let lyrixaInstance = null;
        let scriptsLoaded = 0;
        const totalScripts = 4;

        function updateStatus(text, isActive = false) {{
            const indicator = document.getElementById('statusIndicator');
            const statusText = document.getElementById('statusText');

            indicator.className = `status-indicator ${{isActive ? 'status-active' : 'status-loading'}}`;
            statusText.textContent = text;
        }}

        function logDebug(message) {
            const debugLog = document.getElementById('debugLog');
            const timestamp = new Date().toLocaleTimeString();
            debugLog.innerHTML += `<br>[${timestamp}] ${message}`;
            debugLog.scrollTop = debugLog.scrollHeight;
        }

        function checkScriptsLoaded() {{
            scriptsLoaded++;
            logDebug(`Loaded script ${{scriptsLoaded}}/${{totalScripts}}`);
            updateStatus(`Loading AI systems... ${{scriptsLoaded}}/${{totalScripts}}`);

            if (scriptsLoaded === totalScripts) {{
                setTimeout(() => {{
                    try {{
                        lyrixaInstance = new LyrixaCore();
                        updateStatus('Phase 2 AI Systems Active', true);
                        logDebug('✅ Lyrixa Phase 2 fully initialized!');
                        logDebug(`✅ ${{lyrixaInstance.pluginManager ? lyrixaInstance.pluginManager.getActivePlugins().length : 0}} plugins active`);
                    }} catch (error) {{
                        logDebug(`❌ Error initializing: ${{error.message}}`);
                        updateStatus('Error loading AI systems');
                    }}
                }}, 1000);
            }}
        }}

        // Set up script load handlers
        window.addEventListener('load', () => {{
            // Scripts should be loaded by now, check for initialization
            if (typeof LyrixaCore !== 'undefined') {{
                checkScriptsLoaded();
            }}
        }});

        async function testIntent(message) {{
            if (!lyrixaInstance) {{
                addMessage('⚠️ Lyrixa is still loading. Please wait...', 'ai');
                return;
            }}

            addMessage(message, 'user');
            addMessage('🤔 Analyzing intent and selecting appropriate plugin...', 'ai');

            try {{
                const response = await lyrixaInstance.processMessage(message);

                // Remove thinking message
                const messages = document.getElementById('chatMessages');
                const lastMessage = messages.lastElementChild;
                if (lastMessage && lastMessage.textContent.includes('Analyzing intent')) {{
                    lastMessage.remove();
                }}

                addMessage(response.text, 'ai');

                logDebug(`Intent processed: ${{response.context?.intent || 'unknown'}}`);
                logDebug(`Plugin used: ${{response.context?.plugin || 'none'}}`);
                logDebug(`Confidence: ${{((response.confidence || 0) * 100).toFixed(1)}}%`);

            }} catch (error) {{
                addMessage(`❌ Error: ${{error.message}}`, 'ai');
                logDebug(`❌ Error: ${{error.message}}`);
            }}
        }}

        async function sendMessage() {{
            const input = document.getElementById('chatInput');
            const message = input.value.trim();

            if (!message) return;

            input.value = '';
            await testIntent(message);
        }}

        function addMessage(text, sender) {{
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}-message`;

            // Convert newlines to HTML breaks and handle formatting
            const formattedText = text
                .replace(/\\n/g, '<br>')
                .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                .replace(/\\*(.*?)\\*/g, '<em>$1</em>');

            messageDiv.innerHTML = formattedText;
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}

        // Initialize debug logging
        logDebug('Phase 2 test page initialized');
        logDebug('Loading intent recognition system...');
        logDebug('Loading plugin manager...');
        logDebug('Loading personality engine...');
        logDebug('Loading core engine...');
    </script>
</body>
</html>"""

    with open("lyrixa_phase2_test.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath("lyrixa_phase2_test.html")


def main():
    """Main test execution"""
    print("🚀 LYRIXA PHASE 2 - INTELLIGENCE LAYER TESTING")
    print("=" * 60)
    print("Testing advanced AI capabilities:")
    print("🎯 Intent Recognition System")
    print("🧩 Plugin System with Active Execution")
    print("🛠️ Code Generation & Analysis")
    print("📚 Learning & Project Assistance")
    print("💬 Enhanced Conversation Management")

    # Create test page
    print("\\n📄 Creating Phase 2 test page...")
    test_page_path = create_phase2_test_page()
    test_page_url = f"file:///{test_page_path.replace(os.sep, '/')}"

    print(f"✅ Created: {test_page_path}")
    print(f"🌐 URL: {test_page_url}")

    # Launch test page
    print("\\n🌐 Launching Phase 2 test environment...")
    try:
        webbrowser.open(test_page_url)
        print("✅ Test page launched successfully!")
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        return False

    # Testing instructions
    print("\\n🧪 PHASE 2 TESTING INSTRUCTIONS:")
    print("=" * 40)
    print("1. ✅ Wait for 'Phase 2 AI Systems Active' status")
    print("2. ✅ Test intent recognition with the preset buttons")
    print("3. ✅ Try typing complex requests in the chat")
    print("4. ✅ Watch the debug panel for system logs")
    print("5. ✅ Test different types of requests:")
    print("   • Code generation: 'Create a React component'")
    print("   • Code analysis: 'Review this code for bugs'")
    print("   • Learning: 'Explain how APIs work'")
    print("   • Project help: 'Best practices for folder structure'")
    print("6. ✅ Verify plugin system responses are intelligent")
    print("7. ✅ Check that different intents route to different plugins")

    print("\\n🔍 WHAT TO LOOK FOR:")
    print("• Intent recognition accuracy")
    print("• Plugin system execution")
    print("• Code generation quality")
    print("• Educational explanations")
    print("• System performance and logs")

    print("\\n🎉 PHASE 2 TESTING READY!")
    print("The advanced Lyrixa intelligence layer is now testable! 🚀")

    return True


if __name__ == "__main__":
    main()
