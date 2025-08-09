#!/usr/bin/env python3
"""
🧠 Aetherra Cognitive Task Manager - Simplified Version
=======================================================

A reliable real-time dashboard for monitoring Aetherra AI OS cognitive activity.
This version focuses on working correctly with the shared registry.
"""

import asyncio
import json
import logging
import sys
import threading
import time
import webbrowser
from datetime import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Web framework
try:
    from flask import Flask, jsonify, render_template
    from flask_socketio import SocketIO, emit

    WEB_AVAILABLE = True
except ImportError:
    print("❌ Flask/SocketIO not available")
    WEB_AVAILABLE = False

# Service registry
try:
    from aetherra_service_registry import get_service_registry

    REGISTRY_AVAILABLE = True
    print("✅ Service registry available")
except ImportError:
    print("❌ Service registry not available")
    REGISTRY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleCognitiveTaskManager:
    """Simplified cognitive task manager that definitely works."""

    def __init__(self, port: int = 8889):
        self.port = port
        self.metrics = {
            "services": {},
            "service_count": 0,
            "shared_registry": {"enabled": False},
            "status": "initializing",
        }
        self.running = False

    def create_app(self):
        """Create Flask app."""
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "aetherra-simple"
        socketio = SocketIO(app, cors_allowed_origins="*")

        @app.route("/")
        def dashboard():
            return """
<!DOCTYPE html>
<html>
<head>
    <title>🧠 Aetherra Cognitive Task Manager</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <style>
        body {
            font-family: monospace;
            background: #0f0f23;
            color: #00ff88;
            margin: 20px;
        }
        .panel {
            border: 2px solid #00ff88;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            background: rgba(0, 255, 136, 0.1);
        }
        .metric { font-size: 2em; text-align: center; margin: 10px; }
        .service {
            background: rgba(0, 255, 136, 0.05);
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
        }
        .live { color: #ff0088; animation: blink 1s infinite; }
        @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
    </style>
</head>
<body>
    <h1>🧠 AETHERRA COGNITIVE TASK MANAGER <span class="live">● LIVE</span></h1>

    <div class="panel">
        <h2>🔧 Active Services</h2>
        <div class="metric" id="service-count">Loading...</div>
        <div id="services-list">Connecting to shared registry...</div>
    </div>

    <div class="panel">
        <h2>🌐 Shared Registry Status</h2>
        <div id="registry-status">Checking...</div>
    </div>

    <div class="panel">
        <h2>📡 System Log</h2>
        <div id="log">Starting cognitive monitoring...</div>
    </div>

    <script>
        const socket = io();

        socket.on('metrics', function(data) {
            document.getElementById('service-count').textContent = data.service_count || 0;

            const servicesList = document.getElementById('services-list');
            if (data.services && Object.keys(data.services).length > 0) {
                servicesList.innerHTML = '';
                Object.values(data.services).forEach(service => {
                    const div = document.createElement('div');
                    div.className = 'service';
                    div.innerHTML = `<strong>${service.name}</strong> - Status: ${service.status}`;
                    servicesList.appendChild(div);
                });
            } else {
                servicesList.innerHTML = 'No services detected';
            }

            const registryStatus = document.getElementById('registry-status');
            if (data.shared_registry && data.shared_registry.enabled) {
                registryStatus.innerHTML = `
                    ✅ Enabled<br>
                    Services: ${data.shared_registry.total_services || 0}<br>
                    Port: ${data.shared_registry.communication_port || 'N/A'}
                `;
            } else {
                registryStatus.innerHTML = '❌ Not connected';
            }

            addLog(`Updated: ${data.service_count} services found`);
        });

        function addLog(message) {
            const log = document.getElementById('log');
            const time = new Date().toLocaleTimeString();
            log.innerHTML = `[${time}] ${message}<br>` + log.innerHTML;

            // Keep only last 10 lines
            const lines = log.innerHTML.split('<br>');
            if (lines.length > 10) {
                log.innerHTML = lines.slice(0, 10).join('<br>');
            }
        }

        socket.on('connect', function() {
            addLog('Connected to dashboard');
        });

        // Request updates every 3 seconds
        setInterval(() => {
            socket.emit('request_update');
        }, 3000);
    </script>
</body>
</html>
            """

        @socketio.on("request_update")
        def handle_update_request():
            emit("metrics", self.metrics)

        return app, socketio

    async def update_metrics(self):
        """Update metrics from shared registry."""
        while self.running:
            try:
                if REGISTRY_AVAILABLE:
                    # Get registry with shared support
                    registry = await get_service_registry(enable_shared=True)
                    services = registry.list_services()

                    # Convert services to serializable format
                    service_data = {}
                    for name, info in services.items():
                        service_data[name] = {
                            "name": name,
                            "status": str(info.status).replace("ServiceStatus.", ""),
                            "metadata": getattr(info, "metadata", {}),
                        }

                    self.metrics["services"] = service_data
                    self.metrics["service_count"] = len(service_data)

                    # Get shared registry status
                    if (
                        hasattr(registry, "_shared_enabled")
                        and registry._shared_enabled
                    ):
                        if (
                            hasattr(registry, "_shared_registry")
                            and registry._shared_registry
                        ):
                            shared_status = (
                                registry._shared_registry.get_registry_status()
                            )
                            self.metrics["shared_registry"] = {
                                "enabled": True,
                                "total_services": shared_status.get(
                                    "total_services", 0
                                ),
                                "communication_port": shared_status.get(
                                    "communication_port"
                                ),
                            }
                        else:
                            self.metrics["shared_registry"] = {"enabled": False}
                    else:
                        self.metrics["shared_registry"] = {"enabled": False}

                    self.metrics["status"] = "running"
                    logger.info(f"📊 Metrics updated: {len(service_data)} services")

                else:
                    self.metrics["status"] = "registry_unavailable"
                    logger.warning("⚠️ Registry not available")

            except Exception as e:
                logger.error(f"❌ Metrics update error: {e}")
                self.metrics["status"] = f"error: {e}"

            await asyncio.sleep(3)

    def run(self):
        """Run the dashboard."""
        if not WEB_AVAILABLE:
            print("❌ Flask not available")
            return

        app, socketio = self.create_app()
        self.running = True

        # Start metrics updater in background
        def start_updater():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.update_metrics())

        threading.Thread(target=start_updater, daemon=True).start()

        # Open browser
        def open_browser():
            time.sleep(1)
            webbrowser.open(f"http://localhost:{self.port}")

        threading.Thread(target=open_browser, daemon=True).start()

        print(
            f"🧠 Simple Cognitive Task Manager starting on http://localhost:{self.port}"
        )
        print("🌐 Opening browser...")

        try:
            socketio.run(app, host="localhost", port=self.port, debug=False)
        except KeyboardInterrupt:
            print("🛑 Shutting down...")
        finally:
            self.running = False


if __name__ == "__main__":
    dashboard = SimpleCognitiveTaskManager()
    dashboard.run()
