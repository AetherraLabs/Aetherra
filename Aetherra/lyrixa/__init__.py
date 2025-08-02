"""
🧠 Lyrixa AI Intelligence Bridge
===============================

This module serves as a bridge to redirect legacy import paths to the new lyrixa_core structure.
"""

# Re-export from lyrixa_core to maintain backward compatibility
try:
    from ..lyrixa_core.conversation_manager import *
except ImportError:
    pass

try:
    from ..lyrixa_core.intelligence_integration import *
except ImportError:
    pass


# Legacy bridge classes for backward compatibility
class LyrixaIntelligenceStack:
    """Legacy bridge for LyrixaIntelligenceStack"""

    def __init__(self, *args, **kwargs):
        self.workspace_path = kwargs.get("workspace_path", "")
        self.conversation_manager = None
        self.is_available = False

    def get_conversation_manager(self):
        return self.conversation_manager


class LyrixaConversationManager:
    """Legacy bridge for LyrixaConversationManager"""

    def __init__(self, *args, **kwargs):
        self.is_available = False

    def process_message(self, message):
        return {"response": "Bridge mode - full AI not yet connected"}


# Export for backward compatibility
__all__ = ["LyrixaIntelligenceStack", "LyrixaConversationManager"]
