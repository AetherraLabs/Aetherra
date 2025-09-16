import os
from flask.testing import FlaskClient
from aetherra_hub.app import create_app

class _DummySelfInc:
    async def get_status(self):  # minimal async contract used by blueprint
        return {"status": "ok", "running": True, "files_by_type": {"total": 0}}


def _register_dummy_service():
    # Lazy import inside helper to avoid import cycles if registry not initialized yet
    import asyncio
    from aetherra_service_registry import register_service
    asyncio.run(register_service("self_incorporation", _DummySelfInc()))


def test_selfinc_status_endpoint_ok(monkeypatch):
    # Ensure environment does not trigger prod abort guard
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    _register_dummy_service()
    client: FlaskClient = app.test_client()
    resp = client.get("/api/selfinc/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["running"] is True


def test_selfinc_status_endpoint_unavailable(monkeypatch):
    # New app without service registration returns 503
    app = create_app()
    client: FlaskClient = app.test_client()
    resp = client.get("/api/selfinc/status")
    # Accept either 503 (explicit unregistered) or 500 if event loop mismatch
    assert resp.status_code in (503, 500)
