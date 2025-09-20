#!/usr/bin/env python3
"""Affect Engine MVP

Computes simple affective state (valence, arousal, uncertainty) using recent episodic events.
Rules (Phase 1 heuristic):
- action/thought events with sub_type containing 'error' decrease valence, raise arousal & uncertainty
- successful plugin_execution_outcome slightly raises valence, lowers uncertainty
- high importance events (>0.8) nudge arousal upward
Bias integration: provide weight multiplier for workspace candidate prioritization.
"""

from __future__ import annotations

# Standard library imports
import os
from datetime import datetime, timedelta
from typing import Optional

# Local imports
from .episodic_store import EpisodicStore, get_episodic_store
from .schemas.affect_snapshot import AffectSnapshot

# Workspace not directly needed yet; reserved for future bias injection

AFFECT_WINDOW_SEC = int(
    os.getenv("AETHERRA_AFFECT_WINDOW_SEC", "900")
)  # 15 min default


class AffectEngine:
    def __init__(self):
        self._last_snapshot: Optional[AffectSnapshot] = None

    def compute(self) -> AffectSnapshot:
        store: EpisodicStore = get_episodic_store()
        cutoff = datetime.utcnow() - timedelta(seconds=AFFECT_WINDOW_SEC)
        events = [e for e in store.list_recent(500) if e.ts >= cutoff]

        valence = 0.0
        arousal = 0.1  # baseline mild activation
        uncertainty = 0.2
        adjustments = 0

        for e in events:
            sub = (e.sub_type or "").lower()
            if "error" in sub:
                valence -= 0.15
                arousal += 0.1
                uncertainty += 0.12
                adjustments += 1
            elif sub == "execute":  # successful execution
                valence += 0.05
                uncertainty -= 0.03
                adjustments += 1
            if e.importance >= 0.8:  # salient events raise arousal
                arousal += 0.05
                adjustments += 1

        # Normalize / clamp ranges
        valence = max(-1.0, min(1.0, valence))
        arousal = max(0.0, min(1.0, arousal))
        uncertainty = max(0.0, min(1.0, uncertainty))
        rationale = f"derived from {len(events)} events ({adjustments} adjustments)"
        snapshot = AffectSnapshot(
            schema_version=1,
            valence=valence,
            arousal=arousal,
            uncertainty=uncertainty,
            rationale=rationale,
        )
        self._last_snapshot = snapshot
        return snapshot

    def get_last(self) -> Optional[AffectSnapshot]:
        return self._last_snapshot

    def affect_weight(self, base_priority: int) -> float:
        if not os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1":
            return 1.0
        snap = self._last_snapshot or self.compute()
        # Simple weight: higher arousal -> amplify, negative valence slightly dampens
        weight = 1.0 + (snap.arousal * 0.5) - (max(0.0, -snap.valence) * 0.3)
        return max(0.3, min(2.0, weight))


AFFECT_ENGINE_SINGLETON: Optional[AffectEngine] = None


def get_affect_engine() -> AffectEngine:
    global AFFECT_ENGINE_SINGLETON
    if AFFECT_ENGINE_SINGLETON is None:
        AFFECT_ENGINE_SINGLETON = AffectEngine()
    return AFFECT_ENGINE_SINGLETON
