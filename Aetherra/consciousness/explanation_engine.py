# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Explanation Engine (Phase 5)
============================

Produces human-readable "why" explanations across the lifecycle:
- Why an event was focused
- Why an intent was formed
- Why a policy allowed/denied
- Why an action outcome occurred

Lightweight and dependency-free initial implementation. Designed to
be extended with richer causal graphs and UI surfaces.
"""

from __future__ import annotations

import contextlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from Aetherra.consciousness.core.types import Focus, Intent, LedgerEntry, QualiaVector


@dataclass
class Why:
    """Structured explanation record.

    Attributes:
        subject: What is being explained (focus|intent|policy|action)
        because: Primary natural language reason
        confidence: 0.0–1.0 confidence score
        factors: Map of contributing factors and weights
        details: Arbitrary structured metadata for UI
    """

    subject: str
    because: str
    confidence: float = 0.6
    factors: Dict[str, float] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)


class ExplanationEngine:
    """Generates explanations and tracks coverage/latency metrics."""

    def __init__(self) -> None:
        self.total_events: int = 0
        self.total_explained: int = 0
        self.total_latency_ms: float = 0.0
        self.last_focus_explanations: List[Why] = []
        self.last_intent_explanations: List[Why] = []
        self.last_policy_explanations: List[Why] = []
        self.last_action_explanations: List[Why] = []
        # Optional JSONL persistence for audit
        self._persist_enabled = os.getenv("AETHERRA_EXPLAIN_PERSIST", "1") == "1"
        self._log_path = Path(os.getenv("AETHERRA_EXPLAIN_LOG_PATH", "data/explanations_log.jsonl"))
        self._max_bytes = int(os.getenv("AETHERRA_EXPLAIN_LOG_MAX_BYTES", str(2 * 1024 * 1024)))
        self._max_backups = int(os.getenv("AETHERRA_EXPLAIN_LOG_BACKUPS", "3"))
        if self._persist_enabled:
            self._log_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Focus ---
    def explain_focus(self, focus: Focus, qualia: Optional[QualiaVector] = None) -> Why:
        """Explain why a focus was selected."""
        self.total_events += 1

        because = focus.reason or "resonance with goals"
        factors = {"resonance": round(focus.resonance, 3)}
        if qualia is not None:
            factors.update(
                {
                    "arousal": round(qualia.arousal, 3),
                    "valence": round(qualia.valence, 3),
                    "certainty": round(qualia.certainty, 3),
                }
            )

        why = Why(
            subject=f"focus:{focus.event.type}",
            because=because,
            confidence=min(1.0, 0.5 + focus.resonance * 0.5),
            factors=factors,
            details={"event_payload_keys": list(focus.event.payload.keys())[:8]},
        )

        self.last_focus_explanations.append(why)
        self._append_log("focus", why)
        self.total_explained += 1
        self._trim_buffers()
        return why

    # --- Intent ---
    def explain_intent(self, intent: Intent, from_focus: Optional[Focus] = None) -> Why:
        because = intent.why or "derived from salient focus"
        factors: Dict[str, float] = {
            "expected_gain": intent.expected_gain,
            "priority": intent.priority,
        }
        if from_focus is not None:
            factors["focus_resonance"] = round(from_focus.resonance, 3)

        why = Why(
            subject=f"intent:{intent.goal}",
            because=because,
            confidence=min(1.0, 0.4 + intent.expected_gain * 0.6),
            factors=factors,
            details={"risk": intent.risk, "deadline_s": intent.deadline_s},
        )
        self.last_intent_explanations.append(why)
        self._append_log("intent", why)
        self.total_explained += 1
        self._trim_buffers()
        return why

    # --- Policy ---
    def explain_policy(
        self,
        decision_status: str,
        reason: str,
        mode: str,
        capabilities: List[str],
    ) -> Why:
        factors = {"mode": 1.0 if mode else 0.0, "capabilities_count": float(len(capabilities))}
        why = Why(
            subject="policy",
            because=reason,
            confidence=0.7 if decision_status == "allowed" else 0.6,
            factors=factors,
            details={"status": decision_status, "mode": mode, "capabilities": capabilities[:6]},
        )
        self.last_policy_explanations.append(why)
        self._append_log("policy", why)
        self.total_explained += 1
        self._trim_buffers()
        return why

    # --- Action ---
    def explain_action(self, ledger: LedgerEntry) -> Why:
        because = ledger.notes or "execution outcome"
        factors = {
            "steps": float(len(ledger.actions)),
            "policy": 1.0 if ledger.policy_decision else 0.0,
        }
        if ledger.success is not None:
            factors["success"] = 1.0 if ledger.success else 0.0

        why = Why(
            subject=f"action:{ledger.plan.intent.goal}",
            because=because,
            confidence=0.8 if ledger.success else 0.5,
            factors=factors,
            details={"policy_decision": ledger.policy_decision},
        )
        self.last_action_explanations.append(why)
        self._append_log("action", why)
        self.total_explained += 1
        self._trim_buffers()
        return why

    # --- Metrics ---
    def get_metrics(self) -> Dict[str, Any]:
        coverage = (self.total_explained / self.total_events) if self.total_events else 0.0
        avg_latency_ms = (self.total_latency_ms / self.total_events) if self.total_events else 0.0
        return {
            "coverage_ratio": round(coverage, 3),
            "avg_latency_ms": round(avg_latency_ms, 2),
            "explained_events": self.total_explained,
            "total_events": self.total_events,
        }

    def _trim_buffers(self) -> None:
        self.last_focus_explanations = self.last_focus_explanations[-100:]
        self.last_intent_explanations = self.last_intent_explanations[-100:]
        self.last_policy_explanations = self.last_policy_explanations[-100:]
        self.last_action_explanations = self.last_action_explanations[-100:]

    def _append_log(self, event: str, why: Why) -> None:
        if not self._persist_enabled:
            return
        try:
            payload = {"event": event, "ts": time.time(), **asdict(why)}
            self._maybe_rotate()
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            # Persistence is best-effort; never block
            pass

    def _maybe_rotate(self) -> None:
        try:
            if not self._log_path.exists():
                return
            if self._log_path.stat().st_size < self._max_bytes:
                return
            for idx in range(self._max_backups, 0, -1):
                src = self._log_path.with_suffix(self._log_path.suffix + f".{idx}")
                dst = self._log_path.with_suffix(self._log_path.suffix + f".{idx + 1}")
                if src.exists():
                    if idx == self._max_backups:
                        with contextlib.suppress(Exception):
                            src.unlink()
                    else:
                        with contextlib.suppress(Exception):
                            src.rename(dst)
            backup1 = self._log_path.with_suffix(self._log_path.suffix + ".1")
            with contextlib.suppress(Exception):
                self._log_path.rename(backup1)
        except Exception:
            pass
