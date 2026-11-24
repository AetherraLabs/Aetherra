# Standard library imports
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.maintenance import (
    MAINTENANCE_SERVICE_ALIASES,
    MAINTENANCE_SERVICE_NAME,
    MaintenanceCoordinator,
    MaintenanceDecision,
    MaintenanceEvidence,
    MaintenanceExecution,
    MaintenanceProposal,
    MaintenanceRecordStore,
    MaintenanceService,
    MaintenanceVerification,
    maintenance_service_metadata,
    register_maintenance_service,
)


def _proposal() -> MaintenanceProposal:
    return MaintenanceProposal(
        proposal_id="proposal-service-1",
        source="self_improvement",
        target_subsystem="memory",
        issue="memory recall latency elevated",
        proposed_action="optimize memory index",
        expected_benefit="lower recall latency",
        risk_level="medium",
        rollback_plan="restore previous memory index",
    )


def _diagnosis() -> MaintenanceEvidence:
    return MaintenanceEvidence(
        source="self_improvement",
        summary="memory index pressure likely cause",
    )


class _FakeRegistry:
    def __init__(self, *, fail_primary: bool = False):
        self.fail_primary = fail_primary
        self.registrations = []

    async def register_service(self, name, instance, metadata=None):
        self.registrations.append((name, instance, metadata or {}))
        return not (name == MAINTENANCE_SERVICE_NAME and self.fail_primary)


def test_service_status_wraps_coordinator_without_claiming_extra_authority():
    service = MaintenanceService(autosave=False)

    status = service.get_status()

    assert status["available"] is True
    assert status["coordinator"] == "maintenance"
    assert status["contract"]["authority_ownership"]["maintenance"] == [
        "coordinate",
        "route",
        "record_outcome",
    ]
    assert status["service"]["available"] is True
    assert status["service"]["record_store_configured"] is False


def test_maintenance_service_metadata_declares_authority_boundaries():
    metadata = maintenance_service_metadata()

    assert metadata["authority"] == "coordinate_route_record_outcome"
    assert metadata["authority_boundaries"]["approve"] == "guardian"
    assert metadata["authority_boundaries"]["enforce"] == "security"
    assert metadata["authority_boundaries"]["execute"] == "self_incorporation"
    assert metadata["authority_boundaries"]["record_outcome"] == "maintenance"
    assert metadata["endpoints"]["status"] == "/api/maintenance/status"


def test_service_routes_and_records_outcome_through_coordinator(tmp_path):
    service = MaintenanceService(
        record_store=MaintenanceRecordStore.default(tmp_path),
        autosave=True,
    )

    cycle = service.route_proposal(
        _proposal(),
        diagnosis=_diagnosis(),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-service-1",
    )
    completed = service.record_outcome(
        cycle.cycle_id,
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="memory index optimized",
            rollback_token="rb-service-1",
        ),
        verification=MaintenanceVerification(
            verifier="homeostasis",
            status="improved",
            summary="latency recovered",
        ),
        learning_record={"outcome": "improved"},
    )

    assert completed is cycle
    assert completed.learning_record["outcome"] == "improved"
    assert service.record_store.file_path.exists()


def test_service_loads_existing_records_on_startup(tmp_path):
    first = MaintenanceService(
        record_store=MaintenanceRecordStore.default(tmp_path),
        autosave=True,
    )
    first.route_proposal(
        _proposal(),
        diagnosis=_diagnosis(),
        guardian_decision=MaintenanceDecision(
            status="allow_limited",
            reason="bounded maintenance proposal",
        ),
        security_allowed=True,
        security_reason="capabilities satisfied",
        cycle_id="maint-service-load",
    )

    second = MaintenanceService(
        record_store=MaintenanceRecordStore.default(tmp_path),
        autoload=True,
        autosave=False,
    )

    assert second.get_cycle("maint-service-load").can_execute() is True
    assert second.get_status()["service"]["loaded_records"] == 1


def test_service_returns_none_for_unknown_outcome_cycle():
    service = MaintenanceService(autosave=False)

    result = service.record_outcome(
        "missing-cycle",
        execution=MaintenanceExecution(
            executor="self_incorporation",
            status="applied",
            summary="should not be recorded",
        ),
    )

    assert result is None


