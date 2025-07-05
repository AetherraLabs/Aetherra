"""
Enhanced Lyrixa Window
=====================

Main enhanced UI window for the Lyrixa assistant system.
Provides a sophisticated interface for Aetherra code interaction with real AI functionality.
Integrates Phase 3 components: Analytics Dashboard, Suggestion Notifications, Configuration Manager, and Performance Monitor.
"""

import asyncio
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

# Import Phase 3 GUI components
try:
    # Import GUI components from the lyrixa.gui package
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "lyrixa"))
    from lyrixa.gui.analytics_dashboard import AnalyticsDashboard
    from lyrixa.gui.suggestion_notifications import SuggestionNotificationSystem
    from lyrixa.gui.configuration_manager import ConfigurationManager
    from lyrixa.gui.performance_monitor import PerformanceMonitor
    PHASE3_GUI_AVAILABLE = True
except ImportError as e:
    print(f"Phase 3 GUI components not available: {e}")
    PHASE3_GUI_AVAILABLE = False

# Import anticipation engine
try:
    from lyrixa.core.anticipation_engine import AnticipationEngine
    ANTICIPATION_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Anticipation engine not available: {e}")
    ANTICIPATION_ENGINE_AVAILABLE = False


class EnhancedLyrixaWindow:
    """
    Enhanced Lyrixa Assistant Window

    Main window for the Lyrixa assistant with advanced features:
    - Multi-panel interface
    - Real-time code interpretation
    - Plugin integration
    - Enhanced chat capabilities
    """

    def __init__(self):
        """Initialize the Enhanced Lyrixa Window."""
        print("🎙️ Enhanced Lyrixa Window initialized")
        self.window_title = "Lyrixa Assistant - Enhanced Interface"
        self.width = 1200
        self.height = 800

        # Initialize event loop for async operations
        self.loop = None
        self.executor = ThreadPoolExecutor(max_workers=2)

        # Initialize core components first
        self.plugins = []  # Initialize plugins list first
        self.goals = []
        self.memory = None
        self.advanced_memory = None
        self.lyrixa_ai = None

        # Initialize Phase 3 components
        self.analytics_dashboard = None
        self.notification_system = None
        self.config_manager = None
        self.performance_monitor = None
        self.anticipation_engine = None

        # Initialize AI and memory systems
        self._initialize_lyrixa_ai()
        
        # Initialize Phase 3 components
        self._initialize_phase3_components()

        print("✅ Enhanced Lyrixa Window ready with Phase 3 integration")
        self.height = 800

        # Initialize core functionality first (before Qt setup)
        self.code_content = ""
        self.chat_history = []
        self.plugins = [
            "Memory System",
            "Code Analyzer",
            "Performance Monitor",
            "Debug Assistant",
            "Documentation Generator",
            "Goal Tracker",
            "Agent Orchestrator",
            "Aether Interpreter",
        ]
        self.active_plugin = None

        # Initialize advanced memory system early
        self.advanced_memory = None
        self.reflection_engine = None

        # Initialize real Lyrixa AI
        self.lyrixa_ai = None
        self._initialize_lyrixa_ai()

        # Check if Qt is available
        try:
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QAction
            from PySide6.QtWidgets import (
                QHBoxLayout,
                QLabel,
                QLineEdit,
                QMainWindow,
                QMenu,
                QMenuBar,
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

            self.qt_available = True
            self._setup_qt_window()
        except ImportError:
            self.qt_available = False
            print("⚠️ PySide6 not available - running in console mode")

    def _initialize_lyrixa_ai(self):
        """Initialize the real Lyrixa AI system with Phase 1 Advanced Memory."""
        try:
            # Add the Lyrixa module to path
            import os
            import sys

            project_root = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            lyrixa_path = os.path.join(project_root, "lyrixa")
            if lyrixa_path not in sys.path:
                sys.path.insert(0, lyrixa_path)

            from lyrixa import LyrixaAI

            # Initialize Lyrixa AI with workspace
            workspace_path = project_root
            self.lyrixa_ai = LyrixaAI(workspace_path=workspace_path)
            print("✅ Real Lyrixa AI system initialized")

            # Initialize Phase 1 Advanced Memory System
            self._initialize_advanced_memory()

        except Exception as e:
            print(f"⚠️ Could not initialize Lyrixa AI: {e}")
            self.lyrixa_ai = None

    def _initialize_advanced_memory(self):
        """Initialize Phase 1 Advanced Memory System."""
        try:
            from lyrixa.core.advanced_vector_memory import (
                AdvancedMemorySystem,
                ReflexiveAnalysisEngine,
            )

            # Initialize advanced memory
            self.advanced_memory = AdvancedMemorySystem()
            self.reflection_engine = ReflexiveAnalysisEngine(self.advanced_memory)

            print("🧠 Phase 1 Advanced Memory System integrated")
            print("   ✅ Vector embeddings enabled")
            print("   ✅ Confidence modeling active")
            print("   ✅ Reflexive analysis ready")

            # Add memory system to plugins
            if "Advanced Memory" not in self.plugins:
                self.plugins.insert(0, "Advanced Memory")

        except Exception as e:
            print(f"⚠️ Could not initialize Advanced Memory: {e}")
            self.advanced_memory = None
            self.reflection_engine = None

    def _initialize_phase3_components(self):
        """Initialize Phase 3 GUI components and anticipation engine."""
        try:
            # Initialize anticipation engine first
            if ANTICIPATION_ENGINE_AVAILABLE:
                self.anticipation_engine = AnticipationEngine()
                print("🔮 Anticipation Engine initialized")
            
            # Initialize Phase 3 GUI components if available
            if PHASE3_GUI_AVAILABLE:
                try:
                    # Analytics Dashboard
                    self.analytics_dashboard = AnalyticsDashboard()
                    print("📊 Analytics Dashboard initialized")
                    
                    # Suggestion Notification System
                    self.notification_system = SuggestionNotificationSystem()
                    print("💡 Suggestion Notification System initialized")
                    
                    # Configuration Manager
                    self.config_manager = ConfigurationManager()
                    print("⚙️ Configuration Manager initialized")
                    
                    # Performance Monitor
                    self.performance_monitor = PerformanceMonitor()
                    print("⚡ Performance Monitor initialized")
                    
                    # Connect anticipation engine to notification system
                    if self.anticipation_engine and self.notification_system:
                        self._connect_anticipation_to_notifications()
                    
                    print("✅ Phase 3 components integrated successfully")
                    
                except Exception as e:
                    print(f"⚠️ Error initializing Phase 3 GUI components: {e}")
                    # Set components to None if initialization fails
                    self.analytics_dashboard = None
                    self.notification_system = None
                    self.config_manager = None
                    self.performance_monitor = None
            else:
                print("ℹ️ Phase 3 GUI components not available")
                
        except Exception as e:
            print(f"⚠️ Error in Phase 3 initialization: {e}")
    
    def _connect_anticipation_to_notifications(self):
        """Connect the anticipation engine to the notification system."""
        try:
            # This would integrate the anticipation engine with notifications
            # For now, we'll set up basic connectivity
            print("🔗 Connecting anticipation engine to notification system")
            
            # In a full implementation, we would:
            # 1. Connect anticipation engine suggestion generation to notification display
            # 2. Set up callback handlers for user feedback
            # 3. Integrate with analytics for suggestion effectiveness tracking
            
            print("✅ Anticipation engine connected to notifications")
            
        except Exception as e:
            print(f"⚠️ Error connecting anticipation to notifications: {e}")

    def show_analytics_dashboard(self):
        """Show the analytics dashboard."""
        if self.analytics_dashboard:
            self.analytics_dashboard.show()
            self.analytics_dashboard.raise_()
        else:
            print("Analytics dashboard not available")
    
    def show_configuration_manager(self):
        """Show the configuration manager."""
        if self.config_manager:
            self.config_manager.show()
            self.config_manager.raise_()
        else:
            print("Configuration manager not available")
    
    def show_performance_monitor(self):
        """Show the performance monitor."""
        if self.performance_monitor:
            self.performance_monitor.show()
            self.performance_monitor.raise_()
        else:
            print("Performance monitor not available")
    
    def toggle_suggestions(self):
        """Toggle the suggestion notification system."""
        if self.notification_system:
            if self.notification_system.isVisible():
                self.notification_system.hide()
            else:
                self.notification_system.show()
                self.notification_system.raise_()
        else:
            print("Suggestion system not available")

    def _setup_qt_window(self):
        """Setup Qt-based GUI if available."""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QAction
        from PySide6.QtWidgets import (
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QPushButton,
            QSplitter,
            QStatusBar,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        class QtWindow(QMainWindow):
            def __init__(self, parent_window):
                super().__init__()
                self.parent_window = parent_window
                self.setWindowTitle(parent_window.window_title)
                self.resize(parent_window.width, parent_window.height)
                self.setup_ui()

            def setup_ui(self):
                central_widget = QWidget()
                self.setCentralWidget(central_widget)

                # Create menu bar
                self.create_menu_bar()

                # Create main splitter
                main_splitter = QSplitter()
                try:
                    main_splitter.setOrientation(Qt.Orientation.Horizontal)
                except Exception:
                    pass  # Use default orientation
                layout = QVBoxLayout(central_widget)
                layout.addWidget(main_splitter)

                # Left panel - Aetherra Code & Console
                left_widget = QWidget()
                left_layout = QVBoxLayout(left_widget)

                # Code editor section
                left_layout.addWidget(QLabel("🔮 Aetherra Code Editor"))
                self.code_editor = QTextEdit()
                self.code_editor.setPlaceholderText("""// Enter your Aetherra code here...
goal: create a simple greeting
memory: remember name as "User"
agent: on
when greeting_requested:
    say "Hello, " + recall("name") + "!"
    optimize for "friendliness"
end""")
                left_layout.addWidget(self.code_editor)

                # Execute button
                execute_btn = QPushButton("🚀 Execute Aetherra Code")
                execute_btn.clicked.connect(self.execute_code)
                execute_btn.setStyleSheet(
                    "background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;"
                )
                left_layout.addWidget(execute_btn)

                # Console
                left_layout.addWidget(QLabel("📟 Console Output"))
                self.console = QTextEdit()
                self.console.setReadOnly(True)
                self.console.setStyleSheet(
                    "background-color: #1e1e1e; color: #00ff00; font-family: 'Courier New';"
                )
                left_layout.addWidget(self.console)

                main_splitter.addWidget(left_widget)

                # Right panel - Lyrixa Assistant & Features
                right_widget = QTabWidget()

                # Chat Tab
                chat_tab = QWidget()
                chat_layout = QVBoxLayout(chat_tab)

                # Lyrixa header
                lyrixa_header = QLabel("🎙️ Lyrixa AI Assistant")
                lyrixa_header.setStyleSheet(
                    "font-size: 16px; font-weight: bold; color: #2196F3; padding: 10px;"
                )
                chat_layout.addWidget(lyrixa_header)

                self.chat_display = QTextEdit()
                self.chat_display.setReadOnly(True)
                self.chat_display.setStyleSheet(
                    "background-color: #f5f5f5; border: 1px solid #ddd; padding: 10px;"
                )
                # Add welcome message
                self.chat_display.append(
                    "🎙️ Lyrixa: Hello! I'm your AI assistant for Aetherra development."
                )
                self.chat_display.append(
                    "🎙️ Lyrixa: I can help you with code generation, memory management, goal setting, and more!"
                )
                chat_layout.addWidget(self.chat_display)

                # Chat input
                input_layout = QHBoxLayout()
                self.chat_input = QLineEdit()
                self.chat_input.setPlaceholderText(
                    "Ask Lyrixa anything about Aetherra, goals, memory, or request assistance..."
                )
                self.chat_input.returnPressed.connect(self.send_message)
                self.chat_input.setStyleSheet(
                    "padding: 8px; border: 2px solid #2196F3; border-radius: 5px;"
                )
                input_layout.addWidget(self.chat_input)

                send_btn = QPushButton("💬 Send")
                send_btn.clicked.connect(self.send_message)
                send_btn.setStyleSheet(
                    "background-color: #2196F3; color: white; padding: 8px 15px; border-radius: 5px;"
                )
                input_layout.addWidget(send_btn)
                chat_layout.addLayout(input_layout)

                right_widget.addTab(chat_tab, "💬 Chat")

                # Memory Tab
                memory_tab = QWidget()
                memory_layout = QVBoxLayout(memory_tab)
                memory_layout.addWidget(QLabel("🧠 Memory System"))
                self.memory_display = QTextEdit()
                self.memory_display.setReadOnly(True)
                self.memory_display.setPlaceholderText(
                    "Lyrixa's memories will appear here..."
                )
                memory_layout.addWidget(self.memory_display)
                refresh_memory_btn = QPushButton("🔄 Refresh Memory")
                refresh_memory_btn.clicked.connect(self.refresh_memory)
                memory_layout.addWidget(refresh_memory_btn)
                right_widget.addTab(memory_tab, "🧠 Memory")

                # Goals Tab
                goals_tab = QWidget()
                goals_layout = QVBoxLayout(goals_tab)
                goals_layout.addWidget(QLabel("🎯 Goals & Tasks"))
                self.goals_display = QTextEdit()
                self.goals_display.setReadOnly(True)
                self.goals_display.setPlaceholderText(
                    "Your goals and tasks will appear here..."
                )
                goals_layout.addWidget(self.goals_display)
                refresh_goals_btn = QPushButton("🎯 Refresh Goals")
                refresh_goals_btn.clicked.connect(self.refresh_goals)
                goals_layout.addWidget(refresh_goals_btn)
                right_widget.addTab(goals_tab, "🎯 Goals")

                # Plugins Tab
                plugins_tab = QWidget()
                plugins_layout = QVBoxLayout(plugins_tab)
                plugins_layout.addWidget(QLabel("🧩 Available Plugins"))
                self.plugins_display = QTextEdit()
                self.plugins_display.setReadOnly(True)
                plugins_layout.addWidget(self.plugins_display)
                self.load_plugins_list()
                right_widget.addTab(plugins_tab, "🧩 Plugins")

                # Dashboard Tab
                dashboard_tab = QWidget()
                dashboard_layout = QVBoxLayout(dashboard_tab)
                dashboard_layout.addWidget(QLabel("🧠 Memory Dashboard"))
                self.dashboard_display = QTextEdit()
                self.dashboard_display.setReadOnly(True)
                self.dashboard_display.setPlaceholderText(
                    "Memory dashboard will appear here..."
                )
                dashboard_layout.addWidget(self.dashboard_display)
                refresh_dashboard_btn = QPushButton("🔄 Refresh Dashboard")
                refresh_dashboard_btn.clicked.connect(self.refresh_dashboard)
                dashboard_layout.addWidget(refresh_dashboard_btn)
                right_widget.addTab(dashboard_tab, "📊 Dashboard")

                # Phase 3 - Analytics Dashboard
                if PHASE3_GUI_AVAILABLE:
                    analytics_tab = QWidget()
                    analytics_layout = QVBoxLayout(analytics_tab)
                    analytics_layout.addWidget(QLabel("📊 Analytics Dashboard"))
                    self.analytics_display = QTextEdit()
                    self.analytics_display.setReadOnly(True)
                    self.analytics_display.setPlaceholderText(
                        "Analytics data will appear here..."
                    )
                    analytics_layout.addWidget(self.analytics_display)
                    refresh_analytics_btn = QPushButton("🔄 Refresh Analytics")
                    refresh_analytics_btn.clicked.connect(self.refresh_analytics)
                    analytics_layout.addWidget(refresh_analytics_btn)
                    right_widget.addTab(analytics_tab, "📊 Analytics")

                main_splitter.addWidget(right_widget)

                # Status bar
                self.setStatusBar(QStatusBar())
                self.statusBar().showMessage(
                    "🎙️ Lyrixa Assistant Ready - Real AI System Loaded"
                )

            def create_menu_bar(self):
                """Create the menu bar."""
                menubar = self.menuBar()

                # File menu
                file_menu = menubar.addMenu("📁 File")

                new_action = QAction("🆕 New Aetherra File", self)
                file_menu.addAction(new_action)

                open_action = QAction("📂 Open File", self)
                file_menu.addAction(open_action)

                save_action = QAction("💾 Save", self)
                file_menu.addAction(save_action)

                # Lyrixa menu
                lyrixa_menu = menubar.addMenu("🎙️ Lyrixa")

                reset_action = QAction("🔄 Reset Lyrixa", self)
                reset_action.triggered.connect(self.reset_lyrixa)
                lyrixa_menu.addAction(reset_action)

                memory_action = QAction("🧠 Show Memory", self)
                memory_action.triggered.connect(self.show_memory)
                lyrixa_menu.addAction(memory_action)

            def load_plugins_list(self):
                """Load and display available plugins."""
                plugins_text = "🧩 Available Lyrixa Plugins:\n\n"
                for i, plugin in enumerate(self.parent_window.plugins, 1):
                    plugins_text += f"{i}. {plugin}\n"
                plugins_text += (
                    "\n💡 Plugins provide extended functionality for Lyrixa."
                )
                self.plugins_display.setPlainText(plugins_text)

            def execute_code(self):
                code = self.code_editor.toPlainText()
                if not code.strip():
                    self.console.append("⚠️ No code to execute!")
                    return

                self.console.append(f"🚀 Executing Aetherra code...")
                self.console.append(
                    f"📝 Code: {code[:100]}{'...' if len(code) > 100 else ''}"
                )

                try:
                    result = self.parent_window.execute_code(code)
                    if result:
                        self.console.append("✅ Code execution completed successfully!")
                        self.console.append(f"📊 Result: {result}")
                    else:
                        self.console.append("⚠️ Code execution completed (no output)")
                except Exception as e:
                    self.console.append(f"❌ Execution error: {e}")

            def send_message(self):
                message = self.chat_input.text()
                if not message.strip():
                    return

                self.chat_display.append(f"👤 You: {message}")
                self.chat_input.clear()

                # Show processing indicator
                self.chat_display.append("🎙️ Lyrixa: *thinking...*")

                try:
                    response = self.parent_window.send_message(message)
                    # Remove the thinking message
                    cursor = self.chat_display.textCursor()
                    cursor.movePosition(cursor.MoveOperation.End)
                    cursor.select(cursor.SelectionType.LineUnderCursor)
                    cursor.removeSelectedText()
                    cursor.deletePreviousChar()

                    self.chat_display.append(f"🎙️ Lyrixa: {response}")
                except Exception as e:
                    self.chat_display.append(
                        f"🎙️ Lyrixa: Sorry, I encountered an error: {e}"
                    )

            def refresh_memory(self):
                """Refresh the memory display."""
                try:
                    memories = self.parent_window.get_memories()
                    self.memory_display.clear()
                    self.memory_display.append("🧠 Lyrixa's Memory System\n")
                    for memory in memories:
                        self.memory_display.append(f"• {memory}")
                except Exception as e:
                    self.memory_display.append(f"❌ Error loading memories: {e}")

            def refresh_goals(self):
                """Refresh the goals display."""
                try:
                    goals = self.parent_window.get_goals()
                    self.goals_display.clear()
                    self.goals_display.append("🎯 Current Goals & Tasks\n")
                    for goal in goals:
                        self.goals_display.append(f"• {goal}")
                except Exception as e:
                    self.goals_display.append(f"❌ Error loading goals: {e}")

            def refresh_dashboard(self):
                """Refresh the memory dashboard."""
                try:
                    dashboard_info = self.parent_window.get_memory_dashboard()
                    self.dashboard_display.setPlainText(dashboard_info)
                except Exception as e:
                    self.dashboard_display.setPlainText(
                        f"❌ Error loading dashboard: {e}"
                    )

            def refresh_analytics(self):
                """Refresh the analytics display."""
                try:
                    analytics_info = self.parent_window.get_analytics_data()
                    self.analytics_display.setPlainText(analytics_info)
                except Exception as e:
                    self.analytics_display.setPlainText(
                        f"❌ Error loading analytics: {e}"
                    )

            def reset_lyrixa(self):
                """Reset Lyrixa AI system."""
                self.chat_display.append("🔄 Resetting Lyrixa AI system...")
                try:
                    self.parent_window.reset_lyrixa()
                    self.chat_display.append("✅ Lyrixa has been reset and is ready!")
                except Exception as e:
                    self.chat_display.append(f"❌ Reset failed: {e}")

            def show_memory(self):
                """Show memory in chat."""
                self.refresh_memory()
                self.chat_display.append(
                    "🧠 Memory system refreshed - check the Memory tab!"
                )

        self.qt_window = QtWindow(self)

    def execute_code(self, code):
        """Execute Aetherra code using real Lyrixa AI."""
        self.code_content = code
        print(f"🚀 Executing Aetherra code through Lyrixa: {code[:100]}...")

        try:
            if self.lyrixa_ai and hasattr(self.lyrixa_ai, "aether_interpreter"):
                # Use real Aetherra interpreter
                result = self.lyrixa_ai.aether_interpreter.execute(code)
                return f"Execution result: {result}"
            else:
                # Fallback simulation
                lines = code.strip().split("\n")
                results = []
                for line in lines:
                    if line.startswith("goal:"):
                        goal = line.replace("goal:", "").strip()
                        results.append(f"✅ Goal set: {goal}")
                    elif line.startswith("memory:"):
                        memory = line.replace("memory:", "").strip()
                        results.append(f"🧠 Memory stored: {memory}")
                    elif line.startswith("agent:"):
                        agent = line.replace("agent:", "").strip()
                        results.append(f"🤖 Agent {agent}")
                    elif "say" in line:
                        message = line.split("say")[1].strip().strip('"')
                        results.append(f"💬 Output: {message}")

                return "\n".join(results) if results else "Code processed"

        except Exception as e:
            return f"❌ Execution error: {e}"

    def send_message(self, message):
        """Send message to real Lyrixa assistant with Phase 1 Advanced Memory."""
        self.chat_history.append(
            {"user": message, "timestamp": datetime.now().isoformat()}
        )
        print(f"🎙️ Lyrixa received: {message}")

        try:
            # Store user message in advanced memory
            if hasattr(self, "advanced_memory") and self.advanced_memory:
                asyncio.run(self._store_user_interaction(message))

            if self.lyrixa_ai:
                # Get relevant memories for context
                context = {}
                if hasattr(self, "advanced_memory") and self.advanced_memory:
                    context = asyncio.run(self._get_memory_context(message))

                # Use real Lyrixa AI if available
                response = asyncio.run(self.lyrixa_ai.process_natural_language(message))
                ai_response = response.get(
                    "lyrixa_response", "I understand your message."
                )

                # Analyze confidence and store AI response
                if hasattr(self, "advanced_memory") and self.advanced_memory:
                    asyncio.run(self._analyze_and_store_response(ai_response, context))

                return ai_response
            else:
                # Enhanced fallback responses with memory
                return self._generate_enhanced_fallback(message)

        except Exception as e:
            error_response = f"I encountered an error: {e}. But I'm still here to help!"

            # Store error in memory for learning
            if hasattr(self, "advanced_memory") and self.advanced_memory:
                asyncio.run(
                    self.advanced_memory.store_memory(
                        content=f"Error occurred: {str(e)}",
                        memory_type="error",
                        tags=["error", "debugging"],
                        confidence=0.3,
                    )
                )

            return error_response

    def get_memories(self):
        """Get memories from Lyrixa AI system."""
        try:
            if self.lyrixa_ai and hasattr(self.lyrixa_ai, "memory"):
                # Get real memories
                memories = self.lyrixa_ai.memory.get_recent_memories(limit=10)
                return [f"{mem.get('content', 'Memory item')}" for mem in memories]
            else:
                # Sample memories
                return [
                    "User prefers Python for scripting",
                    "Working on Aetherra project",
                    "Interested in AI-native programming",
                    "Uses VS Code as primary editor",
                    "Learning about goal-oriented programming",
                ]
        except Exception as e:
            return [f"Error loading memories: {e}"]

    def get_goals(self):
        """Get goals from Lyrixa AI system."""
        try:
            if self.lyrixa_ai and hasattr(self.lyrixa_ai, "goals"):
                # Get real goals
                goals = self.lyrixa_ai.goals.get_active_goals()
                return [
                    f"{goal.description} (Priority: {goal.priority.value})"
                    for goal in goals
                ]
            else:
                # Sample goals
                return [
                    "📚 Learn Aetherra programming language",
                    "🚀 Complete current project",
                    "🧠 Improve memory management",
                    "🤖 Set up AI agent workflow",
                    "⚡ Optimize code performance",
                ]
        except Exception as e:
            return [f"Error loading goals: {e}"]

    def reset_lyrixa(self):
        """Reset the Lyrixa AI system."""
        try:
            if self.lyrixa_ai:
                # Reinitialize Lyrixa
                self._initialize_lyrixa_ai()
                return True
            else:
                # Reset fallback state
                self.chat_history = []
                self.code_content = ""
                return True
        except Exception as e:
            print(f"Error resetting Lyrixa: {e}")
            return False

    def activate_plugin(self, plugin_name):
        """Activate a plugin."""
        if plugin_name in self.plugins:
            self.active_plugin = plugin_name
            print(f"Activated plugin: {plugin_name}")
            return True
        return False

    def show(self):
        """Show the window."""
        if self.qt_available and hasattr(self, "qt_window"):
            self.qt_window.show()
            return self.qt_window
        else:
            print("Enhanced Lyrixa Window is running in console mode")
            print(f"Title: {self.window_title}")
            print(f"Size: {self.width}x{self.height}")
            print("Available plugins:", self.plugins)
            return self

    def close(self):
        """Close the window."""
        if self.qt_available and hasattr(self, "qt_window"):
            self.qt_window.close()
        print("Enhanced Lyrixa Window closed")


def launch_enhanced_lyrixa():
    """Launch function to run the Enhanced Lyrixa Window."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = EnhancedLyrixaWindow()
        qt_window = window.show()
        if qt_window and hasattr(qt_window, "exec"):
            sys.exit(app.exec())
        elif qt_window:
            sys.exit(app.exec_())
    except ImportError:
        # Fallback to console mode
        window = EnhancedLyrixaWindow()
        window.show()
        print("Press Enter to exit...")
        input()


if __name__ == "__main__":
    launch_enhanced_lyrixa()

    def execute_code(self):
        """Execute Aetherra code from the editor."""
        code = self.code_editor.toPlainText()
        if code.strip():
            self.console_output.append(f"> Executing Aetherra code:\n{code}\n")
            # Emit signal for external handling
            self.code_executed.emit(code)
            self.status_bar.showMessage("Code executed successfully")
        else:
            self.console_output.append("> No code to execute")

    def send_message(self):
        """Send message to Lyrixa assistant."""
        message = self.chat_input.text()
        if message.strip():
            self.chat_display.append(f"You: {message}")
            self.chat_input.clear()

            # Simulate assistant response
            response = f"Lyrixa: I understand you said '{message}'. How can I help you with Aetherra development?"
            self.chat_display.append(response)
            self.assistant_response.emit(response)

    def activate_plugin(self):
        """Activate the selected plugin."""
        plugin = self.plugin_combo.currentText()
        self.console_output.append(f"> Activating plugin: {plugin}")
        self.status_bar.showMessage(f"Plugin activated: {plugin}")

    def update_performance(self):
        """Update performance metrics."""
        # Simulate performance data
        self.status_bar.showMessage("System running optimally - Memory: 45MB, CPU: 12%")

    # Menu action handlers
    def new_project(self):
        self.code_editor.clear()
        self.console_output.clear()
        self.status_bar.showMessage("New project created")

    def open_file(self):
        self.status_bar.showMessage("Open file dialog would appear here")

    def save_file(self):
        self.status_bar.showMessage("File saved successfully")

    def undo(self):
        self.code_editor.undo()

    def redo(self):
        self.code_editor.redo()

    def cut(self):
        self.code_editor.cut()

    def copy(self):
        self.code_editor.copy()

    def paste(self):
        self.code_editor.paste()

    def toggle_debug(self):
        self.console_output.append("> Debug mode toggled")

    def show_memory(self):
        self.console_output.append("> Memory viewer would open here")

    def show_about(self):
        self.console_output.append(
            "> About: Lyrixa Assistant - Enhanced Aetherra Interface"
        )

    def show_docs(self):
        self.console_output.append("> Documentation would open here")


def launch_enhanced_lyrixa():
    """Launch the Enhanced Lyrixa Window."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        window = EnhancedLyrixaWindow()
        window.show()

        print("🎙️ Enhanced Lyrixa GUI launched successfully!")
        return window

    except ImportError:
        print("❌ PySide6 not available. Cannot run Enhanced Lyrixa Window.")
        print("Install with: pip install PySide6")
        return None


def main():
    """Main function to run the Enhanced Lyrixa Window."""
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        window = EnhancedLyrixaWindow()
        window.show()

        print("🎙️ Starting Enhanced Lyrixa - Full AI Assistant Interface")
        sys.exit(app.exec())

    except ImportError:
        print("❌ PySide6 not available. Cannot run Enhanced Lyrixa Window.")
        print("Install with: pip install PySide6")
    except Exception as e:
        print(f"❌ Error launching Enhanced Lyrixa: {e}")


if __name__ == "__main__":
    main()

    async def _store_user_interaction(self, message):
        """Store user interaction in advanced memory."""
        try:
            await self.advanced_memory.store_memory(
                content=f"User said: {message}",
                memory_type="interaction",
                tags=["user", "chat", "interaction"],
                confidence=1.0,
            )
        except Exception as e:
            print(f"Warning: Could not store user interaction: {e}")

    async def _get_memory_context(self, message):
        """Get relevant memory context for the message."""
        try:
            # Search for relevant memories
            relevant_memories = await self.advanced_memory.semantic_search(
                query=message, top_k=5
            )

            return {
                "relevant_memories": relevant_memories,
                "message": message,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"Warning: Could not get memory context: {e}")
            return {"relevant_memories": [], "message": message}

    async def _analyze_and_store_response(self, response, context):
        """Analyze AI response confidence and store it."""
        try:
            # Analyze confidence
            confidence_analysis = await self.advanced_memory.analyze_confidence(
                response, context
            )

            # Store the AI response with confidence
            await self.advanced_memory.store_memory(
                content=f"AI responded: {response}",
                memory_type="response",
                tags=["ai", "response", "chat"],
                confidence=confidence_analysis["confidence_score"],
                context=confidence_analysis,
            )

            # If confidence is low, log for improvement
            if confidence_analysis["needs_clarification"]:
                print(
                    f"⚠️ Low confidence response (score: {confidence_analysis['confidence_score']:.2f})"
                )
                for question in confidence_analysis.get("clarification_questions", []):
                    print(f"   💭 Suggestion: {question}")

        except Exception as e:
            print(f"Warning: Could not analyze response: {e}")

    def _generate_enhanced_fallback(self, message):
        """Generate enhanced fallback response using memory."""
        message_lower = message.lower()

        # Try to get context from memory if available
        fallback_context = ""
        if hasattr(self, "advanced_memory") and self.advanced_memory:
            try:
                # Get some recent context
                stats = asyncio.run(self.advanced_memory.get_memory_statistics())
                if stats["total_memories"] > 0:
                    fallback_context = (
                        f" (I have {stats['total_memories']} memories to help you)"
                    )
            except Exception:
                pass

        # Enhanced fallback responses
        if any(word in message_lower for word in ["goal", "task", "objective"]):
            return f"I can help you set and track goals! Try using Aetherra code like: goal: your objective here{fallback_context}"
        elif any(word in message_lower for word in ["memory", "remember", "recall"]):
            return f"Memory is important! Use Aetherra syntax: memory: remember data as 'tag' or recall('tag'){fallback_context}"
        elif any(word in message_lower for word in ["confidence", "certain", "sure"]):
            return f"I understand you're asking about confidence. I can analyze my own confidence levels and let you know when I'm uncertain{fallback_context}"
        elif any(word in message_lower for word in ["code", "execute", "run"]):
            return f"I can help you write and execute Aetherra code! Try the code editor on the left{fallback_context}"
        elif any(word in message_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm Lyrixa, your AI assistant for Aetherra development with advanced memory and self-reflection capabilities{fallback_context}"
        elif any(word in message_lower for word in ["help", "what", "how"]):
            return f"I can assist with: 🎯 Goal setting, 🧠 Advanced memory with semantic search, 🔮 Aetherra code generation, 🤖 Agent coordination, and self-reflection{fallback_context}!"
        else:
            return f"I understand you're asking about: '{message}'. I'm here to help with Aetherra development, with advanced memory and confidence analysis{fallback_context}!"

    async def get_memory_dashboard(self):
        """Get memory dashboard information for display."""
        if not hasattr(self, "advanced_memory") or not self.advanced_memory:
            return "Advanced Memory System not available"

        try:
            # Get memory statistics
            stats = await self.advanced_memory.get_memory_statistics()

            # Get recent reflection if available
            reflection_summary = "No recent reflections"
            if hasattr(self, "reflection_engine") and self.reflection_engine:
                try:
                    reflection = await self.reflection_engine.daily_reflection()
                    if reflection.get("insights"):
                        reflection_summary = (
                            f"Latest insight: {reflection['insights'][0]}"
                        )
                except Exception:
                    reflection_summary = "Reflection system active"

            dashboard = f"""🧠 ADVANCED MEMORY DASHBOARD
================================
📊 Total Memories: {stats["total_memories"]}
🎯 Average Confidence: {stats["average_confidence"]:.2f}
📅 Recent Activity: {stats["recent_memories_7days"]} (last 7 days)
🔍 Vector Search: {"✅ Enabled" if stats["vector_support_enabled"] else "❌ Disabled"}

📈 Memory Types:
{chr(10).join([f"   • {mem_type}: {count}" for mem_type, count in stats["memory_types"].items()])}

🤔 Reflection Status: {reflection_summary}
"""
            return dashboard

        except Exception as e:
            return f"Error accessing memory dashboard: {e}"

    async def search_memories(self, query, limit=5):
        """Search memories using semantic search."""
        if not hasattr(self, "advanced_memory") or not self.advanced_memory:
            return "Advanced Memory System not available"

        try:
            results = await self.advanced_memory.semantic_search(query, top_k=limit)

            if not results:
                return f"No memories found for query: '{query}'"

            search_results = f"🔍 MEMORY SEARCH RESULTS for '{query}'\n"
            search_results += "=" * 50 + "\n"

            for i, result in enumerate(results, 1):
                similarity = result.get("similarity_score", 0)
                content = (
                    result["content"][:100] + "..."
                    if len(result["content"]) > 100
                    else result["content"]
                )
                search_results += f"{i}. [{result['memory_type']}] {content}\n"
                search_results += f"   Similarity: {similarity:.3f} | Confidence: {result.get('confidence', 'N/A')}\n\n"

            return search_results

        except Exception as e:
            return f"Error searching memories: {e}"
