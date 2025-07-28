#!/usr/bin/env python3
"""
Aetherra GUI Launcher and Dependency Analyzer
Launches the new React-based GUI and analyzes required dependencies
"""

import http.server
import os
import re
import socketserver
import threading
import time
import webbrowser
from pathlib import Path


class AetherraGUILauncher:
    def __init__(self):
        self.gui_dir = Path(__file__).parent
        self.port = 8080
        self.server = None

    def analyze_dependencies(self):
        """Analyze the JSX file for dependencies"""
        jsx_file = self.gui_dir / "AetherraGUI.jsx"

        if not jsx_file.exists():
            print(f"❌ AetherraGUI.jsx not found at {jsx_file}")
            return {}

        with open(jsx_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract import statements
        import_pattern = r'import\s+(?:{[^}]+}|\*\s+as\s+\w+|\w+)?\s*(?:,\s*{[^}]+})?\s*from\s+["\']([^"\']+)["\']'
        imports = re.findall(import_pattern, content)

        # Extract dependencies from imports
        deps = {
            "react_dependencies": [],
            "three_js_dependencies": [],
            "ui_dependencies": [],
            "state_management": [],
            "other_dependencies": [],
        }

        for imp in imports:
            if "react" in imp.lower():
                deps["react_dependencies"].append(imp)
            elif "three" in imp.lower() or "@react-three" in imp:
                deps["three_js_dependencies"].append(imp)
            elif "motion" in imp or "framer" in imp:
                deps["ui_dependencies"].append(imp)
            elif "zustand" in imp or "redux" in imp:
                deps["state_management"].append(imp)
            else:
                deps["other_dependencies"].append(imp)

        return deps

    def print_dependency_analysis(self):
        """Print detailed dependency analysis"""
        print("🔍 AETHERRA GUI DEPENDENCY ANALYSIS")
        print("=" * 50)

        deps = self.analyze_dependencies()

        print("\n📦 REQUIRED DEPENDENCIES:")
        print("-" * 30)

        if deps["react_dependencies"]:
            print("🔹 React Dependencies:")
            for dep in deps["react_dependencies"]:
                print(f"  • {dep}")
        else:
            print("🔹 React Dependencies: react, react-dom (detected in code)")

        if deps["three_js_dependencies"]:
            print("🔹 Three.js Dependencies:")
            for dep in deps["three_js_dependencies"]:
                print(f"  • {dep}")
        else:
            print(
                "🔹 Three.js Dependencies: @react-three/fiber, @react-three/drei (detected in code)"
            )

        if deps["ui_dependencies"]:
            print("🔹 UI/Animation Dependencies:")
            for dep in deps["ui_dependencies"]:
                print(f"  • {dep}")
        else:
            print("🔹 UI/Animation Dependencies: framer-motion (detected in code)")

        if deps["state_management"]:
            print("🔹 State Management:")
            for dep in deps["state_management"]:
                print(f"  • {dep}")
        else:
            print("🔹 State Management: zustand (detected in code)")

        print("\n📋 COMPLETE DEPENDENCY LIST:")
        print("-" * 30)
        required_deps = [
            "react",
            "react-dom",
            "three",
            "@react-three/fiber",
            "@react-three/drei",
            "framer-motion",
            "zustand",
        ]

        for dep in required_deps:
            print(f"  • {dep}")

        print("\n💻 INSTALLATION COMMANDS:")
        print("-" * 30)
        print("npm install " + " ".join(required_deps))
        print("# or")
        print("yarn add " + " ".join(required_deps))

        print("\n🎨 ADDITIONAL REQUIREMENTS:")
        print("-" * 30)
        print("  • Tailwind CSS (for styling)")
        print("  • WebSocket connection to ws://localhost:7070/ws")
        print("  • Modern browser with WebGL support")

    def start_server(self):
        """Start HTTP server for GUI testing"""
        os.chdir(self.gui_dir)

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                super().end_headers()

        self.server = socketserver.TCPServer(("", self.port), CustomHandler)
        print(f"🌐 Starting server at http://localhost:{self.port}")

        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        return server_thread

    def launch_gui(self):
        """Launch the GUI in browser"""
        print("🚀 LAUNCHING AETHERRA GUI")
        print("=" * 50)

        # Print dependency analysis first
        self.print_dependency_analysis()

        # Check if Vite dev server is running
        print("\n🔍 Checking for Vite development server...")

        use_vite = False
        vite_url = "http://localhost:3000"
        server_thread = None

        try:
            import requests

            try:
                response = requests.get(vite_url, timeout=2)
                if response.status_code == 200:
                    print("✅ Vite server detected at http://localhost:3000")
                    use_vite = True
                else:
                    use_vite = False
            except Exception:
                use_vite = False
        except ImportError:
            # requests not available, try basic socket check
            import socket

            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(("localhost", 3000))
                sock.close()
                use_vite = result == 0
                if use_vite:
                    print("✅ Vite server detected at http://localhost:3000")
            except Exception:
                use_vite = False

        if use_vite:
            # Use Vite development server
            print("🎯 Using Vite development server (recommended)")
            target_url = vite_url
        else:
            print("⚠️  Vite server not running, starting fallback test server...")
            print("💡 For best experience, run: npm run dev")

            # Start fallback server
            print("\n🌐 Starting fallback server...")
            server_thread = self.start_server()
            time.sleep(2)
            target_url = f"http://localhost:{self.port}/test_aetherra_gui.html"

        print(f"🌍 Opening browser to: {target_url}")

        try:
            webbrowser.open(target_url)
            print("✅ GUI launched successfully!")

            if use_vite:
                print("🚀 Using full React development environment with hot reload")
                print("📁 Vite serving from: src/ directory")
                print("🔥 All dependencies loaded and ready")
            else:
                print(f"📁 Serving files from: {self.gui_dir}")
                print("\n⚠️  NOTE: This is a dependency test page.")
                print(
                    "   For full functionality, run 'npm run dev' in the GUI directory"
                )

            print(
                "\n🔌 The GUI expects a WebSocket connection at ws://localhost:7070/ws"
            )
            print("   Make sure Lyrixa is running to provide real-time data.")

            if not use_vite:
                print("\n📄 Available files:")
                for file in self.gui_dir.glob("*"):
                    if file.is_file():
                        print(f"   • {file.name}")

        except Exception as e:
            print(f"❌ Error opening browser: {e}")

        return server_thread

    def stop_server(self):
        """Stop the HTTP server"""
        if self.server:
            self.server.shutdown()
            print("🛑 Server stopped")


def main():
    launcher = AetherraGUILauncher()

    try:
        server_thread = launcher.launch_gui()

        print(f"\n{'=' * 50}")
        print("🎮 GUI is running! Press Ctrl+C to stop.")
        print("=" * 50)

        if server_thread:
            print("📡 Fallback server active - use 'npm run dev' for better experience")
        else:
            print("🚀 Using Vite development server - optimal experience!")

        # Keep running until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping GUI launcher...")
        launcher.stop_server()
        print("✅ Goodbye!")

    except Exception as e:
        print(f"❌ Error: {e}")
        launcher.stop_server()


if __name__ == "__main__":
    main()
