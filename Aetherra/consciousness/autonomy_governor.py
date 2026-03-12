#!/usr/bin/env python3
"""Autonomy Governor.

Applies safety guardrails to proposed autonomous actions.
"""

from __future__ import annotations

# Standard library imports
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class GovernorDecision:
    allowed: bool
    reason: str
    risk_score: float
    requires_approval: bool
    violations: List[str] = field(default_factory=list)


class AutonomyGovernor:
    """Safety envelope for autonomous operations."""

    def __init__(self) -> None:
        self.max_file_changes = int(os.getenv("AETHERRA_MAX_FILE_CHANGES", "25"))
        self.max_api_calls_per_min = int(os.getenv("AETHERRA_MAX_API_CALLS_PER_MIN", "120"))
        self.max_risk_score = float(os.getenv("AETHERRA_MAX_RISK_SCORE", "0.75"))
        self.require_approval_for_breaking = os.getenv("AETHERRA_APPROVAL_BREAKING", "1") == "1"
        self.forbidden_ops = {
            "rm -rf",
            "format c:",
            "del /s /q",
            "shutdown",
            "reboot",
            "git reset --hard",
        }
        self._api_call_times: deque[float] = deque()

    def evaluate(self, action: Dict[str, Any]) -> GovernorDecision:
        """Evaluate whether an autonomous action is safe to execute."""
        violations: List[str] = []

        op = str(action.get("operation", "")).lower()
        file_changes = int(action.get("file_changes", 0) or 0)
        api_calls = int(action.get("api_calls", 0) or 0)
        risk_score = float(action.get("risk_score", 0.0) or 0.0)
        breaking = bool(action.get("breaking_change", False))

        if any(token in op for token in self.forbidden_ops):
            violations.append("forbidden_operation")

        if file_changes > self.max_file_changes:
            violations.append("file_change_limit_exceeded")

        if risk_score > self.max_risk_score:
            violations.append("risk_limit_exceeded")

        if api_calls > 0:
            self._register_api_calls(api_calls)
            if not self._check_rate_limit():
                violations.append("api_rate_limit_exceeded")

        requires_approval = False
        if breaking and self.require_approval_for_breaking:
            requires_approval = True
            violations.append("breaking_change_requires_approval")

        if risk_score > 0.6:
            requires_approval = True

        allowed = len([v for v in violations if v != "breaking_change_requires_approval"]) == 0
        reason = "allowed" if allowed else ",".join(violations)

        return GovernorDecision(
            allowed=allowed and not (breaking and self.require_approval_for_breaking),
            reason=reason,
            risk_score=risk_score,
            requires_approval=requires_approval,
            violations=violations,
        )

    def _register_api_calls(self, count: int) -> None:
        now = time.time()
        for _ in range(count):
            self._api_call_times.append(now)
        self._prune_old_calls(now)

    def _prune_old_calls(self, now: float | None = None) -> None:
        ts = now if now is not None else time.time()
        while self._api_call_times and (ts - self._api_call_times[0]) > 60.0:
            self._api_call_times.popleft()

    def _check_rate_limit(self) -> bool:
        self._prune_old_calls()
        return len(self._api_call_times) <= self.max_api_calls_per_min


AUTONOMY_GOVERNOR_SINGLETON: AutonomyGovernor | None = None


def get_autonomy_governor() -> AutonomyGovernor:
    global AUTONOMY_GOVERNOR_SINGLETON
    if AUTONOMY_GOVERNOR_SINGLETON is None:
        AUTONOMY_GOVERNOR_SINGLETON = AutonomyGovernor()
    return AUTONOMY_GOVERNOR_SINGLETON
