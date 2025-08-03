#!/usr/bin/env python3
"""
🎙️ Lyrixa Hybrid Window - Phase 1
==================================

PySide6 + Embedded Web Hybrid UI for Lyrixa AI Operating System
Combines native Qt performance with beautiful web-styled panels
matching the Aetherra.dev aesthetic.

Architecture:
- Base: PySide6 QMainWindow for native performance
- Panels: QWebEngineView embedding HTML panels styled like Aetherra.dev
- Communication: QWebChannel for bidirectional Python ↔ JavaScript
- Styling: Authentic Aetherra colors and effects
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QSplitter, QPushButton, QLabel, QFrame, QMenuBar,
    QStatusBar, QSystemTrayIcon, QMenu
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import QObject, QUrl, Slot, Qt, QTimer, Signal
from PySide6.QtGui import QIcon, QFont, QPalette, QColor
from PySide6.QtCore import QTimer
import psutil
import os

class LyrixaContextBridge(QObject):
    """
    🌉 Phase 2: Live Context Bridge
    ===============================

    Real-time bidirectional communication bridge between Python backend
    and embedded web panels. Handles:
    - Memory stats and updates
    - Plugin status and controls
    - Agent goals and thoughts
    - System metrics and notifications
    """

    # Signals for sending data to web panels
    memory_updated = Signal(str)      # Memory system updates
    plugin_updated = Signal(str)      # Plugin status changes
    agent_updated = Signal(str)       # Agent thoughts/goals
    metrics_updated = Signal(str)     # System metrics
    notification_sent = Signal(str)   # System notifications

    def __init__(self):
        super().__init__()
        self.data_cache = {
            'memory': {},
            'plugins': {},
            'agents': {},
            'metrics': {},
            'system': {}
        }
        self.backend_services = {}

        # Start periodic updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.refresh_all_data)
        self.update_timer.start(2000)  # Update every 2 seconds

    # === SLOT METHODS (Called from JavaScript) ===

    @Slot(str)
    def handlePanelCommand(self, command_json):
        """Handle commands from web panels."""
        try:
            command = json.loads(command_json)
            command_type = command.get('type')
            payload = command.get('payload', {})

            print(f"🎛️ Panel command: {command_type} | {payload}")

            if command_type == 'plugin_action':
                self.handle_plugin_command(payload)
            elif command_type == 'memory_query':
                self.handle_memory_command(payload)
            elif command_type == 'agent_command':
                self.handle_agent_command(payload)
            elif command_type == 'system_command':
                self.handle_system_command(payload)
            else:
                print(f"[WARN] Unknown command type: {command_type}")

        except Exception as e:
            print(f"❌ Error handling panel command: {e}")
            self.send_notification('error', f"Command failed: {e}")

    @Slot(str, result=str)
    def getData(self, category):
        """Get cached data for specific category."""
        data = self.data_cache.get(category, {})
        return json.dumps(data)

    @Slot(result=str)
    def getAllData(self):
        """Get all cached data for initial panel load."""
        return json.dumps(self.data_cache)

    # === BACKEND INTEGRATION ===

    def connect_backend_services(self, services: Dict[str, Any]):
        """Connect to backend services (memory, plugins, agents, etc.)"""
        self.backend_services = services
        print(f"🔗 Connected to {len(services)} backend services")
        self.refresh_all_data()

    def refresh_all_data(self):
        """Refresh data from all backend services."""
        try:
            self.refresh_memory_data()
            self.refresh_plugin_data()
            self.refresh_agent_data()
            self.refresh_metrics_data()
        except Exception as e:
            print(f"[WARN] Error refreshing data: {e}")

    def refresh_memory_data(self):
        """Refresh memory system data."""
        memory_system = self.backend_services.get('memory_system')
        if memory_system:
            try:
                # Gather memory stats
                memory_data = {
                    'total_memories': getattr(memory_system, 'total_memories', 0),
                    'recent_memories': getattr(memory_system, 'recent_count', 0),
                    'memory_load': 45,  # Placeholder - replace with actual metric
                    'last_updated': QTimer().remainingTime(),
                    'status': 'active'
                }

                if memory_data != self.data_cache['memory']:
                    self.data_cache['memory'] = memory_data
                    self.memory_updated.emit(json.dumps(memory_data))

            except Exception as e:
                print(f"[WARN] Memory data refresh error: {e}")

    def refresh_plugin_data(self):
        """Refresh plugin manager data."""
        plugin_manager = self.backend_services.get('plugin_manager')
        if plugin_manager:
            try:
                # Get plugin status from manager
                plugins_data = {
                    'loaded_plugins': [],
                    'active_count': 0,
                    'total_count': 0,
                    'status': 'operational'
                }

                # Try to get actual plugin info
                if hasattr(plugin_manager, 'get_all_plugins'):
                    plugins_info = plugin_manager.get_all_plugins()
                    plugins_data['loaded_plugins'] = [
                        {
                            'name': name,
                            'status': 'active' if info.get('loaded') else 'loaded',
                            'version': info.get('version', '1.0.0')
                        }
                        for name, info in plugins_info.items()
                    ]
                    plugins_data['total_count'] = len(plugins_info)
                    plugins_data['active_count'] = sum(1 for info in plugins_info.values() if info.get('loaded'))

                if plugins_data != self.data_cache['plugins']:
                    self.data_cache['plugins'] = plugins_data
                    self.plugin_updated.emit(json.dumps(plugins_data))

            except Exception as e:
                print(f"[WARN] Plugin data refresh error: {e}")

    def refresh_agent_data(self):
        """Refresh agent orchestrator data."""
        agent_orchestrator = self.backend_services.get('agent_orchestrator')
        if agent_orchestrator:
            try:
                agents_data = {
                    'active_agents': 0,
                    'current_goals': [],
                    'recent_thoughts': [],
                    'status': 'thinking'
                }

                # Try to get actual agent info
                if hasattr(agent_orchestrator, 'agents'):
                    agents_data['active_agents'] = len(agent_orchestrator.agents)

                if hasattr(agent_orchestrator, 'current_goals'):
                    agents_data['current_goals'] = agent_orchestrator.current_goals[:5]  # Last 5

                if agents_data != self.data_cache['agents']:
                    self.data_cache['agents'] = agents_data
                    self.agent_updated.emit(json.dumps(agents_data))

            except Exception as e:
                print(f"[WARN] Agent data refresh error: {e}")

    def refresh_metrics_data(self):
        """Refresh system metrics."""
        import psutil
        import os
        import time

        try:
            metrics_data = {
                'cpu_usage': psutil.cpu_percent(interval=0.1),
                'memory_usage': psutil.virtual_memory().percent,
                'process_count': len(psutil.pids()),
                'uptime': time.time() % 86400,  # Seconds since midnight
                'timestamp': int(time.time())
            }

            if metrics_data != self.data_cache['metrics']:
                self.data_cache['metrics'] = metrics_data
                self.metrics_updated.emit(json.dumps(metrics_data))

        except Exception as e:
            print(f"[WARN] Metrics refresh error: {e}")

    # === COMMAND HANDLERS ===

    def handle_plugin_command(self, payload):
        """Handle plugin-related commands."""
        action = payload.get('action')
        plugin_name = payload.get('plugin')

        print(f"🔌 Plugin command: {action} on {plugin_name}")

        plugin_manager = self.backend_services.get('plugin_manager')
        if not plugin_manager:
            self.send_notification('error', 'Plugin manager not available')
            return

        if action == 'activate':
            # TODO: Activate plugin
            self.send_notification('success', f'Activated plugin: {plugin_name}')
        elif action == 'deactivate':
            # TODO: Deactivate plugin
            self.send_notification('success', f'Deactivated plugin: {plugin_name}')
        elif action == 'reload':
            # TODO: Reload plugin
            self.send_notification('success', f'Reloaded plugin: {plugin_name}')
        else:
            self.send_notification('warning', f'Unknown plugin action: {action}')

    def handle_memory_command(self, payload):
        """Handle memory-related commands."""
        action = payload.get('action')
        query = payload.get('query', '')

        print(f"🧠 Memory command: {action} | {query}")

        memory_system = self.backend_services.get('memory_system')
        if not memory_system:
            self.send_notification('error', 'Memory system not available')
            return

        if action == 'search':
            # TODO: Search memory
            self.send_notification('info', f'Searching memory for: {query}')
        elif action == 'clear':
            # TODO: Clear memory
            self.send_notification('warning', 'Memory cleared')
        else:
            self.send_notification('warning', f'Unknown memory action: {action}')

    def handle_agent_command(self, payload):
        """Handle agent-related commands."""
        action = payload.get('action')
        goal = payload.get('goal', '')

        print(f"🤖 Agent command: {action} | {goal}")

        agent_orchestrator = self.backend_services.get('agent_orchestrator')
        if not agent_orchestrator:
            self.send_notification('error', 'Agent orchestrator not available')
            return

        if action == 'add_goal':
            # TODO: Add goal to agent
            self.send_notification('success', f'Added goal: {goal}')
        elif action == 'pause':
            # TODO: Pause agents
            self.send_notification('info', 'Agents paused')
        elif action == 'resume':
            # TODO: Resume agents
            self.send_notification('info', 'Agents resumed')
        else:
            self.send_notification('warning', f'Unknown agent action: {action}')

    def handle_system_command(self, payload):
        """Handle system-level commands."""
        action = payload.get('action')

        print(f"⚙️ System command: {action}")

        if action == 'refresh':
            self.refresh_all_data()
            self.send_notification('info', 'System data refreshed')
        elif action == 'status':
            self.send_system_status()
        else:
            self.send_notification('warning', f'Unknown system action: {action}')

    # === NOTIFICATION SYSTEM ===

    def send_notification(self, level: str, message: str):
        """Send notification to web panels."""
        notification = {
            'level': level,  # info, success, warning, error
            'message': message,
            'timestamp': QTimer().remainingTime()
        }
        self.notification_sent.emit(json.dumps(notification))

    def send_system_status(self):
        """Send comprehensive system status."""
        status = {
            'backend_connected': len(self.backend_services) > 0,
            'services': list(self.backend_services.keys()),
            'data_categories': list(self.data_cache.keys()),
            'update_frequency': '2 seconds',
            'bridge_active': True
        }
        self.send_notification('info', f'System status: {len(self.backend_services)} services connected')


# Maintain backward compatibility
LyrixaWebBridge = LyrixaContextBridge


class LyrixaHybridWindow(QMainWindow):
    """
    🎙️ Lyrixa Hybrid Window - PySide6 + Web Panel Integration

    Features:
    - Native Qt controls for performance-critical operations
    - Beautiful web panels matching Aetherra.dev styling
    - Dynamic panel loading and switching
    - Real-time data synchronization
    """

    def __init__(self):
        super().__init__()
        self.web_bridge = LyrixaWebBridge()
        self.web_panels = {}
        self.current_panel = None

        # Backend connections (will be set by launcher)
        self.service_registry = None
        self.plugin_manager = None
        self.lyrixa_engine = None
        self.memory_system = None
        self.agent_orchestrator = None

        self.setupUI()
        self.setupWebChannel()
        self.setupTimers()
        self.applyAetherraTheme()

    def setupUI(self):
        """Setup the main UI structure."""
        self.setWindowTitle("🎙️ Lyrixa AI Operating System")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Native controls
        self.left_panel = self.createLeftPanel()
        splitter.addWidget(self.left_panel)

        # Center panel - Web view
        self.center_panel = self.createCenterPanel()
        splitter.addWidget(self.center_panel)

        # Right panel - Status and metrics
        self.right_panel = self.createRightPanel()
        splitter.addWidget(self.right_panel)

        # Set splitter proportions (20% : 60% : 20%)
        splitter.setSizes([280, 840, 280])

        # Menu bar
        self.createMenuBar()

        # Status bar
        self.createStatusBar()

        # Load default panel
        self.loadPanel('dashboard')

    def createLeftPanel(self) -> QWidget:
        """Create the left native control panel."""
        panel = QFrame()
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)

        # Title
        title = QLabel("🎙️ LYRIXA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #00ff88;
                padding: 20px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Navigation buttons
        nav_buttons = [
            ("🧠 Neural Interface", "dashboard"),
            ("🔌 Plugin Manager", "plugins"),
            ("📈 Metrics", "metrics"),
            ("💭 Memory", "memory"),
            ("⚙️ Settings", "settings")
        ]

        for text, panel_id in nav_buttons:
            btn = QPushButton(text)
            btn.setObjectName(f"nav_{panel_id}")
            btn.clicked.connect(lambda checked, pid=panel_id: self.loadPanel(pid))
            btn.setStyleSheet(self.getButtonStyle())
            layout.addWidget(btn)

        # Spacer
        layout.addStretch()

        # System status
        status_frame = QFrame()
        status_layout = QVBoxLayout(status_frame)

        self.status_label = QLabel("🌟 All Systems Online")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-weight: bold;
                padding: 10px;
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
            }
        """)
        status_layout.addWidget(self.status_label)

        layout.addWidget(status_frame)

        return panel

    def createCenterPanel(self) -> QWidget:
        """Create the center web panel area."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Web engine view
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        return panel

    def createRightPanel(self) -> QWidget:
        """Create the right metrics/status panel."""
        panel = QFrame()
        panel.setFixedWidth(280)
        layout = QVBoxLayout(panel)

        # Quick stats
        stats_title = QLabel("📊 Live Metrics")
        stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #00ff88;
                padding: 15px;
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(stats_title)

        # Metrics widgets
        self.metrics_widgets = {}
        metrics = [
            ("Memory Load", "45%", "#00ff88"),
            ("CPU Usage", "23%", "#0078d4"),
            ("Agents Active", "7", "#ff6b00"),
            ("Plugins Loaded", "12", "#9d4edd")
        ]

        for name, value, color in metrics:
            metric_widget = self.createMetricWidget(name, value, color)
            layout.addWidget(metric_widget)
            self.metrics_widgets[name] = metric_widget

        layout.addStretch()

        return panel

    def createMetricWidget(self, name: str, value: str, color: str) -> QWidget:
        """Create a metric display widget."""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background: rgba(26, 26, 26, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 10px;
                margin: 5px 0;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 8, 10, 8)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 12px;")

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")

        layout.addWidget(name_label)
        layout.addWidget(value_label)

        return widget

    def createMenuBar(self):
        """Create the menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project")
        file_menu.addAction("&Open Project")
        file_menu.addSeparator()
        file_menu.addAction("E&xit", self.close)

        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("&Dashboard", lambda: self.loadPanel('dashboard'))
        view_menu.addAction("&Plugins", lambda: self.loadPanel('plugins'))
        view_menu.addAction("&Memory", lambda: self.loadPanel('memory'))

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction("&Plugin Manager")
        tools_menu.addAction("&Memory Browser")
        tools_menu.addAction("&System Diagnostics")

    def createStatusBar(self):
        """Create the status bar."""
        status_bar = self.statusBar()
        status_bar.showMessage("🌟 Lyrixa AI Operating System - Ready")
        status_bar.setStyleSheet("""
            QStatusBar {
                background: #1a1a1a;
                color: #00ff88;
                border-top: 1px solid rgba(0, 255, 136, 0.3);
            }
        """)

    def setupWebChannel(self):
        """Setup QWebChannel for Python ↔ JavaScript communication."""
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("pybridge", self.web_bridge)
        self.web_view.page().setWebChannel(self.web_channel)

    def setupTimers(self):
        """Setup periodic timers for live updates."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.updateStatus)
        self.status_timer.start(2000)  # Update every 2 seconds

        # Metrics update timer
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.updateMetrics)
        self.metrics_timer.start(5000)  # Update every 5 seconds

    def loadPanel(self, panel_id: str):
        """Load a specific web panel."""
        try:
            panel_path = Path(__file__).parent / "web_panels" / f"{panel_id}_panel.html"

            if not panel_path.exists():
                # Create default panel if it doesn't exist
                self.createDefaultPanel(panel_id, panel_path)

            self.web_view.load(QUrl.fromLocalFile(str(panel_path.absolute())))
            self.current_panel = panel_id
            self.statusBar().showMessage(f"🌟 Loaded {panel_id.title()} Panel")

        except Exception as e:
            print(f"❌ Error loading panel {panel_id}: {e}")

    def createDefaultPanel(self, panel_id: str, path: Path):
        """Create a default panel if it doesn't exist."""
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>{panel_id.title()} Panel</title>
            <link rel="stylesheet" href="../assets/style.css">
        </head>
        <body>
            <div class="panel-container" data-panel="{panel_id}">
                <div class="panel-header">
                    <h1>🎙️ {panel_id.title()} Panel</h1>
                </div>
                <div class="panel-content">
                    <div class="placeholder">
                        <div class="glow-orb"></div>
                        <p>Panel coming in Phase 2...</p>
                    </div>
                </div>
            </div>
            <script src="../assets/effects.js"></script>
        </body>
        </html>
        '''

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html_content, encoding='utf-8')

    def applyAetherraTheme(self):
        """Apply the Aetherra color scheme and styling."""
        self.setStyleSheet("""
            QMainWindow {
                background: #0a0a0a;
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }

            QFrame {
                background: rgba(26, 26, 26, 0.8);
                border-radius: 8px;
            }

            QMenuBar {
                background: #1a1a1a;
                color: #ffffff;
                border-bottom: 1px solid rgba(0, 255, 136, 0.3);
            }

            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
            }

            QMenuBar::item:selected {
                background: rgba(0, 255, 136, 0.2);
                border-radius: 4px;
            }
        """)

    def getButtonStyle(self) -> str:
        """Get the Aetherra-themed button style."""
        return """
            QPushButton {
                background: rgba(26, 26, 26, 0.8);
                color: #ffffff;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: bold;
                margin: 4px 0;
                text-align: left;
            }

            QPushButton:hover {
                background: rgba(0, 255, 136, 0.1);
                border-color: rgba(0, 255, 136, 0.6);
                box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.2);
            }
        """

    def updateStatus(self):
        """Update system status display."""
        # This will be connected to real backend data in later phases
        if self.service_registry:
            self.status_label.setText("🌟 All Systems Online")
        else:
            self.status_label.setText("[WARN] Connecting...")

    def updateMetrics(self):
        """Update metrics display."""
        # This will be connected to real backend metrics in later phases
        import random

        # Simulate live metrics for now
        metrics_data = {
            "memory_load": random.randint(30, 70),
            "cpu_usage": random.randint(10, 40),
            "agents_active": random.randint(5, 12),
            "plugins_loaded": 12
        }

        # Update web bridge data
        self.web_bridge.data_cache['metrics'] = metrics_data
        self.web_bridge.metrics_updated.emit(json.dumps(metrics_data))

    # Backend connection methods (called by launcher)
    def set_service_registry(self, service_registry):
        """Connect service registry."""
        self.service_registry = service_registry
        self._update_backend_services()

    def set_plugin_manager(self, plugin_manager):
        """Connect plugin manager."""
        self.plugin_manager = plugin_manager
        self._update_backend_services()

    def set_lyrixa_engine(self, lyrixa_engine):
        """Connect Lyrixa engine."""
        self.lyrixa_engine = lyrixa_engine
        self._update_backend_services()

    def set_memory_system(self, memory_system):
        """Connect memory system."""
        self.memory_system = memory_system
        self._update_backend_services()

    def set_agent_orchestrator(self, agent_orchestrator):
        """Connect agent orchestrator."""
        self.agent_orchestrator = agent_orchestrator
        self._update_backend_services()

    def _update_backend_services(self):
        """Update the context bridge with current backend services."""
        services = {}

        if hasattr(self, 'service_registry') and self.service_registry:
            services['service_registry'] = self.service_registry

        if hasattr(self, 'plugin_manager') and self.plugin_manager:
            services['plugin_manager'] = self.plugin_manager

        if hasattr(self, 'lyrixa_engine') and self.lyrixa_engine:
            services['lyrixa_engine'] = self.lyrixa_engine

        if hasattr(self, 'memory_system') and self.memory_system:
            services['memory_system'] = self.memory_system

        if hasattr(self, 'agent_orchestrator') and self.agent_orchestrator:
            services['agent_orchestrator'] = self.agent_orchestrator

        # Connect services to the context bridge
        self.web_bridge.connect_backend_services(services)


def main():
    """Standalone launcher for testing."""
    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Hybrid UI")

    window = LyrixaHybridWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
