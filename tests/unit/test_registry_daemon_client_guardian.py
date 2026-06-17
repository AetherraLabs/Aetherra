import json

import aetherra_registry_client as client


class _FakeResponse:
    status_code = 200

    def json(self):
        return {"ok": True, "services": {}}


class _FakeRequests:
    def __init__(self):
        self.calls = []

    def get(self, url, timeout):
        self.calls.append(("get", url, None, timeout))
        return _FakeResponse()

    def post(self, url, json, timeout):
        self.calls.append(("post", url, json, timeout))
        return _FakeResponse()


def _guardian_env(monkeypatch, tmp_path, *, requester=None, strict=False):
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "http://daemon.local:3030")
    if requester:
        monkeypatch.setenv("AETHERRA_PRINCIPAL", requester)
    else:
        monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    if strict:
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    else:
        monkeypatch.delenv("AETHERRA_REQUIRE_CAPABILITIES", raising=False)


def _audit_text(tmp_path):
    return (tmp_path / ".aetherra" / "security" / "audit.jsonl").read_text(
        encoding="utf-8"
    )


def _audit_entries(tmp_path):
    return [
        json.loads(line)
        for line in _audit_text(tmp_path).splitlines()
        if line.strip()
    ]


def test_registry_daemon_register_is_guardian_audited_without_metadata_values(
    monkeypatch, tmp_path
):
    _guardian_env(monkeypatch, tmp_path)
    fake_requests = _FakeRequests()
    monkeypatch.setattr(client, "requests", fake_requests)

    result = client.http_register_service(
        "demo_service",
        status="healthy",
        metadata={"token": "do-not-audit-this-token"},
        endpoints={"api": "http://127.0.0.1/private"},
    )

    assert result is True
    assert fake_requests.calls
    ledger_text = _audit_text(tmp_path)
    assert "do-not-audit-this-token" not in ledger_text
    assert "daemon.local" not in ledger_text
    assert "127.0.0.1/private" not in ledger_text
    assert _audit_entries(tmp_path)[-1]["details"]["intent"]["action"] == (
        "service_registry.daemon_register"
    )


def test_registry_daemon_heartbeat_denial_skips_http(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-registry-client",
        strict=True,
    )
    fake_requests = _FakeRequests()
    monkeypatch.setattr(client, "requests", fake_requests)

    result = client.http_heartbeat("demo_service")

    assert result is False
    assert fake_requests.calls == []
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "service_registry.daemon_heartbeat"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_registry_daemon_update_denial_skips_http(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-registry-client",
        strict=True,
    )
    fake_requests = _FakeRequests()
    monkeypatch.setattr(client, "requests", fake_requests)

    result = client.http_update(
        "demo_service",
        status="degraded",
        metadata={"reason": "do-not-forward"},
    )

    assert result is False
    assert fake_requests.calls == []
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "service_registry.daemon_update"
    assert entry["details"]["decision"]["reason"] == "missing_capability"


def test_registry_daemon_status_denial_skips_http(monkeypatch, tmp_path):
    _guardian_env(
        monkeypatch,
        tmp_path,
        requester="external-registry-client",
        strict=True,
    )
    fake_requests = _FakeRequests()
    monkeypatch.setattr(client, "requests", fake_requests)

    result = client.http_get_status()

    assert result is None
    assert fake_requests.calls == []
    entry = _audit_entries(tmp_path)[-1]
    assert entry["details"]["intent"]["action"] == "service_registry.daemon_status"
    assert entry["details"]["decision"]["reason"] == "missing_capability"
