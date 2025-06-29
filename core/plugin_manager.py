# core/plugin_manager.py
import importlib.util
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PluginMetadata:
    """Plugin metadata for enhanced discovery and transparency"""

    name: str
    description: str = "No description provided"
    capabilities: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "Unknown"
    category: str = "general"
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    last_loaded: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary for serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
            "author": self.author,
            "category": self.category,
            "dependencies": self.dependencies,
            "enabled": self.enabled,
            "last_loaded": self.last_loaded,
        }


# Enhanced plugin registry with metadata
PLUGIN_REGISTRY: Dict[str, Callable] = {}
PLUGIN_METADATA: Dict[str, PluginMetadata] = {}

PLUGIN_DIR = os.path.join(os.path.dirname(__file__), "..", "plugins")
os.makedirs(PLUGIN_DIR, exist_ok=True)


def register_plugin(
    name: str,
    description: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: str = "Unknown",
    category: str = "general",
    dependencies: Optional[List[str]] = None,
):
    """
    Enhanced plugin registration decorator with metadata support

    Args:
        name: Plugin name
        description: Human-readable description of what the plugin does
        capabilities: List of capabilities/features the plugin provides
        version: Plugin version
        author: Plugin author
        category: Plugin category for organization
        dependencies: List of required dependencies
    """

    def decorator(func: Callable) -> Callable:
        # Register the plugin function
        PLUGIN_REGISTRY[name] = func

        # Create and store metadata
        metadata = PluginMetadata(
            name=name,
            description=description or func.__doc__ or "No description provided",
            capabilities=capabilities or [],
            version=version,
            author=author,
            category=category,
            dependencies=dependencies or [],
            enabled=True,
            last_loaded=None,  # Will be set during loading
        )

        PLUGIN_METADATA[name] = metadata
        return func

    return decorator


def load_plugins():
    """Load plugins with enhanced metadata tracking"""
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            filepath = os.path.join(PLUGIN_DIR, filename)
            module_name = filename[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)

            if spec is None:
                print(f"[Plugin Error] Could not create spec for {module_name}")
                continue

            module = importlib.util.module_from_spec(spec)

            if spec.loader is None:
                print(f"[Plugin Error] No loader available for {module_name}")
                continue

            try:
                spec.loader.exec_module(module)

                # Update metadata for all plugins loaded from this module
                current_time = str(datetime.now())
                for _, metadata in PLUGIN_METADATA.items():
                    if metadata.last_loaded is None:  # New plugin
                        metadata.last_loaded = current_time

                print(f"[Plugin] Loaded: {module_name}")
            except Exception as e:
                print(f"[Plugin Error] Failed to load {module_name}: {e}")


def get_plugin(name: str) -> Optional[Callable]:
    """Get a specific plugin by name"""
    return PLUGIN_REGISTRY.get(name)


def get_plugin_metadata(name: str) -> Optional[PluginMetadata]:
    """Get metadata for a specific plugin"""
    return PLUGIN_METADATA.get(name)


def list_plugins() -> List[str]:
    """List all available plugin names"""
    return list(PLUGIN_REGISTRY.keys())


def list_plugins_by_category(category: str) -> List[str]:
    """List plugins by category"""
    return [
        name
        for name, metadata in PLUGIN_METADATA.items()
        if metadata.category == category and metadata.enabled
    ]


def get_plugin_categories() -> List[str]:
    """Get all unique plugin categories"""
    categories = set()
    for metadata in PLUGIN_METADATA.values():
        categories.add(metadata.category)
    return sorted(categories)


def get_plugins_info() -> Dict[str, Dict[str, Any]]:
    """Get comprehensive information about all plugins for UI display"""
    plugins_info = {}

    for name, metadata in PLUGIN_METADATA.items():
        plugin_func = PLUGIN_REGISTRY.get(name)

        plugins_info[name] = {
            "metadata": metadata.to_dict(),
            "available": plugin_func is not None,
            "docstring": plugin_func.__doc__ if plugin_func else None,
            "signature": str(plugin_func.__annotations__) if plugin_func else None,
        }

    return plugins_info


def toggle_plugin(name: str, enabled: bool) -> bool:
    """Enable or disable a plugin"""
    if name in PLUGIN_METADATA:
        PLUGIN_METADATA[name].enabled = enabled
        return True
    return False


def search_plugins(query: str) -> List[str]:
    """Search plugins by name, description, or capabilities"""
    query_lower = query.lower()
    matching_plugins = []

    for name, metadata in PLUGIN_METADATA.items():
        if (
            query_lower in name.lower()
            or query_lower in metadata.description.lower()
            or any(query_lower in cap.lower() for cap in metadata.capabilities)
        ):
            matching_plugins.append(name)

    return matching_plugins


def execute_plugin(name: str, *args, **kwargs) -> Any:
    """Execute a plugin with given arguments"""
    plugin = get_plugin(name)
    metadata = get_plugin_metadata(name)

    if plugin is None:
        raise ValueError(f"Plugin '{name}' not found")

    if metadata and not metadata.enabled:
        raise ValueError(f"Plugin '{name}' is disabled")

    try:
        return plugin(*args, **kwargs)
    except Exception as e:
        print(f"[Plugin Error] Error executing {name}: {e}")
        raise


def get_plugin_ui_data() -> Dict[str, Any]:
    """Get plugin data formatted for UI display"""
    categories = {}

    for name, metadata in PLUGIN_METADATA.items():
        category = metadata.category
        if category not in categories:
            categories[category] = []

        plugin_info = {
            "name": name,
            "description": metadata.description,
            "capabilities": metadata.capabilities,
            "version": metadata.version,
            "author": metadata.author,
            "enabled": metadata.enabled,
            "last_loaded": metadata.last_loaded,
            "available": name in PLUGIN_REGISTRY,
        }

        categories[category].append(plugin_info)

    return {
        "categories": categories,
        "total_plugins": len(PLUGIN_METADATA),
        "enabled_plugins": sum(1 for m in PLUGIN_METADATA.values() if m.enabled),
        "available_plugins": len(PLUGIN_REGISTRY),
    }


def validate_plugin_dependencies(name: str) -> Dict[str, bool]:
    """Check if plugin dependencies are available"""
    metadata = get_plugin_metadata(name)
    if not metadata:
        return {}

    dependency_status = {}
    for dep in metadata.dependencies:
        # Check if dependency is available (simplified check)
        try:
            __import__(dep)
            dependency_status[dep] = True
        except ImportError:
            dependency_status[dep] = False

    return dependency_status


def reload_plugins():
    """Reload all plugins"""
    global PLUGIN_REGISTRY, PLUGIN_METADATA
    PLUGIN_REGISTRY.clear()
    PLUGIN_METADATA.clear()
    load_plugins()


# Call this at startup to populate PLUGIN_REGISTRY
load_plugins()
