# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Plugin System
"""

try:
    # Try relative import first (when used as a package)
    from .enhanced_plugin_manager import PluginManager
except ImportError:
    # Fall back to absolute import (when imported directly)
    try:
        from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager
    except ImportError:
        # If that fails too, provide a placeholder
        class PluginManager:
            """Placeholder PluginManager when imports fail."""
            def __init__(self, *args, **kwargs):
                pass

__all__ = ["PluginManager"]
