"""Temporal history and C2b share storage, never a job slot or retention policy."""

# Standard library imports
import json
import threading
import time

# Third party imports
import pytest

# Local imports
from . import test_memory_checkpoint_stream as checkpoint
from . import test_memory_lifecycle_checkpoint as legacy

policy = legacy.policy
memory = legacy.memory
governed = checkpoint.governed
approve_prune = checkpoint.approve_prune
approved_prune = checkpoint.approved_prune


@pytest.fixture
def history_memory(governed, policy):
    path = policy / "guardian.json"
    data = json.loads(path.read_text())
    data["allow"].extend(
        dict(data["allow"][0], action="consciousness.temporal_history_" + operation)
        for operation in ("acquire", "append", "read", "inspect")
    )
    path.write_text(json.dumps(data))
    return governed


def opening(memory):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import temporal_history as h

    selected = checkpoint.done(
        memory.submit_acquire_temporal_history(
            key=h.HistoryKey(h.OWNER, h.SCOPE, "a" * 32),
            start_mode="create",
            control=legacy.control(),
        )
    )
    source = h.TemporalSource("c" * 32, 10.0, 1, 11.0, 1.0, 3, 2, 1)
    request = h.AppendRequest(
        selected.token,
        selected.head,
        "d" * 32,
        (
            h.TemporalEvent("e" * 32, "session_start", source, 11.1, "created"),
            h.TemporalEvent("f" * 32, "observation", source, 11.1),
        ),
    )
    return selected, request


@pytest.mark.parametrize("phase", ["audit", "preflight", "postcommit"])
def test_temporal_external_io_does_not_hold_sqlite_writer_or_c2b_slot(
    history_memory, monkeypatch, phase
):
    # Aetherra imports
    import Aetherra.guardian.core as guardian
    from Aetherra.aetherra_core.memory import temporal_history_worker as worker

    memory = history_memory
    selected, request = opening(memory)
    core = checkpoint.done(checkpoint.acquire(memory))
    reached, release = threading.Event(), threading.Event()

    def pause():
        reached.set()
        assert release.wait(5), "test did not release Temporal external I/O"

    if phase == "audit":
        original = guardian.append_guardian_decision

        def audit(intent, *args, **kwargs):
            if intent.action == "consciousness.temporal_history_append":
                pause()
            return original(intent, *args, **kwargs)

        monkeypatch.setattr(guardian, "append_guardian_decision", audit)
    else:
        original = worker._recheck_policy
        calls = 0

        def recheck(intent):
            nonlocal calls
            original(intent)
            if intent.action == "consciousness.temporal_history_append":
                calls += 1
                if calls == (1 if phase == "preflight" else 2):
                    pause()

        monkeypatch.setattr(worker, "_recheck_policy", recheck)
    job = memory.submit_append_temporal_history(
        request=request, control=legacy.control()
    )
    try:
        assert reached.wait(1)
        assert memory.temporal_history_pending()
        assert job.outstanding
        # This is a real governed C2b write while Temporal has not settled.
        saved = checkpoint.done(
            checkpoint.advance(memory, checkpoint.request(core.token, core.head, 1))
        )
        assert saved.head.generation == 1
        assert memory.temporal_history_pending()
        job.cancel()
        start = time.monotonic()
        assert job.poll(local_owned=True).error_code == "uncertain"
        assert job.outstanding
        assert time.monotonic() - start < 0.1
    finally:
        release.set()
    checkpoint.done(job, "uncertain")
    page = checkpoint.done(
        memory.submit_read_temporal_history(
            token=selected.token,
            selected_head=request.expected_head,
            after_ordinal=0,
            limit=1,
            control=legacy.control(),
        )
    )
    assert page.records == ()
    # Empty-prefix read is valid even after postcommit uncertainty advanced the head.
    count = memory.conn.execute(
        "SELECT count(*) FROM temporal_history_records"
    ).fetchone()[0]
    assert count == (2 if phase == "postcommit" else 0)


def test_c2b_pruning_preserves_exact_temporal_history(history_memory, approved_prune):
    memory = history_memory
    selected, request = opening(memory)
    receipt = checkpoint.done(
        memory.submit_append_temporal_history(request=request, control=legacy.control())
    )
    before = memory.conn.execute(
        "SELECT * FROM temporal_history_records ORDER BY ordinal"
    ).fetchall()
    core = checkpoint.done(checkpoint.acquire(memory, retain=2))
    head = checkpoint.fill(memory, core, [1, 2, 3])
    pruned = checkpoint.done(approved_prune(memory, core, head, 2))
    assert pruned.deleted_count == 1
    assert checkpoint.members(memory) == [(2,), (3,)]
    assert (
        memory.conn.execute(
            "SELECT * FROM temporal_history_records ORDER BY ordinal"
        ).fetchall()
        == before
    )
    page = checkpoint.done(
        memory.submit_read_temporal_history(
            token=selected.token,
            selected_head=receipt.head,
            after_ordinal=0,
            limit=64,
            control=legacy.control(),
        )
    )
    assert page.records == receipt.records
    assert all(
        row[0] not in {r.event.record_id for r in page.records}
        for row in legacy.rows(memory)
    )
    core_head = memory.conn.execute(
        "SELECT generation,record_id FROM checkpoint_stream_heads"
    ).fetchone()
    assert core_head == (head.generation, head.record_id)


def test_shared_audit_stall_keeps_c2b_deadline_truthful(history_memory, monkeypatch):
    # Aetherra imports
    from Aetherra.security.audit_ledger import SecurityAuditLedger

    memory = history_memory
    _, request = opening(memory)
    core = checkpoint.done(checkpoint.acquire(memory))
    reached, release = threading.Event(), threading.Event()
    original = SecurityAuditLedger._append_bytes

    def blocked_write(ledger, encoded):
        intent = json.loads(encoded)["details"].get("intent", {})
        if intent.get("action") == "consciousness.temporal_history_append":
            reached.set()
            assert release.wait(5), "test did not release shared signed-audit write"
        return original(ledger, encoded)

    monkeypatch.setattr(SecurityAuditLedger, "_append_bytes", blocked_write)
    temporal = memory.submit_append_temporal_history(
        request=request, control=legacy.control()
    )
    try:
        assert reached.wait(1)
        started = time.monotonic()
        c2b = checkpoint.advance(
            memory,
            checkpoint.request(core.token, core.head, 1),
            deadline=started + 0.15,
        )
        completion = None
        while completion is None and time.monotonic() - started < 0.6:
            completion = c2b.poll(local_owned=True)
            time.sleep(0.001)
        assert completion.error_code == "uncertain"
        assert time.monotonic() - started < 0.6
        assert c2b.outstanding
        assert temporal.outstanding
        connection = memory.conn
        assert memory.close() is False
        assert memory.conn is connection
    finally:
        release.set()
    checkpoint.done(temporal, "uncertain")
    checkpoint.done(c2b, "uncertain")
    assert memory.conn.execute(
        "SELECT generation FROM checkpoint_stream_heads"
    ).fetchone() == (0,)
    assert (
        memory.conn.execute("SELECT count(*) FROM temporal_history_records").fetchone()[
            0
        ]
        == 0
    )
    assert memory.close()
