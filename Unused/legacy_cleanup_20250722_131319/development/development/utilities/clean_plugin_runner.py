#!/usr/bin/env python3
"""
Clean Plugin Runner
==================
🔧 Direct plugin execution interface for Lyrixa Plugin Manager
🚀 Execute plugins with parameters and goal context
📊 Real-time plugin monitoring and output display
"""

import os
import sys
import json
import time
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QSplitter,
        QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
        QGroupBox, QTabWidget, QListWidget, QListWidgetItem,
        QProgressBar, QCheckBox, QSpinBox, QSlider, QFrame,
        QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView,
        QApplication, QMessageBox, QFileDialog, QDialog, QDialogButtonBox
    )
    from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject
    from PySide6.QtGui import QFont, QColor, QTextCursor, QIcon
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False
    print("⚠️  PySide6 not available - Clean Plugin Runner requires GUI")


class PluginExecutionThread(QThread):
    """Thread for executing plugins asynchronously"""

    execution_started = Signal(str)
    execution_finished = Signal(str, object)
    execution_error = Signal(str, str)
    output_received = Signal(str)

    def __init__(self, plugin_manager, plugin_name: str, params: Dict[str, Any]):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.plugin_name = plugin_name
        self.params = params
        self.result = None
        self.error = None

    def run(self):
        """Execute the plugin in a separate thread"""
        try:
            self.execution_started.emit(self.plugin_name)

            # Execute plugin through enhanced plugin manager
            if hasattr(self.plugin_manager, 'execute_plugin'):
                self.result = self.plugin_manager.execute_plugin(
                    self.plugin_name, **self.params
                )
            else:
                # Fallback for basic plugin managers
                if self.plugin_name in self.plugin_manager.plugins:
                    plugin = self.plugin_manager.plugins[self.plugin_name]
                    if hasattr(plugin, 'execute'):
                        self.result = plugin.execute(**self.params)
                    elif hasattr(plugin, 'main'):
                        self.result = plugin.main(**self.params)
                    else:
                        self.result = "Plugin has no execute() or main() method"
                else:
                    self.result = f"Plugin '{self.plugin_name}' not found"

            self.execution_finished.emit(self.plugin_name, self.result)

        except Exception as e:
            self.error = str(e)
            self.execution_error.emit(self.plugin_name, str(e))


class PluginDiscovery:
    """Plugin discovery and metadata extraction"""

    def __init__(self):
        self.known_plugins = {}
        self.plugin_paths = [
            "Aetherra/plugins",
            "Aetherra/lyrixa/plugins",
            "plugins"
        ]
        self.discover_plugins()

    def discover_plugins(self):
        """Discover all available plugins"""
        self.known_plugins = {}

        for plugin_dir in self.plugin_paths:
            if os.path.exists(plugin_dir):
                self._scan_directory(plugin_dir)

    def _scan_directory(self, directory: str):
        """Scan directory for plugins"""
        try:
            for file in os.listdir(directory):
                if file.endswith('.py') and not file.startswith('__'):
                    plugin_path = os.path.join(directory, file)
                    plugin_name = file[:-3]  # Remove .py extension

                    # Extract metadata from plugin file
                    metadata = self._extract_metadata(plugin_path)

                    self.known_plugins[plugin_name] = {
                        'name': plugin_name,
                        'path': plugin_path,
                        'description': metadata.get('description', 'No description'),
                        'category': metadata.get('category', 'general'),
                        'parameters': metadata.get('parameters', {}),
                        'capabilities': metadata.get('capabilities', [])
                    }

        except Exception as e:
            print(f"Error scanning {directory}: {e}")

    def _extract_metadata(self, plugin_path: str) -> Dict[str, Any]:
        """Extract metadata from plugin file"""
        metadata = {}

        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple metadata extraction (could be enhanced)
            lines = content.split('\n')
            for line in lines[:50]:  # Check first 50 lines
                line = line.strip()
                if line.startswith('# Description:'):
                    metadata['description'] = line.split(':', 1)[1].strip()
                elif line.startswith('# Category:'):
                    metadata['category'] = line.split(':', 1)[1].strip()
                elif 'def execute(' in line or 'def main(' in line:
                    # Extract parameter names from function signature
                    if '(' in line and ')' in line:
                        params_str = line.split('(')[1].split(')')[0]
                        params = [p.strip().split(':')[0].strip() for p in params_str.split(',')]
                        params = [p for p in params if p and p != 'self']
                        metadata['parameters'] = {p: 'string' for p in params}

        except Exception as e:
            print(f"Error extracting metadata from {plugin_path}: {e}")

        return metadata

    def get_plugin_list(self) -> List[str]:
        """Get list of available plugin names"""
        return list(self.known_plugins.keys())

    def get_plugin_info(self, plugin_name: str) -> Dict[str, Any]:
        """Get detailed info about a plugin"""
        return self.known_plugins.get(plugin_name, {})


