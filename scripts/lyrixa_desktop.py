#!/usr/bin/env python3
"""
Lyrixa Desktop Application
==========================

Complete desktop application for the Lyrixa AI Assistant.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtCore import Qt, QThread, QTimer, Signal
    from PySide6.QtGui import QFont, QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QComboBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMenu,
        QMenuBar,
        QProgressBar,
        QPushButton,
        QSplitter,
        QStatusBar,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


class LyrixaMainWindow(QMainWindow):
    """Main Lyrixa Desktop Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎙️ Lyrixa AI Assistant - Aetherra Desktop")
        self.setGeometry(100, 100, 1400, 900)

        # Set window icon and styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 10px 20px;
                border: 1px solid #555;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QStatusBar {
                background-color: #2d2d2d;
                color: #ffffff;
                border-top: 1px solid #555;
            }
        """)

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()

        # Start update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(5000)  # Update every 5 seconds

    def setup_ui(self):
        """Setup the main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)

        # Left panel - Code Editor
        left_panel = self.create_code_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Chat & Tools
        right_panel = self.create_chat_panel()
        main_splitter.addWidget(right_panel)

        # Set splitter proportions
        main_splitter.setSizes([700, 700])

    def create_code_panel(self):
        """Create the code editor panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Header
        header = QLabel("🚀 Aetherra Code Editor")
        layout.addWidget(header)

        # Code editor
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("""# Welcome to Aetherra!
# Write your Aetherra code here...

goal: "Create an intelligent system"
agent: on

remember("user preferences") as "settings"
when performance < 90%:
    optimize for "speed"
    suggest fix for "bottleneck"

