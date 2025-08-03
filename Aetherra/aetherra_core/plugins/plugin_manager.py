#!/usr/bin/env python3
"""
[PLUGIN] Aetherra Plugin Manager
==========================
Plugin system management for Aetherra AI OS.

Handles plugin loading, execution, lifecycle management, and coordination
with the Aetherra Hub marketplace.
"""

import asyncio
import importlib.util
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin status enumeration."""
    UNKNOWN = "unknown"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"


class PluginType(Enum):
    """Plugin type enumeration."""
    PYTHON = "python"
    AETHERPLUG = "aetherplug"
    NATIVE = "native"
    HYBRID = "hybrid"


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = "Unknown"
    license: str = "MIT"
    plugin_type: PluginType = PluginType.PYTHON
    entry_point: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    category: str = "utility"
    min_aetherra_version: str = "1.0.0"
    max_aetherra_version: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None


@dataclass
class PluginInstance:
    """A loaded plugin instance."""
    metadata: PluginMetadata
    module: Optional[Any] = None
    instance: Optional[Any] = None
    status: PluginStatus = PluginStatus.UNKNOWN
    load_time: Optional[datetime] = None
    error_message: Optional[str] = None
    file_path: Optional[Path] = None


class PluginManager:
    """
    [PLUGIN] Aetherra Plugin Manager

    Manages the loading, execution, and lifecycle of plugins within
    the Aetherra AI Operating System.
    """

    def __init__(self, plugin_directories: Optional[List[Union[str, Path]]] = None):
        self.plugin_directories = [Path(d) for d in (plugin_directories or ["Aetherra/plugins"])]
        self.loaded_plugins: Dict[str, PluginInstance] = {}
        self.active_plugins: Set[str] = set()
        self.plugin_hooks: Dict[str, List[str]] = {}  # Hook name -> list of plugin names
        self._initialized = False

    async def initialize(self):
        """Initialize the plugin manager."""
        if self._initialized:
            logger.warning("Plugin manager already initialized")
            return

        logger.info("[PLUGIN] Initializing Aetherra Plugin Manager...")

        # Plugin directories are already Path objects from __init__

        # Create plugin directories if they don't exist
        for directory in self.plugin_directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📁 Plugin directory: {directory}")

        self._initialized = True
        logger.info("[OK] Plugin Manager initialized")

    async def discover_plugins(self) -> List[PluginMetadata]:
        """Discover all available plugins in the plugin directories."""
        if not self._initialized:
            await self.initialize()

        logger.info("[DISC] Discovering plugins...")
        discovered = []

        for directory in self.plugin_directories:
            if not directory.exists():
                logger.warning(f"[WARN] Plugin directory not found: {directory}")
                continue

            # Look for Python files
            for py_file in directory.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    metadata = await self._extract_plugin_metadata(py_file)
                    if metadata:
                        discovered.append(metadata)
                        logger.debug(f"[DISC] Discovered plugin: {metadata.name}")
                except Exception as e:
                    logger.error(f"[ERROR] Error discovering plugin {py_file}: {e}")

            # Look for .aetherplug directories
            for aether_dir in directory.rglob("*/"):
                manifest_file = aether_dir / "aetherra-plugin.json"
                if manifest_file.exists():
                    try:
                        metadata = await self._load_aetherplug_manifest(manifest_file)
                        if metadata:
                            discovered.append(metadata)
                            logger.debug(f"[DISC] Discovered .aetherplug: {metadata.name}")
                    except Exception as e:
                        logger.error(f"[ERROR] Error loading .aetherplug {manifest_file}: {e}")

        logger.info(f"[OK] Discovered {len(discovered)} plugins")
        return discovered

    async def load_plugin(self, plugin_name: str, plugin_path: Optional[Path] = None) -> bool:
        """Load a specific plugin."""
        if plugin_name in self.loaded_plugins:
            logger.warning(f"[WARN] Plugin '{plugin_name}' already loaded")
            return True

        logger.info(f"[LOAD] Loading plugin: {plugin_name}")

        try:
            # Find the plugin if path not provided
            if plugin_path is None:
                plugin_path = await self._find_plugin_path(plugin_name)
                if plugin_path is None:
                    logger.error(f"[ERROR] Plugin '{plugin_name}' not found")
                    return False

            # Extract metadata
            metadata = await self._extract_plugin_metadata(plugin_path)
            if metadata is None:
                logger.error(f"[ERROR] Could not extract metadata for '{plugin_name}'")
                return False

            # Load the plugin module
            plugin_instance = PluginInstance(metadata=metadata, file_path=plugin_path)

            if plugin_path.suffix == ".py":
                # Python plugin
                success = await self._load_python_plugin(plugin_instance)
            else:
                # Other plugin types
                success = await self._load_other_plugin(plugin_instance)

            if success:
                plugin_instance.status = PluginStatus.LOADED
                plugin_instance.load_time = datetime.now()
                self.loaded_plugins[plugin_name] = plugin_instance
                logger.info(f"[OK] Plugin '{plugin_name}' loaded successfully")
                return True
            else:
                logger.error(f"[ERROR] Failed to load plugin '{plugin_name}'")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Error loading plugin '{plugin_name}': {e}")
            return False

    async def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin."""
        if plugin_name not in self.loaded_plugins:
            logger.error(f"[ERROR] Plugin '{plugin_name}' not loaded")
            return False

        if plugin_name in self.active_plugins:
            logger.warning(f"[WARN] Plugin '{plugin_name}' already active")
            return True

        logger.info(f"🔥 Activating plugin: {plugin_name}")

        try:
            plugin_instance = self.loaded_plugins[plugin_name]

            # Call plugin's activate method if available
            if plugin_instance.instance and hasattr(plugin_instance.instance, 'activate'):
                if asyncio.iscoroutinefunction(plugin_instance.instance.activate):
                    await plugin_instance.instance.activate()
                else:
                    plugin_instance.instance.activate()

            plugin_instance.status = PluginStatus.ACTIVE
            self.active_plugins.add(plugin_name)

            logger.info(f"[OK] Plugin '{plugin_name}' activated")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error activating plugin '{plugin_name}': {e}")
            return False

    async def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate an active plugin."""
        if plugin_name not in self.active_plugins:
            logger.warning(f"[WARN] Plugin '{plugin_name}' not active")
            return True

        logger.info(f"💤 Deactivating plugin: {plugin_name}")

        try:
            plugin_instance = self.loaded_plugins[plugin_name]

            # Call plugin's deactivate method if available
            if plugin_instance.instance and hasattr(plugin_instance.instance, 'deactivate'):
                if asyncio.iscoroutinefunction(plugin_instance.instance.deactivate):
                    await plugin_instance.instance.deactivate()
                else:
                    plugin_instance.instance.deactivate()

            plugin_instance.status = PluginStatus.INACTIVE
            self.active_plugins.discard(plugin_name)

            logger.info(f"[OK] Plugin '{plugin_name}' deactivated")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error deactivating plugin '{plugin_name}': {e}")
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.loaded_plugins:
            logger.warning(f"[WARN] Plugin '{plugin_name}' not loaded")
            return True

        # Deactivate first if active
        if plugin_name in self.active_plugins:
            await self.deactivate_plugin(plugin_name)

        logger.info(f"📤 Unloading plugin: {plugin_name}")

        try:
            plugin_instance = self.loaded_plugins[plugin_name]

            # Call plugin's cleanup method if available
            if plugin_instance.instance and hasattr(plugin_instance.instance, 'cleanup'):
                if asyncio.iscoroutinefunction(plugin_instance.instance.cleanup):
                    await plugin_instance.instance.cleanup()
                else:
                    plugin_instance.instance.cleanup()

            # Remove from loaded plugins
            del self.loaded_plugins[plugin_name]

            logger.info(f"[OK] Plugin '{plugin_name}' unloaded")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Error unloading plugin '{plugin_name}': {e}")
            return False

    async def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        logger.info("[LOAD] Loading all discovered plugins...")

        results = {}

        # First discover all available plugins
        discovered_plugins = await self.discover_plugins()
        logger.info(f"[DISC] Found {len(discovered_plugins)} plugins to load")

        # Load each discovered plugin
        for plugin_metadata in discovered_plugins:
            plugin_name = plugin_metadata.name
            try:
                result = await self.load_plugin(plugin_name)
                results[plugin_name] = result
                if result:
                    logger.info(f"[OK] Loaded plugin: {plugin_name}")
                else:
                    logger.error(f"[ERROR] Failed to load plugin: {plugin_name}")
            except Exception as e:
                logger.error(f"[ERROR] Error loading plugin '{plugin_name}': {e}")
                results[plugin_name] = False

        loaded_count = sum(1 for success in results.values() if success)
        logger.info(f"[SUMMARY] Loaded {loaded_count}/{len(discovered_plugins)} plugins successfully")

        return results

    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all loaded plugins with their status."""
        plugin_list = {}

        for name, instance in self.loaded_plugins.items():
            plugin_list[name] = {
                "name": instance.metadata.name,
                "version": instance.metadata.version,
                "description": instance.metadata.description,
                "author": instance.metadata.author,
                "status": instance.status.value,
                "type": instance.metadata.plugin_type.value,
                "category": instance.metadata.category,
                "load_time": instance.load_time.isoformat() if instance.load_time else None,
                "active": name in self.active_plugins,
                "error": instance.error_message
            }

        return plugin_list

    def get_plugin_status(self, plugin_name: str) -> Optional[PluginStatus]:
        """Get the status of a specific plugin."""
        instance = self.loaded_plugins.get(plugin_name)
        return instance.status if instance else None

    async def execute_plugin_method(self, plugin_name: str, method_name: str, *args, **kwargs) -> Any:
        """Execute a method on a specific plugin."""
        if plugin_name not in self.loaded_plugins:
            raise ValueError(f"Plugin '{plugin_name}' not loaded")

        instance = self.loaded_plugins[plugin_name]
        if not hasattr(instance.instance, method_name):
            raise AttributeError(f"Plugin '{plugin_name}' has no method '{method_name}'")

        method = getattr(instance.instance, method_name)

        if asyncio.iscoroutinefunction(method):
            return await method(*args, **kwargs)
        else:
            return method(*args, **kwargs)

    async def _extract_plugin_metadata(self, plugin_path: Path) -> Optional[PluginMetadata]:
        """Extract metadata from a plugin file."""
        try:
            if plugin_path.suffix == ".py":
                return await self._extract_python_metadata(plugin_path)
            else:
                logger.warning(f"[WARN] Unsupported plugin file type: {plugin_path}")
                return None

        except Exception as e:
            logger.error(f"[ERROR] Error extracting metadata from {plugin_path}: {e}")
            return None

    async def _extract_python_metadata(self, py_file: Path) -> Optional[PluginMetadata]:
        """Extract metadata from a Python plugin file."""
        try:
            # Read the file to look for metadata
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try to import and extract metadata
            spec = importlib.util.spec_from_file_location("temp_plugin", py_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Look for plugin_data dictionary
                if hasattr(module, 'plugin_data'):
                    data = module.plugin_data
                    return PluginMetadata(
                        name=data.get('name', py_file.stem),
                        version=data.get('version', '1.0.0'),
                        description=data.get('description', 'No description'),
                        author=data.get('author', 'Unknown'),
                        license=data.get('license', 'MIT'),
                        plugin_type=PluginType.PYTHON,
                        entry_point=data.get('entry_point'),
                        dependencies=data.get('dependencies', []),
                        tags=data.get('tags', []),
                        category=data.get('category', 'utility')
                    )

                # Look for plugin classes
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if hasattr(attr, '__name__') and 'plugin' in attr.__name__.lower():
                        return PluginMetadata(
                            name=getattr(attr, 'name', py_file.stem),
                            version=getattr(attr, 'version', '1.0.0'),
                            description=getattr(attr, 'description', 'No description'),
                            author=getattr(attr, 'author', 'Unknown'),
                            plugin_type=PluginType.PYTHON
                        )

                # Fallback: create basic metadata
                return PluginMetadata(
                    name=py_file.stem,
                    description=f"Plugin loaded from {py_file.name}",
                    plugin_type=PluginType.PYTHON
                )

        except Exception as e:
            logger.error(f"[ERROR] Error extracting Python metadata from {py_file}: {e}")
            return None

    async def _load_aetherplug_manifest(self, manifest_file: Path) -> Optional[PluginMetadata]:
        """Load metadata from an .aetherplug manifest file."""
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            return PluginMetadata(
                name=manifest.get('name', manifest_file.parent.name),
                version=manifest.get('version', '1.0.0'),
                description=manifest.get('description', ''),
                author=manifest.get('author', 'Unknown'),
                license=manifest.get('license', 'MIT'),
                plugin_type=PluginType.AETHERPLUG,
                entry_point=manifest.get('entry_point'),
                dependencies=manifest.get('dependencies', []),
                tags=manifest.get('keywords', []),
                category=manifest.get('category', 'utility'),
                min_aetherra_version=manifest.get('aetherra_version', '1.0.0'),
                homepage=manifest.get('homepage'),
                repository=manifest.get('repository'),
                documentation=manifest.get('documentation')
            )

        except Exception as e:
            logger.error(f"[ERROR] Error loading .aetherplug manifest {manifest_file}: {e}")
            return None

    async def _find_plugin_path(self, plugin_name: str) -> Optional[Path]:
        """Find the path to a plugin by name."""
        for directory in self.plugin_directories:
            # Look for Python file
            py_file = directory / f"{plugin_name}.py"
            if py_file.exists():
                return py_file

            # Look for directory with manifest
            plugin_dir = directory / plugin_name
            manifest_file = plugin_dir / "aetherra-plugin.json"
            if manifest_file.exists():
                return manifest_file

        return None

    async def _load_python_plugin(self, plugin_instance: PluginInstance) -> bool:
        """Load a Python plugin."""
        try:
            plugin_path = plugin_instance.file_path
            if plugin_path is None:
                return False

            spec = importlib.util.spec_from_file_location(plugin_instance.metadata.name, plugin_path)

            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                plugin_instance.module = module
                spec.loader.exec_module(module)

                # Look for plugin class or callable
                plugin_class = None

                # Try to find a plugin class
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (hasattr(attr, '__name__') and
                        'plugin' in attr.__name__.lower() and
                        callable(attr)):
                        plugin_class = attr
                        break

                if plugin_class:
                    plugin_instance.instance = plugin_class()
                else:
                    # Use the module itself as the plugin instance
                    plugin_instance.instance = module

                return True
            else:
                return False

        except Exception as e:
            plugin_instance.error_message = str(e)
            logger.error(f"[ERROR] Error loading Python plugin: {e}")
            return False

    async def _load_other_plugin(self, plugin_instance: PluginInstance) -> bool:
        """Load non-Python plugins (placeholder for future implementation)."""
        logger.warning(f"[WARN] Loading {plugin_instance.metadata.plugin_type.value} plugins not yet implemented")
        return False


# Default plugin manager instance
_default_manager: Optional[PluginManager] = None


async def get_plugin_manager() -> PluginManager:
    """Get the default plugin manager instance."""
    global _default_manager

    if _default_manager is None:
        _default_manager = PluginManager()
        await _default_manager.initialize()

    return _default_manager


# Convenience functions
async def discover_plugins() -> List[PluginMetadata]:
    """Discover plugins using the default manager."""
    manager = await get_plugin_manager()
    return await manager.discover_plugins()


async def load_plugin(plugin_name: str) -> bool:
    """Load a plugin using the default manager."""
    manager = await get_plugin_manager()
    return await manager.load_plugin(plugin_name)


async def activate_plugin(plugin_name: str) -> bool:
    """Activate a plugin using the default manager."""
    manager = await get_plugin_manager()
    return await manager.activate_plugin(plugin_name)


async def list_plugins() -> Dict[str, Dict[str, Any]]:
    """List plugins using the default manager."""
    manager = await get_plugin_manager()
    return manager.list_plugins()


async def load_all_plugins() -> Dict[str, bool]:
    """Load all plugins using the default manager."""
    manager = await get_plugin_manager()
    return await manager.load_all_plugins()

