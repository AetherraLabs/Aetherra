"""The HMR denial test must release the real registry process it creates."""

# Standard library imports
import asyncio
import shutil
import sys
from pathlib import Path

# Third party imports
import aiohttp
import pytest

# Aetherra imports
import aetherra_kernel_loop as kernel_module
import aetherra_service_registry as registry_module
from aetherra_hub.services import metrics_accum
from tests.unit.test_hmr_denied_metrics import (
    test_hmr_denied_metric_increments as run_hmr_case,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("assertion_failure", [False, True])
async def test_hmr_denial_case_reaps_owned_registry_daemon(
    monkeypatch, tmp_path, unused_tcp_port, assertion_failure
):
    source = Path(__file__).resolve().parents[2] / "aetherra_registry_daemon.py"
    shutil.copyfile(source, tmp_path / source.name)
    monkeypatch.chdir(tmp_path)
    registry_url = f"http://127.0.0.1:{unused_tcp_port}"
    monkeypatch.setenv("AETHERRA_REGISTRY_URL", registry_url)
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_SKIP_DOTENV", "1")
    monkeypatch.setenv("AETHERRA_LYRIXA_FORCE_OFFLINE", "1")
    monkeypatch.setattr(registry_module, "_service_registry", None)
    monkeypatch.setattr(
        kernel_module, "kernel_loop", kernel_module.AetherraKernelLoop()
    )
    monkeypatch.setattr(metrics_accum, "chat_metrics", metrics_accum.ChatMetrics())
    if assertion_failure:
        monkeypatch.setattr(metrics_accum, "build_all_metrics_lines", lambda: [])

    processes = []
    ready_processes = []
    spawn = asyncio.create_subprocess_exec

    async def track_spawn(*args, **kwargs):
        process = await spawn(*args, **kwargs)
        if len(args) > 1 and Path(args[1]).name == "aetherra_registry_daemon.py":
            processes.append(process)
            launcher_type = sys.modules["aetherra_os_launcher"].AetherraOSLauncher

            async def no_component(*_args):
                pass

            # The target test reloads the launcher before spawning. Isolate its
            # unrelated components now; retain the real core loader's HMR gate.
            for name in vars(launcher_type):
                if name.startswith("_load_") and name != "_load_core_systems":
                    monkeypatch.setattr(launcher_type, name, no_component)
            load_core = launcher_type._load_core_systems

            async def observe_ready(launcher, config):
                assert process.returncode is None
                timeout = aiohttp.ClientTimeout(total=2)
                async with (
                    aiohttp.ClientSession(timeout=timeout) as session,
                    session.get(f"{registry_url}/api/registry/status") as reply,
                ):
                    assert reply.status == 200
                    assert "services" in await reply.json()
                ready_processes.append(process.pid)
                await load_core(launcher, config)

            monkeypatch.setattr(launcher_type, "_load_core_systems", observe_ready)
        return process

    # Observe the real process creation; do not replace daemon startup or shutdown.
    monkeypatch.setattr(asyncio, "create_subprocess_exec", track_spawn)
    try:
        if assertion_failure:
            with pytest.raises(AssertionError):
                await asyncio.wait_for(run_hmr_case(monkeypatch), timeout=30)
        else:
            await asyncio.wait_for(run_hmr_case(monkeypatch), timeout=30)
        denied = metrics_accum.chat_metrics.hmr_denied_reasons
        assert denied["requirements_not_met"] == 1
        assert len(processes) == 1, "The case must exercise owned daemon startup"
        assert ready_processes == [processes[0].pid]
        assert processes[0].returncode is not None, "Owned daemon survived"
        assert registry_module.get_existing_service_registry() is None
    finally:
        # Retain ownership during RED runs too; never kill an unrelated daemon.
        for process in processes:
            if process.returncode is None:
                process.kill()
                await asyncio.wait_for(process.wait(), timeout=3)
        await registry_module.shutdown_service_registry()
