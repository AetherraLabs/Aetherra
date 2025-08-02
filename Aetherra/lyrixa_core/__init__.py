"""
🧠 Lyrixa Core AI Intelligence Module
=====================================

This module provides the core intelligence capabilities for the Aetherra AI OS,
including conversation management, memory integration, and agent coordination.
"""

__version__ = "1.0.0"
__author__ = "Aetherra Labs"

# Import core components for easy access
try:
    from .conversation_manager import LyrixaConversationManager
except ImportError:
    LyrixaConversationManager = None

try:
    from .intelligence_integration import LyrixaIntelligenceStack
except ImportError:
    LyrixaIntelligenceStack = None

# Export main classes
__all__ = [
    "LyrixaConversationManager",
    "LyrixaIntelligenceStack",
]
