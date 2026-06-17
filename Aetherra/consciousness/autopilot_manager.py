# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Autopilot Manager (Phase 5)
===========================

Evaluates eligibility for graduating autonomy mode to autopilot.
Tracks recent action outcomes and integrates trust/continuity signals.
"""

from __future__ import annotations

import hashlib
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

from Aetherra.consciousness.continuity_memory import ContinuityMemory
from Aetherra.consciousness.self_trust import SelfTrust


def _hash_value(value: object) -> str | None:
    raw = str(value) if value is not None else ""
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_requester() -> str:
    return os.environ.get("AETHERRA_PRINCIPAL", "").strip() or "autopilot_manager"


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "autopilot_manager" and capability in {
        "autonomy:control",
        "consciousness:write",
        "memory:write",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _guardian_preflight_autopilot_operation(
    *,
    action: str,
    purpose: str,
    metadata: Dict[str, object],
) -> None:
    from Aetherra.guardian import GuardianStatus, IntentDeclaration, evaluate_intent

    decision = evaluate_intent(
        IntentDeclaration(
            requester=_guardian_requester(),
            subsystem="consciousness",
            action=action,
            target="consciousness:autopilot_manager",
            purpose=purpose,
            capabilities=("consciousness:write", "autonomy:control", "memory:write"),
            evidence=("AutopilotManager", action),
            reversible=True,
            rollback_plan="restore previous autopilot history/status snapshot",
            metadata=metadata,
        ),
        capability_checker=_guardian_capability_checker,
    )
    if decision.status not in {
        GuardianStatus.ALLOW,
        GuardianStatus.ALLOW_LIMITED,
    }:
        raise PermissionError(f"guardian_denied:{decision.reason}:{action}")


@dataclass
class AutopilotStatus:
    mode: str
    eligible: bool
    reasons: List[str] = field(default_factory=list)
    days_clean: float = 0.0
    incidents_last_7d: int = 0
    suggested_mode: Optional[str] = None


class AutopilotManager:
    """Simple heuristic evaluator for autopilot graduation."""

    def __init__(self, self_trust: SelfTrust, continuity: ContinuityMemory) -> None:
        self.self_trust = self_trust
        self.continuity = continuity
        self.history: Deque[Tuple[float, bool, str]] = deque(maxlen=500)  # (ts, success, policy)
        self.last_eval: Optional[AutopilotStatus] = None

        # Thresholds (tunable via env)
        self.trust_threshold = float(os.getenv("AETHERRA_AUTOPILOT_TRUST_MIN", "60"))
        self.snci_threshold = float(os.getenv("AETHERRA_AUTOPILOT_SNCI_MIN", "0.5"))
        self.success_window = int(os.getenv("AETHERRA_AUTOPILOT_WINDOW", "50"))
        self.success_ratio_min = float(os.getenv("AETHERRA_AUTOPILOT_SUCCESS_MIN", "0.8"))

    def record_ledger(self, ts: float, success: bool, policy_status: str) -> None:
        _guardian_preflight_autopilot_operation(
            action="consciousness.autopilot_record_ledger",
            purpose="Record an autonomy action outcome for autopilot readiness evaluation",
            metadata={
                "operation": "record_ledger",
                "history_count": len(self.history),
                "success": bool(success),
                "policy_status_hash": _hash_value(policy_status),
                "timestamp_bucket": int(float(ts) // 3600) if ts else None,
                "success_window": self.success_window,
            },
        )
        self.history.append((ts, success, policy_status))

    def evaluate(self, current_mode: str) -> AutopilotStatus:
        reasons: List[str] = []
        now = time.time()

        # Compute recent success ratio
        recent = list(self.history)[-self.success_window :]
        successes = sum(1 for _, ok, _ in recent if ok)
        ratio = (successes / len(recent)) if recent else 0.0

        if len(recent) < max(10, int(self.success_window * 0.5)):
            reasons.append("insufficient_recent_actions")

        if ratio < self.success_ratio_min:
            reasons.append("low_success_ratio")

        # Trust and continuity signals
        trust = self.self_trust.global_score()
        if trust < self.trust_threshold:
            reasons.append("self_trust_below_threshold")

        snci = self.continuity.compute_continuity_index(
            {
                "valence": 0.0,
                "arousal": 0.0,
                "certainty": 0.0,
                "curiosity": 0.0,
                "care": 0.0,
                "fatigue": 0.0,
            }
        )
        if snci < self.snci_threshold:
            reasons.append("snci_below_threshold")

        # Incidents in last 7 days (failures or denied)
        seven_days_ago = now - 7 * 24 * 3600
        incidents = sum(
            1
            for ts, ok, pol in self.history
            if ts >= seven_days_ago and (not ok or pol != "allowed")
        )

        # Eligibility requires explicit opt-in
        opted_in = os.getenv("AETHERRA_AUTOPILOT_OPT_IN", "0") == "1"
        if not opted_in:
            reasons.append("explicit_opt_in_required")

        eligible = (
            opted_in
            and ratio >= self.success_ratio_min
            and trust >= self.trust_threshold
            and snci >= self.snci_threshold
            and incidents == 0
        )

        suggested_mode = None
        if eligible and current_mode in ("observe", "assist"):
            suggested_mode = "autopilot"

        status = AutopilotStatus(
            mode=current_mode,
            eligible=eligible,
            reasons=reasons,
            days_clean=round((now - seven_days_ago) / (24 * 3600), 2) if incidents == 0 else 0.0,
            incidents_last_7d=incidents,
            suggested_mode=suggested_mode,
        )
        _guardian_preflight_autopilot_operation(
            action="consciousness.autopilot_evaluate",
            purpose="Update autopilot readiness status from trust, continuity, and action history",
            metadata={
                "operation": "evaluate",
                "current_mode": current_mode,
                "history_count": len(self.history),
                "recent_count": len(recent),
                "success_ratio": round(float(ratio), 6),
                "trust": round(float(trust), 6),
                "snci": round(float(snci), 6),
                "incidents_last_7d": incidents,
                "eligible": eligible,
                "suggested_mode": suggested_mode,
                "reason_hashes": tuple(_hash_value(reason) for reason in reasons),
            },
        )
        self.last_eval = status
        return status

    def get_stats(self) -> Dict[str, float | int | str | bool]:
        recent = list(self.history)[-self.success_window :]
        successes = sum(1 for _, ok, _ in recent if ok)
        ratio = (successes / len(recent)) if recent else 0.0
        return {
            "recent_actions": len(recent),
            "recent_success_ratio": round(ratio, 3),
            "total_seen": len(self.history),
            "last_mode": self.last_eval.mode if self.last_eval else "",
            "eligible": self.last_eval.eligible if self.last_eval else False,
        }
