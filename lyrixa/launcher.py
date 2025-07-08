#!/usr/bin/env python3
"""
🎙️ LYRIXA AI ASSISTANT LAUNCHER
===============================

Launch the new Python-based Lyrixa AI Assistant for Aetherra.
Enhanced with Aether Runtime integration for AI OS capabilities.
Features modern dark theme GUI with Aetherra green accents.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent  # Go up one level to project root
sys.path.insert(0, str(project_root))

# Try to import GUI dependencies
GUI_AVAILABLE = False
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
    print(f"⚠️ GUI dependencies not available: {e}")
    print("To use GUI mode, install PySide6: pip install PySide6")
    GUI_AVAILABLE = False

try:
    from Aetherra.runtime.aether_runtime import AetherRuntime
    from lyrixa import LyrixaAI
    from lyrixa.intelligence_integration import LyrixaIntelligenceStack
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running this from the project root directory.")
    sys.exit(1)


class LyrixaLauncherGUI(QMainWindow):
    """Modern Dark Theme GUI for Lyrixa AI Assistant"""

    def __init__(self):
        super().__init__()
        self.lyrixa = None
        self.aether_runtime = None
        self.intelligence_stack = None
        self.setup_ui()
        self.setup_theme()
        self.setup_connections()

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
        splitter = QSplitter(Qt.Horizontal)
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
            self.tasks_table.setItem(row, 0, QTableWidgetItem(name))
            self.tasks_table.setItem(row, 1, QTableWidgetItem(status))

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setValue(progress)
            self.tasks_table.setCellWidget(row, 2, progress_bar)

            self.tasks_table.setItem(row, 3, QTableWidgetItem(started))
            self.tasks_table.setItem(row, 4, QTableWidgetItem(eta))

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
        cursor.movePosition(QTextCursor.End)

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
        self.chat_display.moveCursor(QTextCursor.End)
        self.chat_display.ensureCursorVisible()

    def simulate_ai_response(self, user_message):
        """Generate AI response using intelligence stack"""
        # Check for intelligence commands first
        message_lower = user_message.lower()
        
        # Intelligence stack commands
        if "intelligence status" in message_lower or "system status" in message_lower:
            QTimer.singleShot(500, lambda: self.handle_intelligence_status())
            return
        elif "run workflow" in message_lower:
            workflow_name = self.extract_workflow_name(user_message)
            if workflow_name:
                QTimer.singleShot(500, lambda: self.handle_run_workflow(workflow_name))
            else:
                QTimer.singleShot(500, lambda: self.add_chat_message("Lyrixa", "Available workflows: goal_autopilot, agent_sync, memory_cleanser, daily_reflector, plugin_watchdog"))
            return
        elif "system reflection" in message_lower:
            QTimer.singleShot(500, lambda: self.handle_system_reflection())
            return
        elif "intelligence health" in message_lower:
            QTimer.singleShot(500, lambda: self.handle_intelligence_health())
            return
        
        # Traditional responses enhanced with intelligence awareness
        responses = {
            "hello": "Hello! I'm Lyrixa, your AI assistant with full intelligence stack integration. How can I help you today?",
            "status": "🎯 System Status: All intelligence components are active. Use 'intelligence status' for detailed analysis.",
            "help": "I can help you with:\n• 🧠 Intelligence stack monitoring\n• 📊 System workflow execution\n• 🔍 System reflection and analysis\n• ⚙️ Plugin and agent management\n• 📈 Performance optimization\n\nTry: 'intelligence status', 'run workflow', or 'system reflection'",
            "plugins": "🔌 Plugin monitoring via intelligence stack. Use 'run workflow plugin_watchdog' for detailed health check.",
            "agents": "🤖 Agent synchronization active. Use 'run workflow agent_sync' to ensure all agents are in sync.",
            "memory": "🧠 Memory management via intelligence stack. Use 'run workflow memory_cleanser' to optimize memory.",
            "goals": "🎯 Goal management active. Use 'run workflow goal_autopilot' to check goal status.",
        }

        response = "I'm processing your request using the intelligence stack. How can I assist you further?"
        
        for key, value in responses.items():
            if key in message_lower:
                response = value
                break

        # Add AI response with a slight delay for realism
        QTimer.singleShot(1000, lambda: self.add_chat_message("Lyrixa", response))

    def extract_workflow_name(self, message):
        """Extract workflow name from user message"""
        workflows = ["goal_autopilot", "agent_sync", "memory_cleanser", "daily_reflector", "plugin_watchdog"]
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
                self.add_chat_message("Lyrixa", "❌ Intelligence stack not initialized", is_system=True)
                return

            status = await self.intelligence_stack.get_intelligence_status()
            health_score = status.get('overall_health', 0) * 100
            
            # Intelligence Layer Status
            intel_status = status.get('intelligence_layer', {})
            intel_health = intel_status.get('health', 0) * 100
            
            # System Workflows Status
            workflow_status = status.get('system_workflows', {})
            workflow_health = workflow_status.get('health', 0) * 100
            active_workflows = workflow_status.get('active_count', 0)
            
            # System Modules Status
            module_status = status.get('system_modules', {})
            module_health = module_status.get('health', 0) * 100
            active_modules = module_status.get('active_count', 0)
            
            # Generate comprehensive status report
            status_report = f"""🧠 INTELLIGENCE STACK STATUS
            
