"""Observation requests must survive startup, coordination, and execution."""

# Standard library imports
import asyncio
import logging
import time
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis import audit_trace_layer
from Aetherra.homeostasis import homeostasis_integration as integration
from Aetherra.homeostasis import system_supervisor as supervisor_module
from Aetherra.homeostasis.autonomous_error_corrector import AutonomousErrorCorrector
from Aetherra.homeostasis.homeostasis_actuators import HomeostasisActuators
from Aetherra.homeostasis.homeostasis_core import (
    ActionPriority,
    ControlAction,
    ControllerMode,
    HomeostasisController,
)
from Aetherra.homeostasis.stability_metrics import StabilityMetrics
from Aetherra.homeostasis.system_supervisor import (
    ServiceCriticality,
    ServiceHealth,
    ServiceStatus,
    SystemRunlevel,
    SystemSupervisor,
)


@pytest.fixture
def orchestrator(monkeypatch, tmp_path):
    # Keep audit/policy files and external service effects out of the workspace.
    config_dir = Path("Aetherra/homeostasis/configs").resolve()
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", raising=False)
    monkeypatch.delenv("AETHERRA_HOMEOSTASIS_MODE", raising=False)
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.setattr(audit_trace_layer, "_audit_layer_instance", None)
    instance = integration.HomeostasisOrchestrator(str(config_dir))
    instance.actuators = HomeostasisActuators(
        str(config_dir / "homeostasis_policy.yaml")
    )
    instance.controller = HomeostasisController(
        metrics=StabilityMetrics(str(config_dir / "setpoints.yaml")),
        actuators=instance.actuators,
        config_path=str(config_dir / "setpoints.yaml"),
        policy_path=str(config_dir / "homeostasis_policy.yaml"),
    )
    return instance


def _action():
    return ControlAction(
        action_type="increase_plugin_timeouts",
        target_service="plugin_manager",
        parameters={"multiplier": 2.0},
        priority=ActionPriority.HIGH,
        timestamp=time.time(),
        controller_name="plugin_health",
        reason="Plugin latency exceeded its threshold",
    )


