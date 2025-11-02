# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Policy Reasoner (Phase 5)
=========================

Provides minimal "what would need to change to allow this?" diffs
for denied or approval-required policy decisions.

Works alongside the existing PolicyEngine without modifying it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PolicyDiff:
    """Minimal changes to move a decision toward allowed.

    Attributes:
        mode_change: Suggested mode override (e.g., observe→assist)
        whitelist_add: Capabilities to add to whitelist
        blacklist_remove: Capabilities to remove from blacklist
        require_approval: Whether human approval is needed
        notes: Human-readable notes/rationale
    """

    mode_change: Optional[str] = None
    whitelist_add: List[str] = field(default_factory=list)
    blacklist_remove: List[str] = field(default_factory=list)
    require_approval: bool = False
    notes: str = ""


class PolicyReasoner:
    """Computes minimal policy diffs given a decision outcome."""

    def minimal_allow(
        self,
        mode: str,
        intent_risk: str,
        capabilities: List[str],
        decision_status: str,
        decision_reason: str,
        denied_caps: List[str] | None = None,
        whitelist_mode: bool = False,
        whitelisted: List[str] | None = None,
    ) -> PolicyDiff:
        denied_caps = denied_caps or []
        whitelisted = whitelisted or []

        diff = PolicyDiff()

        # Mode suggestions
        if (decision_status == "denied" and "observe" in decision_reason.lower()) or (
            mode == "observe"
        ):
            diff.mode_change = "assist"
            diff.notes = "Observed in read-only mode; assist mode would allow low-risk actions."

        # Risk/decision-based approval recommendation
        if decision_status == "needs_approval" or intent_risk == "high":
            diff.require_approval = True
            if not diff.notes:
                diff.notes = "Action requires human approval (per policy and/or risk level)."

        # Blacklist cleanup
        for cap in capabilities:
            if cap in denied_caps and cap not in diff.blacklist_remove:
                diff.blacklist_remove.append(cap)

        # Whitelist enablement
        if whitelist_mode:
            for cap in capabilities:
                if cap not in whitelisted and cap not in diff.whitelist_add:
                    diff.whitelist_add.append(cap)
            if not diff.notes:
                diff.notes = "Whitelist mode: add required capabilities to allow."

        return diff
