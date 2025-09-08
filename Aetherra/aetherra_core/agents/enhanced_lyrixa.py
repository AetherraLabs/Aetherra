# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Enhanced Lyrixa Window
=====================

Main enhanced UI window for the Lyrixa assistant system.
Provides a sophisticated interface for Aetherra code interaction.
"""

import sys

# Public exports for optional GUI component
__all__ = ["EnhancedLyrixaWindow", "launch_enhanced_lyrixa"]


class EnhancedLyrixaWindow:
    """
    Enhanced Lyrixa Assistant Window

    Main window for the Lyrixa assistant with advanced features:
    - Multi-panel interface
    - Real-time code interpretation
    - Plugin integration
    - Enhanced chat capabilities
    """

    def __init__(self):
        """Initialize the Enhanced Lyrixa Window."""
        print("Enhanced Lyrixa Window initialized")
        self.window_title = "Lyrixa Assistant - Enhanced Interface"
        self.width = 1200
        self.height = 800

        # Check if Qt is available
        try:
            from PySide6.QtCore import Qt  # noqa: F401 (optional runtime import)

            # Defer heavy widget imports to _setup_qt_window to avoid F401 noise here
            self.qt_available = True
            self._setup_qt_window()
        except ImportError:
            self.qt_available = False
            print("PySide6 not available - running in console mode")

        # Initialize core functionality
        self.code_content = ""
        self.chat_history = []
        self.plugins = [
            "Memory System",
            "Code Analyzer",
            "Performance Monitor",
            "Debug Assistant",
            "Documentation Generator",
        ]
        self.active_plugin = None

    def _setup_qt_window(self):
        """Setup Qt-based GUI if available."""
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QPushButton,
            QSplitter,
            QStatusBar,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        class QtWindow(QMainWindow):
            def __init__(self, parent_window):
                super().__init__()
                self.parent_window = parent_window
                self.setWindowTitle(parent_window.window_title)
                self.resize(parent_window.width, parent_window.height)
                self.setup_ui()

            def setup_ui(self):
                central_widget = QWidget()
                self.setCentralWidget(central_widget)

                # Create main splitter with safe orientation attempt
                main_splitter = QSplitter()
                import contextlib

                with contextlib.suppress(Exception):
                    orientation = getattr(Qt, "Horizontal", None)
                    if orientation is not None:
                        main_splitter.setOrientation(orientation)
                layout = QVBoxLayout(central_widget)
                layout.addWidget(main_splitter)

                # Left panel
                left_widget = QWidget()
                left_layout = QVBoxLayout(left_widget)

                # Code editor
                left_layout.addWidget(QLabel("Aetherra Code Editor"))
                self.code_editor = QTextEdit()
                self.code_editor.setPlaceholderText("Enter your Aetherra code here...")
                left_layout.addWidget(self.code_editor)

                # Execute button
                execute_btn = QPushButton("Execute Aetherra Code")
                execute_btn.clicked.connect(self.execute_code)
                left_layout.addWidget(execute_btn)

                # Console
                left_layout.addWidget(QLabel("Console Output"))
                self.console = QTextEdit()
                self.console.setReadOnly(True)
                left_layout.addWidget(self.console)

                main_splitter.addWidget(left_widget)

                # Right panel
                right_widget = QWidget()
                right_layout = QVBoxLayout(right_widget)

                # Chat
                right_layout.addWidget(QLabel("Lyrixa Assistant"))
                self.chat_display = QTextEdit()
                self.chat_display.setReadOnly(True)
                right_layout.addWidget(self.chat_display)

                # Chat input
                input_layout = QHBoxLayout()
                self.chat_input = QLineEdit()
                self.chat_input.setPlaceholderText("Ask Lyrixa anything...")
                self.chat_input.returnPressed.connect(self.send_message)
                input_layout.addWidget(self.chat_input)

                send_btn = QPushButton("Send")
                send_btn.clicked.connect(self.send_message)
                input_layout.addWidget(send_btn)
                right_layout.addLayout(input_layout)

                main_splitter.addWidget(right_widget)

                # Status bar
                self.setStatusBar(QStatusBar())
                self.statusBar().showMessage("Lyrixa Assistant Ready")

            def execute_code(self):
                code = self.code_editor.toPlainText()
                self.parent_window.execute_code(code)
                self.console.append(f"> Executed: {code[:50]}...")

            def send_message(self):
                message = self.chat_input.text()
                if message.strip():
                    self.parent_window.send_message(message)
                    self.chat_display.append(f"You: {message}")
                    self.chat_display.append("Lyrixa: Processing your request...")
                    self.chat_input.clear()

        self.qt_window = QtWindow(self)

    def execute_code(self, code):
        """Execute Aetherra code."""
        self.code_content = code
        print(f"Executing Aetherra code: {code[:100]}...")
        # Add actual code execution logic here
        return True

    def send_message(self, message):
        """Send message to Lyrixa assistant."""
        self.chat_history.append({"user": message, "timestamp": "now"})
        print(f"Lyrixa received: {message}")
        # Add actual assistant logic here
        return f"Lyrixa: I understand you said '{message}'"

    def activate_plugin(self, plugin_name):
        """Activate a plugin."""
        if plugin_name in self.plugins:
            self.active_plugin = plugin_name
            print(f"Activated plugin: {plugin_name}")
            return True
        return False

    def show(self):
        """Show the window."""
        if self.qt_available and hasattr(self, "qt_window"):
            self.qt_window.show()
            return self.qt_window
        else:
            print("Enhanced Lyrixa Window is running in console mode")
            print(f"Title: {self.window_title}")
            print(f"Size: {self.width}x{self.height}")
            print("Available plugins:", self.plugins)
            return self

    def close(self):
        """Close the window."""
        if self.qt_available and hasattr(self, "qt_window"):
            self.qt_window.close()
        print("Enhanced Lyrixa Window closed")


def launch_enhanced_lyrixa():
    """Launch function to run the Enhanced Lyrixa Window."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = EnhancedLyrixaWindow()
        qt_window = window.show()
        if qt_window and hasattr(qt_window, "exec"):
            sys.exit(app.exec())
        elif qt_window:
            sys.exit(app.exec_())
    except ImportError:
        # Fallback to console mode
        window = EnhancedLyrixaWindow()
        window.show()
        print("Press Enter to exit...")
        input()


if __name__ == "__main__":
    # Direct module execution launches (GUI if available, else console fallback)
    launch_enhanced_lyrixa()
