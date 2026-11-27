"""Governed Temporal history admission on the real Memory and Guardian stack."""

# Standard library imports
import asyncio
import gc
import json
import sqlite3
import threading
import time
import weakref

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from Aetherra.security.audit_ledger import SecurityAuditLedger

# Local imports
from . import test_memory_lifecycle_checkpoint as legacy

policy = legacy.policy
memory = legacy.memory


def api():
    # Aetherra imports
    from Aetherra.aetherra_core.memory import temporal_history

    return temporal_history


def acquire(system, mode="create", *, control=None):
    submit = system.submit_acquire_temporal_history
    history = api()
    return submit(
        key=history.HistoryKey(history.OWNER, history.SCOPE, "b" * 32),
        start_mode=mode,
        control=control or legacy.control(),
    )


def append(system, request, *, control=None):
    return system.submit_append_temporal_history(
        request=request, control=control or legacy.control()
    )


def first_append(selection):
    history = api()
    source = history.TemporalSource("a" * 32, 12.25, 5, 17.875, 5.625, 7, 11, 13)
    return history.AppendRequest(
        selection.token,
        selection.head,
        "c" * 32,
        (
            history.TemporalEvent("d" * 32, "session_start", source, 19.125, "created"),
            history.TemporalEvent("e" * 32, "observation", source, 19.125),
        ),
    )


def done(job, code=None):
    deadline = time.monotonic() + 3
    while job.outstanding and time.monotonic() < deadline:
        time.sleep(0.001)
    assert not job.outstanding
    completion = job.poll(local_owned=True)
    assert completion.error_code == code
    return completion.value


@pytest.fixture
def temporal_policy(policy):
    guardian = policy / "guardian.json"
    rules = json.loads(guardian.read_text(encoding="utf-8"))
    for operation in ("acquire", "append", "read", "inspect"):
        rules["allow"].append(
            dict(
                rules["allow"][0], action=f"consciousness.temporal_history_{operation}"
            )
        )
    guardian.write_text(json.dumps(rules), encoding="utf-8")
    return policy


def test_acquire_denial_leaves_selected_database_unchanged(memory, monkeypatch):
    legacy.forbid_open(monkeypatch)
    done(acquire(memory), "denied")


@pytest.mark.parametrize("missing", ["memory:read", "memory:write", "fs:write"])
def test_acquire_requires_each_capability(
    memory, temporal_policy, monkeypatch, missing
):
    capabilities = temporal_policy / "capabilities.json"
    data = json.loads(capabilities.read_text(encoding="utf-8"))
    data["allow"]["consciousness:core"].remove(missing)
    capabilities.write_text(json.dumps(data), encoding="utf-8")
    legacy.forbid_open(monkeypatch)
    done(acquire(memory), "denied")


def test_missing_history_is_distinct_from_closed_admission(memory, temporal_policy):
    done(acquire(memory, "resume"), "missing")
    assert memory.drain_temporal_history(0.5)
    refused = acquire(memory)
    assert not refused.admitted
    done(refused, "unavailable")
    assert memory.conn is not None


def test_in_memory_database_cannot_open_an_independent_history(temporal_policy):
    with LyrixaMemorySystem() as system:
        refused = acquire(system)
        assert not refused.admitted
        done(refused, "unavailable")


def test_temporal_audit_carries_identity_and_digest_without_event_content(
    memory, temporal_policy, tmp_path
):
    selection = done(acquire(memory))
    request = first_append(selection)
    receipt = done(append(memory, request))
    ledger = tmp_path / ".aetherra/security/audit.jsonl"
    assert SecurityAuditLedger(ledger).verify_integrity(require_signed_records=True)
    records = [
        json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
    ]
    entry = next(entry for entry in records if entry["hash"] == receipt.audit_id)
    intent = entry["details"]["intent"]
    assert intent["action"] == "consciousness.temporal_history_append"
    assert intent["metadata"] == {
        "history_id": selection.token.key.history_id,
        "operation_id": request.operation_id,
        # The shared Security audit heuristic redacts token-like strings.
        "request_digest": "***REDACTED***",
    }
    assert "19.125" not in json.dumps(intent)
    assert "active_intention_count" not in json.dumps(intent)


