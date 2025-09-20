# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Lyrixa Memory Module
=======================

Memory management and storage for the Aetherra AI OS.
Provides various memory types and integration capabilities.
"""

# Import all memory components
try:
    # Local imports
    from .lyrixa_memory_engine import LyrixaMemoryEngine
except ImportError:
    LyrixaMemoryEngine = None

try:
    # Local imports
    from .quantum_memory_integration import (
        QuantumMemoryLayer,
        QuantumMemoryNode,
        initialize_quantum_memory,
        quantum_memory_search,
    )
except ImportError:
    QuantumMemoryLayer = None
    QuantumMemoryNode = None
    quantum_memory_search = None
    initialize_quantum_memory = None

try:
    # Local imports
    from .episodic_memory import EpisodicMemory
except ImportError:
    EpisodicMemory = None

try:
    # Local imports
    from .semantic_memory import SemanticMemory
except ImportError:
    SemanticMemory = None

__all__ = [
    "LyrixaMemoryEngine",
    "QuantumMemoryLayer",
    "QuantumMemoryNode",
    "quantum_memory_search",
    "initialize_quantum_memory",
    "EpisodicMemory",
    "SemanticMemory",
]
