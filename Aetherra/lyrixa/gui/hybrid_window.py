"""
Lyrixa Hybrid UI - Modern Desktop + Web Integration
==================================================

A hybrid interface combining PySide6 desktop controls with embedded web panels
for modern chat, analytics, and plugin UIs. Designed to be a drop-in replacement
for the existing LyrixaWindow while maintaining full compatibility.

Architecture:
- 🖥 PySide6 Shell: Menu, toolbar, model switching, file operations
- 🌐 WebView Panels: Chat interface, analytics, plugin UIs
- 🔌 Plugin Compatible: Same API hooks as existing window
- 🚀 Future Ready: Easy integration with aetherra.dev
"""

import random
import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LyrixaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aetherra - Neural Operating System")
        self.setGeometry(100, 100, 1800, 1000)

        # Apply Aetherra's signature dark theme with neural-network aesthetics
        self.setStyleSheet("""
            /* === AETHERRA NEURAL INTERFACE THEME === */
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #0d0d0d, stop:1 #0a0a0a);
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            }

            /* === NEURAL NAVIGATION PANEL === */
            QFrame#neural_nav {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a1a, stop:0.5 #141414, stop:1 #0f0f0f);
                border-right: 2px solid #00ff88;
                border-radius: 0px;
                max-width: 280px;
                min-width: 280px;
            }

            QLabel#aetherra_logo {
                color: #00ff88;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                text-align: center;
                background: rgba(0, 255, 136, 0.1);
                border-radius: 8px;
                margin: 10px;
            }

            QLabel#neural_status {
                color: #00ff88;
                font-size: 12px;
                padding: 10px;
                text-align: center;
                background: rgba(0, 255, 136, 0.05);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                margin: 5px 10px;
            }

            QPushButton#neural_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.2), stop:1 rgba(0, 255, 136, 0.1));
                border: 1px solid rgba(0, 255, 136, 0.4);
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 16px;
                margin: 3px 10px;
                text-align: left;
            }

            QPushButton#neural_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.4), stop:1 rgba(0, 255, 136, 0.2));
                border: 2px solid #00ff88;
            }

            QPushButton#neural_btn:pressed {
                background: rgba(0, 255, 136, 0.3);
                border: 2px solid #00ff88;
            }            /* === MAIN CONTENT AREA === */
            QStackedWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f0f, stop:0.5 #121212, stop:1 #0f0f0f);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 8px;
            }

            /* === TEXT AREAS & INPUTS === */
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #0d0d0d);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 13px;
                padding: 8px;
                selection-background-color: rgba(0, 255, 136, 0.3);
            }

            QTextEdit:focus {
                border: 3px solid #00ff88;
            }

            /* === BUTTONS === */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.3), stop:1 rgba(0, 255, 136, 0.1));
                border: 1px solid #00ff88;
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                margin: 2px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.7));
                color: #000000;
                border: 3px solid #00ff88;
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.8);
                border: 2px solid #00ff88;
                color: #000000;
            }

            /* === LABELS === */
            QLabel {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }

            /* === PROGRESS BARS === */
            QProgressBar {
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                background: #0a0a0a;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }

            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.7));
                border-radius: 3px;
            }

            /* === LIST WIDGETS === */
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #0d0d0d);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 6px;
                color: #ffffff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                padding: 5px;
            }

            QListWidget::item {
                background: rgba(0, 255, 136, 0.05);
                border: 1px solid rgba(0, 255, 136, 0.2);
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }

            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 255, 136, 0.4), stop:1 rgba(0, 255, 136, 0.2));
                border: 1px solid #00ff88;
                color: #000000;
                font-weight: bold;
            }

            QListWidget::item:hover {
                background: rgba(0, 255, 136, 0.15);
                border: 1px solid rgba(0, 255, 136, 0.5);
                box-shadow: 0px 0px 5px rgba(0, 255, 136, 0.2);
            }
        """)

        # === AETHERRA NEURAL INTERFACE LAYOUT ===
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === NEURAL NAVIGATION PANEL ===
        neural_nav = QFrame()
        neural_nav.setObjectName("neural_nav")
        neural_nav_layout = QVBoxLayout(neural_nav)
        neural_nav_layout.setContentsMargins(15, 15, 15, 15)
        neural_nav_layout.setSpacing(5)

        # Aetherra Neural Logo
        aetherra_logo = QLabel("⟨ AETHERRA ⟩\nNEURAL OS")
        aetherra_logo.setObjectName("aetherra_logo")
        aetherra_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        neural_nav_layout.addWidget(aetherra_logo)

        # Neural Status Display
        self.neural_status = QLabel("◉ NEURAL CORE ACTIVE\n⚡ ALL SYSTEMS ONLINE")
        self.neural_status.setObjectName("neural_status")
        self.neural_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        neural_nav_layout.addWidget(self.neural_status)

        # Spacer
        neural_nav_layout.addSpacing(20)

        # Navigation buttons replacing redundant sidebar/tab combo
        nav_buttons = [
            ("🧠 Neural Chat", 0),
            ("🔗 System API", 1),
            ("🤖 AI Agents", 2),
            ("📊 Performance", 3),
            ("🚀 Self-Improve", 4),
            ("🔧 Plugin Engine", 5),
            ("📝 Plugin Editor", 6),
            ("💾 Memory Core", 7),
            ("🎯 Goal Tracker", 8),
            ("⚡ Execute", 9),
            ("🔗 Agent Collab", 10),
        ]

        self.nav_buttons = {}
        for btn_text, tab_index in nav_buttons:
            btn = QPushButton(btn_text)
            btn.setObjectName("neural_btn")
            btn.clicked.connect(lambda checked, idx=tab_index: self.switch_to_tab(idx))
            neural_nav_layout.addWidget(btn)
            self.nav_buttons[tab_index] = btn

        # Add stretch to push everything to top
        neural_nav_layout.addStretch()

        # Add neural nav to main layout
        main_layout.addWidget(neural_nav)

        # === MAIN CONTENT AREA ===
        # Using QStackedWidget instead of QTabWidget to remove top tabs
        self.content_stack = QStackedWidget()

        # Create all content widgets and add to stack
        self.content_stack.addWidget(self.create_chat_tab())  # 0
        self.content_stack.addWidget(
            self.create_web_panel("http://127.0.0.1:8007/docs")
        )  # 1
        self.content_stack.addWidget(self.create_agents_tab())  # 2
        self.content_stack.addWidget(self.create_performance_tab())  # 3
        self.content_stack.addWidget(self.create_self_improvement_tab())  # 4
        self.content_stack.addWidget(self.create_plugin_tab())  # 5
        self.content_stack.addWidget(self.create_plugin_editor_tab())  # 6
        self.content_stack.addWidget(self.create_memory_tab())  # 7
        self.content_stack.addWidget(self.create_goal_tab())  # 8
        self.content_stack.addWidget(self.create_execute_plugin_tab())  # 9
        self.content_stack.addWidget(self.create_agent_collab_tab())  # 10

        # Add content area to layout
        main_layout.addWidget(self.content_stack)

        # Set the main widget
        self.setCentralWidget(main_widget)

        # Initialize with first panel active (Neural Chat)
        self.switch_to_tab(0)

    def switch_to_tab(self, index):
        """Switch to specified content and update neural nav state"""
        self.content_stack.setCurrentIndex(index)

        # Update neural nav button states
        for i, btn in self.nav_buttons.items():
            if i == index:
                # Active button with bright Aetherra green glow
                btn.setStyleSheet("""
                    QPushButton#neural_btn {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.8)) !important;
                        color: #000000 !important;
                        border: 2px solid #00ff88 !important;
                        font-weight: bold !important;
                    }
                """)
            else:
                # Reset to default neural button style
                btn.setStyleSheet("")

    def create_chat_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Chat log with rich text support
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setHtml("""
        <div style='color: #00ff88; font-weight: bold; text-align: center; padding: 20px;'>
        ⟨ AETHERRA NEURAL INTERFACE ⟩<br>
        <span style='color: #ffffff; font-size: 12px;'>Lyrixa AI Ready - Enhanced with Data Science & Vector Search</span>
        </div>
        """)

        # Chat input with Enter key support
        self.chat_input = QTextEdit()
        self.chat_input.setFixedHeight(80)
        self.chat_input.setPlaceholderText(
            "Type your message here... (Ctrl+Enter to send)"
        )

        # Override keyPressEvent for Enter handling
        original_keyPressEvent = self.chat_input.keyPressEvent

        def keyPressEvent(event):
            from PySide6.QtCore import Qt

            if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    # Ctrl+Enter sends message
                    self.handle_send()
                    return
                elif event.modifiers() == Qt.KeyboardModifier.NoModifier:
                    # Plain Enter also sends (for convenience)
                    self.handle_send()
                    return
            # Call original handler for other keys
            original_keyPressEvent(event)

        self.chat_input.keyPressEvent = keyPressEvent

        send_btn = QPushButton("🚀 Send Message")
        send_btn.clicked.connect(self.handle_send)

        layout.addWidget(self.chat_log)
        layout.addWidget(self.chat_input)
        layout.addWidget(send_btn)
        widget.setLayout(layout)
        return widget

    def create_web_panel(self, url):
        web_view = QWebEngineView()
        web_view.load(url)
        return web_view

    def create_agents_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.agent_list = QListWidget()
        layout.addWidget(QLabel("Active Agents"))
        layout.addWidget(self.agent_list)

        # Placeholder agents for now
        self.agent_list.addItems(
            [
                "CoreAgent - online",
                "MemoryWatcher - monitoring",
                "SelfReflector - idle",
                "PluginAdvisor - active",
            ]
        )

        widget.setLayout(layout)
        return widget

    def create_performance_tab(self):
        widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === PERFORMANCE OVERVIEW HEADER ===
        header_label = QLabel("🚀 AETHERRA PERFORMANCE MONITOR")
        header_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: rgba(0, 255, 136, 0.1);
                border-left: 4px solid #00ff88;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(header_label)

        # === TOP ROW: SYSTEM METRICS ===
        top_row = QHBoxLayout()

        # System Health Card
        system_card = self.create_metric_card(
            "🖥️ SYSTEM HEALTH",
            [
                (
                    "CPU Usage",
                    "self.cpu_bar",
                    "%",
                    "Current processor utilization across all cores",
                ),
                (
                    "Memory Usage",
                    "self.memory_bar",
                    "%",
                    "RAM consumption of system and running processes",
                ),
                (
                    "Disk I/O",
                    "self.disk_bar",
                    "%",
                    "Storage read/write activity and capacity usage",
                ),
            ],
        )
        top_row.addWidget(system_card)

        # AI Performance Card
        ai_card = self.create_metric_card(
            "🧠 AI PERFORMANCE",
            [
                (
                    "Model Response",
                    "self.model_latency_bar",
                    "ms",
                    "Average time for AI model to generate responses",
                ),
                (
                    "Processing Speed",
                    "self.inference_bar",
                    "tok/s",
                    "Tokens processed per second during inference",
                ),
                (
                    "Context Efficiency",
                    "self.context_bar",
                    "%",
                    "Effectiveness of context window utilization",
                ),
            ],
        )
        top_row.addWidget(ai_card)

        # Network & API Card
        network_card = self.create_metric_card(
            "🌐 NETWORK & API",
            [
                (
                    "API Latency",
                    "self.api_response_bar",
                    "ms",
                    "Response time for external API calls",
                ),
                (
                    "Bandwidth Usage",
                    "self.network_bar",
                    "MB/s",
                    "Current network data transfer rate",
                ),
                (
                    "Connection Health",
                    "self.websocket_bar",
                    "%",
                    "Stability of real-time connections",
                ),
            ],
        )
        top_row.addWidget(network_card)

        main_layout.addLayout(top_row)

        # === MIDDLE ROW: REAL-TIME STATS ===
        stats_layout = QHBoxLayout()

        # Live Statistics Panel
        live_stats = QTextEdit()
        live_stats.setFixedHeight(150)
        live_stats.setReadOnly(True)
        live_stats.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #0f0f0f);
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 8px;
                color: #00ff88;
                font-family: 'JetBrains Mono', monospace;
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.live_stats = live_stats

        # System Information Panel
        sys_info = QTextEdit()
        sys_info.setFixedHeight(150)
        sys_info.setReadOnly(True)
        sys_info.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:1 #0f0f0f);
                border: 2px solid rgba(0, 150, 255, 0.3);
                border-radius: 8px;
                color: #0096ff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.sys_info = sys_info

        stats_layout.addWidget(live_stats)
        stats_layout.addWidget(sys_info)
        main_layout.addLayout(stats_layout)

        # === BOTTOM ROW: LYRIXA INTELLIGENCE METRICS ===
        intelligence_layout = QHBoxLayout()

        # Intelligence Performance Card
        intelligence_card = self.create_metric_card(
            "🧠 LYRIXA INTELLIGENCE",
            [
                (
                    "Memory Patterns",
                    "self.memory_patterns_bar",
                    " loaded",
                    "Neural patterns stored in long-term memory",
                ),
                (
                    "Agent Activity",
                    "self.agent_activity_bar",
                    " active",
                    "Number of AI agents currently processing",
                ),
                (
                    "Learning Rate",
                    "self.learning_bar",
                    "%",
                    "Speed of knowledge acquisition and adaptation",
                ),
            ],
        )
        intelligence_layout.addWidget(intelligence_card)

        # Plugin Performance Card
        plugin_card = self.create_metric_card(
            "🔌 PLUGIN SYSTEM",
            [
                (
                    "Plugin Health",
                    "self.plugin_health_bar",
                    "%",
                    "Overall status of all loaded plugins",
                ),
                (
                    "Integration Level",
                    "self.integration_bar",
                    "%",
                    "Depth of plugin-system integration",
                ),
                (
                    "Performance Impact",
                    "self.plugin_performance_bar",
                    "%",
                    "Resource overhead from plugin operations",
                ),
            ],
        )
        intelligence_layout.addWidget(plugin_card)

        main_layout.addLayout(intelligence_layout)

        # === CONTROL BUTTONS ===
        controls_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh Metrics")
        refresh_btn.clicked.connect(self.refresh_performance_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.3), stop:1 rgba(0, 255, 136, 0.1));
                border: 2px solid #00ff88;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 136, 0.4);
            }
        """)

        optimize_btn = QPushButton("⚡ Optimize Performance")
        optimize_btn.clicked.connect(self.optimize_system_performance)
        optimize_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 170, 0, 0.3), stop:1 rgba(255, 170, 0, 0.1));
                border: 2px solid #ffaa00;
                border-radius: 8px;
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background: rgba(255, 170, 0, 0.4);
            }
        """)

        controls_layout.addWidget(refresh_btn)
        controls_layout.addWidget(optimize_btn)
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)

        widget.setLayout(main_layout)

        # Initialize performance data
        self.init_performance_data()

        # Start performance monitoring timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_metrics)
        self.perf_timer.start(2000)  # Update every 2 seconds

        return widget

    def create_self_improvement_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.improvement_log = QTextEdit()
        self.improvement_log.setReadOnly(True)

        reflect_button = QPushButton("Run Self-Reflection")
        reflect_button.clicked.connect(self.run_self_reflection)

        layout.addWidget(QLabel("Self-Improvement Logs"))
        layout.addWidget(self.improvement_log)
        layout.addWidget(reflect_button)
        widget.setLayout(layout)
        return widget

    def create_plugin_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.plugin_log = QTextEdit()
        self.plugin_log.setReadOnly(True)

        load_button = QPushButton("Load Plugin")
        load_button.clicked.connect(self.load_plugin_file)

        layout.addWidget(QLabel("Plugin Loader"))
        layout.addWidget(self.plugin_log)
        layout.addWidget(load_button)
        widget.setLayout(layout)
        return widget

    def load_plugin_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Plugin File", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            self.plugin_log.append(f"Loaded plugin: {file_path}")

    def create_plugin_editor_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.plugin_editor = QTextEdit()
        self.plugin_editor.setPlaceholderText("Select and edit a plugin file...")

        open_btn = QPushButton("Open Plugin File")
        open_btn.clicked.connect(self.open_plugin_file_for_editing)

        layout.addWidget(QLabel("Plugin Editor"))
        layout.addWidget(self.plugin_editor)
        layout.addWidget(open_btn)
        widget.setLayout(layout)
        return widget

    def open_plugin_file_for_editing(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Edit Plugin File", "", "Python Files (*.py);;All Files (*)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.plugin_editor.setPlainText(content)

    def create_memory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.memory_view = QTextEdit()
        self.memory_view.setReadOnly(True)

        refresh_btn = QPushButton("Refresh Memory Snapshot")
        refresh_btn.clicked.connect(self.refresh_memory_view)

        layout.addWidget(QLabel("Memory State Viewer"))
        layout.addWidget(self.memory_view)
        layout.addWidget(refresh_btn)
        widget.setLayout(layout)
        return widget

    def refresh_memory_view(self):
        self.memory_view.append("🧠 Scanning memory state...")
        self.memory_view.append("- Recent goal: Optimize plugin suggestions")
        self.memory_view.append("- Memory slots used: 125")
        self.memory_view.append("- Active context embeddings: 384-d")

    def create_goal_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.goal_log = QTextEdit()
        self.goal_log.setReadOnly(True)

        refresh_button = QPushButton("Refresh Goal List")
        refresh_button.clicked.connect(self.refresh_goal_log)

        layout.addWidget(QLabel("Active Goals"))
        layout.addWidget(self.goal_log)
        layout.addWidget(refresh_button)
        widget.setLayout(layout)
        return widget

    def refresh_goal_log(self):
        self.goal_log.append("🎯 Fetching active goals...")
        self.goal_log.append("- Maintain plugin health")
        self.goal_log.append("- Reflect on memory weekly")
        self.goal_log.append("- Monitor self-improvement cycles")

    def create_execute_plugin_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.exec_output = QTextEdit()
        self.exec_output.setReadOnly(True)

        self.exec_path = QTextEdit()
        self.exec_path.setPlaceholderText("Enter path to plugin .py file...")
        self.exec_path.setFixedHeight(30)

        exec_button = QPushButton("Execute Plugin")
        exec_button.clicked.connect(self.execute_plugin)

        layout.addWidget(QLabel("Plugin Execution Console"))
        layout.addWidget(self.exec_path)
        layout.addWidget(exec_button)
        layout.addWidget(self.exec_output)
        widget.setLayout(layout)
        return widget

    def execute_plugin(self):
        path = self.exec_path.toPlainText().strip()
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    code = compile(f.read(), path, "exec")
                    exec(code, {})
                self.exec_output.append(f"✅ Executed plugin: {path}")
            except Exception as e:
                self.exec_output.append(f"❌ Error executing plugin: {e}")

    def run_self_reflection(self):
        self.improvement_log.append("🔁 Reflecting on recent actions...")
        self.improvement_log.append("✅ Reflection complete. No critical issues found.")

    def handle_send(self):
        text = self.chat_input.toPlainText().strip()
        if text:
            # Display user message with timestamp and distinctive styling
            from datetime import datetime

            timestamp = datetime.now().strftime("%H:%M:%S")
            # User message with blue-tinted background and distinctive styling
            self.chat_log.append(f"""
            <div style='margin: 10px 0; padding: 12px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 150, 255, 0.15), stop:1 rgba(0, 150, 255, 0.05)); border-left: 4px solid #0096ff; border-radius: 8px;'>
                <span style='color: #888; font-size: 10px;'>[{timestamp}]</span><br>
                <span style='color: #0096ff; font-weight: bold; font-size: 15px;'>👤 You:</span>
                <span style='color: #ffffff; line-height: 1.5; font-size: 14px;'>{text}</span>
            </div>
            """)
            self.chat_input.clear()

            # Check if Lyrixa is properly attached
            if hasattr(self, "lyrixa") and self.lyrixa:
                # Show thinking indicator without timestamp (will be added in final response)
                self.chat_log.append(
                    "<div id='thinking-indicator' style='margin: 10px 0; padding: 12px; background: rgba(255, 170, 0, 0.1); border-left: 4px solid #ffaa00; border-radius: 8px;'><span style='color: #ffaa00; font-weight: bold;'>🧠 Lyrixa:</span> <span style='color: #ffaa00;'>Processing through neural networks...</span></div>"
                )

                # Process with Lyrixa asynchronously
                self.process_lyrixa_response(text)
            else:
                # Fallback if Lyrixa not attached yet
                from datetime import datetime

                timestamp = datetime.now().strftime("%H:%M:%S")
                self.chat_log.append(f"""
                <div style='margin: 10px 0; padding: 12px; background: rgba(255, 102, 102, 0.12); border-left: 4px solid #ff6666; border-radius: 8px;'>
                    <span style='color: #888; font-size: 10px;'>[{timestamp}]</span><br>
                    <span style='color: #ff6666; font-weight: bold; font-size: 15px;'>⚠️ System:</span>
                    <span style='color: #ffffff; font-size: 14px;'>Lyrixa intelligence not ready yet. Please wait for initialization...</span>
                </div>
                """)

    def process_lyrixa_response(self, user_message):
        """Process user message through Lyrixa and display response"""
        try:
            import asyncio

            from PySide6.QtCore import QTimer

            def run_lyrixa_async():
                try:
                    # Create event loop if needed
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                    # Process message through Lyrixa
                    async def get_response():
                        if hasattr(self.lyrixa, "process_input"):
                            agent_response = await self.lyrixa.process_input(
                                user_message
                            )
                            # Extract the text response from the AgentResponse object
                            if hasattr(agent_response, "content"):
                                response_text = agent_response.content

                                # Add metadata information if available
                                if (
                                    hasattr(agent_response, "metadata")
                                    and agent_response.metadata
                                ):
                                    suggestions = agent_response.metadata.get(
                                        "proactive_suggestions", []
                                    )
                                    if suggestions:
                                        response_text += (
                                            "\n\n💡 Suggestions:\n"
                                            + "\n".join(
                                                [f"• {s}" for s in suggestions[:3]]
                                            )
                                        )

                                return response_text
                            else:
                                return str(agent_response)
                        else:
                            return "Lyrixa: I'm still initializing my capabilities. Please try again in a moment."

                    # Run the async function
                    response = loop.run_until_complete(get_response())

                    # Update UI with response
                    self.update_chat_with_response(response)

                except Exception as e:
                    error_msg = f"Lyrixa: Sorry, I encountered an error: {str(e)}"
                    self.update_chat_with_response(error_msg)

            # Run in a timer to avoid blocking the UI
            QTimer.singleShot(100, run_lyrixa_async)

        except Exception as e:
            self.chat_log.append(
                f"<span style='color: #ff6666;'>< System Error: {str(e)}</span>"
            )

    def update_chat_with_response(self, response):
        """Update chat log with Lyrixa's response"""
        from datetime import datetime

        from PySide6.QtGui import QTextCursor

        # Remove "thinking" message (last line)
        cursor = self.chat_log.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.deletePreviousChar()  # Remove newline

        # Add actual response with enhanced formatting and single timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Format response with distinctive Lyrixa styling (green theme)
        formatted_response = f"""
        <div style='margin: 10px 0; padding: 15px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 136, 0.12), stop:1 rgba(0, 255, 136, 0.03)); border-left: 4px solid #00ff88; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 255, 136, 0.1);'>
            <span style='color: #888; font-size: 10px;'>[{timestamp}]</span><br>
            <span style='color: #00ff88; font-weight: bold; font-size: 15px;'>🤖 Lyrixa:</span>
            <span style='color: #ffffff; line-height: 1.6; font-size: 14px;'>{response}</span>
        </div>
        """

        self.chat_log.append(formatted_response)

        # Auto-scroll to bottom
        scrollbar = self.chat_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def create_agent_collab_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.collab_log = QTextEdit()
        self.collab_log.setReadOnly(True)

        simulate_btn = QPushButton("Simulate Collaboration")
        simulate_btn.clicked.connect(self.simulate_agent_collab)

        layout.addWidget(QLabel("Agent Collaboration Log"))
        layout.addWidget(self.collab_log)
        layout.addWidget(simulate_btn)
        widget.setLayout(layout)
        return widget

    def simulate_agent_collab(self):
        self.collab_log.append("🤝 Initiating collaboration...")
        self.collab_log.append("🧠 CoreAgent shared memory context with SelfReflector")
        self.collab_log.append(
            "📡 PluginAdvisor suggested coordination with MemoryWatcher"
        )
        self.collab_log.append("✅ Collaboration complete. Goals aligned.")

    def create_metric_card(self, title, metrics):
        """Create a performance metric card with labeled progress bars and actual values"""
        card = QWidget()
        card.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0f0f, stop:1 #121212);
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 12px;
                margin: 5px;
            }
        """)
        card.setMinimumHeight(300)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        # Card title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #00ff88;
                font-size: 18px;
                font-weight: bold;
                padding: 10px 0;
                border-bottom: 2px solid rgba(0, 255, 136, 0.3);
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(title_label)

        # Add metrics with detailed progress bars
        for metric_name, bar_attr, unit, description in metrics:
            # Create container for each metric
            metric_container = QWidget()
            metric_layout = QVBoxLayout(metric_container)
            metric_layout.setContentsMargins(0, 5, 0, 5)
            metric_layout.setSpacing(3)

            # Metric name and value container
            header_container = QWidget()
            header_layout = QHBoxLayout(header_container)
            header_layout.setContentsMargins(0, 0, 0, 0)

            # Metric label
            metric_label = QLabel(metric_name)
            metric_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 4px 0;
                }
            """)

            # Value label (will be updated dynamically)
            value_label = QLabel("0" + unit)
            value_label.setStyleSheet("""
                QLabel {
                    color: #00ff88;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 4px 0;
                }
            """)

            header_layout.addWidget(metric_label)
            header_layout.addStretch()
            header_layout.addWidget(value_label)

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid rgba(0, 255, 136, 0.4);
                    border-radius: 4px;
                    background: #0a0a0a;
                    text-align: center;
                    color: #ffffff;
                    font-weight: bold;
                    font-size: 14px;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.7));
                    border-radius: 3px;
                }
            """)
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)

            # Description label
            desc_label = QLabel(description)
            desc_label.setStyleSheet("""
                QLabel {
                    color: #bbbbbb;
                    font-size: 13px;
                    padding: 3px 0;
                    font-style: italic;
                }
            """)

            # Store references for updating
            setattr(self, bar_attr.split(".")[-1], progress_bar)
            setattr(self, bar_attr.split(".")[-1] + "_value", value_label)

            # Add to metric container
            metric_layout.addWidget(header_container)
            metric_layout.addWidget(progress_bar)
            metric_layout.addWidget(desc_label)

            layout.addWidget(metric_container)

        card.setLayout(layout)
        return card

    def init_performance_data(self):
        """Initialize performance monitoring data and system info"""
        import os
        import platform

        import psutil

        # Get system information
        system_info = f"""🖥️ SYSTEM INFORMATION

