# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Self-Trust Layer (STL) — Phase 3
================================

Gives Aetherra a sense of self-trust: it knows when it's broken/fixed.
Computes a Self-Trust Score (STS) 0–100 per subsystem + global.
Exposes STS to attention/intention to bias toward stabilizing shaky parts.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SubsystemTrust:
    """Trust metrics for a single subsystem."""

    name: str
    score: float = 100.0  # 0..100
    last_event_ts: float = 0.0
    history: List[float] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"SubsystemTrust({self.name}, score={self.score:.1f})"


class SelfTrust:
    """Tracks self-trust across subsystems with exponential decay toward baseline.

    Trust is updated based on health-check outcomes:
    - "ok": minor boost (+1.5)
    - "repaired": significant boost (+4.0)
    - "failed": penalty (-12.0)

    Trust decays exponentially toward a healthy baseline (90.0) when no events occur.
    """

    def __init__(self, half_life_s: int = 3600):
        """Initialize self-trust tracker.

        Args:
            half_life_s: Time in seconds for trust to decay halfway to baseline (default 1 hour)
        """
        self.subsystems: Dict[str, SubsystemTrust] = {}
        self.half_life = half_life_s

    def _decay(self, s: SubsystemTrust) -> None:
        """Apply exponential decay toward baseline 90.0.

        Args:
            s: Subsystem trust to decay
        """
        now = time.time()
        dt = max(0.0, now - s.last_event_ts)
        if dt <= 0:
            return

        # Exponential revert toward 90 as neutral healthy baseline
        target = 90.0
        lam = math.log(2) / self.half_life
        s.score = target + (s.score - target) * math.exp(-lam * dt)
        s.last_event_ts = now

    def observe(self, name: str, outcome: str) -> None:
        """Record a health-check outcome for a subsystem.

        Args:
            name: Subsystem identifier (e.g., "services", "disk", "memory")
            outcome: "ok" | "repaired" | "failed"
        """
        s = self.subsystems.setdefault(name, SubsystemTrust(name=name))
        s.last_event_ts = time.time()
        self._decay(s)

        if outcome == "ok":
            s.score = min(100.0, s.score + 1.5)
        elif outcome == "repaired":
            s.score = min(100.0, s.score + 4.0)
        else:  # failed
            s.score = max(0.0, s.score - 12.0)

        s.history.append(s.score)
        if len(s.history) > 1000:  # cap history
            s.history = s.history[-1000:]

    def global_score(self) -> float:
        """Compute global trust score using harmonic mean (emphasizes weakest link).

        Returns:
            Global trust score 0.0–100.0
        """
        if not self.subsystems:
            return 0.0

        # Harmonic mean emphasizes weakest link
        eps = 1e-6
        inv = sum(1.0 / max(eps, s.score) for s in self.subsystems.values())
        return len(self.subsystems) / inv

    def bias_for_attention(self, name: str) -> float:
        """Compute attention multiplier for a subsystem based on trust.

        Lower trust → higher attention bias (range 1.0..2.0).

        Args:
            name: Subsystem identifier

        Returns:
            Attention multiplier 1.0 (fully trusted) to 2.0 (zero trust)
        """
        s = self.subsystems.get(name)
        if not s:
            return 1.0

        # Update decay before computing bias
        self._decay(s)
        # Lower trust -> higher attention multiplier
        # 90 is baseline; amplify sensitivity so multiple failures exceed 1.5x
        # Map 100->1.0, 60->2.0 (clamped)
        multiplier = 1.0 + max(0.0, (100.0 - s.score) / 40.0)
        return min(2.0, multiplier)

    def get_subsystem_scores(self) -> Dict[str, float]:
        """Get all subsystem trust scores.

        Returns:
            Dict mapping subsystem name to trust score
        """
        # Apply decay to all before returning
        for s in self.subsystems.values():
            self._decay(s)

        return {name: s.score for name, s in self.subsystems.items()}

    def get_status(self) -> dict:
        """Get diagnostic status for telemetry.

        Returns:
            Dict with global score and per-subsystem scores
        """
        return {
            "global_trust": self.global_score(),
            "subsystems": self.get_subsystem_scores(),
            "tracked_count": len(self.subsystems),
        }
