#!/usr/bin/env python3
"""
Natural Language Panel
=====================

Modular component for natural language processing and interaction.
"""

from typing import Any, Dict

from ..cards import ModernCard
from ..theme import ModernTheme
from ..utils.qt_imports import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class NaturalLanguagePanel(ModernCard):
    """Panel for natural language processing and interaction"""

    def __init__(self, parent=None):
        super().__init__("💬 Natural Language", parent)
        self.conversation_history = []
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        # Language model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))

        self.model_combo = QComboBox()
        self.model_combo.addItems(["GPT-4", "GPT-3.5-Turbo", "Claude-3", "Gemini-Pro"])
        model_layout.addWidget(self.model_combo)

        model_layout.addStretch()

        model_widget = QWidget()
        model_widget.setLayout(model_layout)
        self.add_widget(model_widget)

        # Conversation display
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_PRIMARY};
                font-family: 'Consolas', 'Monaco', monospace;
            }}
        """)
        self.conversation_display.setPlaceholderText("Conversation will appear here...")
        self.add_widget(self.conversation_display)

        # Input area
        input_layout = QVBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_PRIMARY};
                padding: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # Control buttons
        buttons_layout = QHBoxLayout()

        self.send_btn = QPushButton("📤 Send")
        self.send_btn.clicked.connect(self.send_message)
        buttons_layout.addWidget(self.send_btn)

        self.clear_btn = QPushButton("🗑️ Clear")
        self.clear_btn.clicked.connect(self.clear_conversation)
        buttons_layout.addWidget(self.clear_btn)

        self.translate_btn = QPushButton("🌐 Translate")
        self.translate_btn.clicked.connect(self.translate_message)
        buttons_layout.addWidget(self.translate_btn)

        buttons_layout.addStretch()

        self.voice_btn = QPushButton("🎤 Voice")
        self.voice_btn.clicked.connect(self.start_voice_input)
        buttons_layout.addWidget(self.voice_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        input_layout.addWidget(buttons_widget)

        input_widget = QWidget()
        input_widget.setLayout(input_layout)
        self.add_widget(input_widget)

        # Quick actions
        actions_layout = QHBoxLayout()

        quick_actions = [
            ("📝 Summarize", self.quick_summarize),
            ("🔍 Analyze", self.quick_analyze),
            ("💡 Suggest", self.quick_suggest),
            ("🔧 Debug", self.quick_debug),
        ]

        for text, callback in quick_actions:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {ModernTheme.SURFACE_VARIANT};
                    border: 1px solid {ModernTheme.BORDER};
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background-color: {ModernTheme.PRIMARY};
                }}
            """)
            actions_layout.addWidget(btn)

        actions_layout.addStretch()

        actions_widget = QWidget()
        actions_widget.setLayout(actions_layout)
        self.add_widget(actions_widget)

    def send_message(self):
        """Send a message to the AI"""
        message = self.input_field.text().strip()
        if not message:
            return

        # Add user message to conversation
        self.add_message("User", message)
        self.input_field.clear()

        # Simulate AI response
        ai_response = self.get_ai_response(message)
        self.add_message("AI", ai_response)

    def add_message(self, sender: str, message: str):
        """Add a message to the conversation display"""
        timestamp = "12:34"  # In real implementation, use actual timestamp

        # Color code messages
        if sender == "User":
            color = ModernTheme.PRIMARY
        else:
            color = ModernTheme.SECONDARY

        formatted_message = f"""
<div style="margin-bottom: 10px;">
    <span style="color: {color}; font-weight: bold;">[{timestamp}] {sender}:</span><br>
    <span style="color: {ModernTheme.TEXT_PRIMARY};">{message}</span>
</div>
"""

        self.conversation_display.append(formatted_message)

        # Store in history
        self.conversation_history.append(
            {"sender": sender, "message": message, "timestamp": timestamp}
        )

    def get_ai_response(self, message: str) -> str:
        """Get AI response to message (simulated)"""
        # This would connect to actual AI service in production
        responses = [
            "I understand your request. Let me help you with that.",
            "That's an interesting question. Here's what I think...",
            "Based on the context, I would suggest...",
            "I can help you solve this problem step by step.",
            "Let me analyze this for you...",
        ]

        import random

        return random.choice(responses)

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_display.clear()
        self.conversation_history.clear()

    def translate_message(self):
        """Translate the current input"""
        message = self.input_field.text().strip()
        if message:
            # Simulate translation
            translated = f"[Translated] {message}"
            self.input_field.setText(translated)

    def start_voice_input(self):
        """Start voice input (placeholder)"""
        self.add_message("System", "Voice input feature would be implemented here")

    def quick_summarize(self):
        """Quick summarize action"""
        self.input_field.setText("Please summarize the main points of our conversation")
        self.send_message()

    def quick_analyze(self):
        """Quick analyze action"""
        self.input_field.setText("Can you analyze the current situation and provide insights?")
        self.send_message()

    def quick_suggest(self):
        """Quick suggest action"""
        self.input_field.setText("What would you suggest as the next steps?")
        self.send_message()

    def quick_debug(self):
        """Quick debug action"""
        self.input_field.setText("Help me debug this issue step by step")
        self.send_message()

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for msg in self.conversation_history if msg["sender"] == "User")
        ai_messages = total_messages - user_messages

        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "selected_model": self.model_combo.currentText(),
        }
