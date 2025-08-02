# launch_aetherra_gui.py
"""
Launches the Aetherra Lyrixa GUI (Vite/React dev server) from Python.
- Installs dependencies if needed
- Starts the Vite dev server
- Starts the API server for backend communication
- Opens the browser to the GUI
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
    """Start the Flask API server in a separate thread"""
    try:
        print("🚀 Starting Aetherra API server...")
        # Import and start the web interface server
        sys.path.insert(0, os.path.dirname(GUI_DIR))
        from Aetherra.gui.web_interface_server import AetherraWebServer

        # Create and run the web server
        server = AetherraWebServer(host="127.0.0.1", port=8686)
        server.start_server(debug=False, auto_open=False)
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        print("📝 Note: Some API features may not be available")


# 1. Install dependencies if node_modules is missing
def ensure_dependencies():
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("📦 Installing frontend dependencies (npm install)...")
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


# 2. Start Vite dev server
def start_vite():
    print("🌐 Starting Vite dev server...")
    try:
        proc = subprocess.Popen("npm run dev", cwd=FRONTEND_DIR, shell=True)
        return proc
    except FileNotFoundError:
        print(
            "❌ ERROR: npm (Node.js) is not installed or not in your PATH. Please install Node.js from https://nodejs.org/ and try again."
        )
        sys.exit(1)


# 3. Open browser to localhost:3000 (Vite port for Lyrixa GUI)
def open_browser():
    # Wait a moment for servers to start
    time.sleep(3)

    url = "http://localhost:3000/"
    print(f"🌍 Opening browser at {url}")
    webbrowser.open(url)

    print("💡 Note: API server is also running at http://localhost:8686")
    print("   You can access the alternative web interface there if needed.")


if __name__ == "__main__":
    print("🚀 Starting Aetherra Lyrixa GUI with integrated API server...")

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

    # Start API server in background thread
    print("🔧 Starting API server in background...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    # Start Vite dev server
    proc = start_vite()

    # Open browser
    open_browser()

    print("✅ Aetherra Lyrixa GUI is launching with full API support!")
    print("📝 Frontend: http://localhost:3000")
    print("📝 API Server: http://localhost:8686")
    print("📝 Press Ctrl+C to stop both servers.")

    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down GUI and API servers...")
        proc.terminate()
        sys.exit(0)
