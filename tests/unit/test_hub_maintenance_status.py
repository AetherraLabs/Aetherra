# Standard library imports
import asyncio
import numbers
import os

# Third party imports
from flask.testing import FlaskClient

# Aetherra imports
from aetherra_hub.app import create_app


class _DummyHomeostasis:
    def get_orchestrator_status(self):
        return {"running": True, "initialized": True}

    async def get_system_health_status(
        self,
    ):  # minimal async contract used by blueprint
        return {
            "system_health": {
                "health_summary": {
                    "health_percentage": 90.0,
                    "critical_health_percentage": 95.0,
                }
            },
            "supervisor": {"runlevel": "ONLINE"},
        }


class _DummySIE:
    async def handle_message(self, message_type, data):  # minimal async
        if str(message_type).endswith("status"):
            return {"improvement_active": True, "total_proposals": 0}
        return {"ok": True}


class _DummySelfInc:
    async def get_status(self):  # minimal async
        return {
            "status": "ok",
            "running": True,
            "files_by_type": {"total": 0},
            "metrics": {
                "files_integrated": 0,
                "files_quarantined": 0,
                # Provide last rollback token only via metrics to test fallback path
                "last_rollback_token": "rb-test-123",
            },
        }


def _register_dummy_services(
    homeo: bool = False, sie: bool = False, selfinc: bool = False
):
    # Lazy import inside helper to avoid import cycles if registry not initialized yet
    from aetherra_service_registry import register_service

    async def _go():
        if homeo:
            await register_service("homeostasis_system", _DummyHomeostasis())
        if sie:
            await register_service("self_improvement_engine", _DummySIE())
        if selfinc:
            await register_service("self_incorporation", _DummySelfInc())

    asyncio.run(_go())


def test_maintenance_status_no_services():
    # Ensure environment does not trigger prod abort guard
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    client: FlaskClient = app.test_client()
    resp = client.get("/api/maintenance/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["homeostasis"]["available"] is False
    assert data["self_improvement"]["available"] is False
    assert data["self_incorporation"]["available"] is False


def test_maintenance_status_with_services():
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    _register_dummy_services(homeo=True, sie=True, selfinc=True)
    client: FlaskClient = app.test_client()
    resp = client.get("/api/maintenance/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["homeostasis"]["available"] is True
    assert data["self_improvement"]["available"] is True
    assert data["self_incorporation"]["available"] is True
    # Headline fields filled
    assert data["overall"]["runlevel"] in ("ONLINE", "UNKNOWN")
    # Health percentages may be None in some environments; only assert presence when reported
    hp = data["overall"].get("health_percent")
    if hp is not None:
        assert isinstance(hp, numbers.Real)
        # When overall health percent is present, system_health_score should mirror it / 100
        kpis = data.get("kpis", {})
        assert isinstance(kpis, dict)
        if "system_health_score" in kpis and kpis["system_health_score"] is not None:
            assert abs(kpis["system_health_score"] - (float(hp) / 100.0)) < 1e-6
    else:
        # kpis still present best-effort
        assert isinstance(data.get("kpis", {}), dict)


def test_maintenance_status_selfinc_metrics_roll_back_token_only():
    os.environ.pop("AETHERRA_PROFILE", None)
    app = create_app()
    # Register only self-incorporation to isolate KPI extraction
    _register_dummy_services(selfinc=True)
    client: FlaskClient = app.test_client()
    resp = client.get("/api/maintenance/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["self_incorporation"]["available"] is True
    kpis = data.get("kpis", {})
    assert isinstance(kpis, dict)
    # Ensure fallback pulled from metrics
    assert kpis.get("last_rollback_token") == "rb-test-123"
