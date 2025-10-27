# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Policy Engine
=============

Decision engine for action permissions based on risk, mode, and constraints.
This is the gatekeeper—consciousness can want, but policy decides if it may.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class PolicyDecision:
    """Policy decision for an action request."""

    status: str  # allowed | denied | needs_approval
    reason: str
    conditions: List[str] | None = None  # Additional conditions if allowed


class PolicyEngine:
    """Policy-based action permission system.

    Modes:
    - observe: no actions allowed (awareness only)
    - assist: low-risk auto, medium-risk approval, high-risk blocked
    - autopilot: low/medium-risk auto (within envelope), high-risk approval
    - emergency: constrained actions for homeostasis, then fallback
    """

    def __init__(self, mode: str = "observe"):
        """Initialize policy engine.

        Args:
            mode: Autonomy mode (observe|assist|autopilot|emergency)
        """
        self.mode = mode
        self.human_approval_required: List[str] = []  # Intent goals awaiting approval
        self.denied_capabilities: List[str] = []  # Blacklisted capabilities
        self.allowed_capabilities: List[str] = []  # Whitelisted (if using whitelist mode)
        self.use_whitelist: bool = False

    def evaluate(
        self, intent_risk: str, capabilities: List[str], context: dict | None = None
    ) -> PolicyDecision:
        """Evaluate whether an action is permitted.

        Args:
            intent_risk: Risk level (low|medium|high)
            capabilities: List of capability names in the plan
            context: Optional context (time, user, resources, etc.)

        Returns:
            PolicyDecision with status and reason
        """
        # Mode-based decisions
        if self.mode == "observe":
            return PolicyDecision(
                status="denied", reason="Running in observe-only mode (awareness, no actions)"
            )

        # Blacklist check
        for cap in capabilities:
            if cap in self.denied_capabilities:
                return PolicyDecision(status="denied", reason=f"Capability {cap} is blacklisted")

        # Whitelist check (if enabled)
        if self.use_whitelist:
            for cap in capabilities:
                if cap not in self.allowed_capabilities:
                    return PolicyDecision(
                        status="denied", reason=f"Capability {cap} not in whitelist"
                    )

        # Risk-based decisions
        if intent_risk == "high":
            # High-risk always requires approval
            return PolicyDecision(
                status="needs_approval",
                reason="High-risk action requires human approval",
            )

        if intent_risk == "medium":
            if self.mode == "assist":
                return PolicyDecision(
                    status="needs_approval",
                    reason="Medium-risk action requires approval in assist mode",
                )
            elif self.mode == "autopilot":
                # Autopilot can handle medium-risk within constraints
                return PolicyDecision(
                    status="allowed",
                    reason="Medium-risk allowed in autopilot mode",
                    conditions=["rollback_required", "audit_required"],
                )

        if intent_risk == "low" and self.mode in ("assist", "autopilot", "emergency"):
            return PolicyDecision(
                status="allowed",
                reason=f"Low-risk action allowed in {self.mode} mode",
                conditions=["audit_required"],
            )

        # Emergency mode: homeostasis actions only
        if self.mode == "emergency" and context and context.get("homeostasis_critical"):
            return PolicyDecision(
                status="allowed",
                reason="Emergency homeostasis action",
                conditions=["fallback_to_assist_after"],
            )

        # Default: deny if no rule matched
        return PolicyDecision(
            status="denied",
            reason=f"No policy rule matched for risk={intent_risk}, mode={self.mode}",
        )

    def set_mode(self, mode: str) -> None:
        """Change autonomy mode.

        Args:
            mode: New mode (observe|assist|autopilot|emergency)
        """
        valid_modes = {"observe", "assist", "autopilot", "emergency"}
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")
        self.mode = mode

    def blacklist_capability(self, cap_name: str) -> None:
        """Blacklist a capability (permanently deny)."""
        if cap_name not in self.denied_capabilities:
            self.denied_capabilities.append(cap_name)

    def whitelist_capability(self, cap_name: str) -> None:
        """Whitelist a capability (required if using whitelist mode)."""
        if cap_name not in self.allowed_capabilities:
            self.allowed_capabilities.append(cap_name)

    def enable_whitelist_mode(self, enabled: bool = True) -> None:
        """Enable/disable whitelist mode (default: blacklist)."""
        self.use_whitelist = enabled

    def request_approval(self, intent_goal: str) -> None:
        """Mark an intent as awaiting human approval."""
        if intent_goal not in self.human_approval_required:
            self.human_approval_required.append(intent_goal)

    def grant_approval(self, intent_goal: str) -> bool:
        """Grant approval for a pending intent.

        Returns:
            True if intent was in approval queue, False otherwise
        """
        if intent_goal in self.human_approval_required:
            self.human_approval_required.remove(intent_goal)
            return True
        return False

    def get_status(self) -> dict:
        """Get current policy engine status."""
        return {
            "mode": self.mode,
            "use_whitelist": self.use_whitelist,
            "blacklisted_count": len(self.denied_capabilities),
            "whitelisted_count": len(self.allowed_capabilities),
            "pending_approvals": len(self.human_approval_required),
        }
