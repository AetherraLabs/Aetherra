# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Actuator - World-Changing Action Executor
==========================================

The ONLY component that can modify the outside world.
All actions are gated, logged, reversible, and auditable.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .capability_registry import CapabilityRegistry
    from .policy_engine import PolicyEngine

from Aetherra.consciousness.core.types import LedgerEntry, Plan


class Actuator:
    """Execute plans with safety guarantees.

    This is the effector organ—the only way consciousness can change
    the world. Every action carries a rollback plan and audit trail.
    """

    def __init__(self, registry: CapabilityRegistry, policy: PolicyEngine):
        """Initialize actuator.

        Args:
            registry: Capability registry
            policy: Policy engine for permissions
        """
        self.registry = registry
        self.policy = policy
        self.ledger_history: list[LedgerEntry] = []
        self.total_actions: int = 0
        self.total_successes: int = 0
        self.total_failures: int = 0
        self.total_rollbacks: int = 0

    def execute(self, plan: Plan, context: dict | None = None) -> LedgerEntry:
        """Execute a plan with safety envelope.

        Args:
            plan: Executable plan with intent, steps, rollback
            context: Optional execution context

        Returns:
            LedgerEntry with execution outcome and audit trail
        """
        # Create ledger entry
        ledger = LedgerEntry(
            intent=plan.intent,
            plan=plan,
            policy_decision="pending",
            actions=[],
        )

        # Policy check
        cap_names = [s.capability for s in plan.steps]
        decision = self.policy.evaluate(plan.intent.risk, cap_names, context)
        ledger.policy_decision = decision.status

        if decision.status == "denied":
            ledger.success = False
            ledger.notes = decision.reason
            self.total_actions += 1
            self.total_failures += 1
            self._append_ledger(ledger)
            return ledger

        if decision.status == "needs_approval":
            ledger.success = False
            ledger.notes = f"Awaiting approval: {decision.reason}"
            self.policy.request_approval(plan.intent.goal)
            self.total_actions += 1
            self._append_ledger(ledger)
            return ledger

        # Execute with rollback guarantee
        try:
            for step in plan.steps:
                cap = self.registry.get(step.capability)
                if not cap:
                    raise RuntimeError(f"Unknown capability: {step.capability}")

                # Precondition check
                if not cap.precondition(step.args):
                    raise RuntimeError(f"Precondition failed: {step.capability}")

                # Execute action
                start_time = time.time()
                result = cap.action(step.args)
                duration = time.time() - start_time

                # Verify success
                verified = cap.verify(step.args)

                ledger.actions.append(
                    {
                        "step_id": step.id,
                        "capability": cap.name,
                        "args": step.args,
                        "result": result,
                        "verified": verified,
                        "duration_s": round(duration, 3),
                    }
                )

                if not verified:
                    raise RuntimeError(f"Verification failed: {cap.name} (result: {result})")

            # All steps succeeded
            ledger.success = True
            ledger.notes = "All steps completed and verified"
            self.total_actions += 1
            self.total_successes += 1

        except Exception as e:
            # Rollback on failure
            ledger.success = False
            ledger.notes = f"Failed: {e}. Attempting rollback..."
            self.total_actions += 1
            self.total_failures += 1

            rollback_results = self._rollback(plan)
            ledger.notes += f" Rollback: {rollback_results}"

        self._append_ledger(ledger)
        return ledger

    def _rollback(self, plan: Plan) -> str:
        """Execute rollback steps (best-effort).

        Args:
            plan: Plan with rollback steps

        Returns:
            Rollback summary message
        """
        self.total_rollbacks += 1
        rollback_count = 0
        rollback_errors = []

        for step in reversed(plan.rollback):
            cap = self.registry.get(step.capability)
            if not cap:
                rollback_errors.append(f"Unknown cap: {step.capability}")
                continue

            try:
                cap.rollback(step.args)
                rollback_count += 1
            except Exception as e:
                rollback_errors.append(f"{step.capability}: {e}")

        if rollback_errors:
            return (
                f"Partial rollback ({rollback_count} steps); errors: {'; '.join(rollback_errors)}"
            )
        return f"Complete rollback ({rollback_count} steps)"

    def _append_ledger(self, ledger: LedgerEntry) -> None:
        """Append to audit ledger (with size limit)."""
        self.ledger_history.append(ledger)
        if len(self.ledger_history) > 10000:
            # Keep recent 5000 entries
            self.ledger_history = self.ledger_history[-5000:]

    def get_recent_ledger(self, count: int = 10) -> list[LedgerEntry]:
        """Get recent ledger entries.

        Args:
            count: Number of recent entries to return

        Returns:
            List of recent ledger entries
        """
        return self.ledger_history[-count:]

    def get_stats(self) -> dict:
        """Get actuator statistics."""
        success_rate = (
            (self.total_successes / self.total_actions * 100) if self.total_actions > 0 else 0.0
        )

        return {
            "total_actions": self.total_actions,
            "total_successes": self.total_successes,
            "total_failures": self.total_failures,
            "total_rollbacks": self.total_rollbacks,
            "success_rate_pct": round(success_rate, 2),
            "ledger_size": len(self.ledger_history),
        }
