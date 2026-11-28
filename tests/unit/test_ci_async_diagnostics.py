"""Contracts for private, bounded asyncio diagnostics and Linux signal ownership."""

# Standard library imports
import asyncio
import json
import os
import subprocess
import sys
import time
import types

# Third party imports
import pytest

# Aetherra imports
from tools import ci_capabilities_diagnostics as diagnostics
from tools import ci_capabilities_phase as phase


def _read_records(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


@pytest.mark.parametrize("generator_bridge", [False, True])
def test_capture_includes_nested_await_frames_without_private_values(
    tmp_path, generator_bridge
):
    assert callable(getattr(phase, "_capture_async_stacks", None))

    async def scenario():
        event = asyncio.Event()

        async def inner():
            private_local = "PRIVATE_LOCAL_SENTINEL"
            await event.wait()
            return private_local

        @types.coroutine
        def bridge():
            yield from inner()

        async def outer():
            await (bridge() if generator_bridge else inner())

        task = asyncio.create_task(outer(), name="PRIVATE_TASK_SENTINEL")
        await asyncio.sleep(0)
        state = {
            "enabled": True,
            "pending": True,
            "output": tmp_path,
            "pid": os.getpid(),
        }
        try:
            phase._capture_async_stacks(state, asyncio.get_running_loop())
            records = _read_records(tmp_path / "async-stacks.jsonl")
            chains = [
                [frame["function"] for frame in task["frames"]]
                for task in records[0]["tasks"]
            ]
            assert any(
                all(
                    any(name.endswith(part) for name in names)
                    for part in ("outer", "inner", "Event.wait")
                )
                for names in chains
            )
            if generator_bridge:
                assert any(
                    any(name.endswith("bridge") for name in names) for names in chains
                )
            assert all(
                set(frame) == {"function", "file", "line"}
                for item in records[0]["tasks"]
                for frame in item["frames"]
            )
            text = (tmp_path / "async-stacks.jsonl").read_text()
            assert "PRIVATE_LOCAL_SENTINEL" not in text
            assert "PRIVATE_TASK_SENTINEL" not in text
            assert state["pending"] is False
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(scenario())


def test_capture_follows_awaited_task_outside_initial_inventory(monkeypatch, tmp_path):
    async def scenario():
        release = asyncio.Event()
        entered = asyncio.Event()
        cancellation_consumed = asyncio.Event()

        async def boot():
            private_local = "PRIVATE_LOCAL_SENTINEL"
            entered.set()
            try:
                await release.wait()
            except asyncio.CancelledError:
                cancellation_consumed.set()
                await release.wait()
            return private_local

        async def heartbeat():
            await release.wait()

        boot_task = asyncio.create_task(boot(), name="PRIVATE_TASK_SENTINEL")
        await asyncio.wait_for(entered.wait(), timeout=2)
        boot_task.cancel()
        await asyncio.wait_for(cancellation_consumed.wait(), timeout=2)

        async def parent():
            await boot_task

        parent_task = asyncio.create_task(parent())
        heartbeats = [asyncio.create_task(heartbeat()) for _ in range(40)]
        await asyncio.sleep(0)
        inventory = [heartbeats[0], parent_task, *heartbeats[1:], boot_task]
        state = {
            "enabled": True,
            "pending": True,
            "output": tmp_path,
            "pid": os.getpid(),
        }
        try:
            # Control enumeration only; every await edge belongs to a real Task.
            with monkeypatch.context() as patch:
                patch.setattr(
                    phase,
                    "asyncio",
                    types.SimpleNamespace(
                        all_tasks=lambda _loop: inventory,
                        Task=asyncio.Task,
                    ),
                )
                phase._capture_async_stacks(state, asyncio.get_running_loop())
            capture = tmp_path / "async-stacks.jsonl"
            tasks = _read_records(capture)[0]["tasks"]
            boots = [
                task
                for task in tasks
                if any(frame["function"].endswith("boot") for frame in task["frames"])
            ]
            assert len(boots) == 1, "Awaited boot task was omitted"
            parent_record = next(
                task
                for task in tasks
                if any(frame["function"].endswith("parent") for frame in task["frames"])
            )
            assert parent_record["awaits_task"] == boots[0]["task_id"]
            assert boots[0]["cancelling"] == 1
            assert boots[0]["awaits_task"] is None  # Event's plain Future is opaque.
            assert "PRIVATE_LOCAL_SENTINEL" not in capture.read_text()
            assert "PRIVATE_TASK_SENTINEL" not in capture.read_text()
        finally:
            release.set()
            await asyncio.wait_for(
                asyncio.gather(parent_task, boot_task, *heartbeats), timeout=2
            )

    asyncio.run(scenario())


@pytest.mark.parametrize("coroutine_depth", [0, 12])
def test_awaited_task_graph_respects_global_limits(
    monkeypatch, tmp_path, coroutine_depth
):
    async def scenario():
        release = asyncio.Event()

        async def leaf():
            await release.wait()

        async def link(child):
            async def nested(depth):
                if depth:
                    await nested(depth - 1)
                else:
                    await child

            await nested(coroutine_depth)

        owned = [asyncio.create_task(leaf())]
        for _ in range(40):
            owned.append(asyncio.create_task(link(owned[-1])))
        await asyncio.sleep(0)
        state = {
            "enabled": True,
            "pending": True,
            "output": tmp_path,
            "pid": os.getpid(),
        }
        try:
            with monkeypatch.context() as patch:
                patch.setattr(
                    phase,
                    "asyncio",
                    types.SimpleNamespace(
                        all_tasks=lambda _loop: [owned[-1], *owned],
                        Task=asyncio.Task,
                    ),
                )
                phase._capture_async_stacks(state, asyncio.get_running_loop())
            tasks = _read_records(tmp_path / "async-stacks.jsonl")[0]["tasks"]
            ids = {task["task_id"] for task in tasks}
            assert len(tasks) == len(ids) <= 32
            assert sum(len(task["frames"]) for task in tasks) <= 256
            assert any(task["awaits_task"] is not None for task in tasks)
            assert all(
                task["awaits_task"] is None or task["awaits_task"] in ids
                for task in tasks
            )
            if coroutine_depth == 0:
                assert len(tasks) == 32
            else:
                assert sum(len(task["frames"]) for task in tasks) == 256
        finally:
            release.set()
            await asyncio.wait_for(asyncio.gather(*owned), timeout=2)

    asyncio.run(scenario())


def test_await_chain_is_bounded_and_disabled_callback_does_not_write(tmp_path):
    assert callable(getattr(phase, "_await_chain", None))

    async def scenario():
        event = asyncio.Event()

        async def nested(depth):
            if depth:
                await nested(depth - 1)
            else:
                await event.wait()

        task = asyncio.create_task(nested(80))
        await asyncio.sleep(0)
        try:
            frames = phase._await_chain(task.get_coro(), max_frames=3)
            assert len(frames) == 3
            state = {
                "enabled": False,
                "pending": True,
                "output": tmp_path,
                "pid": os.getpid(),
            }
            phase._capture_async_stacks(state, asyncio.get_running_loop())
            assert not (tmp_path / "async-stacks.jsonl").exists()
        finally:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)

    asyncio.run(scenario())


