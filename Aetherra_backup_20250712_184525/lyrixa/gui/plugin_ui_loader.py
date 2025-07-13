"""
PluginUIManager: Manages the dynamic loading and rendering of plugin-driven UI components.
"""

import importlib.util
import json
import os
import tempfile
import zipfile
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests


class PluginSchema:
    """Defines the schema for plugins."""

    def __init__(
        self, name: str, version: str, author: str, description: str, ui_component: Any
    ):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.ui_component = ui_component

    def validate(self) -> bool:
        """Validate the plugin schema."""
        required_fields = [self.name, self.version, self.author, self.ui_component]
        return all(required_fields)


class PluginUIManager:
    def __init__(self):
        """Initialize the PluginUIManager with default settings."""
        self.plugins = []  # List to store registered plugins
        self.zones = {
            "suggestion_panel": None,
            "analytics_panel": None,
            "plugin_slot_left": None,
            "plugin_slot_right": None,
        }
        self.theme = "light"  # Default theme
        self.mode = "Simple"  # Default mode
        self.viewports = {}  # Dictionary to store viewport configurations

    def register_plugin(self, plugin):
        """Register a new plugin to the UI manager."""
        self.plugins.append(plugin)

    def set_zone(self, zone_name, plugin):
        """Assign a plugin to a specific zone."""
        if zone_name in self.zones:
            self.zones[zone_name] = plugin
        else:
            raise ValueError(f"Invalid zone name: {zone_name}")

    def switch_theme(self, theme):
        """Switch the UI theme (light/dark)."""
        if theme in ["light", "dark"]:
            self.theme = theme
            print(f"Theme switched to: {self.theme}")
            self.notify_plugins_of_theme_change()
        else:
            raise ValueError("Theme must be 'light' or 'dark'")

    def get_theme_styles(self):
        """Get CSS styles for the current theme."""
        if self.theme == "dark":
            return {
                "background": "#2b2b2b",
                "text": "#ffffff",
                "border": "#555555",
                "accent": "#0078d4",
                "hover": "#404040",
                "tab_style": """
                    QTabWidget::pane {
                        border: 1px solid #555555;
                        background-color: #2b2b2b;
                    }
                    QTabBar::tab {
                        background-color: #404040;
                        color: #ffffff;
                        border: 1px solid #555555;
                        padding: 8px 16px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background-color: #0078d4;
                        color: #ffffff;
                    }
                    QTabBar::tab:hover {
                        background-color: #505050;
                    }
                """,
                "text_style": """
                    QTextEdit, QLabel, QPushButton {
                        background-color: #2b2b2b;
                        color: #ffffff;
                        border: 1px solid #555555;
                    }
                    QPushButton:hover {
                        background-color: #404040;
                    }
                    QPushButton:pressed {
                        background-color: #0078d4;
                    }
                """,
            }
        else:  # light theme
            return {
                "background": "#ffffff",
                "text": "#000000",
                "border": "#cccccc",
                "accent": "#0078d4",
                "hover": "#f0f0f0",
                "tab_style": """
                    QTabWidget::pane {
                        border: 1px solid #cccccc;
                        background-color: #ffffff;
                    }
                    QTabBar::tab {
                        background-color: #f0f0f0;
                        color: #000000;
                        border: 1px solid #cccccc;
                        padding: 8px 16px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background-color: #0078d4;
                        color: #ffffff;
                    }
                    QTabBar::tab:hover {
                        background-color: #e0e0e0;
                    }
                """,
                "text_style": """
                    QTextEdit, QLabel, QPushButton {
                        background-color: #ffffff;
                        color: #000000;
                        border: 1px solid #cccccc;
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                    }
                    QPushButton:pressed {
                        background-color: #0078d4;
                        color: #ffffff;
                    }
                """,
            }

    def apply_theme_to_widget(self, widget):
        """Apply current theme styles to a widget."""
        styles = self.get_theme_styles()

        # Combine all styles
        full_style = styles["tab_style"] + "\n" + styles["text_style"]

        # Apply to widget
        if hasattr(widget, "setStyleSheet"):
            widget.setStyleSheet(full_style)

        return styles

    def create_themed_widget(self, widget_class, *args, **kwargs):
        """Create a widget with theme applied."""
        widget = widget_class(*args, **kwargs)
        self.apply_theme_to_widget(widget)
        return widget

    def notify_plugins_of_theme_change(self):
        """Notify all plugins about the theme change."""
        styles = self.get_theme_styles()
        for plugin in self.plugins:
            if hasattr(plugin, "on_theme_change"):
                plugin.on_theme_change(self.theme, styles)
            elif hasattr(plugin, "apply_theme"):
                plugin.apply_theme(styles)

    def initialize_layout(self):
        """Initialize the layout with default zones."""
        print("Initializing layout with default zones...")
        for zone in self.zones:
            print(f"Zone initialized: {zone}")

    def render(self):
        """Render the UI with the current plugins and theme."""
        print(f"Rendering UI with theme: {self.theme}")
        for zone, plugin in self.zones.items():
            if plugin:
                print(f"Rendering plugin '{plugin.name}' in {zone}")
            else:
                print(f"No plugin assigned to {zone}")

    def load_plugin(self, plugin_data: Dict[str, Any]):
        """Load a plugin based on the provided schema."""
        plugin = PluginSchema(**plugin_data)
        if plugin.validate():
            self.register_plugin(plugin)
        else:
            raise ValueError("Invalid plugin schema")

    def switch_mode(self, mode):
        """Switch the UI mode (e.g., Developer, Simple, Live Agent)."""
        valid_modes = ["Developer", "Simple", "Live Agent"]
        if mode in valid_modes:
            self.mode = mode
            print(f"Mode switched to: {self.mode}")
            self.update_layout_for_mode()
        else:
            raise ValueError(f"Invalid mode. Valid modes are: {valid_modes}")

    def update_layout_for_mode(self):
        """Update the layout based on the current mode."""
        print(f"Updating layout for mode: {self.mode}")
        # Example: Adjust zones or plugins based on the mode
        if self.mode == "Developer":
            self.zones["analytics_panel"] = None  # Example adjustment
        elif self.mode == "Live Agent":
            self.zones["plugin_slot_left"] = None  # Example adjustment
        # Add more adjustments as needed

    def configure_viewports(self, viewports):
        """Configure dynamic viewports for the UI."""
        self.viewports = viewports
        print(f"Viewports configured: {self.viewports}")

    def update_viewport(self, viewport_name, configuration):
        """Update a specific viewport's configuration."""
        if viewport_name in self.viewports:
            self.viewports[viewport_name] = configuration
            print(f"Viewport '{viewport_name}' updated: {configuration}")
        else:
            raise ValueError(f"Viewport '{viewport_name}' does not exist.")

    def get_system_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the Lyrixa Plugin UI system."""
        summary = {
            "system_info": {
                "name": "Lyrixa Plugin UI System",
                "version": "1.0.0",
                "theme": self.theme,
                "mode": self.mode,
                "total_plugins": len(self.plugins),
                "total_zones": len(self.zones),
                "configured_viewports": len(self.viewports),
            },
            "plugins": [],
            "zones": {},
            "viewports": self.viewports.copy(),
            "capabilities": [
                "Dynamic plugin loading and management",
                "Theme switching (light/dark)",
                "Mode switching (Developer/Simple/Live Agent)",
                "Plugin zone assignment and management",
                "Viewport configuration",
                "Real-time theme updates to plugins",
            ],
        }

        # Add plugin details
        for plugin in self.plugins:
            if hasattr(plugin, "name") and hasattr(plugin, "version"):
                plugin_info = {
                    "name": plugin.name,
                    "version": plugin.version,
                    "author": getattr(plugin, "author", "Unknown"),
                    "description": getattr(plugin, "description", "No description"),
                    "has_ui_component": hasattr(plugin, "ui_component"),
                    "supports_themes": hasattr(plugin, "apply_theme"),
                }
            else:
                # Handle dict-based plugins
                plugin_info = {
                    "name": plugin.get("name", "Unknown"),
                    "version": plugin.get("version", "Unknown"),
                    "author": plugin.get("author", "Unknown"),
                    "description": plugin.get("description", "No description"),
                    "has_ui_component": "ui_component" in plugin,
                    "supports_themes": False,
                }
            summary["plugins"].append(plugin_info)

        # Add zone assignments
        for zone_name, assigned_plugin in self.zones.items():
            if assigned_plugin:
                if hasattr(assigned_plugin, "name"):
                    summary["zones"][zone_name] = assigned_plugin.name
                else:
                    summary["zones"][zone_name] = assigned_plugin.get(
                        "name", "Unknown Plugin"
                    )
            else:
                summary["zones"][zone_name] = "Empty"

        return summary

    def print_system_summary(self):
        """Print a formatted system summary to console."""
        summary = self.get_system_summary()

        print("=" * 60)
        print("🎙️ LYRIXA PLUGIN UI SYSTEM SUMMARY")
        print("=" * 60)

        # System Info
        info = summary["system_info"]
        print(f"📊 System: {info['name']} v{info['version']}")
        print(f"🎨 Theme: {info['theme'].title()}")
        print(f"🎯 Mode: {info['mode']}")
        print(f"🧩 Plugins: {info['total_plugins']} loaded")
        print(f"📍 Zones: {info['total_zones']} configured")
        print(f"📱 Viewports: {info['configured_viewports']} configured")

        # Plugins
        if summary["plugins"]:
            print("\n🧩 LOADED PLUGINS:")
            for i, plugin in enumerate(summary["plugins"], 1):
                print(f"  {i}. {plugin['name']} v{plugin['version']}")
                print(f"     Author: {plugin['author']}")
                print(f"     Description: {plugin['description']}")
                print(
                    f"     UI Component: {'✅' if plugin['has_ui_component'] else '❌'}"
                )
                print(
                    f"     Theme Support: {'✅' if plugin['supports_themes'] else '❌'}"
                )
                print()
        else:
            print("\n🧩 No plugins currently loaded")

        # Zone Assignments
        print("📍 ZONE ASSIGNMENTS:")
        for zone, assignment in summary["zones"].items():
            status = "✅" if assignment != "Empty" else "⭕"
            print(f"  {status} {zone}: {assignment}")

        # Capabilities
        print("\n🚀 SYSTEM CAPABILITIES:")
        for capability in summary["capabilities"]:
            print(f"  ✅ {capability}")

        print("=" * 60)
        return summary

    def install_remote_plugin(
        self, source_url: str, plugin_name: str = None
    ) -> Dict[str, Any]:
        """Install a plugin from a remote source (Git, marketplace, etc.)."""
        try:
            result = {
                "status": "success",
                "plugin_name": plugin_name,
                "source_url": source_url,
                "installed_at": datetime.now().isoformat(),
            }

            # Determine source type
            parsed_url = urlparse(source_url)

            if "github.com" in parsed_url.netloc:
                # GitHub repository
                result.update(self._install_from_github(source_url, plugin_name))
            elif source_url.endswith(".zip"):
                # Direct ZIP download
                result.update(self._install_from_zip(source_url, plugin_name))
            elif source_url.endswith(".py"):
                # Direct Python file
                result.update(self._install_from_python_file(source_url, plugin_name))
            else:
                # Try as plugin marketplace URL
                result.update(self._install_from_marketplace(source_url, plugin_name))

            return result

        except ImportError:
            return {
                "status": "error",
                "message": "requests library required for remote plugin installation",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _install_from_github(
        self, github_url: str, plugin_name: str = None
    ) -> Dict[str, Any]:
        """Install plugin from GitHub repository."""

        # Convert GitHub URL to API URL for downloading
        if github_url.endswith(".git"):
            github_url = github_url[:-4]

        # Extract owner/repo from URL
        parts = github_url.split("/")
        owner, repo = parts[-2], parts[-1]

        # Download as ZIP
        zip_url = f"https://github.com/{owner}/{repo}/archive/main.zip"

        try:
            response = requests.get(zip_url)
            response.raise_for_status()

            # Save and extract
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            with zipfile.ZipFile(tmp_file_path, "r") as zip_ref:
                # Extract to temporary directory
                with tempfile.TemporaryDirectory() as extract_dir:
                    zip_ref.extractall(extract_dir)

                    # Look for plugin files
                    plugin_files = self._find_plugin_files(extract_dir)

                    if plugin_files:
                        # Load and register the plugin
                        plugin_data = self._load_plugin_from_files(plugin_files)
                        if plugin_data:
                            self.register_plugin(plugin_data)
                            return {
                                "plugin_loaded": True,
                                "plugin_name": plugin_data.get("name", plugin_name),
                                "files_found": len(plugin_files),
                            }

            return {"plugin_loaded": False, "message": "No valid plugin files found"}

        except Exception as e:
            return {
                "plugin_loaded": False,
                "message": f"GitHub installation failed: {str(e)}",
            }

    def _install_from_zip(
        self, zip_url: str, plugin_name: str = None
    ) -> Dict[str, Any]:
        """Install plugin from ZIP file."""

        try:
            response = requests.get(zip_url)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            with zipfile.ZipFile(tmp_file_path, "r") as zip_ref:
                with tempfile.TemporaryDirectory() as extract_dir:
                    zip_ref.extractall(extract_dir)
                    plugin_files = self._find_plugin_files(extract_dir)

                    if plugin_files:
                        plugin_data = self._load_plugin_from_files(plugin_files)
                        if plugin_data:
                            self.register_plugin(plugin_data)
                            return {
                                "plugin_loaded": True,
                                "plugin_name": plugin_data.get("name", plugin_name),
                            }

            return {
                "plugin_loaded": False,
                "message": "No valid plugin files found in ZIP",
            }

        except Exception as e:
            return {
                "plugin_loaded": False,
                "message": f"ZIP installation failed: {str(e)}",
            }

    def _install_from_python_file(
        self, file_url: str, plugin_name: str = None
    ) -> Dict[str, Any]:
        """Install plugin from a single Python file."""

        try:
            response = requests.get(file_url)
            response.raise_for_status()

            # Save to temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp_file:
                tmp_file.write(response.text)
                tmp_file_path = tmp_file.name

            # Load the module
            spec = importlib.util.spec_from_file_location(
                "remote_plugin", tmp_file_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for plugin_data
                if hasattr(module, "plugin_data"):
                    plugin_data = module.plugin_data
                    self.register_plugin(plugin_data)
                    return {
                        "plugin_loaded": True,
                        "plugin_name": plugin_data.get("name", plugin_name),
                    }

            return {
                "plugin_loaded": False,
                "message": "No plugin_data found in Python file",
            }

        except Exception as e:
            return {
                "plugin_loaded": False,
                "message": f"Python file installation failed: {str(e)}",
            }

    def _install_from_marketplace(
        self, marketplace_url: str, plugin_name: str = None
    ) -> Dict[str, Any]:
        """Install plugin from plugin marketplace."""

        try:
            # Fetch plugin metadata from marketplace
            response = requests.get(f"{marketplace_url}/api/plugin/{plugin_name}")
            response.raise_for_status()

            plugin_info = response.json()
            download_url = plugin_info.get("download_url")

            if download_url:
                if download_url.endswith(".zip"):
                    return self._install_from_zip(download_url, plugin_name)
                elif download_url.endswith(".py"):
                    return self._install_from_python_file(download_url, plugin_name)

            return {
                "plugin_loaded": False,
                "message": "Invalid download URL from marketplace",
            }

        except Exception as e:
            return {
                "plugin_loaded": False,
                "message": f"Marketplace installation failed: {str(e)}",
            }

    def _find_plugin_files(self, directory: str) -> List[str]:
        """Find plugin files in a directory."""
        plugin_files = []

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and (
                    "plugin" in file.lower() or file == "__init__.py"
                ):
                    plugin_files.append(os.path.join(root, file))

        return plugin_files

    def _load_plugin_from_files(self, file_paths: List[str]) -> Dict:
        """Load plugin data from plugin files."""

        for file_path in file_paths:
            try:
                spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    if hasattr(module, "plugin_data"):
                        return module.plugin_data

            except Exception as e:
                print(f"Failed to load plugin from {file_path}: {e}")
                continue

        return {}

    def list_remote_sources(self) -> List[Dict[str, str]]:
        """List configured remote plugin sources."""
        return [
            {
                "name": "GitHub",
                "type": "git_repository",
                "description": "Install plugins from GitHub repositories",
                "example_url": "https://github.com/user/lyrixa-plugin",
            },
            {
                "name": "Plugin Marketplace",
                "type": "marketplace",
                "description": "Official Lyrixa plugin marketplace",
                "example_url": "https://plugins.lyrixa.ai/plugin-name",
            },
            {
                "name": "Direct Download",
                "type": "direct",
                "description": "Install from direct ZIP or Python file URLs",
                "example_url": "https://example.com/plugin.zip",
            },
        ]

    def update_plugin(self, plugin_name: str, source_url: str = None) -> Dict[str, Any]:
        """Update an installed plugin from its original source."""
        # Find the plugin
        existing_plugin = None
        for plugin in self.plugins:
            if getattr(plugin, "name", plugin.get("name")) == plugin_name:
                existing_plugin = plugin
                break

        if not existing_plugin:
            return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}

        # Get source URL from plugin metadata or use provided URL
        if not source_url:
            source_url = getattr(
                existing_plugin, "source_url", existing_plugin.get("source_url")
            )

        if not source_url:
            return {"status": "error", "message": "No source URL available for update"}

        # Remove existing plugin
        self.plugins.remove(existing_plugin)

        # Reinstall from source
        result = self.install_remote_plugin(source_url, plugin_name)
        result["action"] = "update"

        return result

    def load_flagship_plugins(self):
        """Load all flagship plugins from the lyrixa.plugins module."""
        flagship_plugins = []
        try:
            from lyrixa.plugins import (
                assistant_trainer_plugin,
                plugin_generator_plugin,
                workflow_builder_plugin,
            )

            # Load workflow builder
            if hasattr(workflow_builder_plugin, "plugin_data"):
                self.register_plugin(workflow_builder_plugin.plugin_data)
                flagship_plugins.append(workflow_builder_plugin.plugin_data)
                print("✅ Workflow Builder Plugin loaded")

            # Load assistant trainer
            if hasattr(assistant_trainer_plugin, "plugin_data"):
                self.register_plugin(assistant_trainer_plugin.plugin_data)
                flagship_plugins.append(assistant_trainer_plugin.plugin_data)
                print("✅ Assistant Trainer Plugin loaded")

            # Load plugin generator
            if hasattr(plugin_generator_plugin, "plugin_data"):
                self.register_plugin(plugin_generator_plugin.plugin_data)
                flagship_plugins.append(plugin_generator_plugin.plugin_data)
                print("✅ Plugin Generator Plugin loaded")

            return flagship_plugins

        except Exception as e:
            print(f"⚠️ Could not load flagship plugins: {e}")
            return []

    def get_plugin_generator(self):
        """Get the plugin generator plugin if available."""
        for plugin in self.plugins:
            plugin_name = getattr(plugin, "name", plugin.get("name", ""))
            if (
                "generator" in plugin_name.lower()
                or "plugingenerator" in plugin_name.lower()
            ):
                return plugin
        return None

    def create_plugin_from_template(
        self, template_type: str, plugin_name: str, description: str = ""
    ):
        """Create a new plugin using the plugin generator."""
        generator = self.get_plugin_generator()
        if not generator:
            return {"status": "error", "message": "Plugin Generator not available"}

        try:
            # If the plugin has a create method, use it
            if hasattr(generator, "create_plugin"):
                result = generator.create_plugin(
                    template_type, plugin_name, description
                )
                return {
                    "status": "success",
                    "plugin": result,
                    "message": f"Plugin '{plugin_name}' created successfully",
                }

            # Fallback: create a basic plugin structure
            basic_plugin = {
                "name": plugin_name,
                "version": "1.0.0",
                "author": "Lyrixa User",
                "description": description or f"Auto-generated {template_type} plugin",
                "template_type": template_type,
                "ui_component": lambda: f"{plugin_name} UI Component",
                "created_at": datetime.now().isoformat(),
            }

            self.register_plugin(basic_plugin)
            return {
                "status": "success",
                "plugin": basic_plugin,
                "message": f"Basic plugin '{plugin_name}' created",
            }

        except Exception as e:
            return {"status": "error", "message": f"Error creating plugin: {e}"}

    def get_available_zones(self):
        """Get list of available (empty) zones."""
        return [zone for zone, plugin in self.zones.items() if plugin is None]

    def get_occupied_zones(self):
        """Get list of occupied zones with their plugins."""
        return {
            zone: plugin for zone, plugin in self.zones.items() if plugin is not None
        }

    def execute_plugin_action(self, plugin_name: str, action: str, **kwargs):
        """Execute an action on a specific plugin."""
        plugin = None
        for p in self.plugins:
            p_name = getattr(p, "name", p.get("name", ""))
            if p_name == plugin_name:
                plugin = p
                break

        if not plugin:
            return {"status": "error", "message": f"Plugin '{plugin_name}' not found"}

        try:
            # Check if plugin has the requested action method
            if hasattr(plugin, action):
                method = getattr(plugin, action)
                if callable(method):
                    result = method(**kwargs)
                    return {"status": "success", "result": result}

            # Check if plugin is a dict with action
            elif isinstance(plugin, dict) and action in plugin:
                method = plugin[action]
                if callable(method):
                    result = method(**kwargs)
                    return {"status": "success", "result": result}

            return {
                "status": "error",
                "message": f"Action '{action}' not available on plugin '{plugin_name}'",
            }

        except Exception as e:
            return {"status": "error", "message": f"Error executing action: {e}"}

    def get_plugin_info(self, plugin_name: str):
        """Get detailed information about a specific plugin."""
        for plugin in self.plugins:
            p_name = getattr(plugin, "name", plugin.get("name", ""))
            if p_name == plugin_name:
                info = {
                    "name": p_name,
                    "version": getattr(
                        plugin, "version", plugin.get("version", "Unknown")
                    ),
                    "author": getattr(
                        plugin, "author", plugin.get("author", "Unknown")
                    ),
                    "description": getattr(
                        plugin,
                        "description",
                        plugin.get("description", "No description"),
                    ),
                    "has_ui_component": hasattr(plugin, "ui_component")
                    or "ui_component" in plugin,
                    "supports_themes": hasattr(plugin, "apply_theme")
                    or "apply_theme" in plugin,
                    "available_actions": [],
                }

                # Get available actions/methods
                if hasattr(plugin, "__dict__"):
                    info["available_actions"] = [
                        attr
                        for attr in dir(plugin)
                        if not attr.startswith("_") and callable(getattr(plugin, attr))
                    ]
                elif isinstance(plugin, dict):
                    info["available_actions"] = [
                        key for key, value in plugin.items() if callable(value)
                    ]

                return info

        return None
