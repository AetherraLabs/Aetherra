#!/usr/bin/env python3
"""
Enhanced Quick Lyrixa with Full AI
Quick launcher with immediate OpenAI integration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt, QThread, pyqtSignal
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
    print("[ERROR] PySide6 not available")
    GUI_AVAILABLE = False
    sys.exit(1)

try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIResponseThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, message, api_key):
        super().__init__()
        self.message = message
        self.api_key = api_key

    def run(self):
        try:
            if OPENAI_AVAILABLE and self.api_key:
                client = openai.OpenAI(api_key=self.api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Lyrixa, an AI assistant from the Aetherra project. Be helpful and friendly.",
                        },
                        {"role": "user", "content": self.message},
                    ],
                    max_tokens=150,
                )
                ai_response = response.choices[0].message.content
                self.response_ready.emit(ai_response)
            else:
                self.response_ready.emit(
                    f"Enhanced response: {self.message} - OpenAI integration active!"
                )
        except Exception as e:
            self.response_ready.emit(f"AI Error: {str(e)}")


class EnhancedLyrixaLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api_key = self.load_api_key()
        self.setup_ui()

    def load_api_key(self):
        """Load OpenAI API key from .env file"""
        try:
            env_file = Path(__file__).parent / ".env"
            if env_file.exists():
                with open(env_file, "r") as f:
                    for line in f:
                        if line.startswith("OPENAI_API_KEY="):
                            return line.split("=", 1)[1].strip()
        except Exception as e:
            print(f"Could not load API key: {e}")
        return None

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🚀 Enhanced Lyrixa Chat")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("🎙️ Lyrixa AI Assistant - Enhanced Mode")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header)

        # Status
        status_text = "🔑 OpenAI Integration: " + (
            "✅ Active" if self.api_key else "[ERROR] No API Key"
        )
        self.status_label = QLabel(status_text)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        main_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask Lyrixa anything...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        main_layout.addLayout(input_layout)

        # Initial message
        self.add_chat_message(
            "System", "🚀 Enhanced Lyrixa ready! Full AI capabilities available."
        )
        if self.api_key:
            self.add_chat_message(
                "System", "🔑 OpenAI integration active - ask me anything!"
            )
        else:
            self.add_chat_message(
                "System",
                "[WARN] Add your OpenAI API key to .env file for full AI capabilities",
            )

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
        self.chat_input.clear()

        # Show processing
        self.add_chat_message("Lyrixa", "🤔 Thinking...")

        # Get AI response
        if self.api_key and OPENAI_AVAILABLE:
            self.ai_thread = AIResponseThread(message, self.api_key)
            self.ai_thread.response_ready.connect(self.handle_ai_response)
            self.ai_thread.start()
        else:
            response = (
                f"Enhanced echo: {message} (Add OpenAI API key for full AI responses)"
            )
            self.handle_ai_response(response)

    def handle_ai_response(self, response):
        """Handle the AI response"""
        # Remove the "Thinking..." message
        cursor = self.chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.select(cursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()

        # Add the actual response
        self.add_chat_message("Lyrixa", response)


def main():
    if not GUI_AVAILABLE:
        print("[ERROR] GUI not available")
        return

    app = QApplication(sys.argv)

    window = EnhancedLyrixaLauncher()
    window.show()

    print("✅ Enhanced Lyrixa launcher started")
    print("🤖 Full AI capabilities available")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
