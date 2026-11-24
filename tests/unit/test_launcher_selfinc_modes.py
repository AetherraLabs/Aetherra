"""The normal launcher must preserve explicit Self-Incorporation operating modes."""

# Standard library imports
import asyncio
import contextlib
from pathlib import Path
from unittest.mock import AsyncMock

# Third party imports
import pytest
from flask import Flask

# Aetherra imports
import aetherra_service_registry as registry_module
from aetherra_hub.blueprints.self_improvement import bp as improvement_bp
from aetherra_hub.blueprints.self_incorporation import bp
from aetherra_os_launcher import AetherraOSLauncher
from aetherra_self_incorporation import (
    SelfIncorporationConfig,
    SelfIncorporationService,
)


@pytest.fixture
def isolated_runtime(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", "")
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.delenv("AETHERRA_SELFINC_ENABLED", raising=False)
    registry = registry_module.AetherraServiceRegistry()
    monkeypatch.setattr(registry_module, "_service_registry", registry)
    launcher = AetherraOSLauncher()
    launcher.service_registry = registry
    return launcher, registry, tmp_path


async def _load_maintenance(launcher, tmp_path):
    try:
        await launcher._load_self_maintenance_systems(
            {"self_improvement_db": str(tmp_path / "self_improvement.db")}
        )
    finally:
        adapter = launcher.systems.get("self_improvement")
        if adapter is not None:
            await adapter.impl.stop_improvement_cycle()
        task = launcher._improvement_telemetry_task
        if task is not None:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


@pytest.mark.parametrize(
    ("requested", "enabled"), [(None, False), ("0", False), ("1", True)]
)
def test_launcher_honors_selfinc_opt_in(
    isolated_runtime, monkeypatch, requested, enabled
):
    launcher, registry, tmp_path = isolated_runtime
    if requested is not None:
        monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", requested)
    asyncio.run(_load_maintenance(launcher, tmp_path))

    service = registry.get_service("self_incorporation")
    assert service is launcher.systems["self_incorporation"]
    assert service.config.enabled is enabled
    assert service._running is False


def test_launcher_preserves_configured_roots_and_strict_policy(
    isolated_runtime, monkeypatch
):
    launcher, _, tmp_path = isolated_runtime
    root = tmp_path / "reviewed-source"
    root.mkdir()
    monkeypatch.setenv("AETHERRA_SELFINC_ROOTS", str(root))
    monkeypatch.setenv("AETHERRA_SELFINC_TRUST_MODE", "strict")
    asyncio.run(_load_maintenance(launcher, tmp_path))

    service = launcher.systems["self_incorporation"]
    assert service.config.roots == [root]
    assert service.config.trust_mode == "strict"
    assert service.security_layer.trust_mode == "strict"


def test_disabled_launcher_activation_never_scans(isolated_runtime, monkeypatch):
    launcher, registry, tmp_path = isolated_runtime
    monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", "0")
    (tmp_path / "synthetic_plugin.py").write_text("VALUE = 1\n", encoding="utf-8")
    service = SelfIncorporationService(SelfIncorporationConfig())
    launcher.systems["self_incorporation"] = service

    async def activate():
        await registry.register_service("self_incorporation", service)
        await launcher._activate_systems({"quiet": True})
        pending = asyncio.all_tasks() - {asyncio.current_task()}
        if pending:
            await asyncio.gather(*pending)

    asyncio.run(activate())
    assert service.code_index.list_files() == []
    assert service.metrics["last_scan_timestamp"] == 0
    assert service._running is False

    app = Flask(__name__)
    app.register_blueprint(bp)
    response = app.test_client().get("/api/selfinc/status")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "disabled"
    assert body["config_enabled"] is False
    assert body["running"] is False


@pytest.mark.parametrize(
    ("operation", "kwargs"),
    [
        ("trigger_scan", {}),
        ("trigger_classify", {}),
        ("trigger_security_eval", {}),
        ("trigger_integrate", {"force": True}),
        ("integrate_with_canary", {"canary_duration": 0}),
    ],
)
def test_disabled_service_rejects_work(
    isolated_runtime, monkeypatch, operation, kwargs
):
    _, _, tmp_path = isolated_runtime
    monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", "0")
    (tmp_path / "synthetic_plugin.py").write_text("VALUE = 1\n", encoding="utf-8")
    service = SelfIncorporationService(SelfIncorporationConfig())
    # Any planning below the disabled gate would reach an execution path. Keep
    # this failure explicit without exercising external plugins or HMR.
    service._run_integration_planning = AsyncMock(
        side_effect=AssertionError("Disabled service attempted integration planning")
    )

    result = asyncio.run(getattr(service, operation)(**kwargs))

    assert result["ok"] is False
    assert result["status"] == "disabled"
    assert result["reason"] == "service_disabled"
    assert service.code_index.list_files() == []
    assert service.metrics["proposals_executed"] == 0


def test_standalone_default_remains_enabled(isolated_runtime):
    assert SelfIncorporationConfig().enabled is True


def test_explicit_enabled_launcher_still_starts_and_scans(
    isolated_runtime, monkeypatch
):
    launcher, registry, tmp_path = isolated_runtime
    monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", "1")
    source = tmp_path / "reviewed-source"
    source.mkdir()
    (source / "synthetic_plugin.py").write_text("VALUE = 1\n", encoding="utf-8")
    monkeypatch.setenv("AETHERRA_SELFINC_ROOTS", str(source))
    service = SelfIncorporationService(SelfIncorporationConfig())
    launcher.systems["self_incorporation"] = service

    async def activate():
        await registry.register_service("self_incorporation", service)
        await launcher._activate_systems({"quiet": True})
        pending = asyncio.all_tasks() - {asyncio.current_task()}
        if pending:
            await asyncio.gather(*pending)
        return await service.get_status()

    status = asyncio.run(activate())
    assert status["status"] == "healthy"
    assert status["running"] is True
    assert status["config_enabled"] is True
    assert len(service.code_index.list_files()) == 1
    assert status["last_scan"]["timestamp"] > 0
    asyncio.run(service.stop())


def test_disabled_service_keeps_planning_diagnostics(isolated_runtime, monkeypatch):
    monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", "0")
    service = SelfIncorporationService(SelfIncorporationConfig())
    result = asyncio.run(service.trigger_planning())
    assert result["ok"] is True
    assert result["actions"] == 0
    assert service.metrics["files_integrated"] == 0


def test_disabled_service_rollback_still_requires_guardian(
    isolated_runtime, monkeypatch
):
    monkeypatch.setenv("AETHERRA_SELFINC_ENABLED", "0")
    service = SelfIncorporationService(SelfIncorporationConfig())
    result = asyncio.run(
        service.trigger_rollback("rb_synthetic_recovery", requester="unprivileged-test")
    )
    assert result["ok"] is False
    assert result["error"].startswith("guardian_denied:")
    assert result["guardian"]["status"] == "deny"


@pytest.mark.parametrize("requested", ["0", "1"])
def test_launcher_self_improvement_status_reports_effective_authority(
    isolated_runtime, monkeypatch, requested
):
    launcher, _, tmp_path = isolated_runtime
    monkeypatch.setenv("AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT", requested)
    asyncio.run(_load_maintenance(launcher, tmp_path))
    app = Flask(__name__)
    app.register_blueprint(improvement_bp)

    response = app.test_client().get("/api/selfimprove/status")

    assert response.status_code == 200
    status = response.get_json()
    assert status["autonomous_implementation_requested"] is (requested == "1")
    assert status["autonomous_implementation_enabled"] is False
    assert status["implementation_authority"] == "guardian_controlled_execution"
