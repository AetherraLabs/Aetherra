#!/usr/bin/env python3
"""
🌙 LYRIXA AI ASSISTANT - MODERN DARK MODE GUI
===========================================

A beautiful, modern dark theme GUI for Lyrixa AI Assistant
Featuring:
- Modern dark theme design
- Knowledge responder integration
- Real-time conversation
- Memory system visualization
- Clean, intuitive interface
- Responsive layout
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Check for GUI framework
try:
    from PySide6.QtCore import (
        QEasingCurve,
        QPropertyAnimation,
        Qt,
        QThread,
        QTimer,
        Signal,
    )
    from PySide6.QtGui import QColor, QFont, QIcon, QPalette, QPixmap
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMenuBar,
        QMessageBox,
        QProgressBar,
        QPushButton,
        QScrollArea,
        QSplitter,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    GUI_AVAILABLE = True
except ImportError:
    print("❌ PySide6 not available - please install: pip install PySide6")
    GUI_AVAILABLE = False
    sys.exit(1)

# Import Lyrixa components
try:
    from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
    from lyrixa.core.conversation import LyrixaConversationalEngine
    from lyrixa.core.project_knowledge_responder import ProjectKnowledgeResponder

    LYRIXA_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Lyrixa components not fully available: {e}")
    LYRIXA_AVAILABLE = False


class LyrixaWorkerThread(QThread):
    """Background thread for Lyrixa conversations to keep UI responsive."""

    response_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, engine, user_input):
        super().__init__()
        self.engine = engine
        self.user_input = user_input

    def run(self):
        """Process conversation in background thread."""
        try:
            # Run async conversation processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            response = loop.run_until_complete(
                self.engine.process_conversation_turn(self.user_input)
            )

            loop.close()
            self.response_ready.emit(response)

        except Exception as e:
            self.error_occurred.emit(str(e))


class ModernLyrixaGUI(QMainWindow):
    """
    Modern Dark Mode GUI for Lyrixa AI Assistant
    """

    def __init__(self):
        super().__init__()
        self.engine = None
        self.memory_system = None
        self.worker_thread = None

        # Initialize Lyrixa components
        self.init_lyrixa_components()

        # Setup UI
        self.init_ui()
        self.apply_dark_theme()

        # Setup timers and connections
        self.setup_connections()

        print("🌙 Modern Lyrixa GUI initialized successfully!")

    def init_lyrixa_components(self):
        """Initialize Lyrixa AI components."""
        if not LYRIXA_AVAILABLE:
            self.show_error(
                "Lyrixa components not available",
                "Please ensure Lyrixa is properly installed.",
            )
            return

        try:
            # Initialize memory system
            self.memory_system = AdvancedMemorySystem()

            # Initialize conversation engine
            self.engine = LyrixaConversationalEngine(memory_system=self.memory_system)

            # Initialize conversation session
            asyncio.run(self.engine.initialize_conversation("gui_session"))

            print("🧠 Lyrixa AI components initialized successfully")

        except Exception as e:
            print(f"❌ Error initializing Lyrixa components: {e}")
            self.show_error("Initialization Error", f"Failed to initialize Lyrixa: {e}")

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("🌙 Lyrixa AI Assistant - Modern Interface")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create main splitter for resizable panels
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel - Chat interface
        self.create_chat_panel(main_splitter)

        # Right panel - Information and controls
        self.create_info_panel(main_splitter)

        # Set splitter proportions (70% chat, 30% info)
        main_splitter.setSizes([840, 360])

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.create_status_bar()

    def create_chat_panel(self, parent_splitter):
        """Create the main chat interface panel."""
        chat_frame = QFrame()
        chat_frame.setFrameStyle(QFrame.Box)
        chat_frame.setLineWidth(1)
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(10)

        # Chat title
        chat_title = QLabel("💬 Conversation with Lyrixa")
        chat_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        chat_title.setAlignment(Qt.AlignCenter)
        chat_layout.addWidget(chat_title)

        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 11))
        self.chat_display.setMinimumHeight(400)
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.setPlaceholderText(
            "Ask Lyrixa anything about Aetherra, coding, or get help..."
        )
        self.input_field.setMinimumHeight(35)

        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.send_button.setMinimumHeight(35)
        self.send_button.setMinimumWidth(80)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_button)
        chat_layout.addLayout(input_layout)

        # Typing indicator
        self.typing_indicator = QLabel("💭 Lyrixa is thinking...")
        self.typing_indicator.setFont(QFont("Segoe UI", 10))
        self.typing_indicator.hide()
        chat_layout.addWidget(self.typing_indicator)

        parent_splitter.addWidget(chat_frame)

    def create_info_panel(self, parent_splitter):
        """Create the information and controls panel."""
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Box)
        info_frame.setLineWidth(1)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(15)

        # Tab widget for different info sections
        info_tabs = QTabWidget()

        # System Status Tab
        status_widget = self.create_status_tab()
        info_tabs.addTab(status_widget, "🔧 System")

        # Memory Tab
        memory_widget = self.create_memory_tab()
        info_tabs.addTab(memory_widget, "🧠 Memory")

        # Settings Tab
        settings_widget = self.create_settings_tab()
        info_tabs.addTab(settings_widget, "⚙️ Settings")

        info_layout.addWidget(info_tabs)
        parent_splitter.addWidget(info_frame)

    def create_status_tab(self):
        """Create system status tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # System status display
        status_title = QLabel("System Status")
        status_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(status_title)

        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(200)
        self.status_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.status_display)

        # Update status
        self.update_system_status()

        # Control buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(5)

        clear_btn = QPushButton("Clear Chat")
        clear_btn.clicked.connect(self.clear_chat)
        btn_layout.addWidget(clear_btn)

        memory_btn = QPushButton("Load Knowledge")
        memory_btn.clicked.connect(self.load_knowledge)
        btn_layout.addWidget(memory_btn)

        test_btn = QPushButton("Test System")
        test_btn.clicked.connect(self.test_system)
        btn_layout.addWidget(test_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        return widget

    def create_memory_tab(self):
        """Create memory information tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        memory_title = QLabel("Memory System")
        memory_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(memory_title)

        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.setFont(QFont("Consolas", 9))
        layout.addWidget(self.memory_display)

        # Update memory info
        self.update_memory_info()

        return widget

    def create_settings_tab(self):
        """Create settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        settings_title = QLabel("Settings")
        settings_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(settings_title)

        # Theme selection
        theme_label = QLabel("Theme: Dark Mode 🌙")
        theme_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(theme_label)

        # About section
        about_label = QLabel("About")
        about_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        layout.addWidget(about_label)

        about_text = QLabel(
            "Lyrixa AI Assistant v2.0\n"
            "Modern Dark Mode Interface\n"
            "With Knowledge Responder\n\n"
            "🧠 Advanced Memory System\n"
            "💬 Intelligent Conversations\n"
            "🔍 Project Knowledge Base\n"
            "🌙 Beautiful Dark Theme"
        )
        about_text.setFont(QFont("Segoe UI", 9))
        about_text.setWordWrap(True)
        layout.addWidget(about_text)

        layout.addStretch()
        return widget

    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        clear_action = file_menu.addAction("Clear Chat")
        clear_action.triggered.connect(self.clear_chat)

        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = help_menu.addAction("About Lyrixa")
        about_action.triggered.connect(self.show_about)

    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Status messages
        if self.engine:
            self.status_bar.showMessage("🟢 Lyrixa AI Ready - Ask me anything!")
        else:
            self.status_bar.showMessage("🟡 Lyrixa AI Initializing...")

    def apply_dark_theme(self):
        """Apply modern dark theme."""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }

            /* Text Areas */
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
                color: #ffffff;
                selection-background-color: #4a4a4a;
            }

            /* Input Fields */
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #404040;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 11px;
            }

            QLineEdit:focus {
                border-color: #0078d4;
                background-color: #333333;
            }

            /* Buttons */
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: white;
                font-weight: bold;
                font-size: 11px;
            }

            QPushButton:hover {
                background-color: #106ebe;
            }

            QPushButton:pressed {
                background-color: #005a9e;
            }

            /* Labels */
            QLabel {
                color: #ffffff;
            }

            /* Frames */
            QFrame {
                background-color: #252525;
                border: 1px solid #404040;
                border-radius: 10px;
            }

            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #404040;
                border-radius: 8px;
                background-color: #2d2d2d;
            }

            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }

            QTabBar::tab:selected {
                background-color: #0078d4;
            }

            QTabBar::tab:hover {
                background-color: #505050;
            }

            /* Status Bar */
            QStatusBar {
                background-color: #1e1e1e;
                border-top: 1px solid #404040;
                color: #ffffff;
            }

            /* Menu Bar */
            QMenuBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-bottom: 1px solid #404040;
            }

            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }

            QMenuBar::item:selected {
                background-color: #404040;
                border-radius: 4px;
            }

            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px;
            }

            QMenu::item {
                padding: 6px 12px;
                border-radius: 4px;
            }

            QMenu::item:selected {
                background-color: #0078d4;
            }

            /* Splitter */
            QSplitter::handle {
                background-color: #404040;
                width: 2px;
            }

            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """)

    def setup_connections(self):
        """Setup signal connections."""
        if self.input_field and self.send_button:
            self.input_field.returnPressed.connect(self.send_message)
            self.send_button.clicked.connect(self.send_message)

    def send_message(self):
        """Send user message to Lyrixa."""
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        if not self.engine:
            self.add_to_chat("System", "❌ Lyrixa engine not available", "#ff6b6b")
            return

        # Clear input and show typing indicator
        self.input_field.clear()
        self.add_to_chat("You", user_input, "#4a9eff")
        self.show_typing_indicator(True)

        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        # Start background processing
        self.worker_thread = LyrixaWorkerThread(self.engine, user_input)
        self.worker_thread.response_ready.connect(self.handle_response)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.start()

    def handle_response(self, response):
        """Handle Lyrixa response."""
        self.show_typing_indicator(False)

        # Extract response text
        response_text = response.get("text", "No response")

        # Check if knowledge responder was used
        used_knowledge = any(
            "Knowledge Responder" in note
            for note in response.get("adaptation_notes", [])
        )

        # Add indicator for knowledge responder usage
        if used_knowledge:
            response_text = "🧠 " + response_text

        self.add_to_chat("Lyrixa", response_text, "#51cf66")

        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

        # Update status
        status_msg = "🟢 Response ready"
        if used_knowledge:
            status_msg += " (Knowledge Responder used)"
        self.status_bar.showMessage(status_msg, 3000)

    def handle_error(self, error_msg):
        """Handle processing error."""
        self.show_typing_indicator(False)
        self.add_to_chat("System", f"❌ Error: {error_msg}", "#ff6b6b")

        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

        self.status_bar.showMessage("🔴 Error occurred", 3000)

    def add_to_chat(self, sender, message, color="#ffffff"):
        """Add message to chat display."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format message with colors
        formatted_message = f"""
        <div style="margin-bottom: 12px;">
            <span style="color: #888888; font-size: 10px;">[{timestamp}]</span>
            <span style="color: {color}; font-weight: bold; font-size: 12px;"> {sender}:</span>
            <br>
            <span style="color: #ffffff; font-size: 11px; margin-left: 20px;">{message}</span>
        </div>
        """

        self.chat_display.append(formatted_message)

        # Auto-scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def show_typing_indicator(self, show):
        """Show/hide typing indicator."""
        if show:
            self.typing_indicator.show()
        else:
            self.typing_indicator.hide()

    def clear_chat(self):
        """Clear chat history."""
        self.chat_display.clear()
        self.add_to_chat("System", "Chat cleared. How can I help you?", "#ffd43b")

    def load_knowledge(self):
        """Load project knowledge into memory."""
        if not self.memory_system:
            self.show_error("Error", "Memory system not available")
            return

        try:
            # Show loading message
            self.status_bar.showMessage("📚 Loading project knowledge...")

            # Import and run knowledge loader
            from load_project_knowledge import load_project_knowledge

            # Run async loading
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            stats = loop.run_until_complete(
                load_project_knowledge(
                    "lyrixa_project_knowledge_seed.json", verbose=False
                )
            )
            loop.close()

            self.add_to_chat(
                "System",
                f"📚 Loaded {stats['loaded']} knowledge items successfully!",
                "#51cf66",
            )
            self.status_bar.showMessage("✅ Knowledge loaded successfully", 3000)
            self.update_memory_info()

        except Exception as e:
            self.add_to_chat("System", f"❌ Failed to load knowledge: {e}", "#ff6b6b")
            self.status_bar.showMessage("❌ Knowledge loading failed", 3000)

    def test_system(self):
        """Test system functionality."""
        self.add_to_chat("System", "🧪 Running system test...", "#ffd43b")

        # Test basic functionality
        test_queries = [
            "What is Aetherra?",
            "Tell me about Lyrixa",
            "How can you help me?",
        ]

        for query in test_queries:
            self.add_to_chat("Test", query, "#ff8cc8")
            # Note: For real testing, you'd process these through the engine

    def update_system_status(self):
        """Update system status display."""
        status_text = "🔧 SYSTEM STATUS\n" + "=" * 20 + "\n\n"

        if self.engine:
            status_text += "✅ Lyrixa Engine: Ready\n"
        else:
            status_text += "❌ Lyrixa Engine: Not Available\n"

        if self.memory_system:
            status_text += "✅ Memory System: Ready\n"
        else:
            status_text += "❌ Memory System: Not Available\n"

        if (
            hasattr(self.engine, "knowledge_responder")
            and self.engine.knowledge_responder
        ):
            status_text += "✅ Knowledge Responder: Ready\n"
        else:
            status_text += "❌ Knowledge Responder: Not Available\n"

        status_text += f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}"

        self.status_display.setText(status_text)

    def update_memory_info(self):
        """Update memory information display."""
        if not self.memory_system:
            self.memory_display.setText("❌ Memory system not available")
            return

        try:
            # Get memory statistics
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            stats = loop.run_until_complete(self.memory_system.get_memory_statistics())
            loop.close()

            info_text = "🧠 MEMORY STATISTICS\n" + "=" * 25 + "\n\n"
            info_text += f"📊 Total Memories: {stats.get('total_memories', 0)}\n"
            info_text += (
                f"🎯 Average Confidence: {stats.get('average_confidence', 0):.2f}\n"
            )
            info_text += f"🔍 Vector Support: {'Yes' if stats.get('vector_support_enabled') else 'No'}\n"

            memory_types = stats.get("memory_types", {})
            if memory_types:
                info_text += "\n📁 Memory Types:\n"
                for mem_type, count in memory_types.items():
                    info_text += f"  • {mem_type}: {count}\n"

            self.memory_display.setText(info_text)

        except Exception as e:
            self.memory_display.setText(f"❌ Error getting memory stats: {e}")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About Lyrixa AI Assistant",
            "🌙 Lyrixa AI Assistant v2.0\n\n"
            "Modern Dark Mode Interface with:\n"
            "• Advanced conversation engine\n"
            "• Knowledge responder system\n"
            "• Memory-based learning\n"
            "• Beautiful dark theme\n\n"
            "Built for the Aetherra platform",
        )

    def show_error(self, title, message):
        """Show error dialog."""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Handle application close."""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
        event.accept()


def main():
    """Main application entry point."""
    if not GUI_AVAILABLE:
        print("❌ GUI framework not available")
        return 1

    # Create application
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Lyrixa AI Assistant")
    app.setApplicationVersion("2.0")

    # Set application icon (if available)
    try:
        app.setWindowIcon(QIcon("assets/icons/lyrixa_icon.png"))
    except:
        pass  # Icon not required

    # Create and show main window
    window = ModernLyrixaGUI()
    window.show()

    # Add welcome message
    window.add_to_chat(
        "Lyrixa",
        "🌙 Welcome to Lyrixa AI Assistant!\n\n"
        "I'm here to help you with:\n"
        "• Aetherra platform questions\n"
        "• Coding assistance\n"
        "• Project guidance\n"
        "• General AI assistance\n\n"
        "Ask me anything to get started!",
        "#51cf66",
    )

    print("🚀 Lyrixa Modern GUI launched successfully!")

    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
