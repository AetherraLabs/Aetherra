"""Maintenance observations must preserve evidence without acquiring authority."""

# Standard library imports
from datetime import datetime, timedelta
from types import SimpleNamespace

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_service_registry as registry_module
from Aetherra.maintenance import (
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceExecution,
    MaintenanceProposal,
    MaintenanceService,
)
from Aetherra.runtime_ui import collect_runtime_ui_system_status
from aetherra_hub.blueprints.runtime_ui import bp
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)


@pytest.fixture
def registry(monkeypatch):
    current = AetherraServiceRegistry()
    current._running = True
    monkeypatch.setattr(registry_module, "_service_registry", current)
    return current


def _register(registry, service, *, name="maintenance_system", stale=False):
    registry._services[name] = ServiceInfo(
        name=name,
        instance=service,
        status=ServiceStatus.HEALTHY,
        last_heartbeat=datetime.now() - timedelta(hours=1 if stale else 0),
    )


def _proposed_service(service=None):
    service = service or MaintenanceService(autosave=False)
    cycle = service.route_proposal(
        MaintenanceProposal(
            proposal_id="private-proposal-reference",
            source="self_improvement",
            target_subsystem="memory",
            issue="private issue detail",
            proposed_action="private action detail",
            expected_benefit="lower latency",
            risk_level="low",
            rollback_plan="private rollback detail",
        ),
        diagnosis=MaintenanceEvidence("self_improvement", "private diagnosis"),
        observations=[MaintenanceEvidence("homeostasis", "private observation")],
        cycle_id="private-cycle-reference",
    )
    return service, cycle


@pytest.mark.parametrize("service_name", ["maintenance_system", "aetherra_maintenance"])
def test_bootstrap_exposes_real_proposal_without_deciding_or_executing(
    registry, service_name
):
    service, cycle = _proposed_service()
    before = service.export_records()
    _register(registry, service, name=service_name)
    app = Flask(__name__)
    app.register_blueprint(bp)

    response = app.test_client().get("/api/runtime-ui/bootstrap")
    assert response.status_code == 200
    body = response.get_json()
    maintenance = next(
        item
        for item in body["observatory"]["subsystems"]
        if item["name"] == "maintenance"
    )
    assert maintenance["status"] == "active"
    metrics = maintenance["metrics"]
    assert metrics["service_name"] == service_name
    assert metrics["evidence"] == "service_status"
    assert metrics["readiness_verified"] is False
    assert metrics["cycle_count"] == 1
    assert metrics["latest_cycle_present"] is True
    assert metrics["latest_cycle_status"] == "proposed"
    assert metrics["latest_observations"] == 1
    assert metrics["latest_has_diagnosis"] is True
    assert metrics["latest_has_proposal"] is True
    assert metrics["latest_guardian_status"] == "not_recorded"
    assert metrics["latest_security_enforced"] is False
    assert metrics["latest_execution_status"] == "not_recorded"
    assert metrics["latest_guardian_audit_id_hash"] is None
    assert len(metrics["latest_cycle_id_hash"]) == 16
    assert len(metrics["latest_proposal_id_hash"]) == 16
    assert "private" not in str(maintenance)
    assert body["read_only"] is True
    assert body["manifest"]["controls_enabled"] is False
    assert service.export_records() == before
    assert cycle.guardian_decision is None
    assert cycle.execution is None


def test_snapshot_keeps_real_guardian_audit_relation_separate_from_execution(registry):
    service, cycle = _proposed_service()
    cycle.record_guardian_decision(
        MaintenanceDecision(
            "allow", "private reason", audit_id="private-audit-reference"
        )
    )
    cycle.record_security_enforcement(allowed=True, reason="private enforcement")
    _register(registry, service)

    metrics = collect_runtime_ui_system_status()["maintenance"]["metrics"]
    assert metrics["latest_guardian_status"] == "allow"
    assert len(metrics["latest_guardian_audit_id_hash"]) == 16
    assert metrics["latest_execution_status"] == "not_recorded"
    assert "private" not in str(metrics)

    cycle.record_execution(
        MaintenanceExecution("self_incorporation", "applied", "private outcome")
    )
    applied = collect_runtime_ui_system_status()["maintenance"]["metrics"]
    assert applied["latest_execution_status"] == "applied"
    assert (
        applied["latest_guardian_audit_id_hash"]
        == metrics["latest_guardian_audit_id_hash"]
    )


