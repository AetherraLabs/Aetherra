import sys
import asyncio
from PySide6.QtWidgets import QApplication

from lyrixa.gui.gui_window import LyrixaWindow
from lyrixa.intelligence import LyrixaIntelligenceStack
from lyrixa.agents.core_agent import LyrixaAI
from core.aether_runtime import AetherRuntime
from core.plugin_manager import PluginManager
from core.prompt_engine import PromptEngine
from core.memory_manager import MemoryManager
from core.multi_llm_manager import MultiLLMManager
from utils.launch_utils import run_self_improvement_api
from utils.logging_utils import log

# Global references
lyrixa = None
runtime = None
intelligence_stack = None

# Try to import GUI dependencies
GUI_AVAILABLE = False
if TYPE_CHECKING:
    # Import for type checking only
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QProgressBar,
        QPushButton,
        QSplitter,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
    from PySide6.QtWidgets import (
        QApplication,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QMainWindow,
        QProgressBar,
        QPushButton,
        QSplitter,
        QStatusBar,
        QTableWidget,
        QTableWidgetItem,
        QTabWidget,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )

    GUI_AVAILABLE = True
    print("✅ GUI dependencies loaded successfully")
except ImportError as e:
    print(f"[WARN] GUI dependencies not available: {e}")
    print("To use GUI mode, install PySide6: pip install PySide6")
    GUI_AVAILABLE = False

try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
    from lyrixa import LyrixaAI
    from lyrixa.intelligence_integration import LyrixaIntelligenceStack
