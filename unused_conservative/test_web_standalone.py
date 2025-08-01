#!/usr/bin/env python3
"""
Simple web server to test the Lyrixa web interface standalone
"""

import http.server
import os
import socketserver
import webbrowser
from pathlib import Path


def main():
    # Change to the web directory
    web_dir = Path(__file__).parent / "Aetherra" / "lyrixa" / "gui" / "web"
    os.chdir(web_dir)

    PORT = 8088

    class Handler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers for local development
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "*")
            super().end_headers()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌐 Serving Lyrixa web interface at http://localhost:{PORT}")
        print("📱 This shows how the interface looks before Qt integration")
        print("🔧 Open browser and check console for Qt bridge messages")

        # Open browser
        webbrowser.open(f"http://localhost:{PORT}")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")


if __name__ == "__main__":
    main()
