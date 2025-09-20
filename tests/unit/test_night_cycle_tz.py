# Standard library imports
import asyncio
from datetime import datetime, timezone

# Third party imports
import pytest

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop


@pytest.mark.asyncio
async def test_prod_blocks_without_tz(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Force window to include current UTC hour
    now_utc = datetime.now(timezone.utc)
    monkeypatch.setenv("AETHERRA_NIGHT_START_HOUR", str(now_utc.hour))
    monkeypatch.setenv("AETHERRA_NIGHT_END_HOUR", str(now_utc.hour))
    # Ensure no explicit TZ variables
    monkeypatch.delenv("AETHERRA_NIGHT_TZ", raising=False)
    monkeypatch.delenv("AETHERRA_NIGHT_UTC", raising=False)

    k = AetherraKernelLoop()
    # Call the internal check directly
    await k._check_night_cycle()
    # Should not have incremented cycles without TZ
    assert k.metrics.get("night_cycles_count", 0) == 0
    assert k.metrics.get("night_cycles_blocked_no_tz", 0) >= 1


@pytest.mark.asyncio
async def test_utc_allows_in_window(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "test")
    monkeypatch.setenv("AETHERRA_NIGHT_UTC", "1")
    now_utc = datetime.now(timezone.utc)
    monkeypatch.setenv("AETHERRA_NIGHT_START_HOUR", str(now_utc.hour))
    monkeypatch.setenv("AETHERRA_NIGHT_END_HOUR", str(now_utc.hour))
    # No staggering for determinism in test
    monkeypatch.setenv("AETHERRA_NIGHT_STAGGER_MAX_SEC", "0")

    k = AetherraKernelLoop()

    # Patch _perform_night_cycle to avoid long work and to observe it ran
    ran = {"v": False}

    async def fake_run():
        ran["v"] = True

    k._perform_night_cycle = fake_run  # type: ignore

    await k._check_night_cycle()
    # Give scheduled task a tick
    await asyncio.sleep(0.05)
    assert ran["v"] is True
    assert k.metrics.get("night_cycles_count", 0) >= 1