except ImportError as e:
    print(f"[ERROR] Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


class BackendProcessManager:
    """Manages the FastAPI backend server as a subprocess."""

    def __init__(self, script_path, host="127.0.0.1", port=8005):
        self.script_path = script_path
        self.host = host
        self.port = port
        self.process = None

    def is_running(self):
        try:
            resp = requests.get(f"http://{self.host}:{self.port}/docs", timeout=1)
            return resp.status_code == 200
        except Exception:
            return False

    def start(self):
        if self.is_running():
            print(f"[Lyrixa] Backend already running at http://{self.host}:{self.port}")
            return
        print(f"[Lyrixa] Starting backend: {self.script_path}")
        self.process = subprocess.Popen(
            [sys.executable, self.script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
            text=True,
        )
        # Wait for server to be ready
        for _ in range(30):
            if self.is_running():
                print(f"[Lyrixa] Backend started at http://{self.host}:{self.port}")
                return
            time.sleep(0.5)
        print("[Lyrixa] Backend did not start in time!")
        # Print backend stdout/stderr for debugging
        try:
            out, err = self.process.communicate(timeout=2)
        except Exception:
            out, err = "", ""
        if out:
            print("[Lyrixa][Backend STDOUT]\n" + out)
        if err:
            print("[Lyrixa][Backend STDERR]\n" + err)
        # Optionally, write to a log file
        log_path = os.path.join(
            os.path.dirname(self.script_path), "backend_startup.log"
        )
        with open(log_path, "w", encoding="utf-8") as f:
            if out:
                f.write("[STDOUT]\n" + out + "\n")
            if err:
                f.write("[STDERR]\n" + err + "\n")
        print(f"[Lyrixa] Backend startup logs written to: {log_path}")

    def stop(self):
        if self.process:
            print("[Lyrixa] Stopping backend...")
            if os.name == "nt":
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
            print("[Lyrixa] Backend stopped.")
            self.process = None


BACKEND_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "run_self_improvement_api.py"
)
backend_manager = BackendProcessManager(BACKEND_SCRIPT)

if GUI_AVAILABLE:

    class LyrixaLauncherGUI(QMainWindow):
        """Modern Dark Theme GUI for Lyrixa AI Assistant"""

        def __init__(self):
            super().__init__()
            if not GUI_AVAILABLE:
                raise RuntimeError("GUI dependencies not available")

            self.lyrixa = None
            self.aether_runtime = None
            self.intelligence_stack = None
            self.ai_dashboard_widget = None  # For linting/IDE

            # Ensure QApplication is initialized
            if not QApplication.instance():
                self.app = QApplication(sys.argv)

            # Start backend before UI
            backend_manager.start()

            self.setup_ui()
            self.setup_theme()
            self.setup_connections()

            # Enable chat immediately for basic functionality
            self.chat_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.add_chat_message(
                "System",
                "🚀 Basic chat enabled! Full initialization in progress...",
                is_system=True,
            )

        def setup_ui(self):
            """Setup the user interface"""
            self.setWindowTitle("🎙️ Lyrixa AI Assistant - Aetherra OS")
            self.setGeometry(100, 100, 1200, 800)

            # Central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # Main layout
            main_layout = QHBoxLayout(central_widget)

            # Create splitter for resizable sections
            splitter = QSplitter(Qt.Orientation.Horizontal)
            main_layout.addWidget(splitter)

            # Left panel (System Overview)
            self.setup_left_panel(splitter)

            # Right panel (Chat)
            self.setup_chat_panel(splitter)

            # Set splitter proportions (70% left, 30% right)
            splitter.setStretchFactor(0, 70)
            splitter.setStretchFactor(1, 30)

            # Status bar
            self.setup_status_bar()

            # Menu bar
            self.setup_menu_bar()

        def setup_left_panel(self, splitter):
            """Setup the left panel with system tabs"""
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)

            # System header
            header_label = QLabel("🚀 Aetherra AI OS - System Control")
            header_label.setObjectName("header")
            left_layout.addWidget(header_label)

            # Tab widget for system functions
            self.system_tabs = QTabWidget()
            left_layout.addWidget(self.system_tabs)

            # Add system tabs
            self.setup_dashboard_tab()
            self.setup_plugins_tab()
            self.setup_agents_tab()
            self.setup_tasks_tab()
            self.setup_logs_tab()

            # Delay adding Self-Improvement Dashboard Widget until backend is running
            self._ai_dashboard_widget_pending = True

            def try_add_ai_dashboard_widget():
                if backend_manager.is_running():
                    try:
                        from lyrixa.ui.self_improvement_dashboard_widget import (
                            SelfImprovementDashboardWidget,
                        )

                        self.ai_dashboard_widget = SelfImprovementDashboardWidget()
                        self.system_tabs.addTab(
                            self.ai_dashboard_widget, "AI Intelligence"
                        )
                        self._ai_dashboard_widget_pending = False
                    except Exception as e:
                        print(
                            f"[WARN] Could not load SelfImprovementDashboardWidget: {e}"
                        )
                else:
                    # Retry after 500ms
                    QTimer.singleShot(500, try_add_ai_dashboard_widget)

            from PySide6.QtCore import QTimer

            QTimer.singleShot(500, try_add_ai_dashboard_widget)

            splitter.addWidget(left_widget)

        def setup_chat_panel(self, splitter):
            """Setup the dedicated chat panel"""
            chat_widget = QWidget()
            chat_layout = QVBoxLayout(chat_widget)

            # Chat header
            chat_header = QLabel("💬 Lyrixa AI Chat")
            chat_header.setObjectName("chat_header")
            chat_layout.addWidget(chat_header)

            # Chat display area
            self.chat_display = QTextEdit()
            self.chat_display.setObjectName("chat_display")
            self.chat_display.setReadOnly(True)
            chat_layout.addWidget(self.chat_display)

            # Chat input area
            input_frame = QFrame()
            input_layout = QHBoxLayout(input_frame)

            self.chat_input = QLineEdit()
            self.chat_input.setObjectName("chat_input")
            self.chat_input.setPlaceholderText("Ask Lyrixa anything...")
            input_layout.addWidget(self.chat_input)

            self.send_button = QPushButton("Send")
            self.send_button.setObjectName("send_button")
            input_layout.addWidget(self.send_button)

            chat_layout.addWidget(input_frame)

            # Add welcome message
            self.add_chat_message(
                "Lyrixa",
                "Hello! I'm Lyrixa, your AI assistant for Aetherra. How can I help you today?",
                is_system=True,
            )

            splitter.addWidget(chat_widget)

        def setup_dashboard_tab(self):
            """Setup the system dashboard tab"""
            dashboard_widget = QWidget()
            dashboard_layout = QVBoxLayout(dashboard_widget)

            # System health section
            health_group = QGroupBox("System Health")
            health_layout = QGridLayout(health_group)

            # Health indicators
            self.plugin_health = QProgressBar()
            self.plugin_health.setValue(85)
            health_layout.addWidget(QLabel("Plugin Health:"), 0, 0)
            health_layout.addWidget(self.plugin_health, 0, 1)

            self.memory_usage = QProgressBar()
            self.memory_usage.setValue(60)
            health_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
            health_layout.addWidget(self.memory_usage, 1, 1)

            self.system_load = QProgressBar()
            self.system_load.setValue(40)
            health_layout.addWidget(QLabel("System Load:"), 2, 0)
            health_layout.addWidget(self.system_load, 2, 1)

            dashboard_layout.addWidget(health_group)

            # Self-Improvement Dashboard section
            import asyncio

            from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
            from lyrixa.core.enhanced_self_evaluation_agent import (
                EnhancedSelfEvaluationAgent,
            )

            self.self_improvement_group = QGroupBox("AI Self-Improvement")
            self.self_improvement_layout = QVBoxLayout(self.self_improvement_group)
            self.self_improvement_labels = {}
            for label in [
                ("total_evaluation_cycles", "Evaluation Cycles"),
                ("total_recommendations", "Total Recommendations"),
                ("total_auto_improvements", "Auto-Improvements"),
                ("avg_recommendations_per_cycle", "Avg Recommendations/Cycle"),
                ("improvement_rate", "Improvement Rate"),
                ("last_evaluation", "Last Evaluation"),
            ]:
                key, text = label
                lbl = QLabel(f"{text}: ...")
                self.self_improvement_layout.addWidget(lbl)
                self.self_improvement_labels[key] = lbl

            dashboard_layout.addWidget(self.self_improvement_group)

            # Recent events
            events_group = QGroupBox("Recent Events")
            events_layout = QVBoxLayout(events_group)

            self.events_list = QListWidget()
            self.events_list.addItem("🔄 Plugin watchdog: All plugins healthy")
            self.events_list.addItem("🧠 Memory cleanser: Cleaned 45 old entries")
            self.events_list.addItem("🎯 Goal autopilot: 3 goals completed")
            self.events_list.addItem("👥 Agent sync: All agents synchronized")
            events_layout.addWidget(self.events_list)

            dashboard_layout.addWidget(events_group)

            self.system_tabs.addTab(dashboard_widget, "Dashboard")

            # Async update for self-improvement metrics
            async def update_self_improvement_metrics():
                memory_system = LyrixaEnhancedMemorySystem()
                agent = EnhancedSelfEvaluationAgent(memory_system)
                metrics = await agent.get_evaluation_metrics()
                for key, lbl in self.self_improvement_labels.items():
                    val = metrics.get(key, "...")
                    if key == "improvement_rate" and isinstance(val, float):
                        val = f"{val * 100:.1f}%"
                    elif key == "avg_recommendations_per_cycle" and isinstance(
                        val, float
                    ):
                        val = f"{val:.2f}"
                    lbl.setText(f"{lbl.text().split(':')[0]}: {val}")

            def run_async_update():
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(update_self_improvement_metrics())
                else:
                    loop.run_until_complete(update_self_improvement_metrics())

            run_async_update()

        def setup_plugins_tab(self):
            """Setup the plugins management tab"""
            plugins_widget = QWidget()
            plugins_layout = QVBoxLayout(plugins_widget)

            # Plugin list
            self.plugins_table = QTableWidget()
            self.plugins_table.setColumnCount(4)
            self.plugins_table.setHorizontalHeaderLabels(
                ["Plugin", "Status", "Health", "Actions"]
            )

            # Add sample plugins
            plugins_data = [
                ("goal_autopilot", "Active", "Healthy", "Disable"),
                ("memory_cleanser", "Active", "Healthy", "Configure"),
                ("plugin_watchdog", "Active", "Healthy", "View Logs"),
                ("daily_reflector", "Active", "Healthy", "Run Now"),
                ("agent_sync", "Active", "Healthy", "Sync Now"),
            ]

            self.plugins_table.setRowCount(len(plugins_data))
            for row, (name, status, health, action) in enumerate(plugins_data):
                self.plugins_table.setItem(row, 0, QTableWidgetItem(name))
                self.plugins_table.setItem(row, 1, QTableWidgetItem(status))
                self.plugins_table.setItem(row, 2, QTableWidgetItem(health))
                self.plugins_table.setItem(row, 3, QTableWidgetItem(action))

            plugins_layout.addWidget(self.plugins_table)

            self.system_tabs.addTab(plugins_widget, "Plugins")

        def setup_agents_tab(self):
            """Setup the agents management tab"""
            agents_widget = QWidget()
            agents_layout = QVBoxLayout(agents_widget)

            # Agent list
            self.agents_table = QTableWidget()
            self.agents_table.setColumnCount(4)
            self.agents_table.setHorizontalHeaderLabels(
                ["Agent", "Role", "Status", "Tasks"]
            )

            # Add sample agents
            agents_data = [
                ("core_agent", "Core System", "Active", "2 tasks"),
                ("escalation_mgr", "Escalation", "Active", "1 task"),
                ("reflection_ai", "Reflection", "Idle", "0 tasks"),
            ]

            self.agents_table.setRowCount(len(agents_data))
            for row, (name, role, status, tasks) in enumerate(agents_data):
                self.agents_table.setItem(row, 0, QTableWidgetItem(name))
                self.agents_table.setItem(row, 1, QTableWidgetItem(role))
                self.agents_table.setItem(row, 2, QTableWidgetItem(status))
                self.agents_table.setItem(row, 3, QTableWidgetItem(tasks))

            agents_layout.addWidget(self.agents_table)

            self.system_tabs.addTab(agents_widget, "Agents")

        def setup_tasks_tab(self):
            """Setup the tasks monitoring tab"""
            tasks_widget = QWidget()
            tasks_layout = QVBoxLayout(tasks_widget)

            # Task list
            self.tasks_table = QTableWidget()
            self.tasks_table.setColumnCount(5)
            self.tasks_table.setHorizontalHeaderLabels(
                ["Task", "Status", "Progress", "Started", "ETA"]
            )

            # Add sample tasks
            tasks_data = [
                ("Memory Analysis", "Running", 75, "14:30", "2 min"),
                ("Plugin Health Check", "Completed", 100, "14:25", "Done"),
                ("Goal Processing", "Running", 45, "14:32", "5 min"),
            ]

            self.tasks_table.setRowCount(len(tasks_data))

            for row, (name, status, progress, started, eta) in enumerate(tasks_data):
                # Task name (read-only)
                name_item = QTableWidgetItem(name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tasks_table.setItem(row, 0, name_item)

                # Status (read-only)
                status_item = QTableWidgetItem(status)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tasks_table.setItem(row, 1, status_item)

                # Progress bar
                progress_bar = QProgressBar()
                progress_bar.setValue(progress)
                self.tasks_table.setCellWidget(row, 2, progress_bar)

                # Started (read-only)
                started_item = QTableWidgetItem(started)
                started_item.setFlags(
                    started_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
                self.tasks_table.setItem(row, 3, started_item)

                # ETA (read-only)
                eta_item = QTableWidgetItem(eta)
                eta_item.setFlags(eta_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tasks_table.setItem(row, 4, eta_item)

            tasks_layout.addWidget(self.tasks_table)

            self.system_tabs.addTab(tasks_widget, "Tasks")

        def setup_logs_tab(self):
            """Setup the logs viewing tab"""
            logs_widget = QWidget()
            logs_layout = QVBoxLayout(logs_widget)

            # Log display
            self.logs_display = QTextEdit()
            self.logs_display.setReadOnly(True)
            self.logs_display.setObjectName("logs_display")

            # Add sample log entries
            sample_logs = [
                "2025-07-07 14:30:15 [INFO] Plugin watchdog: All plugins healthy",
                "2025-07-07 14:25:32 [INFO] Memory cleanser: Cleaned 45 old entries",
                "2025-07-07 14:20:45 [SUCCESS] Goal autopilot: Goal #123 completed",
                "2025-07-07 14:15:12 [INFO] Agent sync: Synchronized 3 agents",
                "2025-07-07 14:10:30 [INFO] Daily reflector: Reflection generated",
            ]

            self.logs_display.setPlainText("\n".join(sample_logs))

            logs_layout.addWidget(self.logs_display)

            self.system_tabs.addTab(logs_widget, "Logs")

        def setup_status_bar(self):
            """Setup the status bar"""
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("🚀 Lyrixa AI Assistant - Ready")

        def setup_menu_bar(self):
            """Setup the menu bar"""
            menubar = self.menuBar()

            # File menu
            file_menu = menubar.addMenu("File")
            file_menu.addAction("New Session")
            file_menu.addAction("Save Chat")
            file_menu.addSeparator()
            file_menu.addAction("Exit")

            # System menu
            system_menu = menubar.addMenu("System")
            system_menu.addAction("Refresh Status")
            system_menu.addAction("Run Diagnostics")
            system_menu.addAction("Export Logs")

            # Help menu
            help_menu = menubar.addMenu("Help")
            help_menu.addAction("About Lyrixa")
            help_menu.addAction("Documentation")

        def setup_theme(self):
            """Apply dark theme with Aetherra green accents"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }

                QWidget {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }

                QLabel#header {
                    font-size: 16px;
                    font-weight: bold;
                    color: #22c55e;
                    padding: 10px;
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }

                QLabel#chat_header {
                    font-size: 14px;
                    font-weight: bold;
                    color: #22c55e;
                    padding: 8px;
                    background-color: #2d2d2d;
                    border-radius: 5px;
                    margin-bottom: 5px;
                }

                QTabWidget::pane {
                    border: 1px solid #3d3d3d;
                    background-color: #2d2d2d;
                }

                QTabBar::tab {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }

                QTabBar::tab:selected {
                    background-color: #22c55e;
                    color: #000000;
                }

                QTabBar::tab:hover {
                    background-color: #4ade80;
                    color: #000000;
                }

                QTextEdit#chat_display {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                    padding: 10px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 12px;
                    line-height: 1.4;
                }

                QTextEdit#logs_display {
                    background-color: #1a1a1a;
                    border: 1px solid #3d3d3d;
                    border-radius: 8px;
                    padding: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                    color: #cccccc;
                }

                QLineEdit#chat_input {
                    background-color: #2d2d2d;
                    border: 2px solid #3d3d3d;
                    border-radius: 20px;
                    padding: 8px 15px;
                    font-size: 12px;
                    color: #ffffff;
                }

                QLineEdit#chat_input:focus {
                    border-color: #22c55e;
                }

                QPushButton#send_button {
                    background-color: #22c55e;
                    color: #000000;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 20px;
                    font-weight: bold;
                    font-size: 12px;
                }

                QPushButton#send_button:hover {
                    background-color: #4ade80;
                }

                QPushButton#send_button:pressed {
                    background-color: #16a34a;
                }

                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    gridline-color: #3d3d3d;
                }

                QTableWidget::item {
                    padding: 8px;
                    border: none;
                }

                QTableWidget::item:selected {
                    background-color: #22c55e;
                    color: #000000;
                }

                QListWidget {
                    background-color: #2d2d2d;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    color: #ffffff;
                    padding: 5px;
                }

                QListWidget::item {
                    padding: 5px;
                    border-bottom: 1px solid #3d3d3d;
                }

                QListWidget::item:selected {
                    background-color: #22c55e;
                    color: #000000;
                }

                QProgressBar {
                    background-color: #3d3d3d;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    text-align: center;
                    color: #ffffff;
                }

                QProgressBar::chunk {
                    background-color: #22c55e;
                    border-radius: 5px;
                }

                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #3d3d3d;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }

                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #22c55e;
                }

                QStatusBar {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border-top: 1px solid #22c55e;
                }

                QMenuBar {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border-bottom: 1px solid #3d3d3d;
                }

                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }

                QMenuBar::item:selected {
                    background-color: #22c55e;
                    color: #000000;
                }

                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                }

                QMenu::item:selected {
                    background-color: #22c55e;
                    color: #000000;
                }

                QSplitter::handle {
                    background-color: #3d3d3d;
                    width: 3px;
                }

                QSplitter::handle:hover {
                    background-color: #22c55e;
                }
            """)

        def setup_connections(self):
            """Setup signal connections"""
            self.send_button.clicked.connect(self.send_chat_message)
            self.chat_input.returnPressed.connect(self.send_chat_message)

        def send_chat_message(self):
            """Send a chat message"""
            message = self.chat_input.text().strip()
            if not message:
                return

            # Add user message
            self.add_chat_message("You", message, is_user=True)
            self.chat_input.clear()

            # Simulate AI response (replace with actual Lyrixa integration)
            self.simulate_ai_response(message)

        def add_chat_message(self, sender, message, is_user=False, is_system=False):
            """Add a message to the chat display"""
            cursor = self.chat_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)

            # Format message
            if is_system:
                formatted_message = f"🤖 {sender}: {message}\n\n"
                color = "#22c55e"
            elif is_user:
                formatted_message = f"👤 {sender}: {message}\n\n"
                color = "#4ade80"
            else:
                formatted_message = f"🎙️ {sender}: {message}\n\n"
                color = "#ffffff"

            # Apply formatting
            format = QTextCharFormat()
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
            cursor.insertText(formatted_message)

            # Auto-scroll to bottom
            self.chat_display.moveCursor(QTextCursor.MoveOperation.End)
            self.chat_display.ensureCursorVisible()

        def simulate_ai_response(self, user_message):
            """Generate AI response using intelligence stack or basic AI responses"""
            if not self.intelligence_stack:
                # Use OpenAI directly for better basic responses
                anthropic_key = None  # Ensure anthropic_key is always defined
                try:
                    import os

                    import openai
                    from dotenv import load_dotenv

                    # Load environment variables
                    load_dotenv()
                    openai_key = os.getenv("OPENAI_API_KEY")
                    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

                    # Try OpenAI first, then Claude if quota exceeded
                    if openai_key:
                        try:
                            client = openai.OpenAI(api_key=openai_key)
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "You are Lyrixa, an advanced AI assistant from the Aetherra project. You have full AI capabilities and can help with complex tasks, coding, analysis, and more. Be intelligent, helpful, and engaging.",
                                    },
                                    {"role": "user", "content": user_message},
                                ],
                                max_tokens=300,
                                temperature=0.7,
                            )
                            ai_response = response.choices[0].message.content
                            self.add_chat_message("Lyrixa", f"{ai_response} ✨")
                            return
                        except Exception as openai_error:
                            print(f"OpenAI failed (quota?): {openai_error}")
                            # Fall through to try Claude
                except Exception as openai_error:
                    print(f"OpenAI failed (quota?): {openai_error}")
                    # Fall through to try Claude

                # Try Claude if OpenAI fails
                if anthropic_key:
                    try:
                        import anthropic

                        client = anthropic.Anthropic(api_key=anthropic_key)
                        response = client.messages.create(
                            model="claude-3-sonnet-20240229",
                            max_tokens=300,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"You are Lyrixa, an advanced AI assistant from the Aetherra project. You have full AI capabilities. User message: {user_message}",
                                }
                            ],
                        )
                        # Claude v3 API returns blocks, use .content or str() to get text
                        block = response.content[0]
                        ai_response = getattr(block, "text", None)
                        if ai_response is None:
                            ai_response = getattr(block, "content", None)
                        if ai_response is None:
                            ai_response = str(block)
                        self.add_chat_message("Lyrixa", f"{ai_response} 🧠")
                        return
                    except Exception as claude_error:
                        print(f"Claude failed: {claude_error}")
                        # Fallback to basic response if Claude also fails
                        response = self.generate_basic_response(user_message)
                        self.add_chat_message("Lyrixa", response)
                        return

                # Fallback to enhanced basic responses
                response = self.generate_basic_response(user_message)
                self.add_chat_message("Lyrixa", response)
                return

            # Check for intelligence commands first
            message_lower = user_message.lower()

            # Intelligence stack commands
            if (
                "intelligence status" in message_lower
                or "system status" in message_lower
            ):
                if GUI_AVAILABLE:
                    QTimer.singleShot(500, lambda: self.handle_intelligence_status())
                else:
                    self.handle_intelligence_status()
                return
            elif "run workflow" in message_lower:
                workflow_name = self.extract_workflow_name(user_message)
                if workflow_name:
                    if GUI_AVAILABLE:
                        QTimer.singleShot(
                            500, lambda: self.handle_run_workflow(workflow_name)
                        )
                    else:
                        self.handle_run_workflow(workflow_name)
                else:
                    if GUI_AVAILABLE:
                        QTimer.singleShot(
                            500,
                            lambda: self.add_chat_message(
                                "Lyrixa",
                                "Available workflows: goal_autopilot, agent_sync, memory_cleanser, daily_reflector, plugin_watchdog",
                            ),
                        )
                    else:
                        self.add_chat_message(
                            "Lyrixa",
                            "Available workflows: goal_autopilot, agent_sync, memory_cleanser, daily_reflector, plugin_watchdog",
                        )
                return
            elif "system reflection" in message_lower:
                if GUI_AVAILABLE:
                    QTimer.singleShot(500, lambda: self.handle_system_reflection())
                else:
                    self.handle_system_reflection()
                return
            elif "intelligence health" in message_lower:
                if GUI_AVAILABLE:
                    QTimer.singleShot(500, lambda: self.handle_intelligence_health())
                else:
                    self.handle_intelligence_health()
                return

            # Use intelligence stack for dynamic conversation (now LLM-powered!)
            try:
                response = self.intelligence_stack.generate_response(user_message)
                if not response:
                    response = "I'm sorry, I couldn't process your request."

                # Check if this is a fallback response and add helpful context
                if (
                    "fallback mode" in response.lower()
                    or "smart fallback" in response.lower()
                ):
                    # Add helpful hint about model status
                    status_hint = "\n\n💡 *Note: AI models are currently unavailable (API quota/billing issues), but I'm still functional with enhanced fallback responses!*"
                    response += status_hint

            except Exception as e:
                response = f"Error generating response: {e}"

            # Add AI response with a slight delay for realism
            if GUI_AVAILABLE:
                QTimer.singleShot(
                    1000, lambda: self.add_chat_message("Lyrixa", response)
                )
            else:
                self.add_chat_message("Lyrixa", response)

        def generate_basic_response(self, user_message):
            """Generate intelligent basic responses without full AI stack"""
            message_lower = user_message.lower()

            # Greeting responses
            if any(
                word in message_lower for word in ["hello", "hi", "hey", "greetings"]
            ):
                return "Hello! I'm Lyrixa, your AI assistant. How can I help you today? (Basic mode - full capabilities loading...)"

            # Help requests (check before questions to prioritize)
            elif any(word in message_lower for word in ["help", "assist", "support"]):
                return "I'm here to help! I'm currently in basic mode while loading my full capabilities. You can ask me anything, and I'll do my best to assist you."

            # Status requests
            elif any(word in message_lower for word in ["status", "ready", "working"]):
                return "I'm partially online! My basic chat functions are working, and I'm currently loading my advanced intelligence modules. Full capabilities will be available shortly."

            # Aetherra/Project questions
            elif any(
                word in message_lower
                for word in ["aetherra", "project", "what are you"]
            ):
                return "I'm Lyrixa, an AI assistant that's part of the Aetherra project - an AI-native operating system. I'm currently starting up my full intelligence stack!"

            # Question responses (broader check last)
            elif "?" in user_message:
                return "That's an interesting question. I'm currently in basic mode while my full intelligence stack initializes. I'll be able to provide more detailed answers soon!"

            # Default intelligent response
            else:
                return f"I understand you're saying '{user_message}'. I'm processing this in basic mode while my full AI capabilities initialize. Thank you for your patience!"

        def extract_workflow_name(self, message):
            """Extract workflow name from user message"""
            workflows = [
                "goal_autopilot",
                "agent_sync",
                "memory_cleanser",
                "daily_reflector",
                "plugin_watchdog",
            ]
            message_lower = message.lower()

            for workflow in workflows:
                if workflow in message_lower:
                    return workflow
            return None

        def handle_intelligence_status(self):
            """Handle intelligence status request"""
            asyncio.create_task(self.async_intelligence_status())

        async def async_intelligence_status(self):
            """Async handler for intelligence status"""
            try:
                if not self.intelligence_stack:
                    self.add_chat_message(
                        "Lyrixa",
                        "[ERROR] Intelligence stack not initialized",
                        is_system=True,
                    )
                    return

                status = await self.intelligence_stack.get_intelligence_status()
                health_score = status.get("overall_health", 0) * 100

                # Intelligence Layer Status
                intel_status = status.get("intelligence_layer", {})
                intel_health = intel_status.get("health", 0) * 100

                # System Workflows Status
                workflow_status = status.get("system_workflows", {})
                workflow_health = workflow_status.get("health", 0) * 100
                active_workflows = workflow_status.get("active_count", 0)

                # System Modules Status
                module_status = status.get("system_modules", {})
                module_health = module_status.get("health", 0) * 100
                active_modules = module_status.get("active_count", 0)

                # Generate comprehensive status report
                status_report = f"""🧠 INTELLIGENCE STACK STATUS

🎯 Overall Health: {health_score:.1f}%
🔬 Intelligence Layer: {intel_health:.1f}%
📊 System Workflows: {workflow_health:.1f}% ({active_workflows}/5 active)
⚙️ System Modules: {module_health:.1f}% ({active_modules}/6 active)

💡 Intelligence Components:
• Semantic Memory: {"✅" if status["intelligence_layer"]["status"].get("semantic_memory") else "[ERROR]"}
• System Awareness: {"✅" if status["intelligence_layer"]["status"].get("system_awareness") else "[ERROR]"}
• Self Reflection: {"✅" if status["intelligence_layer"]["status"].get("self_reflection") else "[ERROR]"}
• Event Correlation: {"✅" if status["intelligence_layer"]["status"].get("event_correlation") else "[ERROR]"}
• Conversational Integration: {"✅" if status["intelligence_layer"]["status"].get("conversational_integration") else "[ERROR]"}
• Plugin Monitoring: {"✅" if status["intelligence_layer"]["status"].get("plugin_monitoring") else "[ERROR]"}"""

                self.add_chat_message("Lyrixa", status_report)

            except Exception as e:
                self.add_chat_message(
                    "Lyrixa", f"[ERROR] Failed to get intelligence status: {e}"
                )

        def handle_run_workflow(self, workflow_name):
            """Handle workflow execution request"""
            asyncio.create_task(self.async_run_workflow(workflow_name))

        async def async_run_workflow(self, workflow_name):
            """Async handler for workflow execution"""
            await self.run_intelligence_workflow(workflow_name)

        def handle_system_reflection(self):
            """Handle system reflection request"""
            asyncio.create_task(self.async_system_reflection())

        async def async_system_reflection(self):
            """Async handler for system reflection"""
            await self.perform_system_reflection()

        def handle_intelligence_health(self):
            """Handle intelligence health request"""
            asyncio.create_task(self.async_intelligence_health())

        async def async_intelligence_health(self):
            """Async handler for intelligence health"""
            try:
                if not self.intelligence_stack:
                    self.add_chat_message(
                        "Lyrixa", "[ERROR] Intelligence stack not initialized"
                    )
                    return

                status = await self.intelligence_stack.get_intelligence_status()
                health_score = status.get("overall_health", 0) * 100

                if health_score >= 80:
                    health_status = "🟢 Excellent"
                elif health_score >= 60:
                    health_status = "🟡 Good"
                else:
                    health_status = "🔴 Needs Attention"

                self.add_chat_message(
                    "Lyrixa",
                    f"🎯 Intelligence Health: {health_status} ({health_score:.1f}%)",
                )

            except Exception as e:
                self.add_chat_message(
                    "Lyrixa", f"[ERROR] Failed to get intelligence health: {e}"
                )

        async def initialize_lyrixa(self):
            """Initialize Lyrixa and all core systems"""
            try:
                workspace_path = os.getcwd()
                self.status_bar.showMessage("🎙️ Initializing Lyrixa AI...")

                # Add a timeout to prevent hanging
                print("🔄 Starting Lyrixa initialization...")

                # Initialize Lyrixa core with timeout
                self.lyrixa = LyrixaAI(workspace_path=workspace_path)
                print("🔄 Lyrixa AI instance created, calling initialize...")
                await asyncio.wait_for(self.lyrixa.initialize(), timeout=60.0)
                print("✅ Lyrixa AI initialized")

                # Ensure memory and plugins are initialized
                if not self.lyrixa.memory or not self.lyrixa.plugins:
                    raise RuntimeError(
                        "Lyrixa's memory or plugins failed to initialize."
                    )

                # Initialize Aether Runtime with timeout
                print("🔄 Initializing Aether Runtime...")
                self.aether_runtime = AetherRuntime()

                # Register context BEFORE initialization
                self.aether_runtime.register_context(
                    memory=self.lyrixa.memory,
                    plugins=self.lyrixa.plugins,
                    agents=self.lyrixa.agents,
                )

                await asyncio.wait_for(self.aether_runtime.initialize(), timeout=30.0)
                print("✅ Aether Runtime initialized")

                # Initialize Intelligence Stack with timeout
                self.status_bar.showMessage("🧠 Initializing Intelligence Stack...")
                print("🔄 Initializing Intelligence Stack...")
                self.intelligence_stack = LyrixaIntelligenceStack(
                    workspace_path=workspace_path, aether_runtime=self.aether_runtime
                )

                # Initialize all components sequentially with timeouts
                await asyncio.wait_for(
                    self.intelligence_stack.initialize_intelligence_layer(),
                    timeout=30.0,
                )
                print("✅ Intelligence layer initialized")

                await asyncio.wait_for(
                    self.intelligence_stack.initialize_system_workflows(), timeout=30.0
                )
                print("✅ System workflows initialized")

                await asyncio.wait_for(
                    self.intelligence_stack.initialize_system_modules(), timeout=30.0
                )
                print("✅ System modules initialized")

                # Update UI
                await self.update_intelligence_dashboard()

                self.status_bar.showMessage("✅ Lyrixa AI - Ready")
                self.add_chat_message(
                    "System",
                    "🧠 Lyrixa AI initialized and ready for conversation!",
                    is_system=True,
                )

                # Enable chat input
                self.chat_input.setEnabled(True)
                self.send_button.setEnabled(True)
                print("✅ Lyrixa launcher fully initialized and ready!")

            except asyncio.TimeoutError as e:
                error_msg = f"⏱️ Initialization timed out: {str(e)}"
                print(error_msg)
                self.status_bar.showMessage("[ERROR] Initialization timed out")
                self.add_chat_message("System", error_msg, is_system=True)
            except Exception as e:
                error_msg = f"[ERROR] Initialization failed: {str(e)}"
                print(error_msg)
                self.status_bar.showMessage(f"[ERROR] Initialization failed: {str(e)}")
                self.add_chat_message(
                    "System", f"[WARN] Initialization error: {str(e)}", is_system=True
                )

        async def update_intelligence_dashboard(self):
            """Update the intelligence dashboard with current status"""
            try:
                if not self.intelligence_stack:
                    return

                # Get current intelligence status
                intelligence_status = (
                    await self.intelligence_stack.get_intelligence_status()
                )

                # Update system health display
                overall_health = intelligence_status.get("overall_health", 0)
                health_percentage = int(overall_health * 100)

                # Update progress bars and labels in the dashboard
                # This would update the GUI elements created in setup_dashboard_tab

                # Update chat with intelligence insights
                if overall_health > 0.8:
                    status_msg = (
                        f"🟢 Intelligence Stack: Excellent ({health_percentage}%)"
                    )
                elif overall_health > 0.6:
                    status_msg = f"🟡 Intelligence Stack: Good ({health_percentage}%)"
                else:
                    status_msg = (
                        f"🔴 Intelligence Stack: Needs Attention ({health_percentage}%)"
                    )

                self.add_chat_message("System", status_msg, is_system=True)

                # Update workflow status
                workflow_status = intelligence_status.get("system_workflows", {})
                active_workflows = workflow_status.get("active_count", 0)
                self.add_chat_message(
                    "System",
                    f"📊 Active Workflows: {active_workflows}/5",
                    is_system=True,
                )

                # Update module status
                module_status = intelligence_status.get("system_modules", {})
                active_modules = module_status.get("active_count", 0)
                self.add_chat_message(
                    "System", f"⚙️ Active Modules: {active_modules}/6", is_system=True
                )

            except Exception as e:
                print(f"[ERROR] Failed to update intelligence dashboard: {e}")

        async def run_intelligence_workflow(self, workflow_name: str):
            """Run a specific intelligence workflow"""
            try:
                if not self.intelligence_stack:
                    self.add_chat_message(
                        "System",
                        "[ERROR] Intelligence stack not initialized",
                        is_system=True,
                    )
                    return

                self.add_chat_message(
                    "System", f"🚀 Running workflow: {workflow_name}", is_system=True
                )
                result = await self.intelligence_stack.run_intelligence_workflow(
                    workflow_name
                )

                if result.get("success", False):
                    self.add_chat_message(
                        "System",
                        f"✅ Workflow '{workflow_name}' completed successfully!",
                        is_system=True,
                    )
                else:
                    error_message = result.get("error", "Unknown error")
                    self.add_chat_message(
                        "System",
                        f"[ERROR] Workflow '{workflow_name}' failed: {error_message}",
                        is_system=True,
                    )

            except Exception as e:
                self.add_chat_message(
                    "System", f"[ERROR] Failed to run workflow: {e}", is_system=True
                )

        async def perform_system_reflection(self):
            """Perform comprehensive system reflection"""
            try:
                if not self.intelligence_stack:
                    self.add_chat_message(
                        "System",
                        "[ERROR] Intelligence stack not initialized",
                        is_system=True,
                    )
                    return

                self.add_chat_message(
                    "System", "🔍 Performing system reflection...", is_system=True
                )
                reflection_result = (
                    await self.intelligence_stack.perform_system_reflection()
                )

                if reflection_result.get("success", False):
                    insights = reflection_result.get(
                        "insights", "No insights available."
                    )
                    self.add_chat_message(
                        "System", f"🧠 Reflection Insights: {insights}", is_system=True
                    )
                else:
                    error_message = reflection_result.get("error", "Unknown error")
                    self.add_chat_message(
                        "System",
                        f"[ERROR] System reflection failed: {error_message}",
                        is_system=True,
                    )

            except Exception as e:
                self.add_chat_message(
                    "System",
                    f"[ERROR] Failed to perform system reflection: {e}",
                    is_system=True,
                )


