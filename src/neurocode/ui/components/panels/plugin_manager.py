#!/usr/bin/env python3
"""
Plugin Manager Panel
===================

Modular component for managing plugins and extensions.
"""

import os
from typing import Any, Dict

from ..cards import ModernCard
from ..theme import ModernTheme
from ..utils.qt_imports import (
    QCheckBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    Qt,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PluginManagerPanel(ModernCard):
    """Panel for managing plugins and extensions"""

    def __init__(self, parent=None):
        super().__init__("🔌 Plugin Manager", parent)
        self.plugins = []
        self.plugins_dir = "plugins"
        self.icon_path = self._get_icon_path()
        self.init_ui()
        self.load_plugins()

    def _get_icon_path(self):
        """Get the NeuroCode icon path for plugin branding"""
        from pathlib import Path

        # Try to find the icon in the assets directory
        icon_path = (
            Path(__file__)
            .parent.parent.parent.parent.parent
            / "assets"
            / "images"
            / "neurocode-icon.png"
        )
        if icon_path.exists():
            return str(icon_path)
        return ""

    def init_ui(self):
        """Initialize the user interface"""
        # Plugin list
        self.plugin_list = QListWidget()
        self.plugin_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {ModernTheme.BORDER};
            }}
            QListWidget::item:selected {{
                background-color: {ModernTheme.PRIMARY};
            }}
        """)
        self.plugin_list.itemClicked.connect(self.show_plugin_details)
        self.add_widget(self.plugin_list)

        # Plugin details
        self.plugin_details = QTextEdit()
        self.plugin_details.setMaximumHeight(100)
        self.plugin_details.setPlaceholderText("Select a plugin to view details...")
        self.plugin_details.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
                border-radius: 4px;
                color: {ModernTheme.TEXT_SECONDARY};
                font-size: 11px;
            }}
        """)
        self.add_widget(self.plugin_details)

        # Plugin controls
        controls_layout = QVBoxLayout()

        # Enable/Disable checkbox
        self.enable_checkbox = QCheckBox("Enable Plugin")
        self.enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {ModernTheme.TEXT_PRIMARY};
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {ModernTheme.SUCCESS};
                border: 1px solid {ModernTheme.SUCCESS};
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {ModernTheme.SURFACE};
                border: 1px solid {ModernTheme.BORDER};
            }}
        """)
        self.enable_checkbox.stateChanged.connect(self.toggle_plugin)
        self.enable_checkbox.setEnabled(False)
        controls_layout.addWidget(self.enable_checkbox)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.install_btn = QPushButton("📦 Install")
        self.install_btn.clicked.connect(self.install_plugin)
        buttons_layout.addWidget(self.install_btn)

        self.uninstall_btn = QPushButton("🗑️ Uninstall")
        self.uninstall_btn.clicked.connect(self.uninstall_plugin)
        self.uninstall_btn.setEnabled(False)
        buttons_layout.addWidget(self.uninstall_btn)

        self.reload_btn = QPushButton("🔄 Reload")
        self.reload_btn.clicked.connect(self.reload_plugin)
        self.reload_btn.setEnabled(False)
        buttons_layout.addWidget(self.reload_btn)

        buttons_layout.addStretch()

        self.refresh_btn = QPushButton("🔍 Scan")
        self.refresh_btn.clicked.connect(self.scan_plugins)
        buttons_layout.addWidget(self.refresh_btn)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        controls_layout.addWidget(buttons_widget)

        controls_widget = QWidget()
        controls_widget.setLayout(controls_layout)
        self.add_widget(controls_widget)

    def load_plugins(self):
        """Load available plugins"""
        self.plugins = []

        # Create plugins directory if it doesn't exist
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        # Add some default/example plugins
        default_plugins = [
            {
                "name": "AI Assistant",
                "description": "Enhanced AI interaction capabilities",
                "version": "1.0.0",
                "author": "Neuroplex Team",
                "enabled": True,
                "status": "installed",
                "file": "ai_assistant.py",
            },
            {
                "name": "Memory Enhancer",
                "description": "Advanced memory management and visualization",
                "version": "1.2.0",
                "author": "Neuroplex Team",
                "enabled": True,
                "status": "installed",
                "file": "memory_enhancer.py",
            },
            {
                "name": "Code Generator",
                "description": "Automatic code generation from natural language",
                "version": "0.9.0",
                "author": "Community",
                "enabled": False,
                "status": "available",
                "file": "code_generator.py",
            },
            {
                "name": "Theme Manager",
                "description": "Custom theme and appearance manager",
                "version": "1.1.0",
                "author": "Community",
                "enabled": False,
                "status": "available",
                "file": "theme_manager.py",
            },
        ]

        # Scan for actual plugin files
        if os.path.exists(self.plugins_dir):
            for file in os.listdir(self.plugins_dir):
                if file.endswith(".py") and not file.startswith("__"):
                    plugin_path = os.path.join(self.plugins_dir, file)
                    plugin_info = self.parse_plugin_info(plugin_path)
                    if plugin_info:
                        self.plugins.append(plugin_info)

        # Add defaults if no plugins found
        if not self.plugins:
            self.plugins = default_plugins

        self.update_plugin_display()

    def parse_plugin_info(self, plugin_path: str) -> Dict[str, Any]:
        """Parse plugin metadata from file"""
        try:
            with open(plugin_path) as f:
                content = f.read()

            # Extract basic info from docstring or comments
            plugin_info = {
                "name": os.path.basename(plugin_path).replace(".py", "").title(),
                "description": "Plugin loaded from file",
                "version": "1.0.0",
                "author": "Unknown",
                "enabled": False,
                "status": "installed",
                "file": os.path.basename(plugin_path),
            }

            # Try to extract metadata from docstring
            if '"""' in content:
                docstring = content.split('"""')[1]
                lines = docstring.split("\n")
                for line in lines:
                    if "Name:" in line:
                        plugin_info["name"] = line.split("Name:")[1].strip()
                    elif "Description:" in line:
                        plugin_info["description"] = line.split("Description:")[1].strip()
                    elif "Version:" in line:
                        plugin_info["version"] = line.split("Version:")[1].strip()
                    elif "Author:" in line:
                        plugin_info["author"] = line.split("Author:")[1].strip()

            return plugin_info

        except Exception as e:
            print(f"Error parsing plugin {plugin_path}: {e}")
            return None

    def update_plugin_display(self):
        """Update the plugin list display"""
        self.plugin_list.clear()

        for plugin in self.plugins:
            status_icon = "✅" if plugin.get("enabled") else "⚪"
            install_icon = "📦" if plugin.get("status") == "installed" else "📥"

            item_text = f"{status_icon} {install_icon} {plugin.get('name', 'Unknown Plugin')}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, plugin)

            # Color code by status
            if plugin.get("enabled"):
                # Use QColor instead of string
                from ..utils.qt_imports import QBrush

                item.setForeground(QBrush(ModernTheme.SUCCESS))
            elif plugin.get("status") == "installed":
                from ..utils.qt_imports import QBrush

                item.setForeground(QBrush(ModernTheme.TEXT_SECONDARY))
            else:
                from ..utils.qt_imports import QBrush

                item.setForeground(QBrush(ModernTheme.WARNING))

            self.plugin_list.addItem(item)

    def show_plugin_details(self, item):
        """Show details for selected plugin"""
        plugin = item.data(Qt.ItemDataRole.UserRole)
        if plugin:
            details = f"""Name: {plugin.get("name", "N/A")}
Description: {plugin.get("description", "N/A")}
Version: {plugin.get("version", "N/A")}
Author: {plugin.get("author", "N/A")}
Status: {plugin.get("status", "N/A")}
File: {plugin.get("file", "N/A")}"""

            self.plugin_details.setText(details)

            # Update controls
            self.enable_checkbox.setChecked(plugin.get("enabled", False))
            self.enable_checkbox.setEnabled(plugin.get("status") == "installed")
            self.uninstall_btn.setEnabled(plugin.get("status") == "installed")
            self.reload_btn.setEnabled(plugin.get("enabled", False))

    def toggle_plugin(self, state):
        """Toggle plugin enabled state"""
        current_item = self.plugin_list.currentItem()
        if current_item:
            plugin = current_item.data(Qt.ItemDataRole.UserRole)
            plugin["enabled"] = state == Qt.CheckState.Checked.value
            self.update_plugin_display()

    def install_plugin(self):
        """Install a new plugin"""
        from ..utils.qt_imports import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Install Plugin", "", "Python Files (*.py)"
        )

        if file_path:
            # Copy plugin to plugins directory
            import shutil

            plugin_name = os.path.basename(file_path)
            dest_path = os.path.join(self.plugins_dir, plugin_name)

            try:
                shutil.copy2(file_path, dest_path)
                self.scan_plugins()
            except Exception as e:
                print(f"Error installing plugin: {e}")

    def uninstall_plugin(self):
        """Uninstall selected plugin"""
        from ..utils.qt_imports import QMessageBox

        current_item = self.plugin_list.currentItem()
        if current_item:
            plugin = current_item.data(Qt.ItemDataRole.UserRole)

            reply = QMessageBox.question(
                self,
                "Uninstall Plugin",
                f'Are you sure you want to uninstall "{plugin.get("name", "this plugin")}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Remove plugin file
                plugin_file = plugin.get("file")
                if plugin_file:
                    plugin_path = os.path.join(self.plugins_dir, plugin_file)
                    try:
                        if os.path.exists(plugin_path):
                            os.remove(plugin_path)
                        self.scan_plugins()
                    except Exception as e:
                        print(f"Error uninstalling plugin: {e}")

    def reload_plugin(self):
        """Reload selected plugin"""
        current_item = self.plugin_list.currentItem()
        if current_item:
            plugin = current_item.data(Qt.ItemDataRole.UserRole)
            print(f"Reloading plugin: {plugin.get('name', 'Unknown')}")
            # In a real implementation, this would reload the plugin module

    def scan_plugins(self):
        """Scan for available plugins"""
        self.load_plugins()

    def get_enabled_plugins(self) -> list:
        """Get list of enabled plugins"""
        return [plugin for plugin in self.plugins if plugin.get("enabled", False)]
