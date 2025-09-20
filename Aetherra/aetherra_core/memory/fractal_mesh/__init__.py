# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 FractalMesh Memory Layer
==========================

Multi-dimensional episodic memory system with temporal, symbolic, and associative indexing.
Enables narrative continuity, pattern recognition, and self-reflective memory exploration.
"""

# Local imports
from .analogs.pattern_matcher import CrossContextAnalogies
from .base import FractalMeshCore
from .concepts.concept_clusters import ConceptClusterManager
from .timelines.episodic_timeline import EpisodicTimeline

__all__ = [
    "FractalMeshCore",
    "ConceptClusterManager",
    "EpisodicTimeline",
    "CrossContextAnalogies",
]
