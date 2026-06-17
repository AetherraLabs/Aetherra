import json

from aetherra_hub.app import create_app
from aetherra_hub.blueprints import homeostasis


class _FakeActuators:
    def __init__(self):
        self.actions = []
        self.rollbacks = 0

    def execute_action(self, action):
        self.actions.append(action)
        return True

    def rollback_last_action(self):
        self.rollbacks += 1

        class _Result:
            success = True
            message = "rolled back"

        return _Result()


class _FakeOrchestrator:
    def __init__(self):
        self.actuators = _FakeActuators()
        self.mode_calls = []
        self.emergency_stops = []
        self.emergency_resets = 0

    async def set_controller_mode(self, mode, reason):
        self.mode_calls.append((mode, reason))

    async def emergency_stop(self, reason):
        self.emergency_stops.append(reason)

    async def reset_emergency_stop(self):
        self.emergency_resets += 1


def _client(monkeypatch, tmp_path, orchestrator):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(homeostasis, "get_homeostasis_orchestrator", lambda: orchestrator)
    return create_app().test_client()


def _headers():
    return {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "homeostasis-admin",
    }


def test_homeostasis_actuator_execution_writes_guardian_audit(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/actuators/execute",
        json={
            "action_type": "restart_component",
            "target_service": "plugin_service",
            "parameters": {"component": "demo"},
            "reason": "recover stalled component",
        },
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert response.status_code == 200
    assert response.get_json()["executed"] is True
    assert len(orchestrator.actuators.actions) == 1
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.actuate"
    assert entries[-1]["details"]["intent"]["target"] == (
        "plugin_service:restart_component"
    )


def test_homeostasis_actuator_blocked_by_guardian_missing_capability(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")

    response = client.post(
        "/api/homeostasis/actuators/execute",
        json={"action_type": "restart_component", "target_service": "plugin_service"},
        headers=_headers(),
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "missing_capability"
    assert payload["guardian"]["status"] == "deny"
    assert orchestrator.actuators.actions == []


def test_homeostasis_security_target_is_contained(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/actuators/execute",
        json={
            "action_type": "relax_policy",
            "target_service": "security_policy",
            "parameters": {"mode": "permissive"},
            "reason": "unsafe test request",
        },
        headers=_headers(),
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "critical_risk_requires_containment"
    assert payload["guardian"]["status"] == "contain"
    assert orchestrator.actuators.actions == []


def test_homeostasis_guardian_audit_does_not_store_parameter_values(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/actuators/execute",
        json={
            "action_type": "restart_component",
            "target_service": "plugin_service",
            "parameters": {"token": "do-not-audit-this-value"},
        },
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "do-not-audit-this-value" not in ledger_text
    assert "plugin_service:restart_component" in ledger_text


def test_homeostasis_mode_change_writes_guardian_audit(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/mode",
        json={"mode": "advisory", "reason": "reduce autonomous action"},
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert response.status_code == 200
    assert response.get_json()["mode"] == "advisory"
    assert len(orchestrator.mode_calls) == 1
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.set_mode"
    assert "homeostasis_actuation" in entries[-1]["details"]["risk"]["factors"]


def test_homeostasis_rollback_writes_guardian_audit(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post("/api/homeostasis/rollback", headers=_headers())
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert response.status_code == 200
    assert response.get_json()["rolled_back"] is True
    assert orchestrator.actuators.rollbacks == 1
    assert entries[-1]["details"]["intent"]["action"] == "homeostasis.rollback"


def test_homeostasis_control_blocked_by_guardian_missing_capability(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")

    response = client.post(
        "/api/homeostasis/emergency_stop",
        json={"reason": "operator test"},
        headers=_headers(),
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "missing_capability"
    assert payload["guardian"]["status"] == "deny"
    assert orchestrator.emergency_stops == []
