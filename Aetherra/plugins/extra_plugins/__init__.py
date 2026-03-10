# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Lyrixa Plugin System
"""

try:
    # Try relative import first (when used as a package)
    # Local imports
    from .enhanced_plugin_manager import PluginManager
except ImportError:
    # Fall back to absolute import (when imported directly)
    try:
        # Aetherra imports
        from Aetherra.lyrixa.plugins.enhanced_plugin_manager import PluginManager
    except ImportError:
        # If that fails too, provide a fallback manager
        class PluginManager:
            """Fallback PluginManager when imports fail."""

            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs


__all__ = ["PluginManager"]
