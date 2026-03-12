#!/usr/bin/env python3
"""Consciousness Decision Engine.

Phase 3 implementation that converts a situation payload into a structured
Decision with confidence, risk assessment, alternatives, and rationale.
"""

from __future__ import annotations

# Standard library imports
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

# Local imports (optional and guarded at runtime)
from .episodic_store import get_episodic_store


@dataclass
class Decision:
    action: str
    confidence: float
    rationale: str
    alternatives: List[str]
    risk_level: str
    requires_approval: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class ConsciousnessDecisionEngine:
    """Rule-guided decision engine with memory-informed confidence adjustment."""

    def __init__(self) -> None:
        self.enabled = os.getenv("AETHERRA_CONSCIOUSNESS_ENABLED", "0") == "1"
        self.approval_threshold = float(os.getenv("AETHERRA_DECISION_APPROVAL_THRESHOLD", "0.65"))

    def decide(self, situation: Dict[str, Any]) -> Decision:
        """Produce a decision from a situation payload.

        Situation keys (optional):
        - goal: str
        - context: str
        - risk_hint: low|medium|high
        - urgency: low|medium|high|critical
        - confidence_hint: float in [0,1]
        - constraints: list[str]
        - candidate_actions: list[str]
        """
        goal = str(situation.get("goal", "stabilize")).strip() or "stabilize"
        context = str(situation.get("context", "general"))
        urgency = str(situation.get("urgency", "medium")).lower()
        risk_hint = str(situation.get("risk_hint", "medium")).lower()
        constraints = [str(c) for c in situation.get("constraints", [])]

        candidates = self._candidate_actions(goal, context, situation)
        score_map = self._score_actions(candidates, urgency, risk_hint, constraints)
        best = max(score_map, key=score_map.get)

        base_conf = float(situation.get("confidence_hint", 0.6))
        confidence = self._adjust_confidence(base_conf, context, best)

        risk_level = self._derive_risk_level(best, risk_hint, urgency)
        requires_approval = confidence < self.approval_threshold or risk_level == "high"

        alternatives = [a for a in candidates if a != best][:3]
        rationale = (
            f"Selected '{best}' for goal '{goal}' in context '{context}'. "
            f"urgency={urgency}, risk_hint={risk_hint}, confidence={confidence:.2f}."
        )

        decision = Decision(
            action=best,
            confidence=round(confidence, 3),
            rationale=rationale,
            alternatives=alternatives,
            risk_level=risk_level,
            requires_approval=requires_approval,
        )

        self._record_decision(context, decision)
        return decision

    def _candidate_actions(self, goal: str, context: str, situation: Dict[str, Any]) -> List[str]:
        provided = [str(x) for x in situation.get("candidate_actions", []) if str(x).strip()]
        if provided:
            return provided

        g = goal.lower()
        c = context.lower()
        candidates = ["analyze", "plan", "execute", "defer"]

        if "fix" in g or "bug" in g:
            candidates = ["analyze", "execute", "rollback", "defer"]
        elif "optimize" in g or "performance" in g:
            candidates = ["measure", "analyze", "execute", "defer"]
        elif "security" in g:
            candidates = ["audit", "restrict", "execute", "defer"]

        if "production" in c:
            candidates.insert(0, "analyze")
            if "execute" in candidates:
                candidates.remove("execute")
                candidates.append("execute")

        # Deduplicate preserving order
        out: List[str] = []
        seen = set()
        for x in candidates:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def _score_actions(
        self,
        actions: List[str],
        urgency: str,
        risk_hint: str,
        constraints: List[str],
    ) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        urgency_bonus = {
            "low": 0.0,
            "medium": 0.05,
            "high": 0.1,
            "critical": 0.2,
        }.get(urgency, 0.05)

        risk_penalty = {
            "low": 0.0,
            "medium": 0.05,
            "high": 0.15,
        }.get(risk_hint, 0.05)

        for action in actions:
            s = 0.5
            if action in {"analyze", "measure", "audit", "plan"}:
                s += 0.15
            if action in {"execute", "restrict", "rollback"}:
                s += urgency_bonus
                s -= risk_penalty
            if action == "defer":
                s -= 0.1
            if "no_destructive_ops" in constraints and action in {"execute", "rollback"}:
                s -= 0.25
            scores[action] = s
        return scores

    def _adjust_confidence(self, base: float, context: str, action: str) -> float:
        conf = max(0.0, min(1.0, base))

        # Memory-informed confidence: increase if same context/action recently succeeded.
        try:
            recent = get_episodic_store().list_recent(200)
            matching = [
                e
                for e in recent
                if e.type == "decision"
                and context in (e.content or "")
                and action in (e.content or "")
            ]
            if matching:
                conf += min(0.15, len(matching) * 0.02)
        except Exception:
            pass

        return max(0.0, min(1.0, conf))

    @staticmethod
    def _derive_risk_level(action: str, risk_hint: str, urgency: str) -> str:
        level = risk_hint if risk_hint in {"low", "medium", "high"} else "medium"
        if urgency == "critical" and action in {"execute", "rollback", "restrict"}:
            if level == "low":
                return "medium"
            if level == "medium":
                return "high"
        return level

    def _record_decision(self, context: str, decision: Decision) -> None:
        try:
            get_episodic_store().new_event(
                type="decision",
                source="decision_engine",
                content=(
                    f"context={context};action={decision.action};"
                    f"risk={decision.risk_level};confidence={decision.confidence}"
                ),
                importance=0.6,
            )
        except Exception:
            # Best effort only
            return


DECISION_ENGINE_SINGLETON: ConsciousnessDecisionEngine | None = None


def get_decision_engine() -> ConsciousnessDecisionEngine:
    global DECISION_ENGINE_SINGLETON
    if DECISION_ENGINE_SINGLETON is None:
        DECISION_ENGINE_SINGLETON = ConsciousnessDecisionEngine()
    return DECISION_ENGINE_SINGLETON
