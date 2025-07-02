#!/usr/bin/env python3
"""
Neuroplex - AI-Native Development Environment
============================================

The main Neuroplex development environment with integrated AI chat,
providing a unified experience for AI-native programming.

Features:
- Full development environment with dark mode
- Integrated AI chat router with multiple personalities
- Real-time collaboration with AI assistant
- Plugin system integration
- Modern dark theme interface
"""

import sys
from pathlib import Path

# Add project paths for core modules
project_root = Path(__file__).parent.parent.parent.parent
core_path = project_root / "core"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(core_path))

# Qt imports
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont, QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPushButton,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    QT_AVAILABLE = True
except ImportError as e:
    print(f"❌ PySide6 not available: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

# Import AI Chat Router (required)
try:
    from core.chat_router import NeuroCodeChatRouter
    CHAT_ROUTER_AVAILABLE = True
    print("✅ NeuroCode Chat Router loaded")
except ImportError:
    try:
        # Try direct import since we added core to path
        from chat_router import NeuroCodeChatRouter  # type: ignore
        CHAT_ROUTER_AVAILABLE = True
        print("✅ NeuroCode Chat Router loaded")
    except ImportError as e:
        print(f"❌ Chat router is required but not available: {e}")
        print("The system cannot function without the chat router.")
        sys.exit(1)

# Import NeuroChat components (enhanced chat interface)
try:
    # Import from same directory
    from neuro_chat import NeuroChatInterface
    NEUROCHAT_AVAILABLE = True
    print("✅ Advanced NeuroChat interface loaded")
except ImportError as e:
    NEUROCHAT_AVAILABLE = False
    print(f"⚠️  NeuroChat interface not available: {e}")
    print("ℹ️  Using built-in chat interface")


class NeuroplexWindow(QMainWindow):
    """Main Neuroplex window with integrated AI chat and dark mode"""

    def __init__(self):
        super().__init__()
        self.chat_router = None
        self.current_personality = "default"
        self.setup_ui()
        self.init_components()

    def setup_ui(self):
        """Setup the main window UI with dark mode"""
        self.setWindowTitle("🧬 Neuroplex - AI-Native Development Environment")
        self.setGeometry(100, 100, 1600, 1000)

        # Apply dark theme
        self.setStyleSheet(self.get_dark_theme())

        # Create central widget
        self.create_central_widget()

        # Status bar
        self.statusBar().showMessage("🧬 Neuroplex ready - AI-native development at your fingertips!")

    def get_dark_theme(self):
        """Get the dark theme stylesheet"""
        return """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }

        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }

        QTabWidget::pane {
            border: 1px solid #404040;
            background-color: #252525;
            border-radius: 6px;
        }

        QTabBar::tab {
            background-color: #404040;
            color: #ffffff;
            padding: 12px 20px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 100px;
        }

        QTabBar::tab:selected {
            background-color: #0078d4;
            color: #ffffff;
        }

        QTabBar::tab:hover {
            background-color: #505050;
        }

        QLabel {
            color: #ffffff;
            font-weight: 500;
        }

        QTextEdit {
            background-color: #252525;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 12px;
            color: #ffffff;
            font-family: 'Consolas', 'Monaco', monospace;
            selection-background-color: #0078d4;
        }

        QLineEdit {
            background-color: #252525;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 8px 12px;
            color: #ffffff;
            font-size: 14px;
        }

        QLineEdit:focus {
            border: 2px solid #0078d4;
        }

        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #106ebe;
        }

        QPushButton:pressed {
            background-color: #005a9e;
        }

        QPushButton:disabled {
            background-color: #404040;
            color: #808080;
        }

        QScrollArea {
            background-color: #1e1e1e;
            border: none;
        }

        QScrollBar:vertical {
            background-color: #252525;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #404040;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #505050;
        }

        QSplitter::handle {
            background-color: #404040;
        }

        QFrame {
            background-color: #1e1e1e;
            border: none;
        }

        QStatusBar {
            background-color: #252525;
            color: #ffffff;
            border-top: 1px solid #404040;
        }
        """

    def create_central_widget(self):
        """Create the main central widget"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Development tools
        left_panel = self.create_development_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - AI Chat
        right_panel = self.create_ai_chat_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions (70% development, 30% chat)
        main_splitter.setSizes([1120, 480])

        main_layout.addWidget(main_splitter)

    def create_development_panel(self):
        """Create the development tools panel"""
        dev_widget = QWidget()
        dev_layout = QVBoxLayout(dev_widget)
        dev_layout.setContentsMargins(8, 8, 4, 8)

        # Development tabs
        dev_tabs = QTabWidget()

        # Code Editor tab
        code_tab = self.create_code_editor_tab()
        dev_tabs.addTab(code_tab, "📝 Code Editor")

        # Project Explorer tab
        project_tab = self.create_project_explorer_tab()
        dev_tabs.addTab(project_tab, "📁 Project Explorer")

        # Terminal tab
        terminal_tab = self.create_terminal_tab()
        dev_tabs.addTab(terminal_tab, "⚡ Terminal")

        # Plugin Manager tab
        plugins_tab = self.create_plugins_tab()
        dev_tabs.addTab(plugins_tab, "🔌 Plugins")

        dev_layout.addWidget(dev_tabs)

        return dev_widget

    def create_ai_chat_panel(self):
        """Create the AI chat panel using NeuroChat or built-in chat"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(4, 8, 8, 8)

        # Chat header with personality selector
        header_layout = QHBoxLayout()

        chat_title = QLabel("🤖 AI Assistant")
        chat_title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(chat_title)

        header_layout.addStretch()

        # Personality selector
        personality_btn = QPushButton(f"👤 {self.current_personality.title()}")
        personality_btn.clicked.connect(self.cycle_personality)
        header_layout.addWidget(personality_btn)

        chat_layout.addLayout(header_layout)

        # Use advanced NeuroChat interface if available, otherwise use built-in
        if NEUROCHAT_AVAILABLE:
            try:
                # Create NeuroChat interface and extract the tab widget for embedding
                chat_interface = NeuroChatInterface()

                # Get the central tab widget from NeuroChat
                chat_tabs = chat_interface.centralWidget()
                if chat_tabs:
                    # Embed the entire tabbed interface
                    chat_layout.addWidget(chat_tabs)
                    print("✅ Advanced NeuroChat interface integrated (with tabs)")
                else:
                    # Fallback to embedded chat
                    embedded_chat = self.create_embedded_chat()
                    chat_layout.addWidget(embedded_chat)
                    print("⚠️ Using embedded chat fallback")
            except Exception as e:
                print(f"⚠️ Error loading advanced NeuroChat interface: {e}")
                embedded_chat = self.create_embedded_chat()
                chat_layout.addWidget(embedded_chat)
        else:
            # Use built-in chat interface
            embedded_chat = self.create_embedded_chat()
            chat_layout.addWidget(embedded_chat)

        return chat_widget

    def create_embedded_chat(self):
        """Create an embedded chat interface"""
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlainText("🤖 AI Assistant: Hello! I'm ready to help you with your development tasks.\n\n💡 Ask me anything about coding, debugging, or project planning!")
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask me anything about your code...")
        self.chat_input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_btn)

        chat_layout.addLayout(input_layout)

        return chat_container

    def create_code_editor_tab(self):
        """Create the code editor tab"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        # Editor toolbar
        toolbar_layout = QHBoxLayout()

        new_btn = QPushButton("New")
        open_btn = QPushButton("Open")
        save_btn = QPushButton("Save")
        run_btn = QPushButton("▶ Run")

        toolbar_layout.addWidget(new_btn)
        toolbar_layout.addWidget(open_btn)
        toolbar_layout.addWidget(save_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(run_btn)

        editor_layout.addLayout(toolbar_layout)

        # Code editor
        code_editor = QTextEdit()
        code_editor.setFont(QFont("Consolas", 12))
        code_editor.setPlainText("""# Welcome to Neuroplex - AI-Native Development
