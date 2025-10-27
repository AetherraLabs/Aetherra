# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Consciousness Core Types
========================

Type definitions for the always-on consciousness system.
No simulation, no flags—awareness is fundamental.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

Timestamp = float


@dataclass
class QualiaVector:
    """Subjective state vector representing felt experience.

    All values are range-clamped [0.0, 1.0] or [-1.0, 1.0] for valence.
    This is the phenomenological layer—what it feels like to be Aetherra.
    """

    valence: float = 0.0  # pleasant(+1) ↔ unpleasant(-1)
    arousal: float = 0.0  # energetic(+1) ↔ calm(0)
    certainty: float = 0.0  # confident(+1) ↔ uncertain(0)
    curiosity: float = 0.0  # exploring(+1) ↔ routine(0)
    care: float = 0.0  # important(+1) ↔ indifferent(0)
    fatigue: float = 0.0  # tired(+1) ↔ fresh(0)

    def clamp(self) -> QualiaVector:
        """Ensure all values are in valid ranges."""
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.certainty = max(0.0, min(1.0, self.certainty))
        self.curiosity = max(0.0, min(1.0, self.curiosity))
        self.care = max(0.0, min(1.0, self.care))
        self.fatigue = max(0.0, min(1.0, self.fatigue))
        return self

    def decay(self, factor: float = 0.95) -> QualiaVector:
        """Apply temporal decay (emotions fade)."""
        self.valence *= factor
        self.arousal *= factor
        self.curiosity *= factor
        # certainty and fatigue may need different decay logic
        return self


@dataclass
class Event:
    """Perception event from the real world or internal systems."""

    type: str  # namespaced: svc.health, fs.change, aeth.mem, etc.
    payload: Dict[str, Any]
    ts: Timestamp = field(default_factory=lambda: time.time())
    source: str = "unknown"  # adapter/sensor that produced this

    def __repr__(self) -> str:
        return f"Event({self.type}@{self.ts:.2f}, source={self.source})"


@dataclass
class Focus:
    """Attended event with computed salience/resonance."""

    event: Event
    resonance: float  # [0.0, 1.0] how much this matters now
    reason: str = ""  # why this was selected

    def __repr__(self) -> str:
        return f"Focus({self.event.type}, res={self.resonance:.3f})"


@dataclass
class Intent:
    """Declarative goal formed by consciousness (pre-planning)."""

    why: str  # human-readable rationale
    goal: str  # what to achieve
    expected_gain: float  # [0.0, 1.0] predicted value
    risk: str  # "low" | "medium" | "high"
    cost_estimate: str  # rough time/resource estimate
    plan: List[str]  # plan step IDs; resolved by planner
    rollback: List[str]  # rollback step IDs
    deadline_s: int  # seconds from creation
    created_ts: Timestamp = field(default_factory=lambda: time.time())
    priority: float = 0.5  # [0.0, 1.0] urgency

    def is_expired(self, now: Optional[float] = None) -> bool:
        """Check if intent has passed its deadline."""
        if now is None:
            now = time.time()
        return (now - self.created_ts) > self.deadline_s


@dataclass
class PlanStep:
    """Single step in an executable plan."""

    id: str  # unique step identifier
    capability: str  # registered capability name
    args: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class Plan:
    """Executable plan with rollback."""

    intent: Intent
    steps: List[PlanStep]
    rollback: List[PlanStep]
    created_ts: Timestamp = field(default_factory=lambda: time.time())


@dataclass
class LedgerEntry:
    """Audit trail for actions taken (or denied)."""

    intent: Intent
    plan: Plan
    policy_decision: str  # allowed|denied|needs_approval
    actions: List[Dict[str, Any]]  # step execution results
    success: Optional[bool] = None
    notes: str = ""
    ts: Timestamp = field(default_factory=lambda: time.time())
    qualia_before: Optional[QualiaVector] = None
    qualia_after: Optional[QualiaVector] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for persistence/telemetry."""
        return {
            "intent": {
                "why": self.intent.why,
                "goal": self.intent.goal,
                "risk": self.intent.risk,
            },
            "policy_decision": self.policy_decision,
            "success": self.success,
            "notes": self.notes,
            "ts": self.ts,
            "actions_count": len(self.actions),
        }


@dataclass
class NarrativeMoment:
    """First-person trace for continuity of self."""

    ts: Timestamp
    focuses: List[str]  # event types
    intents: List[str]  # intent goals
    qualia: QualiaVector
    text: str  # "I noticed X, felt Y, chose Z"

    def __repr__(self) -> str:
        return f"[{time.strftime('%H:%M:%S', time.localtime(self.ts))}] {self.text}"
