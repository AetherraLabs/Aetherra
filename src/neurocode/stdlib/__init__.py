#!/usr/bin/env python3
"""
🧬 NeuroCode Standard Library Manager
Manages built-in plugins for NeuroCode
"""

import importlib.util
from pathlib import Path


class StandardLibraryManager:
    """Manages NeuroCode standard library plugins"""

    def __init__(self):
        self.stdlib_path = Path(__file__).parent
        self.plugins = {}
        self.load_standard_plugins()

    def load_standard_plugins(self):
        """Load all standard library plugins"""
        plugin_files = [
            "sysmon.py",
            "optimizer.py",
            "selfrepair.py",
            "whisper.py",
            "reflector.py",
            "executor.py",
            "coretools.py",
        ]

        for plugin_file in plugin_files:
            plugin_path = self.stdlib_path / plugin_file
            if plugin_path.exists():
                try:
                    self.load_plugin(plugin_path)
                except Exception as e:
                    print(f"⚠️ [StdLib] Warning: Could not load {plugin_file}: {e}")

    def load_plugin(self, plugin_path):
        """Load a single plugin from file"""
        plugin_name = plugin_path.stem

        try:
            # Load module
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not create module spec for {plugin_path}")

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get plugin class
            if hasattr(module, "PLUGIN_CLASS"):
                plugin_class = module.PLUGIN_CLASS
                plugin_instance = plugin_class()
                self.plugins[plugin_instance.name] = plugin_instance
                print(
                    f"✅ [StdLib] Loaded plugin: {plugin_instance.name} - {plugin_instance.description}"
                )
            else:
                print(f"⚠️ [StdLib] Warning: {plugin_name} missing PLUGIN_CLASS")
        except Exception as e:
            print(f"⚠️ [StdLib] Error loading {plugin_name}: {e}")
            raise

    def execute_plugin_action(self, plugin_name, action, memory_system=None, **kwargs):
        """Execute an action on a specific plugin"""
        if plugin_name not in self.plugins:
            return f"Plugin '{plugin_name}' not found. Available: {list(self.plugins.keys())}"

        plugin = self.plugins[plugin_name]
        try:
            return plugin.execute_action(action, memory_system=memory_system, **kwargs)
        except Exception as e:
            return f"Error executing {plugin_name}.{action}: {e}"

    def list_plugins(self):
        """List all available standard plugins"""
        return {name: plugin.description for name, plugin in self.plugins.items()}

    def get_plugin_info(self, plugin_name):
        """Get detailed information about a plugin"""
        if plugin_name not in self.plugins:
            return None

        plugin = self.plugins[plugin_name]
        return {
            "name": plugin.name,
            "description": plugin.description,
            "available_actions": getattr(plugin, "available_actions", ["execute_action"]),
            "loaded": True,
        }


# Global instance for easy access
stdlib_manager = StandardLibraryManager()
