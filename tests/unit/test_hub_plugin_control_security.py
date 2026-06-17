"""Security regression tests for Hub plugin registration."""

from __future__ import annotations

from aetherra_hub.app import create_app


def test_unsigned_header_cannot_bypass_strict_signing(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    monkeypatch.delenv("AETHERRA_ALLOW_UNSIGNED_DEV", raising=False)
    monkeypatch.delenv("AETHERRA_HUB_CONTROL_TOKEN", raising=False)
    client = create_app().test_client()

    response = client.post(
        "/api/plugins/register",
        json={
            "name": "unsigned_header_probe",
            "version": "1.0.0",
            "description": "Verifies request headers cannot disable signing policy",
        },
        headers={"X-Aeth-Allow-Unsigned": "1"},
    )

    assert response.status_code == 400


def test_unsigned_dev_override_is_disabled_in_production(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    monkeypatch.setenv("AETHERRA_ALLOW_UNSIGNED_DEV", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "control-secret")
    monkeypatch.setenv("AETHERRA_AI_API_ENABLED", "0")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY_STRICT", "1")
    monkeypatch.setenv("AETHERRA_SIGNING_STRICT", "1")
    client = create_app().test_client()

    response = client.post(
        "/api/plugins/register",
        json={
            "name": "production_unsigned_probe",
            "version": "1.0.0",
            "description": "Verifies production ignores unsigned development override",
        },
        headers={"X-Aetherra-Control-Token": "control-secret"},
    )

    assert response.status_code == 400