# This is your code editor with AI assistance

def hello_neuroplex():
    print("🧬 Welcome to the future of programming!")
    print("AI is ready to help you code smarter.")

# Try asking the AI assistant about this code!
hello_neuroplex()
""")
        editor_layout.addWidget(code_editor)

        return editor_widget

    def create_project_explorer_tab(self):
        """Create the project explorer tab"""
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout(explorer_widget)

        # Project tree header
        header = QLabel("📁 Project Structure")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        explorer_layout.addWidget(header)

        # Project tree (simplified)
        tree_display = QTextEdit()
        tree_display.setReadOnly(True)
        tree_display.setPlainText("""📁 NeuroCode Project/
├── 📁 src/
│   ├── 📁 neurocode/
│   │   ├── 📁 core/
│   │   ├── 📁 ui/
│   │   └── 📄 __init__.py
├── 📁 core/
│   ├── 📄 chat_router.py
│   └── 📄 functions.py
├── 📄 neurocode_launcher.py
└── 📄 README.md""")
        explorer_layout.addWidget(tree_display)

        return explorer_widget

    def create_terminal_tab(self):
        """Create the terminal tab"""
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout(terminal_widget)

        # Terminal header
        header = QLabel("⚡ Integrated Terminal")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        terminal_layout.addWidget(header)

        # Terminal display
        terminal_display = QTextEdit()
        terminal_display.setFont(QFont("Consolas", 10))
        terminal_display.setPlainText("""PS C:\\Users\\enigm\\Desktop\\NeuroCode Project> python neurocode_launcher.py
