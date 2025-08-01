#!/usr/bin/env python3
"""
Simple Lyrixa Chat Test
Minimal chat interface to test if the basic chat functionality works
"""

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
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    GUI_AVAILABLE = True
except ImportError:
    print("❌ PySide6 not available")
    GUI_AVAILABLE = False
    sys.exit(1)


class SimpleChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("🧪 Simple Lyrixa Chat Test")
        self.setGeometry(200, 200, 800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("🧪 Simple Chat Interface Test")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Add initial message
        self.add_message(
            "System", "✅ Simple chat interface ready! Type a message to test."
        )

    def add_message(self, sender, message):
        """Add a message to the chat display"""
        self.chat_display.append(f"<b>{sender}:</b> {message}")

    def send_message(self):
        """Handle sending a message"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.add_message("You", message)

        # Simple echo response
        response = f"Echo: {message} (Chat interface is working!)"
        self.add_message("Lyrixa", response)

        # Clear input
        self.chat_input.clear()


def main():
    if not GUI_AVAILABLE:
        print("❌ GUI not available")
        return

    app = QApplication(sys.argv)

    window = SimpleChatWindow()
    window.show()

    print("✅ Simple chat test window opened")
    print("💡 Try typing in the chat interface to test functionality")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
