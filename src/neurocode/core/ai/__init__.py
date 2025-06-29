"""
NeuroCode AI Integration Subsystem
=================================

AI and LLM integration components for NeuroCode.
Handles multi-LLM management, collaboration, and runtime.
"""

from .collaboration import AICollaboration
from .llm_integration import LLMIntegration
from .local_ai import LocalAI
from .multi_llm_manager import MultiLLMManager
from .runtime import AIRuntime

__all__ = ["AIRuntime", "AICollaboration", "LLMIntegration", "MultiLLMManager", "LocalAI"]


def create_ai_runtime():
    """Create an AI runtime instance."""
    return AIRuntime()
