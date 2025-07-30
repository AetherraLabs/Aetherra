"""
🌌 Quantum Memory Monitoring Web Dashboard
=========================================

Web-based dashboard for monitoring quantum-enhanced Lyrixa memory system.
Integrates with the existing QFAC dashboard framework.

Features:
- Real-time quantum coherence monitoring
- Quantum operation statistics and performance metrics
- Interactive quantum circuit visualization
- Quantum state health indicators
- Performance comparison charts (classical vs quantum)
- Quantum hardware status and scaling information
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    from aiohttp import web, web_ws

    # from aiohttp.web_runner import GracefulExit  # Unused, removed
    WEB_AVAILABLE = True
except ImportError:
    print("⚠️ aiohttp not available - web dashboard will not function")
    WEB_AVAILABLE = False
    web = None  # Ensure 'web' is always defined
    web_ws = None  # Ensure 'web_ws' is always defined

# Import quantum components
try:
    from .quantum_memory_integration import QuantumEnhancedMemoryEngine

    QUANTUM_INTEGRATION_AVAILABLE = True
except ImportError:
    print("⚠️ Quantum integration not available")
    QuantumEnhancedMemoryEngine = Any  # type: ignore
    QUANTUM_INTEGRATION_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuantumWebDashboard:
    """Web-based dashboard for quantum memory monitoring"""

    def __init__(self, quantum_engine=None, port: int = 8080):
        self.quantum_engine = quantum_engine
        self.port = port
        self.app = None
        self.runner = None
        self.site = None
        self.websockets = []  # type: ignore

        # Dashboard data storage
        self.dashboard_data = {
            "quantum_metrics": [],
            "performance_history": [],
            "operation_stats": {},
            "system_status": {},
            "alerts": [],
        }

        # Create dashboard directory
        self.dashboard_dir = Path("quantum_dashboard")
        self.dashboard_dir.mkdir(exist_ok=True)

        # Create static files directory
        self.static_dir = self.dashboard_dir / "static"
        self.static_dir.mkdir(exist_ok=True)

    async def initialize(self):
        """Initialize the web dashboard"""
        if not WEB_AVAILABLE:
            raise RuntimeError("aiohttp not available - cannot start web dashboard")

        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot start web dashboard")
        app = web.Application()
        self.app = app

        # Setup routes
        self.app.router.add_get("/", self.index_handler)
        self.app.router.add_get("/quantum", self.quantum_dashboard_handler)
        self.app.router.add_get("/api/quantum/status", self.api_quantum_status)
        self.app.router.add_get("/api/quantum/metrics", self.api_quantum_metrics)
        self.app.router.add_get("/api/quantum/operations", self.api_quantum_operations)
        self.app.router.add_get("/ws", self.websocket_handler)
        self.app.router.add_static("/static", self.static_dir, name="static")

        # Create static files
        await self.create_static_files()

        logger.info("🌌 Quantum Web Dashboard initialized")

    async def create_static_files(self):
        """Create HTML, CSS, and JavaScript files for the dashboard"""

        # Create main dashboard HTML
        dashboard_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌌 Quantum Memory Dashboard - Aetherra</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3a 100%);
            color: #ffffff;
            min-height: 100vh;
        }

        .header {
            background: linear-gradient(90deg, #2563eb 0%, #7c3aed 100%);
            padding: 1rem 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: transform 0.2s ease;
        }

        .card:hover {
            transform: translateY(-2px);
        }

        .card-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #60a5fa;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.8rem;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 6px;
        }

        .metric-label {
            font-weight: 500;
        }

        .metric-value {
            font-weight: 600;
            color: #34d399;
        }

        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-active {
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
        }

        .status-inactive {
            background: #ef4444;
        }

        .status-warning {
            background: #f59e0b;
        }

        .chart-container {
            height: 200px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 1rem;
        }

        .operations-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }

        .operation-stat {
            text-align: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
        }

        .operation-stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: #a78bfa;
        }

        .operation-stat-label {
            font-size: 0.9rem;
            color: #9ca3af;
            margin-top: 0.5rem;
        }

        .alert {
            padding: 0.8rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            border-left: 4px solid;
        }

        .alert-warning {
            background: rgba(245, 158, 11, 0.1);
            border-color: #f59e0b;
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            border-color: #ef4444;
        }

        .alert-info {
            background: rgba(59, 130, 246, 0.1);
            border-color: #3b82f6;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981, #34d399);
            transition: width 0.3s ease;
        }

        .quantum-circuit {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 1rem;
        }

        .qubit {
            height: 40px;
            background: linear-gradient(45deg, #7c3aed, #a855f7);
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.8rem;
        }

        .connection-status {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .connected {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid #10b981;
        }

        .disconnected {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid #ef4444;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connectionStatus">
        <span class="status-indicator status-inactive"></span>
        Connecting...
    </div>

    <div class="header">
        <h1>🌌 Quantum Memory Dashboard</h1>
    </div>

    <div class="dashboard">
        <!-- Quantum System Status -->
        <div class="card">
            <div class="card-title">⚛️ Quantum System Status</div>
            <div class="metric">
                <span class="metric-label">Quantum Bridge</span>
                <span class="metric-value" id="quantumBridgeStatus">
                    <span class="status-indicator status-inactive"></span>
                    Checking...
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Backend</span>
                <span class="metric-value" id="quantumBackend">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Active Qubits</span>
                <span class="metric-value" id="activeQubits">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Quantum States</span>
                <span class="metric-value" id="quantumStates">-</span>
            </div>
        </div>

        <!-- Quantum Coherence -->
        <div class="card">
            <div class="card-title">🌊 Quantum Coherence</div>
            <div class="metric">
                <span class="metric-label">Average Coherence</span>
                <span class="metric-value" id="avgCoherence">-</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="coherenceProgress" style="width: 0%"></div>
            </div>
            <div class="metric">
                <span class="metric-label">Coherent States</span>
                <span class="metric-value" id="coherentStates">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Decoherent States</span>
                <span class="metric-value" id="decoherentStates">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Corrected States</span>
                <span class="metric-value" id="correctedStates">-</span>
            </div>
        </div>

        <!-- Operation Statistics -->
        <div class="card">
            <div class="card-title">📊 Operation Statistics</div>
            <div class="operations-grid">
                <div class="operation-stat">
                    <div class="operation-stat-number" id="quantumEncodings">-</div>
                    <div class="operation-stat-label">Quantum Encodings</div>
                </div>
                <div class="operation-stat">
                    <div class="operation-stat-number" id="quantumRecalls">-</div>
                    <div class="operation-stat-label">Quantum Recalls</div>
                </div>
                <div class="operation-stat">
                    <div class="operation-stat-number" id="quantumExperiments">-</div>
                    <div class="operation-stat-label">Experiments</div>
                </div>
                <div class="operation-stat">
                    <div class="operation-stat-number" id="classicalFallbacks">-</div>
                    <div class="operation-stat-label">Classical Fallbacks</div>
                </div>
            </div>
        </div>

        <!-- Performance Metrics -->
        <div class="card">
            <div class="card-title">⚡ Performance Metrics</div>
            <div class="metric">
                <span class="metric-label">Quantum Enhancement Ratio</span>
                <span class="metric-value" id="enhancementRatio">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value" id="successRate">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Response Time</span>
                <span class="metric-value" id="avgResponseTime">-</span>
            </div>
            <div class="chart-container">
                <span style="color: #6b7280;">Performance Chart</span>
            </div>
        </div>

        <!-- Quantum Circuit Visualization -->
        <div class="card">
            <div class="card-title">🔗 Active Quantum Circuits</div>
            <div class="quantum-circuit" id="quantumCircuit">
                <div class="qubit">Q0</div>
                <div class="qubit">Q1</div>
                <div class="qubit">Q2</div>
                <div class="qubit">Q3</div>
            </div>
            <div class="metric" style="margin-top: 1rem;">
                <span class="metric-label">Circuit Depth</span>
                <span class="metric-value" id="circuitDepth">-</span>
            </div>
            <div class="metric">
                <span class="metric-label">Gate Operations</span>
                <span class="metric-value" id="gateOperations">-</span>
            </div>
        </div>

        <!-- System Alerts -->
        <div class="card">
            <div class="card-title">🚨 System Alerts</div>
            <div id="alertsContainer">
                <div class="alert alert-info">
                    <strong>Info:</strong> Quantum dashboard initialized
                </div>
            </div>
        </div>
    </div>

    <script>
        let websocket = null;
        let reconnectInterval = null;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            websocket = new WebSocket(wsUrl);

            websocket.onopen = function(event) {
                console.log('WebSocket connected');
                updateConnectionStatus(true);
                clearInterval(reconnectInterval);
            };

            websocket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            websocket.onclose = function(event) {
                console.log('WebSocket disconnected');
                updateConnectionStatus(false);

                // Attempt to reconnect every 5 seconds
                reconnectInterval = setInterval(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket();
                }, 5000);
            };

            websocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        function updateConnectionStatus(connected) {
            const statusEl = document.getElementById('connectionStatus');
            const indicator = statusEl.querySelector('.status-indicator');

            if (connected) {
                statusEl.className = 'connection-status connected';
                statusEl.innerHTML = '<span class="status-indicator status-active"></span>Connected';
            } else {
                statusEl.className = 'connection-status disconnected';
                statusEl.innerHTML = '<span class="status-indicator status-inactive"></span>Disconnected';
            }
        }

        function updateDashboard(data) {
            if (data.type === 'quantum_status') {
                updateQuantumStatus(data.payload);
            } else if (data.type === 'quantum_metrics') {
                updateQuantumMetrics(data.payload);
            } else if (data.type === 'operation_stats') {
                updateOperationStats(data.payload);
            } else if (data.type === 'alerts') {
                updateAlerts(data.payload);
            }
        }

        function updateQuantumStatus(status) {
            const bridgeStatus = document.getElementById('quantumBridgeStatus');
            const indicator = bridgeStatus.querySelector('.status-indicator');

            if (status.quantum_available) {
                indicator.className = 'status-indicator status-active';
                bridgeStatus.innerHTML = '<span class="status-indicator status-active"></span>Active';
            } else {
                indicator.className = 'status-indicator status-inactive';
                bridgeStatus.innerHTML = '<span class="status-indicator status-inactive"></span>Inactive';
            }

            document.getElementById('quantumBackend').textContent = status.quantum_backend || '-';
            document.getElementById('activeQubits').textContent = status.max_qubits || '-';
            document.getElementById('quantumStates').textContent = status.quantum_states_count || '-';
        }

        function updateQuantumMetrics(metrics) {
            if (metrics.coherence_data) {
                const coherence = metrics.coherence_data.average_coherence || 0;
                document.getElementById('avgCoherence').textContent = (coherence * 100).toFixed(1) + '%';
                document.getElementById('coherenceProgress').style.width = (coherence * 100) + '%';
                document.getElementById('coherentStates').textContent = metrics.coherence_data.coherent_states || '-';
                document.getElementById('decoherentStates').textContent = metrics.coherence_data.decoherent_states || '-';
                document.getElementById('correctedStates').textContent = metrics.coherence_data.corrected_states || '-';
            }

            if (metrics.performance) {
                document.getElementById('enhancementRatio').textContent = (metrics.performance.quantum_enhanced_ratio * 100).toFixed(1) + '%';
                document.getElementById('successRate').textContent = (metrics.performance.quantum_success_rate * 100).toFixed(1) + '%';
                document.getElementById('avgResponseTime').textContent = metrics.performance.avg_response_time || '-';
            }
        }

        function updateOperationStats(stats) {
            document.getElementById('quantumEncodings').textContent = stats.quantum_encodings || '0';
            document.getElementById('quantumRecalls').textContent = stats.quantum_recalls || '0';
            document.getElementById('quantumExperiments').textContent = stats.quantum_experiments || '0';
            document.getElementById('classicalFallbacks').textContent = stats.classical_fallbacks || '0';
        }

        function updateAlerts(alerts) {
            const container = document.getElementById('alertsContainer');
            container.innerHTML = '';

            alerts.forEach(alert => {
                const alertEl = document.createElement('div');
                alertEl.className = `alert alert-${alert.level}`;
                alertEl.innerHTML = `<strong>${alert.level.charAt(0).toUpperCase() + alert.level.slice(1)}:</strong> ${alert.message}`;
                container.appendChild(alertEl);
            });

            if (alerts.length === 0) {
                container.innerHTML = '<div class="alert alert-info"><strong>Info:</strong> No active alerts</div>';
            }
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();

            // Request initial data
            setTimeout(() => {
                fetch('/api/quantum/status')
                    .then(response => response.json())
                    .then(data => updateQuantumStatus(data))
                    .catch(console.error);

                fetch('/api/quantum/operations')
                    .then(response => response.json())
                    .then(data => updateOperationStats(data))
                    .catch(console.error);
            }, 1000);
        });
    </script>
</body>
</html>"""

        with open(self.static_dir / "dashboard.html", "w", encoding="utf-8") as f:
            f.write(dashboard_html)

        logger.info("✅ Static dashboard files created")

    async def start(self):
        """Start the web dashboard server"""
        await self.initialize()

        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot start web dashboard")
        # Ensure self.app is a valid Application and not None
        if self.app is None:
            raise RuntimeError("self.app is not initialized as a web.Application")
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, "0.0.0.0", self.port)
        await self.site.start()

        print(
            f"🌐 Quantum Web Dashboard started at http://localhost:{self.port}/quantum"
        )

        # Start background data collection
        asyncio.create_task(self.data_collection_loop())

        return f"http://localhost:{self.port}/quantum"

    async def stop(self):
        """Stop the web dashboard server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()

        # Close all websockets
        for ws in self.websockets:
            if not ws.closed:
                await ws.close()

        logger.info("🛑 Quantum Web Dashboard stopped")

    async def index_handler(self, request):
        """Redirect to quantum dashboard"""
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot redirect")
        return web.HTTPFound("/quantum")

    async def quantum_dashboard_handler(self, request):
        """Serve the quantum dashboard"""
        dashboard_path = self.static_dir / "dashboard.html"
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot serve dashboard")
        return web.FileResponse(dashboard_path)

    async def api_quantum_status(self, request):
        """API endpoint for quantum system status"""
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot serve API")
        if not self.quantum_engine:
            return web.json_response(
                {"quantum_available": False, "message": "Quantum engine not available"}
            )

        try:
            status = self.quantum_engine.get_quantum_system_status()
            return web.json_response(status)
        except Exception as e:
            return web.json_response(
                {"quantum_available": False, "error": str(e)}, status=500
            )

    async def api_quantum_metrics(self, request):
        """API endpoint for quantum metrics"""
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot serve API")
        if not self.quantum_engine:
            return web.json_response({})

        try:
            # Get coherence data
            coherence_data = await self.quantum_engine.check_quantum_coherence()

            # Get enhanced system status
            enhanced_status = await self.quantum_engine.get_enhanced_system_status()

            metrics = {
                "coherence_data": coherence_data,
                "performance": enhanced_status.get("hybrid_operations", {}),
                "capabilities": enhanced_status.get("capabilities", {}),
                "timestamp": datetime.now().isoformat(),
            }

            return web.json_response(metrics)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def api_quantum_operations(self, request):
        """API endpoint for quantum operation statistics"""
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot serve API")
        if not self.quantum_engine:
            return web.json_response({})

        try:
            return web.json_response(self.quantum_engine.quantum_operation_stats)
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    async def websocket_handler(self, request):
        """WebSocket handler for real-time updates"""
        if not WEB_AVAILABLE or web is None:
            raise RuntimeError("aiohttp not available - cannot serve WebSocket")
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.websockets.append(ws)
        logger.info("🔌 WebSocket client connected")

        try:
            async for msg in ws:
                if (
                    web_ws
                    and hasattr(web_ws, "WSMsgType")
                    and msg.type == web_ws.WSMsgType.TEXT
                ):
                    # Handle incoming WebSocket messages if needed
                    pass
                elif (
                    web_ws
                    and hasattr(web_ws, "WSMsgType")
                    and msg.type == web_ws.WSMsgType.ERROR
                ):
                    logger.error(f"WebSocket error: {ws.exception()}")
                    break
        except Exception as e:
            logger.error(f"WebSocket handler error: {e}")
        finally:
            if ws in self.websockets:
                self.websockets.remove(ws)
            logger.info("🔌 WebSocket client disconnected")

        return ws

    async def broadcast_to_websockets(self, data):
        """Broadcast data to all connected WebSocket clients"""
        if not self.websockets:
            return

        message = json.dumps(data)
        disconnected = []

        for ws in self.websockets:
            try:
                if ws.closed:
                    disconnected.append(ws)
                else:
                    await ws.send_str(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(ws)

        # Remove disconnected websockets
        for ws in disconnected:
            if ws in self.websockets:
                self.websockets.remove(ws)

    async def data_collection_loop(self):
        """Background loop to collect and broadcast quantum data"""
        while True:
            try:
                if self.quantum_engine and self.websockets:
                    # Collect quantum status
                    status = self.quantum_engine.get_quantum_system_status()
                    await self.broadcast_to_websockets(
                        {"type": "quantum_status", "payload": status}
                    )

                    # Collect quantum metrics
                    coherence_data = await self.quantum_engine.check_quantum_coherence()
                    enhanced_status = (
                        await self.quantum_engine.get_enhanced_system_status()
                    )

                    metrics = {
                        "coherence_data": coherence_data,
                        "performance": enhanced_status.get("hybrid_operations", {}),
                        "timestamp": datetime.now().isoformat(),
                    }

                    await self.broadcast_to_websockets(
                        {"type": "quantum_metrics", "payload": metrics}
                    )

                    # Collect operation stats
                    await self.broadcast_to_websockets(
                        {
                            "type": "operation_stats",
                            "payload": self.quantum_engine.quantum_operation_stats,
                        }
                    )

                    # Check for alerts
                    alerts = self.check_for_alerts(status, coherence_data)
                    if alerts:
                        await self.broadcast_to_websockets(
                            {"type": "alerts", "payload": alerts}
                        )

                await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Data collection error: {e}")
                await asyncio.sleep(10)  # Wait longer on error

    def check_for_alerts(self, status: Dict, coherence_data: Dict) -> List[Dict]:
        """Check for system alerts based on current status"""
        alerts = []

        if not status.get("quantum_available"):
            alerts.append(
                {
                    "level": "warning",
                    "message": "Quantum bridge not available - running in classical mode",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        if coherence_data.get("average_coherence", 0) < 0.6:
            alerts.append(
                {
                    "level": "warning",
                    "message": f"Low quantum coherence: {coherence_data.get('average_coherence', 0):.2%}",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        if coherence_data.get("decoherent_states", 0) > coherence_data.get(
            "coherent_states", 0
        ):
            alerts.append(
                {
                    "level": "error",
                    "message": "More decoherent states than coherent states detected",
                    "timestamp": datetime.now().isoformat(),
                }
            )

        return alerts


# Integration with existing QFAC dashboard
async def start_quantum_web_dashboard(quantum_engine, port: int = 8080) -> str:
    """
    Start the quantum web dashboard

    Returns:
        str: URL of the started dashboard
    """
    if not WEB_AVAILABLE:
        raise RuntimeError("Web dashboard dependencies not available")

    dashboard = QuantumWebDashboard(quantum_engine, port)
    url = await dashboard.start()

    logger.info(f"🌌 Quantum Web Dashboard available at: {url}")
    return url


# Example usage
async def demo_quantum_web_dashboard():
    """Demonstrate the quantum web dashboard"""
    print("🌌 Starting Quantum Web Dashboard Demo...")

    # Create a quantum-enhanced memory engine
    if QUANTUM_INTEGRATION_AVAILABLE:
        from .quantum_memory_integration import create_quantum_enhanced_memory_engine

        engine = create_quantum_enhanced_memory_engine()

        # Add some test data
        await engine.remember(
            "Quantum computing enables exponential speedup",
            tags=["quantum", "computing"],
        )
        await engine.remember(
            "Superposition allows parallel computation",
            tags=["quantum", "superposition"],
        )
    else:
        engine = None
        print("⚠️ Quantum integration not available - dashboard will show mock data")

    # Start the dashboard
    dashboard = QuantumWebDashboard(engine, port=8080)
    url = await dashboard.start()

    print(f"✅ Quantum dashboard started at: {url}")
    print("Press Ctrl+C to stop the dashboard")

    try:
        # Keep the dashboard running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
        await dashboard.stop()


if __name__ == "__main__":
    if WEB_AVAILABLE:
        asyncio.run(demo_quantum_web_dashboard())
    else:
        print("❌ Web dashboard cannot run - missing dependencies")
        print("Install with: pip install aiohttp")