def run_gui():
    """Run the GUI version of Lyrixa"""
    if not GUI_AVAILABLE:
        print("[ERROR] GUI dependencies not available. Please install PySide6:")
        print("pip install PySide6")
        return False

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better dark theme support

    launcher = LyrixaLauncherGUI()
    launcher.show()

    # Use QTimer properly to avoid threading issues
    from PySide6.QtCore import QTimer

    def start_initialization():
        asyncio.ensure_future(launcher.initialize_lyrixa())

    timer = QTimer()
    timer.singleShot(1000, start_initialization)

    # Ensure backend stops when app closes
    def cleanup_backend():
        backend_manager.stop()

    app.aboutToQuit.connect(cleanup_backend)

    try:
        app.exec()
    finally:
        backend_manager.stop()


def main():
    """Main entry point for Lyrixa AI Assistant"""
    if not GUI_AVAILABLE:
        print("[ERROR] GUI dependencies not available. Please install PySide6:")
        print("pip install PySide6")
        return

    return run_gui()


if __name__ == "__main__":
    if not GUI_AVAILABLE:
        print("[ERROR] GUI dependencies not available. Please install PySide6:")
        print("pip install PySide6")
        print("Run: pip install PySide6")
        sys.exit(1)

    # Run the GUI application
    sys.exit(main())
