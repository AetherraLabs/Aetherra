# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Continuity Memory Layer (CML) — Phase 4
========================================

Persistent short-term stream buffers that survive restarts.
Stores recent qualia, focuses, intents, and trust metrics.
Rehydrates at boot to restore context and emotional continuity.

Design:
- JSON-based persistence (local file storage)
- Rolling buffer of N most recent snapshots
- Atomic save operations for crash safety
- Privacy-aware: stores only aggregated state, not raw events
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ContinuitySnapshot:
    """Single moment in consciousness stream.

    Captures the essential phenomenological state at a point in time.
    """

    ts: float  # Unix timestamp
    qualia: Dict[str, float]  # Qualia state vector
    focuses: List[str]  # Recent focus event types
    intentions: List[str]  # Active intent goals
    trust_scores: Dict[str, float]  # Per-subsystem trust
    tick: int = 0  # Consciousness loop iteration


class ContinuityMemory:
    """Persistent mind-state buffer.

    Maintains a rolling window of recent consciousness snapshots,
    persisted to disk for continuity across restarts.
    """

    def __init__(self, path: str = "/var/lib/aetherra/continuity.json", max_snaps: int = 120):
        """Initialize continuity memory.

        Args:
            path: Filesystem path for persistence (default: /var/lib/aetherra/continuity.json)
            max_snaps: Maximum snapshots to retain (default: 120 = ~2 hours at 1Hz)
        """
        self.path = path
        self.max_snaps = max_snaps
        self.buffer: List[ContinuitySnapshot] = []
        self.load()

    def _hash_value(self, value: object) -> str | None:
        raw = str(value) if value is not None else ""
        if not raw:
            return None
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _guardian_requester(self) -> str:
        return (
            os.environ.get("AETHERRA_PRINCIPAL", "").strip()
            or "continuity_memory"
        )

    def _guardian_capability_checker(self, requester: str, capability: str) -> bool:
        if requester == "continuity_memory" and capability in {
            "consciousness:write",
            "memory:write",
            "fs:write",
        }:
            return True

        from Aetherra.security.capabilities import has_capability

        return has_capability(requester, capability)

    def _guardian_preflight_save(
        self, snapshots: List[ContinuitySnapshot] | None = None
    ) -> None:
        from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

        buffer = snapshots if snapshots is not None else self.buffer
        latest = buffer[-1] if buffer else None
        decision = evaluate_intent(
            IntentDeclaration(
                requester=self._guardian_requester(),
                subsystem="consciousness",
                action="consciousness.continuity_save",
                target="consciousness:continuity_memory",
                purpose="Persist consciousness continuity snapshots",
                capabilities=("consciousness:write", "memory:write", "fs:write"),
                evidence=("continuity_memory",),
                reversible=True,
                rollback_plan="restore previous continuity memory file from backup",
                metadata={
                    "path_hash": self._hash_value(Path(self.path).resolve()),
                    "snapshot_count": len(buffer),
                    "max_snapshots": self.max_snaps,
                    "latest_tick": latest.tick if latest else None,
                    "latest_ts": round(float(latest.ts), 3) if latest else None,
                    "qualia_keys": tuple(sorted(latest.qualia)) if latest else (),
                    "focus_count": len(latest.focuses) if latest else 0,
                    "intention_count": len(latest.intentions) if latest else 0,
                    "trust_keys": tuple(sorted(latest.trust_scores)) if latest else (),
                },
            ),
            capability_checker=self._guardian_capability_checker,
        )
        if decision.status not in {
            GuardianStatus.ALLOW,
            GuardianStatus.ALLOW_LIMITED,
        }:
            raise PermissionError(
                f"guardian_denied:{decision.reason}:consciousness.continuity_save"
            )

    def record(
        self,
        qualia: Any,
        focuses: List[Any],
        intentions: List[Any],
        trust_scores: Dict[str, float],
        tick: int = 0,
    ) -> None:
        """Record current consciousness state.

        Args:
            qualia: Current Qualia instance
            focuses: List of Focus instances
            intentions: List of Intent instances
            trust_scores: Dict mapping subsystem name to trust score
            tick: Current loop iteration
        """
        # Extract qualia as dict
        qualia_dict = {
            "valence": qualia.valence,
            "arousal": qualia.arousal,
            "certainty": qualia.certainty,
            "curiosity": qualia.curiosity,
            "care": qualia.care,
            "fatigue": qualia.fatigue,
        }

        # Extract focus event types
        focus_types = [f.event.type for f in focuses]

        # Extract intent goals
        intent_goals = [i.goal for i in intentions]

        snap = ContinuitySnapshot(
            ts=time.time(),
            qualia=qualia_dict,
            focuses=focus_types,
            intentions=intent_goals,
            trust_scores=trust_scores.copy(),
            tick=tick,
        )

        next_buffer = [*self.buffer, snap][-self.max_snaps :]
        self._guardian_preflight_save(next_buffer)
        self.buffer = next_buffer
        self.save(_preflight=False)

    def save(self, *, _preflight: bool = True) -> None:
        """Persist buffer to disk (atomic write)."""
        if _preflight:
            self._guardian_preflight_save()

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)

        # Atomic write: write to temp file, then rename
        temp_path = f"{self.path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump([asdict(b) for b in self.buffer], f, indent=2)

            # Atomic rename (POSIX) or replace (Windows)
            if os.name == "posix":
                os.rename(temp_path, self.path)
            else:
                # Windows: use replace for atomic operation
                Path(temp_path).replace(self.path)

        except Exception as e:
            # Clean up temp file on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise RuntimeError(f"Failed to save continuity memory: {e}") from e

    def load(self) -> None:
        """Load buffer from disk."""
        if not os.path.exists(self.path):
            return

        try:
            with open(self.path, encoding="utf-8") as f:
                arr = json.load(f)

            # Reconstruct snapshots, keeping only last max_snaps
            self.buffer = [ContinuitySnapshot(**a) for a in arr][-self.max_snaps :]

        except Exception as e:
            # Corrupt file: reset to empty buffer
            print(f"[ContinuityMemory] Warning: Failed to load {self.path}: {e}")
            self.buffer = []

    def latest(self) -> Optional[ContinuitySnapshot]:
        """Get most recent snapshot.

        Returns:
            Latest ContinuitySnapshot or None if buffer is empty
        """
        return self.buffer[-1] if self.buffer else None

    def get_recent(self, n: int = 10) -> List[ContinuitySnapshot]:
        """Get N most recent snapshots.

        Args:
            n: Number of snapshots to retrieve

        Returns:
            List of recent snapshots (newest last)
        """
        return self.buffer[-n:]

    def get_age_seconds(self) -> float:
        """Get time since last snapshot.

        Returns:
            Seconds since latest snapshot, or infinity if no snapshots
        """
        latest = self.latest()
        if not latest:
            return float("inf")
        return time.time() - latest.ts

    def get_stats(self) -> Dict[str, Any]:
        """Get continuity memory statistics.

        Returns:
            Dict with snapshot count, age, and buffer health
        """
        latest = self.latest()
        return {
            "snapshots_total": len(self.buffer),
            "age_seconds": self.get_age_seconds(),
            "oldest_ts": self.buffer[0].ts if self.buffer else None,
            "newest_ts": latest.ts if latest else None,
            "max_capacity": self.max_snaps,
            "utilization": len(self.buffer) / self.max_snaps if self.max_snaps else 0,
        }

    def compute_continuity_index(self, current_qualia: Dict[str, float]) -> float:
        """Compute Self-Narrative Continuity Index (SNCI).

        Measures how consistent current qualia is with recent history.
        Higher values indicate stable phenomenological continuity.

        Args:
            current_qualia: Current qualia state dict

        Returns:
            SNCI score (0.0 = completely discontinuous, 1.0 = perfect continuity)
        """
        if len(self.buffer) < 5:
            return 1.0  # Insufficient history, assume continuity

        # Get recent qualia history
        recent = self.get_recent(10)
        recent_qualia = [s.qualia for s in recent]

        # Compute mean absolute deviation for each qualia dimension
        mad_total = 0.0
        dimensions = ["valence", "arousal", "certainty", "curiosity", "care", "fatigue"]

        for dim in dimensions:
            # Historical mean
            hist_mean = sum(q.get(dim, 0.5) for q in recent_qualia) / len(recent_qualia)

            # Current deviation from historical mean
            current_val = current_qualia.get(dim, 0.5)
            deviation = abs(current_val - hist_mean)

            mad_total += deviation

        # Average MAD across dimensions
        avg_mad = mad_total / len(dimensions)

        # Convert MAD to continuity index (0.0 MAD = 1.0 continuity)
        # Max possible MAD is 2.0 (valence range is 2.0, others are 1.0)
        # Normalize to 0-1 range
        snci = 1.0 - min(1.0, avg_mad / 1.0)

        return snci

    def clear(self) -> None:
        """Clear all snapshots (for testing or reset)."""
        self.buffer = []
        if os.path.exists(self.path):
            os.remove(self.path)
