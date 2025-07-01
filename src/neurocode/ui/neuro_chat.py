#!/usr/bin/env python3
"""
🎭 NeuroChat - Enhanced AI Assistant Interface
=============================================

Modern chat interface for NeuroCode featuring:
- Tabbed interface: Assistant / Reflections / Code Preview
- Auto-scroll and typing indicators for realistic conversation flow
- Memory-aware conversations with reflection browsing
- Real-time code preview and execution
- Intelligent response streaming with animations

Designed for seamless AI-native programming and interaction.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add core modules to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports with PySide6
try:
    from PySide6.QtCore import QPropertyAnimation, QRect, Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSplitter,
        QTabWidget,
        QTextBrowser,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    print("❌ PySide6 not available. Please install PySide6.")
    QT_AVAILABLE = False

# Import NeuroCode components
try:
    from core.interpreter import NeuroInterpreter
    from core.llm_integration import LLMIntegration
    from core.memory import NeuroMemory
except ImportError as e:
    print(f"⚠️ NeuroCode components not fully available: {e}")
    NeuroMemory = None
    NeuroInterpreter = None
    LLMIntegration = None


class TypingIndicator(QWidget):
    """Animated typing indicator for realistic chat experience"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate)
        self.dot_count = 0

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        self.avatar = QLabel("🤖")
        self.avatar.setFont(QFont("Arial", 12))

        self.text_label = QLabel("AI is thinking")
        self.text_label.setFont(QFont("Arial", 10))
        self.text_label.setStyleSheet("color: #666; font-style: italic;")

        layout.addWidget(self.avatar)
        layout.addWidget(self.text_label)
        layout.addStretch()

        self.hide()

    def start_animation(self):
        """Start the typing animation"""
        self.show()
        self.animation_timer.start(500)  # Update every 500ms

    def stop_animation(self):
        """Stop the typing animation"""
        self.hide()
        self.animation_timer.stop()
        self.dot_count = 0

    def animate(self):
        """Animate the typing dots"""
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.text_label.setText(f"AI is thinking{dots}")


