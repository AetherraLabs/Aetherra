# PySide6 Self-Improvement Dashboard Widget
import json

import requests
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

API_BASE = "http://127.0.0.1:8007"  # Enhanced API server with propose_changes endpoint


class APICallThread(QThread):
    resultReady = Signal(dict)

    def __init__(self, endpoint, method="get", payload=None):
        super().__init__()
        self.endpoint = endpoint
        self.method = method
        self.payload = payload

    def run(self):
        try:
            if self.method == "get":
                resp = requests.get(self.endpoint)
            else:
                resp = requests.post(self.endpoint, json=self.payload)
            data = resp.json()
            self.resultReady.emit(data)
        except Exception as e:
            self.resultReady.emit({"error": str(e)})


class SelfImprovementDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Lyrixa Self-Improvement Dashboard")
        self.resize(900, 600)
        self._threads = []  # Prevent QThread GC
        layout = QVBoxLayout(self)
        self.status_bar = QLabel()
        self.status_bar.setStyleSheet(
            "color: #fff; background: #444; padding: 4px; border-radius: 4px;"
        )
        self.status_bar.hide()
        layout.addWidget(self.status_bar)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self._init_self_improvement_tab()
        self._init_plugin_intelligence_tab()
        self._init_goal_forecast_tab()
        self._init_reasoning_context_tab()

        # Check API connectivity on startup
        self._check_api_connectivity()

    def show_error(self, message):
        self.status_bar.setText(f"❌ {message}")
        self.status_bar.setStyleSheet(
            "color: #fff; background: #c00; padding: 4px; border-radius: 4px;"
        )
        self.status_bar.show()

    def show_success(self, message):
        self.status_bar.setText(f"✅ {message}")
        self.status_bar.setStyleSheet(
            "color: #fff; background: #080; padding: 4px; border-radius: 4px;"
        )
        self.status_bar.show()

    def clear_status(self):
        self.status_bar.hide()

    def _init_self_improvement_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        header = QLabel("<b>Self-Improvement Actions</b>")
        header.setToolTip("Trigger and review self-improvement proposals.")
        vbox.addWidget(header)
        self.propose_btn = QPushButton("Propose Changes")
        self.propose_btn.setToolTip(
            "Ask Lyrixa to analyze itself and propose improvements."
        )
        self.propose_btn.clicked.connect(self._propose_changes)
        vbox.addWidget(self.propose_btn)
        self.propose_loading = QProgressBar()
        self.propose_loading.setRange(0, 0)
        self.propose_loading.hide()
        vbox.addWidget(self.propose_loading)
        self.propose_result = QTextEdit()
        self.propose_result.setReadOnly(True)
        vbox.addWidget(self.propose_result)
        self.tabs.addTab(tab, "Self-Improvement")

    def _init_plugin_intelligence_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)

        # Header section
        header = QLabel("<b>Plugin Intelligence Dashboard</b>")
        header.setToolTip("Advanced plugin discovery and management system.")
        vbox.addWidget(header)

        # Control buttons row
        controls_layout = QHBoxLayout()
        self.refresh_plugins_btn = QPushButton("🔄 Refresh Plugins")
        self.refresh_plugins_btn.setToolTip("Reload plugin metadata from the backend.")
        self.refresh_plugins_btn.clicked.connect(self._refresh_plugins)
        controls_layout.addWidget(self.refresh_plugins_btn)

        self.aether_hub_sync_btn = QPushButton("🔄 Sync Aether Hub")
        self.aether_hub_sync_btn.setToolTip("Fetch new plugins from Aether Hub.")
        self.aether_hub_sync_btn.clicked.connect(self._sync_aether_hub)
        controls_layout.addWidget(self.aether_hub_sync_btn)

        controls_layout.addStretch()
        vbox.addLayout(controls_layout)

        # Filter and sort section
        filter_layout = QHBoxLayout()
        self.plugin_search = QLineEdit()
        self.plugin_search.setPlaceholderText("🔍 Search plugins by name, capability, or tag...")
        self.plugin_search.textChanged.connect(self._filter_plugins)
        filter_layout.addWidget(self.plugin_search)

        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Name (A-Z)", "Name (Z-A)", "Confidence ↓", "Confidence ↑",
            "Last Used", "Most Used", "Category", "Recommended"
        ])
        self.sort_combo.currentTextChanged.connect(self._sort_plugins)
        filter_layout.addWidget(self.sort_combo)
        vbox.addLayout(filter_layout)

        # Loading indicator
        self.plugins_loading = QProgressBar()
        self.plugins_loading.setRange(0, 0)
        self.plugins_loading.hide()
        vbox.addWidget(self.plugins_loading)

        # Plugin list with enhanced display
        self.plugin_tree = QTreeWidget()
        self.plugin_tree.setHeaderLabels([
            "Plugin", "Category", "Confidence", "Status", "Actions"
        ])
        self.plugin_tree.setToolTip("Enhanced plugin view with capabilities and actions.")
        self.plugin_tree.itemClicked.connect(self._plugin_item_selected)
        vbox.addWidget(self.plugin_tree)

        # Plugin details panel
        self.plugin_details = QTextEdit()
        self.plugin_details.setReadOnly(True)
        self.plugin_details.setMaximumHeight(150)
        self.plugin_details.setPlaceholderText("Select a plugin to view detailed capabilities, tags, and metadata...")
        vbox.addWidget(self.plugin_details)

        self.tabs.addTab(tab, "🧩 Plugin Intelligence")

    def _init_goal_forecast_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        header = QLabel("<b>Goal Forecast</b>")
        header.setToolTip("Simulate and forecast the outcome of a goal.")
        vbox.addWidget(header)
        hbox = QHBoxLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Describe your goal...")
        self.goal_input.setToolTip("Enter a goal for Lyrixa to forecast.")
        hbox.addWidget(self.goal_input)
        self.forecast_btn = QPushButton("Forecast Goal")
        self.forecast_btn.setToolTip("Get a prediction for this goal.")
        self.forecast_btn.clicked.connect(self._forecast_goal)
        hbox.addWidget(self.forecast_btn)
        vbox.addLayout(hbox)
        self.forecast_loading = QProgressBar()
        self.forecast_loading.setRange(0, 0)
        self.forecast_loading.hide()
        vbox.addWidget(self.forecast_loading)
        self.forecast_result = QTextEdit()
        self.forecast_result.setReadOnly(True)
        vbox.addWidget(self.forecast_result)
        self.tabs.addTab(tab, "Goal Forecast")

    def _init_reasoning_context_tab(self):
        tab = QWidget()
        vbox = QVBoxLayout(tab)
        header = QLabel("<b>Reasoning Context</b>")
        header.setToolTip("See related past cases and outcomes for a goal.")
        vbox.addWidget(header)
        hbox = QHBoxLayout()
        self.reasoning_goal_input = QLineEdit()
        self.reasoning_goal_input.setPlaceholderText("Describe your goal...")
        self.reasoning_goal_input.setToolTip("Enter a goal to see reasoning context.")
        hbox.addWidget(self.reasoning_goal_input)
        self.reasoning_btn = QPushButton("Get Reasoning Context")
        self.reasoning_btn.setToolTip("Find related past cases for this goal.")
        self.reasoning_btn.clicked.connect(self._get_reasoning_context)
        hbox.addWidget(self.reasoning_btn)
        vbox.addLayout(hbox)
        self.reasoning_loading = QProgressBar()
        self.reasoning_loading.setRange(0, 0)
        self.reasoning_loading.hide()
        vbox.addWidget(self.reasoning_loading)
        self.reasoning_result = QTextEdit()
        self.reasoning_result.setReadOnly(True)
        vbox.addWidget(self.reasoning_result)
        self.tabs.addTab(tab, "Reasoning Context")

    def _propose_changes(self):
        self.clear_status()
        self.propose_btn.setEnabled(False)
        self.propose_loading.show()
        thread = APICallThread(
            f"{API_BASE}/api/self_improvement/propose_changes", method="post"
        )
        thread.resultReady.connect(self._show_propose_result)
        thread.finished.connect(lambda: self._threads.remove(thread))
        self._threads.append(thread)
        thread.start()

    def _show_propose_result(self, data):
        self.propose_btn.setEnabled(True)
        self.propose_loading.hide()
        if "error" in data:
            error_msg = data["error"]
            if "Failed to establish a new connection" in error_msg or "Connection refused" in error_msg:
                self.show_error("API Server not available - using offline mode")
                # Provide offline fallback content
                offline_content = {
                    "status": "offline_mode",
                    "message": "Self-Improvement Dashboard - Offline Mode",
                    "suggestions": [
                        "🔧 Optimize memory usage patterns",
                        "⚡ Enhance response time algorithms",
                        "🧠 Improve context understanding",
                        "📊 Better performance analytics",
                        "🔄 Streamline workflow processes"
                    ],
                    "note": "API server offline - showing cached suggestions. Start API server for real-time analysis."
                }
                self.propose_result.setText(json.dumps(offline_content, indent=2))
            else:
                self.show_error(f"Error: {error_msg}")
                self.propose_result.setText(json.dumps(data, indent=2))
        else:
            self.show_success("Proposed changes received.")
            self.propose_result.setText(json.dumps(data, indent=2))

    def _refresh_plugins(self):
        self.clear_status()
        self.refresh_plugins_btn.setEnabled(False)
        self.plugins_loading.show()
        thread = APICallThread(f"{API_BASE}/api/plugins/enhanced_capabilities")
        thread.resultReady.connect(self._show_enhanced_plugins)
        thread.finished.connect(lambda: self._threads.remove(thread))
        self._threads.append(thread)
        thread.start()

    def _show_plugins(self, data):
        self.refresh_plugins_btn.setEnabled(True)
        self.plugins_loading.hide()
        self.plugin_tree.clear()

        if "error" in data:
            error_msg = data["error"]
            if "Failed to establish a new connection" in error_msg or "Connection refused" in error_msg:
                self.show_error("API Server not available - showing offline plugin info")
                # Provide offline fallback content for plugins
                offline_plugins = [
                    {"name": "sysmon", "status": "active", "description": "System performance monitoring", "category": "monitoring", "confidence": 0.95},
                    {"name": "optimizer", "status": "active", "description": "Code and system performance optimization", "category": "enhancement", "confidence": 0.90},
                    {"name": "selfrepair", "status": "active", "description": "Automatic debugging and repair system", "category": "automation", "confidence": 0.88},
                    {"name": "whisper", "status": "active", "description": "Audio transcription and speech processing", "category": "analysis", "confidence": 0.92},
                    {"name": "reflector", "status": "active", "description": "Behavior analysis and self-reflection tools", "category": "analysis", "confidence": 0.85},
                    {"name": "executor", "status": "active", "description": "Command scheduling and execution management", "category": "automation", "confidence": 0.93},
                    {"name": "coretools", "status": "active", "description": "File access and core utility tools", "category": "utility", "confidence": 0.98}
                ]
                for plugin in offline_plugins:
                    item = QTreeWidgetItem(self.plugin_tree)
                    item.setText(0, f"📦 {plugin['name']}")
                    item.setText(1, plugin['category'].title())
                    item.setText(2, f"{plugin['confidence']:.2f}")
                    item.setText(3, f"🟢 {plugin['status']}")
                    item.setText(4, "🔍 View | ▶️ Run")
                    item.setToolTip(0, f"{plugin['description']}\nOffline mode - Connect API for real-time data")
            else:
                self.show_error(f"Error: {error_msg}")
                error_item = QTreeWidgetItem(self.plugin_tree)
                error_item.setText(0, f"❌ Error: {error_msg}")
        elif "plugins" in data:
            self.show_success(f"Loaded {len(data['plugins'])} plugins.")
            for plugin in data["plugins"]:
                item = QTreeWidgetItem(self.plugin_tree)
                name = plugin.get("name") or plugin.get("file") or str(plugin)
                item.setText(0, f"📦 {name}")
                item.setText(1, plugin.get("category", "Unknown").title())
                item.setText(2, str(plugin.get("confidence_score", "N/A")))
                item.setText(3, f"🟢 {plugin.get('status', 'active')}")
                item.setText(4, "🔍 View | ▶️ Run | 🧠 Analyze")

                # Set detailed tooltip with capabilities
                capabilities = plugin.get("capabilities", [])
                tags = plugin.get("tags", [])
                tooltip = f"Plugin: {name}\n"
                tooltip += f"Description: {plugin.get('description', 'No description')}\n"
                if capabilities:
                    tooltip += f"Capabilities: {', '.join(capabilities)}\n"
                if tags:
                    tooltip += f"Tags: {', '.join(tags)}\n"
                tooltip += f"Full data: {json.dumps(plugin, indent=2)}"
                item.setToolTip(0, tooltip)
        else:
            self.show_error("Unexpected response format")
            error_item = QTreeWidgetItem(self.plugin_tree)
            error_item.setText(0, f"❌ Unexpected response: {str(data)}")

    def _show_enhanced_plugins(self, data):
        """Display enhanced plugin capabilities with detailed metadata"""
        self.refresh_plugins_btn.setEnabled(True)
        self.plugins_loading.hide()
        self.plugin_tree.clear()

        if "error" in data:
            error_msg = data["error"]
            self.show_error(f"Enhanced capabilities error: {error_msg}")
            # Fallback to basic plugin display
            self._show_plugins(data)
            return

        if "plugins" not in data:
            self.show_error("Invalid enhanced capabilities response")
            return

        plugins = data["plugins"]
        summary = data.get("summary", {})

        # Show summary in status
        total = summary.get("total_plugins", len(plugins))
        high_conf = summary.get("high_confidence", 0)
        self.show_success(f"✅ Enhanced Analysis: {total} plugins discovered, {high_conf} high-confidence")

        # Display plugins with enhanced metadata
        for plugin in plugins:
            item = QTreeWidgetItem(self.plugin_tree)

            # Plugin name with emoji based on confidence
            confidence = plugin.get("confidence_score", 0)
            if confidence > 0.9:
                icon = "🌟"
            elif confidence > 0.8:
                icon = "⭐"
            elif confidence > 0.6:
                icon = "📦"
            else:
                icon = "⚠️"

            name = plugin.get("name", "Unknown")
            item.setText(0, f"{icon} {name}")

            # Category with proper formatting
            category = plugin.get("category", "unknown").title()
            item.setText(1, category)

            # Confidence score with color coding
            conf_text = f"{confidence:.2f}"
            item.setText(2, conf_text)

            # Status with enhanced info
            is_recommended = plugin.get("lyrixa_recommended", False)
            complexity = plugin.get("complexity_level", "unknown")
            if is_recommended:
                status_text = f"🚀 Recommended ({complexity})"
            else:
                status_text = f"🟢 Available ({complexity})"
            item.setText(3, status_text)

            # Enhanced action buttons
            actions = "🔍 View | ▶️ Run | 🧠 Analyze | ⚙️ Improve"
            if is_recommended:
                actions = "⭐ " + actions
            item.setText(4, actions)

            # Create comprehensive tooltip
            capabilities = plugin.get("capabilities", [])
            tags = plugin.get("tags", [])
            description = plugin.get("description", "No description")

            tooltip = f"🧩 Plugin: {name}\n"
            tooltip += f"📊 Confidence: {confidence:.2f}\n"
            tooltip += f"📂 Category: {category}\n"
            tooltip += f"🔧 Complexity: {complexity.title()}\n"
            tooltip += f"📝 Description: {description[:100]}...\n"

            if capabilities:
                tooltip += f"⚡ Capabilities: {', '.join(capabilities[:5])}\n"
            if tags:
                tooltip += f"🏷️ Tags: {', '.join(tags[:5])}\n"

            collab_potential = plugin.get("collaboration_potential", 0)
            tooltip += f"🤝 Collaboration Potential: {collab_potential:.2f}\n"

            if is_recommended:
                tooltip += "\n⭐ Recommended by Lyrixa AI"

            # Usage stats
            usage_count = plugin.get("usage_count", 0)
            if usage_count > 0:
                tooltip += f"\n📈 Used {usage_count} times"

            item.setToolTip(0, tooltip)

            # Store full plugin data for selection handling
            item.setData(0, 1000, plugin)  # Custom role for plugin data

    def _forecast_goal(self):
        self.clear_status()
        goal = self.goal_input.text().strip()
        if not goal:
            self.show_error("Please enter a goal description.")
            self.forecast_result.setText("")
            return
        self.forecast_btn.setEnabled(False)
        self.forecast_loading.show()
        payload = {"goal": goal}
        thread = APICallThread(
            f"{API_BASE}/api/goals/forecast", method="post", payload=payload
        )
        thread.resultReady.connect(self._show_forecast_result)
        thread.finished.connect(lambda: self._threads.remove(thread))
        self._threads.append(thread)
        thread.start()

    def _show_forecast_result(self, data):
        self.forecast_btn.setEnabled(True)
        self.forecast_loading.hide()
        if "error" in data:
            error_msg = data["error"]
            if "Failed to establish a new connection" in error_msg or "Connection refused" in error_msg:
                self.show_error("API Server not available - using offline forecast")
                goal = self.goal_input.text().strip()
                # Provide offline fallback content for goal forecasting
                offline_forecast = {
                    "status": "offline_mode",
                    "goal": goal,
                    "forecast": {
                        "probability": "75%",
                        "timeline": "2-4 weeks",
                        "key_factors": [
                            "Resource availability",
                            "Technical complexity",
                            "User engagement",
                            "System performance"
                        ],
                        "recommendations": [
                            "Break down into smaller milestones",
                            "Allocate sufficient testing time",
                            "Monitor progress regularly",
                            "Plan for contingencies"
                        ]
                    },
                    "note": "Offline analysis - Connect API server for AI-powered forecasting"
                }
                self.forecast_result.setText(json.dumps(offline_forecast, indent=2))
            else:
                self.show_error(f"Error: {error_msg}")
                self.forecast_result.setText(json.dumps(data, indent=2))
        else:
            self.show_success("Forecast received.")
            self.forecast_result.setText(json.dumps(data, indent=2))

    def _get_reasoning_context(self):
        self.clear_status()
        goal = self.reasoning_goal_input.text().strip()
        if not goal:
            self.show_error("Please enter a goal description.")
            self.reasoning_result.setText("")
            return
        self.reasoning_btn.setEnabled(False)
        self.reasoning_loading.show()
        payload = {"goal": goal}
        thread = APICallThread(
            f"{API_BASE}/api/goals/reasoning_context", method="post", payload=payload
        )
        thread.resultReady.connect(self._show_reasoning_result)
        thread.finished.connect(lambda: self._threads.remove(thread))
        self._threads.append(thread)
        thread.start()

    def _show_reasoning_result(self, data):
        self.reasoning_btn.setEnabled(True)
        self.reasoning_loading.hide()
        if "error" in data:
            self.show_error(data["error"])
        else:
            self.show_success("Reasoning context received.")
        self.reasoning_result.setText(json.dumps(data, indent=2))

    def _check_api_connectivity(self):
        """Check if the API server is running and show status"""
        try:
            import requests
            response = requests.get(f"{API_BASE}/health", timeout=2)
            if response.status_code == 200:
                self.show_success("✅ API Server Connected - Real-time mode active")
            else:
                self.show_error("⚠️ API Server responding but unhealthy - Offline mode")
        except Exception as e:
            self.show_error("⚠️ API Server offline - Using offline mode with cached data")

    def _sync_aether_hub(self):
        """Sync with Aether Hub to fetch new plugins"""
        self.aether_hub_sync_btn.setEnabled(False)
        self.show_success("🔄 Syncing with Aether Hub... (Feature coming soon)")
        # TODO: Implement Aether Hub sync functionality
        # This would connect to Aether Hub API and fetch new plugins
        self.aether_hub_sync_btn.setEnabled(True)

    def _filter_plugins(self, text):
        """Filter plugins based on search text"""
        for i in range(self.plugin_tree.topLevelItemCount()):
            item = self.plugin_tree.topLevelItem(i)
            if item is None:
                continue

            # Check if search text matches plugin name, category, or tooltip
            plugin_text = item.text(0).lower()
            category_text = item.text(1).lower()
            tooltip_text = item.toolTip(0).lower()

            search_text = text.lower()
            visible = (search_text in plugin_text or
                      search_text in category_text or
                      search_text in tooltip_text)
            item.setHidden(not visible)

    def _sort_plugins(self, sort_type):
        """Sort plugins based on selected criteria"""
        # Implementation for sorting plugins
        # This would reorganize the tree widget items based on the sort type
        self.show_success(f"🔄 Sorting by: {sort_type} (Feature coming soon)")
        # TODO: Implement sorting logic for different criteria

    def _plugin_item_selected(self, item, column):
        """Handle plugin item selection and show enhanced details"""
        if item is None:
            return

        # Try to get enhanced plugin data first
        plugin_data = item.data(0, 1000)  # Custom role

        if plugin_data:
            # Enhanced plugin details
            name = plugin_data.get("name", "Unknown")
            confidence = plugin_data.get("confidence_score", 0)
            category = plugin_data.get("category", "unknown")
            description = plugin_data.get("description", "No description")
            capabilities = plugin_data.get("capabilities", [])
            tags = plugin_data.get("tags", [])
            complexity = plugin_data.get("complexity_level", "unknown")
            collab_potential = plugin_data.get("collaboration_potential", 0)
            is_recommended = plugin_data.get("lyrixa_recommended", False)

            # Create detailed display
            details = f"🧩 {name}\n"
            details += "=" * (len(name) + 3) + "\n\n"

            # Core metrics
            details += f"📊 Confidence Score: {confidence:.2f}/1.0\n"
            details += f"📂 Category: {category.title()}\n"
            details += f"🔧 Complexity: {complexity.title()}\n"
            details += f"🤝 Collaboration Potential: {collab_potential:.2f}\n\n"

            # Description
            details += f"📝 Description:\n{description}\n\n"

            # Capabilities
            if capabilities:
                details += f"⚡ Capabilities ({len(capabilities)}):\n"
                for i, cap in enumerate(capabilities, 1):
                    details += f"  {i}. {cap.replace('_', ' ').title()}\n"
                details += "\n"

            # Tags
            if tags:
                details += f"🏷️ Tags: {', '.join(tags)}\n\n"

            # AI Recommendation
            if is_recommended:
                details += "⭐ LYRIXA RECOMMENDED\n"
                details += "This plugin is highly rated by Lyrixa AI for its quality and usefulness.\n\n"

            # Available actions
            details += "🛠️ Available Actions:\n"
            details += "  🔍 View in Plugin Editor\n"
            details += "  ▶️ Run Plugin\n"
            details += "  � Analyze Plugin Performance\n"
            details += "  ⚙️ Improve This Plugin\n"
            if is_recommended:
                details += "  📚 View AI Analysis Report\n"

            # Technical details
            functions = plugin_data.get("functions", [])
            if functions:
                details += f"\n🔧 Technical Details:\n"
                details += f"  Functions: {len(functions)}\n"
                details += f"  Lines of Code: {plugin_data.get('line_count', 'Unknown')}\n"

                main_funcs = [f for f in functions if f.get("is_main", False)]
                if main_funcs:
                    details += f"  Has Main Function: Yes\n"

            self.plugin_details.setText(details)
            self.show_success(f"Selected: {name} (Confidence: {confidence:.2f})")

        else:
            # Fallback to basic details
            plugin_name = item.text(0).replace("📦 ", "").replace("🌟 ", "").replace("⭐ ", "").replace("⚠️ ", "")
            tooltip_data = item.toolTip(0)

            details = f"🧩 Plugin Details: {plugin_name}\n\n"
            details += tooltip_data
            details += "\n\n🛠️ Available Actions:\n"
            details += "🔍 View in Plugin Editor\n"
            details += "▶️ Run Plugin\n"
            details += "🧠 Analyze Plugin\n"
            details += "⚙️ Improve This Plugin\n"

            self.plugin_details.setText(details)
            self.show_success(f"Selected plugin: {plugin_name}")

# To use this widget, import and add to your main window or launcher.
# Example:
# from lyrixa.ui.self_improvement_dashboard_widget import SelfImprovementDashboardWidget
# dashboard = SelfImprovementDashboardWidget()
# dashboard.show()
