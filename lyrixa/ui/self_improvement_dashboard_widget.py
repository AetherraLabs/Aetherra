# PySide6 Self-Improvement Dashboard Widget
import json

import requests
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

API_BASE = "http://localhost:8000"  # Adjust if needed


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
        header = QLabel("<b>Plugin Intelligence</b>")
        header.setToolTip("View and search plugin capabilities and schemas.")
        vbox.addWidget(header)
        self.refresh_plugins_btn = QPushButton("Refresh Plugin Capabilities")
        self.refresh_plugins_btn.setToolTip("Reload plugin metadata from the backend.")
        self.refresh_plugins_btn.clicked.connect(self._refresh_plugins)
        vbox.addWidget(self.refresh_plugins_btn)
        self.plugins_loading = QProgressBar()
        self.plugins_loading.setRange(0, 0)
        self.plugins_loading.hide()
        vbox.addWidget(self.plugins_loading)
        self.plugin_list = QListWidget()
        self.plugin_list.setToolTip("Click a plugin for details.")
        vbox.addWidget(self.plugin_list)
        self.tabs.addTab(tab, "Plugin Intelligence")

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
            self.show_error(data["error"])
        else:
            self.show_success("Proposed changes received.")
        self.propose_result.setText(json.dumps(data, indent=2))

    def _refresh_plugins(self):
        self.clear_status()
        self.refresh_plugins_btn.setEnabled(False)
        self.plugins_loading.show()
        thread = APICallThread(f"{API_BASE}/api/plugins/capabilities")
        thread.resultReady.connect(self._show_plugins)
        thread.finished.connect(lambda: self._threads.remove(thread))
        self._threads.append(thread)
        thread.start()

    def _show_plugins(self, data):
        self.refresh_plugins_btn.setEnabled(True)
        self.plugins_loading.hide()
        self.plugin_list.clear()
        if "plugins" in data:
            self.show_success(f"Loaded {len(data['plugins'])} plugins.")
            for plugin in data["plugins"]:
                item = QListWidgetItem(
                    plugin.get("name") or plugin.get("file") or str(plugin)
                )
                item.setToolTip(json.dumps(plugin, indent=2))
                self.plugin_list.addItem(item)
        else:
            self.show_error(str(data))
            self.plugin_list.addItem(QListWidgetItem("Error: " + str(data)))

    def _forecast_goal(self):
        self.clear_status()
        goal = self.goal_input.text().strip()
        if not goal:
            self.show_error("Please enter a goal description.")
            self.forecast_result.setText("")
            return
        self.forecast_btn.setEnabled(False)
        self.forecast_loading.show()
        payload = {"goal": {"description": goal}}
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
            self.show_error(data["error"])
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
        payload = {"goal": {"description": goal}}
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


# To use this widget, import and add to your main window or launcher.
# Example:
# from lyrixa.ui.self_improvement_dashboard_widget import SelfImprovementDashboardWidget
# dashboard = SelfImprovementDashboardWidget()
# dashboard.show()