def test_closed_result_polling_retains_the_slot_through_blocked_audit(
    memory, temporal_policy, monkeypatch
):
    entered, release = legacy.blocked_audit(monkeypatch)
    caller = threading.get_ident()
    owned_threads = []

    def owned():
        owned_threads.append(threading.get_ident())
        return True

    control = legacy.control(owned=owned)
    job = acquire(memory, control=control)
    try:
        assert entered.wait(2)
        assert job.poll(local_owned=True) is None
        assert memory.temporal_history_pending()
        # Audit is blocked before SQLite locks the database.
        memory.conn.execute("BEGIN IMMEDIATE")
        memory.conn.rollback()
        assert job.poll(local_owned=False).error_code == "uncertain"
        assert job.poll(local_owned=True).error_code == "uncertain"
        assert job.outstanding
        done(acquire(memory), "busy")
        assert not memory.drain_temporal_history(0)
        assert memory.conn is not None
        assert caller not in owned_threads
    finally:
        release.set()
    done(job, "uncertain")
    assert memory.drain_temporal_history(1)
    assert not memory.temporal_history_pending()


def test_sqlite_writer_contention_returns_busy_without_holding_the_slot(
    memory, temporal_policy
):
    memory.conn.execute("BEGIN IMMEDIATE")
    try:
        started = time.monotonic()
        done(acquire(memory), "busy")
        assert time.monotonic() - started < 1
        assert not memory.temporal_history_pending()
    finally:
        memory.conn.rollback()
    assert done(acquire(memory)).head.ordinal == 0


def test_late_commit_remains_uncertain_until_a_new_epoch_inspects(
    memory, temporal_policy, monkeypatch
):
    capabilities = temporal_policy / "capabilities.json"
    original_policy = capabilities.read_text(encoding="utf-8")
    reached, release, armed = (threading.Event() for _ in range(3))
    connect = sqlite3.connect

    class PausedCommit(sqlite3.Connection):
        def commit(self):
            super().commit()
            if armed.is_set():
                reached.set()
                assert release.wait(3)

    def connect_worker(*args, **kwargs):
        if kwargs.get("uri"):
            kwargs["factory"] = PausedCommit
        return connect(*args, **kwargs)

    monkeypatch.setattr(sqlite3, "connect", connect_worker)
    first = done(acquire(memory))
    request = first_append(first)
    armed.set()
    job = append(memory, request)
    try:
        assert reached.wait(2)
        capabilities.write_text('{"allow": {}}', encoding="utf-8")
        assert job.outstanding
        done(acquire(memory, "resume"), "busy")
    finally:
        armed.clear()
        release.set()

    done(job, "uncertain")
    capabilities.write_text(original_policy, encoding="utf-8")
    selection = done(acquire(memory, "resume"))
    inspected = done(
        memory.submit_inspect_temporal_append(
            token=selection.token, request=request, control=legacy.control()
        )
    )
    assert inspected.status == "committed_current"
    assert inspected.receipt.head == selection.head
    assert inspected.receipt.request_digest == request.digest()


