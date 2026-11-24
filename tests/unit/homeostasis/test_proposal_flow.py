"""The normal Homeostasis bridge may create review records, never execute them."""

# Standard library imports
import asyncio
import contextlib
import copy
import json
import time
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_service_registry as registry_module
from Aetherra.aetherra_core.engine.self_improvement_engine import SelfImprovementEngine
from Aetherra.homeostasis.homeostasis_integration import ContinuousValidator
from Aetherra.homeostasis.observation import build_observation_report
from Aetherra.homeostasis.self_improvement_metrics_bridge import (
    SelfImprovementMetricsBridge,
)
from Aetherra.homeostasis.stability_metrics import MetricSnapshot, StabilityMetrics
from Aetherra.maintenance import MaintenanceDecision, MaintenanceService


@pytest.fixture
def isolated_runtime(monkeypatch, tmp_path):
    config_dir = Path(__file__).resolve().parents[3] / "Aetherra/homeostasis/configs"
    monkeypatch.chdir(tmp_path)
    for key, value in {
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(tmp_path / "policy"),
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "1",
        "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT": "1",
        "AETHERRA_SELFINC_ENABLED": "0",
        "AETHERRA_REGISTRY_URL": "",
        "AETHERRA_SKIP_DOTENV": "1",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    registry = registry_module.AetherraServiceRegistry()
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    metrics = StabilityMetrics(str(config_dir / "setpoints.yaml"))
    metrics.current_snapshot = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=300.0,
        raw_data={"measured_metrics": ["memory_rtt"]},
    )
    controller = SimpleNamespace(
        setpoints=metrics.setpoints,
        get_controller_status=lambda: {
            "mode": "observe_only",
            "running": True,
            "pending_actions": 0,
            "stats": {"actions_executed": 7},
        },
        get_control_loop_status=lambda: {},
    )
    homeostasis = SimpleNamespace(
        metrics=metrics,
        controller=controller,
        supervisor=None,
        actuators=None,
        validator=None,
        error_corrector=None,
    )
    return registry, homeostasis


def _observation():
    return build_observation_report(
        metrics_snapshot={"timestamp": time.time(), "memory_rtt": 300.0},
        controller_status={"mode": "observe_only", "running": True},
        setpoints={
            "core_metrics": {
                "memory_rtt": {
                    "target": 50.0,
                    "max_acceptable": 120.0,
                    "critical_threshold": 500.0,
                }
            }
        },
    )


async def _load_launcher(registry, tmp_path):
    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    await launcher._load_self_maintenance_systems(
        {
            "self_improvement_db": str(tmp_path / "self_improvement.db"),
        }
    )
    await launcher.systems["self_improvement"].impl.stop_improvement_cycle()
    if launcher._improvement_telemetry_task:
        launcher._improvement_telemetry_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await launcher._improvement_telemetry_task
    await launcher._load_maintenance_system({"maintenance_enabled": True})
    return launcher


async def test_bridge_reads_direct_registry_instance_and_real_controller_schema(
    isolated_runtime,
):
    registry, homeostasis = isolated_runtime
    assert await registry.register_service("homeostasis_system", homeostasis)
    bridge = SelfImprovementMetricsBridge()
    collected = await bridge._collect_homeostasis_metrics(
        registry.get_service("homeostasis_system")
    )
    assert collected["memory_rtt"]["value"] == 300.0
    assert collected["controller_active"]["value"] == 0.0
    assert collected["actions_executed"]["value"] == 7.0


