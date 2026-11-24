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


def _proposed_service():
    service = MaintenanceService(autosave=False)
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
