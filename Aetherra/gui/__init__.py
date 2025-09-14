#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🎯 Aetherra GUI Package
=======================

Lyrixa GUI stable release implementation with zone-based architecture.

This package provides:
- ZoneManager: Dynamic layout management with diff+patch API
- PluginUIHost: Secure WebView-based plugin isolation
- EventBus: Unified Qt signals + async messaging system
- LyrixaGUI: Main window integrating all components

Key Features:
- Plugin-safe architecture with sandboxing
- Chat reliability with state isolation
- Performance monitoring and resource budgets
- Hot plugin add/remove without restart
- Layout preservation across sessions
"""

from .event_bus import EventBus, EventFactory, get_event_bus
from .lyrixa_gui import LyrixaGUI, create_lyrixa_gui
from .plugin_ui_host import PluginUIHost, PluginUIManager
from .zone_manager import LayoutMode, ZoneManager, ZoneType

__version__ = "1.0.0"
__all__ = [
    # Main GUI
    "LyrixaGUI",
    "create_lyrixa_gui",
    # Zone Management
    "ZoneManager",
    "ZoneType",
    "LayoutMode",
    # Plugin System
    "PluginUIHost",
    "PluginUIManager",
    # Event System
    "EventBus",
    "EventFactory",
    "get_event_bus",
]
