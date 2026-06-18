import json

from Aetherra.guardian.approval import resolve_approval
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

    def get_actuator_status(self):
        return {
            "actions_executed": len(self.actions),
            "rollback_actions_available": self.rollbacks,
        }

    def get_action_history(self, count=50):
        return self.actions[-count:]


class _FakeController:
    setpoints = {
        "core_metrics": {
            "memory_rtt": {
                "target": 50.0,
                "max_acceptable": 120.0,
                "critical_threshold": 500.0,
                "control_band": 20.0,
            },
            "plugin_load_success": {
                "target": 95.0,
                "min_acceptable": 85.0,
                "critical_threshold": 70.0,
                "control_band": 5.0,
            },
            "queue_depth": {
                "target": 5.0,
                "max_acceptable": 50.0,
                "critical_threshold": 100.0,
                "control_band": 10.0,
            },
        }
    }

    def get_controller_status(self):
        return {
            "mode": "observe_only",
            "running": True,
            "emergency_stop": False,
            "pending_actions": 0,
            "confirmation_pending": 0,
        }

    def get_control_loop_status(self):
        return {}


class _FakeOrchestrator:
    def __init__(self):
        self.actuators = _FakeActuators()
        self.mode_calls = []
        self.emergency_stops = []
        self.emergency_resets = 0
        self.controller = _FakeController()
        self.supervisor = None

    async def set_controller_mode(self, mode, reason):
        self.mode_calls.append((mode, reason))

    async def emergency_stop(self, reason):
        self.emergency_stops.append(reason)

    async def reset_emergency_stop(self):
        self.emergency_resets += 1

    async def get_system_health_status(self):
        return {
            "metrics": {"status": "degraded", "health_score": 72.0},
            "current_snapshot": {
                "timestamp": 1000.0,
                "memory_rtt": 180.0,
                "plugin_load_success": 60.0,
                "queue_depth": 120.0,
            },
        }

    async def get_metrics_snapshot(self):
        return {
            "timestamp": 1000.0,
            "memory_rtt": 180.0,
            "plugin_load_success": 60.0,
            "queue_depth": 120.0,
        }


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