def test_empty_maintenance_has_observed_zero_counts_without_a_fabricated_cycle(
    registry,
):
    _register(registry, MaintenanceService(autosave=False))
    metrics = collect_runtime_ui_system_status()["maintenance"]["metrics"]
    assert metrics["cycle_count"] == 0
    assert metrics["failure_count"] == 0
    assert metrics["latest_cycle_present"] is False
    assert metrics["latest_cycle_status"] is None
    assert metrics["latest_execution_status"] is None
    assert metrics["latest_guardian_status"] is None


def test_malformed_maintenance_data_stays_unknown_and_private_fields_are_not_forwarded(
    registry,
):
    service = SimpleNamespace(
        get_status=lambda: {
            "available": True,
            "cycle_count": True,
            "active_cycle_count": -1,
            "terminal_cycle_count": "private-count",
            "failure_count": None,
            "service": {
                "record_store_path": "private/path",
                "last_persist_error": "private-error",
            },
            "recent_cycles": [
                {
                    "cycle_id": {"private": "id"},
                    "status": "private-state",
                    "observations": -3,
                    "has_diagnosis": "private-diagnosis",
                    "has_proposal": 1,
                    "guardian_status": "private-decision",
                    "execution_status": "private-execution",
                    "security_enforced": "private-enforcement",
                    "last_event": {"summary": "private-event"},
                    "failures": ["private-failure"],
                }
            ],
        }
    )
    _register(registry, service)
    metrics = collect_runtime_ui_system_status()["maintenance"]["metrics"]
    for name in (
        "cycle_count",
        "active_cycle_count",
        "terminal_cycle_count",
        "failure_count",
        "latest_cycle_id_hash",
        "latest_cycle_status",
        "latest_observations",
        "latest_has_diagnosis",
        "latest_has_proposal",
        "latest_guardian_status",
        "latest_execution_status",
        "latest_security_enforced",
    ):
        assert metrics[name] is None, name
    assert "private" not in str(metrics)
    assert all(
        value is None or isinstance(value, (str, int, float, bool))
        for value in metrics.values()
    )


def test_stale_maintenance_is_not_queried_or_published_as_fresh(registry):
    def must_not_read():
        pytest.fail("stale Maintenance status must not be queried")

    _register(registry, SimpleNamespace(get_status=must_not_read), stale=True)
    maintenance = collect_runtime_ui_system_status()["maintenance"]
    assert maintenance["status"] == "unknown"
    assert maintenance["metrics"]["evidence"] == "heartbeat_stale"
    assert "cycle_count" not in maintenance["metrics"]


def test_missing_or_failed_maintenance_status_does_not_claim_an_empty_record(registry):
    def unavailable():
        raise RuntimeError("private status failure")

    _register(registry, SimpleNamespace(get_status=unavailable))
    maintenance = collect_runtime_ui_system_status()["maintenance"]
    assert maintenance["status"] == "unknown"
    assert maintenance["metrics"]["evidence"] == "service_status_unavailable"
    assert "cycle_count" not in maintenance["metrics"]
    assert "private" not in str(maintenance)


def test_failed_store_load_is_degraded_without_exposing_error_or_path(
    registry, tmp_path
):
    original = MaintenanceService.with_default_store(tmp_path)
    original.create_cycle("private-load-cycle")
    store_path = original.record_store.file_path
    saved = store_path.read_bytes()
    store_path.write_text("private-invalid-json", encoding="utf-8")
    service = MaintenanceService.with_default_store(tmp_path)
    assert service.get_status()["service"]["last_persist_error"] == "ValueError"
    _register(registry, service)

    failed = collect_runtime_ui_system_status()["maintenance"]
    assert failed["status"] == "degraded"
    assert failed["metrics"]["persistence_state"] == "error"
    assert failed["metrics"]["cycle_count"] == 0
    assert failed["metrics"]["latest_cycle_present"] is False
    assert "private" not in str(failed)
    assert "ValueError" not in str(failed)
    assert str(tmp_path) not in str(failed)
    assert store_path.read_text(encoding="utf-8") == "private-invalid-json"

    store_path.write_bytes(saved)
    assert service.load_records() == 1
    recovered = collect_runtime_ui_system_status()["maintenance"]
    assert recovered["status"] == "active"
    assert recovered["metrics"]["persistence_state"] == "autosave_enabled"
    assert recovered["metrics"]["cycle_count"] == 1
    assert recovered["metrics"]["latest_cycle_present"] is True
    assert store_path.read_bytes() == saved