async def test_normal_bridge_routes_only_persisted_proposed_cycles(
    isolated_runtime, tmp_path
):
    registry, homeostasis = isolated_runtime
    launcher = await _load_launcher(registry, tmp_path)
    assert await registry.register_service("homeostasis_system", homeostasis)
    maintenance = launcher.systems["maintenance"]
    engine = launcher.systems["self_improvement"].impl
    before_executed = launcher.systems["self_incorporation"].metrics.get(
        "proposals_executed", 0
    )

    await SelfImprovementMetricsBridge()._forward_metrics()

    records = maintenance.export_records()
    assert records, "live observation must reach the existing Maintenance store"
    assert len(records) <= 8
    for record in records:
        assert record["status"] == "proposed"
        assert record["proposal"]["source"] == "self_improvement"
        assert record["proposal"]["approval_required"] is True
        assert engine.get_proposal(record["proposal"]["proposal_id"]) is not None
        assert record["observations"][0]["source"] == "homeostasis"
        assert record["diagnosis"]["source"] == "self_improvement"
        assert record["guardian_decision"] is None
        assert record["security_enforced"] is False
        assert record["execution"] is None
        assert record["verification"] is None
        assert maintenance.get_cycle(record["cycle_id"]).can_execute() is False
    reloaded = MaintenanceService.with_default_store(tmp_path)
    assert reloaded.export_records() == records
    assert engine.autonomous_implementation_enabled is False
    assert (
        launcher.systems["self_incorporation"].metrics.get("proposals_executed", 0)
        == before_executed
    )
    assert engine.get_improvement_status()["homeostasis_flow"]["status"] == "proposed"


@pytest.mark.parametrize("validator_state", ["empty", "fallback"])
async def test_validator_defaults_never_become_measured_metric_history(
    isolated_runtime, tmp_path, validator_state
):
    registry, homeostasis = isolated_runtime
    launcher = await _load_launcher(registry, tmp_path)
    assert await registry.register_service("homeostasis_system", homeostasis)
    validator = ContinuousValidator(homeostasis)
    homeostasis.validator = validator
    if validator_state == "fallback":
        scores = await validator._calculate_effectiveness_scores({})
        validator._update_effectiveness_metrics(scores)
    summary = validator.get_validation_summary()
    assert summary["effectiveness_metrics"]["response_time_improvement"]["current"] == (
        0.0 if validator_state == "empty" else 0.5
    )

    # An unrelated fresh measurement cannot establish validator provenance.
    snapshot = homeostasis.metrics.current_snapshot
    snapshot.plugin_load_success = 0.0
    snapshot.raw_data["measured_metrics"].append("plugin_load_success")
    bridge = SelfImprovementMetricsBridge()
    await bridge._forward_metrics()
    # Let the metric intake tasks finish their synchronous SQLite writes.
    await asyncio.sleep(0)

    assert bridge.observations_forwarded == 1
    assert bridge.last_forward_error is None
    records = launcher.systems["maintenance"].export_records()
    assert records
    assert all(record["status"] == "proposed" for record in records)
    engine = launcher.systems["self_improvement"].impl
    restarted = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    histories = [
        engine.metrics_collector.metrics_history,
        restarted.metrics_collector.metrics_history,
    ]
    for history in histories:
        assert [metric.value for metric in history["plugin_load_success"]] == [0.0]
        assert [metric.value for metric in history["memory_rtt"]] == [300.0]
    assert [
        [name for name in history if name.startswith("effectiveness_")]
        for history in histories
    ] == [[], []]