def _audit_entries(audit_path):
    return [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _guardian_decisions(entries):
    return [
        entry
        for entry in entries
        if entry.get("actor") == "guardian"
        and entry.get("event_type") == "guardian_decision"
    ]


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
    entries = _audit_entries(audit_path)
    decisions = _guardian_decisions(entries)

    assert response.status_code == 200
    body = response.get_json()
    assert body["executed"] is True
    assert len(orchestrator.actuators.actions) == 1
    assert decisions[-1]["details"]["intent"]["action"] == "homeostasis.actuate"
    assert decisions[-1]["details"]["intent"]["target"] == (
        "plugin_service:restart_component"
    )
    assert entries[-1]["event_type"] == "guardian_outcome"
    assert entries[-1]["details"]["decision_audit_id"] == body["audit_id"]


def test_homeostasis_observation_is_read_only(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.get("/api/homeostasis/observation")
    payload = response.get_json()

    assert response.status_code == 200
    observation = payload["observation"]
    assert observation["phase"] == "observation"
    assert observation["actions_enabled"] is False
    assert observation["health"]["status"] == "degraded"
    assert observation["metrics"]["values"]["memory_rtt"] == 180.0
    assert observation["risk"]["level"] in {"elevated", "high", "critical"}
    assert orchestrator.actuators.actions == []
    assert orchestrator.mode_calls == []
    assert orchestrator.emergency_stops == []


def test_homeostasis_diagnosis_is_read_only(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.get("/api/homeostasis/diagnosis")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["observation"]["actions_enabled"] is False
    diagnosis = payload["diagnosis"]
    assert diagnosis["phase"] == "diagnosis"
    assert diagnosis["actions_enabled"] is False
    assert diagnosis["summary"]["status"] == "causes_identified"
    categories = {cause["category"] for cause in diagnosis["causes"]}
    assert "memory_pressure" in categories
    assert "agent_or_kernel_overload" in categories
    assert orchestrator.actuators.actions == []
    assert orchestrator.mode_calls == []
    assert orchestrator.emergency_stops == []


def test_homeostasis_recommendations_are_read_only(monkeypatch, tmp_path):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.get("/api/homeostasis/recommendations")
    payload = response.get_json()

    assert response.status_code == 200
    recommendations = payload["recommendations"]
    assert recommendations["phase"] == "recommendation"
    assert recommendations["actions_enabled"] is False
    assert recommendations["execution"]["performed"] is False
    assert recommendations["summary"]["requires_guardian_before_execution"] is True
    assert recommendations["recommendations"]
    assert all(
        item["requires_guardian"] is True
        for item in recommendations["recommendations"]
    )
    assert orchestrator.actuators.actions == []
    assert orchestrator.mode_calls == []
    assert orchestrator.emergency_stops == []


def test_homeostasis_recommendation_execution_requires_confirmation(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/recommendations/execute",
        json={
            "action_type": "increase_task_workers",
            "target_service": "kernel_system",
        },
        headers=_headers(),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "confirm_execution required"
    assert orchestrator.actuators.actions == []


def test_homeostasis_recommendation_execution_rejects_stale_recommendation(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    response = client.post(
        "/api/homeostasis/recommendations/execute",
        json={
            "action_type": "restart_everything",
            "target_service": "kernel_system",
            "confirm_execution": True,
        },
        headers=_headers(),
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "recommendation_not_current"
    assert orchestrator.actuators.actions == []


def test_homeostasis_recommendation_execution_is_guardian_reviewed(
    monkeypatch, tmp_path
):
    orchestrator = _FakeOrchestrator()
    client = _client(monkeypatch, tmp_path, orchestrator)

    pending = client.post(
        "/api/homeostasis/recommendations/execute",
        json={
            "action_type": "increase_task_workers",
            "target_service": "kernel_system",
            "confirm_execution": True,
            "reason": "operator accepted current recommendation",
        },
        headers=_headers(),
    )
    pending_body = pending.get_json()

    assert pending.status_code == 202
    assert pending_body["error"] == "risk_requires_approval"
    approval_id = pending_body["guardian"]["details"]["approval_request_id"]
    assert orchestrator.actuators.actions == []

    resolve_approval(approval_id, approved=True, approver="homeostasis-admin")

    response = client.post(
        "/api/homeostasis/recommendations/execute",
        json={
            "action_type": "increase_task_workers",
            "target_service": "kernel_system",
            "confirm_execution": True,
            "guardian_approval_id": approval_id,
            "reason": "operator accepted current recommendation",
        },
        headers=_headers(),
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = _audit_entries(audit_path)
    decisions = _guardian_decisions(entries)

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["executed"] is True
    assert payload["controlled_action"] == {
        "source": "current_recommendation",
        "guardian_reviewed": True,
        "executed": True,
    }
    assert payload["recommendation"]["action_type"] == "increase_task_workers"
    assert len(orchestrator.actuators.actions) == 1
    action = orchestrator.actuators.actions[0]
    assert action.action_type == "increase_task_workers"
    assert action.parameters == {"worker_count_delta": 1}
    assert decisions[-1]["details"]["intent"]["action"] == "homeostasis.actuate"
    assert decisions[-1]["details"]["intent"]["metadata"]["controller_name"] == (
        "homeostasis_recommendation"
    )
    assert entries[-1]["event_type"] == "guardian_outcome"
    assert payload["outcome_audit_id"] == entries[-1]["hash"]

    learning = client.get("/api/homeostasis/learning", headers=_headers())
    learning_payload = learning.get_json()["learning"]

    assert learning.status_code == 200
    assert learning_payload["summary"]["completed"] == 1
    assert learning_payload["summary"]["success_rate"] == 1.0
    assert (
        learning_payload["action_effectiveness"]["increase_task_workers"]["completed"]
        == 1
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
