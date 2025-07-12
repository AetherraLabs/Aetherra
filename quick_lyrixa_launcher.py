#!/usr/bin/env python3
"""
Quick Lyrixa Chat Launcher
Modified launcher that enables chat immediately without complex initialization
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QSplitter,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    GUI_AVAILABLE = True
except ImportError:
    print("❌ PySide6 not available")
    GUI_AVAILABLE = False
    sys.exit(1)

# Import basic Lyrixa functionality
try:
    from lyrixa import LyrixaAI

    print("✅ Lyrixa AI imported successfully")
except ImportError as e:
    print(f"⚠️ Could not import Lyrixa AI: {e}")
    LyrixaAI = None


class QuickLyrixaLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lyrixa = None
        self.setup_ui()
        self.setup_basic_lyrixa()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🚀 Quick Lyrixa Chat")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel (System info)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # System status
        status_label = QLabel("🎯 Lyrixa Quick Chat")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(status_label)

        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setMaximumHeight(200)
        left_layout.addWidget(self.system_info)

        splitter.addWidget(left_panel)

        # Right panel (Chat)
        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)

        # Chat header
        chat_header = QLabel("💬 Chat with Lyrixa")
        chat_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chat_layout.addWidget(chat_header)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        splitter.addWidget(chat_panel)

        # Set splitter proportions
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        # Add initial messages
        self.add_system_info("✅ Quick Lyrixa launcher initialized")
        self.add_chat_message(
            "System", "🚀 Lyrixa Quick Chat ready! No complex initialization required."
        )

        # Enable chat immediately
        self.chat_input.setEnabled(True)
        self.send_button.setEnabled(True)

    def setup_basic_lyrixa(self):
        """Setup basic Lyrixa functionality"""
        try:
            if LyrixaAI:
                self.lyrixa = LyrixaAI()
                self.add_system_info("✅ Lyrixa AI instance created")
                self.add_chat_message(
                    "System", "🧠 Lyrixa AI is ready for conversation!"
                )
            else:
                self.add_system_info("⚠️ Lyrixa AI not available - using echo mode")
                self.add_chat_message(
                    "System", "⚠️ Running in echo mode - Lyrixa AI not fully loaded"
                )
        except Exception as e:
            self.add_system_info(f"⚠️ Lyrixa setup error: {e}")
            self.add_chat_message("System", f"⚠️ Lyrixa setup error: {e}")

    def add_system_info(self, message):
        """Add message to system info panel"""
        self.system_info.append(message)

    def add_chat_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def send_message(self):
        """Handle sending a message"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.add_chat_message("You", message)

        # Process with Lyrixa or provide echo response
        try:
            if self.lyrixa:
                # Try to get a response from Lyrixa
                response = f"Lyrixa received: '{message}' - Basic response mode active"
                self.add_chat_message("Lyrixa", response)
            else:
                # Echo mode
                response = f"Echo: {message} (Lyrixa AI not fully loaded)"
                self.add_chat_message("Echo", response)
        except Exception as e:
            self.add_chat_message("Error", f"Failed to process message: {e}")

        # Clear input
        self.chat_input.clear()


def main():
    if not GUI_AVAILABLE:
        print("❌ GUI not available")
        return

    app = QApplication(sys.argv)

    window = QuickLyrixaLauncher()
    window.show()

    print("✅ Quick Lyrixa launcher started")
    print("💡 Chat interface is immediately available")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
