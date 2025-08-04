#!/usr/bin/env python3
"""
🏪 Aetherra Hub Server
======================

Built-in Python-based plugin marketplace server for Aetherra OS.
Provides plugin registration, discovery, and basic marketplace functionality.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask not available - using mock hub server")

logger = logging.getLogger(__name__)


class AetherraHubServer:
    """🏪 Built-in Aetherra Hub Server"""

    def __init__(self, port: int = 3001):
        self.port = port
        self.plugins = {}
        self.stats = {
            'total_plugins': 0,
            'active_registrations': 0,
            'startup_time': datetime.now(),
            'requests_served': 0
        }
        self.server_running = False

        if FLASK_AVAILABLE:
            self.app = Flask(__name__)
            CORS(self.app)  # Enable CORS for web interface
            self._setup_routes()
        else:
            self.app = None

    def _setup_routes(self):
        """Setup Flask routes for the Hub API"""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            self.stats['requests_served'] += 1
            return jsonify({
                'status': 'healthy',
                'uptime_seconds': (datetime.now() - self.stats['startup_time']).total_seconds(),
                'plugins_registered': len(self.plugins),
                'requests_served': self.stats['requests_served']
            })

        @self.app.route('/api/plugins', methods=['GET'])
        def list_plugins():
            """List all registered plugins"""
            self.stats['requests_served'] += 1
            return jsonify({
                'plugins': list(self.plugins.values()),
                'total': len(self.plugins),
                'timestamp': datetime.now().isoformat()
            })

        @self.app.route('/api/plugins/register', methods=['POST'])
        def register_plugin():
            """Register a new plugin"""
            try:
                plugin_data = request.get_json()
                if not plugin_data or 'name' not in plugin_data:
                    return jsonify({'error': 'Invalid plugin data'}), 400

                plugin_id = plugin_data['name']
                plugin_data['registered_at'] = datetime.now().isoformat()
                plugin_data['status'] = 'registered'

                self.plugins[plugin_id] = plugin_data
                self.stats['requests_served'] += 1
                self.stats['active_registrations'] += 1

                logger.info(f"[OK] Plugin registered: {plugin_id}")

                return jsonify({
                    'status': 'success',
                    'message': f'Plugin {plugin_id} registered successfully',
                    'plugin_id': plugin_id
                })

            except Exception as e:
                logger.error(f"❌ Plugin registration failed: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/plugins/<plugin_id>', methods=['GET'])
        def get_plugin(plugin_id):
            """Get specific plugin details"""
            self.stats['requests_served'] += 1
            if plugin_id in self.plugins:
                return jsonify(self.plugins[plugin_id])
            else:
                return jsonify({'error': 'Plugin not found'}), 404

        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            """Get Hub statistics"""
            self.stats['requests_served'] += 1
            return jsonify(self.stats)

        @self.app.route('/', methods=['GET'])
        def index():
            """Hub web interface"""
            return """
            <html>
            <head><title>Aetherra Hub - Plugin Marketplace</title></head>
            <body style="font-family: monospace; background: #0a0a0a; color: #00ffaa; padding: 20px;">
                <h1>🏪 Aetherra Hub - Plugin Marketplace</h1>
                <p>Status: <span style="color: #66ffcc;">ONLINE</span></p>
                <p>Registered Plugins: <span id="plugin-count">Loading...</span></p>
                <p>Uptime: <span id="uptime">Loading...</span></p>
                <hr>
                <h2>API Endpoints:</h2>
                <ul>
                    <li><a href="/health" style="color: #00ffaa;">GET /health</a> - Health check</li>
                    <li><a href="/api/plugins" style="color: #00ffaa;">GET /api/plugins</a> - List plugins</li>
                    <li><a href="/api/stats" style="color: #00ffaa;">GET /api/stats</a> - Hub statistics</li>
                    <li>POST /api/plugins/register - Register plugin</li>
                </ul>
                <script>
                    fetch('/api/stats').then(r=>r.json()).then(d=>{
                        document.getElementById('plugin-count').textContent = Object.keys(d).length || 0;
                        document.getElementById('uptime').textContent = Math.round((Date.now() - new Date(d.startup_time)) / 1000) + 's';
                    });
                </script>
            </body>
            </html>
            """

    def start_server(self):
        """Start the Hub server"""
        if not FLASK_AVAILABLE:
            logger.warning("⚠️ Flask not available - starting mock hub server")
            self.server_running = True
            return True

        try:
            logger.info(f"[HUB] Starting Aetherra Hub server on port {self.port}")

            # Start Flask server in a separate thread
            import threading

            def run_flask():
                self.app.run(
                    host='localhost',
                    port=self.port,
                    debug=False,
                    use_reloader=False,
                    threaded=True
                )

            self.server_thread = threading.Thread(target=run_flask, daemon=True)
            self.server_thread.start()

            # Wait a moment for server to start
            time.sleep(1)

            self.server_running = True
            logger.info(f"[OK] Aetherra Hub server online at http://localhost:{self.port}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to start Hub server: {e}")
            self.server_running = False
            return False

    def register_plugin(self, plugin_data: Dict) -> bool:
        """Register a plugin directly (for internal use)"""
        try:
            plugin_id = plugin_data.get('name', f"plugin_{len(self.plugins)}")
            plugin_data['registered_at'] = datetime.now().isoformat()
            plugin_data['status'] = 'registered'
            plugin_data['source'] = 'internal'

            self.plugins[plugin_id] = plugin_data
            self.stats['active_registrations'] += 1

            logger.info(f"[OK] Plugin registered internally: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Internal plugin registration failed: {e}")
            return False

    def is_running(self) -> bool:
        """Check if the Hub server is running"""
        return self.server_running

    def get_plugin_count(self) -> int:
        """Get the number of registered plugins"""
        return len(self.plugins)

    def get_stats(self) -> Dict:
        """Get Hub statistics"""
        return {
            **self.stats,
            'total_plugins': len(self.plugins),
            'uptime_seconds': (datetime.now() - self.stats['startup_time']).total_seconds()
        }

    def stop_server(self):
        """Stop the Hub server"""
        self.server_running = False
        logger.info("🛑 Aetherra Hub server stopped")


# Global Hub instance
hub_server = None


def start_hub_server(port: int = 3001) -> AetherraHubServer:
    """Start the global Hub server"""
    global hub_server
    if hub_server is None:
        hub_server = AetherraHubServer(port)
        hub_server.start_server()
    return hub_server


def get_hub_server() -> Optional[AetherraHubServer]:
    """Get the global Hub server instance"""
    return hub_server


if __name__ == "__main__":
    # Test the Hub server
    print("🧪 Testing Aetherra Hub Server")
    server = AetherraHubServer(3001)

    if server.start_server():
        print("[OK] Hub server started successfully")

        # Register a test plugin
        test_plugin = {
            'name': 'test_plugin',
            'version': '1.0.0',
            'description': 'Test plugin for Hub server',
            'type': 'utility'
        }

        server.register_plugin(test_plugin)
        print(f"📊 Hub stats: {server.get_stats()}")

        # Keep running for testing
        print("🔄 Hub server running... (Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Stopping Hub server...")
            server.stop_server()
    else:
        print("❌ Failed to start Hub server")
