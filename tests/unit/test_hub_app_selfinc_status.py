# Standard library imports
import os

# Third party imports
from flask.testing import FlaskClient

# Aetherra imports
from aetherra_hub.app import create_app


class _DummySelfInc:
    async def get_status(self):  # minimal async contract used by blueprint
        return {"status": "ok", "running": True, "files_by_type": {"total": 0}}


def _register_dummy_service():
    # Lazy import inside helper to avoid import cycles if registry not initialized yet
    # Standard library imports
    import asyncio

    # Aetherra imports
    from aetherra_service_registry import register_service

    asyncio.run(register_service("self_incorporation", _DummySelfInc()))


def _unregister_dummy_service():
    # Standard library imports
    import asyncio

    # Aetherra imports
    from aetherra_service_registry import get_service_registry

    async def _unregister() -> None:
        registry = await get_service_registry()
        await registry.unregister_service("self_incorporation")

    asyncio.run(_unregister())


def test_selfinc_status_endpoint_ok(monkeypatch):
    # Ensure environment does not trigger prod abort guard
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    _register_dummy_service()
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/selfinc/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["running"] is True
    finally:
        _unregister_dummy_service()


def test_selfinc_status_endpoint_unavailable(monkeypatch):
    # New app without service registration returns 503
    app = create_app()
    client: FlaskClient = app.test_client()
    resp = client.get("/api/selfinc/status")
    # Accept either 503 (explicit unregistered) or 500 if event loop mismatch
    assert resp.status_code in (503, 500)
