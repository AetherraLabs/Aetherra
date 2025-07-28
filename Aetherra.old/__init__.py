"""
Aetherra - AI-Native Development Platform
========================================

A revolutionary development platform that bridges natural language and code
through the Aetherra programming language and Lyrixa AI assistant.
"""

__version__ = "2.0.0"
__author__ = "Aetherra Development Team"

# Core module imports - specific imports to avoid wildcard issues
try:
    # Re-enable all core components after fixing syntax issues
    from .core.aetherra_interpreter import (
        AetherraInterpreter,  # Re-enabled after fixing syntax errors
    )
    from .core.aetherra_parser import AetherraParser  # Re-enabled after fixing naming
    from .core.agent import AetherraAgent
    from .core.ai_runtime import ask_ai
    from .core.config import Config
    from .core.memory.base import AetherraMemory
    from .core.plugin_manager import PluginIntent, PluginMetadata
except ImportError:
    # Fallback for development
    pass

__all__ = [
    "__version__",
    "__author__",
    "Config",
    "AetherraMemory",
    "ask_ai",
    "AetherraInterpreter",  # Re-enabled after fixing syntax errors
    "AetherraParser",  # Re-enabled after fixing naming
    "PluginMetadata",
    "PluginIntent",
    "AetherraAgent",  # Re-enabled
]