def test_advanced_and_adapter_forward_only_to_their_original_core(
    memory, temporal_policy, monkeypatch, tmp_path
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngineAdvanced,
    )

    monkeypatch.chdir(tmp_path)
    # Aetherra imports
    from aetherra_os_launcher import MemoryAdapter

    advanced = AetherraMemoryEngineAdvanced()
    original = advanced.core_memory
    adapter = MemoryAdapter(advanced)
    try:
        selection = done(acquire(adapter))
        request = first_append(selection)
        receipt = done(append(advanced, request))
        page = done(
            adapter.submit_read_temporal_history(
                token=selection.token,
                selected_head=receipt.head,
                after_ordinal=0,
                limit=64,
                control=legacy.control(),
            )
        )
        assert page.selected_head == receipt.head
        assert tuple(record.event for record in page.records) == request.events
        assert page.next_ordinal == 2
        entered, release = legacy.blocked_audit(monkeypatch)
        pending = acquire(adapter, "resume")
        try:
            assert entered.wait(2)
            advanced.core_memory = memory
            for backend in (adapter, advanced):
                refused = acquire(backend)
                assert not refused.admitted
                done(refused, "unavailable")
            assert adapter.temporal_history_pending()
            assert advanced.temporal_history_pending()
            assert not adapter.drain_temporal_history(0)
        finally:
            release.set()
        done(pending, "uncertain")
        assert advanced.drain_temporal_history(0.5)
        assert not adapter.temporal_history_pending()
        done(acquire(memory, "resume"), "missing")
    finally:
        assert original.close()


@pytest.mark.parametrize("entrypoint", ["close", "close_connection"])
def test_core_close_keeps_connection_until_temporal_job_settles(
    memory, temporal_policy, monkeypatch, entrypoint
):
    close = getattr(memory, entrypoint)
    original = memory.conn
    entered, release = legacy.blocked_audit(monkeypatch)
    job = acquire(memory)
    try:
        assert entered.wait(2)
        started = time.monotonic()
        assert close() is False
        assert time.monotonic() - started < 1.3
        assert memory.conn is original
        assert job.outstanding
        assert memory.temporal_history_pending()
        refused = acquire(memory)
        assert not refused.admitted
        done(refused, "unavailable")
    finally:
        release.set()
    done(job, "uncertain")
    assert close() is True
    assert memory.conn is None
    assert not memory.temporal_history_pending()
    legacy.error(legacy.save(memory), "unavailable")


def test_read_and_selection_can_recheck_authority_before_application(
    memory, temporal_policy
):
    acquisition = acquire(memory)
    selection = done(acquisition)
    acquisition.check_restore_policy()
    assert acquisition.restore_window_open()

    receipt = done(append(memory, first_append(selection)))
    read = memory.submit_read_temporal_history(
        token=selection.token,
        selected_head=receipt.head,
        after_ordinal=0,
        limit=64,
        control=legacy.control(),
    )
    done(read)
    read.check_restore_policy()
    assert read.restore_window_open()

    capabilities = temporal_policy / "capabilities.json"
    capabilities.write_text('{"allow": {}}', encoding="utf-8")
    with pytest.raises(legacy.api().CheckpointError, match="^denied$"):
        read.check_restore_policy()
    assert read.poll(local_owned=True).value.selected_head == receipt.head


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_shutdown", [False, True])
async def test_engine_shutdown_drains_real_memory_without_blocking_the_loop(
    temporal_policy, monkeypatch, tmp_path, cancel_shutdown
):
    # Aetherra imports
    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    engine = AetherraEngine(
        memory_db_path=str(tmp_path / "memory.db"),
        reasoning_db_path=str(tmp_path / "reasoning.db"),
        improvement_db_path=str(tmp_path / "improvement.db"),
        orchestrator_db_path=str(tmp_path / "orchestrator.json"),
    )
    engine._llm_manager = None
    engine.initialized = True
    core = engine.memory_system
    entered, release = legacy.blocked_audit(monkeypatch)
    job = acquire(core)

    loop = asyncio.get_running_loop()
    close_started = asyncio.Event()
    close_threads = []
    original_close = core.close_connection

    def tracked_close():
        close_threads.append(threading.get_ident())
        loop.call_soon_threadsafe(close_started.set)
        return original_close()

    monkeypatch.setattr(core, "close_connection", tracked_close)
    timer = None
    try:
        assert await asyncio.to_thread(entered.wait, 2)
        shutdown = asyncio.create_task(engine.shutdown())
        await asyncio.wait_for(close_started.wait(), timeout=2)
        if cancel_shutdown:
            shutdown.cancel()
            with pytest.raises(asyncio.CancelledError):
                await shutdown
            assert core.temporal_history_pending()
            engine.memory_system = object()

        timer = loop.call_later(0.01, release.set)
        if cancel_shutdown:
            await engine.shutdown()
        else:
            await shutdown

        assert release.is_set()
        assert core.conn is None
        assert not core.temporal_history_pending()
        assert len(close_threads) == 1
        assert threading.get_ident() not in close_threads
        done(job, "uncertain")
    finally:
        if timer is not None:
            timer.cancel()
        release.set()
        assert await asyncio.to_thread(core.close)


