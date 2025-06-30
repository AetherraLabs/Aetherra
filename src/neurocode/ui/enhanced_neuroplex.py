#!/usr/bin/env python3
"""
Enhanced Neuroplex - Integrated NeuroChat Edition
=================================================

Integration of the enhanced NeuroChat interface into the main Neuroplex
development environment, providing a unified AI-native programming experience.

Features:
- Full Neuroplex development environment
- Enhanced NeuroChat with tabs, typing indicators, and modern UI
- Seamless integration between development and AI assistance
- Unified memory and reflection system
"""

import sys
from datetime import datetime
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "core"))

# Qt imports
try:
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
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
except ImportError:
    print("❌ PySide6 not available. Please install PySide6.")
    QT_AVAILABLE = False

# Import NeuroChat components
try:
    from neuro_chat import NeuroChatInterface

    NEUROCHAT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ NeuroChat components not available: {e}")
    NEUROCHAT_AVAILABLE = False

# Import Agent components
try:
    from neuroplex_agent_integration import NeuroplexAgentIntegration, add_agent_to_neuroplex

    from core.enhanced_agent import EnhancedNeuroAgent, create_enhanced_agent

    AGENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Agent components not available: {e}")
    AGENT_AVAILABLE = False

# Import existing Neuroplex components
try:
    from neuroplex_gui_v2 import ModernTheme

    NEUROPLEX_THEME_AVAILABLE = True
except ImportError:
    NEUROPLEX_THEME_AVAILABLE = False


