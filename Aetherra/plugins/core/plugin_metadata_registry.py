"""
Plugin Metadata & Registry - Enhanced plugin discovery and dependency resolution.

Provides comprehensive plugin metadata management:
  - Rich plugin metadata with schemas, tags, hooks
  - Registry with search by capability/tag/category
  - Dependency resolution and ordering
  - Version tracking and conflict detection

Complements the existing plugin_registry.py (which handles discovery) with
a higher-level metadata management layer.

Example:
    >>> registry = PluginRegistryManager()
    >>> registry.register(PluginMetadataRecord(name="my_plugin", ...))
    >>> results = registry.find_by_capability("data-processing")
    >>> deps = registry.resolve_dependencies("my_plugin")
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadataRecord:
    """Rich plugin metadata record."""

    name: str
    """Unique plugin identifier"""
    version: str = "1.0.0"
    """Semantic version string"""
    description: str = ""
    """Human-readable description"""
    author: str = "Unknown"
    """Author name"""
    category: str = "general"
    """Plugin category"""
    capabilities: List[str] = field(default_factory=list)
    """List of capability strings plugin provides"""
    dependencies: List[str] = field(default_factory=list)
    """Plugin names this plugin requires"""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    """JSON schema for plugin input"""
    output_schema: Dict[str, Any] = field(default_factory=dict)
    """JSON schema for plugin output"""
    tags: List[str] = field(default_factory=list)
    """Searchable tags"""
    hooks: List[str] = field(default_factory=list)
    """Lifecycle hooks plugin registers"""
    ui_elements: Optional[Dict] = None
    """UI configuration (optional)"""
    enabled: bool = True
    """Whether plugin is enabled"""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """ISO timestamp of registration"""
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    """ISO timestamp of last update"""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadataRecord":
        """Create from dictionary."""
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


@dataclass
class RegistrySearchResult:
    """Result of a registry search."""

    plugins: List[PluginMetadataRecord]
    """Matching plugins"""
    query: str
    """Search query used"""
    total_found: int = 0
    """Total number of matches"""

    def __post_init__(self):
        self.total_found = len(self.plugins)


class PluginRegistryManager:
    """
    Enhanced plugin registry with search and dependency resolution.

    Manages plugin metadata in-memory and optionally persists to JSON.
    Complements the discovery-focused plugin_registry.py.
    """

    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize registry.

        Args:
            registry_path: Optional path for JSON persistence
        """
        self._plugins: Dict[str, PluginMetadataRecord] = {}
        self.registry_path = Path(registry_path) if registry_path else None
        if self.registry_path and self.registry_path.exists():
            self._load()
        logger.info("PluginRegistryManager initialized")

    def register(self, plugin: PluginMetadataRecord) -> bool:
        """
        Register a plugin in the registry.

        Args:
            plugin: Plugin metadata to register

        Returns:
            True if registered successfully
        """
        if not plugin.name:
            raise ValueError("Plugin name is required")

        is_update = plugin.name in self._plugins
        plugin.updated_at = datetime.now().isoformat()
        self._plugins[plugin.name] = plugin

        if self.registry_path:
            self._save()

        action = "Updated" if is_update else "Registered"
        logger.info(f"{action} plugin: {plugin.name} v{plugin.version}")
        return True

    def unregister(self, name: str) -> bool:
        """
        Remove a plugin from the registry.

        Args:
            name: Plugin name to remove

        Returns:
            True if removed, False if not found
        """
        if name not in self._plugins:
            return False
        del self._plugins[name]
        if self.registry_path:
            self._save()
        logger.info(f"Unregistered plugin: {name}")
        return True

    def get(self, name: str) -> Optional[PluginMetadataRecord]:
        """Get plugin by name."""
        return self._plugins.get(name)

    def list_all(self) -> List[PluginMetadataRecord]:
        """Return all registered plugins."""
        return list(self._plugins.values())

    def find_by_capability(self, capability: str) -> List[PluginMetadataRecord]:
        """
        Search for plugins that provide a specific capability.

        Args:
            capability: Capability string to search for

        Returns:
            List of matching plugins
        """
        cap_lower = capability.lower()
        return [
            p for p in self._plugins.values()
            if any(cap_lower in c.lower() for c in p.capabilities)
            and p.enabled
        ]

    def find_by_tag(self, tag: str) -> List[PluginMetadataRecord]:
        """
        Search for plugins with a specific tag.

        Args:
            tag: Tag string to search for

        Returns:
            List of matching plugins
        """
        tag_lower = tag.lower()
        return [
            p for p in self._plugins.values()
            if any(tag_lower in t.lower() for t in p.tags)
            and p.enabled
        ]

    def find_by_category(self, category: str) -> List[PluginMetadataRecord]:
        """
        Search for plugins in a category.

        Args:
            category: Category name

        Returns:
            List of matching plugins
        """
        cat_lower = category.lower()
        return [
            p for p in self._plugins.values()
            if p.category.lower() == cat_lower and p.enabled
        ]

    def search(self, query: str) -> RegistrySearchResult:
        """
        Full-text search across name, description, tags, capabilities.

        Args:
            query: Search query string

        Returns:
            RegistrySearchResult with matching plugins
        """
        query_lower = query.lower()
        matches = []

        for plugin in self._plugins.values():
            if not plugin.enabled:
                continue

            # Search across multiple fields
            searchable = " ".join([
                plugin.name,
                plugin.description,
                plugin.category,
                " ".join(plugin.tags),
                " ".join(plugin.capabilities),
            ]).lower()

            if query_lower in searchable:
                matches.append(plugin)

        return RegistrySearchResult(plugins=matches, query=query)

    def resolve_dependencies(self, plugin_name: str) -> List[str]:
        """
        Resolve full dependency tree for a plugin in topological order.

        Args:
            plugin_name: Name of plugin to resolve

        Returns:
            Ordered list of dependency names (deepest first)

        Raises:
            ValueError: If circular dependency detected or dependency not found
        """
        resolved: List[str] = []
        visited: Set[str] = set()
        in_progress: Set[str] = set()

        def _resolve(name: str):
            if name in in_progress:
                raise ValueError(f"Circular dependency: {name}")
            if name in visited:
                return

            in_progress.add(name)
            plugin = self._plugins.get(name)

            if plugin:
                for dep in plugin.dependencies:
                    _resolve(dep)

            in_progress.discard(name)
            visited.add(name)
            if name != plugin_name:
                resolved.append(name)

        _resolve(plugin_name)
        return resolved

    def find_conflicts(self, plugin_name: str) -> List[str]:
        """
        Find plugins that may conflict with the given plugin.

        Simple conflict detection: plugins providing same capabilities
        may conflict if they are in the same category.

        Args:
            plugin_name: Plugin to check for conflicts

        Returns:
            List of potentially conflicting plugin names
        """
        plugin = self._plugins.get(plugin_name)
        if not plugin:
            return []

        conflicts = []
        for name, other in self._plugins.items():
            if name == plugin_name:
                continue
            # Conflict if same category and overlapping capabilities
            if other.category == plugin.category:
                overlap = set(plugin.capabilities) & set(other.capabilities)
                if overlap:
                    conflicts.append(name)

        return conflicts

    def export_json(self) -> str:
        """Export entire registry as JSON string."""
        data = {
            "registry_version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "plugins": [p.to_dict() for p in self._plugins.values()],
        }
        return json.dumps(data, indent=2)

    def import_json(self, json_str: str) -> int:
        """
        Import plugins from JSON string.

        Args:
            json_str: JSON string with plugin definitions

        Returns:
            Number of plugins imported
        """
        data = json.loads(json_str)
        plugins = data.get("plugins", [])
        count = 0
        for plugin_data in plugins:
            plugin = PluginMetadataRecord.from_dict(plugin_data)
            self.register(plugin)
            count += 1
        return count

    def _save(self):
        """Persist registry to JSON file."""
        if not self.registry_path:
            return
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, "w", encoding="utf-8") as f:
            f.write(self.export_json())

    def _load(self):
        """Load registry from JSON file."""
        if not self.registry_path or not self.registry_path.exists():
            return
        if self.registry_path.stat().st_size == 0:
            return
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for plugin_data in data.get("plugins", []):
            plugin = PluginMetadataRecord.from_dict(plugin_data)
            self._plugins[plugin.name] = plugin
        logger.info(f"Loaded {len(self._plugins)} plugins from {self.registry_path}")
