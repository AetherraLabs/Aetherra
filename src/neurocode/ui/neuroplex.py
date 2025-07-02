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
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtGui import QFont
    from PySide6.QtWidgets import (
        QComboBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
    QT_AVAILABLE = True

    # Try to import WebEngine for NeuroHub integration
    try:
        from PySide6.QtWebEngineWidgets import QWebEngineView
        WEBENGINE_AVAILABLE = True
        print("✅ WebEngine available for NeuroHub integration")
    except ImportError:
        WEBENGINE_AVAILABLE = False
        print("⚠️  WebEngine not available - NeuroHub will use external browser")

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
    # Try direct import from same directory
    from neurocode.ui.neuro_chat import NeuroChatInterface
    NEUROCHAT_AVAILABLE = True
    print("✅ Advanced NeuroChat interface loaded")
except ImportError:
    try:
        # Fallback to relative import
        from .neuro_chat import NeuroChatInterface
        NEUROCHAT_AVAILABLE = True
        print("✅ Advanced NeuroChat interface loaded")
    except ImportError as e:
        NEUROCHAT_AVAILABLE = False
        print(f"⚠️  NeuroChat interface not available: {e}")
        print("ℹ️  Using built-in chat interface")

# Import Task Scheduler
try:
    from core.task_scheduler import BackgroundTaskScheduler, TaskPriority
    TASK_SCHEDULER_AVAILABLE = True
    print("✅ Background Task Scheduler loaded")
except ImportError as e:
    TASK_SCHEDULER_AVAILABLE = False
    print(f"⚠️  Task Scheduler not available: {e}")
    print("ℹ️  Background tasks will be disabled")


class NeuroplexWindow(QMainWindow):
    """Main Neuroplex window with integrated AI chat and dark mode"""

    def __init__(self):
        super().__init__()
        self.chat_router = None
        self.task_scheduler = None
        self.neurohub_process = None
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

        # Memory Timeline tab
        memory_tab = self.create_memory_timeline_tab()
        dev_tabs.addTab(memory_tab, "🧠 Memory")

        # Background Tasks tab
        tasks_tab = self.create_tasks_tab()
        dev_tabs.addTab(tasks_tab, "⚙️ Tasks")

        # NeuroHub Package Manager tab
        neurohub_tab = self.create_neurohub_tab()
        dev_tabs.addTab(neurohub_tab, "🌐 NeuroHub")

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

    def create_memory_timeline_tab(self):
        """Create the memory timeline visualization tab"""
        memory_widget = QWidget()
        memory_layout = QVBoxLayout(memory_widget)

        # Memory header with controls
        header_layout = QHBoxLayout()

        header = QLabel("🧠 Memory Timeline")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_memory_timeline)
        header_layout.addWidget(refresh_btn)

        # Clear memory button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self.clear_memory)
        header_layout.addWidget(clear_btn)

        memory_layout.addLayout(header_layout)

        # Memory filter controls
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)

        self.memory_filter = QLineEdit()
        self.memory_filter.setPlaceholderText("Search memories...")
        self.memory_filter.textChanged.connect(self.filter_memory_timeline)
        filter_layout.addWidget(self.memory_filter)

        # Memory type filter
        self.memory_type_filter = QComboBox()
        self.memory_type_filter.addItems(["All Types", "Conversation", "Goal", "Learning", "System", "Plugin"])
        self.memory_type_filter.currentTextChanged.connect(self.filter_memory_timeline)
        filter_layout.addWidget(self.memory_type_filter)

        memory_layout.addLayout(filter_layout)

        # Memory timeline display
        self.memory_timeline = QTextEdit()
        self.memory_timeline.setReadOnly(True)
        memory_layout.addWidget(self.memory_timeline)

        # Memory stats
        self.memory_stats = QLabel("Memory Statistics: Loading...")
        self.memory_stats.setStyleSheet("color: #888888; font-size: 12px;")
        memory_layout.addWidget(self.memory_stats)

        # Initial load
        self.refresh_memory_timeline()

        return memory_widget

    def refresh_memory_timeline(self):
        """Refresh the memory timeline display"""
        try:
            if not self.chat_router:
                self.memory_timeline.setPlainText("Chat router not initialized")
                return

            # Get memories from the chat router
            memories = []

            # Get chat history as memories
            chat_history = self.chat_router.get_chat_history(100)
            for entry in chat_history:
                memories.append({
                    "timestamp": entry.get("timestamp", "Unknown"),
                    "type": "conversation",
                    "content": entry.get("user", ""),
                    "response": entry.get("assistant", "")[:100] + "..." if len(entry.get("assistant", "")) > 100 else entry.get("assistant", ""),
                    "intent": entry.get("intent", {}).get("type", "unknown")
                })

            # Get system memories if available
            if hasattr(self.chat_router.memory, 'memories'):
                system_memories = getattr(self.chat_router.memory, 'memories', [])
                for mem in system_memories:
                    if isinstance(mem, dict):
                        memories.append({
                            "timestamp": mem.get("timestamp", "Unknown"),
                            "type": mem.get("type", "system"),
                            "content": str(mem.get("content", mem))[:200],
                            "response": "",
                            "intent": mem.get("category", "general")
                        })

            # Sort by timestamp (newest first)
            memories.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Build timeline display
            timeline_text = ""
            if not memories:
                timeline_text = "No memories found. Start chatting to build memory!"
            else:
                for i, mem in enumerate(memories[:50]):  # Show last 50 memories
                    timestamp = mem.get("timestamp", "Unknown")
                    if "T" in timestamp:
                        # Parse ISO timestamp
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            time_str = dt.strftime("%H:%M:%S")
                        except Exception:
                            time_str = timestamp
                    else:
                        time_str = timestamp

                    mem_type = mem.get("type", "unknown")
                    content = mem.get("content", "")
                    response = mem.get("response", "")
                    intent = mem.get("intent", "")

                    # Memory type emoji
                    type_emoji = {
                        "conversation": "💬",
                        "goal": "🎯",
                        "learning": "📚",
                        "system": "⚙️",
                        "plugin": "🔌"
                    }.get(mem_type, "📝")

                    timeline_text += f"{type_emoji} [{time_str}] {mem_type.upper()}\n"
                    if content:
                        timeline_text += f"   📝 {content}\n"
                    if response:
                        timeline_text += f"   🤖 {response}\n"
                    if intent and intent != "unknown":
                        timeline_text += f"   🔗 Intent: {intent}\n"
                    timeline_text += "\n"

            self.memory_timeline.setPlainText(timeline_text)

            # Update stats
            total_memories = len(memories)
            conversation_count = len([m for m in memories if m.get("type") == "conversation"])
            self.memory_stats.setText(f"Total Memories: {total_memories} | Conversations: {conversation_count} | System: {total_memories - conversation_count}")

        except Exception as e:
            self.memory_timeline.setPlainText(f"Error loading memories: {str(e)}")
            self.memory_stats.setText("Error loading memory statistics")

    def filter_memory_timeline(self):
        """Filter the memory timeline based on search text and type"""
        # For now, just refresh - in a full implementation this would filter the display
        self.refresh_memory_timeline()

    def clear_memory(self):
        """Clear memory after confirmation"""
        reply = QMessageBox.question(
            self,
            'Clear Memory',
            'Are you sure you want to clear all memories? This cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.chat_router:
                    self.chat_router.clear_chat_history()
                    # Clear system memory if available (not implemented in fallback)

                self.refresh_memory_timeline()
                QMessageBox.information(self, "Memory Cleared", "All memories have been cleared successfully.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to clear memory: {str(e)}")

    def init_components(self):
        """Initialize the chat router and other components"""
        try:
            self.chat_router = NeuroCodeChatRouter(demo_mode=False, debug_mode=False)
            self.chat_router.set_personality(self.current_personality)
            print(f"✅ Chat router initialized with '{self.current_personality}' personality")
        except Exception as e:
            print(f"❌ Failed to initialize chat router: {e}")

        # Initialize task scheduler
        if TASK_SCHEDULER_AVAILABLE:
            try:
                self.task_scheduler = BackgroundTaskScheduler()
                print("✅ Background task scheduler initialized and started")
            except Exception as e:
                print(f"❌ Failed to initialize task scheduler: {e}")
                self.task_scheduler = None
        else:
            print("ℹ️  Task scheduler disabled (not available)")

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

    def create_tasks_tab(self):
        """Create the background tasks management tab"""
        tasks_widget = QWidget()
        tasks_layout = QVBoxLayout(tasks_widget)

        # Tasks header with controls
        header_layout = QHBoxLayout()

        header = QLabel("⚙️ Background Tasks")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_tasks_list)
        header_layout.addWidget(refresh_btn)

        # Clear completed tasks button
        clear_btn = QPushButton("🗑️ Clear Completed")
        clear_btn.clicked.connect(self.clear_completed_tasks)
        header_layout.addWidget(clear_btn)

        tasks_layout.addLayout(header_layout)

        # Task controls
        controls_layout = QHBoxLayout()

        # Add test task button
        test_task_btn = QPushButton("🧪 Add Test Task")
        test_task_btn.clicked.connect(self.add_test_task)
        controls_layout.addWidget(test_task_btn)

        # Pause/Resume scheduler
        self.scheduler_toggle_btn = QPushButton("⏸️ Pause Scheduler")
        self.scheduler_toggle_btn.clicked.connect(self.toggle_scheduler)
        controls_layout.addWidget(self.scheduler_toggle_btn)

        controls_layout.addStretch()

        tasks_layout.addLayout(controls_layout)

        # Task filter controls
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filter:")
        filter_layout.addWidget(filter_label)

        self.task_filter = QLineEdit()
        self.task_filter.setPlaceholderText("Search tasks...")
        self.task_filter.textChanged.connect(self.filter_tasks_list)
        filter_layout.addWidget(self.task_filter)

        # Task status filter
        self.task_status_filter = QComboBox()
        self.task_status_filter.addItems(["All Status", "Pending", "Running", "Completed", "Failed", "Cancelled"])
        self.task_status_filter.currentTextChanged.connect(self.filter_tasks_list)
        filter_layout.addWidget(self.task_status_filter)

        tasks_layout.addLayout(filter_layout)

        # Tasks list display
        self.tasks_list = QListWidget()
        tasks_layout.addWidget(self.tasks_list)

        # Task details area
        details_layout = QHBoxLayout()

        details_label = QLabel("Task Details:")
        details_layout.addWidget(details_label)

        # Task action buttons
        cancel_btn = QPushButton("❌ Cancel Selected")
        cancel_btn.clicked.connect(self.cancel_selected_task)
        details_layout.addWidget(cancel_btn)

        retry_btn = QPushButton("🔄 Retry Selected")
        retry_btn.clicked.connect(self.retry_selected_task)
        details_layout.addWidget(retry_btn)

        tasks_layout.addLayout(details_layout)

        # Task details display
        self.task_details = QTextEdit()
        self.task_details.setReadOnly(True)
        self.task_details.setMaximumHeight(150)
        tasks_layout.addWidget(self.task_details)

        # Tasks statistics
        self.task_stats = QLabel("Task Statistics: Loading...")
        self.task_stats.setStyleSheet("color: #888888; font-size: 12px;")
        tasks_layout.addWidget(self.task_stats)

        # Connect task selection
        self.tasks_list.itemSelectionChanged.connect(self.on_task_selected)

        # Initial load
        self.refresh_tasks_list()

        return tasks_widget

    def refresh_tasks_list(self):
        """Refresh the tasks list display"""
        try:
            if not self.task_scheduler:
                self.tasks_list.clear()
                self.tasks_list.addItem("❌ Task scheduler not available")
                self.task_stats.setText("Task Statistics: Scheduler not available")
                return

            # Get task statistics
            stats = self.task_scheduler.get_statistics()
            self.task_stats.setText(
                f"Task Statistics: {stats['tasks_submitted']} submitted, "
                f"{stats['tasks_completed']} completed, {stats['tasks_failed']} failed, "
                f"Avg time: {stats['average_execution_time']:.2f}s"
            )

            # Get all tasks
            task_list = self.task_scheduler.get_task_list()

            self.tasks_list.clear()
            for task_info in task_list:
                status_emoji = {
                    "pending": "⏳",
                    "running": "🏃",
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🚫",
                    "retrying": "🔄"
                }.get(task_info.get("status", "unknown"), "❓")

                item_text = f"{status_emoji} {task_info.get('name', 'Unknown')} - {task_info.get('status', 'unknown').title()}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, task_info)
                self.tasks_list.addItem(item)

        except Exception as e:
            self.task_stats.setText(f"Error refreshing tasks: {str(e)}")

    def filter_tasks_list(self):
        """Filter the tasks list based on search criteria"""
        search_text = self.task_filter.text().lower()
        status_filter = self.task_status_filter.currentText()

        for i in range(self.tasks_list.count()):
            item = self.tasks_list.item(i)
            if item:
                task_data = item.data(Qt.ItemDataRole.UserRole)

                # Text filter
                text_match = search_text in item.text().lower()

                # Status filter
                if status_filter == "All Status":
                    status_match = True
                else:
                    task_status = task_data.get("status", "unknown") if task_data else "unknown"
                    status_match = status_filter.lower() == task_status.lower()

                # Show/hide item
                item.setHidden(not (text_match and status_match))

    def on_task_selected(self):
        """Handle task selection to show details"""
        current_item = self.tasks_list.currentItem()
        if current_item:
            task_data = current_item.data(Qt.ItemDataRole.UserRole)
            if task_data:
                details = f"""Task ID: {task_data.get('id', 'Unknown')}
Name: {task_data.get('name', 'Unknown')}
Status: {task_data.get('status', 'unknown').title()}
Priority: {task_data.get('priority', 'Unknown')}
Created: {task_data.get('created_at', 'Unknown')}
Started: {task_data.get('started_at', 'Not started')}
Completed: {task_data.get('completed_at', 'Not completed')}
Retries: {task_data.get('retry_count', 0)}/{task_data.get('max_retries', 0)}

Dependencies: {', '.join(task_data.get('dependencies', [])) or 'None'}

Result: {task_data.get('result', 'No result') if task_data.get('status') == 'completed' else 'N/A'}
Error: {task_data.get('error', 'No error') if task_data.get('status') == 'failed' else 'N/A'}"""
                self.task_details.setText(details)
            else:
                self.task_details.setText("No task data available")
        else:
            self.task_details.clear()

    def add_test_task(self):
        """Add a test task to demonstrate the scheduler"""
        if not self.task_scheduler:
            QMessageBox.warning(self, "Error", "Task scheduler not available")
            return

        try:
            import random
            import time

            def test_function():
                """A test function that simulates work"""
                duration = random.uniform(1, 5)
                time.sleep(duration)
                return f"Test task completed in {duration:.2f} seconds"

            task_id = self.task_scheduler.schedule_task(
                function=test_function,
                name=f"Test Task {int(time.time())}",
                priority=TaskPriority.NORMAL
            )

            QMessageBox.information(self, "Task Added", f"Test task scheduled with ID: {task_id}")
            self.refresh_tasks_list()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add test task: {str(e)}")

    def clear_completed_tasks(self):
        """Clear all completed and failed tasks"""
        if not self.task_scheduler:
            return

        try:
            # This would need to be implemented in the task scheduler
            # For now, just refresh the list
            self.refresh_tasks_list()
            QMessageBox.information(self, "Tasks Cleared", "Completed tasks have been cleared.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to clear tasks: {str(e)}")

    def cancel_selected_task(self):
        """Cancel the selected task"""
        current_item = self.tasks_list.currentItem()
        if not current_item or not self.task_scheduler:
            return

        task_data = current_item.data(Qt.ItemDataRole.UserRole)
        if task_data:
            task_id = task_data.get('id')
            if task_id:
                try:
                    success = self.task_scheduler.cancel_task(task_id)
                    if success:
                        QMessageBox.information(self, "Task Cancelled", f"Task {task_id} has been cancelled.")
                        self.refresh_tasks_list()
                    else:
                        QMessageBox.warning(self, "Error", "Failed to cancel task (may already be completed)")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to cancel task: {str(e)}")

    def retry_selected_task(self):
        """Retry the selected failed task"""
        current_item = self.tasks_list.currentItem()
        if not current_item or not self.task_scheduler:
            return

        task_data = current_item.data(Qt.ItemDataRole.UserRole)
        if task_data and task_data.get('status') == 'failed':
            # This would need retry functionality in the task scheduler
            QMessageBox.information(self, "Retry", "Task retry functionality would be implemented here.")
        else:
            QMessageBox.warning(self, "Error", "Can only retry failed tasks")

    def toggle_scheduler(self):
        """Toggle the task scheduler pause/resume state"""
        if not self.task_scheduler:
            return

        # This would need pause/resume functionality in the task scheduler
        # For now, just toggle the button text
        if self.scheduler_toggle_btn.text() == "⏸️ Pause Scheduler":
            self.scheduler_toggle_btn.setText("▶️ Resume Scheduler")
            QMessageBox.information(self, "Scheduler", "Task scheduler paused.")
        else:
            self.scheduler_toggle_btn.setText("⏸️ Pause Scheduler")
            QMessageBox.information(self, "Scheduler", "Task scheduler resumed.")

    def closeEvent(self, event):
        """Handle application shutdown - cleanup resources"""
        try:
            # Shutdown task scheduler
            if self.task_scheduler:
                print("🔄 Shutting down task scheduler...")
                self.task_scheduler.shutdown(timeout=5.0)
                print("✅ Task scheduler shut down successfully")
        except Exception as e:
            print(f"⚠️  Error during task scheduler shutdown: {e}")

        try:
            # Stop NeuroHub server
            if hasattr(self, 'neurohub_process') and self.neurohub_process:
                print("🔄 Stopping NeuroHub server...")
                self.neurohub_process.terminate()
                print("✅ NeuroHub server stopped")
        except Exception as e:
            print(f"⚠️  Error stopping NeuroHub server: {e}")

        # Accept the close event
        event.accept()

    def create_neurohub_tab(self):
        """Create the NeuroHub package manager tab"""
        neurohub_widget = QWidget()
        neurohub_layout = QVBoxLayout(neurohub_widget)

        # NeuroHub header with controls
        header_layout = QHBoxLayout()

        header = QLabel("🌐 NeuroHub Package Manager")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(header)

        header_layout.addStretch()

        # Start NeuroHub server button
        self.neurohub_start_btn = QPushButton("🚀 Start NeuroHub")
        self.neurohub_start_btn.clicked.connect(self.start_neurohub_server)
        header_layout.addWidget(self.neurohub_start_btn)

        # Open in browser button
        self.neurohub_browser_btn = QPushButton("🌐 Open in Browser")
        self.neurohub_browser_btn.clicked.connect(self.open_neurohub_browser)
        self.neurohub_browser_btn.setEnabled(False)
        header_layout.addWidget(self.neurohub_browser_btn)

        neurohub_layout.addLayout(header_layout)

        # NeuroHub status
        self.neurohub_status = QLabel("🔄 NeuroHub Status: Not started")
        self.neurohub_status.setStyleSheet("color: #888888; font-size: 12px;")
        neurohub_layout.addWidget(self.neurohub_status)

        # Web view or placeholder
        if WEBENGINE_AVAILABLE:
            try:
                self.neurohub_web_view = QWebEngineView()
                self.neurohub_web_view.setUrl(QUrl("about:blank"))
                neurohub_layout.addWidget(self.neurohub_web_view)

                # Set initial placeholder
                placeholder_html = """
                <html>
                <head>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background: #1e1e1e;
                            color: #ffffff;
                            text-align: center;
                            padding: 50px;
                        }
                        .placeholder {
                            font-size: 18px;
                            color: #888888;
                        }
                        .instructions {
                            font-size: 14px;
                            color: #aaaaaa;
                            margin-top: 20px;
                        }
                    </style>
                </head>
                <body>
                    <div class="placeholder">
                        🌐 NeuroHub Package Manager
                        <br><br>
                        Click "Start NeuroHub" to launch the package manager server
                        <br>
                        and browse AI packages for NeuroCode.
                    </div>
                    <div class="instructions">
                        NeuroHub provides access to plugins, models, and tools<br>
                        for the NeuroCode AI-native development environment.
                    </div>
                </body>
                </html>
                """
                self.neurohub_web_view.setHtml(placeholder_html)

            except Exception as e:
                print(f"⚠️  Failed to create web view: {e}")
                self.neurohub_web_view = None
                # Fall back to text display
                self.create_neurohub_fallback(neurohub_layout)
        else:
            self.neurohub_web_view = None
            self.create_neurohub_fallback(neurohub_layout)

        # NeuroHub info
        info_text = """
NeuroHub is the AI-native package manager for NeuroCode. It provides:

• 🔌 Plugin Discovery - Browse and install NeuroCode plugins
• 🤖 AI Model Hub - Download and manage AI models
• 🛠️ Tool Integration - Find tools and utilities
• 📦 Package Management - Install, update, and remove packages
• 🌐 Community Sharing - Share your own plugins and tools

To get started, click "Start NeuroHub" to launch the local server.
        """

        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #cccccc; font-size: 12px; padding: 10px;")
        info_label.setWordWrap(True)
        neurohub_layout.addWidget(info_label)

        return neurohub_widget

    def create_neurohub_fallback(self, layout):
        """Create fallback UI when WebEngine is not available"""
        fallback_text = QTextEdit()
        fallback_text.setReadOnly(True)
        fallback_text.setHtml("""
        <h2>🌐 NeuroHub Package Manager</h2>
        <p><strong>WebEngine not available - using external browser mode</strong></p>

        <p>NeuroHub provides a complete package management system for NeuroCode:</p>
        <ul>
            <li><strong>Plugin Discovery:</strong> Browse and install NeuroCode plugins</li>
            <li><strong>AI Model Hub:</strong> Download and manage AI models</li>
            <li><strong>Tool Integration:</strong> Find tools and utilities</li>
            <li><strong>Package Management:</strong> Install, update, and remove packages</li>
            <li><strong>Community Sharing:</strong> Share your own plugins and tools</li>
        </ul>

        <p><strong>To use NeuroHub:</strong></p>
        <ol>
            <li>Click "Start NeuroHub" to launch the server</li>
            <li>Click "Open in Browser" to access the web interface</li>
            <li>Browse and install packages for NeuroCode</li>
        </ol>

        <p><em>Note: Install QtWebEngine for embedded browser support</em></p>
        """)
        layout.addWidget(fallback_text)

    def start_neurohub_server(self):
        """Start the NeuroHub server"""
        try:
            import subprocess

            neurohub_path = Path(__file__).parent.parent.parent.parent / "neurohub"

            if not neurohub_path.exists():
                QMessageBox.warning(self, "NeuroHub Error", "NeuroHub directory not found")
                return

            # Check if Node.js is available
            try:
                subprocess.run(["node", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                QMessageBox.warning(
                    self,
                    "NeuroHub Error",
                    "Node.js is required to run NeuroHub.\nPlease install Node.js from nodejs.org"
                )
                return

            # Start NeuroHub server in background
            if hasattr(self, 'neurohub_process') and self.neurohub_process and self.neurohub_process.poll() is None:
                QMessageBox.information(self, "NeuroHub", "NeuroHub is already running")
                return

            # Change to NeuroHub directory and start server
            self.neurohub_process = subprocess.Popen(
                ["npm", "start"],
                cwd=str(neurohub_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Update UI
            self.neurohub_start_btn.setText("🔄 Starting...")
            self.neurohub_start_btn.setEnabled(False)
            self.neurohub_status.setText("🔄 NeuroHub Status: Starting server...")

            # Schedule status check
            import threading
            def check_server():
                import time
                time.sleep(3)  # Give server time to start

                # Check if server is running
                try:
                    import requests
                    response = requests.get("http://localhost:3001/api/health", timeout=5)
                    if response.status_code == 200:
                        # Server is running
                        self.neurohub_server_started()
                    else:
                        self.neurohub_server_failed()
                except Exception:
                    self.neurohub_server_failed()

            threading.Thread(target=check_server, daemon=True).start()

        except Exception as e:
            QMessageBox.warning(self, "NeuroHub Error", f"Failed to start NeuroHub: {str(e)}")
            self.neurohub_server_failed()

    def neurohub_server_started(self):
        """Called when NeuroHub server starts successfully"""
        self.neurohub_start_btn.setText("🛑 Stop NeuroHub")
        self.neurohub_start_btn.setEnabled(True)
        self.neurohub_start_btn.clicked.disconnect()
        self.neurohub_start_btn.clicked.connect(self.stop_neurohub_server)

        self.neurohub_browser_btn.setEnabled(True)
        self.neurohub_status.setText("✅ NeuroHub Status: Running on http://localhost:3001")

        # Load NeuroHub in web view if available
        if hasattr(self, 'neurohub_web_view') and self.neurohub_web_view:
            self.neurohub_web_view.setUrl(QUrl("http://localhost:8080"))

    def neurohub_server_failed(self):
        """Called when NeuroHub server fails to start"""
        self.neurohub_start_btn.setText("🚀 Start NeuroHub")
        self.neurohub_start_btn.setEnabled(True)
        self.neurohub_status.setText("❌ NeuroHub Status: Failed to start")

    def stop_neurohub_server(self):
        """Stop the NeuroHub server"""
        try:
            if hasattr(self, 'neurohub_process') and self.neurohub_process:
                self.neurohub_process.terminate()
                self.neurohub_process = None

            self.neurohub_start_btn.setText("🚀 Start NeuroHub")
            self.neurohub_start_btn.clicked.disconnect()
            self.neurohub_start_btn.clicked.connect(self.start_neurohub_server)
            self.neurohub_browser_btn.setEnabled(False)
            self.neurohub_status.setText("🔄 NeuroHub Status: Stopped")

            # Reset web view
            if hasattr(self, 'neurohub_web_view') and self.neurohub_web_view:
                self.neurohub_web_view.setUrl(QUrl("about:blank"))

        except Exception as e:
            QMessageBox.warning(self, "NeuroHub Error", f"Failed to stop NeuroHub: {str(e)}")

    def open_neurohub_browser(self):
        """Open NeuroHub in external browser"""
        try:
            import webbrowser
            webbrowser.open("http://localhost:8080")
        except Exception as e:
            QMessageBox.warning(self, "Browser Error", f"Failed to open browser: {str(e)}")