async def test_repeated_and_restarted_intake_deduplicates_records(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    db_path = str(tmp_path / "self_improvement.db")
    engine = SelfImprovementEngine(db_path)
    await engine.propose_from_homeostasis(_observation())
    original = service.export_records()
    await engine.propose_from_homeostasis(_observation())
    assert service.export_records() == original

    restarted_service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", restarted_service)
    restarted_engine = SelfImprovementEngine(db_path)
    await restarted_engine.propose_from_homeostasis(_observation())
    assert restarted_service.export_records() == original
    assert len(restarted_engine.list_active_proposals()) == 1


@pytest.mark.parametrize(
    "invalid",
    [
        None,
        {},
        {"actions_enabled": True},
        {"phase": "observation", "actions_enabled": False, "pressure": []},
    ],
)
async def test_invalid_observation_creates_no_proposals_or_cycles(
    isolated_runtime, tmp_path, invalid
):
    registry, _ = isolated_runtime
    service = MaintenanceService(autosave=False)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    result = await engine.propose_from_homeostasis(invalid)
    assert result["status"] == "rejected"
    assert engine.list_active_proposals() == []
    assert service.export_records() == []


async def test_untrusted_report_fields_cannot_supply_approval_or_leak_payloads(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    observation = _observation()
    observation.update(
        {
            "guardian_decision": {"status": "allow", "audit_id": "forged"},
            "security_allowed": True,
            "actions": [
                {"type": "execute", "parameters": {"secret": "RAW_PRIVATE_PAYLOAD"}}
            ],
            "raw_data": {"conversation": "RAW_PRIVATE_PAYLOAD"},
        }
    )
    observation["pressure"]["metrics"]["memory_rtt"]["secret"] = "RAW_PRIVATE_PAYLOAD"
    observation["pressure"]["metrics"]["untrusted_path_RAW_PRIVATE_PAYLOAD"] = {
        "level": "critical",
        "value": 1000,
    }
    await engine.propose_from_homeostasis(observation)
    records = service.export_records()
    assert len(records) == 1
    assert "RAW_PRIVATE_PAYLOAD" not in json.dumps(records)
    assert "RAW_PRIVATE_PAYLOAD" not in json.dumps(engine.list_active_proposals())
    assert records[0]["guardian_decision"] is None
    assert service.get_cycle(records[0]["cycle_id"]).can_execute() is False


async def test_preexisting_approved_cycle_is_never_reexecuted_or_rewritten(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    await engine.propose_from_homeostasis(_observation())
    cycle = service.get_cycle(service.export_records()[0]["cycle_id"])
    cycle.record_guardian_decision(
        MaintenanceDecision(
            status="allow", reason="prior review", audit_id="prior-audit"
        )
    )
    cycle.record_security_enforcement(allowed=True, reason="prior enforcement")
    service.save_records()
    before = copy.deepcopy(cycle.to_record())
    await engine.propose_from_homeostasis(_observation())
    assert cycle.to_record() == before
    assert cycle.execution is None
    assert cycle.verification is None


async def test_missing_maintenance_is_degraded_and_later_routes(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    result = await engine.propose_from_homeostasis(_observation())
    assert result["status"] == "degraded"
    assert result["reason"] == "maintenance_unavailable"
    assert len(engine.list_active_proposals()) == 1
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    await engine.propose_from_homeostasis(_observation())
    assert len(service.export_records()) == 1


async def test_failed_registry_delivery_is_not_counted_as_forwarded(
    isolated_runtime, monkeypatch
):
    registry, homeostasis = isolated_runtime
    assert await registry.register_service("homeostasis_system", homeostasis)
    assert await registry.register_service("self_improvement_engine", SimpleNamespace())
    bridge = SelfImprovementMetricsBridge()
    # Exercise the real registry's no-handler rejection.
    await bridge._forward_metrics()
    assert bridge.metrics_forwarded == 0
    assert bridge.forward_failures > 0


async def test_persistence_failure_is_visible_and_retryable(
    isolated_runtime, tmp_path, monkeypatch
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    original_export = type(service.record_store).export_from

    def fail_export(self, coordinator):
        raise OSError("private file path must not enter flow status")

    monkeypatch.setattr(type(service.record_store), "export_from", fail_export)
    result = await engine.propose_from_homeostasis(_observation())
    assert result["status"] == "degraded"
    assert result["reason"] == "maintenance_persistence_failed"
    assert "private file path" not in json.dumps(
        engine.get_improvement_status()["homeostasis_flow"]
    )
    monkeypatch.setattr(type(service.record_store), "export_from", original_export)
    await engine.propose_from_homeostasis(_observation())
    assert (
        MaintenanceService.with_default_store(tmp_path).export_records()
        == service.export_records()
    )


@pytest.mark.parametrize(
    "damage",
    ["actions_enabled", "stale", "nonfinite", "invalid_level", "invalid_direction"],
)
async def test_unsafe_or_malformed_report_never_advances_intake(
    isolated_runtime, tmp_path, damage
):
    registry, _ = isolated_runtime
    service = MaintenanceService(autosave=False)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    observation = _observation()
    if damage == "actions_enabled":
        observation["actions_enabled"] = True
    elif damage == "stale":
        observation["metrics"]["sample_timestamp"] = time.time() - 600
    elif damage == "nonfinite":
        observation["pressure"]["metrics"]["memory_rtt"]["value"] = float("nan")
    elif damage == "invalid_level":
        observation["pressure"]["metrics"]["memory_rtt"]["level"] = ["critical"]
    else:
        observation["pressure"]["metrics"]["memory_rtt"]["direction"] = {
            "private": "payload"
        }
    result = await engine.propose_from_homeostasis(observation)
    assert result["status"] == "rejected"
    assert result["observations_received"] == 0
    assert engine.list_active_proposals() == []
    assert service.export_records() == []


async def test_nominal_observation_does_not_fabricate_proposals(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    observation = build_observation_report(
        metrics_snapshot={"timestamp": time.time(), "memory_rtt": 50.0},
        setpoints={
            "core_metrics": {"memory_rtt": {"target": 50.0, "max_acceptable": 120.0}}
        },
    )
    result = await engine.propose_from_homeostasis(observation)
    assert result["status"] == "nominal"
    assert engine.list_active_proposals() == []
    assert service.export_records() == []


async def test_distinct_causes_get_distinct_bounded_cycle_records(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    observation = build_observation_report(
        metrics_snapshot={
            "timestamp": time.time(),
            "memory_rtt": 300.0,
            "queue_depth": 120.0,
        },
        setpoints={
            "core_metrics": {
                "memory_rtt": {"target": 50.0, "max_acceptable": 120.0},
                "queue_depth": {"target": 5.0, "max_acceptable": 50.0},
            }
        },
    )
    await engine.propose_from_homeostasis(observation)
    records = service.export_records()
    assert len(records) == 2
    assert len({record["cycle_id"] for record in records}) == 2
    assert {record["proposal"]["target_subsystem"] for record in records} == {
        "memory_system",
        "kernel_system",
    }
    assert all(len(record["proposal"]["evidence"]) <= 11 for record in records)
    assert all(
        len(item) <= 512
        for record in records
        for item in record["proposal"]["evidence"]
    )


async def test_dismissed_proposal_is_not_routed_or_counted_again(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    db_path = str(tmp_path / "self_improvement.db")
    engine = SelfImprovementEngine(db_path)
    await engine.propose_from_homeostasis(_observation())
    proposal_id = service.export_records()[0]["proposal"]["proposal_id"]
    await engine.dismiss_proposal(
        proposal_id, reason="operator reviewed", actor="operator"
    )
    restarted = SelfImprovementEngine(db_path)
    result = await restarted.propose_from_homeostasis(_observation())
    assert result["status"] == "no_reviewable_proposals"
    assert result["proposals_generated"] == 0
    assert restarted.list_active_proposals() == []
    assert len(service.export_records()) == 1


async def test_failed_proposal_persistence_is_retried_before_routing(
    isolated_runtime, tmp_path, monkeypatch
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    real_store = engine._store_proposal

    async def failed_store(proposal):
        raise OSError("temporary database failure")

    monkeypatch.setattr(engine, "_store_proposal", failed_store)
    result = await engine.propose_from_homeostasis(_observation())
    assert result["status"] == "degraded"
    assert service.export_records() == []
    monkeypatch.setattr(engine, "_store_proposal", real_store)
    result = await engine.propose_from_homeostasis(_observation())
    assert result["status"] == "proposed"
    assert len(service.export_records()) == 1
    assert engine.list_active_proposals()[0]["occurrence_count"] == 1


async def test_failed_refresh_retries_durable_evidence_before_routing(
    isolated_runtime, tmp_path, monkeypatch
):
    registry, _ = isolated_runtime
    db_path = str(tmp_path / "self_improvement.db")
    engine = SelfImprovementEngine(db_path)
    first = await engine.propose_from_homeostasis(_observation())
    assert first["reason"] == "maintenance_unavailable"
    assert first["proposals_generated"] == 1
    original = engine.list_active_proposals()[0]

    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    updated = _observation()
    updated["metrics"]["values"]["memory_rtt"] = 400.0
    updated["pressure"]["metrics"]["memory_rtt"]["value"] = 400.0
    real_store = engine._store_proposal

    async def failed_store(proposal):
        raise OSError("temporary database failure during refresh")

    monkeypatch.setattr(engine, "_store_proposal", failed_store)
    failed = await engine.propose_from_homeostasis(updated)
    assert failed["status"] == "degraded"
    assert service.export_records() == []
    assert (
        engine._load_proposal_from_db(original["proposal_id"]).evidence
        == original["evidence"]
    )

    monkeypatch.setattr(engine, "_store_proposal", real_store)
    retried = await engine.propose_from_homeostasis(updated)
    assert retried["status"] == "proposed"
    assert retried["proposals_generated"] == 1
    assert retried["cycles_routed"] == 1
    records = MaintenanceService.with_default_store(tmp_path).export_records()
    assert len(records) == 1
    record = records[0]
    persisted = SelfImprovementEngine(db_path).get_proposal(original["proposal_id"])
    assert persisted is not None
    proposal_evidence = [
        json.loads(item) for item in persisted["evidence"] if item.startswith("{")
    ]
    assert [item["value"] for item in proposal_evidence] == [400.0]
    assert persisted["occurrence_count"] == 2
    assert list(record["proposal"]["evidence"]) == persisted["evidence"]
    assert record["observations"][0]["details"]["evidence"] == proposal_evidence
    assert record["diagnosis"]["details"]["evidence"] == proposal_evidence
    assert record["status"] == "proposed"
    assert record["guardian_decision"] is None
    assert record["security_enforced"] is False
    assert record["execution"] is None
    assert record["verification"] is None


async def test_bridge_omits_unknown_and_nonfinite_metrics(isolated_runtime):
    _, homeostasis = isolated_runtime
    homeostasis.metrics.current_snapshot = SimpleNamespace(
        timestamp=time.time(),
        memory_rtt=300.0,
        task_latency=float("nan"),
        raw_data={"measured_metrics": ["memory_rtt", "task_latency"]},
    )
    homeostasis.controller.get_controller_status = lambda: {}
    homeostasis.supervisor = SimpleNamespace(get_system_health=lambda: {})
    homeostasis.error_corrector = SimpleNamespace(get_status=lambda: {"statistics": {}})
    collected = await SelfImprovementMetricsBridge()._collect_homeostasis_metrics(
        homeostasis
    )
    assert collected == {
        "memory_rtt": {
            "value": 300.0,
            "unit": "milliseconds",
            "context": {"source": "homeostasis"},
        }
    }


@pytest.mark.parametrize("persist_mode", ["no_store", "autosave_disabled"])
async def test_in_memory_cycle_is_not_reported_as_durable_proposed(
    isolated_runtime, tmp_path, persist_mode
):
    registry, _ = isolated_runtime
    service = (
        MaintenanceService()
        if persist_mode == "no_store"
        else MaintenanceService.with_default_store(tmp_path, autosave=False)
    )
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    result = await engine.propose_from_homeostasis(_observation())
    assert result["status"] == "degraded"
    assert result["reason"] == "maintenance_persistence_unavailable"
    assert len(service.export_records()) == 1
    assert not (tmp_path / "artifacts/maintenance/maintenance_cycles.jsonl").exists()


async def test_observation_proposal_does_not_claim_validated_implementation_or_rollback(
    isolated_runtime, tmp_path
):
    registry, _ = isolated_runtime
    service = MaintenanceService.with_default_store(tmp_path)
    assert await registry.register_service("maintenance_system", service)
    engine = SelfImprovementEngine(str(tmp_path / "self_improvement.db"))
    await engine.propose_from_homeostasis(_observation())
    proposal = engine.list_active_proposals()[0]
    assert proposal["simulation"]["estimate_only"] is True
    assert proposal["simulation"]["rollback_available"] is False
    assert proposal["simulation"]["testable"] is False
    assert proposal["readiness_status"] == "needs_evidence"
    assert "rollback_not_validated" in proposal["readiness_reasons"]
    assert "validation_not_run" in proposal["readiness_reasons"]


def test_observation_collection_never_copies_private_raw_runtime_data(isolated_runtime):
    _, homeostasis = isolated_runtime

    class PrivateRuntimeData:
        def __deepcopy__(self, memo):
            raise AssertionError("private runtime payload must not be copied")

    homeostasis.metrics.current_snapshot.raw_data["private"] = PrivateRuntimeData()
    report = SelfImprovementMetricsBridge._collect_observation(homeostasis)
    assert report["metrics"]["values"]["memory_rtt"] == 300.0
    assert "private" not in json.dumps(report)


async def test_stale_bridge_snapshot_cannot_become_new_metric_evidence(
    isolated_runtime, tmp_path
):
    registry, homeostasis = isolated_runtime
    launcher = await _load_launcher(registry, tmp_path)
    assert await registry.register_service("homeostasis_system", homeostasis)
    homeostasis.metrics.current_snapshot.timestamp = time.time() - 600
    bridge = SelfImprovementMetricsBridge()
    await bridge._forward_metrics()
    engine = launcher.systems["self_improvement"].impl
    assert not engine.metrics_collector.metrics_history
    assert launcher.systems["maintenance"].export_records() == []
    assert bridge.metrics_forwarded == 0
    assert bridge.observations_forwarded == 0
    assert bridge.last_forward_error == "observation_unavailable"


async def test_default_snapshot_without_measurements_never_creates_pressure_evidence(
    isolated_runtime, tmp_path
):
    registry, homeostasis = isolated_runtime
    launcher = await _load_launcher(registry, tmp_path)
    assert await registry.register_service("homeostasis_system", homeostasis)
    homeostasis.metrics.current_snapshot = MetricSnapshot(timestamp=time.time())
    bridge = SelfImprovementMetricsBridge()
    await bridge._forward_metrics()
    assert SelfImprovementMetricsBridge._collect_observation(homeostasis) is None
    assert not launcher.systems[
        "self_improvement"
    ].impl.metrics_collector.metrics_history
    assert launcher.systems["maintenance"].export_records() == []
    assert bridge.last_forward_error == "observation_unavailable"


def test_observation_contains_only_declared_measurements(isolated_runtime):
    _, homeostasis = isolated_runtime
    report = SelfImprovementMetricsBridge._collect_observation(homeostasis)
    assert report["metrics"]["values"] == {"memory_rtt": 300.0}
    assert set(report["pressure"]["metrics"]) == {"memory_rtt"}


@pytest.mark.parametrize("mapping", [False, True])
@pytest.mark.parametrize("measured", [[], ["memory_rtt"]])
def test_shared_observation_respects_explicit_measurement_metadata(mapping, measured):
    snapshot = MetricSnapshot(
        timestamp=time.time(),
        memory_rtt=300.0,
        raw_data={"measured_metrics": measured},
    )
    report = build_observation_report(
        metrics_snapshot=snapshot.__dict__ if mapping else snapshot,
        setpoints={
            "core_metrics": {
                "memory_rtt": {"target": 50.0, "max_acceptable": 120.0},
                "task_throughput": {"target": 10.0, "min_acceptable": 1.0},
            }
        },
    )
    assert report["metrics"]["values"] == ({"memory_rtt": 300.0} if measured else {})
    assert "task_throughput" not in report["pressure"]["metrics"]
