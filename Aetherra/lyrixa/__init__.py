# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Lyrixa AI Intelligence Module
===============================

Core intelligence and consciousness capabilities for Lyrixa AI.
Integrates conversation management, memory systems, and advanced reasoning.
"""

__version__ = "1.0.0"
__author__ = "Aetherra Labs"

# Import core components for easy access
try:
    from .intelligence.lyrixa_full_intelligence import LyrixaIntelligenceCore
except ImportError:
    LyrixaIntelligenceCore = None

try:
    from .LyrixaCore import LyrixaCoreInterface, get_lyrixa_core
except ImportError:
    get_lyrixa_core = None
    LyrixaCoreInterface = None


# Legacy compatibility classes
class LyrixaIntelligenceStack:
    """Enhanced intelligence stack with full AI capabilities"""

    def __init__(self, workspace_path="", *args, **kwargs):
        self.workspace_path = workspace_path
        self.intelligence_core = (
            LyrixaIntelligenceCore() if LyrixaIntelligenceCore else None
        )
        self.lyrixa_core = get_lyrixa_core() if get_lyrixa_core else None
        self.is_available = (
            self.intelligence_core is not None or self.lyrixa_core is not None
        )

    def get_conversation_manager(self):
        """Get conversation management capabilities"""
        if self.lyrixa_core:
            return self.lyrixa_core
        elif self.intelligence_core:
            return self.intelligence_core
        return None

    def process_message(self, message, user_id="user", context=None):
        """Process a message through the intelligence system"""
        if self.lyrixa_core:
            return self.lyrixa_core.process_user_interaction(user_id, message, context)
        elif self.intelligence_core:
            # Use the full intelligence core if available
            return self.intelligence_core.process_conversation(message, user_id)
        return {"response": "Intelligence system not available"}


class LyrixaConversationManager:
    """Enhanced conversation manager with consciousness integration"""

    def __init__(self, *args, **kwargs):
        self.lyrixa_core = get_lyrixa_core() if get_lyrixa_core else None
        self.intelligence_core = (
            LyrixaIntelligenceCore() if LyrixaIntelligenceCore else None
        )
        self.is_available = (
            self.lyrixa_core is not None or self.intelligence_core is not None
        )

    def process_message(self, message, user_id="user", context=None):
        """Process a message with full consciousness integration"""
        if self.lyrixa_core:
            # Use the consciousness-integrated core if available
            result = self.lyrixa_core.process_user_interaction(
                user_id, message, context
            )
            return result.get("response", "Processed through Lyrixa Core")
        elif self.intelligence_core:
            # Fall back to basic intelligence processing
            result = self.intelligence_core.process_conversation(message, user_id)
            return result.get("response", "Processed through Intelligence Core")
        return "Lyrixa conversation system not available"

    def get_identity_profile(self):
        """Get Lyrixa's identity profile"""
        if self.lyrixa_core:
            return self.lyrixa_core.get_identity_profile()
        return None

    def make_decision(self, situation, options):
        """Make an identity-based decision"""
        if self.lyrixa_core:
            return self.lyrixa_core.make_decision(situation, options)
        return None


# Export main classes
__all__ = [
    "LyrixaIntelligenceStack",
    "LyrixaConversationManager",
    "LyrixaIntelligenceCore",
    "LyrixaCoreInterface",
    "get_lyrixa_core",
]
