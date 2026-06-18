from Aetherra.guardian import ContainmentAction, IntentDeclaration
from Aetherra.guardian.approval import resolve_approval
from Aetherra.guardian.containment import clear_containment, record_containment
from aetherra_hub.app import create_app
from aetherra_hub.blueprints import self_improvement


class _FakeSelfImprovementService:
    async def handle_message(self, message_type, data):
        if message_type == "selfimprovement.status":
            return {
                "improvement_active": True,
                "total_proposals": 1,
                "autonomous_implementation_enabled": False,
            }
        if message_type == "selfimprovement.proposals":
            return {
                "status": "ok",
                "proposals": [
                    {
                        "proposal_id": "SI-OBSERVE-1",
                        "status": "active",
                        "risk_level": 0.1,
                    }
                ],
            }
        if message_type == "selfimprovement.trends":
            return {"response_time": {"trend_direction": "degrading"}}
        return {"error": "unknown_message"}


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


def test_self_improvement_read_only_status_proposals_and_trends(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setattr(
        self_improvement,
        "_get_self_improvement_service",
        lambda: _FakeSelfImprovementService(),
    )

    status = client.get("/api/selfimprove/status")
    proposals = client.get("/api/selfimprove/proposals")
    trends = client.get("/api/selfimprove/trends")

    status_payload = status.get_json()
    proposals_payload = proposals.get_json()
    trends_payload = trends.get_json()
    assert status.status_code == 200
    assert status_payload["autonomous_implementation_enabled"] is False
    assert proposals.status_code == 200
    assert proposals_payload["proposals"][0]["proposal_id"] == "SI-OBSERVE-1"
    assert trends.status_code == 200
    assert trends_payload["trends"]["response_time"]["trend_direction"] == "degrading"


def test_self_improvement_batch_apply_accepts_documented_proposal_ids(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/selfimprove/batch-apply",
        json={
            "proposal_ids": ["SI-BATCH-1"],
            "method": "auto",
            "reversible": True,
            "rollback_plan": "manual restore",
        },
        headers={
            "Authorization": "Bearer control-secret",
            "X-Aetherra-Principal": "self_improvement_engine",
        },
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["ok"] is True
    assert payload["total"] == 1
    assert payload["results"][0]["proposal_id"] == "SI-BATCH-1"