@pytest.mark.parametrize(
    ("settings", "expected"),
    [
        ({"AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "1"}, "observe_only"),
        ({"AETHERRA_HOMEOSTASIS_MODE": "observe_only"}, "observe_only"),
        (
            {
                "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "true",
                "AETHERRA_HOMEOSTASIS_MODE": "active",
            },
            "observe_only",
        ),
        ({}, "active"),
    ],
)
@pytest.mark.parametrize("entry_point", ["components", "controller"])
def test_real_start_honors_observation_request(
    orchestrator, monkeypatch, settings, expected, entry_point
):
    for key, value in settings.items():
        monkeypatch.setenv(key, value)

    observed_modes = []

    async def observe_first_control_step():
        observed_modes.append(orchestrator.controller.mode.value)
        orchestrator.controller.stop()

    # Exercise the real start and action-dispatch methods for one bounded cycle.
    monkeypatch.setattr(orchestrator.controller, "step", observe_first_control_step)
    orchestrator.controller.control_interval = 0

    async def run():
        if entry_point == "components":
            await orchestrator._start_components()
            await asyncio.gather(*orchestrator.background_tasks)
        else:
            await orchestrator.controller.start()

    asyncio.run(run())
    assert observed_modes == [expected]
    assert orchestrator.controller.get_controller_status()["mode"] == expected


@pytest.mark.parametrize("runlevel", ["ONLINE", "FAILED", "DEGRADED", "OFFLINE"])
def test_coordination_preserves_requested_observation(
    orchestrator, monkeypatch, runlevel
):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    orchestrator.supervisor = SystemSupervisor(
        str(Path(orchestrator.config_dir) / "setpoints.yaml")
    )
    orchestrator.supervisor.current_runlevel = SystemRunlevel(runlevel)
    orchestrator.running = True

    async def finish_cycle(_delay):
        raise asyncio.CancelledError

    monkeypatch.setattr(integration.asyncio, "sleep", finish_cycle)
    asyncio.run(orchestrator._coordination_loop())
    assert orchestrator.controller.get_controller_status()["mode"] == "observe_only"


@pytest.mark.parametrize(
    "mode",
    [ControllerMode.ACTIVE, ControllerMode.ACTIVE_LIMITED, ControllerMode.EMERGENCY],
)
def test_direct_mode_change_cannot_override_observation(
    orchestrator, monkeypatch, mode
):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "1")
    asyncio.run(orchestrator.set_controller_mode(mode, "Operator mode request"))
    assert orchestrator.controller.get_controller_status()["mode"] == "observe_only"


def test_stale_pending_action_is_not_dispatched_while_observing(
    orchestrator, monkeypatch
):
    # A queue entry can outlive the evaluation that produced it.
    dispatched = []

    async def dispatch(action):
        dispatched.append(action)
        return True

    monkeypatch.setattr(orchestrator.actuators, "execute_action_via_kernel", dispatch)
    orchestrator.controller.pending_actions.append(_action())
    results = asyncio.run(orchestrator.controller.execute_pending_actions())
    assert results == []
    assert dispatched == []
    assert orchestrator.controller.get_controller_status()["pending_actions"] == 0
    assert orchestrator.actuators.get_actuator_status()["actions_executed"] == 0


def test_observation_blocks_direct_actuator_mutation(orchestrator, monkeypatch):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "1")
    service = SimpleNamespace(timeout_config=SimpleNamespace(default_timeout=10.0))
    registry = SimpleNamespace(
        services={"plugin_manager": SimpleNamespace(instance=service)},
        get_service_info=lambda _name: SimpleNamespace(instance=service),
    )

    async def local_registry():
        return registry

    monkeypatch.setattr(orchestrator.actuators, "_get_service_registry", local_registry)
    result = asyncio.run(orchestrator.actuators.execute_action(_action()))
    assert result is False
    assert service.timeout_config.default_timeout == 10.0
    assert orchestrator.actuators.get_actuator_status()["actions_executed"] == 0


def test_observation_never_queues_kernel_actuation(orchestrator, monkeypatch):
    # Aetherra imports
    import aetherra_kernel_loop

    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    submitted = []

    async def submit(**payload):
        submitted.append(payload)
        return {"ok": True}

    monkeypatch.setattr(
        aetherra_kernel_loop,
        "get_kernel",
        lambda: SimpleNamespace(submit_actuator_action_and_wait=submit),
    )
    result = asyncio.run(orchestrator.actuators.execute_action_via_kernel(_action()))
    assert result is False
    assert submitted == []


def test_observation_detects_errors_without_attempting_fixes(orchestrator, monkeypatch):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    corrector = AutonomousErrorCorrector()
    corrector.running = True
    # This real fix only reports an already handled deprecated import.
    message = "old.module is deprecated; use new.module. Temporarily aliasing"
    record = logging.LogRecord("test", logging.WARNING, __file__, 1, message, (), None)

    async def run():
        corrector.process_log_message(record, message)
        await asyncio.sleep(0)

    asyncio.run(run())
    assert corrector.stats["errors_detected"] == 1
    assert corrector.stats["fixes_attempted"] == 0
    assert corrector.detected_errors[0].fix_attempted is False


def test_observation_does_not_restart_failed_services(orchestrator, monkeypatch):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    supervisor = SystemSupervisor(str(Path(orchestrator.config_dir) / "setpoints.yaml"))
    health = ServiceHealth(
        "critical_test", ServiceStatus.FAILED, ServiceCriticality.CRITICAL, 0.0
    )
    supervisor.service_health = {"critical_test": health}
    service = SimpleNamespace(restarts=0)

    async def restart():
        service.restarts += 1

    service.restart = restart

    async def registry():
        return SimpleNamespace(
            get_service_info=lambda _name: SimpleNamespace(instance=service)
        )

    async def no_delay(_delay):
        return None

    monkeypatch.setattr(supervisor_module, "get_service_registry", registry)
    monkeypatch.setattr(supervisor_module.asyncio, "sleep", no_delay)
    asyncio.run(supervisor._manage_service_recovery())
    assert service.restarts == 0
    assert health.restart_count == 0


