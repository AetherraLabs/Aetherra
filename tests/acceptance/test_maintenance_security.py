# Standard library imports
import asyncio

# Third party imports
import pytest

# Aetherra imports
from aetherra_self_incorporation import (
    FileItem,
    ItemType,
    SafetyDecision,
    SelfIncorporationConfig,
    SelfIncorporationService,
    TrustTier,
)


@pytest.fixture(autouse=True)
def isolated_selfinc_environment(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")


async def _start_selfinc():
    cfg = SelfIncorporationConfig()
    svc = SelfIncorporationService(cfg)
    await svc.start()
    return svc


def _workflow_action(svc, name, component):
    svc.code_index.store_file(
        FileItem(
            id=name,
            path=f"workflows/{name}.aether",
            hash="test-workflow-hash",
            size=10,
            mtime=1.0,
            type=ItemType.WORKFLOW,
            language="aether",
        )
    )
    # The integration fixture has already passed signature and capability checks.
    svc.safety_index.store_decision(
        SafetyDecision(
            file_id=name,
            verified=True,
            signing={"ok": True},
            capability_ok=True,
            trust_tier=TrustTier.VERIFIED,
        )
    )
    return {
        "action": "register_workflow",
        "component": component,
        "target": {"file_id": name},
        "deps": [],
    }


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
            "integration_plan": {
                "actions": [_workflow_action(svc, "first_workflow", "compA")]
            }
        },
    }
    r1 = asyncio.run(svc.handle_message("selfimprovement.proposal", p1))
    assert r1.get("status") == "accepted"
    assert r1["details"]["integration"]["applied"] == 1
    assert "first_workflow" in svc._workflows

    # Second proposal on same component within the window should be rejected
    p2 = {
        "type": "optimize",
        "params": {
            "integration_plan": {
                "actions": [_workflow_action(svc, "second_workflow", "compA")]
            }
        },
    }
    r2 = asyncio.run(svc.handle_message("selfimprovement.proposal", p2))
    assert r2.get("status") == "rejected"
    assert r2.get("reason", "").startswith("guard_violation:actuator_frequency:")
    assert "second_workflow" not in svc._workflows


def test_guard_policies_rollback_cascade_rejects_third(monkeypatch):
    # Ensure permissive mode; set low rollback threshold
    monkeypatch.delenv("AETHERRA_PROFILE", raising=False)
    monkeypatch.setenv("AETHERRA_GUARD_ROLLBACKS_PER_HOUR", "2")

    svc = asyncio.run(_start_selfinc())

    # Register real workflows to produce supported audit records and rollback tokens.
    plan = {
        "plan_id": "rollback-guard-plan",
        "status": "ready",
        "actions": [
            _workflow_action(svc, "rollback_one", "compA"),
            _workflow_action(svc, "rollback_two", "compB"),
            _workflow_action(svc, "rollback_three", "compC"),
        ],
    }
    applied = asyncio.run(svc.core_integrator.execute_plan(plan, dry_run=False))
    assert applied["ok"] is True
    assert applied["applied"] == 3
    rb1, rb2, rb3 = [result["rollback_token"] for result in applied["results"]]

    # First two rollbacks allowed
    r1 = asyncio.run(svc.trigger_rollback(rb1))
    r2 = asyncio.run(svc.trigger_rollback(rb2))
    assert r1.get("ok") is True
    assert r2.get("ok") is True
    assert "rollback_one" not in svc._workflows
    assert "rollback_two" not in svc._workflows

    # Third rollback should be rejected by guard policy
    r3 = asyncio.run(svc.trigger_rollback(rb3))
    assert r3.get("ok") is False
    assert r3.get("error", "").startswith("guard_violation:rollback_cascade")
    assert "rollback_three" in svc._workflows
