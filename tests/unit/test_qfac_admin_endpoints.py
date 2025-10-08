from __future__ import annotations

import os

import pytest

from aetherra_hub.app import create_app


@pytest.fixture
def app():
    # Ensure safe defaults (no live QFAC) and no token guard by default
    os.environ.pop("AETHERRA_QFAC_ADMIN_ENABLE_LIVE", None)
    os.environ.pop("AETHERRA_HUB_CONTROL_TOKEN", None)
    os.environ.setdefault("AETHERRA_QUIET", "1")
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()


def test_qfac_admin_show_safe_defaults(client):
    r = client.get("/api/qfac/admin/show")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)
    assert data.get("available") is False
    assert "retrieval_policy" in data
    assert "parity_counters" in data


def test_qfac_admin_reset_safe_defaults(client):
    r = client.post("/api/qfac/admin/reset")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, dict)
    assert data.get("ok") is False
    assert data.get("reason") == "qfac unavailable"


def test_qfac_admin_token_guard_blocks_when_set(client, monkeypatch):
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "secret")
    # New app to pick up env var
    guarded_app = create_app()
    guarded_client = guarded_app.test_client()

    # No header should be 401
    r = guarded_client.get("/api/qfac/admin/show")
    assert r.status_code == 401

    # Wrong token should be 401
    r = guarded_client.get(
        "/api/qfac/admin/show", headers={"Authorization": "Bearer wrong"}
    )
    assert r.status_code == 401

    # Correct token works (Bearer)
    r = guarded_client.get(
        "/api/qfac/admin/show", headers={"Authorization": "Bearer secret"}
    )
    assert r.status_code == 200

    # Correct token works (custom header)
    r = guarded_client.post(
        "/api/qfac/admin/reset", headers={"X-Aetherra-Control-Token": "secret"}
    )
    assert r.status_code == 200
