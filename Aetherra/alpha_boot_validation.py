"""CI-friendly alpha boot validation for Aetherra.

The validator is intentionally headless and non-destructive. It verifies that
the alpha runtime contracts can be assembled in an isolated workspace without
starting long-running servers, opening UI processes, or depending on local
runtime databases.
"""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator


@dataclass(slots=True)
class AlphaBootCheck:
    """One alpha boot validation check result."""

    name: str
    passed: bool
    summary: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AlphaBootValidationReport:
    """Alpha boot validation report."""

    profile: str
    workspace_root: str
    checks: list[AlphaBootCheck]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile,
            "workspace_root": self.workspace_root,
            "passed": self.passed,
            "check_count": len(self.checks),
            "checks": [asdict(check) for check in self.checks],
        }


def run_alpha_boot_validation(
    *,
    workspace_root: str | Path | None = None,
    profile: str = "test",
) -> AlphaBootValidationReport:
    """Run the alpha boot validation in an isolated workspace."""

    if workspace_root is None:
        with tempfile.TemporaryDirectory(prefix="aetherra-alpha-boot-") as tmp_dir:
            return _run_validation(Path(tmp_dir), profile=profile)
    return _run_validation(Path(workspace_root), profile=profile)


def _run_validation(workspace_root: Path, *, profile: str) -> AlphaBootValidationReport:
    workspace_root = workspace_root.expanduser().resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    with _validation_environment(workspace_root, profile=profile):
        checks = [
            _check_core_imports(),
            _check_kernel_readiness_contract(),
            _check_hub_readiness_contract(),
            _check_self_incorporation_health(workspace_root),
        ]
    return AlphaBootValidationReport(
        profile=profile,
        workspace_root=str(workspace_root),
        checks=checks,
    )


def _check_core_imports() -> AlphaBootCheck:
    modules = (
        "aetherra_os_launcher",
        "aetherra_service_registry",
        "aetherra_self_incorporation",
        "aetherra_hub.app",
        "Aetherra.integration_validation",
        "Aetherra.aetherra_core.os_kernel",
    )
    imported: list[str] = []
    failures: dict[str, str] = {}
    for module_name in modules:
        try:
            __import__(module_name)
            imported.append(module_name)
        except Exception as exc:
            failures[module_name] = str(exc)[:200]

    return AlphaBootCheck(
        name="core_imports",
        passed=not failures,
        summary="Core alpha runtime modules are importable for the boot path",
        details={"imported": imported, "failures": failures},
    )


def _kernel_ready_status() -> dict[str, Any]:
    return {
        "running": True,
        "paused": False,
        "uptime": 1.0,
        "cycle_count": 1,
        "backpressure_guard_pass": True,
        "night_schedule_guard_pass": True,
        "metrics": {"errors_count": 0},
        "queue_sizes": {
            "high_priority": 0,
            "normal_priority": 0,
            "background": 0,
        },
        "queue_limits": {
            "high_priority": 10,
            "normal_priority": 20,
            "background": 50,
        },
        "plugin_cb_open": False,
        "dlq_count": 0,
        "hmr": {"attempts": 0, "success": 0, "rollback": 0},
        "inflight": {"engine": 0, "memory": 0, "plugins": 0},
        "_source": "alpha_boot_validation",
    }


def _check_kernel_readiness_contract() -> AlphaBootCheck:
    from Aetherra.aetherra_core.os_kernel import assess_kernel_readiness

    payload = assess_kernel_readiness(_kernel_ready_status())
    passed = bool(
        payload.get("readiness") == "ready"
        and payload.get("safe_to_schedule") is True
        and payload.get("checks", {}).get("status_contract_complete") is True
    )
    return AlphaBootCheck(
        name="kernel_readiness_contract",
        passed=passed,
        summary="Kernel readiness contract reports a schedulable alpha runtime shape",
        details={
            "readiness": payload.get("readiness"),
            "safe_to_schedule": payload.get("safe_to_schedule"),
            "reasons": payload.get("reasons"),
        },
    )


def _check_hub_readiness_contract() -> AlphaBootCheck:
    from aetherra_hub.app import create_app
    from aetherra_hub.config import Settings
    from aetherra_hub.services.readiness import assess_hub_readiness

    settings = Settings(
        ai_api_enabled=False,
        ai_api_require_token=False,
        ai_api_token="",
        prod_profile=False,
    )
    app = create_app(settings)
    registry_status = {
        "services": {
            "aetherra_hub": {"status": "healthy"},
            "kernel_loop": {"status": "healthy"},
        }
    }
    payload = assess_hub_readiness(
        app=app,
        settings=settings,
        kernel_status=_kernel_ready_status(),
        registry_status=registry_status,
    )
    passed = bool(
        payload.get("readiness") == "ready"
        and payload.get("safe_for_clients") is True
        and payload.get("checks", {}).get("required_routes_present") is True
    )
    return AlphaBootCheck(
        name="hub_readiness_contract",
        passed=passed,
        summary="Hub app factory exposes required alpha readiness routes",
        details={
            "readiness": payload.get("readiness"),
            "safe_for_clients": payload.get("safe_for_clients"),
            "reasons": payload.get("reasons"),
            "route_count": payload.get("checks", {}).get("route_count"),
        },
    )


def _check_self_incorporation_health(workspace_root: Path) -> AlphaBootCheck:
    from aetherra_self_incorporation import (
        SelfIncorporationConfig,
        SelfIncorporationService,
    )

    config = SelfIncorporationConfig()
    config.index_db_path = workspace_root / "selfinc_index.db"
    config.index_jsonl_path = workspace_root / "selfinc_index.jsonl"
    config.audit_db_path = workspace_root / "selfinc_audit.db"
    service = SelfIncorporationService(config)

    async def _health() -> dict[str, Any]:
        return await service.health_check()

    import asyncio

    health = asyncio.run(_health())
    passed = bool(
        health.get("status") == "starting"
        and health.get("config_enabled") is True
        and health.get("running") is False
    )
    return AlphaBootCheck(
        name="self_incorporation_health_contract",
        passed=passed,
        summary="Self-Incorporation initializes in an inspectable non-running state",
        details={
            "status": health.get("status"),
            "running": health.get("running"),
            "config_enabled": health.get("config_enabled"),
        },
    )


@contextmanager
def _validation_environment(workspace_root: Path, *, profile: str) -> Iterator[None]:
    updates = {
        "AETHERRA_PROFILE": profile,
        "AETHERRA_WORKSPACE_ROOT": str(workspace_root),
        "AETHERRA_POLICY_HOME": str(workspace_root / "policy"),
        "AETHERRA_AUDIT": "0",
        "AETHERRA_QUIET": "1",
    }
    with _temporary_env(updates):
        yield


@contextmanager
def _temporary_env(updates: dict[str, str]) -> Iterator[None]:
    previous = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main() -> int:
    report = run_alpha_boot_validation()
    print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
