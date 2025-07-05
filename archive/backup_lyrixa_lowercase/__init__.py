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
    from .assistant import LyrixaAI
    from .models import LocalModel, ModelRouter, OpenAIModel

    __all__ = ["LyrixaAI", "LocalModel", "ModelRouter", "OpenAIModel", "__version__"]
except ImportError:
    # If imports fail, just expose version
    __all__ = ["__version__"]
