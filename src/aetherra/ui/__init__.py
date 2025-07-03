"""
Aetherra UI Module
=================

User interface components for the Aetherra programming language.
"""

try:
    from .enhanced_lyrixa import EnhancedLyrixaWindow, launch_enhanced_lyrixa

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    EnhancedLyrixaWindow = None
    launch_enhanced_lyrixa = None


def launch_gui():
    """Launch the main GUI interface."""
    if GUI_AVAILABLE and launch_enhanced_lyrixa:
        return launch_enhanced_lyrixa()
    else:
        print("GUI not available - Enhanced Lyrixa requires PySide6")
        print("Install with: pip install PySide6")
        return None


# Export main components
__all__ = [
    "launch_gui",
    "EnhancedLyrixaWindow",
    "launch_enhanced_lyrixa",
    "GUI_AVAILABLE",
]
