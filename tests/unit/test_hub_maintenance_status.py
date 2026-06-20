# Standard library imports
import asyncio
import numbers
import os

# Third party imports
from flask.testing import FlaskClient

# Aetherra imports
from Aetherra.maintenance import MaintenanceCoordinator, MaintenanceEvidence, MaintenanceService
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


class _FailingMaintenanceCoordinator:
    def get_status(self):
        raise RuntimeError("Traceback: private maintenance path")


def _register_dummy_services(
    homeo: bool = False,
    sie: bool = False,
    selfinc: bool = False,
    maintenance=None,
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
        if maintenance is not None:
            await register_service("maintenance_system", maintenance)

    asyncio.run(_go())


def _unregister_dummy_services():
    from aetherra_service_registry import get_service_registry

    async def _go():
        registry = await get_service_registry()
        for name in (
            "homeostasis_system",
            "aetherra_homeostasis",
            "self_improvement_engine",
            "self_incorporation",
            "maintenance_system",
            "aetherra_maintenance",
        ):
            await registry.unregister_service(name)

    asyncio.run(_go())


def test_maintenance_status_no_services():
    # Ensure environment does not trigger prod abort guard
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    client: FlaskClient = app.test_client()
    resp = client.get("/api/maintenance/status")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    assert data["contract"]["authority_ownership"]["maintenance"] == [
        "coordinate",
        "route",
        "record_outcome",
    ]
    assert data["loop_readiness"]["ready"] is False
    assert data["loop_readiness"]["ready_count"] == 2
    assert data["loop_readiness"]["phase_count"] == 8
    by_phase = {
        item["phase"]: item for item in data["loop_readiness"]["phases"]
    }
    assert by_phase["observe"]["ready"] is False
    assert by_phase["observe"]["readiness_source"] == "runtime"
    assert by_phase["review"]["ready"] is True
    assert by_phase["review"]["readiness_source"] == "contract"
    assert by_phase["enforce"]["ready"] is True
    assert by_phase["enforce"]["readiness_source"] == "contract"
    assert {item["phase"] for item in data["loop_readiness"]["missing_phases"]} == {
        "observe",
        "diagnose",
        "propose",
        "execute",
        "verify",
        "learn",
    }
    assert data["homeostasis"]["available"] is False
    assert data["self_improvement"]["available"] is False
    assert data["self_incorporation"]["available"] is False
    assert data["maintenance"]["available"] is False


def test_maintenance_status_with_services():
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    _register_dummy_services(homeo=True, sie=True, selfinc=True)
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/maintenance/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["homeostasis"]["available"] is True
        assert data["self_improvement"]["available"] is True
        assert data["self_incorporation"]["available"] is True
        readiness = data["loop_readiness"]
        assert readiness["ready"] is False
        assert readiness["ready_count"] == 7
        by_phase = {item["phase"]: item for item in readiness["phases"]}
        assert by_phase["observe"]["owner"] == "homeostasis"
        assert by_phase["observe"]["ready"] is True
        assert by_phase["diagnose"]["ready"] is True
        assert by_phase["execute"]["ready"] is True
        # No coordinator is registered in this test, so learning visibility is degraded.
        assert by_phase["learn"]["ready"] is False
        assert readiness["missing_phases"] == [
            {
                "phase": "learn",
                "owner": "maintenance",
                "readiness_source": "runtime",
            }
        ]
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
    finally:
        _unregister_dummy_services()


def test_maintenance_status_includes_registered_cycle_summary():
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    coordinator = MaintenanceCoordinator()
    cycle = coordinator.create_cycle("maint-visible")
    cycle.record_observation(
        MaintenanceEvidence(source="homeostasis", summary="kernel queue pressure")
    )
    _register_dummy_services(homeo=True, sie=True, selfinc=True, maintenance=coordinator)
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/maintenance/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["maintenance"]["available"] is True
        assert data["loop_readiness"]["ready"] is True
        assert data["loop_readiness"]["ready_count"] == data["loop_readiness"][
            "phase_count"
        ]
        assert data["loop_readiness"]["missing_phases"] == []
        assert data["maintenance"]["cycle_count"] == 1
        assert data["maintenance"]["active_cycles"][0]["cycle_id"] == "maint-visible"
        assert data["maintenance"]["active_cycles"][0]["status"] == "observed"
    finally:
        _unregister_dummy_services()


def test_maintenance_status_includes_registered_service_metadata(tmp_path):
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    service = MaintenanceService.with_default_store(tmp_path, autosave=False)
    service.create_cycle("maint-service-visible")
    _register_dummy_services(maintenance=service)
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/maintenance/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["maintenance"]["available"] is True
        assert data["maintenance"]["cycle_count"] == 1
        assert data["maintenance"]["service"]["available"] is True
        assert data["maintenance"]["service"]["record_store_configured"] is True
        assert "maintenance_cycles.jsonl" in data["maintenance"]["service"][
            "record_store_path"
        ]
    finally:
        _unregister_dummy_services()


def test_maintenance_status_degrades_when_coordinator_status_fails():
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    _register_dummy_services(maintenance=_FailingMaintenanceCoordinator())
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/maintenance/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["maintenance"]["available"] is False
        assert data["maintenance"]["degraded"] is True
        assert data["maintenance"]["reason"] == "maintenance_status_unavailable"
        assert "Traceback" not in str(data["maintenance"])
    finally:
        _unregister_dummy_services()


def test_maintenance_status_selfinc_metrics_roll_back_token_only():
    os.environ.pop("AETHERRA_PROFILE", None)
    _unregister_dummy_services()
    app = create_app()
    # Register only self-incorporation to isolate KPI extraction
    _register_dummy_services(selfinc=True)
    try:
        client: FlaskClient = app.test_client()
        resp = client.get("/api/maintenance/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["self_incorporation"]["available"] is True
        kpis = data.get("kpis", {})
        assert isinstance(kpis, dict)
        # Ensure fallback pulled from metrics
        assert kpis.get("last_rollback_token") == "rb-test-123"
    finally:
        _unregister_dummy_services()
