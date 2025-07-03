"""
NeuroCode Memory Subsystem
=========================

Memory management and storage systems for NeuroCode.
Handles persistent memory, vector memory, and temporal features.
"""

from .base import AetherraMemory
from .vector import EnhancedSemanticMemory

__all__ = ["AetherraMemory", "EnhancedSemanticMemory", "create_memory_system"]


def create_memory_system(vector_enabled=True):
    """Create a NeuroCode memory system."""
    if vector_enabled:
        try:
            return EnhancedSemanticMemory()
        except Exception:
            return AetherraMemory()
    return AetherraMemory()
