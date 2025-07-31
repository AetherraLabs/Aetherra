# Stub for EnhancedPluginManager for modular plugin integration
class EnhancedPluginManager:
    def __init__(self, *args, **kwargs):
        self.plugins = []

    def add_plugin(self, plugin):
        self.plugins.append(plugin)

    def list_plugins(self):
        return self.plugins


"""
Enhanced Plugin Manager
=======================

Advanced plugin management system for Lyrixa with dynamic loading,
lifecycle management, and comprehensive analytics integration.
"""

import importlib
import importlib.util
import os
import sys
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class PluginState:
    """Plugin state management."""

    # Required plugin metadata
    name = "enhanced_plugin_manager"
    description = "PluginState - Auto-generated description"
    input_schema = {
        "type": "object",
        "properties": {"input": {"type": "string", "description": "Input data"}},
        "required": ["input"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string", "description": "Processing result"},
            "status": {"type": "string", "description": "Operation status"},
        },
    }
    created_by = "Plugin System Auto-Fixer"

    INACTIVE = "inactive"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


class PluginManager:
    """Enhanced plugin management system."""

    def __init__(self, plugins_dir: str | None = None):
        self.plugins_dir = plugins_dir or os.path.join(os.path.dirname(__file__))
        self.plugins: Dict[str, Any] = {}
        self.plugin_states: Dict[str, str] = {}
        self.plugin_metadata: Dict[str, Dict] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.auto_reload = False
        self.monitoring_thread = None

        # Analytics integration
        self.analytics = None
        self._initialize_analytics()

    def _initialize_analytics(self):
        """Initialize plugin analytics if available."""
        try:
            from .plugin_analytics import PluginAnalyticsIntegration

            self.analytics = PluginAnalyticsIntegration()
        except ImportError:
            self.analytics = None

    def track_plugin_event(
        self, plugin_name: str, event: str, extra_context: Optional[Dict] = None
    ):
        """Track plugin events using analytics integration."""
        if self.analytics:
            context = {"plugin_name": plugin_name}
            if extra_context:
                context.update(extra_context)
            if event == "load_attempt":
                self.analytics.record_plugin_action(
                    plugin_name, "load_attempt", context
                )
            elif event == "load_success":
                self.analytics.record_plugin_action(
                    plugin_name, "load_success", context
                )
            elif event == "unload":
                self.analytics.record_plugin_action(plugin_name, "unload", context)
            elif event == "execute_start":
                self.analytics.record_plugin_action(
                    plugin_name, "execute_start", context
                )
            elif event == "execute_end":
                self.analytics.record_plugin_action(plugin_name, "execute_end", context)
            elif event == "load_error":
                self.analytics.record_plugin_error(
                    plugin_name, Exception("Load error occurred"), context
                )
            elif event == "execute_error":
                self.analytics.record_plugin_error(
                    plugin_name, Exception("Execution error occurred"), context
                )

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory."""
        plugins = []

        if not os.path.exists(self.plugins_dir):
            return plugins

        for file in os.listdir(self.plugins_dir):
            if file.endswith(".py") and not file.startswith("__"):
                plugin_name = file[:-3]  # Remove .py extension

                # Skip system files
                if plugin_name in [
                    "plugin_manager",
                    "enhanced_plugin_manager",
                    "plugin_analytics",
                    "plugin_quality_control",
                ]:
                    continue

                plugins.append(plugin_name)

        return plugins

    def load_plugin(self, plugin_name: str, force_reload: bool = False) -> bool:
        """Load a plugin with comprehensive error handling."""
        try:
            self.plugin_states[plugin_name] = PluginState.LOADING

            # Analytics tracking
            self.track_plugin_event(plugin_name, "load_attempt")

            # Check if already loaded
            if plugin_name in self.plugins and not force_reload:
                self.plugin_states[plugin_name] = PluginState.ACTIVE
                return True

            # Import the plugin module
            module_path = f"lyrixa.plugins.{plugin_name}"
            if plugin_name in sys.modules and force_reload:
                importlib.reload(sys.modules[plugin_name])

            try:
                module = importlib.import_module(module_path)
            except ImportError:
                # Try direct import
                spec = importlib.util.spec_from_file_location(
                    plugin_name, os.path.join(self.plugins_dir, f"{plugin_name}.py")
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError(f"Could not load spec for {plugin_name}")

            # Look for plugin class or main function
            plugin_instance = None

            # Try to find a plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "execute")
                    and attr_name.lower().endswith("plugin")
                ):
                    plugin_instance = attr()
                    break

            # If no plugin class, look for main function
            if not plugin_instance and hasattr(module, "main"):
                plugin_instance = module

            if plugin_instance:
                self.plugins[plugin_name] = plugin_instance
                self.plugin_states[plugin_name] = PluginState.ACTIVE

                # Load metadata
                self._load_plugin_metadata(plugin_name, module)

                # Trigger loaded event
                self._trigger_event("plugin_loaded", plugin_name)

                # Analytics tracking
                self.track_plugin_event(plugin_name, "load_success")

                return True
            else:
                self.plugin_states[plugin_name] = PluginState.ERROR
                return False

        except Exception as e:
            self.plugin_states[plugin_name] = PluginState.ERROR

            # Analytics tracking
            self.track_plugin_event(plugin_name, "load_error", {"error": str(e)})

            print(f"Error loading plugin {plugin_name}: {e}")
            return False

    def _load_plugin_metadata(self, plugin_name: str, module: Any):
        """Load plugin metadata from module attributes."""
        metadata = {
            "name": plugin_name,
            "version": getattr(module, "__version__", "1.0.0"),
            "description": getattr(module, "__doc__", "").strip(),
            "author": getattr(module, "__author__", "Unknown"),
            "dependencies": getattr(module, "__dependencies__", []),
            "tags": getattr(module, "__tags__", []),
            "category": getattr(module, "__category__", "general"),
            "loaded_at": datetime.now().isoformat(),
        }

        self.plugin_metadata[plugin_name] = metadata

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin safely."""
        try:
            if plugin_name not in self.plugins:
                return False

            # Call cleanup if available
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, "cleanup"):
                plugin.cleanup()

            # Remove from plugins
            del self.plugins[plugin_name]
            self.plugin_states[plugin_name] = PluginState.INACTIVE

            # Trigger unloaded event
            self._trigger_event("plugin_unloaded", plugin_name)

            # Analytics tracking
            self.track_plugin_event(plugin_name, "unload")

            return True

        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False

    def execute_plugin(self, plugin_name: str, *args, **kwargs) -> Any:
        """Execute a plugin with analytics tracking."""
        if plugin_name not in self.plugins:
            if not self.load_plugin(plugin_name):
                return None

        try:
            plugin = self.plugins[plugin_name]

            # Analytics tracking - start
            start_time = time.time()
            self.track_plugin_event(plugin_name, "execute_start")

            # Execute plugin
            if hasattr(plugin, "execute"):
                result = plugin.execute(*args, **kwargs)
            elif hasattr(plugin, "main"):
                result = plugin.main(*args, **kwargs)
            else:
                result = None

            # Analytics tracking - success
            execution_time = time.time() - start_time
            self.track_plugin_event(
                plugin_name,
                "execute_success",
                {
                    "execution_time": execution_time,
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                },
            )

            return result

        except Exception as e:
            # Analytics tracking - error
            self.track_plugin_event(plugin_name, "execute_error", {"error": str(e)})

            print(f"Error executing plugin {plugin_name}: {e}")
            return None

    def execute_chain(self, user_message: str) -> str:
        """Execute a chain of plugins based on the user message."""
        try:
            # Example logic: iterate through plugins and execute matching ones
            for plugin_name, plugin in self.plugins.items():
                if hasattr(plugin, "process_message"):
                    response = plugin.process_message(user_message)
                    if response:
                        return response

            # Fallback if no plugin processes the message
            return "No plugin could process the message."
        except Exception as e:
            return f"Error executing plugin chain: {e}"

    def get_plugin_info(self, plugin_name: str) -> Dict:
        """Get comprehensive plugin information."""
        info = {
            "name": plugin_name,
            "state": self.plugin_states.get(plugin_name, PluginState.INACTIVE),
            "loaded": plugin_name in self.plugins,
            "metadata": self.plugin_metadata.get(plugin_name, {}),
            "analytics": {},
        }

        # Add analytics data
        if self.analytics:
            info["analytics"] = self.analytics.get_plugin_analytics(plugin_name)

        return info

    def list_plugins(self) -> Dict[str, Dict]:
        """List all available plugins with their information."""
        discovered = self.discover_plugins()
        plugin_list = {}

        for plugin_name in discovered:
            plugin_list[plugin_name] = self.get_plugin_info(plugin_name)

        return plugin_list

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin completely."""
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)

        return self.load_plugin(plugin_name, force_reload=True)

    def enable_auto_reload(self, check_interval: int = 5):
        """Enable automatic plugin reloading on file changes."""
        self.auto_reload = True

        if not self.monitoring_thread or not self.monitoring_thread.is_alive():
            self.monitoring_thread = threading.Thread(
                target=self._monitor_plugins, args=(check_interval,), daemon=True
            )
            self.monitoring_thread.start()

    def disable_auto_reload(self):
        """Disable automatic plugin reloading."""
        self.auto_reload = False

    def _monitor_plugins(self, check_interval: int):
        """Monitor plugins for file changes."""
        file_times = {}

        while self.auto_reload:
            try:
                for plugin_name in list(self.plugins.keys()):
                    plugin_file = os.path.join(self.plugins_dir, f"{plugin_name}.py")

                    if os.path.exists(plugin_file):
                        current_time = os.path.getmtime(plugin_file)

                        if plugin_name in file_times:
                            if current_time > file_times[plugin_name]:
                                print(f"Reloading changed plugin: {plugin_name}")
                                self.reload_plugin(plugin_name)

                        file_times[plugin_name] = current_time

                time.sleep(check_interval)

            except Exception as e:
                print(f"Error monitoring plugins: {e}")
                time.sleep(check_interval)

    def register_event_handler(self, event: str, handler: Callable):
        """Register an event handler."""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)

    def _trigger_event(self, event: str, *args, **kwargs):
        """Trigger an event and call all registered handlers."""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    handler(*args, **kwargs)
                except Exception as e:
                    print(f"Error in event handler for {event}: {e}")

    def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary."""
        if not self.analytics:
            return {"error": "Analytics not available"}

        return {
            "total_plugins": len(self.discover_plugins()),
            "loaded_plugins": len(self.plugins),
            "plugin_states": dict(self.plugin_states),
            "analytics": self.analytics.get_dashboard_data(),
        }

    def export_configuration(self) -> Dict:
        """Export current plugin configuration."""
        return {
            "plugins_dir": self.plugins_dir,
            "loaded_plugins": list(self.plugins.keys()),
            "plugin_states": dict(self.plugin_states),
            "plugin_metadata": dict(self.plugin_metadata),
            "auto_reload": self.auto_reload,
            "exported_at": datetime.now().isoformat(),
        }

    def import_configuration(self, config: Dict) -> bool:
        """Import plugin configuration."""
        try:
            # Load specified plugins
            for plugin_name in config.get("loaded_plugins", []):
                self.load_plugin(plugin_name)

            # Set auto-reload if specified
            if config.get("auto_reload", False):
                self.enable_auto_reload()

            return True

        except Exception as e:
            print(f"Error importing configuration: {e}")
            return False


# Global plugin manager instance
plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance."""
    return plugin_manager
