# launch_aetherra_gui.py
"""
🚀 Aetherra AI OS - Enhanced GUI Launcher
==========================================

Launches the Aetherra Lyrixa GUI with full AI capabilities:

🧠 Enhanced Features Available:
- Enhanced Conversational AI (#7): Multi-turn memory, intent translation
- Intelligent Error Handling (#8): AI-powered self-correction
- Advanced Memory Systems (#5): Cross-session memory persistence
- Analytics & Insights Engine (#6): Real-time performance monitoring
- Specialized Agent Ecosystem: Data, Technical, Support, Security agents
- Ethics Integration: Bias detection and moral reasoning

🌐 What This Launcher Does:
- Installs React/Node.js dependencies if needed
- Starts the enhanced Flask API server with all AI features
- Launches the Vite dev server for the React frontend
- Opens browser to the integrated AI interface
- Provides real-time WebSocket communication

[TOOL] Technical Stack:
- Backend: Flask + SocketIO with enhanced Lyrixa AI integration
- Frontend: React + Vite with real-time dashboard
- AI Features: OpenAI integration, memory systems, error handling
- Monitoring: Analytics dashboard with insights generation
"""

import os
import subprocess
import sys
import threading
import time
import webbrowser

GUI_DIR = os.path.dirname(os.path.abspath(__file__))
# The actual React frontend is in lyrixa_core/gui
FRONTEND_DIR = os.path.join(os.path.dirname(GUI_DIR), "lyrixa_core", "gui")


def start_api_server():
    """Start the Enhanced Aetherra API server with full AI capabilities"""
    try:
        print("🚀 Starting Enhanced Aetherra AI API Server...")
        print("   🧠 Enhanced Conversational AI (#7)")
        print("   [TOOL] Intelligent Error Handling (#8)")
        print("   📊 Analytics & Insights Engine (#6)")
        print("   🧠 Advanced Memory Systems (#5)")
        print("   🤖 Specialized Agent Ecosystem")
        print("   ⚖️ Ethics & Bias Detection")

        # Import and start the web interface server
        sys.path.insert(0, os.path.dirname(GUI_DIR))
        from Aetherra.gui.web_interface_server import AetherraWebServer

        # Create and run the enhanced web server
        server = AetherraWebServer(host="127.0.0.1", port=8686)
        print("✅ Enhanced API Server initialized with AI features")
        server.start_server(debug=False, auto_open=False)
    except Exception as e:
        print(f"❌ Failed to start Enhanced API server: {e}")
        print("📝 Note: Some AI features may not be available")
        print("🔍 Check that all dependencies are installed:")
        print("   - Enhanced Conversational AI components")
        print("   - Intelligent Error Handler modules")
        print("   - Analytics & Memory engines")


# 1. Install dependencies if node_modules is missing
def ensure_dependencies():
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("[DISC] Installing frontend dependencies (npm install)...")
        try:
            subprocess.check_call("npm install", cwd=FRONTEND_DIR, shell=True)
        except FileNotFoundError:
            print(
                "❌ ERROR: npm (Node.js) is not installed or not in your PATH. Please install Node.js from https://nodejs.org/ and try again."
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"❌ npm install failed: {e}")
            sys.exit(1)


# 2. Start Enhanced Vite dev server
def start_vite():
    print("🌐 Starting Enhanced React Frontend (Vite dev server)...")
    print("   📱 Modern React interface with real-time AI integration")
    print("   📊 Live analytics dashboard and system monitoring")
    print("   💬 Enhanced chat interface with multi-turn memory")
    try:
        proc = subprocess.Popen("npm run dev", cwd=FRONTEND_DIR, shell=True)
        return proc
    except FileNotFoundError:
        print(
            "❌ ERROR: npm (Node.js) is not installed or not in your PATH. Please install Node.js from https://nodejs.org/ and try again."
        )
        sys.exit(1)


# 3. Open browser to Enhanced Aetherra AI Interface
def open_browser():
    # Wait a moment for servers to start
    time.sleep(3)

    url = "http://localhost:3000/"
    print(f"🌍 Opening Enhanced Aetherra AI Interface at {url}")
    print("🎯 Available Features:")
    print("   💬 Enhanced Conversational AI with multi-turn memory")
    print("   [TOOL] Real-time error monitoring and self-correction")
    print("   📊 Live analytics dashboard with AI insights")
    print("   🧠 Advanced memory systems with pattern learning")
    print("   🤖 Specialized agents for different tasks")
    print("   ⚖️ Ethics monitoring and bias detection")

    webbrowser.open(url)

    print(f"\n💡 API Server Details:")
    print(f"   🔗 Main API: http://localhost:8686")
    print(f"   📊 System Status: http://localhost:8686/api/system/status")
    print(f"   🧠 Enhanced Chat: http://localhost:8686/api/conversation/enhanced")
    print(f"   [TOOL] Error Handler: http://localhost:8686/api/errors/status")
    print(f"   📈 Analytics: http://localhost:8686/api/analytics/status")
    print(f"   💾 Memory: http://localhost:8686/api/memory/advanced/status")


if __name__ == "__main__":
    print("🚀 LAUNCHING AETHERRA AI OS - ENHANCED GUI INTERFACE")
    print("=" * 60)
    print("🌟 Roadmap Items Implemented:")
    print("   ✅ Advanced Memory Systems (#5)")
    print("   ✅ Analytics & Insights Engine (#6)")
    print("   ✅ Enhanced Conversational AI (#7)")
    print("   ✅ Intelligent Error Handling (#8)")
    print("=" * 60)

    # Check if frontend directory exists
    if not os.path.exists(FRONTEND_DIR):
        print(f"❌ ERROR: Frontend directory not found at {FRONTEND_DIR}")
        print("📝 Note: The React frontend should be in Aetherra/lyrixa_core/gui")
        sys.exit(1)

    # Check if package.json exists
    if not os.path.exists(os.path.join(FRONTEND_DIR, "package.json")):
        print(f"❌ ERROR: package.json not found in {FRONTEND_DIR}")
        print("📝 Note: This doesn't appear to be a valid Node.js project")
        sys.exit(1)

    ensure_dependencies()

    # Start Enhanced API server in background thread
    print("[TOOL] Initializing Enhanced AI Systems...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    # Start Enhanced Vite dev server
    proc = start_vite()

    # Open browser to Enhanced Interface
    open_browser()

    print("\n✅ AETHERRA AI OS INTERFACE LAUNCHED SUCCESSFULLY!")
    print("🌐 Frontend Interface: http://localhost:3000")
    print("� Enhanced API Server: http://localhost:8686")
    print("📝 Press Ctrl+C to shutdown all services.")
    print("\n🎯 Available AI Features:")
    print("   💬 Multi-turn conversational AI with memory")
    print("   [TOOL] Intelligent error handling with self-correction")
    print("   📊 Real-time analytics and performance insights")
    print("   🧠 Advanced memory systems with pattern learning")
    print("   🤖 Specialized agents for complex tasks")
    print("   ⚖️ Ethics monitoring and bias detection")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Aetherra AI OS Interface...")
        print("   Stopping Enhanced API Server...")
        print("   Stopping React Frontend...")
        proc.terminate()
        print("✅ Aetherra AI OS Interface shutdown complete.")
        sys.exit(0)
