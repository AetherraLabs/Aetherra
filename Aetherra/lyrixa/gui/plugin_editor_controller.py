#!/usr/bin/env python3
"""
Plugin Editor Controller - Mock Implementation
==============================================

Mock implementation of the plugin editor controller to resolve initialization warnings.
"""

import logging

logger = logging.getLogger(__name__)

class PluginEditorController:
    """Mock Plugin Editor Controller for conversation manager compatibility"""

    _instance = None

    def __init__(self):
        self.plugins = {}
        logger.info("✅ Mock Plugin Editor Controller initialized")

    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_plugin(self, plugin_name: str):
        """Mock plugin loading"""
        logger.info(f"📦 Mock loading plugin: {plugin_name}")
        return True

    def unload_plugin(self, plugin_name: str):
        """Mock plugin unloading"""
        logger.info(f"📦 Mock unloading plugin: {plugin_name}")
        return True

    def list_plugins(self):
        """Return list of mock plugins"""
        return list(self.plugins.keys())

    def get_plugin_status(self, plugin_name: str):
        """Get mock plugin status"""
        return "active" if plugin_name in self.plugins else "inactive"
