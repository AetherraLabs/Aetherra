"""Hub status and controls must address the launcher's initialized homeostasis."""

# Standard library imports
import asyncio
import json
import shutil
from pathlib import Path

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import Aetherra.homeostasis.homeostasis_integration as integration
import aetherra_service_registry as registry_module
from Aetherra.homeostasis import audit_trace_layer, stability_metrics, system_supervisor
from Aetherra.homeostasis.homeostasis_core import ControllerMode
from aetherra_hub.blueprints.homeostasis import bp


@pytest.fixture(params=[False, True], ids=["launcher-first", "hub-first"])
def launched_homeostasis(request, monkeypatch, tmp_path):
    # Initialize real components in an isolated workspace without starting loops.
    config_dir = Path(__file__).resolve().parents[3] / "Aetherra/homeostasis/configs"
    shutil.copytree(config_dir, tmp_path / "Aetherra/homeostasis/configs")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_HUB_CONTROL_TOKEN", "ownership-test-token")
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    policy_dir = tmp_path / "policy"
    policy_dir.mkdir()
    (policy_dir / "capabilities.json").write_text(
        json.dumps({"allow": {"homeostasis": ["homeostasis:control"]}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(integration, "_homeostasis_instance", None)
    monkeypatch.setattr(audit_trace_layer, "_audit_layer_instance", None)
    monkeypatch.setattr(stability_metrics, "_stability_metrics", None)
    monkeypatch.setattr(system_supervisor, "_system_supervisor", None)
    registry = registry_module.AetherraServiceRegistry()
    monkeypatch.setattr(registry_module, "_service_registry", registry)

    # Aetherra imports
    from aetherra_os_launcher import AetherraOSLauncher

    app = Flask(__name__)
    app.register_blueprint(bp)
    client = app.test_client()
    if request.param:
        assert (
            client.get("/api/homeostasis/status").get_json()["orchestrator"][
                "initialized"
            ]
            is False
        )

    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    asyncio.run(launcher._load_homeostasis_system({}))
    return launcher, client, registry


def test_hub_reports_the_homeostasis_initialized_by_launcher(launched_homeostasis):
    launcher, client, registry = launched_homeostasis
    response = client.get("/api/homeostasis/status")

    assert response.status_code == 200
    body = response.get_json()
    assert body["orchestrator"]["initialized"] is True
    assert body["health"]["homeostasis"]["initialized"] is True
    assert body["controller"]["mode"] == "observe_only"
    runtime = launcher.systems["homeostasis"]
    assert registry.get_service("homeostasis_system") is runtime
    assert registry.get_service("aetherra_homeostasis") is runtime
    assert integration.get_homeostasis_orchestrator() is runtime


def test_hub_mode_change_reaches_launcher_controller(launched_homeostasis):
    launcher, client, _registry = launched_homeostasis
    runtime = launcher.systems["homeostasis"]
    response = client.post(
        "/api/homeostasis/mode",
        json={"mode": "disabled", "reason": "Operator paused homeostasis"},
        headers={"X-Aetherra-Token": "ownership-test-token"},
    )

    assert response.status_code == 200
    assert runtime.controller.mode is ControllerMode.DISABLED
    assert (
        client.get("/api/homeostasis/status").get_json()["controller"]["mode"]
        == "disabled"
    )

    # Repeated loading must retain the initialized controller and its control state.
    asyncio.run(launcher._load_homeostasis_system({}))
    assert launcher.systems["homeostasis"] is runtime
    assert runtime.controller.mode is ControllerMode.DISABLED


def test_hub_reports_real_supervisor_runlevel_transitions(launched_homeostasis):
    launcher, client, _registry = launched_homeostasis
    supervisor = launcher.systems["homeostasis"].supervisor
    asyncio.run(
        supervisor._transition_runlevel(
            system_supervisor.SystemRunlevel.BOOTING, "Starting homeostasis"
        )
    )
    supervisor._update_stability_metrics()

    response = client.get("/api/homeostasis/status")

    assert response.status_code == 200
    body = response.get_json()
    health = body["health"]["system_health"]
    assert body["supervisor"]["current_runlevel"] == "BOOTING"
    assert health["runlevel"] == "BOOTING"
    assert health["stability_metrics"]["runlevel"] == "BOOTING"
    assert health["stability_metrics"]["runlevel_changes"] == 1
    transition = health["recent_transitions"][0]
    assert transition["from_level"] == "OFFLINE"
    assert transition["to_level"] == "BOOTING"
    assert transition["reason"] == "Starting homeostasis"
    assert transition["triggered_by"] == "supervisor"
    assert isinstance(transition["timestamp"], float)
    # Reporting preserves the supervisor's typed internal history.
    assert (
        supervisor.runlevel_history[0].to_level
        is system_supervisor.SystemRunlevel.BOOTING
    )
    assert (
        json.loads(json.dumps(supervisor.get_system_health()))["runlevel"] == "BOOTING"
    )


@pytest.mark.parametrize(
    ("initial_mode", "expected_mode"),
    [
        ("disabled", "disabled"),
        ("active", "observe_only"),
        ("active_limited", "observe_only"),
        ("emergency", "observe_only"),
    ],
)
def test_observation_coordination_respects_hub_controller_mode(
    launched_homeostasis, monkeypatch, initial_mode, expected_mode
):
    launcher, client, _registry = launched_homeostasis
    runtime = launcher.systems["homeostasis"]
    monkeypatch.delenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", raising=False)
    monkeypatch.delenv("AETHERRA_HOMEOSTASIS_MODE", raising=False)
    response = client.post(
        "/api/homeostasis/mode",
        json={"mode": initial_mode, "reason": "Operator mode request"},
        headers={"X-Aetherra-Token": "ownership-test-token"},
    )
    assert response.status_code == 200
    assert runtime.controller.mode.value == initial_mode
    monkeypatch.setenv("AETHERRA_HOMEOSTASIS_OBSERVE_ONLY", "1")

    async def run_coordination_tick():
        runtime.running = True
        task = asyncio.create_task(runtime._coordination_loop())
        try:
            # Let the real coordination loop run until its interval wait.
            await asyncio.sleep(0)
        finally:
            runtime.running = False
            task.cancel()
            await task

    asyncio.run(run_coordination_tick())

    assert runtime.controller.mode.value == expected_mode
    assert (
        client.get("/api/homeostasis/status").get_json()["controller"]["mode"]
        == expected_mode
    )