🎯 Overall Health: {health_score:.1f}%
🔬 Intelligence Layer: {intel_health:.1f}%
📊 System Workflows: {workflow_health:.1f}% ({active_workflows}/5 active)
⚙️ System Modules: {module_health:.1f}% ({active_modules}/6 active)

💡 Intelligence Components:
• Semantic Memory: {'✅' if status['intelligence_layer']['status'].get('semantic_memory') else '❌'}
• System Awareness: {'✅' if status['intelligence_layer']['status'].get('system_awareness') else '❌'}
• Self Reflection: {'✅' if status['intelligence_layer']['status'].get('self_reflection') else '❌'}
• Event Correlation: {'✅' if status['intelligence_layer']['status'].get('event_correlation') else '❌'}
• Conversational Integration: {'✅' if status['intelligence_layer']['status'].get('conversational_integration') else '❌'}
• Plugin Monitoring: {'✅' if status['intelligence_layer']['status'].get('plugin_monitoring') else '❌'}"""

            self.add_chat_message("Lyrixa", status_report)
            
        except Exception as e:
            self.add_chat_message("Lyrixa", f"❌ Failed to get intelligence status: {e}")

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
                self.add_chat_message("Lyrixa", "❌ Intelligence stack not initialized")
                return

            status = await self.intelligence_stack.get_intelligence_status()
            health_score = status.get('overall_health', 0) * 100
            
            if health_score >= 80:
                health_status = "🟢 Excellent"
            elif health_score >= 60:
                health_status = "🟡 Good"
            else:
                health_status = "🔴 Needs Attention"
                
            self.add_chat_message("Lyrixa", f"🎯 Intelligence Health: {health_status} ({health_score:.1f}%)")
            
        except Exception as e:
            self.add_chat_message("Lyrixa", f"❌ Failed to get intelligence health: {e}")

    async def initialize_lyrixa(self):
        """Initialize Lyrixa AI system with full intelligence stack"""
        try:
            self.status_bar.showMessage("🚀 Initializing Lyrixa AI...")

            # Initialize Lyrixa
            workspace_path = str(project_root)
            self.lyrixa = LyrixaAI(workspace_path=workspace_path)
            await self.lyrixa.initialize()

            # Initialize Aether Runtime
            self.aether_runtime = AetherRuntime()
            self.aether_runtime.register_context(
                memory=getattr(self.lyrixa, "memory_system", None),
                plugins=getattr(self.lyrixa, "plugin_manager", None),
                agents=getattr(self.lyrixa, "agent_system", None),
            )

            # Initialize Intelligence Stack
            self.status_bar.showMessage("🧠 Initializing Intelligence Stack...")
            self.intelligence_stack = LyrixaIntelligenceStack(
                workspace_path=workspace_path, 
                aether_runtime=self.aether_runtime
            )
            
            # Initialize all intelligence components
            intelligence_result = await self.intelligence_stack.initialize_intelligence_layer()
            workflow_result = await self.intelligence_stack.initialize_system_workflows()
            module_result = await self.intelligence_stack.initialize_system_modules()
            
            # Update UI with intelligence status
            await self.update_intelligence_dashboard()

            self.status_bar.showMessage("✅ Lyrixa AI - Ready (Intelligence Stack Active)")
            self.add_chat_message(
                "System", "🧠 Lyrixa AI system initialized with full intelligence stack!", is_system=True
            )
            
            # Show intelligence summary
            intelligence_status = await self.intelligence_stack.get_intelligence_status()
            health_score = intelligence_status.get('overall_health', 0) * 100
            self.add_chat_message(
                "System", f"🎯 Intelligence Stack Health: {health_score:.1f}%", is_system=True
            )

        except Exception as e:
            self.status_bar.showMessage(f"❌ Initialization failed: {str(e)}")
            self.add_chat_message(
                "System", f"Failed to initialize: {str(e)}", is_system=True
            )

    async def update_intelligence_dashboard(self):
        """Update the intelligence dashboard with current status"""
        try:
            if not self.intelligence_stack:
                return

            # Get current intelligence status
            intelligence_status = await self.intelligence_stack.get_intelligence_status()
            
            # Update system health display
            overall_health = intelligence_status.get('overall_health', 0)
            health_percentage = int(overall_health * 100)
            
            # Update progress bars and labels in the dashboard
            # This would update the GUI elements created in setup_dashboard_tab
            
            # Update chat with intelligence insights
            if overall_health > 0.8:
                status_msg = f"🟢 Intelligence Stack: Excellent ({health_percentage}%)"
            elif overall_health > 0.6:
                status_msg = f"🟡 Intelligence Stack: Good ({health_percentage}%)"
            else:
                status_msg = f"🔴 Intelligence Stack: Needs Attention ({health_percentage}%)"
                
            self.add_chat_message("System", status_msg, is_system=True)
            
            # Update workflow status
            workflow_status = intelligence_status.get('system_workflows', {})
            active_workflows = workflow_status.get('active_count', 0)
            self.add_chat_message("System", f"📊 Active Workflows: {active_workflows}/5", is_system=True)
            
            # Update module status
            module_status = intelligence_status.get('system_modules', {})
            active_modules = module_status.get('active_count', 0)
            self.add_chat_message("System", f"⚙️ Active Modules: {active_modules}/6", is_system=True)

        except Exception as e:
            print(f"❌ Failed to update intelligence dashboard: {e}")

    async def run_intelligence_workflow(self, workflow_name: str):
        """Run a specific intelligence workflow"""
        try:
            if not self.intelligence_stack:
                self.add_chat_message("System", "❌ Intelligence stack not initialized", is_system=True)
                return

            self.add_chat_message("System", f"🚀 Running workflow: {workflow_name}", is_system=True)
            result = await self.intelligence_stack.run_intelligence_workflow(workflow_name)
            
            if result.get('success', False):
                self.add_chat_message("System", f"✅ Workflow '{workflow_name}' completed successfully", is_system=True)
            else:
                error_msg = result.get('message', 'Unknown error')
                self.add_chat_message("System", f"❌ Workflow '{workflow_name}' failed: {error_msg}", is_system=True)
                
        except Exception as e:
            self.add_chat_message("System", f"❌ Failed to run workflow: {e}", is_system=True)

    async def perform_system_reflection(self):
        """Perform comprehensive system reflection"""
        try:
            if not self.intelligence_stack:
                self.add_chat_message("System", "❌ Intelligence stack not initialized", is_system=True)
                return

            self.add_chat_message("System", "🔍 Performing system reflection...", is_system=True)
            reflection = await self.intelligence_stack.perform_system_reflection()
            
            # Display reflection insights
            insights = reflection.get('insights', [])
            for insight in insights[:3]:  # Show first 3 insights
                self.add_chat_message("System", f"💡 {insight}", is_system=True)
            
            # Display recommendations
            recommendations = reflection.get('recommendations', [])
            for recommendation in recommendations[:2]:  # Show first 2 recommendations
                self.add_chat_message("System", f"📋 {recommendation}", is_system=True)
                
            confidence = reflection.get('confidence_score', 0) * 100
            self.add_chat_message("System", f"🎯 Analysis Confidence: {confidence:.1f}%", is_system=True)
            
        except Exception as e:
            self.add_chat_message("System", f"❌ System reflection failed: {e}", is_system=True)


def run_gui():
    """Run the GUI version of Lyrixa"""
    if not GUI_AVAILABLE:
        print("❌ GUI dependencies not available. Please install PySide6:")
        print("pip install PySide6")
        return False

    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better dark theme support

    launcher = LyrixaLauncherGUI()
    launcher.show()

    # Initialize Lyrixa in the background
    QTimer.singleShot(500, lambda: asyncio.create_task(launcher.initialize_lyrixa()))

    return app.exec()


async def main():
    """Original console-based main function"""
    print("🎙️ Starting Lyrixa AI Assistant for Aetherra...")
    print("🚀 Initializing AI OS Kernel...")

    # Initialize Lyrixa
    workspace_path = str(project_root)
    lyrixa = LyrixaAI(workspace_path=workspace_path)

    try:
        # Initialize all systems
        await lyrixa.initialize()

        # Initialize Aether Runtime and connect to Lyrixa's ecosystem
        print("\n🔮 Initializing Aether Runtime...")
        aether_runtime = AetherRuntime()

        # Connect Lyrixa's systems to the Aether Runtime
        aether_runtime.register_context(
            memory=getattr(lyrixa, "memory_system", None),
            plugins=getattr(lyrixa, "plugin_manager", None),
            agents=getattr(lyrixa, "agent_system", None),
        )

        # Store runtime reference in lyrixa for chat integration
        lyrixa.aether_runtime = aether_runtime

        print("\n" + "=" * 60)
        print("🎙️ LYRIXA AI ASSISTANT READY")
        print("🔮 AETHER RUNTIME INTEGRATED")
        print("=" * 60)
        print(
            "Type 'help' for assistance, 'status' for system info, or 'quit' to exit."
        )
        print("You can also ask me anything in natural language!")
        print("💡 NEW: Use .aether commands for AI OS operations!")
        print("   Example: 'run this .aether script: goal \"test goal\"'")
        print()

        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("👋 Goodbye! Thanks for using Lyrixa!")
                    break

                elif user_input.lower() == "status":
                    status = await lyrixa.get_system_status()
                    print(f"""
