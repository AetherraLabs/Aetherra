"""Keep continuity command failures visible without leaking private errors."""

from __future__ import annotations

# Standard library imports
import asyncio
import json
import threading
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from tests.unit import test_memory_lifecycle_checkpoint as checkpoints

policy = checkpoints.policy
memory = checkpoints.memory

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def smoke(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    # Third party imports
    import alpha_consciousness_continuity_smoke

    return alpha_consciousness_continuity_smoke


class Kernel:
    def __init__(self):
        self.cycles = 0

    def get_status(self):
        self.cycles += 1
        return {
            "cycle_count": self.cycles,
            "queue_sizes": {"high_priority": 0},
            "inflight": {},
        }


def launcher(failure_stage):
    async def stop(*, save_checkpoint):
        assert save_checkpoint is True
        if failure_stage == "stop_observer":
            raise RuntimeError("consciousness_shutdown_pending")

    async def start_conversation():
        if failure_stage == "start_conversation":
            raise ValueError("PRIVATE_SYNTHETIC_CONVERSATION_DO_NOT_LOG")

    return SimpleNamespace(
        kernel_loop=Kernel(),
        _stop_consciousness_observer=stop,
        systems={
            "aetherra": SimpleNamespace(
                impl=SimpleNamespace(
                    start_conversation=start_conversation,
                    _public_conversation_context=lambda: {"message_count": 0},
                )
            ),
            "consciousness_core": SimpleNamespace(
                get_runtime_status=lambda: {"runtime_state": "stopped"}
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("stage", "code"),
    [
        ("stop_observer", "consciousness_shutdown_pending"),
        ("start_conversation", "command_failed"),
    ],
)
async def test_command_failure_writes_sanitized_stage_receipt(
    smoke, tmp_path, monkeypatch, stage, code
):
    # Only the unrelated profile inventory is doubled; the command task and
    # receipt writes are real. The injected boundary error must remain visible.
    monkeypatch.setattr(smoke, "side_effect_snapshot", lambda profile: {})
    (tmp_path / "stop-observer").touch()
    task = asyncio.create_task(smoke._run_commands(launcher(stage), tmp_path, tmp_path))
    try:
        await asyncio.wait({task}, timeout=1)
        assert task.done()
        receipt = tmp_path / "command-error.json"
        assert receipt.exists(), "command task failed without an error receipt"
        assert json.loads(receipt.read_text(encoding="utf-8")) == {
            "stage": stage,
            "code": code,
        }
        assert "PRIVATE_SYNTHETIC" not in receipt.read_text(encoding="utf-8")
        assert not (tmp_path / "observer-stopped.json").exists()
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


def test_parent_wait_reports_command_failure_without_waiting_for_timeout(
    smoke, tmp_path, monkeypatch
):
    smoke.write_json(
        tmp_path / "command-error.json",
        {"stage": "stop_observer", "code": "consciousness_shutdown_pending"},
    )

    def no_sleep(seconds):
        pytest.fail("waiter ignored command failure and tried to wait")

    monkeypatch.setattr(smoke.time, "sleep", no_sleep)
    with pytest.raises(
        RuntimeError, match="stop_observer/consciousness_shutdown_pending"
    ):
        smoke.wait_file(
            tmp_path / "observer-stopped.json",
            SimpleNamespace(poll=lambda: None),
            15,
        )


@pytest.mark.asyncio
async def test_success_receipt_remains_usable_after_normal_task_cancellation(
    smoke, tmp_path, monkeypatch
):
    monkeypatch.setattr(smoke, "side_effect_snapshot", lambda profile: {})
    (tmp_path / "stop-observer").touch()
    task = asyncio.create_task(smoke._run_commands(launcher(None), tmp_path, tmp_path))
    try:
        async with asyncio.timeout(1):
            while not (tmp_path / "observer-stopped.json").exists():
                await asyncio.sleep(0.01)
        stopped = smoke.wait_file(
            tmp_path / "observer-stopped.json", SimpleNamespace(poll=lambda: None)
        )
        assert stopped == {
            "observer": {"runtime_state": "stopped"},
            "new_context": {"message_count": 0},
        }
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert not (tmp_path / "command-error.json").exists()


def test_error_receipt_never_replays_unknown_fields(smoke, tmp_path):
    smoke.write_json(
        tmp_path / "command-error.json",
        {"stage": "PRIVATE_STAGE", "code": "PRIVATE_ERROR"},
    )
    with pytest.raises(RuntimeError) as error:
        smoke.wait_file(
            tmp_path / "observer-stopped.json", SimpleNamespace(poll=lambda: None)
        )
    assert str(error.value) == "Continuity command failed (unknown/command_failed)"


def test_waiter_retains_missing_receipt_failure_after_child_exit(smoke, tmp_path):
    with pytest.raises(
        RuntimeError, match="Timed out waiting for observer-stopped.json"
    ):
        smoke.wait_file(
            tmp_path / "observer-stopped.json", SimpleNamespace(poll=lambda: 1), 15
        )


@pytest.mark.parametrize(
    "malformed", ["[]", '{"stage": [], "code": {}}', "PRIVATE_INVALID_JSON"]
)
def test_malformed_error_receipt_fails_safely(smoke, tmp_path, malformed):
    (tmp_path / "command-error.json").write_text(malformed, encoding="utf-8")
    with pytest.raises(RuntimeError) as error:
        smoke.wait_file(
            tmp_path / "observer-stopped.json", SimpleNamespace(poll=lambda: None)
        )
    assert str(error.value) == "Continuity command failed (unknown/command_failed)"


@pytest.mark.parametrize("outcome", ["restored", "cancelled_after_prepare", "fresh"])
def test_restore_evidence_requires_published_live_state(
    smoke, memory, tmp_path, monkeypatch, outcome
):
    # Aetherra imports
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
    from Aetherra.consciousness.runtime_observer import ConsciousnessObserver
    from Aetherra.perception_bus.bus import PerceptionBus

    checkpoint = checkpoints.save(memory).result(timeout=2)
    observer = ConsciousnessObserver(
        readiness=lambda: None,
        observations=lambda: [],
        checkpoint_store=memory,
        continuity_enabled=True,
        restore_checkpoint_id=None if outcome == "fresh" else checkpoint.checkpoint_id,
    )
    core = ConsciousnessCore(PerceptionBus(), observer_only=True)
    if outcome == "cancelled_after_prepare":
        prepare = core.prepare_observer_checkpoint_restore

        def cancel_prepared(state):
            apply = prepare(state)
            observer._stop.set()
            return apply

        monkeypatch.setattr(
            core, "prepare_observer_checkpoint_restore", cancel_prepared
        )
    write = smoke.write_json

    def write_outside_lock(path, data):
        assert observer._lock.acquire(blocking=False), "restore evidence held lock"
        observer._lock.release()
        write(path, data)

    monkeypatch.setattr(smoke, "write_json", write_outside_lock)
    restore = smoke._observe_restore(
        ConsciousnessObserver._restore_checkpoint, tmp_path
    )
    assert restore(observer, core) is (outcome != "cancelled_after_prepare")
    artifact = tmp_path / "private-restored.json"
    if outcome == "restored":
        evidence = json.loads(artifact.read_text(encoding="utf-8"))
        assert evidence == {
            "thread": threading.current_thread().name,
            "checkpoint_id": checkpoint.checkpoint_id,
            "record_id": checkpoint.record_id,
            "tick_count": 0,
            "events_processed": 0,
            "aggregate": smoke.aggregate(checkpoints.payload()),
        }
    else:
        assert not artifact.exists()
