#!/usr/bin/env python3
"""
Plugin Discovery Utility
========================

Always-available plugin discovery functionality for Lyrixa.
This module provides simple access to plugin discovery across all plugin managers.
"""

import os
from typing import Any, Dict, List


def discover_all_plugins() -> Dict[str, List[str]]:
    """
    Discover all plugins from all available plugin managers.

    Returns:
        Dict with plugin sources as keys and plugin lists as values
    """
    results = {
        "advanced_plugins": [],
        "enhanced_plugins": [],
        "combined": [],
        "errors": [],
    }

    # Try Advanced Plugin Manager
    try:
        from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager

        manager = LyrixaAdvancedPluginManager()
        results["advanced_plugins"] = manager.discover_plugins()
    except Exception as e:
        results["errors"].append(f"Advanced Plugin Manager: {str(e)}")

    # Try Enhanced Plugin Manager
    try:
        from lyrixa.plugins.enhanced_plugin_manager import PluginManager

        manager = PluginManager()
        results["enhanced_plugins"] = manager.discover_plugins()
    except Exception as e:
        results["errors"].append(f"Enhanced Plugin Manager: {str(e)}")

    # Combine and deduplicate
    all_plugins = set(results["advanced_plugins"] + results["enhanced_plugins"])
    results["combined"] = sorted(list(all_plugins))

    return results


def get_plugin_directories() -> List[str]:
    """Get all plugin directories that are scanned."""
    directories = []

    # Standard plugin directories
    base_dirs = ["plugins", "lyrixa/plugins", "src/plugins", "core/plugins"]

    for base_dir in base_dirs:
        if os.path.exists(base_dir):
            directories.append(os.path.abspath(base_dir))

    return directories


def discover_plugins_simple() -> List[str]:
    """
    Simple function to discover plugins - returns just the plugin names.

    Returns:
        List of discovered plugin names
    """
    result = discover_all_plugins()
    return result["combined"]


def is_plugin_discovery_available() -> bool:
    """
    Check if plugin discovery is available and working.

    Returns:
        True if discovery is working, False otherwise
    """
    try:
        discover_plugins_simple()
        return True
    except Exception:
        return False


def get_plugin_discovery_status() -> Dict[str, Any]:
    """
    Get detailed status of plugin discovery system.

    Returns:
        Status information including discovered plugins, errors, etc.
    """
    status = {
        "available": False,
        "plugin_count": 0,
        "plugins": [],
        "directories": [],
        "errors": [],
        "managers": {"advanced": False, "enhanced": False},
    }

    try:
        # Check plugin directories
        status["directories"] = get_plugin_directories()

        # Test plugin discovery
        discovery_result = discover_all_plugins()
        status["plugins"] = discovery_result["combined"]
        status["plugin_count"] = len(discovery_result["combined"])
        status["errors"] = discovery_result["errors"]

        # Check manager availability
        try:
            from lyrixa.core.advanced_plugins import (
                LyrixaAdvancedPluginManager,  # noqa: F401
            )

            status["managers"]["advanced"] = True
        except Exception:
            pass

        try:
            from lyrixa.plugins.enhanced_plugin_manager import (
                PluginManager,  # noqa: F401
            )

            status["managers"]["enhanced"] = True
        except Exception:
            pass

        status["available"] = (
            status["plugin_count"] > 0 or len(status["directories"]) > 0
        )

    except Exception as e:
        status["errors"].append(f"Status check error: {str(e)}")

    return status


# Convenience aliases for easier access
discover = discover_plugins_simple
discover_detailed = discover_all_plugins
status = get_plugin_discovery_status


if __name__ == "__main__":
    # CLI interface for plugin discovery
    print("🧩 Lyrixa Plugin Discovery")
    print("=" * 40)

    status_info = get_plugin_discovery_status()

    print(f"Plugin Discovery Available: {status_info['available']}")
    print(f"Total Plugins Found: {status_info['plugin_count']}")
    print(f"Plugin Directories: {len(status_info['directories'])}")

    if status_info["plugins"]:
        print("\nDiscovered Plugins:")
        for plugin in sorted(status_info["plugins"]):
            print(f"  • {plugin}")

    if status_info["directories"]:
        print("\nPlugin Directories:")
        for directory in status_info["directories"]:
            print(f"  • {directory}")

    if status_info["errors"]:
        print("\nErrors:")
        for error in status_info["errors"]:
            print(f"  ⚠️ {error}")

    print("\nManager Status:")
    print(
        f"  Advanced Plugin Manager: {'✅' if status_info['managers']['advanced'] else '❌'}"
    )
    print(
        f"  Enhanced Plugin Manager: {'✅' if status_info['managers']['enhanced'] else '❌'}"
    )
