import asyncio
import contextlib
import types
from typing import Any

import pytest

# We avoid pytest-asyncio dependency by using manual async test runners similar to other acceptance tests.


class DummyServiceInfo:
    def __init__(self, instance):
        self.instance = instance


class DummyServiceRegistry:
    def __init__(self, services: dict[str, object] | None = None):
        self._services = services or {}

    def get_service_info(self, name: str):
        inst = self._services.get(name)
        return DummyServiceInfo(inst) if inst is not None else None

    # Provide no-op async register/unregister to keep interface parity if called
    async def register_service(
        self, name: str, instance: object, metadata: dict | None = None
    ):
        self._services[name] = instance

    async def unregister_service(self, name: str):
        self._services.pop(name, None)


class DummyHomeostasis:
    """Provides a sequence of health scores for successive checks."""

    def __init__(self, sequence: list[float]):
        self.sequence = list(sequence)
        self.idx = 0

    async def get_system_health_status(self):
        if self.idx < len(self.sequence):
            val = self.sequence[self.idx]
            self.idx += 1
        else:
            val = self.sequence[-1] if self.sequence else 0.95
        # Homeostasis returns nested structure with 'system_health.health_score'
        return {
            "system_health": {
                "health_score": val,
            }
        }


class DummyHMRController:
    pass


async def setup_service_with_stubs(health_sequence: list[float]):
    # Import here to avoid heavy imports at module import time
    from aetherra_self_incorporation import SelfIncorporationService

    service = SelfIncorporationService()

    # Inject a stubbed service registry with HMR and Homeostasis
    homeostasis = DummyHomeostasis(health_sequence)
    hmr = DummyHMRController()
    registry = DummyServiceRegistry(
        {
            "homeostasis_system": homeostasis,
            "hmr_controller": hmr,
        }
    )
    service.service_registry = registry

    # Short-circuit planning to avoid file system scans; return a minimal ready plan
    async def fake_planning(self, include_experimental: bool = False):
        return {
            "plan_id": "plan-test-123",
            "status": "ready",
            "actions": [
                # Use an HMR-routed action to ensure rollback_token is generated
                {"action": "register_plugin", "target": {"file_id": "demo_plugin.py"}}
            ],
        }

    # Bind the fake planning coroutine as a method on the instance
    service._run_integration_planning = types.MethodType(fake_planning, service)

    return service


async def teardown_service(service):
    # Nothing special for now; placeholder for future resource cleanup
    with contextlib.suppress(Exception):
        await service.stop()


@pytest.mark.acceptance
def test_canary_promotion_e2e():
    async def _run():
        # Baseline and all checks above threshold
        service = await setup_service_with_stubs([0.95, 0.96, 0.97, 0.98])

        try:
            # Patch asyncio.sleep to run instantly for faster tests
            original_sleep = asyncio.sleep

            async def fast_sleep(_seconds: float):
                return None

            asyncio.sleep = fast_sleep
            # Speed up checks: short canary with rapid intervals
            result = await service.integrate_with_canary(
                plan_id="acceptance-promo",
                canary_percent=0.1,
                canary_duration=1,
                health_check_interval=1,
                rollback_threshold=0.90,
                dry_run=False,
            )

            assert result["ok"] is True
            assert result["status"] == "canary_stable"
            assert result["deployment"] == "canary_promoted"
            assert result.get("checks_completed", 0) >= 1
            assert result["min_health"] >= 0.90
            # Rollback token must be present (generated via HMR path)
            assert (
                isinstance(result.get("rollback_token"), str)
                and len(result["rollback_token"]) > 0
            )
            # Health delta non-negative (avg >= baseline)
            assert result["health_delta"] >= 0.0

            # Metrics reflect success path
            assert service.metrics.get("canary_deployments_successful", 0) >= 1
        finally:
            # Restore original sleep
            asyncio.sleep = original_sleep
            await teardown_service(service)

    asyncio.run(_run())


@pytest.mark.acceptance
def test_canary_auto_rollback_e2e():
    async def _run():
        # Baseline healthy then degrade below threshold during checks
        service = await setup_service_with_stubs([0.95, 0.92, 0.85, 0.84])

        # Stub trigger_rollback to avoid I/O and speed the test
        async def fake_trigger_rollback(token: str):
            service.metrics["rollbacks"] = service.metrics.get("rollbacks", 0) + 1
            return {"ok": True, "token": token, "note": "stubbed"}

        service.trigger_rollback = fake_trigger_rollback

        try:
            # Patch asyncio.sleep to run instantly for faster tests
            original_sleep = asyncio.sleep

            async def fast_sleep(_seconds: float):
                return None

            asyncio.sleep = fast_sleep
            result = await service.integrate_with_canary(
                plan_id="acceptance-rollback",
                canary_percent=0.1,
                canary_duration=3,
                health_check_interval=1,
                rollback_threshold=0.90,
                dry_run=False,
            )

            assert result["ok"] is False
            assert result["status"] == "auto_rollback"
            assert result["deployment"] == "canary_failed"
            assert (
                isinstance(result.get("rollback_token"), str)
                and len(result["rollback_token"]) > 0
            )
            assert "health_below_threshold" in (result.get("rollback_reason") or "")
            assert result.get("checks_completed", 0) >= 1
            # Metrics reflect failure path
            assert service.metrics.get("canary_deployments_failed", 0) >= 1
            assert service.metrics.get("rollbacks", 0) >= 1
        finally:
            # Restore original sleep
            asyncio.sleep = original_sleep
            await teardown_service(service)

    asyncio.run(_run())