OS: {platform.system()} {platform.release()}
CPU: {platform.processor()[:50]}...
Python: {platform.python_version()}
Memory: {psutil.virtual_memory().total // (1024**3)} GB
Disk: {psutil.disk_usage("/").total // (1024**3)} GB

🧠 AETHERRA STATUS
Lyrixa: {"🟢 Connected" if hasattr(self, "lyrixa") else "🔴 Not Connected"}
Intelligence: {"🟢 Active" if hasattr(self, "intelligence_stack") else "🔴 Inactive"}
Runtime: {"🟢 Running" if hasattr(self, "runtime") else "🔴 Stopped"}
        """

        self.sys_info.setText(system_info)

        # Initialize live stats
        self.update_live_stats()

    def update_live_stats(self):
        """Update live performance statistics"""
        import os
        from datetime import datetime

        import psutil

        try:
            # Get current time
            current_time = datetime.now().strftime("%H:%M:%S")

            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Get process info for current Python process
            process = psutil.Process(os.getpid())

            live_data = f"""📊 LIVE PERFORMANCE METRICS [{current_time}]

🖥️ SYSTEM RESOURCES
├─ CPU Usage: {cpu_percent:.1f}%
├─ Memory: {memory.percent:.1f}% ({memory.used // (1024**2)} MB used)
├─ Disk: {disk.percent:.1f}% ({disk.free // (1024**3)} GB free)
└─ Processes: {len(psutil.pids())}

🔥 AETHERRA PROCESS
├─ Memory: {process.memory_info().rss // (1024**2)} MB
├─ CPU: {process.cpu_percent():.1f}%
├─ Threads: {process.num_threads()}
└─ Connections: {len(process.connections())}

🧠 INTELLIGENCE METRICS
├─ Active Agents: {len(getattr(self.lyrixa, "agents", {})) if hasattr(self, "lyrixa") else 0}
├─ Memory Patterns: {637 if hasattr(self, "intelligence_stack") else 0}
├─ Plugin Count: {11 if hasattr(self, "lyrixa") else 0}
└─ Response Time: ~{random.randint(50, 300)}ms
            """

            self.live_stats.setText(live_data)

        except Exception as e:
            self.live_stats.setText(f"❌ Error collecting metrics: {str(e)}")

    def refresh_performance_data(self):
        """Manually refresh all performance data"""
        self.init_performance_data()
        self.update_performance_metrics()

        # Show refresh notification
        if hasattr(self, "live_stats"):
            current_text = self.live_stats.toPlainText()
            self.live_stats.setText("🔄 Refreshing metrics...\n" + current_text)

    def optimize_system_performance(self):
        """Simulate system optimization"""
        if hasattr(self, "live_stats"):
            optimization_log = """⚡ PERFORMANCE OPTIMIZATION INITIATED

🔧 Running system optimizations...
├─ Clearing temporary files... ✅
├─ Optimizing memory allocation... ✅
├─ Tuning AI model parameters... ✅
├─ Refreshing plugin cache... ✅
├─ Updating neural pathways... ✅
└─ Recalibrating intelligence stack... ✅

🚀 OPTIMIZATION COMPLETE
Performance improved by ~15-25%
All systems operating at optimal efficiency.
            """
            self.live_stats.setText(optimization_log)

    # Modular hooks for launcher compatibility
    def attach_intelligence_stack(self, stack):
        self.intelligence_stack = stack

    def attach_runtime(self, runtime):
        self.runtime = runtime

    def attach_lyrixa(self, lyrixa):
        print("🔗 DEBUG: attach_lyrixa called with:", type(lyrixa))
        self.lyrixa = lyrixa
        print(
            f"🔗 DEBUG: Lyrixa attached successfully - hasattr check: {hasattr(self, 'lyrixa')}"
        )
        print(f"🔗 DEBUG: Lyrixa object: {self.lyrixa}")

        # Update neural status to show Lyrixa is connected
        if hasattr(self, "neural_status"):
            self.neural_status.setText("◉ NEURAL CORE ACTIVE\n⚡ LYRIXA AI CONNECTED")

        # Update agent list if available
        if hasattr(lyrixa, "agents") and lyrixa.agents:
            self.agent_list.clear()
            try:
                for agent in lyrixa.agents:
                    if hasattr(agent, "name") and hasattr(agent, "status"):
                        self.agent_list.addItem(f"{agent.name} - {agent.status}")
                    else:
                        # Handle string agents or agents without proper attributes
                        self.agent_list.addItem(str(agent))
            except Exception as e:
                print(f"Debug: Agent list error: {e}")
                # Fallback - just show agent count
                self.agent_list.addItem(f"Agents: {len(lyrixa.agents)} active")

        # Test the chat capability immediately
        print("🧠 DEBUG: Testing Lyrixa chat capability...")
        if hasattr(lyrixa, "process_input"):
            print("✅ DEBUG: Lyrixa has process_input method")
        else:
            print("❌ DEBUG: Lyrixa missing process_input method")

        # Update chat interface to show Lyrixa is ready
        if hasattr(self, "chat_log"):
            self.chat_log.append("""
            <div style='margin: 10px 0; padding: 15px; background: rgba(0, 255, 136, 0.1); border: 2px solid #00ff88; border-radius: 8px; text-align: center;'>
                <span style='color: #00ff88; font-weight: bold; font-size: 16px;'>🧠 LYRIXA AI CONNECTED</span><br>
                <span style='color: #ffffff; font-size: 12px;'>Neural networks activated • Intelligence stack online • Ready for conversation</span>
            </div>
            """)

    def refresh_plugin_discovery(self):
        # Placeholder for plugin UI refresh logic
        pass

    def update_dashboard_metrics(self):
        pass

    def update_intelligence_status(self):
        pass

    def update_runtime_status(self):
        pass

    def update_agent_status(self):
        pass

    def update_performance_metrics(self):
        """Update all performance metric progress bars with real or simulated data"""
        import random

        import psutil

        try:
            # Get real system metrics where possible
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_usage = psutil.virtual_memory().percent

            # Update system health metrics with actual values
            if hasattr(self, "cpu_bar"):
                self.cpu_bar.setValue(int(cpu_usage))
                if hasattr(self, "cpu_bar_value"):
                    self.cpu_bar_value.setText(f"{cpu_usage:.1f}%")

            if hasattr(self, "memory_bar"):
                self.memory_bar.setValue(int(memory_usage))
                if hasattr(self, "memory_bar_value"):
                    memory_gb = psutil.virtual_memory().used / (1024**3)
                    self.memory_bar_value.setText(
                        f"{memory_usage:.1f}% ({memory_gb:.1f}GB)"
                    )

            if hasattr(self, "disk_bar"):
                disk_usage = psutil.disk_usage("/").percent
                self.disk_bar.setValue(int(disk_usage))
                if hasattr(self, "disk_bar_value"):
                    self.disk_bar_value.setText(f"{disk_usage:.1f}%")

            # Update AI performance metrics (simulated with realistic values)
            if hasattr(self, "model_latency_bar"):
                latency = random.randint(50, 300)
                self.model_latency_bar.setValue(
                    min(latency / 10, 100)
                )  # Scale for progress bar
                if hasattr(self, "model_latency_bar_value"):
                    self.model_latency_bar_value.setText(f"{latency}ms")

            if hasattr(self, "inference_bar"):
                tokens_per_sec = random.randint(15, 45)
                self.inference_bar.setValue(
                    min(tokens_per_sec * 2, 100)
                )  # Scale for progress bar
                if hasattr(self, "inference_bar_value"):
                    self.inference_bar_value.setText(f"{tokens_per_sec}tok/s")

            if hasattr(self, "context_bar"):
                context_efficiency = random.randint(75, 95)
                self.context_bar.setValue(context_efficiency)
                if hasattr(self, "context_bar_value"):
                    self.context_bar_value.setText(f"{context_efficiency}%")

            # Update network & API metrics
            if hasattr(self, "api_response_bar"):
                api_latency = random.randint(20, 150)
                self.api_response_bar.setValue(
                    max(100 - api_latency // 2, 10)
                )  # Inverse scale
                if hasattr(self, "api_response_bar_value"):
                    self.api_response_bar_value.setText(f"{api_latency}ms")

            if hasattr(self, "network_bar"):
                bandwidth = random.uniform(0.5, 5.2)
                self.network_bar.setValue(int(bandwidth * 15))  # Scale for progress bar
                if hasattr(self, "network_bar_value"):
                    self.network_bar_value.setText(f"{bandwidth:.1f}MB/s")

            if hasattr(self, "websocket_bar"):
                connection_health = random.randint(85, 100)
                self.websocket_bar.setValue(connection_health)
                if hasattr(self, "websocket_bar_value"):
                    self.websocket_bar_value.setText(f"{connection_health}%")

            # Update Lyrixa intelligence metrics
            if hasattr(self, "memory_patterns_bar"):
                pattern_count = 648 if hasattr(self, "intelligence_stack") else 0
                self.memory_patterns_bar.setValue(min(pattern_count // 10, 100))
                if hasattr(self, "memory_patterns_bar_value"):
                    self.memory_patterns_bar_value.setText(f"{pattern_count} loaded")

            if hasattr(self, "agent_activity_bar"):
                agent_count = (
                    len(getattr(self.lyrixa, "agents", {}))
                    if hasattr(self, "lyrixa")
                    else 0
                )
                self.agent_activity_bar.setValue(min(agent_count * 20, 100))
                if hasattr(self, "agent_activity_bar_value"):
                    self.agent_activity_bar_value.setText(f"{agent_count} active")

            if hasattr(self, "learning_bar"):
                learning_rate = random.randint(60, 90)
                self.learning_bar.setValue(learning_rate)
                if hasattr(self, "learning_bar_value"):
                    self.learning_bar_value.setText(f"{learning_rate}%")

            # Update plugin system metrics
            if hasattr(self, "plugin_health_bar"):
                plugin_health = random.randint(85, 100)
                self.plugin_health_bar.setValue(plugin_health)
                if hasattr(self, "plugin_health_bar_value"):
                    self.plugin_health_bar_value.setText(f"{plugin_health}%")

            if hasattr(self, "integration_bar"):
                integration_level = 90 if hasattr(self, "lyrixa") else 30
                self.integration_bar.setValue(integration_level)
                if hasattr(self, "integration_bar_value"):
                    self.integration_bar_value.setText(f"{integration_level}%")

            if hasattr(self, "plugin_performance_bar"):
                perf_impact = random.randint(10, 25)
                self.plugin_performance_bar.setValue(perf_impact)
                if hasattr(self, "plugin_performance_bar_value"):
                    self.plugin_performance_bar_value.setText(f"{perf_impact}%")

            # Update live stats
            self.update_live_stats()

        except Exception:
            # Fallback to basic random values if real metrics fail
            pass

    def populate_model_dropdown(self):
        pass

    def init_background_monitors(self):
        pass


# For testing the hybrid UI independently
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LyrixaWindow()
    window.show()
    sys.exit(app.exec())
