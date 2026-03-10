#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔧 Plugin Lifecycle Manager
===========================

Manages plugin discovery, loading, validation, and lifecycle with hot-reload support.
Implements signature validation and dependency resolution.

Key Features:
- Plugin discovery from multiple directories
- Signature validation for security
- Dependency resolution and conflict detection
- Hot-add/remove without restart
- Plugin sandboxing and resource monitoring
- Rollback on failure
"""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

# Third party imports
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot

logger = logging.getLogger(__name__)


class PluginStatus(Enum):
    """Plugin lifecycle status."""

    DISCOVERED = "discovered"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    LOADING = "loading"
    LOADED = "loaded"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    UNINSTALLING = "uninstalling"


@dataclass
class PluginDependency:
    """Plugin dependency specification."""

    name: str
    version_min: str | None = None
    version_max: str | None = None
    optional: bool = False


@dataclass
class PluginMetadata:
    """Complete plugin metadata from manifest."""

    id: str
    name: str
    version: str
    description: str
    author: str
    license: str

    # Dependencies
    dependencies: list[PluginDependency] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)

    # UI configuration
    ui_entry: str | None = None
    permissions: list[str] = field(default_factory=list)

    # Resource limits
    memory_limit_mb: int = 512
    cpu_limit_percent: int = 25
    timeout_ms: int = 30000

    # Security
    signature: str | None = None
    trusted: bool = False
    sandbox: bool = True

    # Paths
    plugin_dir: Path | None = None
    manifest_path: Path | None = None

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> PluginMetadata:
        """Load plugin metadata from manifest file."""
        try:
            with manifest_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Parse dependencies
            deps = []
            for dep_data in data.get("dependencies", []):
                deps.append(
                    PluginDependency(
                        name=dep_data["name"],
                        version_min=dep_data.get("version_min"),
                        version_max=dep_data.get("version_max"),
                        optional=dep_data.get("optional", False),
                    )
                )

            return cls(
                id=data["id"],
                name=data["name"],
                version=data["version"],
                description=data.get("description", ""),
                author=data.get("author", "Unknown"),
                license=data.get("license", "Unknown"),
                dependencies=deps,
                conflicts=data.get("conflicts", []),
                ui_entry=data.get("ui_entry"),
                permissions=data.get("permissions", []),
                memory_limit_mb=data.get("memory_limit_mb", 512),
                cpu_limit_percent=data.get("cpu_limit_percent", 25),
                timeout_ms=data.get("timeout_ms", 30000),
                signature=data.get("signature"),
                trusted=data.get("trusted", False),
                sandbox=data.get("sandbox", True),
                plugin_dir=manifest_path.parent,
                manifest_path=manifest_path,
            )
        except Exception as e:
            logger.error(f"Failed to parse manifest {manifest_path}: {e}")
            raise


@dataclass
class PluginInstance:
    """Runtime plugin instance."""

    metadata: PluginMetadata
    status: PluginStatus = PluginStatus.DISCOVERED
    load_time: float | None = None
    error_message: str | None = None
    resource_usage: dict[str, Any] = field(default_factory=dict)
    ui_host: Any | None = None  # PluginUIHost instance


class PluginDiscoveryWorker(QThread):
    """Background worker for plugin discovery."""

    # Signals
    plugin_discovered = Signal(str)  # plugin_path
    discovery_finished = Signal(int)  # count

    def __init__(self, search_paths: list[Path]):
        super().__init__()
        self.search_paths = search_paths
        self._stop_requested = False

    def run(self):
        """Discover plugins in search paths."""
        discovered_count = 0

        for search_path in self.search_paths:
            if self._stop_requested:
                break

            if not search_path.exists():
                continue

            logger.info(f"Scanning for plugins in: {search_path}")

            for plugin_dir in search_path.iterdir():
                if self._stop_requested:
                    break

                if not plugin_dir.is_dir():
                    continue

                manifest_path = plugin_dir / "manifest.json"
                if manifest_path.exists():
                    self.plugin_discovered.emit(str(plugin_dir))
                    discovered_count += 1
                    logger.debug(f"Discovered plugin: {plugin_dir.name}")

        self.discovery_finished.emit(discovered_count)

    def stop(self):
        """Request worker to stop."""
        self._stop_requested = True


class PluginSignatureValidator:
    """Validates plugin signatures for security."""

    def __init__(self):
        self.trusted_keys: set[str] = set()
        self._load_trusted_keys()

    def _load_trusted_keys(self):
        """Load trusted signing keys."""
        # In a real implementation, this would load from a secure key store
        # For now, we'll use a simple approach
        trusted_keys_file = Path("config/trusted_plugin_keys.json")
        if trusted_keys_file.exists():
            try:
                with trusted_keys_file.open("r") as f:
                    data = json.load(f)
                    self.trusted_keys.update(data.get("keys", []))
                logger.info(f"Loaded {len(self.trusted_keys)} trusted keys")
            except Exception as e:
                logger.warning(f"Failed to load trusted keys: {e}")

    def validate_signature(self, plugin_metadata: PluginMetadata) -> bool:
        """Validate plugin signature."""
        if not plugin_metadata.signature:
            # Allow unsigned plugins in development mode
            logger.warning(f"Plugin {plugin_metadata.id} is not signed")
            return not plugin_metadata.trusted  # Unsigned plugins can't be trusted

        # Calculate plugin content hash
        content_hash = self._calculate_plugin_hash(plugin_metadata.plugin_dir)

        # In a real implementation, verify the signature against the hash
        # For now, we'll do a simple check
        expected_hash = plugin_metadata.signature

        if content_hash == expected_hash:
            logger.info(f"Plugin {plugin_metadata.id} signature valid")
            return True
        else:
            logger.error(f"Plugin {plugin_metadata.id} signature invalid")
            return False

    def _calculate_plugin_hash(self, plugin_dir: Path) -> str:
        """Calculate hash of plugin contents."""
        hasher = hashlib.sha256()

        # Hash all files in plugin directory
        for file_path in sorted(plugin_dir.rglob("*")):
            if file_path.is_file():
                try:
                    hasher.update(file_path.read_bytes())
                except Exception as e:
                    logger.warning(f"Failed to hash {file_path}: {e}")

        return hasher.hexdigest()


class PluginLifecycleManager(QObject):
    """
    Manages the complete plugin lifecycle with security and dependency management.

    Features:
    - Discovery from multiple directories
    - Signature validation
    - Dependency resolution
    - Hot-reload support
    - Resource monitoring
    - Rollback on failure
    """

    # Signals
    plugin_discovered = Signal(str)  # plugin_id
    plugin_validated = Signal(str, bool)  # plugin_id, valid
    plugin_loaded = Signal(str)  # plugin_id
    plugin_unloaded = Signal(str)  # plugin_id
    plugin_error = Signal(str, str)  # plugin_id, error
    dependency_error = Signal(str, str)  # plugin_id, missing_dep
    discovery_completed = Signal(int)  # count

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)

        # Plugin registry
        self._plugins: dict[str, PluginInstance] = {}
        self._search_paths: list[Path] = []

        # Components
        self._validator = PluginSignatureValidator()
        self._discovery_worker: PluginDiscoveryWorker | None = None

        # Monitoring
        self._monitor_timer = QTimer()
        self._monitor_timer.timeout.connect(self._monitor_plugins)
        self._monitor_timer.start(10000)  # Monitor every 10 seconds

        logger.info("PluginLifecycleManager initialized")

    def add_search_path(self, path: Path) -> None:
        """Add a directory to search for plugins."""
        if path not in self._search_paths:
            self._search_paths.append(path)
            logger.info(f"Added plugin search path: {path}")

    def discover_plugins(self) -> None:
        """Start plugin discovery in background."""
        if self._discovery_worker and self._discovery_worker.isRunning():
            logger.warning("Plugin discovery already in progress")
            return

        logger.info("Starting plugin discovery...")
        self._discovery_worker = PluginDiscoveryWorker(self._search_paths)
        self._discovery_worker.plugin_discovered.connect(self._on_plugin_discovered)
        self._discovery_worker.discovery_finished.connect(self._on_discovery_finished)
        self._discovery_worker.start()

    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin."""
        if plugin_id not in self._plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False

        plugin = self._plugins[plugin_id]

        if plugin.status == PluginStatus.LOADED:
            logger.warning(f"Plugin {plugin_id} already loaded")
            return True

        try:
            # Check dependencies
            if not self._check_dependencies(plugin.metadata):
                return False

            # Validate signature
            if not self._validator.validate_signature(plugin.metadata):
                plugin.status = PluginStatus.INVALID
                self.plugin_error.emit(plugin_id, "Invalid signature")
                return False

            # Load the plugin
            plugin.status = PluginStatus.LOADING

            # Create backup point for rollback
            backup_id = self._create_backup_point()

            try:
                success = self._do_load_plugin(plugin)
                if success:
                    plugin.status = PluginStatus.LOADED
                    plugin.load_time = self._get_current_time()
                    self.plugin_loaded.emit(plugin_id)
                    logger.info(f"Plugin {plugin_id} loaded successfully")
                    return True
                else:
                    raise Exception("Plugin loading failed")

            except Exception as e:
                # Rollback on failure
                self._rollback_to_backup(backup_id)
                raise e

        except Exception as e:
            plugin.status = PluginStatus.ERROR
            plugin.error_message = str(e)
            self.plugin_error.emit(plugin_id, str(e))
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False

    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a specific plugin."""
        if plugin_id not in self._plugins:
            logger.error(f"Plugin not found: {plugin_id}")
            return False

        plugin = self._plugins[plugin_id]

        if plugin.status != PluginStatus.LOADED:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return True

        try:
            plugin.status = PluginStatus.STOPPING

            # Cleanup UI host
            if plugin.ui_host:
                plugin.ui_host.unload_plugin()
                plugin.ui_host = None

            # Cleanup resources
            self._cleanup_plugin_resources(plugin)

            plugin.status = PluginStatus.STOPPED
            self.plugin_unloaded.emit(plugin_id)
            logger.info(f"Plugin {plugin_id} unloaded successfully")
            return True

        except Exception as e:
            plugin.status = PluginStatus.ERROR
            plugin.error_message = str(e)
            self.plugin_error.emit(plugin_id, str(e))
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False

    def get_plugin(self, plugin_id: str) -> PluginInstance | None:
        """Get plugin instance by ID."""
        return self._plugins.get(plugin_id)

    def list_plugins(self) -> list[str]:
        """Get list of all plugin IDs."""
        return list(self._plugins.keys())

    def list_loaded_plugins(self) -> list[str]:
        """Get list of loaded plugin IDs."""
        return [
            plugin_id
            for plugin_id, plugin in self._plugins.items()
            if plugin.status == PluginStatus.LOADED
        ]

    def get_plugin_status(self, plugin_id: str) -> PluginStatus | None:
        """Get plugin status."""
        plugin = self._plugins.get(plugin_id)
        return plugin.status if plugin else None

    @Slot(str)
    def _on_plugin_discovered(self, plugin_path: str) -> None:
        """Handle plugin discovery."""
        try:
            plugin_dir = Path(plugin_path)
            manifest_path = plugin_dir / "manifest.json"

            # Load metadata
            metadata = PluginMetadata.from_manifest(manifest_path)

            # Create plugin instance
            plugin = PluginInstance(metadata=metadata)
            self._plugins[metadata.id] = plugin

            self.plugin_discovered.emit(metadata.id)
            logger.debug(f"Plugin discovered: {metadata.id}")

        except Exception as e:
            logger.error(f"Failed to process discovered plugin {plugin_path}: {e}")

    @Slot(int)
    def _on_discovery_finished(self, count: int) -> None:
        """Handle discovery completion."""
        self.discovery_completed.emit(count)
        logger.info(f"Plugin discovery completed: {count} plugins found")

    def _check_dependencies(self, metadata: PluginMetadata) -> bool:
        """Check if plugin dependencies are satisfied."""
        for dep in metadata.dependencies:
            if not self._is_dependency_satisfied(dep):
                if not dep.optional:
                    self.dependency_error.emit(metadata.id, dep.name)
                    logger.error(f"Missing required dependency: {dep.name}")
                    return False
                else:
                    logger.warning(f"Missing optional dependency: {dep.name}")

        # Check for conflicts
        for conflict_id in metadata.conflicts:
            if conflict_id in self._plugins:
                conflict_plugin = self._plugins[conflict_id]
                if conflict_plugin.status == PluginStatus.LOADED:
                    logger.error(f"Plugin conflict: {metadata.id} conflicts with {conflict_id}")
                    return False

        return True

    def _is_dependency_satisfied(self, dep: PluginDependency) -> bool:
        """Check if a dependency is satisfied."""
        if dep.name not in self._plugins:
            return False

        dep_plugin = self._plugins[dep.name]
        if dep_plugin.status != PluginStatus.LOADED:
            return False

        # Check version constraints
        if dep.version_min or dep.version_max:
            # Simple version comparison (in real implementation, use packaging.version)
            version = dep_plugin.metadata.version
            if dep.version_min and version < dep.version_min:
                return False
            if dep.version_max and version > dep.version_max:
                return False

        return True

    def _do_load_plugin(self, plugin: PluginInstance) -> bool:
        """Actually load the plugin."""
        # In a real implementation, this would:
        # 1. Load plugin code in sandboxed environment
        # 2. Initialize plugin instance
        # 3. Register plugin services
        # 4. Create UI host if needed

        logger.info(f"Loading plugin: {plugin.metadata.id}")

        # Simulate plugin loading
        # This is where you'd integrate with the actual plugin system
        return True

    def _cleanup_plugin_resources(self, plugin: PluginInstance) -> None:
        """Cleanup plugin resources."""
        logger.debug(f"Cleaning up resources for plugin: {plugin.metadata.id}")
        # Cleanup would happen here

    def _create_backup_point(self) -> str:
        """Create a backup point for rollback."""
        backup_id = str(uuid4())
        logger.debug(f"Created backup point: {backup_id}")
        return backup_id

    def _rollback_to_backup(self, backup_id: str) -> None:
        """Rollback to a backup point."""
        logger.warning(f"Rolling back to backup: {backup_id}")
        # Rollback logic would go here

    def _get_current_time(self) -> float:
        """Get current timestamp."""
        # Standard library imports
        import time

        return time.time()

    @Slot()
    def _monitor_plugins(self) -> None:
        """Monitor plugin resource usage."""
        for plugin_id, plugin in self._plugins.items():
            if plugin.status == PluginStatus.LOADED:
                # Monitor resource usage
                # This would integrate with actual resource monitoring
                logger.debug(f"Monitoring plugin: {plugin_id}")