@pytest.mark.parametrize("failure", ["json", "cycle", "read"])
def test_failed_restore_blocks_saving_until_successful_reload(
    tmp_path, monkeypatch, failure
):
    first = MaintenanceService.with_default_store(tmp_path)
    first.route_proposal(
        _proposal(),
        diagnosis=_diagnosis(),
        guardian_decision=MaintenanceDecision(
            status="deny", reason="preserve prior review", audit_id="audit-before-load"
        ),
        cycle_id="maint-before-load",
    )
    path = first.record_store.file_path
    original = path.read_bytes()
    if failure == "json":
        path.write_bytes(original + b"{invalid json}\n")
    elif failure == "cycle":
        path.write_bytes(original + b'{"cycle_id":"broken","status":"invalid"}\n')
    protected = path.read_bytes()

    with monkeypatch.context() as blocked:
        if failure == "read":
            read_text = Path.read_text

            def unreadable(self, *args, **kwargs):
                if self == path:
                    raise PermissionError("private record path is unreadable")
                return read_text(self, *args, **kwargs)

            blocked.setattr(Path, "read_text", unreadable)
        service = MaintenanceService.with_default_store(tmp_path)
        assert service.save_records() is False
        service.create_cycle("unpersisted-cycle")
        assert path.read_bytes() == protected
        state = service.get_status()["service"]
        assert state["load_failed"] is True
        assert state["last_load_error"] == (
            "PermissionError" if failure == "read" else "ValueError"
        )
        assert state["last_persist_error"] == state["last_load_error"]
        if failure == "cycle":
            restored_cycle = service.get_cycle("maint-before-load")
            assert restored_cycle.guardian_decision.audit_id == "audit-before-load"

    path.write_bytes(original)
    assert service.load_records() == 1
    state = service.get_status()["service"]
    assert state["load_failed"] is False
    assert state["last_load_error"] is None
    assert state["last_persist_error"] is None
    assert service.get_cycle("maint-before-load").guardian_decision.status == "deny"
    assert service.save_records() is True
    restored = MaintenanceService.with_default_store(tmp_path)
    assert restored.get_cycle("maint-before-load").guardian_decision.audit_id == (
        "audit-before-load"
    )


@pytest.mark.parametrize("existing_empty", [False, True])
def test_missing_or_empty_store_allows_first_save(tmp_path, existing_empty):
    store = MaintenanceRecordStore.default(tmp_path)
    if existing_empty:
        store.file_path.parent.mkdir(parents=True)
        store.file_path.write_bytes(b"")
    service = MaintenanceService(record_store=store)
    service.create_cycle("first-cycle")
    assert service.get_status()["service"]["load_failed"] is False
    assert MaintenanceService(record_store=store).get_cycle("first-cycle") is not None


def test_service_can_use_supplied_coordinator():
    coordinator = MaintenanceCoordinator()
    service = MaintenanceService(coordinator=coordinator, autosave=False)

    cycle = service.create_cycle("maint-supplied-coordinator")

    assert coordinator.get_cycle("maint-supplied-coordinator") is cycle


@pytest.mark.asyncio
async def test_register_maintenance_service_registers_primary_and_alias(tmp_path):
    registry = _FakeRegistry()

    service = await register_maintenance_service(
        registry=registry,
        project_root=tmp_path,
    )

    names = [name for name, _instance, _metadata in registry.registrations]
    assert isinstance(service, MaintenanceService)
    assert names[0] == MAINTENANCE_SERVICE_NAME
    assert set(MAINTENANCE_SERVICE_ALIASES).issubset(set(names))
    assert registry.registrations[0][2]["authority"] == (
        "coordinate_route_record_outcome"
    )


@pytest.mark.asyncio
async def test_register_maintenance_service_can_skip_aliases(tmp_path):
    registry = _FakeRegistry()

    await register_maintenance_service(
        registry=registry,
        project_root=tmp_path,
        register_aliases=False,
    )

    assert [name for name, _instance, _metadata in registry.registrations] == [
        MAINTENANCE_SERVICE_NAME
    ]


@pytest.mark.asyncio
async def test_register_maintenance_service_raises_when_primary_registration_fails(
    tmp_path,
):
    registry = _FakeRegistry(fail_primary=True)

    with pytest.raises(RuntimeError, match="failed_to_register_maintenance_service"):
        await register_maintenance_service(registry=registry, project_root=tmp_path)
