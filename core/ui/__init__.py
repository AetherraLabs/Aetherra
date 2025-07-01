"""
🎭 NeuroCode UI System
=====================

Advanced UI components for the Neuroplex AI OS interface.
Provides theming, visual feedback, and interactive elements.

Modules:
- interface: Main UI interface components
- themes: Theme management and customization
- feedback: Visual feedback and status indicators
- commands: Command suggestions and shortcuts
- display: Rich text and content rendering
"""

from .commands import CommandSuggestions
from .display import CodeLanguage, RichDisplay, TextStyle
from .feedback import StatusIndicator, VisualFeedback
from .interface import InterfaceConfig, NeuroplexUI
from .themes import ThemeManager, UIColors, UITheme

__all__ = [
    "NeuroplexUI",
    "InterfaceConfig",
    "ThemeManager",
    "UITheme",
    "UIColors",
    "VisualFeedback",
    "StatusIndicator",
    "CommandSuggestions",
    "RichDisplay",
    "CodeLanguage",
    "TextStyle",
]
