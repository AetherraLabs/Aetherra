"""Security tests for Hub script control endpoints."""

from __future__ import annotations

from aetherra_hub.app import create_app


def test_script_control_requires_configured_token(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    client = create_app().test_client()

    denied = client.post("/api/run", json={"script_name": "system_readiness"})
    allowed = client.post(
        "/api/run",
        json={"script_name": "system_readiness"},
        headers={"X-Aetherra-Control-Token": "control-secret"},
    )

    assert denied.status_code == 401
    assert allowed.status_code == 200
    assert allowed.get_json()["ok"] is True


def test_script_control_rejects_invalid_payload(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    client = create_app().test_client()

    response = client.post(
        "/api/run",
        json={"script_name": "x", "parameters": ["not", "a", "mapping"]},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "invalid_job_payload"
