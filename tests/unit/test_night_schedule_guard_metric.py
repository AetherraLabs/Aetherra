import pytest

from aetherra_kernel_loop import AetherraKernelLoop


@pytest.mark.asyncio
async def test_night_schedule_guard_blocks_prod_without_tz(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    # Clear TZ envs
    monkeypatch.delenv("AETHERRA_NIGHT_TZ", raising=False)
    monkeypatch.delenv("AETHERRA_NIGHT_UTC", raising=False)
    k = AetherraKernelLoop()
    # Force check (window irrelevant; guard should set pass false and block increment)
    await k._check_night_cycle()
    assert getattr(k, "_night_schedule_guard_pass", False) is False
    status = k.get_status()
    assert status.get("night_schedule_guard_pass") is False


@pytest.mark.asyncio
async def test_night_schedule_guard_passes_with_utc(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_NIGHT_UTC", "1")
    k = AetherraKernelLoop()
    await k._check_night_cycle()
    assert getattr(k, "_night_schedule_guard_pass", False) is True
    status = k.get_status()
    assert status.get("night_schedule_guard_pass") is True