🎙️ **LYRIXA SYSTEM STATUS**
Session: {status["session_id"][:8]}...
Workspace: {status["workspace_path"]}
Conversation Length: {status["conversation_length"]} exchanges

💾 Memory: {status["memory_system"]["total_memories"]} memories
🎯 Goals: {status["goal_system"]["active_goals"]} active, {status["goal_system"]["completed_goals"]} completed
🧩 Plugins: {status["plugin_system"]["loaded_plugins"]} loaded
🤖 Agents: {status["agent_system"].__len__()} specialized agents
⚡ Workflows: {status["aether_interpreter"]["execution_history"]} executed
""")
                    continue

                elif user_input.lower() == "help":
                    print("""
🎙️ **LYRIXA AI ASSISTANT HELP**

I'm your AI assistant for Aetherra development. Here's what I can do:

**Natural Language Commands:**
• "Create a data analysis workflow"
• "Remember that I prefer Python for scripting"
• "Show me my active goals"
• "List the files in my project"
• "Execute a web search for machine learning"
• "Plan a testing workflow for my code"

**System Commands:**
• `status` - Show system status
• `aether status` - Show Aether Runtime status
• `bootstrap` - Run bootstrap.aether script
• `debug` - Show debug console state
• `debug thoughts` - Show recent thought processes
• `debug export` - Export debug session to file
• `debug level <LEVEL>` - Change debug level (MINIMAL, STANDARD, DETAILED, VERBOSE, TRACE)
• `help` - Show this help
• `quit` - Exit Lyrixa

