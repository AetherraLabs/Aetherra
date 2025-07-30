# launch_aetherra_gui.py
"""
Launches the Aetherra Lyrixa GUI (Vite/React dev server) from Python.
- Installs dependencies if needed
- Starts the Vite dev server
- Opens the browser to the GUI
"""

import os
import subprocess
import sys
import webbrowser

GUI_DIR = os.path.dirname(os.path.abspath(__file__))


# 1. Install dependencies if node_modules is missing
def ensure_dependencies():
    if not os.path.exists(os.path.join(GUI_DIR, "node_modules")):
        print("Installing frontend dependencies (npm install)...")
        try:
            subprocess.check_call("npm install", cwd=GUI_DIR, shell=True)
        except FileNotFoundError:
            print(
                "ERROR: npm (Node.js) is not installed or not in your PATH. Please install Node.js from https://nodejs.org/ and try again."
            )
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"npm install failed: {e}")
            sys.exit(1)


# 2. Start Vite dev server
def start_vite():
    print("Starting Vite dev server...")
    try:
        proc = subprocess.Popen("npm run dev", cwd=GUI_DIR, shell=True)
        return proc
    except FileNotFoundError:
        print(
            "ERROR: npm (Node.js) is not installed or not in your PATH. Please install Node.js from https://nodejs.org/ and try again."
        )
        sys.exit(1)


# 3. Open browser to localhost:3000 (Vite port for Lyrixa GUI)
def open_browser():
    url = "http://localhost:3000/"
    print(f"Opening browser at {url}")
    webbrowser.open(url)


if __name__ == "__main__":
    ensure_dependencies()
    proc = start_vite()
    open_browser()
    print("Aetherra Lyrixa GUI is launching. Press Ctrl+C to stop.")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("Shutting down GUI server...")
        proc.terminate()
        sys.exit(0)