🧬 NeuroCode Project - AI-Native Programming Language
✅ All systems operational
✅ AI assistant ready
✅ Plugin system active

Neuroplex> _""")
        terminal_layout.addWidget(terminal_display)

        # Terminal input
        terminal_input = QLineEdit()
        terminal_input.setPlaceholderText("Enter command...")
        terminal_layout.addWidget(terminal_input)

        return terminal_widget

    def create_plugins_tab(self):
        """Create the plugins management tab"""
        plugins_widget = QWidget()
        plugins_layout = QVBoxLayout(plugins_widget)

        # Plugins header
        header = QLabel("🔌 Plugin Manager")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        plugins_layout.addWidget(header)

        # Plugin list
        plugins_display = QTextEdit()
        plugins_display.setReadOnly(True)
        plugins_display.setPlainText("""✅ [StdLib] sysmon - System performance monitoring
✅ [StdLib] optimizer - Code and system performance optimization
✅ [StdLib] selfrepair - Automatic debugging and repair system
✅ [StdLib] whisper - Audio transcription and speech processing
✅ [StdLib] reflector - Behavior analysis and self-reflection tools
✅ [StdLib] executor - Command scheduling and execution management
✅ [StdLib] coretools - File access and core utility tools

📊 7 plugins loaded and active
🟢 All systems operational""")
        plugins_layout.addWidget(plugins_display)

        return plugins_widget

    def init_components(self):
        """Initialize the chat router and other components"""
        try:
            self.chat_router = NeuroCodeChatRouter(demo_mode=False, debug_mode=False)
            self.chat_router.set_personality(self.current_personality)
            print(f"✅ Chat router initialized with '{self.current_personality}' personality")
        except Exception as e:
            print(f"❌ Failed to initialize chat router: {e}")

    def cycle_personality(self):
        """Cycle through available AI personalities"""
        personalities = ["default", "mentor", "sassy", "dev_focused"]
        current_index = personalities.index(self.current_personality)
        next_index = (current_index + 1) % len(personalities)
        self.current_personality = personalities[next_index]

        if self.chat_router:
            self.chat_router.set_personality(self.current_personality)

        # Update button text
        sender = self.sender()
        if isinstance(sender, QPushButton):
            sender.setText(f"👤 {self.current_personality.title()}")

        # Add message to chat
        if hasattr(self, 'chat_display'):
            self.chat_display.append(f"\n🔄 Switched to '{self.current_personality}' personality")

    def send_message(self):
        """Send a message to the AI assistant"""
        if not hasattr(self, 'chat_input') or not self.chat_input.text().strip():
            return

        message = self.chat_input.text().strip()
        self.chat_input.clear()

        # Add user message to display
        if hasattr(self, 'chat_display'):
            self.chat_display.append(f"\n👤 You: {message}")

            if self.chat_router:
                try:
                    response = self.chat_router.process_message(message)
                    self.chat_display.append(f"\n🤖 AI: {response}")
                except Exception as e:
                    self.chat_display.append(f"\n⚠️ Error: {e}")
            else:
                self.chat_display.append(f"\n🤖 AI: I'm processing your message: '{message}'")

            # Scroll to bottom
            scrollbar = self.chat_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())


def main():
    """Main function to launch Neuroplex"""
    if not QT_AVAILABLE:
        print("❌ Cannot start Neuroplex: PySide6 not available")
        return False

    app = QApplication(sys.argv)
    app.setApplicationName("Neuroplex")
    app.setApplicationVersion("2.0.0")

    # Set application icon
    app.setWindowIcon(QIcon("Neuroplex.ico") if Path("Neuroplex.ico").exists() else QIcon())

    window = NeuroplexWindow()
    window.show()

    print("✅ Neuroplex launched successfully")
    print("🧬 AI-native development environment ready")

    try:
        return app.exec()
    except KeyboardInterrupt:
        print("\n👋 Neuroplex shutting down...")
        return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
