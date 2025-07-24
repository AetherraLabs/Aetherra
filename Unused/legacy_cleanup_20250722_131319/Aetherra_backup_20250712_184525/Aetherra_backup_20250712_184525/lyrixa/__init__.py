#!/usr/bin/env python3
"""
Lyrixa - AI Assistant for Aetherra
==================================
"""

import os
import sys

__version__ = "3.0.0-aetherra-assistant"

# Add the parent directory to path if needed
_lyrixa_dir = os.path.dirname(__file__)
_parent_dir = os.path.dirname(_lyrixa_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import key classes for easy access
try:
    from Aetherra.core.prompt_engine import build_dynamic_prompt

    from .assistant import LyrixaAI
    from .core.advanced_plugins import LyrixaAdvancedPluginManager
    from .models import LocalModel, ModelRouter, OpenAIModel
    from .plugin_discovery import discover, discover_detailed
    from .plugin_discovery import status as plugin_status
    from .plugins.enhanced_plugin_manager import PluginManager

    __all__ = [
        "LyrixaAI",
        "LocalModel",
        "ModelRouter",
        "OpenAIModel",
        "build_dynamic_prompt",
        "LyrixaAdvancedPluginManager",
        "PluginManager",
        "discover",
        "discover_detailed",
        "plugin_status",
        "__version__",
    ]
except ImportError:
    # If imports fail, just expose version
    __all__ = ["__version__"]
