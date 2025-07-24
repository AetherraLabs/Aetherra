"""
LyrixaCore - Unified Cognitive Stack for Phase 6
Main package for the unified cognitive architecture integrating identity, beliefs, and coherence.
"""

try:
    # Try relative imports first
    from .IdentityAgent.core_beliefs import CoreBeliefs
    from .IdentityAgent.personal_history import EventType, PersonalHistory
    from .IdentityAgent.self_model import SelfModel
    from .interface_bridge import LyrixaContextBridge
except ImportError:
    # Fall back to absolute imports or placeholders
    try:
        from Aetherra.lyrixa.LyrixaCore.IdentityAgent.core_beliefs import CoreBeliefs
        from Aetherra.lyrixa.LyrixaCore.IdentityAgent.personal_history import EventType, PersonalHistory
        from Aetherra.lyrixa.LyrixaCore.IdentityAgent.self_model import SelfModel
        from Aetherra.lyrixa.LyrixaCore.interface_bridge import LyrixaContextBridge
    except ImportError:
        print("⚠️ Using placeholder LyrixaCore classes")

        from enum import Enum

        class EventType(Enum):
            CONVERSATION = "conversation"
            LEARNING = "learning"
            REFLECTION = "reflection"

        class CoreBeliefs:
            def __init__(self, *args, **kwargs):
                self.beliefs = {}

        class PersonalHistory:
            def __init__(self, *args, **kwargs):
                self.events = []

        class SelfModel:
            def __init__(self, *args, **kwargs):
                self.identity = {}

        class LyrixaContextBridge:
            def __init__(self, *args, **kwargs):
                pass

__version__ = "6.0.0"
__author__ = "Aetherra Project"

__all__ = [
    "LyrixaContextBridge",
    "CoreBeliefs",
    "PersonalHistory",
    "EventType",
    "SelfModel",
]
