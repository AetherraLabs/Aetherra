"""Shutdown must close run intent even when a dependency consumes cancellation."""

# Standard library imports
import asyncio
import contextlib
import json
import os
import sys
import types
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.homeostasis import system_supervisor
from Aetherra.homeostasis.homeostasis_core import HomeostasisController
from Aetherra.homeostasis.homeostasis_integration import HomeostasisOrchestrator


class _ControlledAwait:
    def __init__(self, completion_race):
        self.completion_race = completion_race
        self.waiting = asyncio.Event()
        self.release = asyncio.Event()
        self.reply = asyncio.get_running_loop().create_future()
        self.returned = False

    async def wait(self):
        self.waiting.set()
        if self.completion_race:
            # Exercise real wait_for; newer Python must also satisfy the contract.
            await asyncio.wait_for(self.reply, timeout=60)
        else:
            # Model a dependency finishing work after consuming one cancellation.
            with contextlib.suppress(asyncio.CancelledError):
                await self.release.wait()
        self.returned = True


async def _nothing(*args):
    return None


def _owner(component, worker, component_kind):
    # Exercise production shutdown without booting services or audit persistence.
    owner = object.__new__(HomeostasisOrchestrator)
    owner.running = True
    owner.controller = component if component_kind != "supervisor_cycle" else None
    owner.supervisor = component if component_kind == "supervisor_cycle" else None
    owner.watchdog = owner.dlq_monitor = None
    owner.si_metrics_bridge = owner.metrics_bridge = owner.error_corrector = None
    owner.background_tasks = [worker]
    owner.metrics_collection_task = None
    owner.scheduler_integration = False
    return owner


def _await_frames(task):
    frames = []
    coroutine = task.get_coro()
    for _ in range(16):
        if not isinstance(coroutine, types.CoroutineType):
            break
        frame = coroutine.cr_frame
        if frame is not None:
            frames.append(
                {
                    "function": frame.f_code.co_qualname,
                    "file": Path(frame.f_code.co_filename).name,
                    "line": frame.f_lineno,
                }
            )
        coroutine = coroutine.cr_await
    return frames


async def _shutdown_case(monkeypatch, tmp_path, component_kind, completion_race):
    boundary = _ControlledAwait(completion_race)
    post_stop_action_passes = []
    if component_kind == "supervisor_cycle":
        component = system_supervisor.SystemSupervisor(
            config_path=str(tmp_path / "absent-setpoints.yaml")
        )
        component.health_check_interval = 3600
        monkeypatch.setattr(component, "_transition_runlevel", _nothing)
        monkeypatch.setattr(component, "_update_service_health", _nothing)
        monkeypatch.setattr(component, "_supervision_cycle", boundary.wait)
        bootstrap = True

        async def sleep(delay):
            nonlocal bootstrap
            if bootstrap:
                bootstrap = False
                assert delay == 10
                return
            await asyncio.sleep(delay)

        # Skip only bootstrap delay, keeping the actual loop's blocking sleep.
        # Replace this module's reference, never asyncio.sleep globally.
        monkeypatch.setattr(
            system_supervisor,
            "asyncio",
            types.SimpleNamespace(
                sleep=sleep,
                CancelledError=asyncio.CancelledError,
            ),
        )
    else:
        metrics = types.SimpleNamespace(
            get_current_snapshot=lambda: None,
            collect_snapshot=(
                boundary.wait if component_kind == "controller_step" else _nothing
            ),
        )
        component = HomeostasisController(
            metrics=metrics,
            config_path=str(tmp_path / "absent-setpoints.yaml"),
            policy_path=str(tmp_path / "absent-policy.yaml"),
        )
        component.control_interval = 3600
        execute = component.execute_pending_actions

        async def execute_actions():
            if not owner.running:
                post_stop_action_passes.append(True)
            if component_kind == "controller_action":
                await boundary.wait()
            return await execute()

        monkeypatch.setattr(component, "execute_pending_actions", execute_actions)

    worker = asyncio.create_task(component.start())
    owner = _owner(component, worker, component_kind)
    stop_task = None
    try:
        await asyncio.wait_for(boundary.waiting.wait(), timeout=2)
        if completion_race:
            # FIFO ordering: wait_for's completion callback precedes stop();
            # on 3.11 the worker resumes after stop() has cancelled it.
            boundary.reply.set_result(None)
        stop_task = asyncio.create_task(owner.stop())
        await asyncio.wait((stop_task,), timeout=2)
        completed = stop_task.done()
        report = {
            "component": component_kind,
            "scenario": (
                "wait_for_completion_race"
                if completion_race
                else "absorbed_cancellation"
            ),
            "python": sys.version.split()[0],
            "pid": os.getpid(),
            "worker_cancelling": worker.cancelling(),
            "stop_done": completed,
            "component_running": component.running,
            "worker_done": worker.done(),
            "dependency_returned": boundary.returned,
            "post_stop_action_passes": len(post_stop_action_passes),
            "stop_frames": _await_frames(stop_task),
            "worker_frames": _await_frames(worker),
        }
        if output := os.getenv("AETHERRA_CI_DIAGNOSTICS"):
            directory = Path(output)
            directory.mkdir(parents=True, exist_ok=True)
            with (directory / "homeostasis-shutdown.jsonl").open(
                "a", encoding="utf-8"
            ) as stream:
                stream.write(json.dumps(report, sort_keys=True) + "\n")
        assert completed, json.dumps(report, sort_keys=True)
        await stop_task
        assert worker.done()
        assert not component.running
        assert len(owner.background_tasks) == 0
        assert not post_stop_action_passes
    finally:
        # Release the controlled dependency before bounded cancellation cleanup.
        component.stop()
        boundary.release.set()
        tasks = [task for task in (worker, stop_task) if task is not None]
        for task in tasks:
            if not task.done():
                task.cancel()
        _, pending = await asyncio.wait(tasks, timeout=2)
        assert len(pending) == 0, "Controlled shutdown tasks survived cleanup"
        for task in tasks:
            if not task.cancelled():
                task.result()


@pytest.mark.parametrize(
    "component_kind", ["controller_step", "controller_action", "supervisor_cycle"]
)
@pytest.mark.parametrize(
    "completion_race",
    [False, True],
    ids=["absorbed_cancellation", "wait_for_completion_race"],
)
def test_stop_finishes_when_dependency_consumes_cancellation(
    monkeypatch, tmp_path, component_kind, completion_race
):
    asyncio.run(_shutdown_case(monkeypatch, tmp_path, component_kind, completion_race))


def test_controller_completes_normal_cycle_before_stopping(monkeypatch, tmp_path):
    events = []

    async def collect_snapshot():
        events.append("metrics")
        if events.count("metrics") == 2:
            controller.stop()

    controller = HomeostasisController(
        metrics=types.SimpleNamespace(
            get_current_snapshot=lambda: None,
            collect_snapshot=collect_snapshot,
        ),
        config_path=str(tmp_path / "absent-setpoints.yaml"),
        policy_path=str(tmp_path / "absent-policy.yaml"),
    )
    controller.control_interval = 0
    execute = controller.execute_pending_actions

    async def execute_actions():
        events.append("actions")
        return await execute()

    monkeypatch.setattr(controller, "execute_pending_actions", execute_actions)

    async def run():
        await asyncio.wait_for(controller.start(), timeout=2)

    asyncio.run(run())
    assert events == ["metrics", "actions", "metrics"]
    assert not controller.running
