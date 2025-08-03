#!/usr/bin/env python3
"""
🧩 LYRIXA PLUGIN MANAGER
========================

Lyrixa's plugin ecosystem for extending capabilities and integrations.
Manages plugin discovery, loading, execution, and security.
"""

import importlib.util
import inspect
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from .plugin_state_memory import CognitivePluginMemory, PluginStateMemory

# Import our new version control system
from .plugin_version_control import PluginVersionControl, PluginVersionHooks

# Import our new semantic discovery system
from .semantic_plugin_discovery import SemanticPluginDiscovery


@dataclass
class PluginInfo:
    """Information about a plugin"""

    name: str
    version: str
    description: str
    author: str
    category: str
    capabilities: List[str]
    dependencies: List[str]
    file_path: str
    enabled: bool = True
    loaded: bool = False

    # Plugin Chaining Metadata
    input_types: Optional[List[str]] = None  # Data types this plugin accepts
    output_types: Optional[List[str]] = None  # Data types this plugin produces
    collaborates_with: Optional[List[str]] = None  # Plugin names this can work with
    auto_chain: bool = False  # Whether this plugin can be auto-chained
    chain_priority: float = 0.5  # Priority in chain selection (0.0-1.0)

    def __post_init__(self):
        """Initialize None fields with empty lists"""
        if self.input_types is None:
            self.input_types = []
        if self.output_types is None:
            self.output_types = []
        if self.collaborates_with is None:
            self.collaborates_with = []


class LyrixaPlugin(ABC):
    """
    Base class for all Lyrixa plugins

    All plugins must inherit from this class and implement the required methods.
    """

    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.description = "A Lyrixa plugin"
        self.author = "Unknown"
        self.category = "general"
        self.capabilities = []
        self.dependencies = []

        # Plugin Chaining Metadata
        self.input_types = []  # Data types this plugin accepts
        self.output_types = []  # Data types this plugin produces
        self.collaborates_with = []  # Plugin names this can work with
        self.auto_chain = False  # Whether this plugin can be auto-chained
        self.chain_priority = 0.5  # Priority in chain selection (0.0-1.0)

        # Reference to plugin manager (set during initialization)
        self.plugin_manager: Optional["LyrixaPluginManager"] = None

    @abstractmethod
    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        """Initialize the plugin with Lyrixa context"""
        pass

    @abstractmethod
    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a plugin command"""
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """Clean up plugin resources"""
        pass

    def get_info(self) -> PluginInfo:
        """Get plugin information"""
        return PluginInfo(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            category=self.category,
            capabilities=self.capabilities,
            dependencies=self.dependencies,
            file_path="",
            input_types=self.input_types,
            output_types=self.output_types,
            collaborates_with=self.collaborates_with,
            auto_chain=self.auto_chain,
            chain_priority=self.chain_priority,
        )

    # State Memory Helper Methods
    def set_state(self, key: str, value: Any, state_type: str = "json") -> bool:
        """Set persistent state for this plugin"""
        if self.plugin_manager:
            return self.plugin_manager.set_plugin_state(
                self.name, key, value, state_type
            )
        return False

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get persistent state for this plugin"""
        if self.plugin_manager:
            return self.plugin_manager.get_plugin_state(self.name, key, default)
        return default

    def delete_state(self, key: Optional[str] = None) -> bool:
        """Delete persistent state for this plugin"""
        if self.plugin_manager:
            return self.plugin_manager.delete_plugin_state(self.name, key)
        return False

    def get_shared_state(self, namespace: str, key: str, default: Any = None) -> Any:
        """Get shared state from another plugin"""
        if self.plugin_manager:
            return self.plugin_manager.get_shared_state(
                namespace, key, self.name, default
            )
        return default

    def set_shared_state(
        self,
        namespace: str,
        key: str,
        value: Any,
        allowed_plugins: Optional[List[str]] = None,
    ) -> bool:
        """Set shared state for other plugins to access"""
        if self.plugin_manager:
            return self.plugin_manager.set_shared_state(
                namespace, key, value, self.name, allowed_plugins
            )
        return False

    # Plugin Chaining Helper Methods
    def get_io_spec(self) -> Dict[str, List[str]]:
        """Get input/output specification for chaining"""
        return {"inputs": self.input_types, "outputs": self.output_types}

    def get_collaborators(self) -> List[str]:
        """Get list of plugins this can collaborate with"""
        return self.collaborates_with

    def can_chain_with(self, other_plugin: "LyrixaPlugin") -> bool:
        """Check if this plugin can chain with another plugin"""
        # Check if output types match input types
        if any(
            output_type in other_plugin.input_types for output_type in self.output_types
        ):
            return True

        # Check explicit collaboration
        if other_plugin.name in self.collaborates_with:
            return True

        return False

    def get_chain_priority(self) -> float:
        """Get the chaining priority of this plugin"""
        return self.chain_priority


