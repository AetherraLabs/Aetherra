"""
NeuroCode Plugin API
==================

Core API for registering and managing NeuroCode plugins.
This module provides decorators and utilities for plugin development.
"""

import datetime
import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

# Global plugin registry
PLUGIN_REGISTRY = {}

def register_plugin(
    name: str,
    description: str = "",
    capabilities: Optional[List[str]] = None,
    version: str = "1.0.0",
    author: str = "",
    category: str = "general",
    dependencies: Optional[List[str]] = None,
    intent_purpose: str = "",
    intent_triggers: Optional[List[str]] = None,
    intent_scenarios: Optional[List[str]] = None,
    ai_description: str = "",
    example_usage: str = "",
    confidence_boost: float = 1.0
):
    """
    Register a function as a NeuroCode plugin.

    Args:
        name: Plugin identifier
        description: Plugin description
        capabilities: List of plugin capabilities
        version: Plugin version
        author: Plugin author
        category: Plugin category
        dependencies: Required packages
        intent_purpose: AI integration purpose
        intent_triggers: AI trigger words
        intent_scenarios: Use case scenarios
        ai_description: AI-readable description
        example_usage: Usage example
        confidence_boost: AI confidence multiplier

    Returns:
        Decorated function that is registered as a plugin
    """
    def decorator(func: Callable) -> Callable:
        # Extract function metadata
        sig = inspect.signature(func)
        docstring = inspect.getdoc(func) or ""

        # Create plugin metadata
        plugin_info = {
            "name": name,
            "function": func,
            "description": description or docstring.split('\n')[0],
            "capabilities": capabilities or [],
            "version": version,
            "author": author,
            "category": category,
            "dependencies": dependencies or [],
            "signature": sig,
            "docstring": docstring,
            "intent_purpose": intent_purpose,
            "intent_triggers": intent_triggers or [],
            "intent_scenarios": intent_scenarios or [],
            "ai_description": ai_description or description,
            "example_usage": example_usage,
            "confidence_boost": confidence_boost,
            "registered_at": datetime.datetime.now().isoformat()
        }

        # Register the plugin
        if name not in PLUGIN_REGISTRY:
            PLUGIN_REGISTRY[name] = {}

        function_name = func.__name__
        PLUGIN_REGISTRY[name][function_name] = plugin_info

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "plugin": name,
                    "function": function_name,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "plugin": name,
                    "function": function_name,
                    "timestamp": datetime.datetime.now().isoformat()
                }

        return wrapper

    return decorator

def get_plugin_registry() -> Dict[str, Any]:
    """Get the complete plugin registry."""
    return PLUGIN_REGISTRY

def get_plugin(plugin_name: str) -> Optional[Dict[str, Any]]:
    """Get a specific plugin's information."""
    return PLUGIN_REGISTRY.get(plugin_name)

def list_plugins() -> List[str]:
    """List all registered plugin names."""
    return list(PLUGIN_REGISTRY.keys())

def get_plugin_functions(plugin_name: str) -> List[str]:
    """Get all function names for a specific plugin."""
    plugin = PLUGIN_REGISTRY.get(plugin_name, {})
    return list(plugin.keys())

def call_plugin(plugin_name: str, function_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Call a plugin function by name.

    Args:
        plugin_name: Name of the plugin
        function_name: Name of the function
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Dict containing the result or error information
    """
    try:
        plugin = PLUGIN_REGISTRY.get(plugin_name)
        if not plugin:
            return {
                "success": False,
                "error": f"Plugin '{plugin_name}' not found",
                "timestamp": datetime.datetime.now().isoformat()
            }

        function_info = plugin.get(function_name)
        if not function_info:
            return {
                "success": False,
                "error": f"Function '{function_name}' not found in plugin '{plugin_name}'",
                "timestamp": datetime.datetime.now().isoformat()
            }

        func = function_info["function"]
        return func(*args, **kwargs)

    except Exception as e:
        return {
            "success": False,
            "error": f"Error calling {plugin_name}.{function_name}: {str(e)}",
            "timestamp": datetime.datetime.now().isoformat()
        }

def plugin_help(plugin_name: Optional[str] = None) -> str:
    """
    Get help information for plugins.

    Args:
        plugin_name: Specific plugin name, or None for all plugins

    Returns:
        Help text for the plugin(s)
    """
    if plugin_name:
        plugin = PLUGIN_REGISTRY.get(plugin_name)
        if not plugin:
            return f"Plugin '{plugin_name}' not found"

        help_text = f"Plugin: {plugin_name}\n"
        help_text += "=" * (len(plugin_name) + 8) + "\n\n"

        for func_name, info in plugin.items():
            help_text += f"Function: {func_name}\n"
            help_text += f"Description: {info['description']}\n"
            help_text += f"Signature: {info['signature']}\n"
            if info['docstring']:
                help_text += f"Documentation:\n{info['docstring']}\n"
            help_text += "\n"

        return help_text
    else:
        help_text = "Available Plugins:\n"
        help_text += "==================\n\n"

        for plugin_name, plugin in PLUGIN_REGISTRY.items():
            help_text += f"• {plugin_name}\n"
            for func_name, info in plugin.items():
                help_text += f"  - {func_name}: {info['description']}\n"
            help_text += "\n"

        return help_text

# Compatibility aliases
plugin_registry = register_plugin
get_plugins = get_plugin_registry
