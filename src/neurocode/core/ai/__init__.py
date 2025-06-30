"""
NeuroCode AI Integration Subsystem
=================================

AI and LLM integration components for NeuroCode.
Handles multi-LLM management, collaboration, and runtime.
"""

from .collaboration import AICollaborationFramework as AICollaboration
from .llm_integration import NeuroCodeLLMIntegration as LLMIntegration
from .local_ai import LocalAIEngine as LocalAI
from .multi_llm_manager import MultiLLMManager

__all__ = ["AICollaboration", "LLMIntegration", "MultiLLMManager", "LocalAI"]


def create_ai_runtime():
    """Create an AI runtime instance."""
    return MultiLLMManager()