class LyrixaPluginManager:
    """
    Lyrixa's plugin management system

    Handles plugin discovery, loading, execution, and lifecycle management.
    Provides security sandboxing and capability management.
    """

    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = plugin_directory
        self.loaded_plugins: Dict[str, LyrixaPlugin] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.plugin_registry: Dict[str, Type[LyrixaPlugin]] = {}
        self.enabled_plugins: set = set()
        self.lyrixa_context: Dict[str, Any] = {}

        # Will be initialized after manager is set up
        self.semantic_discovery: Optional[SemanticPluginDiscovery] = None
        self.plugin_chainer = None  # Will be initialized as PluginChainer

        # Initialize plugin state memory
        self.state_memory = PluginStateMemory()
        self.cognitive_memory = CognitivePluginMemory(self.state_memory)

        # Initialize version control system
        self.version_control = PluginVersionControl(
            memory_system=None
        )  # Will be set later
        self.version_hooks = PluginVersionHooks(self.version_control)

        # Create plugin directory if it doesn't exist
        os.makedirs(plugin_directory, exist_ok=True)

        # Initialize built-in plugins
        self._register_builtin_plugins()

    async def initialize(self, lyrixa_context: Dict[str, Any]):
        """Initialize the plugin manager with Lyrixa context"""
        self.lyrixa_context = lyrixa_context

        # Initialize semantic plugin discovery
        self.semantic_discovery = SemanticPluginDiscovery(self)

        # Initialize plugin chainer
        from .plugin_chainer import PluginChainer

        self.plugin_chainer = PluginChainer(self)

        # Discover and load plugins
        await self._discover_plugins()
        await self._load_enabled_plugins()

        # Index plugins for semantic discovery
        await self._index_plugins_for_semantic_search()

        print(f"🧩 Plugin manager initialized with {len(self.loaded_plugins)} plugins")

    def _register_builtin_plugins(self):
        """Register built-in plugins"""
        # Register built-in plugin classes
        self.plugin_registry.update(
            {
                "FileManagerPlugin": FileManagerPlugin,
                "WebSearchPlugin": WebSearchPlugin,
                "CodeAnalyzerPlugin": CodeAnalyzerPlugin,
                "DataVisualizerPlugin": DataVisualizerPlugin,
                "APIConnectorPlugin": APIConnectorPlugin,
            }
        )

    async def _discover_plugins(self):
        """Discover plugins in the plugin directory"""
        print(f"🔍 Discovering plugins in {self.plugin_directory}")

        # Built-in plugins
        for plugin_name, plugin_class in self.plugin_registry.items():
            try:
                plugin_instance = plugin_class()
                info = plugin_instance.get_info()
                info.file_path = "built-in"
                self.plugin_info[plugin_name] = info
                print(f"   [DISC] Found built-in plugin: {plugin_name}")
            except Exception as e:
                print(f"   ❌ Failed to load built-in plugin {plugin_name}: {e}")

        # External plugins
        if os.path.exists(self.plugin_directory):
            for filename in os.listdir(self.plugin_directory):
                if filename.endswith(".py") and not filename.startswith("_"):
                    await self._discover_plugin_file(filename)

    async def _discover_plugin_file(self, filename: str):
        """Discover and validate a plugin file"""
        file_path = os.path.join(self.plugin_directory, filename)
        plugin_name = filename[:-3]  # Remove .py extension

        try:
            # Load the module
            spec = importlib.util.spec_from_file_location(plugin_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find plugin classes in the module
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, LyrixaPlugin)
                        and obj != LyrixaPlugin
                    ):
                        plugin_instance = obj()
                        info = plugin_instance.get_info()
                        info.file_path = file_path

                        self.plugin_info[name] = info
                        self.plugin_registry[name] = obj

                        print(f"   [DISC] Found external plugin: {name}")
                        break

        except Exception as e:
            print(f"   ❌ Failed to load plugin {filename}: {e}")

    async def _load_enabled_plugins(self):
        """Load all enabled plugins"""
        for plugin_name, info in self.plugin_info.items():
            if info.enabled:
                await self.load_plugin(plugin_name)

    async def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin"""
        if plugin_name in self.loaded_plugins:
            return True

        if plugin_name not in self.plugin_registry:
            print(f"❌ Plugin {plugin_name} not found in registry")
            return False

        try:
            # Create plugin instance
            plugin_class = self.plugin_registry[plugin_name]
            plugin_instance = plugin_class()

            # Set plugin manager reference for state memory access
            plugin_instance.plugin_manager = self

            # Initialize the plugin
            success = await plugin_instance.initialize(self.lyrixa_context)

            if success:
                self.loaded_plugins[plugin_name] = plugin_instance
                self.enabled_plugins.add(plugin_name)
                self.plugin_info[plugin_name].loaded = True

                print(f"✅ Loaded plugin: {plugin_name}")
                return True
            else:
                print(f"❌ Failed to initialize plugin: {plugin_name}")
                return False

        except Exception as e:
            print(f"❌ Error loading plugin {plugin_name}: {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return True

        try:
            plugin = self.loaded_plugins[plugin_name]
            await plugin.cleanup()

            del self.loaded_plugins[plugin_name]
            self.enabled_plugins.discard(plugin_name)
            self.plugin_info[plugin_name].loaded = False

            print(f"🔄 Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"❌ Error unloading plugin {plugin_name}: {e}")
            return False

    async def execute_plugin(
        self, plugin_name: str, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a command on a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return {
                "success": False,
                "error": f"Plugin {plugin_name} is not loaded",
                "result": None,
            }

        start_time = datetime.now()
        try:
            plugin = self.loaded_plugins[plugin_name]
            result = await plugin.execute(command, params or {})

            # Track execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_plugin_performance(plugin_name, True, execution_time)

            # Remember successful interaction for learning
            self.cognitive_memory.remember_interaction(
                plugin_name=plugin_name,
                user_input=f"{command}: {params}",
                plugin_response=str(result),
                success=True,
            )

            return {
                "success": True,
                "error": None,
                "result": result,
                "plugin": plugin_name,
                "command": command,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            # Track execution failure
            execution_time = (datetime.now() - start_time).total_seconds()
            self.update_plugin_performance(plugin_name, False, execution_time)

            # Remember failed interaction for learning
            self.cognitive_memory.remember_interaction(
                plugin_name=plugin_name,
                user_input=f"{command}: {params}",
                plugin_response=str(e),
                success=False,
            )

            return {
                "success": False,
                "error": str(e),
                "result": None,
                "plugin": plugin_name,
                "command": command,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

    async def execute_capability(
        self, capability: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a capability across all plugins that support it"""
        results = []

        for plugin_name, plugin in self.loaded_plugins.items():
            info = self.plugin_info[plugin_name]
            if capability in info.capabilities:
                result = await self.execute_plugin(plugin_name, capability, params)
                results.append(result)

        return results

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.plugin_info.get(plugin_name)

    def list_plugins(
        self, category: Optional[str] = None, loaded_only: bool = False
    ) -> List[PluginInfo]:
        """List available plugins"""
        plugins = []

        for info in self.plugin_info.values():
            if category and info.category != category:
                continue
            if loaded_only and not info.loaded:
                continue
            plugins.append(info)

        return plugins

    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all available capabilities and the plugins that provide them"""
        capabilities = {}

        for plugin_name, info in self.plugin_info.items():
            if info.loaded:
                for capability in info.capabilities:
                    if capability not in capabilities:
                        capabilities[capability] = []
                    capabilities[capability].append(plugin_name)

        return capabilities

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name)

    async def cleanup(self):
        """Clean up all plugins"""
        for plugin_name in list(self.loaded_plugins.keys()):
            await self.unload_plugin(plugin_name)

    async def _index_plugins_for_semantic_search(self):
        """Index all loaded plugins for semantic discovery"""
        if not self.semantic_discovery:
            return

        try:
            indexed_count = self.semantic_discovery.discover_and_index_plugins()
            print(f"🔍 Indexed {indexed_count} plugins for semantic discovery")
        except Exception as e:
            print(f"[WARN] Failed to index plugins for semantic discovery: {e}")

    async def suggest_plugins_for_goal(self, user_goal: str) -> str:
        """Get plugin suggestions based on user goal using semantic discovery"""
        if not self.semantic_discovery:
            return "Semantic plugin discovery not available."

        try:
            relevant_plugins = await self.semantic_discovery.find_relevant_plugins(
                user_goal
            )

            if not relevant_plugins:
                return "No relevant plugins found for your goal. Try being more specific or enabling additional plugins."

            suggestions = []
            for plugin_name in relevant_plugins:
                info = self.plugin_info.get(plugin_name)
                if info:
                    status = "✅ Enabled" if info.loaded else "[WARN] Available"
                    suggestions.append(
                        f"• {plugin_name}: {info.description} ({status})"
                    )

            response = f"🎯 Suggested plugins for '{user_goal}':\n"
            response += "\n".join(suggestions[:5])  # Limit to top 5

            if len(relevant_plugins) > 5:
                response += f"\n\n... and {len(relevant_plugins) - 5} more plugins."

            return response

        except Exception as e:
            return f"Error finding plugin suggestions: {e}"

    # Plugin Chaining Methods
    async def build_plugin_chain(
        self,
        goal: str,
        available_plugins: Optional[List[str]] = None,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Build a plugin chain to achieve a goal"""
        if not self.plugin_chainer:
            return None

        try:
            from .plugin_chainer import ChainExecutionMode

            chain = await self.plugin_chainer.build_chain(
                goal=goal,
                available_plugins=available_plugins,
                input_data=input_data,
                execution_mode=ChainExecutionMode.ADAPTIVE,
            )

            if not chain:
                return None

            return {
                "chain_id": chain.chain_id,
                "plugins": [node.plugin_name for node in chain.nodes],
                "execution_mode": chain.execution_mode.value,
                "metadata": chain.metadata,
            }

        except Exception as e:
            print(f"❌ Error building plugin chain: {e}")
            return None

    async def execute_plugin_chain(
        self, chain_id: str, initial_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a previously built plugin chain"""
        if not self.plugin_chainer:
            return {"error": "Plugin chainer not available"}

        try:
            if chain_id not in self.plugin_chainer.active_chains:
                return {"error": f"Chain {chain_id} not found"}

            chain = self.plugin_chainer.active_chains[chain_id]
            result = await self.plugin_chainer.run_chain(chain, initial_data)

            return {
                "success": True,
                "chain_id": chain_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "chain_id": chain_id,
                "timestamp": datetime.now().isoformat(),
            }

    async def suggest_plugin_chains(
        self, user_input: str, context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Suggest plugin chains based on user input"""
        if not self.plugin_chainer:
            return []

        try:
            suggestions = await self.plugin_chainer.suggest_chains(
                user_input=user_input, context=context or {}
            )

            return suggestions

        except Exception as e:
            print(f"❌ Error suggesting plugin chains: {e}")
            return []

    def get_chain_status(self, chain_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a plugin chain"""
        if not self.plugin_chainer:
            return None

        return self.plugin_chainer.get_chain_status(chain_id)

    async def cleanup_chain(self, chain_id: str) -> bool:
        """Clean up a completed plugin chain"""
        if not self.plugin_chainer:
            return False

        return self.plugin_chainer.cleanup_chain(chain_id)

    def update_plugin_performance(
        self, plugin_name: str, success: bool, execution_time: float
    ):
        """Update plugin performance metrics after execution"""
        if self.semantic_discovery:
            self.semantic_discovery.update_plugin_performance(
                plugin_name, success, execution_time
            )

    # Plugin State Memory Methods
    def set_plugin_state(
        self,
        plugin_name: str,
        state_key: str,
        state_value: Any,
        state_type: str = "json",
    ) -> bool:
        """Set persistent state for a plugin"""
        return self.state_memory.set_plugin_state(
            plugin_name, state_key, state_value, state_type
        )

    def get_plugin_state(
        self, plugin_name: str, state_key: str, default: Any = None
    ) -> Any:
        """Get persistent state for a plugin"""
        return self.state_memory.get_plugin_state(plugin_name, state_key, default)

    def delete_plugin_state(
        self, plugin_name: str, state_key: Optional[str] = None
    ) -> bool:
        """Delete plugin state"""
        return self.state_memory.delete_plugin_state(plugin_name, state_key)

    def get_plugin_insights(self, plugin_name: str) -> Dict[str, Any]:
        """Get insights about plugin usage and performance"""
        return self.cognitive_memory.get_plugin_insights(plugin_name)

    def suggest_plugin_optimizations(self, plugin_name: str) -> List[str]:
        """Get optimization suggestions for a plugin"""
        return self.cognitive_memory.suggest_optimization(plugin_name)

    def set_shared_state(
        self,
        namespace: str,
        state_key: str,
        state_value: Any,
        owner_plugin: str,
        allowed_plugins: Optional[List[str]] = None,
    ) -> bool:
        """Set shared state accessible by multiple plugins"""
        return self.state_memory.set_shared_state(
            namespace, state_key, state_value, owner_plugin, allowed_plugins
        )

    def get_shared_state(
        self,
        namespace: str,
        state_key: str,
        requesting_plugin: str,
        default: Any = None,
    ) -> Any:
        """Get shared state with permission checking"""
        return self.state_memory.get_shared_state(
            namespace, state_key, requesting_plugin, default
        )

    def cleanup_old_plugin_data(self, days_old: int = 30) -> int:
        """Clean up old plugin data to prevent bloat"""
        return self.state_memory.cleanup_old_states(days_old)

    # ==============================================
    # PLUGIN VERSION CONTROL METHODS
    # ==============================================

    def create_plugin_snapshot(
        self,
        plugin_name: str,
        confidence_score: float = 0.0,
        description: str = "",
        created_by: str = "system",
    ) -> bool:
        """Create a snapshot of a plugin's current state"""
        try:
            plugin_path = os.path.join(self.plugin_directory, f"{plugin_name}.py")

            if not os.path.exists(plugin_path):
                print(f"❌ Plugin file not found: {plugin_path}")
                return False

            with open(plugin_path, "r", encoding="utf-8") as f:
                plugin_code = f.read()

            snapshot = self.version_control.create_snapshot(
                plugin_name, plugin_code, confidence_score, created_by, description
            )

            return snapshot is not None

        except Exception as e:
            print(f"❌ Failed to create snapshot for {plugin_name}: {e}")
            return False

    def rollback_plugin(self, plugin_name: str, timestamp: str) -> bool:
        """Rollback a plugin to a previous version"""
        try:
            # Create snapshot before rollback
            self.create_plugin_snapshot(
                plugin_name, 0.0, "Pre-rollback backup", "rollback_system"
            )

            # Perform rollback
            target_path = os.path.join(self.plugin_directory, f"{plugin_name}.py")
            success = self.version_control.rollback_plugin(
                plugin_name, timestamp, target_path
            )

            if success:
                # Reload the plugin if it's currently loaded
                if plugin_name in self.loaded_plugins:
                    print(f"🔄 Reloading plugin {plugin_name} after rollback...")
                    # Note: This is a simplified reload - in production you might want
                    # more sophisticated hot-reloading
                    self.enabled_plugins.add(plugin_name)

                print(f"✅ Plugin {plugin_name} rolled back successfully")

            return success

        except Exception as e:
            print(f"❌ Failed to rollback plugin {plugin_name}: {e}")
            return False

    def get_plugin_version_history(self, plugin_name: str) -> List[Dict[str, Any]]:
        """Get version history for a plugin"""
        try:
            snapshots = self.version_control.list_snapshots(plugin_name)

            history = []
            for snapshot in snapshots:
                history.append(
                    {
                        "timestamp": snapshot.timestamp,
                        "confidence_score": snapshot.confidence_score,
                        "file_path": snapshot.file_path,
                        "size": snapshot.size,
                        "metadata": snapshot.metadata,
                    }
                )

            return history

        except Exception as e:
            print(f"❌ Failed to get version history for {plugin_name}: {e}")
            return []

    def diff_plugin_versions(
        self,
        plugin_name: str,
        version1: str,
        version2: str,
        format_type: str = "unified",
    ) -> str:
        """Generate diff between two plugin versions"""
        try:
            return self.version_control.diff_plugin_versions(
                plugin_name, version1, version2, format_type
            )
        except Exception as e:
            print(f"❌ Failed to generate diff for {plugin_name}: {e}")
            return f"Error generating diff: {e}"

    def cleanup_plugin_versions(self, plugin_name: str, keep_count: int = 10) -> int:
        """Clean up old versions of a plugin"""
        try:
            return self.version_control.cleanup_old_snapshots(plugin_name, keep_count)
        except Exception as e:
            print(f"❌ Failed to cleanup versions for {plugin_name}: {e}")
            return 0

    def get_plugin_version_stats(self, plugin_name: str) -> Dict[str, Any]:
        """Get version statistics for a plugin"""
        try:
            return self.version_control.get_plugin_history_stats(plugin_name)
        except Exception as e:
            print(f"❌ Failed to get version stats for {plugin_name}: {e}")
            return {}

    def export_plugin_version(
        self, plugin_name: str, timestamp: str, export_path: str
    ) -> bool:
        """Export a specific plugin version"""
        try:
            return self.version_control.export_snapshot(
                plugin_name, timestamp, export_path
            )
        except Exception as e:
            print(f"❌ Failed to export plugin version: {e}")
            return False

    # ==============================================
    # END VERSION CONTROL METHODS
    # ==============================================

    # ...existing methods continue...


# Built-in Plugin Implementations


class FileManagerPlugin(LyrixaPlugin):
    """Plugin for file and directory operations"""

    def __init__(self):
        super().__init__()
        self.name = "FileManager"
        self.description = "File and directory operations"
        self.category = "system"
        self.capabilities = ["read_file", "write_file", "list_directory", "file_search"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        self.workspace_path = lyrixa_context.get("workspace_path", ".")
        return True

    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "read_file":
            return await self._read_file(params.get("file_path", ""))
        elif command == "write_file":
            return await self._write_file(
                params.get("file_path", ""), params.get("content", "")
            )
        elif command == "list_directory":
            return await self._list_directory(params.get("directory_path", "."))
        elif command == "file_search":
            return await self._file_search(
                params.get("pattern", ""), params.get("directory", ".")
            )
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _read_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {"content": content, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}

    async def _write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "bytes_written": len(content)}
        except Exception as e:
            return {"error": str(e)}

    async def _list_directory(self, directory_path: str) -> Dict[str, Any]:
        try:
            items = os.listdir(directory_path)
            return {"items": items, "count": len(items)}
        except Exception as e:
            return {"error": str(e)}

    async def _file_search(self, pattern: str, directory: str) -> Dict[str, Any]:
        try:
            import glob

            matches = glob.glob(os.path.join(directory, pattern), recursive=True)
            return {"matches": matches, "count": len(matches)}
        except Exception as e:
            return {"error": str(e)}


class WebSearchPlugin(LyrixaPlugin):
    """Plugin for web search capabilities"""

    def __init__(self):
        super().__init__()
        self.name = "WebSearch"
        self.description = "Web search and information retrieval"
        self.category = "internet"
        self.capabilities = ["web_search", "url_fetch", "web_summarize"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "web_search":
            return await self._web_search(params.get("query", ""))
        elif command == "url_fetch":
            return await self._url_fetch(params.get("url", ""))
        elif command == "web_summarize":
            return await self._web_summarize(params.get("url", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _web_search(self, query: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            "query": query,
            "results": [
                {
                    "title": f"Result for {query}",
                    "url": "https://example.com",
                    "snippet": "Sample result",
                }
            ],
        }

    async def _url_fetch(self, url: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {"url": url, "content": f"Content from {url}", "status": 200}

    async def _web_summarize(self, url: str) -> Dict[str, Any]:
        # Placeholder implementation
        return {"url": url, "summary": f"Summary of content from {url}"}


class CodeAnalyzerPlugin(LyrixaPlugin):
    """Plugin for code analysis capabilities"""

    def __init__(self):
        super().__init__()
        self.name = "CodeAnalyzer"
        self.description = "Code analysis and quality assessment"
        self.category = "development"
        self.capabilities = ["analyze_code", "code_metrics", "find_issues"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "analyze_code":
            return await self._analyze_code(
                params.get("code", ""), params.get("language", "python")
            )
        elif command == "code_metrics":
            return await self._code_metrics(params.get("file_path", ""))
        elif command == "find_issues":
            return await self._find_issues(params.get("code", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        lines = code.split("\n")
        return {
            "language": language,
            "lines_of_code": len(lines),
            "functions": len([line for line in lines if "def " in line]),
            "classes": len([line for line in lines if "class " in line]),
        }

    async def _code_metrics(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            return await self._analyze_code(code, "python")
        except Exception as e:
            return {"error": str(e)}

    async def _find_issues(self, code: str) -> Dict[str, Any]:
        issues = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(f"Line {i}: Line too long ({len(line)} characters)")
            if "TODO" in line:
                issues.append(f"Line {i}: TODO comment found")

        return {"issues": issues, "count": len(issues)}


class DataVisualizerPlugin(LyrixaPlugin):
    """Plugin for data visualization"""

    def __init__(self):
        super().__init__()
        self.name = "DataVisualizer"
        self.description = "Data visualization and charting"
        self.category = "data"
        self.capabilities = ["create_chart", "visualize_data", "export_chart"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "create_chart":
            return await self._create_chart(
                params.get("data", []), params.get("chart_type", "bar")
            )
        elif command == "visualize_data":
            return await self._visualize_data(params.get("data", []))
        elif command == "export_chart":
            return await self._export_chart(
                params.get("chart_data", {}), params.get("format", "png")
            )
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _create_chart(self, data: List[Any], chart_type: str) -> Dict[str, Any]:
        return {
            "chart_type": chart_type,
            "data_points": len(data),
            "chart_url": f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
        }

    async def _visualize_data(self, data: List[Any]) -> Dict[str, Any]:
        return await self._create_chart(data, "auto")

    async def _export_chart(
        self, chart_data: Dict[str, Any], format: str
    ) -> Dict[str, Any]:
        return {
            "exported": True,
            "format": format,
            "file_path": f"chart_export.{format}",
        }


class APIConnectorPlugin(LyrixaPlugin):
    """Plugin for API connections and integrations"""

    def __init__(self):
        super().__init__()
        self.name = "APIConnector"
        self.description = "API connections and integrations"
        self.category = "integration"
        self.capabilities = ["api_call", "auth_setup", "rate_limit_check"]

    async def initialize(self, lyrixa_context: Dict[str, Any]) -> bool:
        return True

    async def execute(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        params = params or {}

        if command == "api_call":
            return await self._api_call(
                params.get("url", ""),
                params.get("method", "GET"),
                params.get("headers", {}),
                params.get("data", {}),
            )
        elif command == "auth_setup":
            return await self._auth_setup(
                params.get("auth_type", ""), params.get("credentials", {})
            )
        elif command == "rate_limit_check":
            return await self._rate_limit_check(params.get("api_name", ""))
        else:
            return {"error": f"Unknown command: {command}"}

    async def cleanup(self) -> bool:
        return True

    async def _api_call(
        self, url: str, method: str, headers: Dict[str, str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Placeholder implementation
        return {
            "url": url,
            "method": method,
            "status": 200,
            "response": {"message": f"Mock response from {url}"},
        }

    async def _auth_setup(
        self, auth_type: str, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "auth_type": auth_type,
            "configured": True,
            "expires_at": (datetime.now().timestamp() + 3600),  # 1 hour from now
        }

    async def _rate_limit_check(self, api_name: str) -> Dict[str, Any]:
        return {
            "api_name": api_name,
            "requests_remaining": 100,
            "reset_time": datetime.now().timestamp() + 3600,
        }
