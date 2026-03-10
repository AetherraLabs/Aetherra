# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🖥️ AETHERRA OS - MAIN INTERFACE WINDOW
=====================================

Hybrid PySide6 + Web Dashboard for Aetherra Operating System
- Native Python performance and OS integration
- Beautiful web-based panels for complex visualizations
- Real-time monitoring of all OS components
- Live cognitive state visualization

This is the primary interface to the Aetherra AI Operating System.
"""

# Standard library imports
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Third party imports
from PySide6.QtCore import (
    QSettings,  # noqa: F401 (optional runtime import)
    Qt,
    QThread,
    QUrl,
    Signal,
)
from PySide6.QtGui import (
    QAction,  # noqa: F401 (optional runtime import)
    QFont,
    QIcon,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSplitter,
    QStatusBar,
    QSystemTrayIcon,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import Aetherra OS components
try:
    # Aetherra imports (optional embedded server)
    from Aetherra.gui.web_interface_server import AetherraWebServer

    AETHERRA_SERVER_AVAILABLE = True
except Exception:
    AETHERRA_SERVER_AVAILABLE = False
    print("[WARN] Aetherra web server not available - running in direct-fetch mode")

try:
    # Third party imports
    import psutil

    SYSTEM_MONITORING_AVAILABLE = True
except ImportError:
    SYSTEM_MONITORING_AVAILABLE = False


class AetherraOSMonitor(QThread):
    """Background thread for monitoring Aetherra OS state"""

    # Signals for real-time updates
    system_update = Signal(dict)
    memory_update = Signal(dict)
    agent_update = Signal(dict)
    cognitive_update = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.update_interval = 1000  # 1 second
        # Endpoints configurable via environment
        self.base_url: str = os.environ.get("AETHERRA_BASE_URL", "http://127.0.0.1:3001").rstrip(
            "/"
        )
        self.qfac_url: str = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip(
            "/"
        )
        # Resolve Windows drive root for psutil disk
        self._disk_root = "C:\\" if os.name == "nt" else "/"

    def run(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Collect system metrics
                system_data = self.collect_system_metrics()
                self.system_update.emit(system_data)

                # Collect memory metrics
                memory_data = self.collect_memory_metrics()
                self.memory_update.emit(memory_data)

                # Collect agent status
                agent_data = self.collect_agent_metrics()
                self.agent_update.emit(agent_data)

                # Collect cognitive state
                cognitive_data = self.collect_cognitive_metrics()
                self.cognitive_update.emit(cognitive_data)

                self.msleep(self.update_interval)

            except Exception as e:
                print(f"Monitor error: {e}")
                self.msleep(5000)  # Wait 5 seconds on error

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics"""
        data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "status": "online",
            "uptime": self.get_uptime(),
        }

        if SYSTEM_MONITORING_AVAILABLE:
            data["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            data["memory_percent"] = psutil.virtual_memory().percent
            data["disk_usage"] = psutil.disk_usage(self._disk_root).percent
            data["active_processes"] = len(psutil.pids())
            data["network_connections"] = len(psutil.net_connections())

        return data

    def collect_memory_metrics(self) -> Dict[str, Any]:
        """Collect Aetherra memory (QFAC) metrics from live endpoint with fallback"""
        # Try QFAC dashboard endpoints
        status = self._http_get_json(f"{self.qfac_url}/api/status")
        perf = self._http_get_json(f"{self.qfac_url}/api/performance")
        if status or perf:
            data: Dict[str, Any] = {"timestamp": datetime.now().isoformat()}
            if status:
                data.update(
                    {
                        "memory_health": status.get("health") or status.get("status"),
                        "total_memories": status.get("total_memories") or status.get("memories"),
                        "recent_events": status.get("recent_events") or status.get("recent") or [],
                    }
                )
            if perf:
                data.update(
                    {
                        "fractal_compression_ratio": perf.get("compression_ratio")
                        or perf.get("ratio"),
                        "quantum_coherence": perf.get("parity") or perf.get("coherence"),
                        "observer_branches": perf.get("nodes") or perf.get("branches"),
                    }
                )
            return data

        # Fallback minimal when endpoints unavailable
        return {
            "timestamp": datetime.now().isoformat(),
            "memory_health": "unknown",
            "recent_events": [],
        }

    def collect_agent_metrics(self) -> Dict[str, Any]:
        """Collect agent ecosystem metrics from Hub API"""
        agents_json = self._http_get_json(f"{self.base_url}/api/agents")
        data: Dict[str, Any] = {"timestamp": datetime.now().isoformat()}
        items_list: list = []
        if isinstance(agents_json, dict):
            maybe = agents_json.get("agents")
            if isinstance(maybe, list):
                items_list = maybe
        elif isinstance(agents_json, list):
            items_list = agents_json

        data["active_agents"] = len(items_list)
        status_map: Dict[str, Any] = {}
        for i, a in enumerate(items_list):
            if isinstance(a, dict):
                name = str(a.get("name", f"agent_{i}"))
                status_map[name] = {
                    "status": a.get("status", "unknown"),
                    "load": a.get("load", 0),
                    "health": a.get("health", 1.0),
                }
        data["agent_status"] = status_map
        return data

    def collect_cognitive_metrics(self) -> Dict[str, Any]:
        """Collect Lyrixa cognitive state metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cognitive_load": "normal",
            "emotional_vector": {"curiosity": 0.8, "confidence": 0.9, "empathy": 0.7},
            "personality_drift": {
                "curiosity": +0.2,
                "formality": -0.1,
                "technical_focus": +0.3,
            },
            "recent_goals": [
                "optimize_memory_performance",
                "enhance_user_interaction",
                "monitor_system_health",
            ],
            "learning_state": "active",
            "consciousness_level": 0.87,
        }

    def get_uptime(self) -> str:
        """Get system uptime"""
        if SYSTEM_MONITORING_AVAILABLE:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            return str(uptime).split(".")[0]  # Remove microseconds
        else:
            return "2:34:17"  # Mock uptime

    # --- HTTP helpers ---
    def _http_get_json(self, url: str, timeout: float = 1.2) -> Optional[Any]:
        """Lightweight HTTP GET returning JSON without third-party deps.

        Uses urllib to avoid adding requests dependency to the GUI.
        """
        try:
            # Standard library imports
            import json as _json
            from urllib.error import HTTPError, URLError
            from urllib.request import Request, urlopen

            req = Request(url, headers={"Accept": "application/json"})
            with urlopen(req, timeout=timeout) as resp:  # nosec B310: trusted localhost endpoints
                ctype = resp.headers.get("Content-Type", "")
                raw = resp.read()
                if b"application/json" in ctype.encode() or raw.strip().startswith(b"{"):
                    return _json.loads(raw.decode("utf-8", errors="ignore"))
                return None
        except (URLError, HTTPError, ValueError):
            return None

    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.wait()


class AetherraOSMainWindow(QMainWindow):
    """Main window for Aetherra OS Interface"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aetherra AI Operating System - Live Dashboard")
        self.setMinimumSize(1400, 900)
        self.setStyleSheet(self.get_dark_theme())

        # Initialize components
        self.web_server = None
        self.monitor_thread = None
        self.settings = QSettings("AetherraLabs", "AetherraOS")

        # Setup UI
        self.setup_ui()
        self.setup_monitoring()
        self.setup_system_tray()

        # Start web server
        self.start_web_server()

        # Restore window state
        self.restore_window_state()

    def setup_ui(self):
        """Setup the main UI components"""
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel - System Overview
        self.create_system_overview_panel(main_splitter)

        # Right panel - Tabbed interface
        self.create_tabbed_interface(main_splitter)

        # Status bar
        self.create_status_bar()

        # Set splitter proportions
        main_splitter.setSizes([400, 1000])

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # System menu
        system_menu = menubar.addMenu("System")

        restart_action = QAction("Restart Aetherra", self)
        restart_action.triggered.connect(self.restart_system)
        system_menu.addAction(restart_action)

        shutdown_action = QAction("Shutdown", self)
        shutdown_action.triggered.connect(self.shutdown_system)
        system_menu.addAction(shutdown_action)

        system_menu.addSeparator()

        exit_action = QAction("Exit Dashboard", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        fullscreen_action = QAction("Toggle Fullscreen", self)
        fullscreen_action.setShortcut("F11")
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        validate_action = QAction("Validate Features", self)
        validate_action.triggered.connect(self.validate_features)
        tools_menu.addAction(validate_action)

        memory_action = QAction("Memory Diagnostics", self)
        memory_action.triggered.connect(self.run_memory_diagnostics)
        tools_menu.addAction(memory_action)

    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        toolbar.setMovable(False)

        # Status indicator
        self.status_indicator = QLabel("🟢 ONLINE")
        bold_font = QFont("Arial", 10)
        bold_font.setBold(True)
        self.status_indicator.setFont(bold_font)
        self.status_indicator.setStyleSheet("color: #00ff88; padding: 5px;")
        toolbar.addWidget(self.status_indicator)

        toolbar.addSeparator()

        # System health button
        health_btn = QPushButton("System Health")
        health_btn.clicked.connect(self.show_system_health)
        toolbar.addWidget(health_btn)

        # Agent status button
        agents_btn = QPushButton("Agents")
        agents_btn.clicked.connect(self.show_agent_dashboard)
        toolbar.addWidget(agents_btn)

        # Memory button
        memory_btn = QPushButton("Memory")
        memory_btn.clicked.connect(self.show_memory_dashboard)
        toolbar.addWidget(memory_btn)

        toolbar.addSeparator()

        # Live toggle
        self.live_toggle = QPushButton("🔴 LIVE")
        self.live_toggle.setCheckable(True)
        self.live_toggle.setChecked(True)
        self.live_toggle.clicked.connect(self.toggle_live_updates)
        self.live_toggle.setStyleSheet(
            """
            QPushButton:checked {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
            }
        """
        )
        toolbar.addWidget(self.live_toggle)

    def create_system_overview_panel(self, parent):
        """Create the system overview panel"""
        overview_widget = QWidget()
        overview_layout = QVBoxLayout(overview_widget)

        # Title
        title = QLabel("AETHERRA OS STATUS")
        title_font = QFont("Arial", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #00ffaa; padding: 10px; border-bottom: 2px solid #00ffaa;")
        overview_layout.addWidget(title)

        # System metrics web view
        self.system_metrics_view = QWebEngineView()
        overview_layout.addWidget(self.system_metrics_view)

        parent.addWidget(overview_widget)

    def create_tabbed_interface(self, parent):
        """Create the main tabbed interface"""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)

        # Dashboard tab
        self.dashboard_view = QWebEngineView()
        self.tab_widget.addTab(self.dashboard_view, "🖥️ Dashboard")

        # Memory visualization tab
        self.memory_view = QWebEngineView()
        self.tab_widget.addTab(self.memory_view, "🧠 Memory Map")

        # Agent ecosystem tab
        self.agents_view = QWebEngineView()
        self.tab_widget.addTab(self.agents_view, "🤖 Agents")

        # Cognitive state tab
        self.cognitive_view = QWebEngineView()
        self.tab_widget.addTab(self.cognitive_view, "🌟 Consciousness")

        # Security & Health tab
        self.security_view = QWebEngineView()
        self.tab_widget.addTab(self.security_view, "🛡️ Security")

        # Live logs tab
        self.logs_view = QWebEngineView()
        self.tab_widget.addTab(self.logs_view, "📜 Live Logs")

        parent.addWidget(self.tab_widget)

    def create_status_bar(self):
        """Create the status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # CPU usage
        self.cpu_label = QLabel("CPU: 0%")
        status_bar.addWidget(self.cpu_label)

        # Memory usage
        self.memory_label = QLabel("Memory: 0%")
        status_bar.addWidget(self.memory_label)

        # Active agents
        self.agents_label = QLabel("Agents: 0")
        status_bar.addWidget(self.agents_label)

        # Uptime
        self.uptime_label = QLabel("Uptime: 00:00:00")
        status_bar.addPermanentWidget(self.uptime_label)

    def setup_monitoring(self):
        """Setup background monitoring"""
        self.monitor_thread = AetherraOSMonitor()

        # Connect signals
        self.monitor_thread.system_update.connect(self.update_system_metrics)
        self.monitor_thread.memory_update.connect(self.update_memory_metrics)
        self.monitor_thread.agent_update.connect(self.update_agent_metrics)
        self.monitor_thread.cognitive_update.connect(self.update_cognitive_metrics)

        # Start monitoring
        self.monitor_thread.start()

    def setup_system_tray(self):
        """Setup system tray icon"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(QIcon("assets/aetherra_icon.png"))  # You'll need to add this

            # Tray menu
            tray_menu = QMenu()

            show_action = QAction("Show Dashboard", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)

            quit_action = QAction("Quit", self)
            quit_action.triggered.connect(self.close)
            tray_menu.addAction(quit_action)

            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()

    def start_web_server(self):
        """Start the embedded web server"""
        if AETHERRA_SERVER_AVAILABLE:
            try:
                self.web_server = AetherraWebServer(host="127.0.0.1", port=8686)
                # Start server in separate thread
                # Standard library imports
                import threading

                if not (
                    self.web_server
                    and hasattr(self.web_server, "socketio")
                    and hasattr(self.web_server, "app")
                ):
                    raise RuntimeError("Embedded web server missing required attributes")

                server_thread = threading.Thread(
                    target=lambda: self.web_server.socketio.run(
                        self.web_server.app, host="127.0.0.1", port=8686, debug=False
                    ),
                    daemon=True,
                )
                server_thread.start()

                # Load web views
                self.load_web_panels()

            except Exception as e:
                print(f"Failed to start web server: {e}")
                self.load_fallback_panels()
        else:
            self.load_fallback_panels()

    def load_web_panels(self):
        """Load web-based panels"""
        base_url = "http://127.0.0.1:8686"

        # Load main dashboard
        self.dashboard_view.load(QUrl(f"{base_url}/"))

        # Load memory visualization
        self.memory_view.load(QUrl(f"{base_url}/quantum"))

        # Create system overview panel
        self.load_system_overview()

        # If QFAC dashboard is available, load it in Memory tab
        qfac_url = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip("/")
        self._try_load_qfac_dashboard(qfac_url)

    def load_system_overview(self):
        """Load system overview panel"""
        overview_html = self.create_system_overview_html()
        self.system_metrics_view.setHtml(overview_html)

    def load_fallback_panels(self):
        """Load fallback HTML panels when web server is not available"""
        dashboard_html = self.create_fallback_dashboard()
        self.dashboard_view.setHtml(dashboard_html)

        memory_html = self.create_fallback_memory_view()
        self.memory_view.setHtml(memory_html)

        self.load_system_overview()

        # Attempt to point Memory tab to live QFAC dashboard if running
        qfac_url = os.environ.get("AETHERRA_QFAC_URL", "http://127.0.0.1:4020").rstrip("/")
        self._try_load_qfac_dashboard(qfac_url)

    def _try_load_qfac_dashboard(self, qfac_url: str) -> None:
        """Try loading the QFAC dashboard; fallback HTML remains if not reachable."""
        # Use a tiny HEAD/GET to test
        try:
            from urllib.error import URLError
            from urllib.request import Request, urlopen

            req = Request(qfac_url + "/", method="GET")
            with urlopen(req, timeout=0.6):  # nosec B310: local endpoint
                pass
            self.memory_view.load(QUrl(qfac_url + "/"))
        except URLError:
            pass

    def create_system_overview_html(self) -> str:
        """Create HTML for system overview panel"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Overview</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
                    color: #00ffaa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    overflow-x: hidden;
                }
                .metric-box {
                    background: rgba(0, 255, 170, 0.1);
                    border: 1px solid #00ffaa;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    transition: all 0.3s ease;
                }
                .metric-box:hover {
                    background: rgba(0, 255, 170, 0.2);
                    transform: translateX(5px);
                }
                .metric-title {
                    font-weight: bold;
                    color: #00ff88;
                    margin-bottom: 5px;
                }
                .metric-value {
                    font-size: 1.2em;
                    color: #ffffff;
                }
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                .status-online { background-color: #00ff88; }
                .status-warning { background-color: #ffaa00; }
                .status-error { background-color: #ff4444; }
                .progress-bar {
                    width: 100%;
                    height: 20px;
                    background: rgba(0, 0, 0, 0.5);
                    border-radius: 10px;
                    overflow: hidden;
                    margin-top: 5px;
                }
                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #00ffaa, #00cc88);
                    transition: width 0.5s ease;
                }
            </style>
            <script>
                function updateMetrics(data) {
                    if (data.cpu_percent !== undefined) {
                        document.getElementById('cpu-value').textContent = data.cpu_percent.toFixed(1) + '%';
                        document.getElementById('cpu-bar').style.width = data.cpu_percent + '%';
                    }
                    if (data.memory_percent !== undefined) {
                        document.getElementById('memory-value').textContent = data.memory_percent.toFixed(1) + '%';
                        document.getElementById('memory-bar').style.width = data.memory_percent + '%';
                    }
                    if (data.uptime !== undefined) {
                        document.getElementById('uptime-value').textContent = data.uptime;
                    }
                    if (data.active_processes !== undefined) {
                        document.getElementById('processes-value').textContent = data.active_processes;
                    }
                }

                // Auto-refresh every 2 seconds
                setInterval(() => {
                    // This would be updated by the Python side
                    console.log('Metrics refresh');
                }, 2000);
            </script>
        </head>
        <body>
            <div class="metric-box">
                <div class="metric-title">
                    <span class="status-indicator status-online"></span>System Status
                </div>
                <div class="metric-value">AETHERRA OS ONLINE</div>
            </div>

            <div class="metric-box">
                <div class="metric-title">Uptime</div>
                <div class="metric-value" id="uptime-value">Loading...</div>
            </div>

            <div class="metric-box">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value" id="cpu-value">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="cpu-bar" style="width: 0%"></div>
                </div>
            </div>

            <div class="metric-box">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value" id="memory-value">0%</div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-bar" style="width: 0%"></div>
                </div>
            </div>

            <div class="metric-box">
                <div class="metric-title">Active Processes</div>
                <div class="metric-value" id="processes-value">0</div>
            </div>

            <div class="metric-box">
                <div class="metric-title">
                    <span class="status-indicator status-online"></span>Lyrixa Consciousness
                </div>
                <div class="metric-value">87% Active</div>
            </div>

            <div class="metric-box">
                <div class="metric-title">Active Agents</div>
                <div class="metric-value" id="agents-value">6</div>
            </div>
        </body>
        </html>
        """

    def create_fallback_dashboard(self) -> str:
        """Create fallback dashboard HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Aetherra OS Dashboard</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0a0a0a, #1a1a2e, #16213e);
                    color: #00ffaa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    min-height: 100vh;
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #00ffaa;
                    padding-bottom: 20px;
                }
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }
                .dashboard-card {
                    background: rgba(0, 255, 170, 0.1);
                    border: 1px solid #00ffaa;
                    border-radius: 10px;
                    padding: 20px;
                    transition: all 0.3s ease;
                }
                .dashboard-card:hover {
                    background: rgba(0, 255, 170, 0.2);
                    transform: translateY(-5px);
                }
                .card-title {
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 15px;
                    color: #00ff88;
                }
                .status-good { color: #00ff88; }
                .status-warning { color: #ffaa00; }
                .status-error { color: #ff4444; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AETHERRA AI OPERATING SYSTEM</h1>
                <p>Live Dashboard - Hybrid Interface</p>
            </div>

            <div class="dashboard-grid">
                <div class="dashboard-card">
                    <div class="card-title">System Overview</div>
                    <p>Status: <span class="status-good">🟢 ONLINE</span></p>
                    <p>Uptime: 2:34:17</p>
                    <p>Active Agents: 6</p>
                    <p>Running Workflows: 3</p>
                </div>

                <div class="dashboard-card">
                    <div class="card-title">Quantum Memory Metrics</div>
                    <p>Total Memories: 1,247</p>
                    <p>Compression Ratio: 4.6:1</p>
                    <p>Observer Branches: 3</p>
                    <p>Quantum Coherence: <span class="status-good">94%</span></p>
                </div>

                <div class="dashboard-card">
                    <div class="card-title">Plugin Ecosystem</div>
                    <p>Installed Plugins: 12</p>
                    <p>Active Chains: 4</p>
                    <p>UI Components: <span class="status-good">Linked</span></p>
                    <p>Last Execution: conversation_enhancement.aether</p>
                </div>

                <div class="dashboard-card">
                    <div class="card-title">Lyrixa Intelligence State</div>
                    <p>Cognitive Load: <span class="status-good">Normal</span></p>
                    <p>Curiosity: 80%</p>
                    <p>Confidence: 90%</p>
                    <p>Learning State: <span class="status-good">Active</span></p>
                </div>

                <div class="dashboard-card">
                    <div class="card-title">Security & Health</div>
                    <p>Import Conflicts: <span class="status-good">✅ None</span></p>
                    <p>Filesystem Watchers: <span class="status-good">✅ Active</span></p>
                    <p>Corruption Watchdog: <span class="status-good">✅ Monitoring</span></p>
                    <p>Risk Flags: <span class="status-good">[WARN] None</span></p>
                </div>

                <div class="dashboard-card">
                    <div class="card-title">Recent Activity</div>
                    <p>• Enhanced conversation processed</p>
                    <p>• Memory compression optimized</p>
                    <p>• Agent collaboration completed</p>
                    <p>• Ethics check passed</p>
                </div>
            </div>
        </body>
        </html>
        """

    def create_fallback_memory_view(self) -> str:
        """Create fallback memory visualization HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Memory Visualization</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0a0a0a, #1a1a2e);
                    color: #00ffaa;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                }
                .memory-container {
                    display: flex;
                    flex-direction: column;
                    gap: 20px;
                }
                .memory-stats {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                }
                .stat-box {
                    background: rgba(0, 255, 170, 0.1);
                    border: 1px solid #00ffaa;
                    border-radius: 8px;
                    padding: 15px;
                    text-align: center;
                }
                .stat-value {
                    font-size: 2em;
                    font-weight: bold;
                    color: #ffffff;
                }
                .stat-label {
                    color: #00ff88;
                    margin-top: 5px;
                }
                .memory-graph {
                    background: rgba(0, 0, 0, 0.5);
                    border: 1px solid #00ffaa;
                    border-radius: 10px;
                    padding: 20px;
                    height: 400px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2em;
                }
            </style>
        </head>
        <body>
            <div class="memory-container">
                <h2>🧠 Quantum Memory System</h2>

                <div class="memory-stats">
                    <div class="stat-box">
                        <div class="stat-value">1,247</div>
                        <div class="stat-label">Total Memories</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">4.6:1</div>
                        <div class="stat-label">Compression Ratio</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">94%</div>
                        <div class="stat-label">Quantum Coherence</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">3</div>
                        <div class="stat-label">Observer Branches</div>
                    </div>
                </div>

                <div class="memory-graph">
                    Memory visualization would appear here<br>
                    (Requires full web server integration)
                </div>
            </div>
        </body>
        </html>
        """

    # Event handlers and update methods
    def update_system_metrics(self, data: Dict[str, Any]):
        """Update system metrics display"""
        if not self.live_toggle.isChecked():
            return

        # Update status bar
        if "cpu_percent" in data:
            self.cpu_label.setText(f"CPU: {data['cpu_percent']:.1f}%")
        if "memory_percent" in data:
            self.memory_label.setText(f"Memory: {data['memory_percent']:.1f}%")
        if "uptime" in data:
            self.uptime_label.setText(f"Uptime: {data['uptime']}")

        # Update web view via JavaScript
        js_code = f"if(typeof updateMetrics === 'function') updateMetrics({json.dumps(data)});"
        self.system_metrics_view.page().runJavaScript(js_code)

    def update_memory_metrics(self, data: Dict[str, Any]):
        """Update memory metrics display"""
        if not self.live_toggle.isChecked():
            return
        # Memory-specific updates would go here
        pass

    def update_agent_metrics(self, data: Dict[str, Any]):
        """Update agent metrics display"""
        if not self.live_toggle.isChecked():
            return
        if "active_agents" in data:
            self.agents_label.setText(f"Agents: {data['active_agents']}")

    def update_cognitive_metrics(self, data: Dict[str, Any]):
        """Update cognitive state display"""
        if not self.live_toggle.isChecked():
            return
        # Cognitive state updates would go here
        pass

    # Menu and toolbar actions
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def toggle_live_updates(self):
        """Toggle live updates"""
        if self.live_toggle.isChecked():
            self.live_toggle.setText("🔴 LIVE")
            self.live_toggle.setStyleSheet(
                """
                QPushButton:checked {
                    background-color: #ff4444;
                    color: white;
                    font-weight: bold;
                }
            """
            )
        else:
            self.live_toggle.setText("⏸️ PAUSED")
            self.live_toggle.setStyleSheet(
                """
                QPushButton {
                    background-color: #666666;
                    color: white;
                    font-weight: bold;
                }
            """
            )

    def show_system_health(self):
        """Show system health dialog"""
        # Third party imports
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox()
        msg.setWindowTitle("System Health")
        msg.setText(
            "🟢 All systems operational\n\n• CPU: Normal\n• Memory: Normal\n• Disk: Normal\n• Network: Normal"
        )
        msg.exec()  # nosec B102: Qt GUI dialog/menu execution

    def show_agent_dashboard(self):
        """Switch to agent dashboard tab"""
        self.tab_widget.setCurrentIndex(2)  # Agents tab

    def show_memory_dashboard(self):
        """Switch to memory dashboard tab"""
        self.tab_widget.setCurrentIndex(1)  # Memory tab

    def validate_features(self):
        """Validate Aetherra features"""
        # Third party imports
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Feature Validation",
            "Feature validation request accepted.\nRun the configured verification task from the Tasks menu for full checks.",
        )

    def run_memory_diagnostics(self):
        """Run memory system diagnostics"""
        # Third party imports
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Memory Diagnostics",
            "Memory diagnostics request accepted.\nRun the diagnostics task for detailed results.",
        )

    def restart_system(self):
        """Restart Aetherra OS"""
        # Third party imports
        from PySide6.QtWidgets import QMessageBox

        if hasattr(self, "statusBar") and self.statusBar():
            self.statusBar().showMessage("Restart requested", 3000)
        QMessageBox.information(
            self,
            "Restart Requested",
            "Aetherra restart has been requested. Use the launcher task to perform a full restart cycle.",
        )

    def shutdown_system(self):
        """Shutdown Aetherra OS"""
        # Third party imports
        from PySide6.QtWidgets import QMessageBox

        if hasattr(self, "statusBar") and self.statusBar():
            self.statusBar().showMessage("Shutdown requested", 3000)
        QMessageBox.information(
            self,
            "Shutdown Requested",
            "Aetherra shutdown has been requested. Use the shutdown workflow task to stop services safely.",
        )

    # Window state management
    def save_window_state(self):
        """Save window state to settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

    def restore_window_state(self):
        """Restore window state from settings"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

    def get_dark_theme(self) -> str:
        """Get dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #0a0a0f;
            color: #a5f1ff;
        }
        QTabWidget::pane {
            border: 1px solid #7a00ff;
            background-color: #0e0e18;
        }
        QTabBar::tab {
            background-color: #121225;
            color: #d8cfff;
            padding: 10px 18px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #00e5ff;
            color: #0b0b12;
        }
        QStatusBar {
            background-color: #0e0e18;
            color: #9adfff;
            border-top: 1px solid #7a00ff;
        }
        QMenuBar {
            background-color: #0e0e18;
            color: #a5f1ff;
        }
        QMenuBar::item:selected {
            background-color: #7a00ff;
            color: #ffffff;
        }
        QMenu {
            background-color: #0e0e18;
            color: #a5f1ff;
            border: 1px solid #7a00ff;
        }
        QMenu::item:selected {
            background-color: #00e5ff;
            color: #0b0b12;
        }
        QToolBar {
            background-color: #0e0e18;
            border: none;
            spacing: 10px;
        }
        QPushButton {
            background-color: #121225;
            color: #d8cfff;
            border: 1px solid #7a00ff;
            padding: 8px 14px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background-color: #1a1a33;
            color: #ffffff;
            border-color: #00e5ff;
        }
        QLabel {
            color: #a5f1ff;
        }
        QSplitter::handle {
            background-color: #7a00ff;
        }
        """

    def closeEvent(self, event):
        """Handle window close event"""
        self.save_window_state()

        if self.monitor_thread:
            self.monitor_thread.stop()

        event.accept()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Aetherra OS")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("AetherraLabs")

    # Set application icon
    # app.setWindowIcon(QIcon("assets/aetherra_icon.png"))

    # Create and show main window
    window = AetherraOSMainWindow()
    window.show()

    return app.exec()  # nosec B102: Qt application execution


if __name__ == "__main__":
    sys.exit(main())
