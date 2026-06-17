import json

from aetherra_hub.app import create_app
from aetherra_hub.blueprints import plugins


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "0")
    plugins._PLUGIN_REGISTRY.clear()
    return create_app().test_client()


def _headers():
    return {
        "X-Aetherra-Control-Token": "control-secret",
        "X-Aetherra-Principal": "plugin-admin",
    }


def test_plugin_registration_writes_guardian_audit(monkeypatch, tmp_path):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/plugins/register",
        json={
            "name": "guardian_registered_plugin",
            "version": "1.0.0",
            "description": "Registered through Guardian",
        },
        headers=_headers(),
    )

    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    guardian_entry = next(
        entry
        for entry in entries
        if entry.get("event_type") == "guardian_decision"
        and entry["details"]["intent"]["action"] == "plugin.register"
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"
    assert guardian_entry["details"]["intent"]["target"] == (
        "plugin:guardian_registered_plugin"
    )
    assert guardian_entry["details"]["intent"]["capabilities"] == ["plugin:register"]
    assert guardian_entry["details"]["risk"]["factors"] == ["plugin_registration"]


def test_plugin_registration_blocked_by_guardian_missing_capability(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")

    response = client.post(
        "/api/plugins/register",
        json={
            "name": "blocked_registration",
            "version": "1.0.0",
            "description": "Should not enter the registry",
        },
        headers=_headers(),
    )
    payload = response.get_json()

    assert response.status_code == 403
    assert payload["error"] == "missing_capability"
    assert payload["guardian"]["status"] == "deny"
    assert plugins._PLUGIN_REGISTRY.get("blocked_registration") is None


def test_plugin_registration_guardian_audit_omits_payload_values(
    monkeypatch, tmp_path
):
    client = _client(monkeypatch, tmp_path)

    response = client.post(
        "/api/plugins/register",
        json={
            "name": "redacted_registration",
            "version": "1.0.0",
            "description": "secret='do-not-audit-this-description'",
            "homepage": "https://example.invalid/private-token-value",
            "signature": "do-not-audit-this-signature",
            "pubkey": "do-not-audit-this-pubkey",
        },
        headers=_headers(),
    )

    ledger_text = (
        tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ).read_text(encoding="utf-8")

    assert response.status_code == 200
    assert "do-not-audit-this-description" not in ledger_text
    assert "do-not-audit-this-signature" not in ledger_text
    assert "do-not-audit-this-pubkey" not in ledger_text
    assert "private-token-value" not in ledger_text
    assert "redacted_registration" in ledger_text
