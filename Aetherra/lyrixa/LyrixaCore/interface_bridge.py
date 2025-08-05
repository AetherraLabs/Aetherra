# Clean Architecture Imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from integration.bridges.aetherra_lyrixa_bridge import bridge

from web.server.web_adapter import web_adapter

"""
Qt Web Bridge for Lyrixa Interface
Handles communication between Qt application and web interface
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget


class LyrixaWebBridge(QObject):
    """Bridge class for Qt-Web communication"""

    # Signals for web->Qt communication
    message_received = Signal(str)
    data_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)

    @Slot(str)
    def send_message(self, message: str):
        """Receive message from web interface"""
        self.logger.debug(f"Received message from web: {message}")
        self.message_received.emit(message)

    @Slot(str)
    def request_data(self, data_type: str):
        """Handle data requests from web interface"""
        self.logger.debug(f"Data requested: {data_type}")
        self.data_requested.emit(data_type)

    @Slot(str, str)
    def log_message(self, level: str, message: str):
        """Log messages from web interface"""
        log_level = getattr(logging, level.upper(), logging.INFO)
        self.logger.log(log_level, f"Web: {message}")


class LyrixaWebView(QWidget):
    """Web view widget for embedding Lyrixa web interface"""

    # Signals for communication with main application
    chat_message_sent = Signal(str)
    web_ready = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.setup_ui()
        self.setup_web_channel()

    def setup_ui(self):
        """Setup the web view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web engine view
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("""
            QWebEngineView {
                background: #0a0a0a;
                border: none;
            }
        """)

        layout.addWidget(self.web_view)

        # Load the web interface
        self.load_web_interface()

    def setup_web_channel(self):
        """Setup Qt WebChannel for communication"""
        self.web_channel = QWebChannel()
        self.bridge = LyrixaWebBridge(self)

        # Connect bridge signals
        self.bridge.message_received.connect(self.handle_web_message)

        # Register bridge object
        self.web_channel.registerObject("bridge", self.bridge)
        self.web_view.page().setWebChannel(self.web_channel)

    def load_web_interface(self):
        """Load the web interface HTML"""
        web_dir = Path(__file__).parent / "web"
        index_file = web_dir / "index.html"

        if index_file.exists():
            url = QUrl.fromLocalFile(str(index_file.absolute()))
            self.web_view.load(url)
            self.logger.info("Loading web interface from local file")
        else:
            self.logger.error(f"Web interface not found at {index_file}")
            self.load_fallback_interface()

    def load_fallback_interface(self):
        """Load a fallback interface if main interface fails"""
        fallback_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Lyrixa Interface</title>
            <style>
                body {
                    font-family: 'JetBrains Mono', monospace;
                    background: #0a0a0a;
                    color: #00ff88;
                    text-align: center;
                    padding: 50px;
                }
                h1 { color: #00ff88; }
                p { color: #cccccc; }
            </style>
        </head>
        <body>
            <h1>🧠 Lyrixa Interface</h1>
            <p>Web interface is loading...</p>
            <p>If this message persists, check the web interface files.</p>
        </body>
        </html>
        """
        self.web_view.setHtml(fallback_html)

    def handle_web_message(self, message: str):
        """Handle messages from web interface"""
        self.logger.debug(f"Web message: {message}")
        self.chat_message_sent.emit(message)

    def send_chat_response(self, sender: str, content: str):
        """Send chat response to web interface"""
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.receiveMessage('{sender}', `{content}`);
        }}
        """
        self.web_view.page().runJavaScript(script)

    def update_stats(self, stats: Dict[str, Any]):
        """Update dashboard stats in web interface"""
        stats_json = json.dumps(stats).replace('"', '\\"')
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.updateData('stats', {stats_json});
        }}
        """
        self.web_view.page().runJavaScript(script)

    def update_thought_log(self, thoughts: list):
        """Update thought log in web interface"""
        thoughts_json = json.dumps(thoughts).replace('"', '\\"')
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.updateData('thoughts', {thoughts_json});
        }}
        """
        self.web_view.page().runJavaScript(script)

    def update_improvement_feed(self, improvements: list):
        """Update self-improvement feed in web interface"""
        improvements_json = json.dumps(improvements).replace('"', '\\"')
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.updateData('improvements', {improvements_json});
        }}
        """
        self.web_view.page().runJavaScript(script)

    def update_reflection_panel(self, reflection_data: Dict[str, Any]):
        """Update reflection panel in web interface"""
        data_json = json.dumps(reflection_data).replace('"', '\\"')
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.updateData('reflection', {data_json});
        }}
        """
        self.web_view.page().runJavaScript(script)

    def update_memory_graph(self, graph_data: Dict[str, Any]):
        """Update memory graph visualization in web interface - ✅ 3. Memory Graph Panel"""
        data_json = json.dumps(graph_data).replace('"', '\\"')
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.updateMemoryGraph({data_json});
        }}
        console.log('Memory graph updated:', {data_json});
        """
        self.web_view.page().runJavaScript(script)

    def set_status(self, status: str, message: str):
        """Update status in web interface"""
        script = f"""
        if (window.lyrixaInterface) {{
            window.lyrixaInterface.setStatus('{status}', '{message}');
        }}
        """
        self.web_view.page().runJavaScript(script)

    def execute_javascript(self, script: str):
        """Execute arbitrary JavaScript in web interface"""
        self.web_view.page().runJavaScript(script)

    def reload_interface(self):
        """Reload the web interface"""
        self.web_view.reload()