def test_failed_store_save_keeps_in_process_proposal_visible_and_can_recover(
    registry, tmp_path
):
    service = MaintenanceService.with_default_store(tmp_path)
    store_path = service.record_store.file_path
    blocked_temp = store_path.with_suffix(".jsonl.tmp")
    blocked_temp.mkdir(parents=True)
    service, cycle = _proposed_service(service)
    error = service.get_status()["service"]["last_persist_error"]
    assert error
    assert not store_path.exists()
    before = service.export_records()
    _register(registry, service)

    failed = collect_runtime_ui_system_status()["maintenance"]
    assert failed["status"] == "degraded"
    assert failed["metrics"]["persistence_state"] == "error"
    assert failed["metrics"]["cycle_count"] == 1
    assert failed["metrics"]["latest_cycle_status"] == "proposed"
    assert failed["metrics"]["latest_guardian_status"] == "not_recorded"
    assert failed["metrics"]["latest_execution_status"] == "not_recorded"
    assert "private" not in str(failed)
    assert error not in str(failed)
    assert str(tmp_path) not in str(failed)
    assert service.export_records() == before
    assert not store_path.exists()

    blocked_temp.rmdir()
    assert service.save_records() is True
    saved = store_path.read_bytes()
    recovered = collect_runtime_ui_system_status()["maintenance"]
    assert recovered["status"] == "active"
    assert recovered["metrics"]["persistence_state"] == "autosave_enabled"
    assert (
        recovered["metrics"]["latest_cycle_id_hash"]
        == failed["metrics"]["latest_cycle_id_hash"]
    )
    assert store_path.read_bytes() == saved
    assert (
        MaintenanceService.with_default_store(tmp_path).get_cycle(cycle.cycle_id)
        is not None
    )


@pytest.mark.parametrize(
    ("configured", "autosave", "expected"),
    [
        (True, True, "autosave_enabled"),
        (True, False, "autosave_disabled"),
        (False, True, "no_store"),
    ],
)
def test_persistence_configuration_is_not_a_durability_claim(
    registry, tmp_path, configured, autosave, expected
):
    service = (
        MaintenanceService.with_default_store(tmp_path, autosave=autosave)
        if configured
        else MaintenanceService(autosave=autosave)
    )
    _register(registry, service)
    maintenance = collect_runtime_ui_system_status()["maintenance"]
    assert maintenance["metrics"]["persistence_state"] == expected
    assert maintenance["metrics"]["readiness_verified"] is False


@pytest.mark.parametrize(
    "metadata",
    [
        None,
        "private-metadata",
        {},
        {"record_store_configured": True, "autosave": True},
        {
            "record_store_configured": "private",
            "autosave": True,
            "last_persist_error": None,
        },
        {
            "record_store_configured": True,
            "autosave": "private",
            "last_persist_error": None,
        },
        {
            "record_store_configured": True,
            "autosave": True,
            "last_persist_error": {"private": "error"},
        },
    ],
)
def test_missing_or_malformed_persistence_metadata_stays_unknown(registry, metadata):
    _register(
        registry,
        SimpleNamespace(
            get_status=lambda: {
                "available": True,
                "cycle_count": 0,
                "recent_cycles": [],
                "service": metadata,
            }
        ),
    )
    maintenance = collect_runtime_ui_system_status()["maintenance"]
    assert maintenance["metrics"]["persistence_state"] == "unknown"
    assert "private" not in str(maintenance)


@pytest.mark.parametrize(
    "restore", [{"load_failed": True}, {"last_load_error": "private-load-error"}]
)
def test_known_restore_failure_degrades_even_without_a_write_error(registry, restore):
    _register(
        registry,
        SimpleNamespace(
            get_status=lambda: {
                "available": True,
                "cycle_count": 0,
                "recent_cycles": [],
                "service": {
                    "record_store_configured": True,
                    "autosave": True,
                    "last_persist_error": None,
                    **restore,
                },
            }
        ),
    )
    maintenance = collect_runtime_ui_system_status()["maintenance"]
    assert maintenance["status"] == "degraded"
    assert maintenance["metrics"]["persistence_state"] == "error"
    assert "private" not in str(maintenance)
