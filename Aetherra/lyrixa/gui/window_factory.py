"""
Lyrixa GUI Factory - Choose Between Classic and Hybrid UI
=========================================================

This module provides a factory for selecting between the original
LyrixaWindow and the new LyrixaHybridWindow based on configuration.

Features:
- 🔄 Drop-in compatibility with launcher.py
- ⚙️ Configuration-based UI selection
- 🔧 Easy A/B testing between interfaces
- 🚀 Future-ready for hybrid development
"""

import os
from typing import Union

from .gui_window import LyrixaWindow as LyrixaClassicWindow
from .hybrid_window import LyrixaWindow as LyrixaHybridWindow


class LyrixaWindowFactory:
    """Factory for creating Lyrixa windows based on configuration"""

    @staticmethod
    def create_window() -> Union[LyrixaClassicWindow, LyrixaHybridWindow]:
        """
        Create a Lyrixa window based on environment configuration

        Returns:
            LyrixaClassicWindow or LyrixaHybridWindow based on LYRIXA_UI_MODE
        """
        ui_mode = os.getenv("LYRIXA_UI_MODE", "classic").lower()

        if ui_mode == "hybrid":
            print("🌟 Starting Lyrixa with Hybrid UI (PySide6 + WebView)")
            return LyrixaHybridWindow()
        else:
            print("🖥️ Starting Lyrixa with Classic UI")
            return LyrixaClassicWindow()


# For backward compatibility, export LyrixaWindow as the default
# This allows existing imports to continue working unchanged
def create_lyrixa_window() -> Union[LyrixaClassicWindow, LyrixaHybridWindow]:
    """Create a Lyrixa window using the factory"""
    return LyrixaWindowFactory.create_window()


# Convenience function for launcher
def get_window_class():
    """Get the appropriate window class based on configuration"""
    ui_mode = os.getenv("LYRIXA_UI_MODE", "classic").lower()

    if ui_mode == "hybrid":
        return LyrixaHybridWindow
    else:
        return LyrixaClassicWindow


# For compatibility - export the appropriate window class as LyrixaWindow
LyrixaWindow = (
    LyrixaHybridWindow
    if os.getenv("LYRIXA_UI_MODE", "classic").lower() == "hybrid"
    else LyrixaClassicWindow
)


# Export both classes for direct access if needed
__all__ = [
    "LyrixaWindow",
    "LyrixaClassicWindow",
    "LyrixaHybridWindow",
    "LyrixaWindowFactory",
    "create_lyrixa_window",
    "get_window_class",
]
