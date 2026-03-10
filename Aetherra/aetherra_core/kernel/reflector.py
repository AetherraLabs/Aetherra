# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors


"""Compatibility wrapper for the production reflector implementation.

The canonical implementation lives under `aetherra_core.memory.reflector`.
This module preserves the historical kernel import path while delegating to
the maintained implementation.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from ..memory.reflector.reflect_analyzer import (
    MemoryReflector as _MemoryReflector,
)


class MemoryReflector(_MemoryReflector):
    def __init__(self, db_path: str | None = None):
        super().__init__(db_path or "memory_reflector.db")

    def analyze_contradictions(self, fragments: list[Any], context: Any):
        """Compatibility shim for legacy second-parameter naming.

        Preferred signature expects concept clusters as the second argument.
        """
        concept_clusters = context if isinstance(context, list) else []
        return super().analyze_contradictions(fragments, concept_clusters)

    def explore_concept_connections(self, *args: Any, **kwargs: Any):
        """Support both legacy and canonical call signatures.

        Canonical:
        - explore_concept_connections(target_concept, fragments, concept_clusters)

        Legacy:
        - explore_concept_connections(fragments, _unused)
        """
        if kwargs:
            return super().explore_concept_connections(**kwargs)

        if len(args) == 3:
            target_concept, fragments, concept_clusters = args
            return super().explore_concept_connections(target_concept, fragments, concept_clusters)

        if len(args) >= 1:
            fragments = args[0]
            if not fragments:
                return []

            # Derive a best-effort target concept from the first fragment.
            target_concept = "general"
            first_fragment = fragments[0]
            semantic_tags = getattr(first_fragment, "semantic_tags", [])
            if semantic_tags:
                target_concept = semantic_tags[0]

            return super().explore_concept_connections(
                target_concept, fragments, concept_clusters=[]
            )

        return []

    def get_recent_insights(self, days: int):
        cutoff = datetime.now().timestamp() - max(days, 0) * 86400
        return [
            insight
            for insight in self.insights.values()
            if insight.discovered_at.timestamp() >= cutoff
        ]

    def get_actionable_recommendations(self):
        return super().get_actionable_recommendations()
