#!/usr/bin/env python3
"""Consciousness Learning Loop.

Phase 4 implementation that closes the decision -> outcome -> memory -> strategy
cycle using lightweight heuristics and persisted learning state.
"""

from __future__ import annotations

# Standard library imports
import copy
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Local imports
from .decision_engine import Decision
from .episodic_store import get_episodic_store


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _learning_capability_checker(requester: str, capability: str) -> bool:
    if requester == "consciousness:learning" and capability in {
        "consciousness:write",
        "memory:write",
        "fs:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


@dataclass
class LearningAdjustment:
    context: str
    action: str
    success: bool
    score: float
    success_rate: float
    recommended_confidence_hint: float
    recommended_risk_hint: str
    strategy_delta: str
    iteration: int
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class LearningLoop:
    """Learns from decision outcomes and adapts future decision hints.

    Design goals:
    - Keep runtime dependencies optional and resilient
    - Persist compact state to survive process restarts
    - Integrate with episodic store and memory engine best-effort
    """

    def __init__(
        self,
        episodic_store=None,
        memory_engine=None,
        state_path: Optional[str | Path] = None,
    ) -> None:
        default_state = os.getenv(
            "AETHERRA_LEARNING_STATE_PATH", ".aetherra/learning_loop_state.json"
        )
        self.state_path = Path(state_path or default_state)

        self.episodic_store = episodic_store or get_episodic_store()
        self.memory_engine: Any = (
            memory_engine if memory_engine is not None else self._build_memory_engine()
        )

        self.state: Dict[str, Any] = {
            "global": {
                "iterations": 0,
                "total_successes": 0,
                "total_failures": 0,
                "last_updated": None,
            },
            "contexts": {},
        }
        self._load_state()

    def process_outcome(
        self,
        decision: Decision | Dict[str, Any],
        outcome: Dict[str, Any],
        context: Optional[str] = None,
    ) -> LearningAdjustment:
        """Run one full learning cycle and return strategy adjustment details."""
        normalized_decision = self._normalize_decision(decision)
        resolved_context = (context or outcome.get("context") or "general").strip() or "general"

        action = str(normalized_decision.get("action", "analyze"))
        score = self._score_outcome(outcome)
        explicit_success = outcome.get("success")
        success = bool(explicit_success) if isinstance(explicit_success, bool) else score >= 0.6

        previous_state = copy.deepcopy(self.state)
        bucket = self._get_action_bucket(resolved_context, action)
        bucket["attempts"] += 1
        bucket["successes"] += 1 if success else 0
        bucket["failures"] += 0 if success else 1
        bucket["total_score"] += score
        bucket["last_score"] = score
        bucket["last_latency_ms"] = int(outcome.get("latency_ms", 0) or 0)
        bucket["last_outcome_at"] = datetime.utcnow().isoformat()

        success_rate = bucket["successes"] / max(1, bucket["attempts"])
        avg_score = bucket["total_score"] / max(1, bucket["attempts"])

        confidence_hint = self._recommended_confidence(success_rate, avg_score)
        risk_hint = self._recommended_risk(success_rate, score)
        strategy_delta = self._strategy_delta(success_rate, score)

        self._increment_global(success)
        try:
            self._save_state()
        except Exception:
            self.state = previous_state
            raise

        adjustment = LearningAdjustment(
            context=resolved_context,
            action=action,
            success=success,
            score=round(score, 3),
            success_rate=round(success_rate, 3),
            recommended_confidence_hint=round(confidence_hint, 3),
            recommended_risk_hint=risk_hint,
            strategy_delta=strategy_delta,
            iteration=int(self.state["global"]["iterations"]),
        )

        self._record_episode(adjustment, outcome, normalized_decision)
        self._update_memory(adjustment)
        return adjustment

    def get_decision_hints(self, context: str, action: Optional[str] = None) -> Dict[str, Any]:
        """Return learned hints to bias future decisions for a context/action."""
        context = (context or "general").strip() or "general"
        ctx = self.state["contexts"].get(context, {})
        actions = ctx.get("actions", {})

        if not actions:
            return {
                "confidence_hint": 0.6,
                "risk_hint": "medium",
                "source": "default",
            }

        selected_name = action if action in actions else self._best_action(actions)
        selected = actions[selected_name]
        attempts = max(1, int(selected.get("attempts", 1)))
        success_rate = float(selected.get("successes", 0)) / attempts
        avg_score = float(selected.get("total_score", 0.0)) / attempts

        return {
            "action": selected_name,
            "confidence_hint": round(self._recommended_confidence(success_rate, avg_score), 3),
            "risk_hint": self._recommended_risk(success_rate, avg_score),
            "source": "learned",
            "attempts": attempts,
            "success_rate": round(success_rate, 3),
        }

    def recent_similar_episodes(
        self, context: str, action: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Return recent outcome episodes matching context and action."""
        context = (context or "general").strip() or "general"
        action = (action or "").strip()
        if not action:
            return []

        episodes: List[Dict[str, Any]] = []
        try:
            recent = self.episodic_store.list_recent(max(limit * 20, 100))
            for event in reversed(recent):
                if event.type != "outcome":
                    continue
                raw = event.raw or {}
                if raw.get("context") != context or raw.get("action") != action:
                    continue
                episodes.append(
                    {
                        "id": event.id,
                        "ts": event.ts.isoformat(),
                        "score": raw.get("score"),
                        "success": raw.get("success"),
                    }
                )
                if len(episodes) >= limit:
                    break
        except Exception:
            return []

        return episodes

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.state.update(loaded)
                self.state.setdefault("global", {})
                self.state.setdefault("contexts", {})
        except Exception:
            # Ignore malformed state and continue with defaults.
            return

    def _save_state(self) -> None:
        global_state = self.state.setdefault("global", {})
        previous_last_updated = global_state.get("last_updated")
        global_state["last_updated"] = datetime.utcnow().isoformat()
        try:
            self._guardian_preflight_state_save()
        except Exception:
            global_state["last_updated"] = previous_last_updated
            raise
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.state, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _guardian_preflight_state_save(self):
        from Aetherra.guardian import IntentDeclaration, evaluate_intent

        requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "consciousness:learning"
        approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
        contexts = self.state.get("contexts", {})
        if not isinstance(contexts, dict):
            contexts = {}
        action_count = 0
        context_hashes: list[str | None] = []
        action_hashes: list[str | None] = []
        for context_name, context_data in contexts.items():
            context_hashes.append(_hash_value(context_name))
            if not isinstance(context_data, dict):
                continue
            actions = context_data.get("actions", {})
            if not isinstance(actions, dict):
                continue
            action_count += len(actions)
            action_hashes.extend(_hash_value(action_name) for action_name in actions)

        global_state = self.state.get("global", {})
        if not isinstance(global_state, dict):
            global_state = {}
        state_payload = json.dumps(self.state, sort_keys=True, default=str)
        decision = evaluate_intent(
            IntentDeclaration(
                requester=requester,
                subsystem="consciousness",
                action="consciousness.learning_state_save",
                target="learning_loop_state",
                purpose="Persist compact decision-outcome learning hints for future consciousness decisions",
                capabilities=("consciousness:write", "memory:write", "fs:write"),
                evidence=("LearningLoop.process_outcome",),
                reversible=True,
                rollback_plan="restore the previous learning-loop state file or remove the latest saved state",
                metadata={
                    "path_hash": _hash_value(self.state_path.resolve()),
                    "state_hash": _hash_value(state_payload),
                    "state_bytes": len(state_payload.encode("utf-8")),
                    "iteration_count": int(global_state.get("iterations", 0) or 0),
                    "total_successes": int(global_state.get("total_successes", 0) or 0),
                    "total_failures": int(global_state.get("total_failures", 0) or 0),
                    "context_count": len(contexts),
                    "action_count": action_count,
                    "context_hashes": context_hashes[:10],
                    "action_hashes": action_hashes[:20],
                },
            ),
            approval_id=approval_id,
            capability_checker=_learning_capability_checker,
        )
        if not decision.allowed:
            raise PermissionError(f"guardian_denied:{decision.reason}")
        return decision

    def _get_action_bucket(self, context: str, action: str) -> Dict[str, Any]:
        contexts = self.state.setdefault("contexts", {})
        ctx = contexts.setdefault(context, {"actions": {}})
        actions = ctx.setdefault("actions", {})
        return actions.setdefault(
            action,
            {
                "attempts": 0,
                "successes": 0,
                "failures": 0,
                "total_score": 0.0,
                "last_score": 0.0,
                "last_latency_ms": 0,
                "last_outcome_at": None,
            },
        )

    def _increment_global(self, success: bool) -> None:
        g = self.state.setdefault("global", {})
        g["iterations"] = int(g.get("iterations", 0)) + 1
        if success:
            g["total_successes"] = int(g.get("total_successes", 0)) + 1
        else:
            g["total_failures"] = int(g.get("total_failures", 0)) + 1

    @staticmethod
    def _normalize_decision(decision: Decision | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(decision, Decision):
            return asdict(decision)
        if isinstance(decision, dict):
            return decision
        raise TypeError("decision must be a Decision or dict")

    @staticmethod
    def _score_outcome(outcome: Dict[str, Any]) -> float:
        quality = float(outcome.get("quality", 0.5))
        latency_ms = float(outcome.get("latency_ms", 0.0) or 0.0)
        regression = bool(outcome.get("regression", False))

        # Convert latency into a mild penalty capped at 0.2.
        latency_penalty = min(0.2, max(0.0, latency_ms / 10000.0))
        regression_penalty = 0.25 if regression else 0.0

        score = quality - latency_penalty - regression_penalty
        return max(0.0, min(1.0, score))

    @staticmethod
    def _recommended_confidence(success_rate: float, avg_score: float) -> float:
        blended = (0.65 * success_rate) + (0.35 * avg_score)
        return max(0.3, min(0.95, 0.3 + (0.7 * blended)))

    @staticmethod
    def _recommended_risk(success_rate: float, score: float) -> str:
        signal = 0.5 * success_rate + 0.5 * score
        if signal >= 0.75:
            return "low"
        if signal >= 0.45:
            return "medium"
        return "high"

    @staticmethod
    def _strategy_delta(success_rate: float, score: float) -> str:
        signal = 0.5 * success_rate + 0.5 * score
        if signal >= 0.75:
            return "increase_autonomy"
        if signal < 0.45:
            return "increase_caution"
        return "maintain"

    @staticmethod
    def _best_action(actions: Dict[str, Dict[str, Any]]) -> str:
        best_name = "analyze"
        best_score = -1.0
        for action, stats in actions.items():
            attempts = max(1, int(stats.get("attempts", 1)))
            success_rate = float(stats.get("successes", 0)) / attempts
            avg_score = float(stats.get("total_score", 0.0)) / attempts
            rank = (0.6 * success_rate) + (0.4 * avg_score)
            if rank > best_score:
                best_name = action
                best_score = rank
        return best_name

    def _record_episode(
        self,
        adjustment: LearningAdjustment,
        outcome: Dict[str, Any],
        decision: Dict[str, Any],
    ) -> None:
        try:
            self.episodic_store.new_event(
                type="outcome",
                sub_type="learning_feedback",
                source="learning_loop",
                content=(
                    f"context={adjustment.context};action={adjustment.action};"
                    f"success={adjustment.success};score={adjustment.score}"
                ),
                importance=0.75 if adjustment.success else 0.85,
                tags=["learning", adjustment.action, adjustment.context],
                raw={
                    "context": adjustment.context,
                    "action": adjustment.action,
                    "success": adjustment.success,
                    "score": adjustment.score,
                    "outcome": outcome,
                    "decision": {
                        "action": decision.get("action"),
                        "confidence": decision.get("confidence"),
                        "risk_level": decision.get("risk_level"),
                    },
                },
            )
        except Exception:
            return

    def _update_memory(self, adjustment: LearningAdjustment) -> None:
        if self.memory_engine is None:
            return

        summary = (
            f"Learning update for context '{adjustment.context}' and action '{adjustment.action}': "
            f"success={adjustment.success}, score={adjustment.score:.2f}, "
            f"success_rate={adjustment.success_rate:.2f}, delta={adjustment.strategy_delta}."
        )
        payload = {
            "content": summary,
            "metadata": {
                "type": "learning_update",
                "context": adjustment.context,
                "action": adjustment.action,
                "success": adjustment.success,
            },
        }

        try:
            if hasattr(self.memory_engine, "store"):
                self.memory_engine.store(payload)
                return
        except TypeError:
            # Some engines use store(content, metadata)
            try:
                self.memory_engine.store(summary, payload["metadata"])
                return
            except Exception:
                return
        except Exception:
            return

    @staticmethod
    def _build_memory_engine():
        try:
            from Aetherra.aetherra_core.memory.aetherra_memory_engine import AetherraMemoryEngine

            return AetherraMemoryEngine()
        except Exception:
            return None


LEARNING_LOOP_SINGLETON: LearningLoop | None = None


def get_learning_loop() -> LearningLoop:
    global LEARNING_LOOP_SINGLETON
    if LEARNING_LOOP_SINGLETON is None:
        LEARNING_LOOP_SINGLETON = LearningLoop()
    return LEARNING_LOOP_SINGLETON
