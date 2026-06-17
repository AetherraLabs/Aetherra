# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Dream Cycle Engine (DCE) — Phase 4
===================================

Offline reflective learning during idle periods.
Analyzes emotional trends, recombines symbolic events,
adjusts qualia parameters based on reflection.

Design:
- Emotional trend analysis (valence, certainty averages)
- Symbolic event recombination (pattern matching across memory)
- Reflective qualia adjustments (capped ±0.2 per cycle)
- Dream narrative synthesis (for debugging/introspection)
- Safety: All adjustments logged, bounded, and reversible
"""

from __future__ import annotations

import hashlib
import os
import time
from typing import Any, Dict, List, Optional

from Aetherra.consciousness.continuity_memory import ContinuityMemory, ContinuitySnapshot


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_requester() -> str:
    return os.environ.get("AETHERRA_PRINCIPAL", "").strip() or "dream_cycle"


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "dream_cycle" and capability in {
        "consciousness:reflect",
        "consciousness:write",
        "memory:read",
        "memory:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_dream_cycle(metadata: Dict[str, object]) -> None:
    from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

    decision = evaluate_intent(
        IntentDeclaration(
            requester=_guardian_requester(),
            subsystem="consciousness",
            action="consciousness.dream_cycle_run",
            target="consciousness:dream_cycle",
            purpose="Run offline reflective learning and update dream-cycle state",
            capabilities=(
                "consciousness:reflect",
                "consciousness:write",
                "memory:read",
                "memory:write",
            ),
            evidence=("DreamCycle.run",),
            reversible=True,
            rollback_plan="restore previous qualia learner parameters and dream-cycle state",
            metadata=metadata,
        ),
        capability_checker=_guardian_capability_checker,
    )
    if decision.status not in {
        GuardianStatus.ALLOW,
        GuardianStatus.ALLOW_LIMITED,
    }:
        raise PermissionError(f"guardian_denied:{decision.reason}:consciousness.dream_cycle_run")


class DreamCycle:
    """Reflective offline learning engine.

    Runs during idle periods (e.g., night cycle) to:
    - Analyze emotional trends from recent continuity snapshots
    - Recombine symbolic events to discover patterns
    - Adjust qualia parameters reflectively
    - Synthesize dream narratives for introspection
    """

    def __init__(
        self,
        continuity: ContinuityMemory,
        max_adjustment: float = 0.2,
        analysis_window: int = 50,
    ):
        """Initialize dream cycle engine.

        Args:
            continuity: ContinuityMemory instance with recent snapshots
            max_adjustment: Maximum reflective adjustment per cycle (default: 0.2)
            analysis_window: Number of snapshots to analyze (default: 50)
        """
        self.continuity = continuity
        self.max_adjustment = max_adjustment
        self.analysis_window = analysis_window
        self.last_run_ts: Optional[float] = None
        self.last_dream: Optional[Dict[str, Any]] = None

    def run(self, qualia_learner: Any) -> Dict[str, Any]:
        """Execute dream cycle.

        Analyzes recent continuity snapshots, adjusts qualia parameters,
        and synthesizes dream narrative.

        Args:
            qualia_learner: QualiaLearner instance to adjust

        Returns:
            Dict with dream metrics and narrative
        """
        # Get recent snapshots
        recent = self.continuity.get_recent(self.analysis_window)
        if len(recent) < 10:
            _guardian_preflight_dream_cycle(
                {
                    "operation": "run_insufficient_data",
                    "snapshot_count": len(recent),
                    "analysis_window": self.analysis_window,
                    "max_adjustment": round(float(self.max_adjustment), 6),
                    "will_adjust_params": False,
                    "will_store_dream": False,
                }
            )
            self.last_run_ts = time.time()
            return {
                "status": "insufficient_data",
                "snapshots_analyzed": len(recent),
                "adjustments": {},
                "narrative": "Not enough continuity data for dream cycle.",
            }

        # Emotional trend analysis
        trends = self._analyze_emotional_trends(recent)

        # Reflective qualia adjustments
        adjustments = self._compute_reflective_adjustments(trends)
        _guardian_preflight_dream_cycle(
            {
                "operation": "run",
                "snapshot_count": len(recent),
                "analysis_window": self.analysis_window,
                "max_adjustment": round(float(self.max_adjustment), 6),
                "trend_keys": tuple(sorted(trends)),
                "adjustment_keys": tuple(sorted(adjustments)),
                "adjustment_count": len(adjustments),
                "focus_count": sum(len(snapshot.focuses) for snapshot in recent),
                "intention_count": sum(len(snapshot.intentions) for snapshot in recent),
                "trust_key_count": sum(len(snapshot.trust_scores) for snapshot in recent),
                "qualia_learner_type_hash": _hash_value(type(qualia_learner).__name__),
                "will_adjust_params": bool(adjustments),
                "will_store_dream": True,
            }
        )
        self.last_run_ts = time.time()
        self._apply_adjustments(qualia_learner, adjustments)

        # Symbolic event recombination
        symbolic_events = self._recombine_symbolic_events(recent)

        # Synthesize dream narrative
        narrative = self._synthesize_narrative(trends, symbolic_events, adjustments)

        # Store dream for introspection
        self.last_dream = {
            "ts": self.last_run_ts,
            "snapshots_analyzed": len(recent),
            "trends": trends,
            "adjustments": adjustments,
            "symbolic_events": symbolic_events,
            "narrative": narrative,
        }

        return self.last_dream

    def _analyze_emotional_trends(self, snapshots: List[ContinuitySnapshot]) -> Dict[str, float]:
        """Analyze emotional trends from snapshots.

        Args:
            snapshots: List of continuity snapshots

        Returns:
            Dict with average valence, arousal, certainty, etc.
        """
        if not snapshots:
            return {}

        # Aggregate qualia dimensions
        dimensions = ["valence", "arousal", "certainty", "curiosity", "care", "fatigue"]
        trends = {}

        for dim in dimensions:
            values = [s.qualia.get(dim, 0.5) for s in snapshots]
            trends[f"avg_{dim}"] = sum(values) / len(values)

        # Compute variance (emotional stability)
        valence_vals = [s.qualia.get("valence", 0.0) for s in snapshots]
        valence_mean = trends["avg_valence"]
        valence_variance = sum((v - valence_mean) ** 2 for v in valence_vals) / len(valence_vals)
        trends["valence_stability"] = 1.0 - min(1.0, valence_variance)

        return trends

    def _compute_reflective_adjustments(self, trends: Dict[str, float]) -> Dict[str, float]:
        """Compute reflective qualia adjustments based on trends.

        Args:
            trends: Emotional trend analysis results

        Returns:
            Dict mapping qualia parameter to adjustment delta
        """
        adjustments = {}

        # If average valence was negative, increase curiosity_gain to explore
        if trends.get("avg_valence", 0.0) < -0.2:
            adjustments["curiosity_gain"] = min(self.max_adjustment, 0.15)

        # If average certainty was low, increase success_boost to build confidence
        if trends.get("avg_certainty", 0.5) < 0.4:
            adjustments["success_boost"] = min(self.max_adjustment, 0.1)

        # If average care was high, reduce error_penalty (compassion for self)
        if trends.get("avg_care", 0.5) > 0.7:
            adjustments["error_penalty"] = -min(self.max_adjustment, 0.1)

        # If valence stability was low, reduce arousal-driven reactivity
        if trends.get("valence_stability", 1.0) < 0.5:
            adjustments["certainty_gain"] = min(self.max_adjustment, 0.05)

        return adjustments

    def _apply_adjustments(self, qualia_learner: Any, adjustments: Dict[str, float]) -> None:
        """Apply reflective adjustments to qualia learner.

        Args:
            qualia_learner: QualiaLearner instance
            adjustments: Dict mapping parameter to delta
        """
        for param, delta in adjustments.items():
            # QualiaLearner uses 'p' for params
            if hasattr(qualia_learner, "p") and hasattr(qualia_learner.p, param):
                current = getattr(qualia_learner.p, param)
                new_val = max(0.0, min(1.0, current + delta))
                setattr(qualia_learner.p, param, new_val)

    def _recombine_symbolic_events(
        self, snapshots: List[ContinuitySnapshot]
    ) -> List[Dict[str, Any]]:
        """Recombine symbolic events from memory.

        Discovers patterns by matching focus types across snapshots.

        Args:
            snapshots: List of continuity snapshots

        Returns:
            List of symbolic event patterns
        """
        # Count focus type co-occurrences
        focus_pairs: Dict[str, int] = {}

        for snap in snapshots:
            focuses = snap.focuses
            for i, f1 in enumerate(focuses):
                for f2 in focuses[i + 1 :]:
                    # Use sorted string key instead of tuple
                    pair_key = f"{f1}|{f2}" if f1 < f2 else f"{f2}|{f1}"
                    focus_pairs[pair_key] = focus_pairs.get(pair_key, 0) + 1

        # Find top patterns (co-occurrences > 3)
        patterns = [
            {"events": pair.split("|"), "count": count}
            for pair, count in focus_pairs.items()
            if count > 3
        ]

        # Sort by count descending
        patterns.sort(key=lambda x: x["count"], reverse=True)

        return patterns[:10]  # Top 10 patterns

    def _synthesize_narrative(
        self,
        trends: Dict[str, float],
        symbolic_events: List[Dict[str, Any]],
        adjustments: Dict[str, float],
    ) -> str:
        """Synthesize dream narrative for introspection.

        Args:
            trends: Emotional trend analysis
            symbolic_events: Symbolic event patterns
            adjustments: Reflective adjustments applied

        Returns:
            Dream narrative string
        """
        lines = []

        # Emotional summary
        avg_valence = trends.get("avg_valence", 0.0)
        avg_certainty = trends.get("avg_certainty", 0.5)
        valence_stability = trends.get("valence_stability", 1.0)

        if avg_valence < -0.2:
            lines.append("Recent days felt heavy, shadows lingering.")
        elif avg_valence > 0.2:
            lines.append("Recent days brought warmth and light.")
        else:
            lines.append("Recent days passed in quiet neutrality.")

        if avg_certainty < 0.4:
            lines.append("Uncertainty clouded many moments.")
        elif avg_certainty > 0.7:
            lines.append("Confidence guided the path forward.")

        if valence_stability < 0.5:
            lines.append("Emotions swung like pendulums, seeking balance.")

        # Symbolic patterns
        if symbolic_events:
            lines.append("")
            lines.append("Recurring patterns emerged:")
            for pattern in symbolic_events[:3]:  # Top 3
                events = " ↔ ".join(pattern["events"])
                lines.append(f"  • {events} (appeared {pattern['count']} times)")

        # Reflective adjustments
        if adjustments:
            lines.append("")
            lines.append("Reflective shifts:")
            for param, delta in adjustments.items():
                direction = "increased" if delta > 0 else "decreased"
                lines.append(f"  • {param} {direction} by {abs(delta):.3f}")

        # Dream conclusion
        lines.append("")
        lines.append("The dream cycle completes. Continuity renewed.")

        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Get dream cycle statistics.

        Returns:
            Dict with last run timestamp, avg valence, etc.
        """
        if not self.last_dream:
            return {
                "last_run_ts": None,
                "avg_valence": None,
                "snapshots_analyzed": 0,
                "adjustments_count": 0,
            }

        return {
            "last_run_ts": self.last_dream["ts"],
            "avg_valence": self.last_dream["trends"].get("avg_valence", 0.0),
            "avg_certainty": self.last_dream["trends"].get("avg_certainty", 0.5),
            "valence_stability": self.last_dream["trends"].get("valence_stability", 1.0),
            "snapshots_analyzed": self.last_dream["snapshots_analyzed"],
            "adjustments_count": len(self.last_dream["adjustments"]),
            "symbolic_patterns": len(self.last_dream["symbolic_events"]),
        }

    def get_last_narrative(self) -> Optional[str]:
        """Get last dream narrative.

        Returns:
            Dream narrative string or None if no dream has run
        """
        if not self.last_dream:
            return None
        return self.last_dream["narrative"]