def test_status_reports_effective_mode_and_attempts(orchestrator, monkeypatch):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "1")
    status = asyncio.run(orchestrator.get_system_health_status())
    assert status["homeostasis"]["observe_only_requested"] is True
    assert status["controller"]["mode"] == "observe_only"
    assert status["actuators"]["actions_attempted"] == 0


@pytest.mark.parametrize("observe_only", [True, False])
def test_watchdog_restarts_components_only_when_recovery_enabled(
    orchestrator, monkeypatch, observe_only
):
    if observe_only:
        monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    lifecycle = []

    async def stop_components():
        lifecycle.append("stop")

    async def start_components():
        lifecycle.append("start")

    async def no_delay(_delay):
        return None

    # Replace process/thread lifecycle at the boundary, keeping watchdog logic real.
    monkeypatch.setattr(orchestrator, "stop", stop_components)
    monkeypatch.setattr(orchestrator, "start", start_components)
    monkeypatch.setattr(integration.asyncio, "sleep", no_delay)
    watchdog = integration.HomeostasisWatchdog(orchestrator)
    asyncio.run(watchdog._restart_orchestrator(orchestrator))
    assert lifecycle == ([] if observe_only else ["stop", "start"])


@pytest.mark.parametrize("observe_only", [True, False])
def test_scheduler_restarts_stopped_components_only_when_recovery_enabled(
    orchestrator, monkeypatch, observe_only
):
    if observe_only:
        monkeypatch.setenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "1")

    async def start_components():
        orchestrator.running = True

    monkeypatch.setattr(orchestrator, "start", start_components)
    asyncio.run(orchestrator._scheduler_heartbeat())
    assert orchestrator.running is (not observe_only)


def test_observation_preserves_preexisting_rollback_history(orchestrator, monkeypatch):
    service = SimpleNamespace(timeout_config=SimpleNamespace(default_timeout=10.0))
    registry = SimpleNamespace(
        services={"plugin_manager": SimpleNamespace(instance=service)},
        get_service_info=lambda _name: SimpleNamespace(instance=service),
    )

    async def local_registry():
        return registry

    monkeypatch.setattr(orchestrator.actuators, "_get_service_registry", local_registry)
    assert asyncio.run(orchestrator.actuators.execute_action(_action())) is True
    assert service.timeout_config.default_timeout == 20.0

    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    result = asyncio.run(orchestrator.actuators.rollback_last_action())
    assert result.success is False
    assert service.timeout_config.default_timeout == 20.0
    assert (
        orchestrator.actuators.get_actuator_status()["rollback_actions_available"] == 1
    )


def test_observation_can_restart_watchdog_monitoring(orchestrator, monkeypatch):
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_MODE", "observe_only")
    monitor_state = SimpleNamespace(running=False)

    def stop_monitor():
        monitor_state.running = False

    def start_monitor():
        monitor_state.running = True

    async def no_delay(_delay):
        return None

    # Only replace thread creation; exercise the actual watchdog restart path.
    orchestrator.watchdog = integration.HomeostasisWatchdog(orchestrator)
    monkeypatch.setattr(orchestrator.watchdog, "stop", stop_monitor)
    monkeypatch.setattr(orchestrator.watchdog, "start", start_monitor)
    monkeypatch.setattr(integration.asyncio, "sleep", no_delay)
    asyncio.run(orchestrator._restart_watchdog())
    assert monitor_state.running is True
