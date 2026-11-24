"""Full-launch readiness reflects live core contracts and optional degradation."""

# Standard library imports
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock

# Third party imports
import pytest

# Aetherra imports
from aetherra_service_registry import (
    AetherraServiceRegistry,
    ServiceInfo,
    ServiceStatus,
)
from tests.unit.test_ai_readiness import _ready_status
from tests.unit.test_kernel_readiness_sources import live_status


@pytest.fixture
def launched_core(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_KEEP_MONITOR", "0")
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    # Aetherra imports
    import aetherra_os_launcher as module

    monkeypatch.setattr(module, "_LATEST_BOOT_READINESS", None)
    registry = AetherraServiceRegistry()
    kernel = SimpleNamespace(
        running=True,
        get_status=lambda: {**live_status(), "cycle_count": 5},
        add_task=AsyncMock(),
    )
    engine = SimpleNamespace(
        get_system_status=AsyncMock(
            return_value=_ready_status(
                generation={
                    "status": "configured",
                    "model_selected": True,
                    "check_scope": "configuration_only",
                }
            )
        )
    )
    for name, instance in {
        "memory_system": object(),
        "aetherra_engine": engine,
        "kernel_loop": kernel,
        "aetherra_hub": object(),
    }.items():
        registry._services[name] = ServiceInfo(name, instance, ServiceStatus.HEALTHY)

    class HubReply:
        status = 200

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        def get(self, *args):
            return self

        async def json(self):
            return {"status": "healthy"}

    monkeypatch.setattr("aiohttp.ClientSession", lambda **kwargs: HubReply())
    launcher = module.AetherraOSLauncher.__new__(module.AetherraOSLauncher)
    launcher.service_registry = registry
    launcher.kernel_loop = kernel
    launcher.startup_time = None
    launcher.readiness_report = None
    return launcher, registry, engine


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "name", ["memory_system", "aetherra_engine", "kernel_loop", "aetherra_hub"]
)
@pytest.mark.parametrize(
    "state", ["missing", "starting", "degraded", "failed", "no_instance"]
)
async def test_missing_or_unready_core_never_announces_ready(
    launched_core, name, state
):
    launcher, registry, _engine = launched_core
    if state == "missing":
        del registry._services[name]
    elif state == "no_instance":
        registry._services[name].instance = None
    else:
        registry._services[name].status = ServiceStatus(state)
    report = await launcher._run_startup_readiness_scan({"gui_enabled": False})
    assert report["status"] != "ready"
    assert report["issues"]
    assert "Ready for commands and questions" not in report["message"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "generation", [None, {"status": "unavailable"}, {"status": "not_selected"}]
)
async def test_generation_requires_authoritative_configuration_evidence(
    launched_core, generation
):
    launcher, _registry, engine = launched_core
    status = _ready_status()
    if generation is not None:
        status["generation"] = generation
    engine.get_system_status.return_value = status
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "degraded"
    assert report["core_readiness"]["engine"]["safe_for_requests"] is False


@pytest.mark.asyncio
async def test_ready_core_keeps_optional_failure_visible_without_blocking_chat(
    launched_core,
):
    launcher, registry, engine = launched_core
    registry._services["quantum_cognition"] = ServiceInfo(
        "quantum_cognition", object(), ServiceStatus.DEGRADED
    )
    registry._services["plugin_manager"] = ServiceInfo(
        "plugin_manager", object(), ServiceStatus.STARTING
    )
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "ready"
    assert report["core_readiness"]["engine"]["safe_for_requests"] is True
    assert report["core_readiness"]["kernel"]["safe_to_schedule"] is True
    assert report["optional_services"]["quantum_cognition"] == "degraded"
    assert report["optional_services"]["plugin_manager"] == "starting"
    assert report["system_scan"]["registry"]["healthy_services"] == 4
    engine.get_system_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_status_failure_degrades_without_disclosing_exception(launched_core):
    launcher, _registry, engine = launched_core
    engine.get_system_status.side_effect = RuntimeError("PRIVATE provider key detail")
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "degraded"
    assert "PRIVATE" not in str(report)


@pytest.mark.asyncio
async def test_online_announcement_respects_degraded_report(launched_core, caplog):
    launcher, _registry, _engine = launched_core
    launcher.readiness_report = {
        "status": "degraded",
        "message": "Core diagnostics incomplete; inspect readiness details.",
    }
    with caplog.at_level(logging.INFO, logger="aetherra_os_launcher"):
        await launcher._announce_os_online()
    assert "Core diagnostics incomplete" in caplog.text
    for unsupported in (
        "Ready for commands and questions",
        "Quantum memory: Operational",
        "Aetherra consciousness: Active",
        "Plugin ecosystem: Ready",
    ):
        assert unsupported not in caplog.text


@pytest.mark.asyncio
async def test_explicitly_disabled_optional_service_remains_visible(launched_core):
    launcher, registry, _engine = launched_core
    registry._services["self_incorporation"] = ServiceInfo(
        "self_incorporation",
        object(),
        ServiceStatus.STARTING,
        metadata={"operating_mode": "disabled", "config_enabled": False},
    )
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "ready"
    assert report["optional_services"]["self_incorporation"] == "disabled"


@pytest.mark.asyncio
async def test_kernel_registration_must_match_observed_instance(launched_core):
    launcher, registry, _engine = launched_core
    registry._services["kernel_loop"].instance = object()
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "degraded"
    assert report["core_readiness"]["kernel"]["safe_to_schedule"] is False
    assert report["core_readiness"]["kernel"]["ok"] is False


@pytest.mark.asyncio
async def test_absent_engine_preserves_offline_assessor_result(launched_core):
    launcher, registry, _engine = launched_core
    del registry._services["aetherra_engine"]
    report = await launcher._run_startup_readiness_scan()
    assert report["status"] == "degraded"
    assert report["core_readiness"]["engine"]["readiness"] == "offline"
