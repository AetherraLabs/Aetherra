import json

from aetherra_hub.app import create_app
from aetherra_hub.blueprints import kernel as kernel_bp


class _FakeKernel:
    def __init__(self):
        self.paused = False
        self.drains = []
        self.queue_limits = {}

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    async def drain_queue(self, name: str, mode: str = "dlq"):
        self.drains.append((name, mode))

    def set_queue_limits(self, limits: dict):
        self.queue_limits.update(limits)

    def get_status(self):
        return {
            "running": True,
            "paused": self.paused,
            "uptime": 1.0,
            "cycle_count": 1,
            "plugin_invoke_timeout_sec": 20.0,
            "backpressure_guard_pass": True,
            "backpressure_guard_violations": [],
            "night_schedule_guard_pass": True,
            "metrics": {"errors_count": 0},
            "queue_sizes": {
                "high_priority": 0,
                "normal_priority": 0,
                "background": 0,
            },
            "queue_limits": dict(self.queue_limits),
            "plugin_cb_open": False,
            "dlq_count": 0,
            "hmr": {"attempts": 0, "success": 0, "rollback": 0},
            "inflight": {},
        }


def _client(monkeypatch, tmp_path, fake_kernel):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setattr(
        kernel_bp.registry_client,
        "get_service",
        lambda service_name: fake_kernel if service_name == "kernel_loop" else None,
    )
    monkeypatch.setattr(
        kernel_bp.registry_client,
        "get_kernel_status",
        lambda: fake_kernel.get_status(),
    )
    return create_app().test_client()


def _headers():
    return {
        "Authorization": "Bearer control-secret",
        "X-Aetherra-Principal": "kernel-admin",
    }


def test_kernel_pause_writes_guardian_audit(monkeypatch, tmp_path):
    fake_kernel = _FakeKernel()
    client = _client(monkeypatch, tmp_path, fake_kernel)

    response = client.post("/api/kernel/control/pause", headers=_headers())
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert response.status_code == 200
    assert response.get_json()["ok"] is True
    assert fake_kernel.paused is True
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "kernel.pause"
    assert "kernel_control" in entries[-1]["details"]["risk"]["factors"]


def test_kernel_pause_blocked_by_guardian_missing_capability(monkeypatch, tmp_path):
    fake_kernel = _FakeKernel()
    client = _client(monkeypatch, tmp_path, fake_kernel)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")

    response = client.post("/api/kernel/control/pause", headers=_headers())
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "missing_capability"
    assert payload["guardian"]["status"] == "deny"
    assert fake_kernel.paused is False


def test_kernel_queue_limits_audit_does_not_store_limit_values(monkeypatch, tmp_path):
    fake_kernel = _FakeKernel()
    client = _client(monkeypatch, tmp_path, fake_kernel)

    response = client.post(
        "/api/kernel/control/queue_limits",
        json={"normal_priority": "do-not-audit-limit-value"},
        headers=_headers(),
    )
    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert response.status_code == 200
    assert fake_kernel.queue_limits == {"normal_priority": "do-not-audit-limit-value"}
    assert "kernel.set_queue_limits" in ledger_text
    assert "do-not-audit-limit-value" not in ledger_text


def test_kernel_readiness_endpoint_reports_ready(monkeypatch, tmp_path):
    fake_kernel = _FakeKernel()
    client = _client(monkeypatch, tmp_path, fake_kernel)

    response = client.get("/api/kernel/readiness")
    payload = response.get_json()

    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert payload["ok"] is True
    assert payload["readiness"]["readiness"] == "ready"
    assert payload["readiness"]["safe_to_schedule"] is True
