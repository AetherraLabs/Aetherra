#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Aetherra Cognitive Task Manager - Live OS Activity Dashboard
=============================================================

A comprehensive real-time dashboard for monitoring Aetherra AI OS cognitive activity.
Think "Task Manager for Cognition" - shows the AI OS breathing and adapting.

Features:
- Live service registry monitoring with shared services
- Real-time goal processing and execution
- Active workflow visualization
- Plugin activity monitoring
- Memory events and cognitive state changes
- Agent message flow
- Consciousness level tracking
- Performance metrics and health indicators

Copyright (C) 2025 AetherraLabs
Licensed under GNU General Public License v3.0
"""

import asyncio
import json
import logging
import sys
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Web framework
try:
    from flask import Flask, jsonify, render_template, request
    from flask_socketio import SocketIO, emit

    WEB_AVAILABLE = True
except ImportError:
    print(
        "❌ Flask/SocketIO not available - install with: pip install flask flask-socketio"
    )
    WEB_AVAILABLE = False

# Aetherra components
try:
    from aetherra_service_registry import get_service_registry
    from aetherra_shared_service_registry import get_shared_service_registry

    REGISTRY_AVAILABLE = True
    registry_funcs = {
        "get_service_registry": get_service_registry,
        "get_shared_service_registry": get_shared_service_registry,
    }
except ImportError:
    print("⚠️ Service registry not available")
    REGISTRY_AVAILABLE = False
    registry_funcs = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CognitiveTaskManager:
    """
    🧠 Cognitive Task Manager

    Real-time dashboard for monitoring AI OS cognitive activity.
    Provides live insights into the AI's thinking and processing.
    """

    def __init__(self, port: int = 8888):
        self.port = port
        self.app = None
        self.socketio = None
        self.running = False

        # Monitoring data
        self.metrics = {
            "services": {},
            "active_goals": [],
            "workflows": [],
            "plugin_activity": [],
            "memory_events": [],
            "agent_messages": [],
            "consciousness_levels": {},
            "performance": {},
            "system_health": {},
        }

        # Monitoring tasks
        self.monitor_tasks = []

    def initialize_app(self):
        """Initialize Flask app and routes."""
        if not WEB_AVAILABLE:
            raise RuntimeError("Flask/SocketIO not available")

        self.app = Flask(
            __name__, template_folder=str(Path(__file__).parent / "templates")
        )
        self.app.config["SECRET_KEY"] = "aetherra-cognitive-dashboard"
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Routes
        self.app.route("/")(self.dashboard)
        self.app.route("/api/metrics")(self.get_metrics)
        self.app.route("/api/services")(self.get_services)
        self.app.route("/api/consciousness")(self.get_consciousness)

        # SocketIO events
        self.socketio.on("connect")(self.on_connect)
        self.socketio.on("disconnect")(self.on_disconnect)

        logger.info("🧠 Cognitive Task Manager app initialized")

    def dashboard(self):
        """Main dashboard page."""
        return self.render_dashboard_html()

    def get_metrics(self):
        """API endpoint for metrics."""
        return jsonify(self.metrics)

    def get_services(self):
        """API endpoint for service status."""
        return jsonify(self.metrics.get("services", {}))

    def get_consciousness(self):
        """API endpoint for consciousness levels."""
        return jsonify(self.metrics.get("consciousness_levels", {}))

    def on_connect(self):
        """Handle client connection."""
        logger.info("🔗 Client connected to cognitive dashboard")
        emit("status", {"message": "Connected to Aetherra Cognitive Task Manager"})

    def on_disconnect(self):
        """Handle client disconnection."""
        logger.info("❌ Client disconnected from cognitive dashboard")

    async def start_monitoring(self):
        """Start all monitoring tasks."""
        if not REGISTRY_AVAILABLE:
            logger.warning("⚠️ Service registry not available - limited monitoring")
            return

        # Start monitoring tasks
        monitor_tasks = [
            asyncio.create_task(self.monitor_services()),
            asyncio.create_task(self.monitor_consciousness()),
            asyncio.create_task(self.monitor_performance()),
            asyncio.create_task(self.monitor_memory_events()),
            asyncio.create_task(self.broadcast_updates()),
        ]

        self.monitor_tasks.extend(monitor_tasks)
        logger.info("🔄 All monitoring tasks started")

    async def monitor_services(self):
        """Monitor service registry for active services."""
        while self.running:
            try:
                if (
                    not REGISTRY_AVAILABLE
                    or "get_service_registry" not in registry_funcs
                ):
                    logger.warning(
                        "⚠️ Registry not available, skipping service monitoring"
                    )
                    await asyncio.sleep(5)
                    continue

                # Get both local and shared registry data
                get_registry_func = registry_funcs["get_service_registry"]
                registry = await get_registry_func(enable_shared=True)
                services = registry.list_services()

                service_data = {}
                for name, info in services.items():
                    service_data[name] = {
                        "name": name,
                        "status": info.status.value
                        if hasattr(info.status, "value")
                        else str(info.status),
                        "registered_at": info.registered_at.isoformat()
                        if hasattr(info.registered_at, "isoformat")
                        else str(info.registered_at),
                        "last_heartbeat": info.last_heartbeat.isoformat()
                        if hasattr(info.last_heartbeat, "isoformat")
                        else str(info.last_heartbeat),
                        "metadata": info.metadata,
                        "dependencies": info.dependencies,
                    }

                self.metrics["services"] = service_data
                self.metrics["service_count"] = len(service_data)

                # Check for shared registry status
                if registry._shared_enabled and registry._shared_registry:
                    shared_status = registry._shared_registry.get_registry_status()
                    self.metrics["shared_registry"] = {
                        "enabled": True,
                        "total_services": shared_status.get("total_services", 0),
                        "healthy_services": shared_status.get("healthy_services", 0),
                        "communication_port": shared_status.get("communication_port"),
                        "registry_file": shared_status.get("registry_file"),
                    }
                    logger.info(
                        f"📊 Dashboard: Found {len(service_data)} services, shared registry has {shared_status.get('total_services', 0)}"
                    )
                else:
                    self.metrics["shared_registry"] = {"enabled": False}
                    logger.warning("⚠️ Dashboard: Shared registry not enabled")

            except Exception as e:
                logger.error(f"❌ Service monitoring error: {e}")
                import traceback

                traceback.print_exc()

            await asyncio.sleep(2)  # Update every 2 seconds

    async def monitor_consciousness(self):
        """Monitor consciousness levels across all systems."""
        while self.running:
            try:
                if (
                    not REGISTRY_AVAILABLE
                    or "get_service_registry" not in registry_funcs
                ):
                    await asyncio.sleep(5)
                    continue

                get_registry_func = registry_funcs["get_service_registry"]
                registry = await get_registry_func(enable_shared=True)

                consciousness_data = {}

                # Check quantum consciousness
                quantum_service = registry.get_service("quantum_consciousness")
                if quantum_service:
                    consciousness_data["quantum"] = {
                        "active": True,
                        "level": getattr(
                            quantum_service, "consciousness_level", "unknown"
                        ),
                        "phase": "quantum",
                        "version": "7.0",
                    }

                # Check cosmic consciousness
                cosmic_service = registry.get_service("cosmic_consciousness")
                if cosmic_service:
                    consciousness_data["cosmic"] = {
                        "active": True,
                        "level": getattr(
                            cosmic_service, "consciousness_level", "unknown"
                        ),
                        "phase": "cosmic",
                        "version": "8.2",
                    }

                # Check beyond transcendence
                transcendence_service = registry.get_service("beyond_transcendence")
                if transcendence_service:
                    consciousness_data["transcendence"] = {
                        "active": True,
                        "level": getattr(
                            transcendence_service, "consciousness_level", "unknown"
                        ),
                        "phase": "transcendence",
                        "version": "8.3",
                    }

                self.metrics["consciousness_levels"] = consciousness_data

            except Exception as e:
                logger.error(f"Consciousness monitoring error: {e}")

            await asyncio.sleep(5)  # Update every 5 seconds

    async def monitor_performance(self):
        """Monitor system performance metrics."""
        while self.running:
            try:
                # Collect performance data
                current_time = datetime.now()

                self.metrics["performance"] = {
                    "timestamp": current_time.isoformat(),
                    "uptime": time.time(),
                    "memory_usage": "unknown",  # TODO: Add actual memory monitoring
                    "cpu_usage": "unknown",  # TODO: Add actual CPU monitoring
                    "response_time": "unknown",  # TODO: Add response time tracking
                }

                # System health indicators
                self.metrics["system_health"] = {
                    "overall": "healthy"
                    if len(self.metrics.get("services", {})) > 0
                    else "degraded",
                    "services_operational": len(
                        [
                            s
                            for s in self.metrics.get("services", {}).values()
                            if s.get("status") in ["healthy", "starting"]
                        ]
                    ),
                    "last_update": current_time.isoformat(),
                }

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")

            await asyncio.sleep(10)  # Update every 10 seconds

    async def monitor_memory_events(self):
        """Monitor memory system events and changes."""
        while self.running:
            try:
                if (
                    not REGISTRY_AVAILABLE
                    or "get_service_registry" not in registry_funcs
                ):
                    await asyncio.sleep(3)
                    continue

                get_registry_func = registry_funcs["get_service_registry"]
                registry = await get_registry_func(enable_shared=True)

                # Check persistent memory system
                memory_service = registry.get_service("persistent_memory_system")
                if memory_service:
                    # TODO: Add actual memory event monitoring
                    # For now, simulate some memory activity
                    memory_events = [
                        {
                            "timestamp": datetime.now().isoformat(),
                            "type": "memory_access",
                            "details": "Accessing episodic memory",
                            "status": "active",
                        }
                    ]
                    self.metrics["memory_events"] = memory_events[
                        -10:
                    ]  # Keep last 10 events

            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")

            await asyncio.sleep(3)  # Update every 3 seconds

    async def broadcast_updates(self):
        """Broadcast real-time updates to connected clients."""
        while self.running:
            try:
                if self.socketio:
                    self.socketio.emit("metrics_update", self.metrics)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

            await asyncio.sleep(1)  # Broadcast every second

    def render_dashboard_html(self):
        """Render the dashboard HTML."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Aetherra Cognitive Task Manager</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', monospace;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: #00ff88;
            overflow-x: hidden;
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            grid-gap: 15px;
            padding: 15px;
            min-height: 100vh;
        }

        .panel {
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            border-radius: 8px;
            padding: 12px;
            backdrop-filter: blur(10px);
            animation: glow 2s ease-in-out infinite alternate;
            height: fit-content;
            max-height: 400px;
        }

        @keyframes glow {
            from { box-shadow: 0 0 20px rgba(0, 255, 136, 0.3); }
            to { box-shadow: 0 0 30px rgba(0, 255, 136, 0.6); }
        }

        .panel h2 {
            color: #00ff88;
            margin-bottom: 10px;
            text-align: center;
            text-shadow: 0 0 10px #00ff88;
            font-size: 1.1em;
        }

        .service-item {
            background: rgba(0, 255, 136, 0.05);
            border: 1px solid #00ff88;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
        }

        .service-name {
            font-weight: bold;
            color: #00ff88;
        }

        .service-status {
            font-size: 0.9em;
            opacity: 0.8;
        }

        .status-healthy { color: #00ff88; }
        .status-starting { color: #ffaa00; }
        .status-degraded { color: #ff6600; }
        .status-failed { color: #ff0000; }

        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            text-align: center;
            margin: 8px 0;
            text-shadow: 0 0 15px currentColor;
        }

        .header {
            grid-column: 1 / -1;
            text-align: center;
            padding: 15px;
            background: rgba(0, 255, 136, 0.1);
            border: 2px solid #00ff88;
            border-radius: 10px;
            margin-bottom: 15px;
        }

        .consciousness-indicator {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin: 0 5px;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }

        .active { background: #00ff88; }
        .inactive { background: #666; }

        .live-indicator {
            color: #ff0088;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }

        .scrollable {
            max-height: 150px;
            overflow-y: auto;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(0, 255, 136, 0.1);
        }

        ::-webkit-scrollbar-thumb {
            background: #00ff88;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 AETHERRA COGNITIVE TASK MANAGER <span class="live-indicator">● LIVE</span></h1>
        <p>Real-time AI OS Activity Monitoring - The AI is thinking...</p>
    </div>

    <div class="dashboard">
        <!-- Services Panel -->
        <div class="panel">
            <h2>🔧 Active Services</h2>
            <div class="metric-value" id="service-count">0</div>
            <div class="scrollable" id="services-list">
                <div class="service-item">
                    <div class="service-name">Loading services...</div>
                </div>
            </div>
        </div>

        <!-- Consciousness Panel -->
        <div class="panel">
            <h2>🧠 Consciousness Levels</h2>
            <div id="consciousness-indicators">
                <div>Quantum: <span class="consciousness-indicator inactive" id="quantum-indicator"></span></div>
                <div>Cosmic: <span class="consciousness-indicator inactive" id="cosmic-indicator"></span></div>
                <div>Transcendence: <span class="consciousness-indicator inactive" id="transcendence-indicator"></span></div>
            </div>
            <div class="metric-value" id="consciousness-level">Initializing...</div>
        </div>

        <!-- Performance Panel -->
        <div class="panel">
            <h2>📊 System Performance</h2>
            <div id="performance-metrics">
                <div>Uptime: <span id="uptime">Starting...</span></div>
                <div>Health: <span id="system-health">Checking...</span></div>
                <div>Services: <span id="operational-services">0</span> operational</div>
            </div>
        </div>

        <!-- Shared Registry Panel -->
        <div class="panel">
            <h2>🌐 Shared Registry</h2>
            <div id="shared-registry-status">
                <div>Status: <span id="registry-status">Unknown</span></div>
                <div>Port: <span id="registry-port">-</span></div>
                <div>Cross-Process: <span id="cross-process">Checking...</span></div>
            </div>
        </div>

        <!-- Memory Events Panel -->
        <div class="panel">
            <h2>🧠 Memory Activity</h2>
            <div class="scrollable" id="memory-events">
                <div>Monitoring memory events...</div>
            </div>
        </div>

        <!-- Live Activity Feed -->
        <div class="panel">
            <h2>📡 Live Activity Feed</h2>
            <div class="scrollable" id="activity-feed">
                <div>[INIT] Cognitive Task Manager started</div>
            </div>
        </div>
    </div>

    <script>
        // Connect to SocketIO
        const socket = io();

        // Connection events
        socket.on('connect', function() {
            addActivity('[CONNECT] Connected to Aetherra OS');
        });

        socket.on('status', function(data) {
            addActivity('[STATUS] ' + data.message);
        });

        // Real-time metrics updates
        socket.on('metrics_update', function(metrics) {
            updateDashboard(metrics);
        });

        function updateDashboard(metrics) {
            // Update service count and list
            const serviceCount = metrics.service_count || 0;
            document.getElementById('service-count').textContent = serviceCount;

            const servicesList = document.getElementById('services-list');
            if (metrics.services) {
                servicesList.innerHTML = '';
                Object.values(metrics.services).forEach(service => {
                    const serviceDiv = document.createElement('div');
                    serviceDiv.className = 'service-item';
                    serviceDiv.innerHTML = `
                        <div class="service-name">${service.name}</div>
                        <div class="service-status status-${service.status}">${service.status}</div>
                    `;
                    servicesList.appendChild(serviceDiv);
                });
            }

            // Update consciousness indicators
            if (metrics.consciousness_levels) {
                updateConsciousnessIndicator('quantum', metrics.consciousness_levels.quantum);
                updateConsciousnessIndicator('cosmic', metrics.consciousness_levels.cosmic);
                updateConsciousnessIndicator('transcendence', metrics.consciousness_levels.transcendence);

                const activeCount = Object.keys(metrics.consciousness_levels).length;
                document.getElementById('consciousness-level').textContent = `${activeCount} Active`;
            }

            // Update performance metrics
            if (metrics.performance) {
                const uptime = Math.floor(Date.now() / 1000 - metrics.performance.uptime);
                document.getElementById('uptime').textContent = formatUptime(uptime);
            }

            if (metrics.system_health) {
                document.getElementById('system-health').textContent = metrics.system_health.overall;
                document.getElementById('operational-services').textContent = metrics.system_health.services_operational || 0;
            }

            // Update shared registry status
            if (metrics.shared_registry) {
                document.getElementById('registry-status').textContent = metrics.shared_registry.enabled ? 'Active' : 'Disabled';
                document.getElementById('registry-port').textContent = metrics.shared_registry.communication_port || '-';
                document.getElementById('cross-process').textContent = metrics.shared_registry.enabled ? 'Enabled' : 'Disabled';
            }

            // Update memory events
            if (metrics.memory_events) {
                const memoryDiv = document.getElementById('memory-events');
                memoryDiv.innerHTML = '';
                metrics.memory_events.forEach(event => {
                    const eventDiv = document.createElement('div');
                    eventDiv.innerHTML = `[${new Date(event.timestamp).toLocaleTimeString()}] ${event.details}`;
                    memoryDiv.appendChild(eventDiv);
                });
            }
        }

        function updateConsciousnessIndicator(type, data) {
            const indicator = document.getElementById(`${type}-indicator`);
            if (data && data.active) {
                indicator.className = 'consciousness-indicator active';
            } else {
                indicator.className = 'consciousness-indicator inactive';
            }
        }

        function addActivity(message) {
            const feed = document.getElementById('activity-feed');
            const timestamp = new Date().toLocaleTimeString();
            const activityDiv = document.createElement('div');
            activityDiv.innerHTML = `[${timestamp}] ${message}`;
            feed.insertBefore(activityDiv, feed.firstChild);

            // Keep only last 20 messages
            while (feed.children.length > 20) {
                feed.removeChild(feed.lastChild);
            }
        }

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;
            return `${hours}h ${minutes}m ${secs}s`;
        }

        // Periodic updates
        setInterval(() => {
            fetch('/api/metrics')
                .then(response => response.json())
                .then(metrics => updateDashboard(metrics))
                .catch(error => console.error('Error fetching metrics:', error));
        }, 5000);

        // Initial load
        fetch('/api/metrics')
            .then(response => response.json())
            .then(metrics => updateDashboard(metrics))
            .catch(error => {
                console.error('Error fetching initial metrics:', error);
                addActivity('[ERROR] Failed to load initial metrics');
            });

        // Add periodic activity to show the system is alive
        setInterval(() => {
            addActivity('[HEARTBEAT] Cognitive systems monitoring...');
        }, 30000);
    </script>
</body>
</html>
        """

    async def start(self):
        """Start the cognitive task manager."""
        if not WEB_AVAILABLE:
            print("❌ Flask/SocketIO not available")
            print("Install with: pip install flask flask-socketio")
            return

        try:
            self.initialize_app()
            self.running = True

            # Start monitoring in background
            await self.start_monitoring()

            # Start Flask app
            logger.info(
                f"🧠 Starting Cognitive Task Manager on http://localhost:{self.port}"
            )
            logger.info("🌐 Opening dashboard in browser...")

            # Open browser
            def open_browser():
                time.sleep(1)  # Wait for server to start
                webbrowser.open(f"http://localhost:{self.port}")

            threading.Thread(target=open_browser, daemon=True).start()

            # Run the Flask app
            self.socketio.run(self.app, host="localhost", port=self.port, debug=False)

        except KeyboardInterrupt:
            logger.info("🛑 Shutting down Cognitive Task Manager...")
        except Exception as e:
            logger.error(f"❌ Error starting dashboard: {e}")
        finally:
            self.running = False
            for task in self.monitor_tasks:
                task.cancel()


async def main():
    """Main entry point."""
    print("🧠 AETHERRA COGNITIVE TASK MANAGER")
    print("=" * 50)
    print("Real-time AI OS Activity Monitoring")
    print("Think 'Task Manager for Cognition'")
    print()

    # Create and start the dashboard
    dashboard = CognitiveTaskManager(port=8888)
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())