**.aether Commands:**
• "run this .aether script: goal \"my goal\""
• "load .aether file: path/to/script.aether"
• "goal \"summarize today's work\""
• "use plugin \"DailyLogSummarizer\""
• "recall \"recent goals\" → $goals"
• "run agent \"Summarizer\" with $goals"
• "store $result in memory"

**Core Capabilities:**
🎯 Goal & Task Management - Set and track development goals
🧠 Memory System - Remember preferences and context
🧩 Plugin Ecosystem - Execute various tools and integrations
⚡ .aether Workflows - Generate and execute .aether code
🤖 Agent Orchestration - Coordinate specialized AI agents
📁 Project Intelligence - Understand and navigate your codebase

🐛 **Debug Console Features:**
• See what Lyrixa perceives in real-time
• View her reasoning process and decision making
• Understand why she picks specific suggestions
• Export debug sessions for analysis
""")
                    continue

                # Handle debug console commands
                elif user_input.lower().startswith("debug"):
                    parts = user_input.lower().split()

                    if len(parts) == 1:  # Just "debug"
                        debug_state = lyrixa.debug_console.show_current_state()
                        print(f"""
🐛 **DEBUG CONSOLE STATE**
Current cognitive state: {debug_state["cognitive_state"]}
Debug level: {debug_state["debug_level"]}
Recent decisions: {debug_state["recent_decision_count"]}
Average decision time: {debug_state["avg_decision_time"]:.1f}ms
Average confidence: {debug_state["avg_confidence"]:.2f}
""")

                    elif len(parts) >= 2 and parts[1] == "thoughts":
                        analysis = lyrixa.debug_console.get_thought_analysis()
                        if "error" in analysis:
                            print(f"🐛 {analysis['error']}")
                        else:
                            print(f"""
