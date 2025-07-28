"""
AetherraCode Memory Subsystem
=========================

Memory management and storage systems for AetherraCode.
Handles persistent memory, vector memory, and temporal features.
"""

from .base import AetherraMemory, BasicMemory, PatternAnalyzer
from .vector import EnhancedSemanticMemory

__all__ = [
    "AetherraMemory",
    "BasicMemory",
    "PatternAnalyzer",
    "EnhancedSemanticMemory",
    "create_memory_system",
]


def create_memory_system(vector_enabled=True):
    """Create a AetherraCode memory system."""
    if vector_enabled:
        try:
            return EnhancedSemanticMemory()
        except Exception:
            return AetherraMemory()
    return AetherraMemory()