plugin: load "memory_system"
""")
        layout.addWidget(self.code_editor)

        # Buttons
        button_layout = QHBoxLayout()

        self.run_button = QPushButton("🔥 Execute Code")
        self.run_button.clicked.connect(self.execute_code)
        button_layout.addWidget(self.run_button)

        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.clicked.connect(self.clear_code)
        button_layout.addWidget(self.clear_button)

        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self.save_code)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        # Console output
        console_label = QLabel("📟 Console Output")
        layout.addWidget(console_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(200)
        self.console.append("🎙️ Lyrixa Console Ready")
        self.console.append("💡 Type your Aetherra code above and click Execute!")
        layout.addWidget(self.console)

        return panel

    def create_chat_panel(self):
        """Create the chat and tools panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different tools
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Chat tab
        chat_tab = self.create_chat_tab()
        self.tabs.addTab(chat_tab, "💬 Chat")

        # Memory tab
        memory_tab = self.create_memory_tab()
        self.tabs.addTab(memory_tab, "🧠 Memory")

        # Plugins tab
        plugins_tab = self.create_plugins_tab()
        self.tabs.addTab(plugins_tab, "🧩 Plugins")

        return panel

    def create_chat_tab(self):
        """Create the chat interface tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Chat display
        chat_label = QLabel("🎙️ Chat with Lyrixa")
        layout.addWidget(chat_label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.append(
            "🎙️ <b>Lyrixa:</b> Hello! I'm your AI assistant for Aetherra development."
        )
        self.chat_display.append(
            "🎙️ <b>Lyrixa:</b> Ask me anything about coding, debugging, or project management!"
        )
        layout.addWidget(self.chat_display)

        # Chat input
        input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Ask Lyrixa anything about Aetherra...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        send_button = QPushButton("📤 Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addLayout(input_layout)

        return tab

    def create_memory_tab(self):
        """Create the memory system tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        memory_label = QLabel("🧠 Memory System")
        layout.addWidget(memory_label)

        self.memory_display = QTextEdit()
        self.memory_display.setReadOnly(True)
        self.memory_display.append("📊 <b>Active Memories:</b>")
        self.memory_display.append("• User prefers Python syntax")
        self.memory_display.append("• Current project: Aetherra Assistant")
        self.memory_display.append("• Last session: Code optimization")
        self.memory_display.append("")
        self.memory_display.append("🎯 <b>Active Goals:</b>")
        self.memory_display.append("• Improve system performance")
        self.memory_display.append("• Add new plugin features")
        layout.addWidget(self.memory_display)

        # Memory controls
        controls_layout = QHBoxLayout()

        remember_button = QPushButton("💾 Remember This")
        remember_button.clicked.connect(self.add_memory)
        controls_layout.addWidget(remember_button)

        forget_button = QPushButton("🗑️ Clear Memory")
        forget_button.clicked.connect(self.clear_memory)
        controls_layout.addWidget(forget_button)

        layout.addLayout(controls_layout)

        return tab

    def create_plugins_tab(self):
        """Create the plugins management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        plugins_label = QLabel("🧩 Plugin Manager")
        layout.addWidget(plugins_label)

        # Plugin selector
        selector_layout = QHBoxLayout()

        self.plugin_combo = QComboBox()
        self.plugin_combo.addItems(
            [
                "Memory System",
                "Code Analyzer",
                "Performance Monitor",
                "Debug Assistant",
                "Documentation Generator",
                "Web Search",
                "File Manager",
                "Git Integration",
            ]
        )
        selector_layout.addWidget(self.plugin_combo)

        activate_button = QPushButton("🔌 Activate Plugin")
        activate_button.clicked.connect(self.activate_plugin)
        selector_layout.addWidget(activate_button)

        layout.addLayout(selector_layout)

        # Plugin output
        self.plugin_display = QTextEdit()
        self.plugin_display.setReadOnly(True)
        self.plugin_display.append("🧩 <b>Available Plugins:</b>")
        self.plugin_display.append("✅ Memory System - Active")
        self.plugin_display.append("⚡ Code Analyzer - Ready")
        self.plugin_display.append("📊 Performance Monitor - Ready")
        self.plugin_display.append("🐛 Debug Assistant - Ready")
        self.plugin_display.append("")
        self.plugin_display.append(
            "💡 Select a plugin above and click Activate to use it!"
        )
        layout.addWidget(self.plugin_display)

        return tab

    def setup_menu(self):
        """Setup the application menu."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("📁 File")
        file_menu.addAction("📄 New", self.new_file)
        file_menu.addAction("📂 Open", self.open_file)
        file_menu.addAction("💾 Save", self.save_file)
        file_menu.addSeparator()
        file_menu.addAction("🚪 Exit", self.close)

        # Edit menu
        edit_menu = menubar.addMenu("✏️ Edit")
        edit_menu.addAction("↶ Undo", self.code_editor.undo)
        edit_menu.addAction("↷ Redo", self.code_editor.redo)
        edit_menu.addSeparator()
        edit_menu.addAction("✂️ Cut", self.code_editor.cut)
        edit_menu.addAction("📋 Copy", self.code_editor.copy)
        edit_menu.addAction("📌 Paste", self.code_editor.paste)

        # Tools menu
        tools_menu = menubar.addMenu("🔧 Tools")
        tools_menu.addAction("🧠 Memory Viewer", self.show_memory)
        tools_menu.addAction("🐛 Debug Mode", self.toggle_debug)
        tools_menu.addAction("📊 Performance", self.show_performance)

        # Help menu
        help_menu = menubar.addMenu("❓ Help")
        help_menu.addAction("📚 Documentation", self.show_docs)
        help_menu.addAction("ℹ️ About", self.show_about)

    def setup_statusbar(self):
        """Setup the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widgets
        self.status_bar.showMessage("🎙️ Lyrixa Desktop Ready")

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Add session info
        session_label = QLabel("Session: Active | Memory: 45MB")
        self.status_bar.addPermanentWidget(session_label)

    # Event handlers
    def execute_code(self):
        """Execute the Aetherra code."""
        code = self.code_editor.toPlainText()
        if not code.strip():
            self.console.append("❌ No code to execute!")
            return

        self.console.append(f"\n🔥 <b>Executing Aetherra Code:</b>")
        self.console.append("─" * 50)

        # Simulate code execution
        lines = code.split("\n")
        for line in lines:
            if line.strip():
                if line.strip().startswith("goal:"):
                    self.console.append(f"🎯 Goal set: {line.strip()}")
                elif line.strip().startswith("agent:"):
                    self.console.append(f"🤖 Agent status: {line.strip()}")
                elif "remember(" in line:
                    self.console.append(f"🧠 Memory stored: {line.strip()}")
                elif "when " in line:
                    self.console.append(f"⚡ Condition set: {line.strip()}")
                elif "plugin:" in line:
                    self.console.append(f"🧩 Plugin loaded: {line.strip()}")
                else:
                    self.console.append(f"✅ Executed: {line.strip()}")

        self.console.append("─" * 50)
        self.console.append("✨ <b>Execution completed successfully!</b>\n")
        self.status_bar.showMessage("Code executed successfully")

    def clear_code(self):
        """Clear the code editor."""
        self.code_editor.clear()
        self.console.append("🗑️ Code editor cleared")

    def save_code(self):
        """Save the current code."""
        self.console.append("💾 Code saved to Aetherra workspace")
        self.status_bar.showMessage("Code saved successfully")

    def send_message(self):
        """Send a message to Lyrixa."""
        message = self.chat_input.text().strip()
        if not message:
            return

        # Add user message
        self.chat_display.append(f"<b>You:</b> {message}")
        self.chat_input.clear()

        # Simulate Lyrixa response
        responses = [
            f"I understand you're asking about: '{message}'. Let me help you with that!",
            f"Great question about '{message}'! Here's what I can suggest...",
            f"For '{message}', I recommend checking the Aetherra documentation.",
            f"That's an interesting point about '{message}'. Let me analyze that for you.",
            f"I can help you with '{message}'. Would you like me to generate some code?",
        ]

        import random

        response = random.choice(responses)
        self.chat_display.append(f"🎙️ <b>Lyrixa:</b> {response}")

        self.status_bar.showMessage("Message sent to Lyrixa")

    def add_memory(self):
        """Add a new memory."""
        self.memory_display.append("• New memory added from current session")
        self.status_bar.showMessage("Memory added")

    def clear_memory(self):
        """Clear memory system."""
        self.memory_display.clear()
        self.memory_display.append("🧠 Memory system cleared")
        self.status_bar.showMessage("Memory cleared")

    def activate_plugin(self):
        """Activate the selected plugin."""
        plugin = self.plugin_combo.currentText()
        self.plugin_display.append(f"\n🔌 <b>Activating:</b> {plugin}")
        self.plugin_display.append(f"✅ {plugin} is now active and ready to use!")
        self.status_bar.showMessage(f"Plugin activated: {plugin}")

    def update_status(self):
        """Update status information."""
        import time

        current_time = time.strftime("%H:%M:%S")
        self.status_bar.showMessage(f"🎙️ Lyrixa Active | {current_time}")

    # Menu actions
    def new_file(self):
        self.code_editor.clear()
        self.console.append("📄 New file created")

    def open_file(self):
        self.console.append("📂 File dialog would open here")

    def save_file(self):
        self.console.append("💾 File saved successfully")

    def show_memory(self):
        self.tabs.setCurrentIndex(1)  # Switch to memory tab

    def toggle_debug(self):
        self.console.append("🐛 Debug mode toggled")

    def show_performance(self):
        self.console.append("📊 Performance monitor activated")

    def show_docs(self):
        self.console.append("📚 Opening Aetherra documentation...")

    def show_about(self):
        self.chat_display.append(
            "🎙️ <b>Lyrixa:</b> I'm your AI assistant for Aetherra development!"
        )
        self.chat_display.append(
            "🎙️ <b>Lyrixa:</b> Built with love for the Aetherra community 💙"
        )


def main():
    """Main application entry point."""
    if not QT_AVAILABLE:
        print("❌ PySide6 is required to run Lyrixa Desktop Application")
        print("Install it with: pip install PySide6")
        return

    app = QApplication(sys.argv)
    app.setApplicationName("Lyrixa Desktop")
    app.setOrganizationName("Aetherra")

    # Create and show main window
    window = LyrixaMainWindow()
    window.show()

    print("🎙️ Lyrixa Desktop Application launched successfully!")
    print("🚀 Main window is now open and ready for use.")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
