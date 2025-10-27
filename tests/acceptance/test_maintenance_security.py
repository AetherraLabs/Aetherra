import asyncio
import os

from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


async def _start_selfinc():
    cfg = SelfIncorporationConfig()
    svc = SelfIncorporationService(cfg)
    await svc.start()
    return svc


def test_guard_policies_integration_velocity_accept_then_reject(monkeypatch):
    # Ensure permissive mode for auth; we're testing guard enforcement
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    # Set low threshold for the test
    monkeypatch.setenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "2")

    svc = asyncio.run(_start_selfinc())

    # Three optimize proposals
    p = {"type": "optimize", "params": {"hint": "x", "value": True}}

    r1 = asyncio.run(svc.handle_message("selfimprovement.proposal", p))
    r2 = asyncio.run(svc.handle_message("selfimprovement.proposal", p))
    r3 = asyncio.run(svc.handle_message("selfimprovement.proposal", p))

    # First two accepted, third rejected by guard policy
    assert r1.get("status") == "accepted"
    assert r2.get("status") == "accepted"
    assert r3.get("status") == "rejected"
    assert r3.get("reason", "").startswith("guard_violation:integration_velocity")


def test_guard_policies_actuator_frequency_rejects_second_action(monkeypatch):
    # Ensure permissive mode for auth; we're testing guard enforcement
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.setenv("AETHERRA_GUARD_ACTUATIONS_PER_COMPONENT_PER_MIN", "1")

    svc = asyncio.run(_start_selfinc())

    # First proposal with an action on component A
    p1 = {
        "type": "optimize",
        "params": {
            "integration_plan": {"actions": [{"component": "compA", "op": "tune"}]}
        },
    }
    r1 = asyncio.run(svc.handle_message("selfimprovement.proposal", p1))
    assert r1.get("status") == "accepted"

    # Second proposal on same component within the window should be rejected
    p2 = {
        "type": "optimize",
        "params": {
            "integration_plan": {"actions": [{"component": "compA", "op": "tune"}]}
        },
    }
    r2 = asyncio.run(svc.handle_message("selfimprovement.proposal", p2))
    assert r2.get("status") == "rejected"
    assert r2.get("reason", "").startswith("guard_violation:actuator_frequency:")


def test_guard_policies_rollback_cascade_rejects_third(monkeypatch):
    # Ensure permissive mode; set low rollback threshold
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.setenv("AETHERRA_GUARD_ROLLBACKS_PER_HOUR", "2")

    svc = asyncio.run(_start_selfinc())

    # Create three fake rollback tokens with proper prefix
    rb1, rb2, rb3 = "rb_1", "rb_2", "rb_3"

    # Provide a stub HMR controller via service registry
    class _StubInfo:
        def __init__(self, instance):
            self.instance = instance

    class _StubRegistry:
        def get_service_info(self, name: str):
            if name == "hmr_controller":
                return _StubInfo(object())
            return None

    svc.service_registry = _StubRegistry()

    # Append audit entries to make tokens discoverable
    svc.audit_ledger.append(
        plan_id="p1",
        action="proposal:optimize",
        status="applied",
        target={"a": 1},
        result={"rollback_token": rb1},
        trace_id="t1",
        ethics_overall=None,
        risk_level="low",
    )
    svc.audit_ledger.append(
        plan_id="p2",
        action="proposal:optimize",
        status="applied",
        target={"a": 2},
        result={"rollback_token": rb2},
        trace_id="t2",
        ethics_overall=None,
        risk_level="low",
    )
    svc.audit_ledger.append(
        plan_id="p3",
        action="proposal:optimize",
        status="applied",
        target={"a": 3},
        result={"rollback_token": rb3},
        trace_id="t3",
        ethics_overall=None,
        risk_level="low",
    )

    # First two rollbacks allowed
    r1 = asyncio.run(svc.trigger_rollback(rb1))
    r2 = asyncio.run(svc.trigger_rollback(rb2))
    assert r1.get("ok") is True
    assert r2.get("ok") is True

    # Third rollback should be rejected by guard policy
    r3 = asyncio.run(svc.trigger_rollback(rb3))
    assert r3.get("ok") is False
    assert r3.get("error", "").startswith("guard_violation:rollback_cascade")
