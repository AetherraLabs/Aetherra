#!/usr/bin/env python3
"""
🖥️🧩 GUI PLUGIN INTEGRATION
===========================

This module provides GUI components for displaying plugin information
discovered through the Plugin-Intelligence Bridge. It updates existing
GUI interfaces with real plugin data.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginGUIIntegrator:
    """
    🖥️ GUI Plugin Display Integration

    Integrates real plugin discovery data with GUI components
    """

    def __init__(self, plugin_bridge=None):
        self.plugin_bridge = plugin_bridge
        self.gui_components = {}

    def register_gui_component(self, name: str, component):
        """Register a GUI component for plugin display updates"""
        self.gui_components[name] = component
        logger.info(f"✅ Registered GUI component: {name}")

    async def update_all_gui_components(self):
        """Update all registered GUI components with plugin data"""
        if not self.plugin_bridge:
            logger.warning("⚠️ No plugin bridge available")
            return False

        try:
            # Get comprehensive plugin summary
            plugin_summary = self.plugin_bridge.get_plugin_summary_for_gui()

            # Update each registered component
            for name, component in self.gui_components.items():
                try:
                    await self._update_component(name, component, plugin_summary)
                except Exception as e:
                    logger.error(f"❌ Failed to update GUI component {name}: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ Error updating GUI components: {e}")
            return False

    async def _update_component(
        self, name: str, component, plugin_summary: Dict[str, Any]
    ):
        """Update a specific GUI component"""
        if hasattr(component, "update_plugin_display"):
            component.update_plugin_display(plugin_summary)
        elif hasattr(component, "refresh_plugin_data"):
            component.refresh_plugin_data(plugin_summary)
        else:
            # Try to update common Qt components
            await self._update_qt_component(component, plugin_summary)

    async def _update_qt_component(self, component, plugin_summary: Dict[str, Any]):
        """Update Qt-based GUI components"""
        try:
            # Check if it's a QTableWidget (like in launcher_backup.py)
            if hasattr(component, "setRowCount") and hasattr(component, "setItem"):
                await self._update_table_widget(component, plugin_summary)
            # Check if it's a QListWidget
            elif hasattr(component, "addItem") and hasattr(component, "clear"):
                await self._update_list_widget(component, plugin_summary)
            # Check if it's a QLabel
            elif hasattr(component, "setText"):
                await self._update_label_widget(component, plugin_summary)

        except Exception as e:
            logger.debug(f"Could not update Qt component: {e}")

    async def _update_table_widget(self, table_widget, plugin_summary: Dict[str, Any]):
        """Update a QTableWidget with plugin data"""
        # Clear existing data
        table_widget.setRowCount(0)

        # Get discovered plugins
        if not self.plugin_bridge:
            return

        plugins = self.plugin_bridge.discovered_plugins
        table_widget.setRowCount(len(plugins))

        row = 0
        for plugin_key, plugin_data in plugins.items():
            try:
                # Import QTableWidgetItem locally to avoid import errors
                from PySide6.QtWidgets import QTableWidgetItem

                # Update table cells
                table_widget.setItem(
                    row, 0, QTableWidgetItem(plugin_data.get("name", "Unknown"))
                )
                table_widget.setItem(
                    row, 1, QTableWidgetItem(plugin_data.get("status", "Unknown"))
                )

                # Health based on status
                health = (
                    "Healthy"
                    if plugin_data.get("status") in ["loaded", "active", "installed"]
                    else "Unknown"
                )
                table_widget.setItem(row, 2, QTableWidgetItem(health))

                # Actions based on status
                action = (
                    "Configure" if plugin_data.get("status") == "loaded" else "Load"
                )
                table_widget.setItem(row, 3, QTableWidgetItem(action))

                row += 1

            except ImportError:
                # PySide6 not available
                break
            except Exception as e:
                logger.debug(f"Error updating table row {row}: {e}")
                row += 1

    async def _update_list_widget(self, list_widget, plugin_summary: Dict[str, Any]):
        """Update a QListWidget with plugin data"""
        list_widget.clear()

        try:
            # Add summary information
            total = plugin_summary.get("total_plugins", 0)
            list_widget.addItem(f"🔌 Total Plugins: {total}")

            # Add status breakdown
            by_status = plugin_summary.get("by_status", {})
            for status, count in by_status.items():
                list_widget.addItem(f"   📊 {status.title()}: {count}")

            list_widget.addItem("")  # Spacer

            # Add featured plugins
            featured = plugin_summary.get("featured_plugins", [])
            if featured:
                list_widget.addItem("⭐ Featured Plugins:")
                for plugin in featured[:3]:
                    list_widget.addItem(f"   • {plugin.get('name', 'Unknown')}")

        except Exception as e:
            logger.debug(f"Error updating list widget: {e}")

    async def _update_label_widget(self, label_widget, plugin_summary: Dict[str, Any]):
        """Update a QLabel with plugin summary"""
        try:
            total = plugin_summary.get("total_plugins", 0)
            active_count = plugin_summary.get("by_status", {}).get("active", 0)
            text = f"Plugins: {total} total, {active_count} active"
            label_widget.setText(text)
        except Exception as e:
            logger.debug(f"Error updating label widget: {e}")

    def create_plugin_info_widget(self):
        """Create a new widget to display plugin information"""
        try:
            from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

            widget = QWidget()
            layout = QVBoxLayout(widget)

            # Header
            header = QLabel("🧩 Discovered Plugins")
            header.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(header)

            # Plugin list
            plugin_list = QListWidget()
            layout.addWidget(plugin_list)

            # Register for updates
            self.register_gui_component("plugin_info_widget", plugin_list)

            return widget

        except ImportError:
            logger.warning("⚠️ PySide6 not available - cannot create plugin widget")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating plugin info widget: {e}")
            return None


class LyrixaPluginAwareChat:
    """
    💬 Plugin-Aware Chat Interface

    Chat interface that can query and recommend plugins using the intelligence bridge
    """

    def __init__(self, intelligence_stack=None):
        self.intelligence_stack = intelligence_stack
        self.plugin_awareness_enabled = intelligence_stack is not None

    async def handle_plugin_query(self, user_message: str) -> str:
        """Handle user queries about plugins"""
        if not self.plugin_awareness_enabled:
            return "Plugin awareness is not available in this session."

        try:
            # Check if user is asking about plugins
            plugin_keywords = [
                "plugin",
                "plugins",
                "extension",
                "add-on",
                "tool",
                "feature",
            ]
            message_lower = user_message.lower()

            is_plugin_query = any(
                keyword in message_lower for keyword in plugin_keywords
            )

            if is_plugin_query:
                # Get plugin recommendations
                recommendations = (
                    await self.intelligence_stack.get_plugin_recommendations_for_lyrixa(
                        user_message
                    )
                )

                if recommendations:
                    response = "I found these relevant plugins for you:\n\n"

                    for i, plugin in enumerate(recommendations[:3], 1):
                        name = plugin.get("name", "Unknown")
                        description = plugin.get(
                            "description", "No description available"
                        )
                        status = plugin.get("status", "unknown")

                        response += f"{i}. **{name}** ({status})\n"
                        response += f"   {description}\n\n"

                    response += (
                        "Would you like me to help you with any of these plugins?"
                    )
                    return response
                else:
                    return "I didn't find any plugins matching your query. Could you be more specific about what you're looking for?"

            return None  # Not a plugin query

        except Exception as e:
            logger.error(f"❌ Error handling plugin query: {e}")
            return "I encountered an error while searching for plugins."

    async def get_plugin_help_response(self, plugin_name: str) -> str:
        """Get help information for a specific plugin"""
        if not self.plugin_awareness_enabled:
            return "Plugin information is not available."

        try:
            # Query for specific plugin
            results = (
                await self.intelligence_stack.get_plugin_recommendations_for_lyrixa(
                    plugin_name
                )
            )

            if results:
                plugin = results[0]
                name = plugin.get("name", "Unknown")
                description = plugin.get("description", "No description available")
                capabilities = plugin.get("capabilities", [])
                status = plugin.get("status", "unknown")

                response = f"**{name}** Plugin\n\n"
                response += f"Status: {status}\n"
                response += f"Description: {description}\n"

                if capabilities:
                    response += "\nCapabilities:\n"
                    for capability in capabilities:
                        response += f"• {capability}\n"

                return response
            else:
                return f"I couldn't find information about the '{plugin_name}' plugin."

        except Exception as e:
            logger.error(f"❌ Error getting plugin help: {e}")
            return "I encountered an error while getting plugin information."


# Export main classes
__all__ = ["PluginGUIIntegrator", "LyrixaPluginAwareChat"]