🐛 **LATEST THOUGHT PROCESS**
ID: {analysis["thought_id"]}
Duration: {analysis["execution_time_ms"]:.1f}ms
Reasoning steps: {len(analysis["reasoning_steps"])}

🧠 **Reasoning Process:**""")
                            for i, step in enumerate(analysis["reasoning_steps"], 1):
                                print(f"   {i}. {step}")

                            if analysis["final_decision"]:
                                print(
                                    f"\n✅ Final Decision: {analysis['final_decision']}"
                                )

                    elif len(parts) >= 2 and parts[1] == "export":
                        filepath = lyrixa.debug_console.export_debug_session()
                        print(f"🐛 Debug session exported to: {filepath}")

                    elif len(parts) >= 3 and parts[1] == "level":
                        level_name = parts[2].upper()
                        try:
                            from lyrixa.core.debug_console import DebugLevel

                            level = DebugLevel[level_name]
                            lyrixa.debug_console.toggle_debug_level(level)
                            print(f"🐛 Debug level changed to: {level.name}")
                        except KeyError:
                            print(f"🐛 Invalid debug level: {level_name}")
                            print(
                                "Valid levels: MINIMAL, STANDARD, DETAILED, VERBOSE, TRACE"
                            )

                    else:
                        print("🐛 Debug commands:")
                        print("   debug - Show current state")
                        print("   debug thoughts - Show recent thought processes")
                        print("   debug export - Export session to file")
                        print("   debug level <LEVEL> - Change debug level")

                    continue

                # Check for .aether commands
                if ".aether" in user_input.lower():
                    print("🔮 Detected .aether command...")

                    # Extract .aether script from user input
                    if "run this .aether script:" in user_input.lower():
                        # Extract the script part
                        script_start = user_input.lower().find(
                            "run this .aether script:"
                        ) + len("run this .aether script:")
                        aether_script = user_input[script_start:].strip()

                        print(f"🔮 Executing .aether script: {aether_script}")
                        try:
                            aether_runtime.execute_goal(aether_script)
                        except Exception as e:
                            print(f"❌ .aether execution failed: {e}")
                        continue

                    # Check for individual .aether commands
                    elif any(
                        cmd in user_input
                        for cmd in [
                            "goal ",
                            "use plugin ",
                            "recall ",
                            "run agent ",
                            "store ",
                        ]
                    ):
                        print(f"🔮 Executing .aether instruction: {user_input}")
                        try:
                            success = aether_runtime.interpret_aether_line(user_input)
                            if not success:
                                print(
                                    "💡 Try: 'goal \"my goal\"', 'use plugin \"name\"', 'recall \"query\" → $var'"
                                )
                        except Exception as e:
                            print(f"❌ .aether command failed: {e}")
                        continue

                    # Load .aether file
                    elif "load .aether file:" in user_input.lower():
                        file_start = user_input.lower().find(
                            "load .aether file:"
                        ) + len("load .aether file:")
                        file_path = user_input[file_start:].strip()

                        print(f"📁 Loading .aether file: {file_path}")
                        try:
                            aether_runtime.load_aether_goal(file_path)
                        except Exception as e:
                            print(f"❌ Failed to load .aether file: {e}")
                        continue

                # Special commands for Aether Runtime
                elif user_input.lower() in ["aether status", ".aether status"]:
                    stats = aether_runtime.get_execution_stats()
                    print("🔮 Aether Runtime Status:")
                    print(f"   🎯 Goals completed: {stats['goals_completed']}")
                    print(f"   ❌ Goals failed: {stats['goals_failed']}")
                    print(f"   📝 Variables set: {stats['variables_set']}")
                    print(f"   🎯 Goals defined: {stats['goals_defined']}")
                    print(f"   📋 Queue size: {stats['queue_size']}")
                    continue

                elif user_input.lower() in ["bootstrap", "run bootstrap"]:
                    print("🚀 Running bootstrap.aether...")
                    try:
                        bootstrap_path = project_root / "bootstrap.aether"
                        if bootstrap_path.exists():
                            aether_runtime.load_aether_goal(str(bootstrap_path))
                        else:
                            print("❌ bootstrap.aether file not found")
                    except Exception as e:
                        print(f"❌ Bootstrap failed: {e}")
                    continue

                # Process natural language input
                print("🎙️ Lyrixa: Processing...")
                response = await lyrixa.process_natural_language(user_input)

                print(f"🎙️ Lyrixa: {response['lyrixa_response']}")

                # Show suggestions if available
                if response.get("suggestions"):
                    print(f"\n💡 Suggestions: {', '.join(response['suggestions'][:3])}")

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using Lyrixa!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("I'm still here! Try asking me something else.")
                continue

    except KeyboardInterrupt:
        print("\n👋 Goodbye! Thanks for using Lyrixa!")
    except Exception as e:
        print(f"❌ Failed to start Lyrixa: {e}")
    finally:
        # Cleanup
        try:
            await lyrixa.cleanup()
        except Exception:
            pass


def run_lyrixa():
    """Synchronous wrapper for running Lyrixa"""
    import argparse

    parser = argparse.ArgumentParser(description="🎙️ Lyrixa AI Assistant Launcher")
    parser.add_argument("--gui", action="store_true", help="Launch with GUI interface")
    parser.add_argument("--console", action="store_true", help="Launch in console mode")
    args = parser.parse_args()

    # Default to GUI if available, otherwise console
    if args.gui or (not args.console and GUI_AVAILABLE):
        print("🎙️ Starting Lyrixa AI Assistant with GUI...")
        return run_gui()
    else:
        print("🎙️ Starting Lyrixa AI Assistant in console mode...")
        try:
            if sys.platform == "win32":
                # Windows-specific event loop policy
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Failed to run Lyrixa: {e}")


if __name__ == "__main__":
    run_lyrixa()
