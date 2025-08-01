#!/usr/bin/env python3
"""
🧠 SIMPLE LYRIXA GUI TEST
=========================

A simplified GUI to test basic functionality and identify issues.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test imports
print("🧪 Testing GUI dependencies...")

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import (
        QApplication,
        QLabel,
        QMainWindow,
        QPushButton,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    print("✅ PySide6 available")
except ImportError as e:
    print(f"❌ PySide6 import error: {e}")
    sys.exit(1)

try:
    from lyrixa.core.conversation import LyrixaConversationalEngine

    print("✅ Lyrixa conversation engine available")
except ImportError as e:
    print(f"❌ Lyrixa core import error: {e}")

try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

    print("✅ Memory system available")
except ImportError as e:
    print(f"❌ Memory system import error: {e}")


class SimpleLyrixaGUI(QMainWindow):
    """Simple GUI for testing Lyrixa functionality."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("🧠 Lyrixa AI Assistant - Simple Test")
        self.setGeometry(200, 200, 800, 600)

        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Layout
        layout = QVBoxLayout(main_widget)

        # Title
        title = QLabel("🧠 Lyrixa AI Assistant")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        # Status
        self.status_label = QLabel("💭 Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setPlaceholderText("Chat conversation will appear here...")
        layout.addWidget(self.chat_area)

        # Input area
        self.input_area = QTextEdit()
        self.input_area.setMaximumHeight(100)
        self.input_area.setPlaceholderText("Type your message here...")
        layout.addWidget(self.input_area)

        # Send button
        self.send_button = QPushButton("💬 Send Message")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        # Test buttons
        test_layout = QVBoxLayout()

        self.test_memory_button = QPushButton("🧠 Test Memory System")
        self.test_memory_button.clicked.connect(self.test_memory)
        test_layout.addWidget(self.test_memory_button)

        self.test_conversation_button = QPushButton("💬 Test Conversation Engine")
        self.test_conversation_button.clicked.connect(self.test_conversation)
        test_layout.addWidget(self.test_conversation_button)

        layout.addLayout(test_layout)

        # Initialize status
        self.update_status("🟢 Ready")

    def update_status(self, message):
        """Update the status label."""
        self.status_label.setText(message)

    def append_chat(self, message):
        """Append a message to the chat area."""
        self.chat_area.append(message)

    def send_message(self):
        """Handle sending a message."""
        message = self.input_area.toPlainText().strip()
        if not message:
            return

        self.append_chat(f"You: {message}")
        self.input_area.clear()

        # Simple echo response for now
        self.append_chat(f"Lyrixa: I received your message: '{message}'")

    def test_memory(self):
        """Test the memory system."""
        try:
            self.update_status("🧠 Testing memory system...")
            self.append_chat("🧠 Testing memory system...")

            from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem

            memory = AdvancedMemorySystem()

            self.append_chat("✅ Memory system initialized successfully")
            self.update_status("🟢 Memory test passed")

        except Exception as e:
            self.append_chat(f"❌ Memory test failed: {e}")
            self.update_status("🔴 Memory test failed")

    def test_conversation(self):
        """Test the conversation engine."""
        try:
            self.update_status("💬 Testing conversation engine...")
            self.append_chat("💬 Testing conversation engine...")

            from lyrixa.core.conversation import LyrixaConversationalEngine

            engine = LyrixaConversationalEngine()

            self.append_chat("✅ Conversation engine initialized successfully")
            self.update_status("🟢 Conversation test passed")

        except Exception as e:
            self.append_chat(f"❌ Conversation test failed: {e}")
            self.update_status("🔴 Conversation test failed")


def main():
    """Main entry point."""
    print("🚀 Starting Simple Lyrixa GUI...")

    app = QApplication(sys.argv)

    # Create and show the GUI
    gui = SimpleLyrixaGUI()
    gui.show()

    print("👆 GUI window should be visible")
    print("💡 Use the test buttons to check functionality")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
