from Aetherra.guardian import GuardianMode, IntentDeclaration
from Aetherra.guardian.approval import create_approval_request
from Aetherra.guardian.containment import record_containment
from Aetherra.guardian.models import ContainmentAction
from Aetherra.guardian.preauthorization import create_preauthorization
from Aetherra.guardian.risk import assess_risk
from Aetherra.guardian.tiers import classify_decision_tier
from aetherra_hub.app import create_app


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    return create_app().test_client()


def _approval():
    intent = IntentDeclaration(
        requester="self_improvement_engine",
        subsystem="self_improvement",
        action="self.apply_proposal",
        target="kernel",
        purpose="Apply proposal",
        capabilities=("self:modify",),
        evidence=("proposal:SI-API",),
    )
    return create_approval_request(intent, assess_risk(intent))


def _preauthorization():
    intent = IntentDeclaration(
        requester="lyrixa",
        subsystem="status",
        action="status.message_publish",
        target="local_status_channel",
        purpose="Publish bounded local status update",
        reversible=True,
        rollback_plan="publish corrected status",
    )
    risk = assess_risk(intent)
    return create_preauthorization(
        intent,
        risk,
        decision_tier=classify_decision_tier(intent, risk),
        guardian_mode=GuardianMode.STRICT,
    )


def test_guardian_approvals_api_requires_control_token(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/guardian/approvals")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_guardian_status_requires_control_token(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.get("/api/guardian/status")

    assert response.status_code == 401
    assert response.get_json()["error"] == "unauthorized"


def test_guardian_status_summarizes_operational_state(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "strict")
    client = _client(monkeypatch, tmp_path)
    _approval()
    _preauthorization()
    intent = IntentDeclaration(
        requester="self_improvement_engine",
        subsystem="self_improvement",
        action="self.apply_proposal",
        target="*",
        purpose="Isolate proposal application",
        capabilities=("self:modify",),
        evidence=("guardian:test",),
    )
    record_containment(
        intent,
        ContainmentAction.ISOLATE_SUBSYSTEM,
        reason="test_containment",
    )

    response = client.get(
        "/api/guardian/status",
        headers={"Authorization": "Bearer control-secret"},
    )

    assert response.status_code == 200
    payload = response.get_json()["guardian"]
    assert payload["enabled"] is True
    assert payload["mode"] == "strict"
    assert payload["approvals"] == {"total": 1, "pending": 1}
    assert payload["containment"] == {"total": 1, "active": 1}
    assert payload["preauthorizations"] == {"total": 1, "active": 1}


def test_guardian_approvals_api_lists_and_resolves(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    approval = _approval()
    headers = {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "guardian-admin",
    }

    listed = client.get("/api/guardian/approvals", headers=headers)
    resolved = client.post(
        f"/api/guardian/approvals/{approval.request_id}/resolve",
        json={"approved": True},
        headers=headers,
    )
    fetched = client.get(
        f"/api/guardian/approvals/{approval.request_id}",
        headers=headers,
    )

    assert listed.status_code == 200
    assert listed.get_json()["total"] == 1
    assert resolved.status_code == 200
    assert resolved.get_json()["approval"]["state"] == "approved"
    assert fetched.status_code == 200
    assert fetched.get_json()["approval"]["state"] == "approved"


def test_guardian_approval_resolve_validates_payload(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    approval = _approval()

    response = client.post(
        f"/api/guardian/approvals/{approval.request_id}/resolve",
        json={"approved": "yes"},
        headers={"Authorization": "Bearer control-secret"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "approved boolean required"


def test_guardian_containment_api_lists_and_clears(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    intent = IntentDeclaration(
        requester="plugin:demo",
        subsystem="plugin_manager",
        action="plugin.execute",
        target="demo",
        purpose="Execute plugin",
        capabilities=("execute",),
        evidence=("plugin:demo",),
    )
    containment = record_containment(
        intent,
        ContainmentAction.BLOCK_ACTION,
        reason="test_containment",
    )
    headers = {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "guardian-admin",
    }

    listed = client.get("/api/guardian/containment", headers=headers)
    fetched = client.get(
        f"/api/guardian/containment/{containment.containment_id}",
        headers=headers,
    )
    cleared = client.post(
        f"/api/guardian/containment/{containment.containment_id}/clear",
        json={"reason": "manual_recovery"},
        headers=headers,
    )
    fetched_after = client.get(
        f"/api/guardian/containment/{containment.containment_id}",
        headers=headers,
    )

    assert listed.status_code == 200
    assert listed.get_json()["total"] == 1
    assert fetched.status_code == 200
    assert fetched.get_json()["containment"]["state"] == "active"
    assert cleared.status_code == 200
    assert cleared.get_json()["containment"]["state"] == "cleared"
    assert fetched_after.get_json()["containment"]["state"] == "cleared"


def test_guardian_containment_clear_requires_reason(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/guardian/containment/cnt_missing/clear",
        json={},
        headers={"Authorization": "Bearer control-secret"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "reason required"


def test_guardian_preauthorization_api_lists_and_fetches(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)
    grant = _preauthorization()
    headers = {"Authorization": "Bearer control-secret"}

    listed = client.get("/api/guardian/preauthorizations", headers=headers)
    fetched = client.get(
        f"/api/guardian/preauthorizations/{grant.grant_id}",
        headers=headers,
    )
    missing = client.get("/api/guardian/preauthorizations/pag_missing", headers=headers)

    assert listed.status_code == 200
    assert listed.get_json()["total"] == 1
    assert fetched.status_code == 200
    assert fetched.get_json()["preauthorization"]["state"] == "active"
    assert missing.status_code == 404