class MessageWidget(QFrame):
    """Individual message widget with styling and animations"""

    def __init__(self, message: str, is_user: bool = True, timestamp: str = None, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        # Header with avatar and timestamp
        header = QHBoxLayout()

        avatar = "👤" if self.is_user else "🤖"
        name = "You" if self.is_user else "NeuroAI"

        avatar_label = QLabel(avatar)
        avatar_label.setFont(QFont("Arial", 14))

        name_label = QLabel(name)
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        time_label = QLabel(self.timestamp)
        time_label.setFont(QFont("Arial", 9))
        time_label.setStyleSheet("color: #888;")

        header.addWidget(avatar_label)
        header.addWidget(name_label)
        header.addStretch()
        header.addWidget(time_label)

        # Message content
        message_text = QTextBrowser()
        message_text.setPlainText(self.message)
        message_text.setMaximumHeight(200)
        message_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Styling based on sender
        if self.is_user:
            self.setStyleSheet("""
                QFrame {
                    background-color: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 8px;
                    margin: 2px 50px 2px 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #f5f5f5;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    margin: 2px 2px 2px 50px;
                }
            """)

        layout.addLayout(header)
        layout.addWidget(message_text)


class ChatView(QWidget):
    """Main chat interface with message history and input"""

    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.messages = []
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Chat history area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.addStretch()  # Push messages to bottom

        self.scroll_area.setWidget(self.chat_container)

        # Typing indicator
        self.typing_indicator = TypingIndicator()
        self.chat_layout.addWidget(self.typing_indicator)

        # Input area
        input_container = QFrame()
        input_container.setFrameStyle(QFrame.Shape.StyledPanel)
        input_layout = QHBoxLayout(input_container)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.scroll_area)
        layout.addWidget(input_container)

        # Add welcome message
        self.add_message(
            "Hello! I'm NeuroAI, your AI programming assistant. How can I help you today?", False
        )

    def add_message(self, text: str, is_user: bool = True):
        """Add a message to the chat"""
        message_widget = MessageWidget(text, is_user)

        # Insert before typing indicator (second to last)
        insert_index = self.chat_layout.count() - 2
        self.chat_layout.insertWidget(insert_index, message_widget)

        self.messages.append({"text": text, "is_user": is_user, "timestamp": datetime.now()})

        # Auto-scroll to bottom
        QTimer.singleShot(50, self.scroll_to_bottom)

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Send user message"""
        text = self.message_input.text().strip()
        if not text:
            return

        # Add user message
        self.add_message(text, True)
        self.message_input.clear()

        # Emit signal for processing
        self.message_sent.emit(text)

        # Show typing indicator
        self.typing_indicator.start_animation()

    def add_ai_response(self, response: str):
        """Add AI response and stop typing indicator"""
        self.typing_indicator.stop_animation()
        self.add_message(response, False)


class ReflectionBrowser(QWidget):
    """Browse and analyze memory reflections"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🧠 Memory Reflections & Insights")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Splitter for browsing
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Reflection categories
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("📂 Reflection Categories"))

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabels(["Category", "Count"])
        self.category_tree.itemSelectionChanged.connect(self.on_category_selected)

        # Add some sample categories
        categories = [
            ("Learning Progress", "12"),
            ("Problem Solving", "8"),
            ("Code Patterns", "15"),
            ("AI Interactions", "25"),
            ("Memory Formation", "7"),
        ]

        for category, count in categories:
            item = QTreeWidgetItem([category, count])
            self.category_tree.addTopLevelItem(item)

        left_layout.addWidget(self.category_tree)

        # Right panel - Reflection details
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("🔍 Reflection Analysis"))

        self.reflection_viewer = QTextBrowser()
        self.reflection_viewer.setPlainText("Select a category to view reflections...")
        right_layout.addWidget(self.reflection_viewer)

        # Insights panel
        right_layout.addWidget(QLabel("💡 AI Insights"))

        self.insights_viewer = QTextBrowser()
        self.insights_viewer.setMaximumHeight(150)
        right_layout.addWidget(self.insights_viewer)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)

    def on_category_selected(self):
        """Handle category selection"""
        current_item = self.category_tree.currentItem()
        if not current_item:
            return

        category = current_item.text(0)
        self.show_reflections_for_category(category)

    def show_reflections_for_category(self, category: str):
        """Show reflections for selected category"""
        # Mock reflection data
        reflections = {
            "Learning Progress": """
📈 Learning Trajectory Analysis

Recent learning patterns show consistent engagement with NeuroCode concepts:

• Session 1: Introduction to AI-native programming
  - Duration: 45 minutes
  - Comprehension: High
  - Key insights: Natural language as code interface

• Session 2: Memory system exploration  
  - Duration: 30 minutes
  - Comprehension: Very High
  - Key insights: Persistent context awareness

• Session 3: Plugin architecture deep-dive
  - Duration: 60 minutes
  - Comprehension: High
  - Key insights: Modular AI capabilities

🎯 Learning Velocity: Accelerating
📊 Retention Rate: 92%
🔄 Application Success: Strong
            """,
            "AI Interactions": """
🤖 AI Interaction Patterns

Analysis of recent AI assistant conversations:

• Question Types:
  - Technical queries: 45%
  - Conceptual discussions: 30%  
  - Implementation help: 25%

• Response Quality:
  - Helpful: 94%
  - Accurate: 91%
  - Complete: 87%

• Conversation Flow:
  - Average turns: 5.2
  - Resolution rate: 89%
  - Follow-up questions: 34%

💬 Communication Style: Collaborative
🎯 Goal Achievement: High
🔍 Curiosity Level: Very High
            """,
        }

        reflection_text = reflections.get(category, f"No reflections available for {category}")
        self.reflection_viewer.setPlainText(reflection_text)

        # Generate insights
        insights = f"""
🧠 AI Analysis for {category}:

• Pattern Recognition: Strong consistent patterns detected
• Growth Trajectory: Positive upward trend  
• Optimization Opportunities: Focus on practical application
• Recommended Actions: Continue current learning approach

Confidence: 87% | Data Points: 15 | Time Span: 7 days
        """
        self.insights_viewer.setPlainText(insights)


class CodePreview(QWidget):
    """Live code preview and execution environment"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("📝 Live Code Preview & Execution")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Splitter for code and output
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Code editor area
        code_container = QWidget()
        code_layout = QVBoxLayout(code_container)

        code_layout.addWidget(QLabel("💻 NeuroCode Editor"))

        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 11))
        self.code_editor.setPlainText("""# NeuroCode Example
goal: "Learn AI-native programming"

# Remember key concepts
remember("NeuroCode uses natural language as code") as "core_concept"

# AI assistant integration
assistant: "Explain the memory system benefits"

# Plugin usage
plugin: calculate "2 + 3 * 4"

# Memory recall
recall "core_concept"
""")

        code_layout.addWidget(self.code_editor)

        # Execution controls
        controls = QHBoxLayout()

        self.run_button = QPushButton("▶️ Run Code")
        self.run_button.clicked.connect(self.execute_code)

        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_output)

        self.save_button = QPushButton("💾 Save")

        controls.addWidget(self.run_button)
        controls.addWidget(self.clear_button)
        controls.addWidget(self.save_button)
        controls.addStretch()

        code_layout.addLayout(controls)

        # Output area
        output_container = QWidget()
        output_layout = QVBoxLayout(output_container)

        output_layout.addWidget(QLabel("📋 Execution Output"))

        self.output_display = QTextBrowser()
        self.output_display.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_display)

        # Execution progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        output_layout.addWidget(self.progress_bar)

        splitter.addWidget(code_container)
        splitter.addWidget(output_container)
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

    def execute_code(self):
        """Execute the NeuroCode"""
        code = self.code_editor.toPlainText()

        if not code.strip():
            self.output_display.setPlainText("❌ No code to execute")
            return

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Simulate execution (replace with actual NeuroCode execution)
        output = f"""🚀 NeuroCode Execution Started