class CleanPluginRunner(QWidget):
    """Clean interface for executing Lyrixa plugins"""

    def __init__(self, plugin_manager=None):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.plugin_discovery = PluginDiscovery()
        self.execution_thread = None
        self.execution_history = []

        # Initialize plugin manager if not provided
        if not self.plugin_manager:
            self.init_plugin_manager()

        # Apply Aetherra dark theme
        self.setStyleSheet("""
            /* === AETHERRA DARK THEME === */
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #0d0d0d, stop:1 #0a0a0a);
                color: #ffffff;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            }

            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 255, 136, 0.3), stop:1 rgba(0, 255, 136, 0.1));
                border: 1px solid #00ff88;
                border-radius: 6px;
                color: #ffffff;
                font-weight: bold;
                padding: 10px 20px;
            }

            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.7));
                color: #000000;
            }

            QPushButton:pressed {
                background: rgba(0, 255, 136, 0.8);
                color: #000000;
            }

            QComboBox {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
                font-size: 14px;
            }

            QComboBox::drop-down {
                border: none;
                background: rgba(0, 255, 136, 0.2);
            }

            QComboBox::down-arrow {
                background: #00ff88;
                border: none;
            }

            QComboBox QAbstractItemView {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                color: #ffffff;
                selection-background-color: rgba(0, 255, 136, 0.2);
            }

            QLineEdit {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border: 2px solid #00ff88;
            }

            QTextEdit {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
                padding: 8px;
                font-size: 13px;
                font-family: 'JetBrains Mono', monospace;
            }

            QLabel {
                color: #ffffff;
                font-weight: bold;
                font-size: 14px;
            }

            QGroupBox {
                border: 2px solid rgba(0, 255, 136, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: #00ff88;
                font-size: 15px;
            }

            QGroupBox::title {
                color: #00ff88;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }

            QTabWidget::pane {
                border: 1px solid rgba(0, 255, 136, 0.3);
                background: #0f0f0f;
            }

            QTabBar::tab {
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 13px;
            }

            QTabBar::tab:selected {
                background: rgba(0, 255, 136, 0.3);
                border: 2px solid #00ff88;
            }

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
                    stop:0 #00ff88, stop:1 rgba(0, 255, 136, 0.6));
                border-radius: 3px;
            }

            QListWidget {
                background: #0a0a0a;
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 4px;
                color: #ffffff;
            }

            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(0, 255, 136, 0.1);
            }

            QListWidget::item:selected {
                background: rgba(0, 255, 136, 0.2);
            }
        """)

        self.init_ui()
        self.load_plugin_list()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_plugin_list)
        self.refresh_timer.start(10000)  # Refresh every 10 seconds

    def init_plugin_manager(self):
        """Initialize the plugin manager"""
        try:
            # Try to import enhanced plugin manager
            from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager
            self.plugin_manager = PluginManager()
            print("✅ Enhanced Plugin Manager initialized")
        except ImportError:
            try:
                # Fallback to basic plugin manager
                from Aetherra.core.plugin_manager import PluginManager
                self.plugin_manager = PluginManager()
                print("✅ Basic Plugin Manager initialized")
            except ImportError:
                print("❌ No plugin manager available")
                self.plugin_manager = None

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("🔧 Clean Plugin Runner")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff88;")

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 12px; color: #ffffff;")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)

        layout.addLayout(header_layout)

        # Main content
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel - Plugin selection and configuration
        left_panel = self.create_left_panel()
        main_splitter.addWidget(left_panel)

        # Right panel - Output and monitoring
        right_panel = self.create_right_panel()
        main_splitter.addWidget(right_panel)

        main_splitter.setSizes([400, 600])
        layout.addWidget(main_splitter)

        # Bottom controls
        controls_layout = QHBoxLayout()

        self.execute_btn = QPushButton("🚀 Execute Plugin")
        self.execute_btn.clicked.connect(self.execute_plugin)
        self.execute_btn.setStyleSheet("font-size: 16px; padding: 12px 24px;")

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)

        self.clear_btn = QPushButton("🧹 Clear Output")
        self.clear_btn.clicked.connect(self.clear_output)

        controls_layout.addWidget(self.execute_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addStretch()

        layout.addLayout(controls_layout)

        self.setLayout(layout)

    def create_left_panel(self) -> QWidget:
        """Create the left panel with plugin selection and configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Plugin selection
        selection_group = QGroupBox("🔍 Plugin Selection")
        selection_layout = QVBoxLayout(selection_group)

        # Plugin dropdown
        plugin_layout = QHBoxLayout()
        plugin_layout.addWidget(QLabel("Plugin:"))

        self.plugin_combo = QComboBox()
        self.plugin_combo.currentTextChanged.connect(self.on_plugin_selected)
        plugin_layout.addWidget(self.plugin_combo)

        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.clicked.connect(self.refresh_plugin_list)
        self.refresh_btn.setMaximumWidth(40)
        plugin_layout.addWidget(self.refresh_btn)

        selection_layout.addLayout(plugin_layout)

        # Plugin info
        self.plugin_info_label = QLabel("Select a plugin to see details")
        self.plugin_info_label.setStyleSheet("color: #cccccc; font-size: 12px; padding: 8px;")
        self.plugin_info_label.setWordWrap(True)
        selection_layout.addWidget(self.plugin_info_label)

        layout.addWidget(selection_group)

        # Plugin parameters
        params_group = QGroupBox("⚙️ Plugin Parameters")
        params_layout = QVBoxLayout(params_group)

        # Scrollable parameter area
        self.params_scroll = QScrollArea()
        self.params_widget = QWidget()
        self.params_layout = QVBoxLayout(self.params_widget)
        self.params_scroll.setWidget(self.params_widget)
        self.params_scroll.setWidgetResizable(True)
        self.params_scroll.setMaximumHeight(200)

        params_layout.addWidget(self.params_scroll)

        layout.addWidget(params_group)

        # Goal context
        context_group = QGroupBox("🎯 Goal Context")
        context_layout = QVBoxLayout(context_group)

        self.goal_input = QTextEdit()
        self.goal_input.setPlaceholderText("Enter goal context or additional parameters (JSON format)...")
        self.goal_input.setMaximumHeight(100)
        context_layout.addWidget(self.goal_input)

        layout.addWidget(context_group)

        # Execution options
        options_group = QGroupBox("🔧 Execution Options")
        options_layout = QVBoxLayout(options_group)

        self.async_checkbox = QCheckBox("Asynchronous execution")
        self.async_checkbox.setChecked(True)
        options_layout.addWidget(self.async_checkbox)

        self.verbose_checkbox = QCheckBox("Verbose output")
        options_layout.addWidget(self.verbose_checkbox)

        layout.addWidget(options_group)

        layout.addStretch()

        return widget

    def create_right_panel(self) -> QWidget:
        """Create the right panel with output and monitoring"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Tabs for different output views
        tabs = QTabWidget()

        # Output tab
        output_tab = QWidget()
        output_layout = QVBoxLayout(output_tab)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Plugin output will appear here...")
        output_layout.addWidget(self.output_text)

        tabs.addTab(output_tab, "📄 Output")

        # Monitoring tab
        monitoring_tab = QWidget()
        monitoring_layout = QVBoxLayout(monitoring_tab)

        # Execution progress
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progress:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        monitoring_layout.addLayout(progress_layout)

        # Execution stats
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setPlaceholderText("Execution statistics will appear here...")
        monitoring_layout.addWidget(self.stats_text)

        tabs.addTab(monitoring_tab, "📊 Monitoring")

        # History tab
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.view_history_item)
        history_layout.addWidget(self.history_list)

        tabs.addTab(history_tab, "📈 History")

        layout.addWidget(tabs)

        return widget

    def load_plugin_list(self):
        """Load the list of available plugins"""
        self.plugin_combo.clear()
        self.plugin_combo.addItem("-- Select Plugin --")

        # Get plugins from discovery
        plugins = self.plugin_discovery.get_plugin_list()

        # Add plugins from plugin manager if available
        if self.plugin_manager:
            if hasattr(self.plugin_manager, 'plugins'):
                for plugin_name in self.plugin_manager.plugins.keys():
                    if plugin_name not in plugins:
                        plugins.append(plugin_name)
            elif hasattr(self.plugin_manager, 'get_available_plugins'):
                available = self.plugin_manager.get_available_plugins()
                for plugin in available:
                    if plugin not in plugins:
                        plugins.append(plugin)

        # Add plugins to combo box
        for plugin in sorted(plugins):
            self.plugin_combo.addItem(plugin)

        self.status_label.setText(f"Found {len(plugins)} plugins")

    def refresh_plugin_list(self):
        """Refresh the plugin list"""
        self.plugin_discovery.discover_plugins()
        self.load_plugin_list()

    def on_plugin_selected(self, plugin_name: str):
        """Handle plugin selection"""
        if plugin_name == "-- Select Plugin --":
            self.plugin_info_label.setText("Select a plugin to see details")
            self.clear_parameters()
            return

        # Get plugin info
        plugin_info = self.plugin_discovery.get_plugin_info(plugin_name)

        if plugin_info:
            info_text = f"<b>{plugin_info['name']}</b><br>"
            info_text += f"<i>{plugin_info['description']}</i><br>"
            info_text += f"Category: {plugin_info['category']}<br>"
            if plugin_info['capabilities']:
                info_text += f"Capabilities: {', '.join(plugin_info['capabilities'])}"

            self.plugin_info_label.setText(info_text)
            self.setup_parameters(plugin_info.get('parameters', {}))
        else:
            self.plugin_info_label.setText(f"Plugin: {plugin_name}\nNo additional information available")
            self.clear_parameters()

    def setup_parameters(self, parameters: Dict[str, str]):
        """Setup parameter input fields"""
        self.clear_parameters()

        if not parameters:
            label = QLabel("No parameters required")
            label.setStyleSheet("color: #cccccc; font-style: italic;")
            self.params_layout.addWidget(label)
            return

        self.param_widgets = {}

        for param_name, param_type in parameters.items():
            param_layout = QHBoxLayout()

            # Parameter label
            label = QLabel(f"{param_name}:")
            label.setMinimumWidth(100)
            param_layout.addWidget(label)

            # Parameter input
            if param_type.lower() in ['int', 'integer']:
                widget = QSpinBox()
                widget.setRange(-999999, 999999)
            elif param_type.lower() in ['float', 'number']:
                widget = QLineEdit()
                widget.setPlaceholderText("0.0")
            elif param_type.lower() == 'bool':
                widget = QCheckBox()
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(f"Enter {param_name}...")

            param_layout.addWidget(widget)
            self.params_layout.addLayout(param_layout)

            self.param_widgets[param_name] = widget

    def clear_parameters(self):
        """Clear parameter input fields"""
        while self.params_layout.count():
            child = self.params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                while child.layout().count():
                    subchild = child.layout().takeAt(0)
                    if subchild.widget():
                        subchild.widget().deleteLater()

        self.param_widgets = {}

    def execute_plugin(self):
        """Execute the selected plugin"""
        plugin_name = self.plugin_combo.currentText()

        if plugin_name == "-- Select Plugin --":
            QMessageBox.warning(self, "No Plugin Selected", "Please select a plugin to execute.")
            return

        if not self.plugin_manager:
            QMessageBox.critical(self, "Plugin Manager Error", "Plugin manager not available.")
            return

        # Collect parameters
        params = {}

        # Get parameters from input fields
        if hasattr(self, 'param_widgets'):
            for param_name, widget in self.param_widgets.items():
                if isinstance(widget, QSpinBox):
                    params[param_name] = widget.value()
                elif isinstance(widget, QCheckBox):
                    params[param_name] = widget.isChecked()
                elif isinstance(widget, QLineEdit):
                    value = widget.text()
                    if value:
                        params[param_name] = value

        # Add goal context if provided
        goal_context = self.goal_input.toPlainText().strip()
        if goal_context:
            try:
                goal_data = json.loads(goal_context)
                params.update(goal_data)
            except json.JSONDecodeError:
                params['goal_context'] = goal_context

        # Execute plugin
        if self.async_checkbox.isChecked():
            self.execute_async(plugin_name, params)
        else:
            self.execute_sync(plugin_name, params)

    def execute_async(self, plugin_name: str, params: Dict[str, Any]):
        """Execute plugin asynchronously"""
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        self.output_text.clear()
        self.output_text.append(f"🚀 Executing {plugin_name} asynchronously...")
        self.output_text.append(f"📋 Parameters: {json.dumps(params, indent=2)}")
        self.output_text.append("=" * 50)

        # Create and start execution thread
        self.execution_thread = PluginExecutionThread(self.plugin_manager, plugin_name, params)
        self.execution_thread.execution_started.connect(self.on_execution_started)
        self.execution_thread.execution_finished.connect(self.on_execution_finished)
        self.execution_thread.execution_error.connect(self.on_execution_error)
        self.execution_thread.start()

        # Update stats
        self.update_stats(f"Executing {plugin_name}...", params)

    def execute_sync(self, plugin_name: str, params: Dict[str, Any]):
        """Execute plugin synchronously"""
        self.execute_btn.setEnabled(False)
        self.output_text.clear()
        self.output_text.append(f"🚀 Executing {plugin_name} synchronously...")
        self.output_text.append(f"📋 Parameters: {json.dumps(params, indent=2)}")
        self.output_text.append("=" * 50)

        try:
            start_time = time.time()

            # Execute plugin
            if hasattr(self.plugin_manager, 'execute_plugin'):
                result = self.plugin_manager.execute_plugin(plugin_name, **params)
            else:
                # Fallback execution
                if plugin_name in self.plugin_manager.plugins:
                    plugin = self.plugin_manager.plugins[plugin_name]
                    if hasattr(plugin, 'execute'):
                        result = plugin.execute(**params)
                    elif hasattr(plugin, 'main'):
                        result = plugin.main(**params)
                    else:
                        result = "Plugin has no execute() or main() method"
                else:
                    result = f"Plugin '{plugin_name}' not found"

            execution_time = time.time() - start_time

            # Display result
            self.output_text.append(f"✅ Execution completed in {execution_time:.2f} seconds")
            self.output_text.append(f"📤 Result: {result}")

            # Add to history
            self.add_to_history(plugin_name, params, result, execution_time, None)

            # Update stats
            self.update_stats(f"Completed {plugin_name}", params, execution_time)

        except Exception as e:
            error_msg = f"❌ Error executing {plugin_name}: {str(e)}"
            self.output_text.append(error_msg)
            self.output_text.append(f"🔍 Traceback:\n{traceback.format_exc()}")

            # Add to history
            self.add_to_history(plugin_name, params, None, None, str(e))

            # Update stats
            self.update_stats(f"Error in {plugin_name}", params, None, str(e))

        finally:
            self.execute_btn.setEnabled(True)

    def on_execution_started(self, plugin_name: str):
        """Handle execution started"""
        self.status_label.setText(f"Executing {plugin_name}...")

    def on_execution_finished(self, plugin_name: str, result: Any):
        """Handle execution finished"""
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.output_text.append(f"✅ Execution completed")
        self.output_text.append(f"📤 Result: {result}")

        # Add to history
        self.add_to_history(plugin_name, {}, result, None, None)

        self.status_label.setText(f"Completed {plugin_name}")

    def on_execution_error(self, plugin_name: str, error: str):
        """Handle execution error"""
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        error_msg = f"❌ Error executing {plugin_name}: {error}"
        self.output_text.append(error_msg)

        # Add to history
        self.add_to_history(plugin_name, {}, None, None, error)

        self.status_label.setText(f"Error in {plugin_name}")

    def stop_execution(self):
        """Stop plugin execution"""
        if self.execution_thread and self.execution_thread.isRunning():
            self.execution_thread.terminate()
            self.execution_thread.wait()

        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.output_text.append("⏹️ Execution stopped by user")
        self.status_label.setText("Execution stopped")

    def clear_output(self):
        """Clear the output text"""
        self.output_text.clear()
        self.stats_text.clear()

    def add_to_history(self, plugin_name: str, params: Dict[str, Any], result: Any, execution_time: Optional[float], error: Optional[str]):
        """Add execution to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        history_item = {
            'timestamp': timestamp,
            'plugin': plugin_name,
            'params': params,
            'result': result,
            'execution_time': execution_time,
            'error': error
        }

        self.execution_history.append(history_item)

        # Update history list
        status = "✅" if not error else "❌"
        time_str = f"({execution_time:.2f}s)" if execution_time else ""

        list_item = QListWidgetItem(f"{status} {timestamp} - {plugin_name} {time_str}")
        list_item.setData(Qt.UserRole, history_item)
        self.history_list.addItem(list_item)

        # Scroll to bottom
        self.history_list.scrollToBottom()

    def view_history_item(self, item: QListWidgetItem):
        """View details of a history item"""
        history_data = item.data(Qt.UserRole)

        details = f"Plugin: {history_data['plugin']}\n"
        details += f"Timestamp: {history_data['timestamp']}\n"
        details += f"Parameters: {json.dumps(history_data['params'], indent=2)}\n"

        if history_data['error']:
            details += f"Error: {history_data['error']}\n"
        else:
            details += f"Result: {history_data['result']}\n"
            if history_data['execution_time']:
                details += f"Execution Time: {history_data['execution_time']:.2f} seconds\n"

        QMessageBox.information(self, "Execution Details", details)

    def update_stats(self, status: str, params: Dict[str, Any], execution_time: Optional[float] = None, error: Optional[str] = None):
        """Update execution statistics"""
        stats = f"Status: {status}\n"
        stats += f"Parameters: {len(params)} provided\n"
        stats += f"History: {len(self.execution_history)} executions\n"

        if execution_time:
            stats += f"Last Execution Time: {execution_time:.2f} seconds\n"

        if error:
            stats += f"Last Error: {error}\n"

        # Calculate success rate
        if self.execution_history:
            successful = len([h for h in self.execution_history if not h['error']])
            success_rate = (successful / len(self.execution_history)) * 100
            stats += f"Success Rate: {success_rate:.1f}%\n"

        self.stats_text.setText(stats)


def main():
    """Main application entry point"""
    if not HAS_PYSIDE6:
        print("❌ PySide6 required for Clean Plugin Runner")
        return

    app = QApplication(sys.argv)

    # Create and show the plugin runner
    runner = CleanPluginRunner()
    runner.setWindowTitle("🔧 Clean Plugin Runner")
    runner.resize(1200, 800)
    runner.show()

    # Show welcome message
    QMessageBox.information(runner, "🔧 Clean Plugin Runner",
                          "Welcome to the Clean Plugin Runner!\n\n"
                          "Features:\n"
                          "🔍 Automatic plugin discovery\n"
                          "⚙️ Dynamic parameter configuration\n"
                          "🚀 Async/sync execution modes\n"
                          "📊 Real-time monitoring\n"
                          "📈 Execution history\n"
                          "🎯 Goal context integration\n\n"
                          "Select a plugin from the dropdown to get started!")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
