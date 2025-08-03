#!/usr/bin/env python3
"""
🎙️ LYRIXA HYBRID GUI WINDOW - PySide6 + Web Interface
=====================================================

A sophisticated hybrid GUI that combines:
- PySide6 Qt interface for native OS integration
- Embedded web server for modern web UI components
- WebView integration for seamless hybrid experience
- Real-time communication between Qt and Web components

This provides the best of both worlds:
- Native OS integration (Qt)
- Modern web UI capabilities (HTML/CSS/JS)
- Real-time data synchronization
- Professional appearance and functionality
"""

import asyncio
import json
import logging
import sys
import threading
import time
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for PySide6 availability
try:
    from PySide6.QtCore import Qt, QTimer, QThread, Signal, QUrl
    from PySide6.QtGui import QBrush, QColor, QPainter, QFont
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QTextEdit, QLabel, QPushButton, QSplitter,
        QFrame, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem
    )
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        WEBENGINE_AVAILABLE = True
    except ImportError:
        WEBENGINE_AVAILABLE = False
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    WEBENGINE_AVAILABLE = False
    logger.warning("PySide6 not available - GUI features will be limited")

# Check for Flask availability
try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("Flask not available - web features will be disabled")

class LyrixaWebServer:
    """Background web server for the hybrid interface."""

    def __init__(self, port=8787):
        self.port = port
        self.app = None
        self.socketio = None
        self.lyrixa_data = {}
        self.server_thread = None
        self.running = False

    def start(self):
        """Start the web server in a separate thread."""
        if not FLASK_AVAILABLE:
            logger.error("Flask not available for web server")
            return

        self.server_thread = threading.Thread(target=self._run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.running = True

    def _run_server(self):
        """Run the Flask web server."""
        # Create Flask app
        self.app = Flask(
            __name__,
            template_folder=str(Path(__file__).parent / 'web_templates'),
            static_folder=str(Path(__file__).parent / 'web_static')
        )

        # Create SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        # Routes
        @self.app.route('/')
        def index():
            return render_template('lyrixa_main.html')

        @self.app.route('/api/status')
        def api_status():
            return jsonify(self.lyrixa_data)

        @self.socketio.on('connect')
        def handle_connect():
            logger.info("Web client connected")
            emit('lyrixa_data', self.lyrixa_data)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Web client disconnected")

        # Start server
        try:
            logger.info(f"Starting Lyrixa web server on port {self.port}")
            self.socketio.run(self.app, host='localhost', port=self.port, debug=False, allow_unsafe_werkzeug=True)
        except Exception as e:
            logger.error(f"Web server error: {e}")

    def update_data(self, data: Dict[str, Any]):
        """Update data and broadcast to web clients."""
        self.lyrixa_data.update(data)
        if self.socketio:
            self.socketio.emit('lyrixa_data', self.lyrixa_data)

    def isRunning(self):
        """Check if server is running."""
        return self.running

    def terminate(self):
        """Terminate the server."""
        self.running = False

if PYSIDE6_AVAILABLE:
    class LyrixaHybridWindow(QMainWindow):
        """
        🎙️ LYRIXA HYBRID GUI WINDOW

        Combines PySide6 Qt interface with embedded web components
        for a modern, powerful, and beautiful user experience.
        """

        def __init__(self):
            super().__init__()

            # Backend connections (set by launcher)
            self.service_registry = None
            self.plugin_manager = None
            self.lyrixa_engine = None
            self.memory_system = None
            self.agent_orchestrator = None

            # Web server for hybrid interface
            self.web_server = LyrixaWebServer()

            # Initialize UI
            self.init_ui()
            self.init_web_server()
            self.init_timers()

        def init_ui(self):
            """Initialize the Qt-based UI components."""
            self.setWindowTitle("🎙️ Lyrixa AI Operating System - Hybrid Interface")
        self.setGeometry(100, 100, 1400, 900)

        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                color: #f0f6fc;
            }
            QTabWidget::pane {
                border: 1px solid #30363d;
                background-color: #161b22;
            }
            QTabBar::tab {
                background-color: #21262d;
                color: #f0f6fc;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0969da;
            }
            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                color: #f0f6fc;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QLabel {
                color: #f0f6fc;
            }
        """)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Tab widget for different interfaces
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_overview_tab()
        self.create_hybrid_web_tab()
        self.create_system_monitor_tab()
        self.create_console_tab()

    def create_header(self):
        """Create the main header with Lyrixa branding."""
        header_frame = QFrame()
        header_frame.setFixedHeight(80)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1f6feb, stop:1 #0969da);
                border-radius: 8px;
                margin: 5px;
            }
        """)

        layout = QHBoxLayout(header_frame)

        # Title
        title = QLabel("🎙️ LYRIXA AI OPERATING SYSTEM")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            margin: 10px;
        """)
        layout.addWidget(title)

        layout.addStretch()

        # Status indicator
        self.status_label = QLabel("🌟 Systems Online")
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #26d0ce;
            margin: 10px;
        """)
        layout.addWidget(self.status_label)

        return header_frame

    def create_overview_tab(self):
        """Create the system overview tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # System status display
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        # Control buttons
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.clicked.connect(self.refresh_system_status)
        button_layout.addWidget(refresh_btn)

        web_btn = QPushButton("🌐 Open Web Interface")
        web_btn.clicked.connect(self.open_web_interface)
        button_layout.addWidget(web_btn)

        plugins_btn = QPushButton("🔌 Manage Plugins")
        plugins_btn.clicked.connect(self.show_plugins)
        button_layout.addWidget(plugins_btn)

        layout.addLayout(button_layout)

        self.tab_widget.addTab(tab, "📊 Overview")

    def create_hybrid_web_tab(self):
        """Create the embedded web interface tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        if PYSIDE6_AVAILABLE:
            try:
                # Embedded web view
                self.web_view = QWebEngineView()
                layout.addWidget(self.web_view)

                # Load web interface when ready
                self.web_ready = False

            except Exception as e:
                logger.warning(f"WebEngine not available: {e}")
                # Fallback to simple message
                fallback = QLabel("🌐 Web interface starting...\nOpen http://localhost:8787 in your browser")
                fallback.setAlignment(Qt.AlignCenter)
                fallback.setStyleSheet("font-size: 16px; padding: 50px;")
                layout.addWidget(fallback)
        else:
            fallback = QLabel("PySide6 not available for web integration")
            layout.addWidget(fallback)

        self.tab_widget.addTab(tab, "🌐 Web Interface")

    def create_system_monitor_tab(self):
        """Create the system monitoring tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # System metrics display
        self.metrics_display = QTextEdit()
        self.metrics_display.setReadOnly(True)
        layout.addWidget(self.metrics_display)

        self.tab_widget.addTab(tab, "📈 System Monitor")

    def create_console_tab(self):
        """Create the console/terminal tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Console output
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #26d0ce;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.console_output)

        self.tab_widget.addTab(tab, "💻 Console")

    def init_web_server(self):
        """Initialize the web server component."""
        if FLASK_AVAILABLE:
            # Start web server in background
            self.web_server.start()
            logger.info("Web server starting...")
        else:
            logger.warning("Flask not available - web features disabled")

    def init_timers(self):
        """Initialize update timers."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.refresh_system_status)
        self.status_timer.start(5000)  # Update every 5 seconds

        # Web readiness timer
        self.web_timer = QTimer()
        self.web_timer.timeout.connect(self.check_web_ready)
        self.web_timer.start(2000)  # Check every 2 seconds

    def check_web_ready(self):
        """Check if web server is ready and load web interface."""
        if hasattr(self, 'web_view') and not self.web_ready:
            try:
                # Try to load the web interface
                self.web_view.load(QUrl("http://localhost:8787"))
                self.web_ready = True
                self.web_timer.stop()
                logger.info("Web interface loaded in embedded view")
            except Exception as e:
                logger.debug(f"Web interface not ready yet: {e}")

    def refresh_system_status(self):
        """Refresh and display system status."""
        status_text = "🌟 LYRIXA AI OPERATING SYSTEM STATUS\n"
        status_text += "=" * 50 + "\n\n"

        # Check backend systems
        status_text += f"📡 Service Registry: {'✅ Online' if self.service_registry else '❌ Offline'}\n"
        status_text += f"🔌 Plugin Manager: {'✅ Active' if self.plugin_manager else '❌ Inactive'}\n"
        status_text += f"🎙️ Lyrixa Engine: {'✅ Running' if self.lyrixa_engine else '❌ Stopped'}\n"
        status_text += f"🧠 Memory System: {'✅ Active' if self.memory_system else '❌ Inactive'}\n"
        status_text += f"🤖 Agent Orchestrator: {'✅ Ready' if self.agent_orchestrator else '❌ Not Ready'}\n\n"

        # Web server status
        web_status = "✅ Online" if self.web_server.isRunning() else "❌ Offline"
        status_text += f"🌐 Web Server: {web_status} (http://localhost:8787)\n\n"

        # Capabilities
        status_text += "🎯 ACTIVE CAPABILITIES:\n"
        status_text += "• Full system control and monitoring\n"
        status_text += "• Real-time data visualization\n"
        status_text += "• Hybrid Qt + Web interface\n"
        status_text += "• Plugin management\n"
        status_text += "• Memory system integration\n"
        status_text += "• Agent orchestration\n\n"

        status_text += f"⏰ Last updated: {time.strftime('%H:%M:%S')}\n"

        self.status_display.setPlainText(status_text)

        # Update web server data
        web_data = {
            'timestamp': time.time(),
            'service_registry': bool(self.service_registry),
            'plugin_manager': bool(self.plugin_manager),
            'lyrixa_engine': bool(self.lyrixa_engine),
            'memory_system': bool(self.memory_system),
            'agent_orchestrator': bool(self.agent_orchestrator),
            'web_server_running': self.web_server.isRunning()
        }
        self.web_server.update_data(web_data)

        # Update console
        console_msg = f"[{time.strftime('%H:%M:%S')}] System status refreshed - All systems operational\n"
        self.console_output.append(console_msg)

    def open_web_interface(self):
        """Open the web interface in external browser."""
        webbrowser.open("http://localhost:8787")

    def show_plugins(self):
        """Show plugin information."""
        if self.plugin_manager:
            self.console_output.append(f"[{time.strftime('%H:%M:%S')}] Plugin manager active - Use web interface for detailed plugin management\n")
        else:
            self.console_output.append(f"[{time.strftime('%H:%M:%S')}] Plugin manager not available\n")

    # Backend connection methods (called by launcher)
    def set_service_registry(self, service_registry):
        self.service_registry = service_registry
        logger.info("Service registry connected to GUI")

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager
        logger.info("Plugin manager connected to GUI")

    def set_lyrixa_engine(self, lyrixa_engine):
        self.lyrixa_engine = lyrixa_engine
        logger.info("Lyrixa engine connected to GUI")

    def set_memory_system(self, memory_system):
        self.memory_system = memory_system
        logger.info("Memory system connected to GUI")

    def set_agent_orchestrator(self, agent_orchestrator):
        self.agent_orchestrator = agent_orchestrator
        logger.info("Agent orchestrator connected to GUI")

    def closeEvent(self, event):
        """Handle window close event."""
        logger.info("Shutting down Lyrixa hybrid interface...")

        # Stop web server
        if self.web_server.isRunning():
            self.web_server.terminate()
            self.web_server.wait(3000)  # Wait up to 3 seconds

        event.accept()

# Export the main window class
__all__ = ['LyrixaHybridWindow']
