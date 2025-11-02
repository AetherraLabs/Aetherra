# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Semantic Resonance Engine (SRE) — Phase 3
==========================================

Unites events, goals, beliefs, and recent narrative into a shared vector space.
Produces Resonance Scores that drive focus selection beyond raw severity.

Currently uses simple hash-based pseudo-embeddings as a placeholder.
TODO: Swap to real embeddings (SentenceTransformer, fastText, etc.) when ready.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Tuple


class SemanticResonance:
    """Semantic resonance engine for focus selection.

    Maps events and goals to a shared vector space and computes
    cosine similarity to determine relevance/resonance.

    Starter implementation uses deterministic hash-based pseudo-vectors.
    Replace with real embeddings for production use.
    """

    def __init__(self, vector_dim: int = 8):
        """Initialize semantic resonance engine.

        Args:
            vector_dim: Dimensionality of embedding vectors (default 8 for lightweight demo)
        """
        self.vector_dim = vector_dim
        self._proj: Dict[str, List[float]] = {}  # Cache for computed embeddings

    def embed_event(self, e_type: str, payload: Dict[str, Any]) -> List[float]:
        """Embed an event into vector space.

        Args:
            e_type: Event type (e.g., "svc.health", "disk.status")
            payload: Event payload dict

        Returns:
            Vector representation of the event
        """
        # Cache key combines type and payload keys
        cache_key = f"evt:{e_type}:{tuple(sorted(payload.keys()))}"
        if cache_key in self._proj:
            return self._proj[cache_key]

        # Minimal placeholder: hash-based pseudo-vector with semantic boosting
        # TODO: Replace with sentence-transformers or fastText
        text = f"{e_type} {' '.join(str(k) for k in payload)}"
        h = abs(hash((e_type, tuple(sorted(payload)))))
        vec = [((h >> i) & 255) / 255.0 for i in range(self.vector_dim)]

        # Boost specific dimensions based on semantic keywords
        # Resource-related keywords get stronger boosts to ensure proper ranking
        keywords = {
            "disk": (0, 0.5),
            "mem": (1, 0.5),
            "memory": (1, 0.5),
            "cpu": (2, 0.5),
            "resource": (3, 0.5),
            "usage": (4, 0.5),
            "status": (5, 0.4),
            "free": (0, 0.4),
            "pct": (1, 0.4),
            "chat": (6, 0.2),
            "message": (7, 0.2),
            "text": (7, 0.2),
        }
        for word, (dim_idx, boost) in keywords.items():
            if word in text.lower() and dim_idx < self.vector_dim:
                vec[dim_idx] = min(1.0, vec[dim_idx] + boost)

        self._proj[cache_key] = vec
        return vec

    def embed_goal(self, goal: str) -> List[float]:
        """Embed a goal/intention into vector space.

        Args:
            goal: Goal description string

        Returns:
            Vector representation of the goal
        """
        cache_key = f"goal:{goal}"
        if cache_key in self._proj:
            return self._proj[cache_key]

        # Hash-based pseudo-vector with semantic boosting
        h = abs(hash(goal))
        vec = [((h >> i) & 255) / 255.0 for i in range(self.vector_dim)]

        # Boost specific dimensions based on semantic keywords
        # Resource-related keywords get stronger boosts
        keywords = {
            "disk": (0, 0.5),
            "mem": (1, 0.5),
            "memory": (1, 0.5),
            "cpu": (2, 0.5),
            "resource": (3, 0.5),
            "usage": (4, 0.5),
            "status": (5, 0.4),
            "optimize": (3, 0.5),
            "chat": (6, 0.2),
            "message": (7, 0.2),
        }
        for word, (dim_idx, boost) in keywords.items():
            if word in goal.lower() and dim_idx < self.vector_dim:
                vec[dim_idx] = min(1.0, vec[dim_idx] + boost)

        self._proj[cache_key] = vec
        return vec

    @staticmethod
    def cosine(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            a: First vector
            b: Second vector

        Returns:
            Cosine similarity in range [-1.0, 1.0] (typically 0.0–1.0 for positive vectors)
        """
        num = sum(x * y for x, y in zip(a, b, strict=True))
        da = math.sqrt(sum(x * x for x in a)) or 1.0
        db = math.sqrt(sum(x * x for x in b)) or 1.0
        return num / (da * db)

    def resonance(self, event_vec: List[float], goal_vecs: List[List[float]]) -> float:
        """Compute maximum resonance between an event and a list of goals.

        Args:
            event_vec: Event embedding
            goal_vecs: List of goal embeddings

        Returns:
            Maximum cosine similarity with any goal (0.0 if no goals)
        """
        if not goal_vecs:
            return 0.0

        return max(self.cosine(event_vec, g) for g in goal_vecs)

    def top_resonances(
        self, event_vecs: List[Tuple[str, List[float]]], goal_vecs: List[List[float]], k: int = 5
    ) -> List[Tuple[str, float]]:
        """Compute top-k resonant events with goals.

        Args:
            event_vecs: List of (event_id, embedding) tuples
            goal_vecs: List of goal embeddings
            k: Number of top results to return

        Returns:
            List of (event_id, resonance_score) sorted by resonance descending
        """
        scored = [(eid, self.resonance(vec, goal_vecs)) for eid, vec in event_vecs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def clear_cache(self) -> None:
        """Clear embedding cache (useful for long-running processes)."""
        self._proj.clear()

    def get_cache_size(self) -> int:
        """Get number of cached embeddings.

        Returns:
            Cache entry count
        """
        return len(self._proj)
