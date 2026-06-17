from Aetherra.guardian import (
    ContainmentAction,
    GuardianStatus,
    IntentDeclaration,
    evaluate_intent,
)
from Aetherra.guardian.containment import (
    clear_containment,
    containment_status,
    list_containment_statuses,
    record_containment,
)


def _intent(**overrides):
    values = {
        "requester": "plugin:demo",
        "subsystem": "plugin_manager",
        "action": "plugin.execute",
        "target": "demo",
        "purpose": "Execute plugin",
        "capabilities": ("execute",),
        "evidence": ("plugin:demo",),
    }
    values.update(overrides)
    return IntentDeclaration(**values)


def test_active_containment_blocks_matching_intent(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    containment = record_containment(
        intent,
        ContainmentAction.BLOCK_ACTION,
        reason="test_containment",
    )

    decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.CONTAIN
    assert decision.reason == "active_containment"
    assert decision.details["containment_id"] == containment.containment_id


def test_cleared_containment_no_longer_blocks(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    containment = record_containment(
        intent,
        ContainmentAction.BLOCK_ACTION,
        reason="test_containment",
    )
    clear_containment(containment.containment_id, cleared_by="guardian", reason="test_clear")

    decision = evaluate_intent(
        intent,
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.ALLOW_LIMITED
    assert containment_status(containment.containment_id)["state"] == "cleared"
    assert list_containment_statuses()[0]["state"] == "cleared"


def test_clear_containment_handles_missing_and_repeat(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    intent = _intent()
    containment = record_containment(
        intent,
        ContainmentAction.BLOCK_ACTION,
        reason="test_containment",
    )

    missing = clear_containment("cnt_missing", cleared_by="guardian", reason="test")
    first = clear_containment(containment.containment_id, cleared_by="guardian", reason="test")
    second = clear_containment(containment.containment_id, cleared_by="guardian", reason="test")

    assert missing["state"] == "not_found"
    assert first["state"] == "cleared"
    assert second["state"] == "already_cleared"


def test_subsystem_wildcard_containment_blocks_different_targets(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    record_containment(
        _intent(subsystem="self_improvement", target="*"),
        ContainmentAction.ISOLATE_SUBSYSTEM,
        reason="pause_self_improvement",
    )
    proposal_intent = IntentDeclaration(
        requester="self_improvement_engine",
        subsystem="self_improvement",
        action="self.apply_proposal",
        target="SI-NEW",
        purpose="Apply proposal",
        capabilities=("self:modify",),
        evidence=("proposal:SI-NEW",),
    )

    decision = evaluate_intent(
        proposal_intent,
        capability_checker=lambda requester, capability: True,
    )

    assert decision.status == GuardianStatus.CONTAIN
    assert decision.reason == "active_containment"