@pytest.mark.parametrize(
    "after_commit", [False, True], ids=["before_io", "after_commit"]
)
def test_cancelled_owner_callback_settles_and_wakes(
    memory, temporal_policy, after_commit
):
    def has_history():
        return (
            memory.conn.execute(
                "SELECT 1 FROM sqlite_master WHERE name='temporal_history_heads'"
            ).fetchone()
            is not None
        )

    def owned():
        if not after_commit or has_history():
            raise asyncio.CancelledError
        return True

    wake = threading.Event()
    control = legacy.api().CheckpointJobControl(
        threading.Event(), time.monotonic() + 1, owned, wake
    )
    job = acquire(memory, control=control)
    assert wake.wait(2)
    done(job, "uncertain")
    assert not memory.temporal_history_pending()
    assert has_history() is after_commit
    assert (
        done(acquire(memory, "resume" if after_commit else "create")).head.ordinal == 0
    )


def test_unexpected_daemon_exit_closes_and_settles(
    memory, temporal_policy, monkeypatch
):
    # The default thread hook ignores a deliberate SystemExit.
    monkeypatch.setattr(threading, "excepthook", threading.__excepthook__)

    def stop():
        raise SystemExit

    wake = threading.Event()
    job = acquire(
        memory,
        control=legacy.api().CheckpointJobControl(
            threading.Event(), time.monotonic() + 1, stop, wake
        ),
    )
    thread = memory._temporal_history._thread
    thread.join(2)
    assert not thread.is_alive()
    assert wake.is_set()
    done(job, "uncertain")
    refused = acquire(memory)
    assert not refused.admitted
    done(refused, "unavailable")
    assert memory.drain_temporal_history(0.5)
    assert not memory.temporal_history_pending()


@pytest.mark.parametrize("owned", [False, True], ids=["lost_owner", "success"])
def test_idle_daemon_releases_last_core(temporal_policy, tmp_path, owned):
    core = LyrixaMemorySystem(str(tmp_path / "collect.db"))
    ref = weakref.ref(core)
    try:
        done(acquire(core))
        job = acquire(core, "resume", control=legacy.control(owned=lambda: owned))
        done(job, None if owned else "uncertain")
        thread = core._temporal_history._thread
        del core, job
        gc.collect()
        thread.join(1)
        assert ref() is None
        assert not thread.is_alive()
    finally:
        if ref() is not None:
            ref().close()


def test_invalid_database_reports_corrupt_at_worker_boundary(temporal_policy, tmp_path):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.temporal_history_worker import (
        TemporalHistoryWorker,
    )

    path = tmp_path / "invalid.db"
    original = b"non-SQLite contents" * 32
    path.write_bytes(original)
    worker = TemporalHistoryWorker(str(path))
    history = api()
    try:
        job = worker.submit(
            operation="acquire",
            key=history.HistoryKey(history.OWNER, history.SCOPE, "b" * 32),
            start_mode="resume",
            control=legacy.control(),
        )
        done(job, "corrupt")
        assert path.read_bytes() == original
    finally:
        assert worker.shutdown()
