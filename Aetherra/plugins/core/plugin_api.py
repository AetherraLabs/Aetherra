# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors


# Stub for PluginManager for modular plugin integration
class PluginManager:
    def __init__(self, *args, **kwargs):
        self.plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def list_plugins(self):
        return self.plugins


"""
🌉 Plugin API Bridge
Interface for safe plugin invocation from Lyrixa
"""

from typing import Any, Dict, List

from Aetherra.aetherra_core.plugins.plugin_manager import PluginManager


class PluginAPI:
    """Clean plugin interface for Lyrixa"""

    def __init__(self):
        self.manager = PluginManager()

    def invoke_plugin(self, plugin_id: str, action: str, **kwargs) -> Any:
        """Safely invoke plugin action"""
        return self.manager.execute_plugin(plugin_id, action, **kwargs)

    def list_plugins(self) -> List[Dict]:
        """Get available plugins"""
        return self.manager.list_available_plugins()