class EnhancedNeuroplexWindow(QMainWindow):
    """Enhanced Neuroplex with integrated NeuroChat interface and Agent system"""

    def __init__(self):
        super().__init__()
        # Initialize agent system
        self.agent = None
        self.agent_integration = None
        self.setup_ui()
        self.init_components()
        self.init_agent_system()

    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle("🧬 Enhanced Neuroplex - AI-Native Development Environment")
        self.setGeometry(100, 100, 1600, 1000)

        # Apply theme if available
        if NEUROPLEX_THEME_AVAILABLE:
            self.setStyleSheet(ModernTheme.get_main_stylesheet())
        else:
            self.setStyleSheet(self.get_fallback_style())

        # Create central widget
        self.create_central_widget()

        # Status bar
        self.statusBar().showMessage(
            "🧬 Enhanced Neuroplex ready - AI-native development at your fingertips!"
        )

    def create_central_widget(self):
        """Create the main central widget with enhanced layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Development tools
        left_panel = self.create_development_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Enhanced AI Assistant (NeuroChat)
        right_panel = self.create_enhanced_chat_panel()
        main_splitter.addWidget(right_panel)

        # Set proportions (60% development, 40% chat)
        main_splitter.setSizes([960, 640])

        main_layout.addWidget(main_splitter)

    def create_development_panel(self):
        """Create the main development panel"""
        dev_widget = QWidget()
        dev_layout = QVBoxLayout(dev_widget)

        # Header
        header = QLabel("🛠️ NeuroCode Development Environment")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dev_layout.addWidget(header)

        # Create tabs for different development views
        self.dev_tabs = QTabWidget()

        # Code Editor tab
        code_tab = self.create_code_editor_tab()
        self.dev_tabs.addTab(code_tab, "📝 Code Editor")

        # Memory & Goals tab
        memory_tab = self.create_memory_goals_tab()
        self.dev_tabs.addTab(memory_tab, "🧠 Memory & Goals")

        # Plugin Manager tab
        plugin_tab = self.create_plugin_manager_tab()
        self.dev_tabs.addTab(plugin_tab, "🔌 Plugin Manager")

        # Performance Monitor tab
        perf_tab = self.create_performance_tab()
        self.dev_tabs.addTab(perf_tab, "📊 Performance")

        # Agent Control tab
        agent_tab = self.create_agent_control_tab()
        self.dev_tabs.addTab(agent_tab, "🤖 Agent Control")

        dev_layout.addWidget(self.dev_tabs)

        return dev_widget

    def create_enhanced_chat_panel(self):
        """Create the enhanced chat panel using NeuroChat components"""
        if NEUROCHAT_AVAILABLE:
            # Use the full NeuroChat interface
            chat_interface = NeuroChatInterface()
            # Remove the window decorations since it's embedded
            chat_interface.setWindowFlags(Qt.WindowType.Widget)
            return chat_interface.centralWidget()
        else:
            # Fallback to basic chat
            return self.create_fallback_chat_panel()

    def create_fallback_chat_panel(self):
        """Create a fallback chat panel if NeuroChat is not available"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # Header
        header = QLabel("🤖 AI Assistant")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chat_layout.addWidget(header)

        # Simple chat area
        chat_display = QTextEdit()
        chat_display.setReadOnly(True)
        chat_display.setPlainText(
            "AI Assistant: Hello! Enhanced NeuroChat components are not available.\nInstall the full NeuroChat module for advanced features."
        )
        chat_layout.addWidget(chat_display)

        # Input area
        input_layout = QHBoxLayout()
        chat_input = QLineEdit()
        chat_input.setPlaceholderText("Ask me anything...")
        send_button = QPushButton("Send")

        input_layout.addWidget(chat_input)
        input_layout.addWidget(send_button)
        chat_layout.addLayout(input_layout)

        return chat_widget

    def create_code_editor_tab(self):
        """Create the code editor tab"""
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        # Code editor
        code_editor = QTextEdit()
        code_editor.setFont(QFont("Consolas", 12))
        code_editor.setPlaceholderText(
            '# Write your NeuroCode here...\n\ngoal: "Build amazing AI-native applications"\n\nremember("This is a powerful development environment") as "dev_env"\n\nassistant: "Help me optimize this code"'
        )

        editor_layout.addWidget(QLabel("💻 NeuroCode Editor"))
        editor_layout.addWidget(code_editor)

        # Toolbar
        toolbar = QHBoxLayout()
        run_btn = QPushButton("▶️ Run")
        save_btn = QPushButton("💾 Save")
        load_btn = QPushButton("📂 Load")

        toolbar.addWidget(run_btn)
        toolbar.addWidget(save_btn)
        toolbar.addWidget(load_btn)
        toolbar.addStretch()

        editor_layout.addLayout(toolbar)

        return editor_widget

    def create_memory_goals_tab(self):
        """Create memory and goals management tab"""
        mg_widget = QWidget()
        mg_layout = QVBoxLayout(mg_widget)

        mg_layout.addWidget(QLabel("🧠 Memory & Goal Management"))

        # Splitter for memory and goals
        mg_splitter = QSplitter(Qt.Orientation.Vertical)

        # Goals section
        goals_widget = QWidget()
        goals_layout = QVBoxLayout(goals_widget)
        goals_layout.addWidget(QLabel("🎯 Active Goals"))

        goals_display = QTextEdit()
        goals_display.setMaximumHeight(200)
        goals_display.setPlainText(
            "• Build enhanced NeuroCode interface\n• Integrate AI assistant capabilities\n• Create seamless development workflow"
        )
        goals_layout.addWidget(goals_display)

        mg_splitter.addWidget(goals_widget)

        # Memory section
        memory_widget = QWidget()
        memory_layout = QVBoxLayout(memory_widget)
        memory_layout.addWidget(QLabel("🗄️ Memory Store"))

        memory_display = QTextEdit()
        memory_display.setPlainText(
            "Recent memories:\n• dev_env: This is a powerful development environment\n• ui_concepts: Modern tabbed interface with enhanced features\n• integration_pattern: Seamless AI-development workflow"
        )
        memory_layout.addWidget(memory_display)

        mg_splitter.addWidget(memory_widget)
        mg_layout.addWidget(mg_splitter)

        return mg_widget

    def create_plugin_manager_tab(self):
        """Create plugin manager tab"""
        plugin_widget = QWidget()
        plugin_layout = QVBoxLayout(plugin_widget)

        plugin_layout.addWidget(QLabel("🔌 Plugin Ecosystem"))

        plugin_info = QTextEdit()
        plugin_info.setPlainText("""Available Plugins:

🧮 Math Plugin
   • Basic calculations and mathematical operations
   • Status: Active

🔍 Demo Plugin  
   • Demonstration and testing capabilities
   • Status: Active
   
📊 Analysis Plugin
   • Code analysis and optimization suggestions
   • Status: Available
   
🌐 Web Plugin
   • Web scraping and API interactions
   • Status: Available
   
Install new plugins or configure existing ones through the AI assistant.""")

        plugin_layout.addWidget(plugin_info)

        return plugin_widget

    def create_performance_tab(self):
        """Create performance monitoring tab"""
        perf_widget = QWidget()
        perf_layout = QVBoxLayout(perf_widget)

        perf_layout.addWidget(QLabel("📊 System Performance"))

        perf_info = QTextEdit()
        perf_info.setPlainText("""System Status:

🚀 Execution Engine: Optimal
⚡ Memory Usage: 45% (Normal)
🔄 Parser Performance: Excellent
🧠 AI Response Time: < 2s
🔌 Plugin Load Time: < 500ms

Recent Activity:
• 15 NeuroCode executions (last hour)
• 8 AI assistant interactions
• 3 memory operations
• 2 plugin invocations

All systems operational and performing within expected parameters.""")

        perf_layout.addWidget(perf_info)

        return perf_widget

    def create_agent_control_tab(self):
        """Create the agent control tab"""
        agent_widget = QWidget()
        layout = QVBoxLayout(agent_widget)

        # Agent Status Section
        status_group = QWidget()
        status_layout = QVBoxLayout(status_group)

        status_label = QLabel("🤖 Agent Status")
        status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(status_label)

        self.agent_status_display = QTextEdit()
        self.agent_status_display.setMaximumHeight(100)
        self.agent_status_display.setReadOnly(True)
        status_layout.addWidget(self.agent_status_display)

        layout.addWidget(status_group)

        # Agent Control Buttons
        controls_group = QWidget()
        controls_layout = QHBoxLayout(controls_group)

        self.start_agent_btn = QPushButton("▶️ Start Agent")
        self.start_agent_btn.clicked.connect(self.on_start_agent)
        controls_layout.addWidget(self.start_agent_btn)

        self.stop_agent_btn = QPushButton("⏹️ Stop Agent")
        self.stop_agent_btn.clicked.connect(self.on_stop_agent)
        controls_layout.addWidget(self.stop_agent_btn)

        self.refresh_status_btn = QPushButton("🔄 Refresh Status")
        self.refresh_status_btn.clicked.connect(self.on_refresh_agent_status)
        controls_layout.addWidget(self.refresh_status_btn)

        layout.addWidget(controls_group)

        # Agent Mode Selection
        mode_group = QWidget()
        mode_layout = QVBoxLayout(mode_group)

        mode_label = QLabel("🎯 Agent Mode")
        mode_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        mode_layout.addWidget(mode_label)

        mode_controls = QHBoxLayout()
        self.mode_input = QLineEdit()
        self.mode_input.setPlaceholderText(
            "Enter agent mode (idle, reflecting, goal_monitoring, etc.)"
        )
        mode_controls.addWidget(self.mode_input)

        self.set_mode_btn = QPushButton("Set Mode")
        self.set_mode_btn.clicked.connect(self.on_set_agent_mode)
        mode_controls.addWidget(self.set_mode_btn)

        mode_layout.addLayout(mode_controls)
        layout.addWidget(mode_group)

        # Agent Goals Section
        goals_group = QWidget()
        goals_layout = QVBoxLayout(goals_group)

        goals_label = QLabel("🎯 Agent Goals")
        goals_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        goals_layout.addWidget(goals_label)

        self.goals_display = QTextEdit()
        self.goals_display.setMaximumHeight(120)
        self.goals_display.setReadOnly(True)
        goals_layout.addWidget(self.goals_display)

        # Add Goal Controls
        add_goal_layout = QHBoxLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Enter new goal for the agent")
        add_goal_layout.addWidget(self.goal_input)

        self.add_goal_btn = QPushButton("Add Goal")
        self.add_goal_btn.clicked.connect(self.on_add_agent_goal)
        add_goal_layout.addWidget(self.add_goal_btn)

        self.clear_goals_btn = QPushButton("Clear Goals")
        self.clear_goals_btn.clicked.connect(self.on_clear_agent_goals)
        add_goal_layout.addWidget(self.clear_goals_btn)

        goals_layout.addLayout(add_goal_layout)
        layout.addWidget(goals_group)

        # Update agent status on tab creation
        self.update_agent_display()

        return agent_widget

    def on_start_agent(self):
        """Handle start agent button click"""
        if hasattr(self, "agent_integration") and self.agent_integration:
            result = self.agent_integration.start_agent()
            self.update_agent_display()
            if result.get("status") == "started":
                self.statusBar().showMessage("🤖 Agent started successfully")
            else:
                self.statusBar().showMessage(
                    f"⚠️ Agent start failed: {result.get('message', 'Unknown error')}"
                )
        else:
            self.statusBar().showMessage("⚠️ Agent system not available")

    def on_stop_agent(self):
        """Handle stop agent button click"""
        if hasattr(self, "agent_integration") and self.agent_integration:
            result = self.agent_integration.stop_agent()
            self.update_agent_display()
            if result.get("status") == "stopped":
                self.statusBar().showMessage("🤖 Agent stopped successfully")
            else:
                self.statusBar().showMessage(
                    f"⚠️ Agent stop failed: {result.get('message', 'Unknown error')}"
                )
        else:
            self.statusBar().showMessage("⚠️ Agent system not available")

    def on_refresh_agent_status(self):
        """Handle refresh agent status button click"""
        self.update_agent_display()
        self.statusBar().showMessage("🔄 Agent status refreshed")

    def on_set_agent_mode(self):
        """Handle set agent mode button click"""
        new_mode = self.mode_input.text().strip()
        if not new_mode:
            self.statusBar().showMessage("⚠️ Please enter a valid agent mode")
            return

        if hasattr(self, "agent") and self.agent:
            try:
                self.agent.set_state(new_mode)
                self.update_agent_display()
                self.statusBar().showMessage(f"🤖 Agent mode set to: {new_mode}")
                self.mode_input.clear()
            except ValueError as e:
                self.statusBar().showMessage(f"⚠️ Invalid agent mode: {e}")
        else:
            self.statusBar().showMessage("⚠️ Agent system not available")

    def on_add_agent_goal(self):
        """Handle add agent goal button click"""
        goal_text = self.goal_input.text().strip()
        if not goal_text:
            self.statusBar().showMessage("⚠️ Please enter a valid goal")
            return

        if hasattr(self, "agent") and self.agent:
            goal_dict = {
                "text": goal_text,
                "priority": "medium",
                "created": datetime.now().isoformat(),
            }
            self.agent.add_goal(goal_dict)
            self.update_agent_display()
            self.statusBar().showMessage(f"🎯 Goal added: {goal_text}")
            self.goal_input.clear()
        else:
            self.statusBar().showMessage("⚠️ Agent system not available")

    def on_clear_agent_goals(self):
        """Handle clear agent goals button click"""
        if hasattr(self, "agent") and self.agent:
            self.agent.set_goals([])
            self.update_agent_display()
            self.statusBar().showMessage("🗑️ Agent goals cleared")
        else:
            self.statusBar().showMessage("⚠️ Agent system not available")

    def update_agent_display(self):
        """Update the agent status and goals display"""
        if not hasattr(self, "agent_status_display"):
            return

        if hasattr(self, "agent") and self.agent:
            # Update status
            status_text = f"State: {self.agent.get_state()}\n"
            status_text += f"Running: {getattr(self.agent, 'is_running', False)}\n"
            status_text += f"Cycles: {getattr(self.agent, 'stats', {}).get('cycles_completed', 0)}"
            self.agent_status_display.setText(status_text)

            # Update goals
            goals = self.agent.get_goals()
            if goals:
                goals_text = "\n".join([f"• {goal.get('text', str(goal))}" for goal in goals])
            else:
                goals_text = "No active goals"
            self.goals_display.setText(goals_text)
        else:
            self.agent_status_display.setText("Agent system not available")
            self.goals_display.setText("Agent system not available")

    def init_agent_system(self):
        """Initialize the agent system"""
        if AGENT_AVAILABLE:
            try:
                # Create and configure the enhanced neuro agent
                self.agent = EnhancedNeuroAgent()
                self.agent_integration = NeuroplexAgentIntegration(self)
                self.agent_integration.set_agent(self.agent)

                # Add agent widgets to the development tabs (handled by create_agent_control_tab)
                print("✅ Agent system initialized")
                print("🤖 Agent ready for autonomous operation")
            except Exception as e:
                print(f"⚠️ Agent system initialization warning: {e}")
                self.agent = None
                self.agent_integration = None

    def get_fallback_style(self):
        """Fallback styling when ModernTheme is not available"""
        return """
        QMainWindow {
            background-color: #f5f5f5;
            color: #333;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e0e0e0;
            padding: 8px 16px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: #2196F3;
            color: white;
        }
        QLabel {
            color: #333;
        }
        QTextEdit {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 8px;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        """


def main():
    """Main entry point for Enhanced Neuroplex"""
    if not QT_AVAILABLE:
        print("❌ Qt not available. Please install PySide6.")
        return 1

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create and show the enhanced interface
    window = EnhancedNeuroplexWindow()
    window.show()

    print("🚀 Enhanced Neuroplex launched successfully!")
    print("💡 Features:")
    print("   • Integrated NeuroChat interface")
    print("   • Unified development environment")
    print("   • AI-native programming workflow")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
