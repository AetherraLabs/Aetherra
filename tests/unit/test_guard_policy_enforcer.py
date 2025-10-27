import os
import time

from Aetherra.homeostasis.guard_policy_enforcer import GuardPolicyEnforcer


def test_guard_policy_integration_velocity_threshold(monkeypatch):
    # Set very low threshold to exercise quickly
    monkeypatch.setenv("AETHERRA_GUARD_INTEGRATION_PER_HOUR", "3")
    enforcer = GuardPolicyEnforcer(policy_path=None)

    proposal = {"proposal_id": "p1", "type": "optimize", "params": {}}

    # First three should pass pre-check, then record accept
    ok, violations = enforcer.check_proposal(proposal)
    assert ok
    assert not violations
    enforcer.record_accept(proposal)

    ok, violations = enforcer.check_proposal(proposal)
    assert ok
    assert not violations
    enforcer.record_accept(proposal)

    ok, violations = enforcer.check_proposal(proposal)
    assert ok
    assert not violations
    enforcer.record_accept(proposal)

    # Fourth violates integration_velocity
    ok, violations = enforcer.check_proposal(proposal)
    assert not ok
    assert "integration_velocity" in violations[0]


def test_guard_policy_actuator_frequency(monkeypatch):
    monkeypatch.setenv("AETHERRA_GUARD_ACTUATIONS_PER_COMPONENT_PER_MIN", "1")
    enforcer = GuardPolicyEnforcer(policy_path=None)

    proposal = {
        "proposal_id": "p2",
        "type": "optimize",
        "params": {
            "integration_plan": {
                "actions": [
                    {"component": "compA", "op": "adjust"},
                ]
            }
        },
    }

    ok, violations = enforcer.check_proposal(proposal)
    assert ok
    enforcer.record_accept(proposal)

    # Second action on same component within a minute should be flagged
    proposal2 = {
        "proposal_id": "p3",
        "type": "optimize",
        "params": {
            "integration_plan": {
                "actions": [
                    {"component": "compA", "op": "adjust"},
                ]
            }
        },
    }
    ok, violations = enforcer.check_proposal(proposal2)
    assert not ok
    assert any(v.startswith("actuator_frequency:") for v in violations)


def test_guard_policy_rollback_cascade(monkeypatch):
    monkeypatch.setenv("AETHERRA_GUARD_ROLLBACKS_PER_HOUR", "2")
    enforcer = GuardPolicyEnforcer(policy_path=None)

    rollback_proposal = {"proposal_id": "r1", "type": "rollback", "params": {}}

    # Two rollbacks ok
    ok, violations = enforcer.check_proposal(rollback_proposal)
    assert ok
    enforcer.record_rollback()

    ok, violations = enforcer.check_proposal(rollback_proposal)
    assert ok
    enforcer.record_rollback()

    # Third should violate
    ok, violations = enforcer.check_proposal(rollback_proposal)
    assert not ok
    assert "rollback_cascade" in violations
