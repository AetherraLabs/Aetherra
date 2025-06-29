"""
NeuroCode Memory Subsystem
=========================

Memory management and storage systems for NeuroCode.
Handles persistent memory, vector memory, and temporal features.
"""

from .base import MemorySystem
from .vector import VectorMemory

__all__ = ["MemorySystem", "VectorMemory"]


def create_memory_system(vector_enabled=True):
    """Create a NeuroCode memory system."""
    if vector_enabled:
        return VectorMemory()
    return MemorySystem()
