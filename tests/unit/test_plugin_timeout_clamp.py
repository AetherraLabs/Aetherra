# Third party imports
import pytest

# Aetherra imports
from aetherra_kernel_loop import AetherraKernelLoop

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_plugin_timeout_clamp_over_ceiling(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "999")  # way above ceiling
    kernel = AetherraKernelLoop()
    assert kernel.plugin_invoke_timeout_sec == 120.0, (
        "Timeout should clamp to 120s ceiling in production"
    )


@pytest.mark.asyncio
async def test_plugin_timeout_non_positive_resets(monkeypatch):
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "0")  # non-positive
    kernel = AetherraKernelLoop()
    assert kernel.plugin_invoke_timeout_sec == 20.0, (
        "Non-positive timeout should reset to conservative 20s default in production"
    )


def test_plugin_timeout_metric_export(monkeypatch):
    # Ensure value propagates to metrics exporter lines (synchronous context so registry client can fetch status)
    monkeypatch.setenv("AETHERRA_PROFILE", "prod")
    monkeypatch.setenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "45")
    kernel = AetherraKernelLoop()
    # Standard library imports
    import asyncio

    # Aetherra imports
    from aetherra_service_registry import get_service_registry

    async def _setup():
        reg = await get_service_registry()
        try:
            await reg.register_service("kernel_loop", kernel)  # type: ignore[attr-defined]
        except Exception:
            pass

    asyncio.run(_setup())

    # Aetherra imports
    from aetherra_hub.services import metrics_accum

    lines = metrics_accum.build_all_metrics_lines()
    joined = "\n".join(lines)
    assert "aetherra_kernel_plugin_invoke_timeout_sec" in joined, joined
    assert (
        "aetherra_kernel_plugin_invoke_timeout_sec 45.0" in joined
        or "aetherra_kernel_plugin_invoke_timeout_sec 45" in joined
    ), joined
