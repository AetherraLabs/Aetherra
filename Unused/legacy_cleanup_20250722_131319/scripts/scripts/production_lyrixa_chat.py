#!/usr/bin/env python3
"""
Production Lyrixa Chat - Full AI Capabilities
This launcher provides immediate access to full AI capabilities without waiting for complex initialization
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QStatusBar,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    GUI_AVAILABLE = True
except ImportError:
    print("[ERROR] PySide6 not available")
    GUI_AVAILABLE = False
    sys.exit(1)


class AIResponseThread(QThread):
    response_ready = Signal(str, str)  # response, provider

    def __init__(self, message):
        super().__init__()
        self.message = message

    def run(self):
        """Try multiple AI providers for the best response"""
        # Load environment variables
        try:
            from dotenv import load_dotenv

            load_dotenv()
            openai_key = os.getenv("OPENAI_API_KEY")
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        except:
            openai_key = None
            anthropic_key = None

        # Try OpenAI first
        if openai_key:
            try:
                import openai

                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are Lyrixa, an advanced AI assistant from the Aetherra project. You have full capabilities including coding, analysis, creative tasks, and complex problem-solving. Be intelligent, helpful, and engaging.",
                        },
                        {"role": "user", "content": self.message},
                    ],
                    max_tokens=400,
                    temperature=0.7,
                )
                ai_response = response.choices[0].message.content
                self.response_ready.emit(ai_response, "OpenAI GPT-3.5")
                return
            except Exception as e:
                print(f"OpenAI failed: {e}")

        # Try Claude if OpenAI fails
        if anthropic_key:
            try:
                import anthropic

                client = anthropic.Anthropic(api_key=anthropic_key)
                response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=400,
                    messages=[
                        {
                            "role": "user",
                            "content": f"You are Lyrixa, an advanced AI assistant from the Aetherra project with full capabilities. Respond to: {self.message}",
                        }
                    ],
                )
                ai_response = response.content[0].text
                self.response_ready.emit(ai_response, "Claude")
                return
            except Exception as e:
                print(f"Claude failed: {e}")

        # Fallback response
        self.response_ready.emit(
            f"I understand you're asking about '{self.message}'. I'm currently running in offline mode. To enable full AI capabilities, please add a valid OpenAI or Anthropic API key to your .env file.",
            "Offline Mode",
        )


class ProductionLyrixaChat(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_api_status()

    def load_api_status(self):
        """Check which AI providers are available"""
        try:
            from dotenv import load_dotenv

            load_dotenv()
            openai_key = os.getenv("OPENAI_API_KEY")
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")

            providers = []
            if openai_key:
                providers.append("OpenAI")
            if anthropic_key:
                providers.append("Claude")

            if providers:
                status = f"🔑 AI Providers: {', '.join(providers)}"
                self.add_system_message(
                    f"✅ Full AI capabilities enabled with {', '.join(providers)}"
                )
            else:
                status = "[WARN] No AI providers configured"
                self.add_system_message(
                    "[WARN] Add OpenAI or Anthropic API key to .env file for full AI capabilities"
                )

            self.status_bar.showMessage(status)

        except Exception as e:
            self.status_bar.showMessage("[ERROR] Configuration error")

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("🎙️ Lyrixa AI - Production Chat")
        self.setGeometry(150, 150, 1000, 700)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("🎙️ Lyrixa AI Assistant - Full Capabilities")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setStyleSheet(
            "color: #00ff88; background: #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 10px;"
        )
        layout.addWidget(header)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #00ff88;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText(
            "Ask Lyrixa anything... (Full AI capabilities)"
        )
        self.chat_input.returnPressed.connect(self.send_message)
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 2px solid #00ff88;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
            }
        """)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: #000000;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00cc66;
            }
        """)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #00ff88;
                border-top: 1px solid #00ff88;
            }
        """)

        # Welcome message
        self.add_system_message(
            "🚀 Lyrixa Production Chat initialized - Full AI capabilities ready!"
        )

    def add_system_message(self, message):
        """Add a system message"""
        self.chat_display.append(
            f'<span style="color: #00ff88;"><b>🤖 System:</b> {message}</span><br>'
        )

    def add_user_message(self, message):
        """Add a user message"""
        self.chat_display.append(
            f'<span style="color: #4ade80;"><b>👤 You:</b> {message}</span><br>'
        )

    def add_ai_message(self, message, provider):
        """Add an AI response"""
        self.chat_display.append(
            f'<span style="color: #ffffff;"><b>🎙️ Lyrixa ({provider}):</b> {message}</span><br>'
        )

    def send_message(self):
        """Handle sending a message"""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.add_user_message(message)
        self.chat_input.clear()

        # Show processing
        self.add_system_message("🤔 Processing with full AI capabilities...")

        # Get AI response
        self.ai_thread = AIResponseThread(message)
        self.ai_thread.response_ready.connect(self.handle_ai_response)
        self.ai_thread.start()

    def handle_ai_response(self, response, provider):
        """Handle the AI response"""
        # Remove the "Processing..." message
        content = self.chat_display.toPlainText()
        lines = content.split("\n")
        if lines and "Processing with full AI capabilities" in lines[-1]:
            # Remove last line
            self.chat_display.clear()
            self.chat_display.append("\n".join(lines[:-1]))

        # Add the actual response
        self.add_ai_message(response, provider)


def main():
    if not GUI_AVAILABLE:
        print("[ERROR] GUI not available")
        return

    app = QApplication(sys.argv)

    window = ProductionLyrixaChat()
    window.show()

    print("✅ Production Lyrixa Chat started")
    print("🤖 Full AI capabilities available immediately")
    print("🔑 Supports OpenAI and Claude APIs")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
