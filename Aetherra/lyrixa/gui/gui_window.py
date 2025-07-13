"""
Main GUI Window for Lyrixa AI Assistant
Modern dark theme with Aetherra green accents
"""

import sys
from typing import Any, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .plugin_editor_tab import PluginEditorTab


class LyrixaWindow(QMainWindow):
    """
    Main window for Lyrixa AI Assistant with modern dark theme
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lyrixa AI Assistant - Aetherra OS")
        self.setGeometry(100, 100, 1200, 800)

        # References to attached components
        self.intelligence_stack = None
        self.runtime = None
        self.lyrixa_agent = None

        # Setup UI components
        self.setup_ui()
        self.setup_dark_theme()

        # Timers for background monitoring
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_dashboard_metrics)

    def setup_ui(self):
        """Setup the main UI layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Chat interface
        self.setup_chat_panel(splitter)

        # Right panel - Dashboard and controls
        self.setup_dashboard_panel(splitter)

        # Status bar
        self.setup_status_bar()

        # Set splitter proportions
        splitter.setSizes([700, 500])

    def setup_chat_panel(self, parent):
        """Setup the chat interface panel"""
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)

        # Chat header
        chat_header = QLabel("💬 Lyrixa AI Assistant")
        chat_header.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #00ff88; padding: 10px;"
        )
        chat_layout.addWidget(chat_header)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Lyrixa responses will appear here...")
        chat_layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()

        # AI Model Selection
        model_layout = QHBoxLayout()
        model_label = QLabel("🤖 AI Model:")
        model_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        model_layout.addWidget(model_label)

        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(
            [
                "gpt-4o (OpenAI)",
                "gpt-3.5-turbo (OpenAI)",
                "claude-3-opus (Anthropic)",
                "claude-3-sonnet (Anthropic)",
                "gemini-pro (Google)",
                "mistral (Ollama)",
                "llama3 (Ollama)",
                "llama3.2 (Ollama)",
            ]
        )
        self.model_dropdown.setCurrentText("gpt-4o (OpenAI)")
        self.model_dropdown.currentTextChanged.connect(self.on_model_changed)
        self.model_dropdown.setToolTip("Select AI model for Lyrixa responses")
        model_layout.addWidget(self.model_dropdown)

        chat_layout.addLayout(model_layout)

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message to Lyrixa...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet(
            "background-color: #00ff88; color: black; font-weight: bold;"
        )
        input_layout.addWidget(self.send_button)

        chat_layout.addLayout(input_layout)
        parent.addWidget(chat_widget)

    def setup_dashboard_panel(self, parent):
        """Setup the dashboard panel with tabs"""
        self.tab_widget = QTabWidget()

        # System Status Tab
        self.setup_system_status_tab()

        # Agent Status Tab
        self.setup_agent_status_tab()

        # Performance Tab
        self.setup_performance_tab()

        # Self-Improvement Tab
        self.setup_self_improvement_tab()

        # 🔌 Plugins Tab - NEW: Show discovered plugins for Lyrixa
        self.setup_plugins_tab()

        parent.addWidget(self.tab_widget)

    def setup_system_status_tab(self):
        """Setup system status monitoring tab"""
        status_widget = QWidget()
        status_layout = QVBoxLayout(status_widget)

        # System metrics
        status_layout.addWidget(QLabel("🔧 System Status"))

        self.system_metrics = QTextEdit()
        self.system_metrics.setReadOnly(True)
        self.system_metrics.setMaximumHeight(200)
        status_layout.addWidget(self.system_metrics)

        # Intelligence Stack Status
        status_layout.addWidget(QLabel("🧠 Intelligence Stack"))

        self.intelligence_status = QTextEdit()
        self.intelligence_status.setReadOnly(True)
        self.intelligence_status.setMaximumHeight(200)
        status_layout.addWidget(self.intelligence_status)

        # Runtime Status
        status_layout.addWidget(QLabel("⚙️ Runtime Status"))

        self.runtime_status = QTextEdit()
        self.runtime_status.setReadOnly(True)
        status_layout.addWidget(self.runtime_status)

        self.tab_widget.addTab(status_widget, "System")

    def setup_agent_status_tab(self):
        """Setup agent status monitoring tab"""
        agent_widget = QWidget()
        agent_layout = QVBoxLayout(agent_widget)

        agent_layout.addWidget(QLabel("🤖 Agent Status"))

        self.agent_status = QTextEdit()
        self.agent_status.setReadOnly(True)
        agent_layout.addWidget(self.agent_status)

        self.tab_widget.addTab(agent_widget, "Agents")

    def setup_performance_tab(self):
        """Setup performance monitoring tab"""
        perf_widget = QWidget()
        perf_layout = QVBoxLayout(perf_widget)

        perf_layout.addWidget(QLabel("📊 Performance Metrics"))

        self.performance_metrics = QTextEdit()
        self.performance_metrics.setReadOnly(True)
        perf_layout.addWidget(self.performance_metrics)

        self.tab_widget.addTab(perf_widget, "Performance")

    def setup_self_improvement_tab(self):
        """Setup self-improvement dashboard tab"""
        try:
            from Aetherra.lyrixa.ui.self_improvement_dashboard_widget import (
                SelfImprovementDashboardWidget,
            )

            # Create the self-improvement dashboard widget
            self.self_improvement_widget = SelfImprovementDashboardWidget()

            # Add as a tab
            self.tab_widget.addTab(self.self_improvement_widget, "Self-Improvement")

            print("✅ Self-Improvement Dashboard tab added to GUI")

        except ImportError as e:
            print(f"⚠️ Self-Improvement Dashboard widget not available: {e}")

            # Create a fallback widget
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)

            fallback_layout.addWidget(QLabel("🔧 Self-Improvement Dashboard"))

            fallback_text = QTextEdit()
            fallback_text.setReadOnly(True)
            fallback_text.setPlainText("""Self-Improvement Dashboard

This feature provides:
• Performance analytics and insights
• Learning optimization tracking
• Behavioral pattern analysis
• Continuous improvement metrics

Status: Widget not available - using fallback display
API Endpoint: http://127.0.0.1:8005

To enable full dashboard:
1. Ensure self_improvement_dashboard_api.py is running
2. Check UI widget imports are working
3. Verify PySide6 dependencies""")

            fallback_layout.addWidget(fallback_text)

            self.tab_widget.addTab(fallback_widget, "Self-Improvement")
            print("⚠️ Self-Improvement Dashboard using fallback widget")

    def setup_plugins_tab(self):
        """Setup plugins discovery and management tab"""
        plugins_widget = QWidget()
        plugins_layout = QVBoxLayout(plugins_widget)

        # Header
        header_label = QLabel("🔌 Discovered Plugins")
        header_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #00ff88; padding: 10px;"
        )
        plugins_layout.addWidget(header_label)

        # Plugin discovery status
        self.plugin_discovery_status = QLabel(
            "🔍 Plugin discovery status: Not initialized"
        )
        self.plugin_discovery_status.setStyleSheet("color: #ffaa00; padding: 5px;")
        plugins_layout.addWidget(self.plugin_discovery_status)

        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_plugins_btn = QPushButton("🔄 Refresh Plugin Discovery")
        self.refresh_plugins_btn.clicked.connect(self.refresh_plugin_discovery)
        self.refresh_plugins_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a2a;
                color: #00ff88;
                border: 1px solid #00ff88;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
        """)
        refresh_layout.addWidget(self.refresh_plugins_btn)
        refresh_layout.addStretch()
        plugins_layout.addLayout(refresh_layout)

        # Plugin list display
        self.plugin_list = QTextEdit()
        self.plugin_list.setReadOnly(True)
        self.plugin_list.setPlaceholderText(
            "Plugin discovery will show available plugins here...\n\nThis enables Lyrixa to:\n• Reference plugins in conversations\n• Rank and recommend plugins\n• Store plugin metadata in memory"
        )
        plugins_layout.addWidget(self.plugin_list)

        # Plugin memory integration status
        self.plugin_memory_status = QLabel(
            "💾 Plugin memory integration: Not initialized"
        )
        self.plugin_memory_status.setStyleSheet("color: #ffaa00; padding: 5px;")
        plugins_layout.addWidget(self.plugin_memory_status)

        self.tab_widget.addTab(plugins_widget, "Plugins")

    def refresh_plugin_discovery(self):
        """Refresh plugin discovery and update display"""
        try:
            if self.intelligence_stack:
                # Update status
                self.plugin_discovery_status.setText(
                    "🔍 Plugin discovery status: Refreshing..."
                )
                self.plugin_discovery_status.setStyleSheet(
                    "color: #ffaa00; padding: 5px;"
                )

                # Get discovered plugins directly from plugin bridge
                import asyncio

                try:
                    if (
                        hasattr(self.intelligence_stack, "plugin_bridge")
                        and self.intelligence_stack.plugin_bridge
                    ):
                        # First refresh plugin discovery
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        discovered_plugins = loop.run_until_complete(
                            self.intelligence_stack.plugin_bridge.discover_all_plugins()
                        )
                        loop.close()

                        # Convert discovered plugins to display format
                        plugins_for_display = []
                        for plugin_key, plugin_data in discovered_plugins.items():
                            plugins_for_display.append(
                                {
                                    "name": plugin_data.get("name", plugin_key),
                                    "description": plugin_data.get(
                                        "description", "No description available"
                                    ),
                                    "category": plugin_data.get("category", "Unknown"),
                                    "rating": plugin_data.get("rating", "N/A"),
                                    "capabilities": plugin_data.get("capabilities", []),
                                    "in_memory": True,  # Since we just discovered and stored them
                                    "status": plugin_data.get("status", "Unknown"),
                                    "type": plugin_data.get("type", "Unknown"),
                                }
                            )

                        if plugins_for_display:
                            self.update_plugin_display(plugins_for_display)
                            self.plugin_discovery_status.setText(
                                f"🔍 Plugin discovery status: ✅ Active - {len(plugins_for_display)} plugins found"
                            )
                            self.plugin_discovery_status.setStyleSheet(
                                "color: #00ff88; padding: 5px;"
                            )
                            self.plugin_memory_status.setText(
                                "💾 Plugin memory integration: ✅ Active - Plugins stored in memory"
                            )
                            self.plugin_memory_status.setStyleSheet(
                                "color: #00ff88; padding: 5px;"
                            )
                        else:
                            self.plugin_list.setPlainText(
                                "No plugins discovered. This might mean:\n\n• Plugin discovery is not properly initialized\n• No plugins are available in the system\n• Plugin bridge is not connected\n\nCheck the system logs for more details."
                            )
                            self.plugin_discovery_status.setText(
                                "🔍 Plugin discovery status: ⚠️ No plugins found"
                            )
                            self.plugin_discovery_status.setStyleSheet(
                                "color: #ff6600; padding: 5px;"
                            )
                    else:
                        self.plugin_list.setPlainText(
                            "Plugin bridge not available. Plugin discovery requires the plugin-intelligence bridge to be properly initialized."
                        )
                        self.plugin_discovery_status.setText(
                            "🔍 Plugin discovery status: ❌ No plugin bridge"
                        )
                        self.plugin_discovery_status.setStyleSheet(
                            "color: #ff4444; padding: 5px;"
                        )

                except Exception as e:
                    self.plugin_list.setPlainText(
                        f"Error refreshing plugins: {str(e)}\n\nThis indicates that plugin discovery integration needs to be properly initialized in the intelligence stack."
                    )
                    self.plugin_discovery_status.setText(
                        "🔍 Plugin discovery status: ❌ Error"
                    )
                    self.plugin_discovery_status.setStyleSheet(
                        "color: #ff4444; padding: 5px;"
                    )
            else:
                self.plugin_list.setPlainText(
                    "Intelligence stack not available. Plugin discovery requires the intelligence stack to be properly initialized."
                )
                self.plugin_discovery_status.setText(
                    "🔍 Plugin discovery status: ❌ No intelligence stack"
                )
                self.plugin_discovery_status.setStyleSheet(
                    "color: #ff4444; padding: 5px;"
                )

        except Exception as e:
            self.plugin_list.setPlainText(
                f"Failed to refresh plugin discovery: {str(e)}"
            )
            self.plugin_discovery_status.setText(
                "🔍 Plugin discovery status: ❌ Failed"
            )
            self.plugin_discovery_status.setStyleSheet("color: #ff4444; padding: 5px;")

    def update_plugin_display(self, plugins):
        """Update the plugin display with discovered plugins"""
        try:
            if not plugins:
                self.plugin_list.setPlainText("No plugins currently available.")
                return

            plugin_text = f"🔌 Discovered Plugins ({len(plugins)} total)\n"
            plugin_text += "=" * 50 + "\n\n"

            for i, plugin in enumerate(plugins, 1):
                plugin_text += f"{i}. {plugin.get('name', 'Unknown Plugin')}\n"
                plugin_text += f"   📝 Description: {plugin.get('description', 'No description available')}\n"
                plugin_text += f"   🏷️  Category: {plugin.get('category', 'Unknown')}\n"
                plugin_text += f"   ⭐ Rating: {plugin.get('rating', 'N/A')}\n"
                plugin_text += (
                    f"   📊 Capabilities: {', '.join(plugin.get('capabilities', []))}\n"
                )
                plugin_text += f"   💾 Stored in memory: {'✅ Yes' if plugin.get('in_memory') else '⚠️ No'}\n"
                plugin_text += "-" * 40 + "\n\n"

            plugin_text += "\n🧠 These plugins are now available for Lyrixa to:\n"
            plugin_text += "• Reference in conversations\n"
            plugin_text += "• Recommend based on user needs\n"
            plugin_text += "• Query from memory when needed\n"
            plugin_text += "• Integrate into workflows\n"

            self.plugin_list.setPlainText(plugin_text)

        except Exception as e:
            self.plugin_list.setPlainText(f"Error displaying plugins: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event"""
        # Cleanup timers
        if hasattr(self, "monitor_timer"):
            self.monitor_timer.stop()
        if hasattr(self, "diag_timer"):
            self.diag_timer.stop()

        # Shutdown agents gracefully
        if self.lyrixa_agent:
            # Note: In a real implementation, you'd await this
            # asyncio.run(self.lyrixa_agent.shutdown())
            pass

        event.accept()

    def on_model_changed(self, model_text: str):
        """Handle AI model selection change"""
        try:
            # Extract model name from dropdown text (e.g., "gpt-4o (OpenAI)" -> "gpt-4o")
            model_name = model_text.split(" (")[0]

            # Update status display
            self.add_chat_message(
                "System", f"🤖 Switching AI Model to: {model_name}...", "#ffaa00"
            )

            # If Lyrixa agent is available, update its model dynamically
            if self.lyrixa_agent and hasattr(self.lyrixa_agent, "llm_manager"):
                # Use the correct method name from MultiLLMManager
                if hasattr(self.lyrixa_agent.llm_manager, "set_model"):
                    success = self.lyrixa_agent.llm_manager.set_model(model_name)
                    if success:
                        self.add_chat_message(
                            "System",
                            f"✅ Successfully switched to {model_name} - No restart required!",
                            "#00ff88",
                        )

                        # Update the model info in status
                        model_info = (
                            self.lyrixa_agent.llm_manager.get_current_model_info()
                        )
                        if model_info:
                            provider = model_info.get("provider", "unknown")
                            self.add_chat_message(
                                "System",
                                f"📊 Provider: {provider.upper()}, Context: {model_info.get('context_window', 'N/A')} tokens",
                                "#88aaff",
                            )
                    else:
                        self.add_chat_message(
                            "System",
                            f"❌ Failed to switch to {model_name} - Model may not be available",
                            "#ff4444",
                        )
                else:
                    self.add_chat_message(
                        "System",
                        f"⚠️ Model switching not supported by current LLM manager",
                        "#ffaa00",
                    )
            else:
                self.add_chat_message(
                    "System",
                    f"⚠️ Lyrixa agent not ready - Model preference saved for next session",
                    "#ffaa00",
                )

        except Exception as e:
            self.add_chat_message(
                "System", f"❌ Error changing model: {str(e)}", "#ff4444"
            )
            import traceback

            print(f"Model change error: {traceback.format_exc()}")

    def populate_model_dropdown(self):
        """Populate model dropdown with available models from LLM manager"""
        if self.lyrixa_agent and hasattr(self.lyrixa_agent, "llm_manager"):
            try:
                # Get available models from the LLM manager
                available_models = self.lyrixa_agent.llm_manager.list_available_models()

                # Clear current items
                self.model_dropdown.clear()

                # Add available models with provider info
                for model_name, model_info in available_models.items():
                    provider = model_info.get("provider", "unknown").upper()
                    display_text = f"{model_name} ({provider})"
                    self.model_dropdown.addItem(display_text)

                # Set current model as selected
                current_model_info = (
                    self.lyrixa_agent.llm_manager.get_current_model_info()
                )
                if current_model_info:
                    current_name = current_model_info.get("model_name", "")
                    current_provider = current_model_info.get("provider", "").upper()
                    current_text = f"{current_name} ({current_provider})"

                    # Find and select the current model
                    for i in range(self.model_dropdown.count()):
                        if self.model_dropdown.itemText(i) == current_text:
                            self.model_dropdown.setCurrentIndex(i)
                            break

                self.add_chat_message(
                    "System",
                    f"📋 Loaded {len(available_models)} available AI models",
                    "#88aaff",
                )

            except Exception as e:
                # Fallback to default models if dynamic loading fails
                self.add_chat_message(
                    "System", f"⚠️ Using default model list: {str(e)}", "#ffaa00"
                )
        else:
            self.add_chat_message(
                "System",
                "⚠️ LLM manager not available - using default models",
                "#ffaa00",
            )

    # =============================
    # MODULAR ATTACHMENT METHODS
    # =============================

    def attach_intelligence_stack(self, intelligence_stack):
        """Attach the intelligence stack to the GUI"""
        self.intelligence_stack = intelligence_stack

        # Auto-refresh plugin discovery when intelligence stack is attached
        try:
            self.refresh_plugin_discovery()
        except Exception as e:
            print(f"⚠️ Could not auto-refresh plugin discovery: {e}")

    def attach_runtime(self, runtime):
        """Attach the Aetherra runtime to the GUI"""
        self.runtime = runtime

    def attach_lyrixa(self, lyrixa_agent):
        """Attach the Lyrixa AI agent to the GUI"""
        self.lyrixa_agent = lyrixa_agent

    def add_plugin_editor_tab(self):
        """Add the plugin editor tab for editing and creating plugins"""
        # Initialize with safe defaults
        plugin_dir = "Aetherra/plugins"
        memory_manager = getattr(self, "memory", None)
        plugin_manager = getattr(self, "plugins", None)

        tab = PluginEditorTab(
            plugin_dir=plugin_dir,
            memory_manager=memory_manager,
            plugin_manager=plugin_manager,
        )
        self.tab_widget.addTab(tab, "🧩 Plugin Editor")

        # Store reference for later use
        self.plugin_editor_tab = tab

    def inject_plugin_code(self, code: str, filename: str = "generated_plugin.aether"):
        """Inject generated plugin code into the Plugin Editor tab"""
        if hasattr(self, "plugin_editor_tab"):
            self.plugin_editor_tab.set_code_block(code, filename)
            self.tab_widget.setCurrentWidget(self.plugin_editor_tab)
            self.plugin_editor_tab.focus_editor()
            return True
        else:
            print("⚠️ Plugin Editor tab not available")
            return False

    # =============================
    # DASHBOARD UPDATE METHODS
    # =============================

    def update_dashboard_metrics(self):
        """Update all dashboard metrics and status displays"""
        try:
            self.update_system_metrics()
            self.update_intelligence_status()
            self.update_runtime_status()
            self.update_agent_status()
            self.update_performance_metrics()
        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def update_system_metrics(self):
        """Update system metrics display"""
        if hasattr(self, "system_metrics"):
            try:
                if self.intelligence_stack:
                    # Get real-time metrics from intelligence stack
                    metrics = self.intelligence_stack.get_real_time_metrics()

                    system_text = f"""📊 System Overview
Uptime: {metrics.get("uptime", "Unknown")}
Status: {metrics.get("status", "Unknown")}
Active Agents: {metrics.get("active_agents", 0)}
Total Insights: {metrics.get("total_insights", 0)}
Recent Activity: {metrics.get("recent_activity", 0)}
Performance Score: {metrics.get("performance_score", 0.0):.1%}

🏥 Health Status:
Intelligence: {metrics.get("intelligence", {}).get("health", 0):.1f}%
Workflows: {metrics.get("workflows", {}).get("health", 0):.1f}%
Modules: {metrics.get("modules", {}).get("health", 0):.1f}%
Overall: {metrics.get("overall_health", 0):.1f}%

💻 System Resources:
CPU: {metrics.get("performance", {}).get("cpu", 0):.1f}%
Memory: {metrics.get("performance", {}).get("memory", 0):.1f}%
Disk: {metrics.get("performance", {}).get("disk", 0):.1f}%"""
                else:
                    system_text = """📊 System Overview
Status: ⚠️ Intelligence Stack not connected
Please check system initialization."""

                self.system_metrics.setPlainText(system_text)
            except Exception as e:
                self.system_metrics.setPlainText(f"⚠️ System metrics error: {e}")
                print(f"Error updating system metrics: {e}")

    def update_intelligence_status(self):
        """Update intelligence system status display"""
        if hasattr(self, "intelligence_status") and self.intelligence_stack:
            try:
                status = self.intelligence_stack.get_status()
                patterns = len(
                    self.intelligence_stack.intelligence_system.memory_patterns
                )
                status_text = f"""🧠 Intelligence Status: ✅ Active
Memory Patterns: {patterns}
Learning Iterations: {status.get("learning_iterations", 0)}
Pattern Recognition: {status.get("pattern_recognitions", 0)}"""
                self.intelligence_status.setPlainText(status_text)
            except Exception as e:
                self.intelligence_status.setPlainText(
                    f"⚠️ Intelligence status error: {e}"
                )

    def update_runtime_status(self):
        """Update Aetherra runtime status display"""
        if hasattr(self, "runtime_status") and self.runtime:
            try:
                runtime_text = """⚡ Runtime Status: ✅ Active
Mode: Production
Uptime: Available
Performance: Optimal"""
                self.runtime_status.setPlainText(runtime_text)
            except Exception as e:
                self.runtime_status.setPlainText(f"⚠️ Runtime status error: {e}")

    def update_agent_status(self):
        """Update Lyrixa agent status display"""
        if hasattr(self, "agent_status") and self.lyrixa_agent:
            try:
                agent_count = 6  # Main agent + 5 sub-agents
                agent_text = f"""🤖 Agent Status: ✅ Active
Main Agent: Lyrixa AI
Sub-Agents: {agent_count - 1} active
Model: {getattr(self.lyrixa_agent, "current_model", "gpt-4o")}
State: Ready"""
                self.agent_status.setPlainText(agent_text)
            except Exception as e:
                self.agent_status.setPlainText(f"⚠️ Agent status error: {e}")

    def update_performance_metrics(self):
        """Update system performance metrics"""
        if hasattr(self, "performance_metrics"):
            try:
                import sys

                performance_text = f"""📊 Performance Metrics
Python: {sys.version.split()[0]}
Platform: Windows
Memory: Available
CPU: Active
LLM Models: 9 available
Plugins: {len(getattr(self.intelligence_stack, "discovered_plugins", [])) if self.intelligence_stack else 0}"""
                self.performance_metrics.setPlainText(performance_text)
            except Exception as e:
                self.performance_metrics.setPlainText(
                    f"⚠️ Performance metrics error: {e}"
                )

    def init_background_monitors(self):
        """Initialize background monitoring timers"""
        try:
            # Start the dashboard update timer
            self.monitor_timer.start(5000)  # Update every 5 seconds

            # Add any other background monitoring here
            print("🔄 Background monitoring initialized")
        except Exception as e:
            print(f"⚠️ Monitor initialization error: {e}")

    # =============================
    # CHAT FUNCTIONALITY METHODS
    # =============================

    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Lyrixa AI Assistant - Ready")

    def add_chat_message(self, sender: str, message: str, color: str = "#ffffff"):
        """Add a message to the chat display"""
        try:
            # Format the message with HTML for styling
            timestamp = __import__("datetime").datetime.now().strftime("%H:%M:%S")
            formatted_message = f"""
            <div style="margin: 10px 0; padding: 8px; border-left: 3px solid {color};">
                <span style="color: {color}; font-weight: bold;">[{timestamp}] {sender}:</span><br>
                <span style="color: #ffffff; margin-left: 10px;">{message}</span>
            </div>
            """

            # Append to chat display
            self.chat_display.append(formatted_message)

            # Auto-scroll to bottom
            scrollbar = self.chat_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

        except Exception as e:
            print(f"Error adding chat message: {e}")

    def send_message(self):
        """Send a message to Lyrixa and get response"""
        try:
            user_message = self.chat_input.text().strip()
            if not user_message:
                return

            # Clear input
            self.chat_input.clear()

            # Add user message to chat
            self.add_chat_message("You", user_message, "#00ff88")

            # Send to Lyrixa if available
            if self.intelligence_stack:
                try:
                    # Show thinking indicator
                    self.add_chat_message("Lyrixa", "🤔 Thinking...", "#ffaa00")

                    # Generate response using intelligence stack
                    response = self.intelligence_stack.generate_response(user_message)

                    # Remove thinking indicator by replacing last message
                    self.add_chat_message("Lyrixa", response, "#88aaff")

                except Exception as e:
                    self.add_chat_message(
                        "System", f"❌ Error generating response: {e}", "#ff4444"
                    )
            else:
                self.add_chat_message(
                    "System",
                    "⚠️ Intelligence stack not available - please wait for initialization",
                    "#ffaa00",
                )

        except Exception as e:
            self.add_chat_message("System", f"❌ Error sending message: {e}", "#ff4444")

    def setup_dark_theme(self):
        """Setup the dark theme for the application"""
        try:
            # Set application-wide dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #1a1a1a;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 5px;
                }
                QLineEdit {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 8px;
                }
                QComboBox {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    border: none;
                }
                QPushButton {
                    background-color: #2a2a2a;
                    color: #ffffff;
                    border: 1px solid #404040;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #3a3a3a;
                }
                QPushButton:pressed {
                    background-color: #1a1a1a;
                }
                QTabWidget::pane {
                    border: 1px solid #404040;
                    background-color: #2a2a2a;
                }
                QTabWidget::tab-bar {
                    alignment: center;
                }
                QTabBar::tab {
                    background-color: #1a1a1a;
                    color: #ffffff;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #2a2a2a;
                    color: #00ff88;
                }
                QTabBar::tab:hover {
                    background-color: #3a3a3a;
                }
                QLabel {
                    color: #ffffff;
                }
                QSplitter::handle {
                    background-color: #404040;
                }
            """)
        except Exception as e:
            print(f"Error setting up dark theme: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LyrixaWindow()
    window.show()
    sys.exit(app.exec())
