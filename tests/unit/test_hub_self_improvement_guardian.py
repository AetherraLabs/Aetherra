from Aetherra.guardian import ContainmentAction, IntentDeclaration
from Aetherra.guardian.approval import resolve_approval
from Aetherra.guardian.containment import clear_containment, record_containment
from aetherra_hub.app import create_app


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    return create_app().test_client()


def test_self_improvement_apply_requires_guardian_approval_without_rollback(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/selfimprove/apply",
        json={
            "proposal_id": "SI-GUARD-1",
            "method": "hmr",
            "hmr_target": "kernel",
            "hmr_source": "Aetherra.kernel.patch",
        },
        headers={
            "Authorization": "Bearer control-secret",
            "X-Aetherra-Principal": "self_improvement_engine",
        },
    )

    payload = response.get_json()
    assert response.status_code == 202
    assert payload["ok"] is False
    assert payload["applied"] is False
    assert payload["error"] == "rollback_required"
    assert payload["guardian"]["status"] == "require_approval"


def test_self_improvement_apply_with_rollback_reaches_existing_manual_path(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/selfimprove/apply",
        json={
            "proposal_id": "SI-GUARD-2",
            "method": "auto",
            "description": "Document-only improvement",
            "reversible": True,
            "rollback_plan": "git diff restore docs",
        },
        headers={
            "Authorization": "Bearer control-secret",
            "X-Aetherra-Principal": "self_improvement_engine",
        },
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["applied"] is False
    assert payload["method"] == "manual"


def test_self_improvement_apply_consumes_guardian_approval(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    proposal = {
        "proposal_id": "SI-GUARD-3",
        "method": "hmr",
        "hmr_target": "kernel",
        "hmr_source": "Aetherra.kernel.patch",
    }
    headers = {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "self_improvement_engine",
    }

    first = client.post("/api/selfimprove/apply", json=proposal, headers=headers)
    first_payload = first.get_json()
    approval_id = first_payload["guardian"]["details"]["approval_request_id"]
    resolve_approval(approval_id, approved=True, approver="user")

    second = client.post(
        "/api/selfimprove/apply",
        json={**proposal, "guardian_approval_id": approval_id},
        headers=headers,
    )
    replay = client.post(
        "/api/selfimprove/apply",
        json={**proposal, "guardian_approval_id": approval_id},
        headers=headers,
    )

    second_payload = second.get_json()
    replay_payload = replay.get_json()
    assert second.status_code == 200
    assert second_payload["ok"] is True
    assert second_payload["restart_required"] is True
    assert replay.status_code == 202
    assert replay_payload["guardian"]["status"] == "require_approval"


def test_self_improvement_subsystem_containment_blocks_until_cleared(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)
    contained_intent = IntentDeclaration(
        requester="guardian",
        subsystem="self_improvement",
        action="self.apply_proposal",
        target="*",
        purpose="Pause self-improvement subsystem",
        capabilities=("self:modify",),
        evidence=("guardian:test",),
    )
    containment = record_containment(
        contained_intent,
        ContainmentAction.ISOLATE_SUBSYSTEM,
        reason="test_pause",
    )
    proposal = {
        "proposal_id": "SI-CONTAINED",
        "method": "auto",
        "description": "Document-only improvement",
        "reversible": True,
        "rollback_plan": "git diff restore docs",
    }
    headers = {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "self_improvement_engine",
    }

    blocked = client.post("/api/selfimprove/apply", json=proposal, headers=headers)
    clear_containment(
        containment.containment_id,
        cleared_by="guardian",
        reason="test_clear",
    )
    allowed = client.post("/api/selfimprove/apply", json=proposal, headers=headers)

    blocked_payload = blocked.get_json()
    allowed_payload = allowed.get_json()
    assert blocked.status_code == 403
    assert blocked_payload["error"] == "active_containment"
    assert allowed.status_code == 200
    assert allowed_payload["method"] == "manual"