⏰ Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

📋 Parsing NeuroCode...
✅ Goal registered: "Learn AI-native programming"
✅ Memory stored: "NeuroCode uses natural language as code" → core_concept
🤖 AI Assistant: Responding to "Explain the memory system benefits"
🔌 Plugin executed: calculate "2 + 3 * 4" = 14
🧠 Memory recalled: "NeuroCode uses natural language as code"

✅ Execution completed successfully!
📊 Runtime: 0.23 seconds
💡 Suggestions: Try exploring more memory operations or plugin integrations
"""

        # Simulate processing delay
        QTimer.singleShot(1000, lambda: self.show_execution_result(output))

    def show_execution_result(self, output: str):
        """Show execution result"""
        self.progress_bar.setVisible(False)
        self.output_display.setPlainText(output)

    def clear_output(self):
        """Clear the output display"""
        self.output_display.clear()


class NeuroChatInterface(QMainWindow):
    """Main NeuroChat application with enhanced tabbed interface"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.init_components()

    def setup_ui(self):
        self.setWindowTitle("🎭 NeuroChat - AI Assistant Interface")
        self.setGeometry(100, 100, 1400, 900)

        # Create central tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab styling
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                top: -1px;
            }
            
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #c0c0c0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
            
            QTabBar::tab:hover {
                background: #e0e0e0;
            }
        """)

        # Create tabs
        self.create_tabs()

        # Status bar
        self.statusBar().showMessage("🎭 NeuroChat ready - AI assistant at your service!")

    def create_tabs(self):
        """Create the main tabs"""
        # Assistant Chat Tab
        self.chat_view = ChatView()
        self.chat_view.message_sent.connect(self.handle_user_message)
        self.tab_widget.addTab(self.chat_view, "🤖 Assistant")

        # Reflections Tab
        self.reflection_browser = ReflectionBrowser()
        self.tab_widget.addTab(self.reflection_browser, "🧠 Reflections")

        # Code Preview Tab
        self.code_preview = CodePreview()
        self.tab_widget.addTab(self.code_preview, "📝 Code Preview")

    def init_components(self):
        """Initialize NeuroCode components"""
        try:
            self.memory = NeuroMemory() if NeuroMemory else None
            self.interpreter = NeuroInterpreter() if NeuroInterpreter else None
            self.llm = LLMIntegration() if LLMIntegration else None
        except Exception as e:
            print(f"⚠️ Component initialization failed: {e}")
            self.memory = None
            self.interpreter = None
            self.llm = None

    def handle_user_message(self, message: str):
        """Handle user message and generate AI response"""
        # Simulate AI processing delay
        QTimer.singleShot(2000, lambda: self.generate_ai_response(message))

    def generate_ai_response(self, user_message: str):
        """Generate AI response to user message"""
        # Mock AI responses (replace with actual LLM integration)
        responses = {
            "hello": "Hello! I'm NeuroAI, your programming assistant. I can help you with NeuroCode, memory management, plugin usage, and more!",
            "help": "I can assist you with:\n• NeuroCode syntax and concepts\n• Memory system operations\n• Plugin discovery and usage\n• Code execution and debugging\n• Learning AI-native programming\n\nWhat would you like to explore?",
            "memory": "The NeuroCode memory system allows persistent context across sessions. You can store information with `remember()`, retrieve it with `recall()`, and search patterns with `memory.search()`. It's designed for AI-native programming workflows!",
            "plugins": "NeuroCode has a rich plugin ecosystem! Use `plugin: <name> <args>` to execute plugins. Available categories include mathematics, text analysis, and development tools. Try asking me about specific plugin capabilities!",
        }

        # Simple keyword matching (replace with actual AI)
        response = None
        for keyword, resp in responses.items():
            if keyword in user_message.lower():
                response = resp
                break

        if not response:
            response = f"I understand you're asking about: '{user_message}'. Let me help you with that! NeuroCode is designed for natural language programming. Would you like me to show you some examples or explain specific concepts?"

        self.chat_view.add_ai_response(response)


def main():
    """Main entry point for NeuroChat"""
    if not QT_AVAILABLE:
        print("❌ Qt not available. Please install PySide6.")
        return

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create and show the chat interface
    chat_interface = NeuroChatInterface()
    chat_interface.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