def _child_environment(output):
    env = dict(
        os.environ,
        AETHERRA_CI_DIAGNOSTICS=str(output),
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        env.pop(name, None)
    return env


@pytest.mark.parametrize("inherited", ["addopts", "plugins", "both"])
def test_isolated_child_ignores_parent_pytest_configuration(
    monkeypatch, tmp_path, inherited
):
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS"):
        monkeypatch.delenv(name, raising=False)
    if inherited in ("addopts", "both"):
        monkeypatch.setenv("PYTEST_ADDOPTS", "--cov-append")
    if inherited in ("plugins", "both"):
        monkeypatch.setenv("PYTEST_PLUGINS", "ci_async_unavailable_plugin_sentinel")
    suite = tmp_path / "test_minimal.py"
    suite.write_text(
        "import sys\n"
        "def test_minimal():\n"
        "    assert 'tools.ci_capabilities_phase' in sys.modules\n"
    )
    output = tmp_path / "diagnostics"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-o",
            "addopts=",
            "-p",
            "tools.ci_capabilities_phase",
            str(suite),
        ],
        env=_child_environment(output),
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (output / "phases.jsonl").exists()


def _wait_until(predicate, child, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        if child.poll() is not None:
            stdout, stderr = child.communicate(timeout=1)
            pytest.fail(
                "diagnostic test child exited before readiness:\n" + stdout + stderr
            )
        time.sleep(0.02)
    pytest.fail("diagnostic child did not become ready")


@pytest.mark.skipif(sys.platform != "linux", reason="Linux SIGUSR1 lifecycle contract")
@pytest.mark.parametrize("exit_code", [0, 1])
def test_linux_signal_captures_wait_chain_and_late_signal_preserves_exit(
    tmp_path, exit_code
):
    output = tmp_path / "diagnostics"
    ready = tmp_path / "test-ready"
    release = tmp_path / "release"
    suite = tmp_path / "test_waiting.py"
    suite.write_text(
        "import asyncio\nfrom pathlib import Path\n"
        "def test_waiting():\n"
        "    async def scenario():\n"
        "        event = asyncio.Event()\n"
        "        async def inner():\n"
        "            private_local = 'PRIVATE_LOCAL_SENTINEL'\n"
        "            await event.wait()\n"
        "        async def outer():\n"
        "            child_task = asyncio.create_task(inner(), name='PRIVATE_TASK_SENTINEL')\n"
        "            await child_task\n"
        "        async def release_when_ready():\n"
        f"            while not Path({str(release)!r}).exists():\n"
        "                await asyncio.sleep(0.02)\n"
        "            event.set()\n"
        "        task = asyncio.create_task(outer(), name='PRIVATE_TASK_SENTINEL')\n"
        "        releaser = asyncio.create_task(release_when_ready())\n"
        "        await asyncio.sleep(0)\n"
        f"        Path({str(ready)!r}).touch()\n"
        "        await task\n"
        "        await releaser\n"
        "    asyncio.run(scenario())\n"
        f"    assert {exit_code} == 0\n"
    )
    code = (
        "import os,signal,sys,pytest; "
        f"result=pytest.main(['-q','-o','addopts=','--tb=no','-p','tools.ci_capabilities_phase',{str(suite)!r}]); "
        f"assert result == {exit_code}, f'pytest returned {{result}} before late SIGUSR1'; "
        "os.kill(os.getpid(),signal.SIGUSR1); sys.exit(result)"
    )
    env = _child_environment(output)
    child = subprocess.Popen(
        [sys.executable, "-c", code],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    marker = output / f"async-ready-{child.pid}.json"
    try:
        _wait_until(lambda: ready.exists() and marker.exists(), child)
        owner = diagnostics.read_process(child.pid)
        identity = json.loads(marker.read_text())
        assert all(identity[key] == owner[key] for key in ("pid", "start", "session"))
        diagnostics.snapshot(owner, None, output, request_async=True)
        capture = output / "async-stacks.jsonl"
        _wait_until(capture.exists, child)
        records = _read_records(capture)
        tasks = {task["task_id"]: task for task in records[0]["tasks"]}
        outer = next(
            task
            for task in tasks.values()
            if any(frame["function"].endswith("outer") for frame in task["frames"])
        )
        inner = tasks[outer["awaits_task"]]
        names = [frame["function"] for frame in inner["frames"]]
        assert all(
            any(name.endswith(part) for name in names)
            for part in ("inner", "Event.wait")
        )
        assert "PRIVATE_LOCAL_SENTINEL" not in capture.read_text()
        assert "PRIVATE_TASK_SENTINEL" not in capture.read_text()
        release.touch()
        stdout, stderr = child.communicate(timeout=15)
        assert child.returncode == exit_code, stdout + stderr
        assert not marker.exists()
    finally:
        if child.poll() is None:
            child.kill()
        child.communicate(timeout=5)


@pytest.mark.skipif(
    sys.platform != "linux", reason="Linux existing-handler ownership contract"
)
@pytest.mark.parametrize("install_when", ["before", "during"])
def test_linux_plugin_preserves_custom_signal_handler(tmp_path, install_when):
    suite = tmp_path / "test_simple.py"
    suite.write_text(
        "import signal, __main__\ndef test_simple():\n"
        + (
            "    signal.signal(signal.SIGUSR1, __main__.handler)\n"
            if install_when == "during"
            else "    pass\n"
        )
    )
    output = tmp_path / "diagnostics"
    code = (
        "import os,signal,sys,pytest; "
        "handler=lambda signum,frame: None; "
        + (
            "signal.signal(signal.SIGUSR1,handler); "
            if install_when == "before"
            else ""
        )
        + f"result=pytest.main(['-q','-o','addopts=','-p','tools.ci_capabilities_phase',{str(suite)!r}]); "
        "assert signal.getsignal(signal.SIGUSR1) is handler; "
        "os.kill(os.getpid(),signal.SIGUSR1); sys.exit(result)"
    )
    env = _child_environment(output)
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert not list(output.glob("async-ready-*.json"))
