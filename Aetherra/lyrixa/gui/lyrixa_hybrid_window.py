#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

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

import contextlib
import logging
import threading
import time
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict

logger = logging.getLogger(__name__)

if TYPE_CHECKING:  # Hints only
    from PySide6.QtCore import QTimer, QUrl  # pragma: no cover
    from PySide6.QtWebEngineWidgets import QWebEngineView  # pragma: no cover
    from PySide6.QtWidgets import (  # pragma: no cover
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

try:  # Runtime import (optional)
    from PySide6.QtCore import QTimer, QUrl  # type: ignore
    from PySide6.QtWidgets import (  # type: ignore
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView  # type: ignore

        WEBENGINE_AVAILABLE = True
    except ImportError:
        QWebEngineView = None  # type: ignore
        WEBENGINE_AVAILABLE = False
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    WEBENGINE_AVAILABLE = False
    logger.warning("PySide6 not available - GUI features will be limited")

# Check for Flask availability (optional web backend)
try:  # pragma: no cover - network/server side effects
    from flask import Flask, jsonify, render_template  # type: ignore
    from flask_socketio import SocketIO, emit  # type: ignore

    FLASK_AVAILABLE = True
except ImportError:  # Provide harmless placeholders
    FLASK_AVAILABLE = False
    Flask = None  # type: ignore
    SocketIO = None  # type: ignore

    def _noop(*_a, **_k):  # type: ignore
        return ""

    jsonify = render_template = emit = _noop  # type: ignore
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
        """Run the Flask web server (only if Flask available)."""
        if not FLASK_AVAILABLE:
            logger.error("Cannot start web server - Flask not installed")
            return
        # Create Flask app
        self.app = Flask(  # type: ignore[operator]
            __name__,
            template_folder=str(Path(__file__).parent / "web_templates"),
            static_folder=str(Path(__file__).parent / "web_static"),
        )
        # Create SocketIO for real-time communication
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")  # type: ignore[misc]

        # Routes
        @self.app.route("/")
        def index():  # type: ignore[no-redef]
            return render_template("lyrixa_main.html")  # type: ignore[misc]

        @self.app.route("/api/status")
        def api_status():  # type: ignore[no-redef]
            return jsonify(self.lyrixa_data)  # type: ignore[misc]

        @self.socketio.on("connect")  # type: ignore[attr-defined]
        def handle_connect():  # type: ignore[no-redef]
            logger.info("Web client connected")
            emit("lyrixa_data", self.lyrixa_data)  # type: ignore[misc]

        @self.socketio.on("disconnect")  # type: ignore[attr-defined]
        def handle_disconnect():  # type: ignore[no-redef]
            logger.info("Web client disconnected")

        # Start server
        try:  # pragma: no cover - network side effects
            logger.info(f"Starting Lyrixa web server on port {self.port}")
            self.socketio.run(  # type: ignore[func-returns-value]
                self.app,
                host="localhost",
                port=self.port,
                debug=False,
                allow_unsafe_werkzeug=True,
            )
        except Exception as e:  # pragma: no cover
            logger.error(f"Web server error: {e}")

    def update_data(self, data: Dict[str, Any]):
        """Update data and broadcast to web clients."""
        self.lyrixa_data.update(data)
        if self.socketio:
            self.socketio.emit("lyrixa_data", self.lyrixa_data)

    def isRunning(self):
        """Check if server is running."""
        return self.running

    def terminate(self):
        """Terminate the server."""
        self.running = False
        # Best-effort join; the underlying Werkzeug server may not exit immediately
        if (
            self.server_thread and self.server_thread.is_alive()
        ):  # pragma: no cover - timing dependent
            with contextlib.suppress(Exception):  # pragma: no cover - best effort
                self.server_thread.join(timeout=2)


if PYSIDE6_AVAILABLE:

    class LyrixaHybridWindow(QMainWindow):
        """Hybrid Lyrixa GUI combining Qt widgets and an embedded web backend."""

        def __init__(self):
            super().__init__()
            # Backend connections (provided later by launcher)
            self.service_registry = None
            self.plugin_manager = None
            self.lyrixa_engine = None
            self.memory_system = None
            self.agent_orchestrator = None
            # Web server bridge
            self.web_server = LyrixaWebServer()
            # Build interface
            self.init_ui()
            self.init_web_server()
            self.init_timers()

        # ---------------- UI CONSTRUCTION -----------------
        def init_ui(self):
            self.setWindowTitle("🎙️ Lyrixa AI Operating System - Hybrid Interface")
            self.setGeometry(100, 100, 1400, 900)
            self.setStyleSheet(
                """
                QMainWindow { background-color: #0d1117; color: #f0f6fc; }
                QTabWidget::pane { border: 1px solid #30363d; background-color: #161b22; }
                QTabBar::tab { background-color: #21262d; color: #f0f6fc; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
                QTabBar::tab:selected { background-color: #0969da; }
                QTextEdit { background-color: #0d1117; border: 1px solid #30363d; color: #f0f6fc; font-family: 'Consolas','Monaco',monospace; font-size: 12px; }
                QPushButton { background-color: #238636; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; }
                QPushButton:hover { background-color: #2ea043; }
                QLabel { color: #f0f6fc; }
                """
            )
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.addWidget(self.create_header())
            self.tab_widget = QTabWidget()
            layout.addWidget(self.tab_widget)
            self.create_overview_tab()
            self.create_hybrid_web_tab()
            self.create_system_monitor_tab()
            self.create_console_tab()

        def create_header(self):
            frame = QFrame()
            frame.setFixedHeight(80)
            frame.setStyleSheet(
                "QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1f6feb, stop:1 #0969da); border-radius:8px; margin:5px; }"
            )
            hl = QHBoxLayout(frame)
            title = QLabel("🎙️ LYRIXA AI OPERATING SYSTEM")
            title.setStyleSheet("font-size:24px; font-weight:bold; color:white; margin:10px;")
            hl.addWidget(title)
            hl.addStretch()
            self.status_label = QLabel("🌟 Systems Online")
            self.status_label.setStyleSheet("font-size:14px; color:#26d0ce; margin:10px;")
            hl.addWidget(self.status_label)
            return frame

        def create_overview_tab(self):
            tab = QWidget()
            v = QVBoxLayout(tab)
            self.status_display = QTextEdit()
            self.status_display.setReadOnly(True)
            v.addWidget(self.status_display)
            buttons = QHBoxLayout()
            btn_refresh = QPushButton("🔄 Refresh Status")
            btn_refresh.clicked.connect(self.refresh_system_status)
            buttons.addWidget(btn_refresh)
            btn_web = QPushButton("🌐 Open Web Interface")
            btn_web.clicked.connect(self.open_web_interface)
            buttons.addWidget(btn_web)
            btn_plugins = QPushButton("🔌 Manage Plugins")
            btn_plugins.clicked.connect(self.show_plugins)
            buttons.addWidget(btn_plugins)
            v.addLayout(buttons)
            self.tab_widget.addTab(tab, "📊 Overview")

        def create_hybrid_web_tab(self):
            tab = QWidget()
            v = QVBoxLayout(tab)
            if QWebEngineView:
                try:  # pragma: no cover - GUI path
                    self.web_view = QWebEngineView()
                    v.addWidget(self.web_view)
                    self.web_ready = False
                except Exception as e:  # pragma: no cover
                    fb = QLabel(f"WebEngine error: {e}")
                    v.addWidget(fb)
            else:
                fb = QLabel("Web engine unavailable")
                v.addWidget(fb)
            self.tab_widget.addTab(tab, "🌐 Web Interface")

        def create_system_monitor_tab(self):
            tab = QWidget()
            v = QVBoxLayout(tab)
            self.metrics_display = QTextEdit()
            self.metrics_display.setReadOnly(True)
            v.addWidget(self.metrics_display)
            self.tab_widget.addTab(tab, "📈 System Monitor")

        def create_console_tab(self):
            tab = QWidget()
            v = QVBoxLayout(tab)
            self.console_output = QTextEdit()
            self.console_output.setReadOnly(True)
            self.console_output.setStyleSheet(
                "QTextEdit { background-color:#0d1117; color:#26d0ce; font-family:'Consolas','Monaco',monospace; font-size:11px; }"
            )
            v.addWidget(self.console_output)
            self.tab_widget.addTab(tab, "💻 Console")

        # ---------------- BACKEND INTEGRATION -----------------
        def init_web_server(self):
            if FLASK_AVAILABLE:
                self.web_server.start()
            else:
                logger.warning("Flask not available - web features disabled")

        def init_timers(self):
            self.status_timer = QTimer()
            self.status_timer.timeout.connect(self.refresh_system_status)
            self.status_timer.start(5000)
            self.web_timer = QTimer()
            self.web_timer.timeout.connect(self.check_web_ready)
            self.web_timer.start(2000)

        def check_web_ready(self):
            if hasattr(self, "web_view") and not getattr(self, "web_ready", True):
                try:  # pragma: no cover - GUI path
                    self.web_view.load(QUrl("http://localhost:8787"))
                    self.web_ready = True
                    self.web_timer.stop()
                except Exception:  # pragma: no cover
                    pass

        def refresh_system_status(self):
            status_text = [
                "🌟 LYRIXA AI OPERATING SYSTEM STATUS",
                "=" * 50,
                "",
                f"📡 Service Registry: {'✅ Online' if self.service_registry else '❌ Offline'}",
                f"🔌 Plugin Manager: {'✅ Active' if self.plugin_manager else '❌ Inactive'}",
                f"🎙️ Lyrixa Engine: {'✅ Running' if self.lyrixa_engine else '❌ Stopped'}",
                f"🧠 Memory System: {'✅ Active' if self.memory_system else '❌ Inactive'}",
                f"🤖 Agent Orchestrator: {'✅ Ready' if self.agent_orchestrator else '❌ Not Ready'}",
                "",
            ]
            web_status = "✅ Online" if self.web_server.isRunning() else "❌ Offline"
            status_text.append(f"🌐 Web Server: {web_status} (http://localhost:8787)")
            status_text.append("")
            status_text.append(f"⏰ Last updated: {time.strftime('%H:%M:%S')}")
            text_blob = "\n".join(status_text)
            if hasattr(self, "status_display"):
                self.status_display.setPlainText(text_blob)
            if hasattr(self, "console_output"):
                self.console_output.append(f"[{time.strftime('%H:%M:%S')}] Status refreshed")
            self.web_server.update_data(
                {
                    "timestamp": time.time(),
                    "service_registry": bool(self.service_registry),
                    "plugin_manager": bool(self.plugin_manager),
                    "lyrixa_engine": bool(self.lyrixa_engine),
                    "memory_system": bool(self.memory_system),
                    "agent_orchestrator": bool(self.agent_orchestrator),
                    "web_server_running": self.web_server.isRunning(),
                }
            )

        # ---------------- USER ACTIONS -----------------
        def open_web_interface(self):
            webbrowser.open("http://localhost:8787")

        def show_plugins(self):
            if self.plugin_manager and hasattr(self, "console_output"):
                self.console_output.append("Plugin manager active")
            elif hasattr(self, "console_output"):
                self.console_output.append("Plugin manager not available")

        # ---------------- BACKEND SETTERS -----------------
        def set_service_registry(self, service_registry):
            self.service_registry = service_registry

        def set_plugin_manager(self, plugin_manager):
            self.plugin_manager = plugin_manager

        def set_lyrixa_engine(self, lyrixa_engine):
            self.lyrixa_engine = lyrixa_engine

        def set_memory_system(self, memory_system):
            self.memory_system = memory_system

        def set_agent_orchestrator(self, agent_orchestrator):
            self.agent_orchestrator = agent_orchestrator

        # ---------------- EVENTS -----------------
        def closeEvent(self, event):  # noqa: N802
            if self.web_server.isRunning():  # pragma: no branch - simple guard
                self.web_server.terminate()
                with contextlib.suppress(Exception):  # pragma: no cover - best effort
                    # If web_server provided a wait method (future extension)
                    self.web_server.wait(3000)  # type: ignore[attr-defined]
            event.accept()
else:

    class _LyrixaHybridWindowStub:  # pragma: no cover - executed only without PySide6
        """Fallback stub when PySide6 isn't installed."""

        def __init__(self):  # noqa: D401
            raise RuntimeError("PySide6 not available; GUI not supported in this environment")

    LyrixaHybridWindow = _LyrixaHybridWindowStub  # type: ignore
# Export the main window class
__all__ = ["LyrixaHybridWindow"]
