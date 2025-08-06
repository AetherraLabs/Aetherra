#!/usr/bin/env python3
"""
🤖 Lyrixa Basic GUI - Simple AI Assistant Interface
==================================================

The Basic Lyrixa GUI with just two core functions:
1. AI Chat Interface
2. Aetherra Hub (Plugin Store)

Clean, simple design that expands when plugins are installed.
"""

import json
import logging
from typing import Optional

from PySide6.QtCore import Qt, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QFont, QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class LyrixaBasicWindow(QMainWindow):
    """
    LYRIXA BASIC AI ASSISTANT WINDOW

    Simple interface with:
    - AI Chat (left panel)
    - Aetherra Hub (right panel)
    """

    def __init__(self, ai_chat=None, hub_connector=None, service_registry=None):
        super().__init__()

        # Store backend connections
        self.ai_chat = ai_chat
        self.hub_connector = hub_connector
        self.service_registry = service_registry

        # UI components
        self.chat_input = None
        self.chat_display = None
        self.plugin_list = None
        self.installed_plugins_list = None

        self._setup_ui()
        self._setup_styling()
        self._connect_signals()
        self._load_initial_data()

    def _setup_ui(self):
        """Setup the basic UI layout."""
        self.setWindowTitle("Lyrixa - AI Assistant")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left Panel: AI Chat
        chat_panel = self._create_chat_panel()
        splitter.addWidget(chat_panel)

        # Right Panel: Aetherra Hub
        hub_panel = self._create_hub_panel()
        splitter.addWidget(hub_panel)

        # Set initial splitter sizes (60% chat, 40% hub)
        splitter.setSizes([720, 480])

    def _create_chat_panel(self) -> QWidget:
        """Create the AI Chat panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(panel)

        # Chat title
        title = QLabel("🤖 AI Chat Assistant")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #00d4ff;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Chat history will appear here...")
        layout.addWidget(self.chat_display)

        # Chat input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.chat_input)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self._send_message)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

        # Add welcome message
        self.chat_display.append(
            "🤖 <b>Lyrixa:</b> Hello! I'm your AI assistant. How can I help you today?"
        )

        return panel

    def _create_hub_panel(self) -> QWidget:
        """Create the Aetherra Hub panel."""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(panel)

        # Hub title
        title = QLabel("🔌 Aetherra Hub")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ff6b00;
                padding: 10px;
                background: #1a1a1a;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Create tabs for available and installed plugins
        tab_widget = QTabWidget()

        # Available Plugins tab
        available_tab = QWidget()
        available_layout = QVBoxLayout(available_tab)

        available_label = QLabel("Available Plugins:")
        available_layout.addWidget(available_label)

        self.plugin_list = QListWidget()
        available_layout.addWidget(self.plugin_list)

        install_button = QPushButton("Install Selected Plugin")
        install_button.clicked.connect(self._install_selected_plugin)
        available_layout.addWidget(install_button)

        tab_widget.addTab(available_tab, "Available")

        # Installed Plugins tab
        installed_tab = QWidget()
        installed_layout = QVBoxLayout(installed_tab)

        installed_label = QLabel("Installed Plugins:")
        installed_layout.addWidget(installed_label)

        self.installed_plugins_list = QListWidget()
        installed_layout.addWidget(self.installed_plugins_list)

        manage_button = QPushButton("Manage Selected Plugin")
        manage_button.clicked.connect(self._manage_selected_plugin)
        installed_layout.addWidget(manage_button)

        tab_widget.addTab(installed_tab, "Installed")

        layout.addWidget(tab_widget)

        return panel

    def _setup_styling(self):
        """Setup the application styling."""
        # Dark theme styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
                color: #f0f6fc;
            }

            QFrame {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 6px;
                margin: 5px;
            }

            QTextEdit {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 10px;
                color: #f0f6fc;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }

            QLineEdit {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 8px;
                color: #f0f6fc;
                font-size: 14px;
            }

            QLineEdit:focus {
                border-color: #58a6ff;
            }

            QPushButton {
                background-color: #238636;
                border: 1px solid #2ea043;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #2ea043;
            }

            QPushButton:pressed {
                background-color: #1a7f37;
            }

            QListWidget {
                background-color: #0d1117;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #f0f6fc;
                font-size: 14px;
            }

            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #21262d;
            }

            QListWidget::item:selected {
                background-color: #1f6feb;
            }

            QTabWidget::pane {
                border: 1px solid #30363d;
                background-color: #161b22;
            }

            QTabBar::tab {
                background-color: #21262d;
                border: 1px solid #30363d;
                padding: 8px 16px;
                margin-right: 2px;
                color: #f0f6fc;
            }

            QTabBar::tab:selected {
                background-color: #161b22;
                border-bottom-color: #161b22;
            }
        """)

    def _connect_signals(self):
        """Connect UI signals."""
        # Auto-refresh timer for hub data
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_hub_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def _load_initial_data(self):
        """Load initial data for the interface."""
        # Load available plugins
        self._refresh_hub_data()

        # Load installed plugins
        self._refresh_installed_plugins()

    @Slot()
    def _send_message(self):
        """Send a message to the AI chat system."""
        if not self.chat_input or not self.ai_chat:
            return

        message = self.chat_input.text().strip()
        if not message:
            return

        # Display user message
        self.chat_display.append(f"👤 <b>You:</b> {message}")
        self.chat_input.clear()

        # Send to AI system (async call)
        self._get_ai_response(message)

    def _get_ai_response(self, message: str):
        """Get AI response asynchronously."""

        # Create a worker thread for AI response
        class AIResponseWorker(QThread):
            response_ready = Signal(str)

            def __init__(self, ai_chat, message):
                super().__init__()
                self.ai_chat = ai_chat
                self.message = message

            def run(self):
                try:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    response = loop.run_until_complete(
                        self.ai_chat.send_message(self.message)
                    )
                    self.response_ready.emit(response)
                except Exception as e:
                    self.response_ready.emit(f"Sorry, I encountered an error: {e}")

        # Start worker thread
        self.ai_worker = AIResponseWorker(self.ai_chat, message)
        self.ai_worker.response_ready.connect(self._display_ai_response)
        self.ai_worker.start()

    @Slot(str)
    def _display_ai_response(self, response: str):
        """Display AI response in chat."""
        self.chat_display.append(f"🤖 <b>Lyrixa:</b> {response}")

        # Auto-scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @Slot()
    def _refresh_hub_data(self):
        """Refresh available plugins from Aetherra Hub."""
        if not self.hub_connector:
            return

        # Get available plugins asynchronously
        class HubDataWorker(QThread):
            plugins_ready = Signal(list)

            def __init__(self, hub_connector):
                super().__init__()
                self.hub_connector = hub_connector

            def run(self):
                try:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    plugins = loop.run_until_complete(
                        self.hub_connector.get_available_plugins()
                    )
                    self.plugins_ready.emit(plugins)
                except Exception as e:
                    logger.error(f"Failed to load hub data: {e}")
                    self.plugins_ready.emit([])

        self.hub_worker = HubDataWorker(self.hub_connector)
        self.hub_worker.plugins_ready.connect(self._update_plugin_list)
        self.hub_worker.start()

    @Slot(list)
    def _update_plugin_list(self, plugins: list):
        """Update the available plugins list."""
        if not self.plugin_list:
            return

        self.plugin_list.clear()

        for plugin in plugins:
            item = QListWidgetItem()
            item.setText(
                f"{plugin.get('display_name', plugin.get('name', 'Unknown'))}\n"
                f"Version: {plugin.get('version', '1.0.0')}\n"
                f"{plugin.get('description', 'No description available')}"
            )
            item.setData(Qt.UserRole, plugin)
            self.plugin_list.addItem(item)

    @Slot()
    def _install_selected_plugin(self):
        """Install the selected plugin."""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select a plugin to install."
            )
            return

        plugin_data = current_item.data(Qt.UserRole)
        plugin_name = plugin_data.get("name", "unknown")

        # Confirm installation
        reply = QMessageBox.question(
            self,
            "Install Plugin",
            f"Do you want to install '{plugin_data.get('display_name', plugin_name)}'?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self._perform_plugin_installation(plugin_name, plugin_data)

    def _perform_plugin_installation(self, plugin_name: str, plugin_data: dict):
        """Perform the actual plugin installation."""

        # Installation worker thread
        class InstallationWorker(QThread):
            installation_complete = Signal(bool, str)

            def __init__(self, hub_connector, plugin_name):
                super().__init__()
                self.hub_connector = hub_connector
                self.plugin_name = plugin_name

            def run(self):
                try:
                    import asyncio

                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(
                        self.hub_connector.install_plugin(self.plugin_name)
                    )
                    self.installation_complete.emit(success, self.plugin_name)
                except Exception as e:
                    logger.error(f"Plugin installation failed: {e}")
                    self.installation_complete.emit(False, self.plugin_name)

        self.install_worker = InstallationWorker(self.hub_connector, plugin_name)
        self.install_worker.installation_complete.connect(
            self._on_installation_complete
        )
        self.install_worker.start()

    @Slot(bool, str)
    def _on_installation_complete(self, success: bool, plugin_name: str):
        """Handle plugin installation completion."""
        if success:
            QMessageBox.information(
                self,
                "Installation Complete",
                f"Plugin '{plugin_name}' installed successfully!",
            )
            self._refresh_installed_plugins()
            # TODO: Dynamically add plugin panel to GUI
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                f"Failed to install plugin '{plugin_name}'.",
            )

    def _refresh_installed_plugins(self):
        """Refresh the list of installed plugins."""
        if not self.installed_plugins_list:
            return

        self.installed_plugins_list.clear()

        try:
            # Check for installed plugins registry
            import json
            from pathlib import Path

            lyrixa_plugins_dir = Path(__file__).parent / "plugins"
            registry_file = lyrixa_plugins_dir / "installed_plugins.json"

            if registry_file.exists():
                with open(registry_file, "r", encoding="utf-8") as f:
                    registry = json.load(f)

                if registry:
                    for name, info in registry.items():
                        # Create display text for the plugin
                        display_text = f"{name} v{info.get('version', '?')}\n{info.get('description', 'No description')}"

                        item = QListWidgetItem(display_text)
                        item.setData(Qt.UserRole, {"name": name, "info": info})
                        self.installed_plugins_list.addItem(item)
                else:
                    placeholder_item = QListWidgetItem(
                        "No plugins installed yet.\nInstall plugins from the Available tab to expand Lyrixa's capabilities."
                    )
                    self.installed_plugins_list.addItem(placeholder_item)
            else:
                placeholder_item = QListWidgetItem(
                    "No plugins installed yet.\nInstall plugins from the Available tab to expand Lyrixa's capabilities."
                )
                self.installed_plugins_list.addItem(placeholder_item)

        except Exception as e:
            logger.error(f"Error refreshing installed plugins: {e}")
            placeholder_item = QListWidgetItem(
                "Error loading installed plugins.\nCheck the log for details."
            )
            self.installed_plugins_list.addItem(placeholder_item)

    @Slot()
    def _manage_selected_plugin(self):
        """Manage the selected installed plugin."""
        current_item = self.installed_plugins_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self, "No Selection", "Please select an installed plugin to manage."
            )
            return

        # TODO: Implement plugin management
        QMessageBox.information(
            self, "Coming Soon", "Plugin management features coming soon!"
        )


def main():
    """Test the Basic Lyrixa GUI."""
    import sys

    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Basic AI Assistant")

    # Create mock backend systems for testing
    class MockAIChat:
        async def send_message(self, message):
            return f"I received your message: {message}"

    class MockHubConnector:
        async def get_available_plugins(self):
            return [
                {
                    "name": "code-editor",
                    "display_name": "Code Editor",
                    "description": "Advanced code editing capabilities",
                    "version": "1.0.0",
                },
                {
                    "name": "system-tools",
                    "display_name": "System Tools",
                    "description": "System monitoring and management tools",
                    "version": "1.0.0",
                },
            ]

        async def install_plugin(self, plugin_name):
            return True

    # Create and show window
    window = LyrixaBasicWindow(
        ai_chat=MockAIChat(), hub_connector=MockHubConnector(), service_registry=None
    )
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
