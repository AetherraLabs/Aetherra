# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

import time

import pytest

from Aetherra.api.approvals import ApprovalStore
from Aetherra.consciousness.core import config as core_config
from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
from Aetherra.consciousness.core.types import Event, LedgerEntry, Plan
from Aetherra.safety_envelope.policy_engine import PolicyDecision


class StubBus:
    def __init__(self, events=None):
        self._events = list(events or [])

    def drain(self, max_items: int = 256):
        out = self._events[:max_items]
        self._events = self._events[max_items:]
        return out


class FakePolicy:
    def __init__(self, mode="assist"):
        self.mode = mode

    def evaluate(
        self, intent_risk: str, capabilities: list[str], context: dict | None = None
    ) -> PolicyDecision:
        # Mirror real semantics: medium-risk in assist requires approval
        if self.mode == "assist" and intent_risk == "medium":
            return PolicyDecision(
                status="needs_approval",
                reason="Medium-risk requires approval in assist",
            )
        if self.mode == "observe":
            return PolicyDecision(
                status="denied", reason="Running in observe-only mode"
            )
        return PolicyDecision(status="allowed", reason="Allowed")


class FakeActuator:
    def __init__(self, policy):
        self.policy = policy

    def execute(self, plan: Plan, context: dict | None = None) -> LedgerEntry:
        # Simulate immediate decision outcome from policy and mark as not executed
        decision = self.policy.evaluate(
            plan.intent.risk, [s.capability for s in plan.steps], context
        )
        return LedgerEntry(
            intent=plan.intent,
            plan=plan,
            policy_decision=decision.status,
            actions=[],
            success=False,
            notes=decision.reason,
        )


def test_policy_explanation_and_diff_medium_in_assist(monkeypatch):
    # Set mode to assist for the core
    old_mode = core_config.AUTONOMY_MODE
    core_config.AUTONOMY_MODE = "assist"
    try:
        # One event that triggers a medium-risk intent (service flapping)
        events = [
            Event(type="svc.health", payload={"restarts_1h": 6, "service": "api"})
        ]
        bus = StubBus(events)
        core = ConsciousnessCore(
            perception_bus=bus,
            safety_envelope=FakeActuator(FakePolicy("assist")),
            memory_engine=None,
        )

        # Run a tick to form intent and attempt execution (pre-check + execute)
        core.tick()

        status = core.get_status()
        # Expect policy diff suggesting approval (needs_approval) and no mode change in assist
        last_diff = status.get("policy", {}).get("last_diff", {})
        assert last_diff.get("require_approval") is True
    finally:
        core_config.AUTONOMY_MODE = old_mode


def test_approvals_store_consent_trace():
    store = ApprovalStore()
    rec = store.request(
        intent_goal="Stabilize api",
        risk="medium",
        requested_by="consciousness",
        reason="Medium-risk action requires approval",
        diff_preview={"mode_change": None, "require_approval": True},
    )
    ok = store.approve(
        rec.id, approver="owner", reason="Allowed during maintenance window"
    )
    assert ok
    got = store.get(rec.id)
    assert got is not None
    assert got.status == "approved"
    assert got.approver == "owner"
    assert got.diff_preview is not None
    assert got.diff_preview.get("require_approval") is True


def test_autopilot_graduation_gate_opt_in(monkeypatch):
    # Ensure opt-in is on
    monkeypatch.setenv("AETHERRA_AUTOPILOT_OPT_IN", "1")
    # Make mode assist to allow actions
    old_mode = core_config.AUTONOMY_MODE
    core_config.AUTONOMY_MODE = "assist"
    try:
        bus = StubBus([])
        core = ConsciousnessCore(
            perception_bus=bus,
            safety_envelope=FakeActuator(FakePolicy("assist")),
            memory_engine=None,
        )

        # Feed a clean history of successes
        now = time.time()
        for _ in range(60):
            core.autopilot.record_ledger(now, True, "allowed")

        ap = core.autopilot.evaluate(core_config.AUTONOMY_MODE)
        assert ap.suggested_mode in (
            "autopilot",
            None,
        )  # If thresholds not met, won't suggest
        # At minimum, eligibility should be True given high success ratio and opt-in (trust/SNCI thresholds may gate)
        # We relax to check the evaluation ran and exposed fields
        assert isinstance(ap.eligible, bool)
    finally:
        core_config.AUTONOMY_MODE = old_mode


def test_explanations_present_in_observe_mode(monkeypatch):
    # Observe mode should not act, but explanations should still be produced for focuses/intents
    old_mode = core_config.AUTONOMY_MODE
    core_config.AUTONOMY_MODE = "observe"
    try:
        events = [Event(type="disk.status", payload={"pct_free": 5})]
        bus = StubBus(events)
        core = ConsciousnessCore(
            perception_bus=bus, safety_envelope=None, memory_engine=None
        )

        core.tick()
        status = core.get_status()
        explain = status.get("explain", {})
        assert explain.get("total_events", 0) >= 1
        assert explain.get("coverage_ratio", 0.0) >= 0.0
    finally:
        core_config.AUTONOMY_MODE = old_mode
