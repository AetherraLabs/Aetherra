"""Atomic stream transactions against the actual governed Memory database."""

# Standard library imports
import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import asdict, replace
from datetime import datetime, timedelta

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from Aetherra.consciousness.checkpoint import decode_checkpoint, dump_checkpoint_json
from Aetherra.security.audit_ledger import SecurityAuditLedger

# Local imports
from . import test_memory_lifecycle_checkpoint as legacy

policy = legacy.policy
memory = legacy.memory


def api():
    # Aetherra imports
    from Aetherra.aetherra_core.memory import checkpoint_stream

    return checkpoint_stream


@pytest.fixture
def governed(memory, policy):
    guardian = policy / "guardian.json"
    rules = json.loads(guardian.read_text())
    for operation in ("acquire", "advance", "prune"):
        rules["allow"].append(
            dict(rules["allow"][0], action="consciousness.continuity_" + operation)
        )
    guardian.write_text(json.dumps(rules))
    return memory


def acquire(system, mode="create", retain=10, control=None):
    key = api().StreamKey(legacy.OWNER, legacy.SCOPE, "b" * 32)
    return system.submit_acquire_checkpoint_stream(
        key=key,
        start_mode=mode,
        retain_checkpoints=retain,
        control=control or legacy.control(),
    )


def wait_for_worker(job):
    timeout = time.monotonic() + 3
    while job.outstanding and time.monotonic() < timeout:
        time.sleep(0.001)
    assert not job.outstanding


def done(job, code=None):
    wait_for_worker(job)
    result = job.poll(local_owned=True)
    assert result.error_code == code
    return result.value


def request(token, head, n, metadata=None):
    handle = f"{n:032x}"
    data = dump_checkpoint_json(decode_checkpoint(legacy.payload(handle)))
    metadata = metadata or api().SnapshotMetadata(
        1, "c" * 32, 140, 126, 123.0, 1.0, 2.0, "periodic"
    )
    meta = metadata.to_bytes()
    attempt = api().AttemptDescriptor(
        token,
        head,
        f"{n + 1000:032x}",
        handle,
        hashlib.sha256(data).hexdigest(),
        hashlib.sha256(meta).hexdigest(),
    )
    return api().AdvanceRequest(attempt, data, meta)


def advance(system, req, **kwargs):
    return system.submit_advance_checkpoint_stream(
        request=req, control=legacy.control(**kwargs)
    )


def test_stream_create_resume_and_conflicts(governed, tmp_path):
    db = governed
    loose = legacy.save(db).result(2)
    before = legacy.rows(db)
    done(acquire(db, "resume"), "missing")
    first = done(acquire(db))
    assert first.token.writer_epoch == 1
    assert first.head == api().StreamHead(0, None, None, None, None)
    assert first.checkpoint is first.metadata is None
    done(acquire(db), "conflict")
    req = request(first.token, first.head, 1)
    receipt = done(advance(db, req))
    assert receipt.attempt == req.attempt
    assert receipt.head.generation == 1
    assert receipt.head.checkpoint_id == f"{1:032x}"
    resumed = done(acquire(db, "resume"))
    assert resumed.token.writer_epoch == 2
    assert resumed.head == receipt.head
    assert resumed.checkpoint.record_id == receipt.head.record_id
    assert resumed.checkpoint.payload == legacy.payload(f"{1:032x}")
    assert resumed.metadata.captured_at_unix_s == 123
    assert not resumed.retention_needed
    assert before[0] in legacy.rows(db)
    assert loose.record_id != receipt.head.record_id
    catalog = db.conn.execute(
        "SELECT record_id, audit_id, predecessor_head_digest FROM checkpoint_stream_commits"
    ).fetchone()
    assert catalog[:2] == (receipt.head.record_id, receipt.audit_id)
    empty = b'{"checkpoint_id":null,"generation":0,"metadata_digest":null,"payload_digest":null,"record_id":null}'
    assert catalog[2] == hashlib.sha256(empty).hexdigest()
    ledger = tmp_path / ".aetherra/security/audit.jsonl"
    assert SecurityAuditLedger(ledger).verify_integrity(require_signed_records=True)
    assert receipt.audit_id in ledger.read_text()
    assert "checkpoint_only_sentinel" not in ledger.read_text()


@pytest.mark.parametrize(
    ("fault", "error"), [("ABORT,'fault'", "unavailable"), ("IGNORE", "conflict")]
)
def test_advance_is_payload_catalog_head_atomic(governed, fault, error):
    db = governed
    first = done(acquire(db))
    db.conn.execute(
        f"CREATE TRIGGER fail_head BEFORE UPDATE OF generation ON checkpoint_stream_heads BEGIN SELECT RAISE({fault}); END"
    )
    req = request(first.token, first.head, 2)
    result = advance(db, req)
    done(result, error)
    assert legacy.rows(db) == []
    assert db.conn.execute(
        "SELECT COUNT(*) FROM checkpoint_stream_commits"
    ).fetchone() == (0,)
    assert db.conn.execute(
        "SELECT generation, record_id FROM checkpoint_stream_heads"
    ).fetchone() == (0, None)


@pytest.mark.parametrize(
    "corruption",
    [
        "content",
        "extra_handle",
        "metadata",
        "missing_entry",
        "predecessor",
        "oversized_digest",
    ],
)
def test_corrupt_head_prevents_takeover(governed, corruption):
    db = governed
    first = done(acquire(db))
    done(advance(db, request(first.token, first.head, 1)))
    if corruption == "content":
        db.conn.execute("UPDATE memories SET content=replace(content,'-0.4','-0.3')")
    if corruption == "extra_handle":
        db.conn.execute(
            "INSERT INTO memories SELECT 'loose', content,context,tags,importance,created_at,last_accessed,access_count,memory_type FROM memories LIMIT 1"
        )
    if corruption == "metadata":
        db.conn.execute("UPDATE checkpoint_stream_commits SET metadata_bytes=x'7b7d'")
    if corruption == "missing_entry":
        db.conn.execute("DELETE FROM checkpoint_stream_commits")
    if corruption == "oversized_digest":
        db.conn.execute(
            "UPDATE checkpoint_stream_heads SET metadata_digest=zeroblob(300000)"
        )
    if corruption == "predecessor":
        db.conn.execute(
            "UPDATE checkpoint_stream_commits SET predecessor_head_digest=?",
            ("1" * 64,),
        )
    db.conn.commit()
    done(acquire(db, "resume"), "corrupt")
    assert db.conn.execute(
        "SELECT writer_epoch, generation FROM checkpoint_stream_heads"
    ).fetchone() == (1, 1)


def test_competing_writers_cas(governed):
    first = done(acquire(governed))
    with LyrixaMemorySystem(governed.db_path) as other:
        barrier = threading.Barrier(2)

        def gate():
            if not getattr(seen, "arrived", False):
                seen.arrived = True
                barrier.wait(1)
            return True

        seen = threading.local()
        jobs = [
            advance(db, request(first.token, first.head, i), owned=gate)
            for i, db in enumerate((governed, other), 1)
        ]
        for job in jobs:
            wait_for_worker(job)
        results = [job.poll(local_owned=True) for job in jobs]
    assert {result.error_code for result in results} == {None, "conflict"}
    winner = next(result.value for result in results if result.value)
    assert [row[0] for row in legacy.rows(governed)] == [winner.head.record_id]


def test_acquire_fences_delayed_old_worker(governed):
    first = done(acquire(governed))
    entered, release = threading.Event(), threading.Event()

    def held():
        entered.set()
        return release.wait(2)

    with LyrixaMemorySystem(governed.db_path) as other:
        delayed = advance(governed, request(first.token, first.head, 1), owned=held)
        try:
            assert entered.wait(1)
            newer = done(acquire(other, "resume"))
        finally:
            release.set()
        done(delayed, "writer_fenced")
    assert newer.token.writer_epoch == 2
    assert legacy.rows(governed) == []


@pytest.mark.parametrize("lower", [True, False])
def test_advance_enforces_current_epoch_capacity(governed, lower):
    first = done(acquire(governed, retain=10 if lower else 2))
    head = first.head
    for n in range(1, 4 if not lower else 6):
        head = done(advance(governed, request(first.token, head, n))).head
    if lower:
        first = done(acquire(governed, "resume", retain=2))
        assert first.retention_needed
    before = legacy.rows(governed)
    done(advance(governed, request(first.token, head, 9)), "capacity")
    assert legacy.rows(governed) == before


@pytest.mark.parametrize("operation", ["acquire", "advance"])
@pytest.mark.parametrize("fault", ["deny", "caps", "audit"])
def test_denied_or_unaudited_stream_operation_never_opens_database(
    governed, policy, monkeypatch, operation, fault
):
    # Aetherra imports
    import Aetherra.guardian.core as guardian

    with LyrixaMemorySystem(governed.db_path) as other:
        first = done(acquire(governed)) if operation == "advance" else None
        if fault == "deny":
            (policy / "guardian.json").write_text('{"version":1,"default":"deny"}')
        elif fault == "caps":
            cap_path = policy / "capabilities.json"
            caps = json.loads(cap_path.read_text())
            caps["allow"]["consciousness:core"].remove("memory:read")
            cap_path.write_text(json.dumps(caps))
        else:
            monkeypatch.setattr(guardian, "append_guardian_decision", lambda *args: " ")
        legacy.forbid_open(monkeypatch)
        job = (
            advance(other, request(first.token, first.head, 1))
            if first
            else acquire(other)
        )
        done(job, "audit_failed" if fault == "audit" else "denied")
    assert legacy.rows(governed) == []


def test_metadata_freezes_and_round_trips(governed, monkeypatch):
    first = done(acquire(governed))
    req = request(first.token, first.head, 1)
    meta = api().SnapshotMetadata.from_bytes(req.metadata_bytes)
    assert meta.session_started_at_unix_s > meta.captured_at_unix_s
    for field, value in [
        ("schema", True),
        ("observation_uptime_s", 3),
        ("capture_uptime_s", -1),
        ("captured_at_unix_s", float("nan")),
        ("observation_uptime_s", True),
        ("session_started_at_unix_s", float("inf")),
    ]:
        with pytest.raises(legacy.api().CheckpointError):
            replace(meta, **{field: value})
    for raw in [
        req.metadata_bytes + b" " * 4097,
        json.dumps(dict(asdict(meta), extra=1)).encode(),
        req.metadata_bytes.replace(b'"schema":1', b'"schema":1,"schema":1'),
    ]:
        with pytest.raises(legacy.api().CheckpointError):
            api().SnapshotMetadata.from_bytes(raw)
    with pytest.raises(legacy.api().CheckpointError):
        replace(req, attempt=replace(req.attempt, metadata_digest="1" * 64))
    with pytest.raises(legacy.api().CheckpointError):
        request(first.token, first.head, 1, replace(meta, captured_at_unix_s=124))
    source = bytearray(req.metadata_bytes)
    frozen = replace(req, metadata_bytes=source)
    entered, release = legacy.blocked_audit(monkeypatch)
    job = advance(governed, frozen)
    try:
        assert entered.wait(1)
        source[:] = b"changed"
        busy = acquire(governed)
        assert not busy.admitted
        done(busy, "busy")
    finally:
        release.set()
    done(job)
    resumed = done(acquire(governed, "resume"))
    assert resumed.metadata == meta


@pytest.mark.parametrize("fault", ["cancel", "deadline", "owner"])
def test_sealed_receipt_requires_timely_local_consumption(governed, monkeypatch, fault):
    job = acquire(governed)
    wait_for_worker(job)
    if fault == "cancel":
        job.cancel()
    elif fault == "deadline":
        future_time = time.monotonic() + 2
        monkeypatch.setattr(time, "monotonic", lambda: future_time)
    assert job.poll(local_owned=fault != "owner").error_code == "uncertain"
    assert job.admitted
    assert job.acceptance_closed
    assert job.poll(local_owned=True).error_code == "uncertain"


def test_older_pinned_head_allows_one_extra_member(governed):
    first = done(acquire(governed, retain=2))
    done(advance(governed, request(first.token, first.head, 1)))
    pinned = done(acquire(governed, "resume", retain=2))
    head = pinned.head
    for n in (2, 3, 4):
        head = done(advance(governed, request(pinned.token, head, n))).head
    assert governed.conn.execute(
        "SELECT restore_pin_generation,generation FROM checkpoint_stream_heads"
    ).fetchone() == (1, 4)
    done(advance(governed, request(pinned.token, head, 5)), "capacity")
    assert len(legacy.rows(governed)) == 4


@pytest.mark.parametrize("phase", ["before_policy", "after_policy", "owner_loss"])
def test_final_governance_observation_and_worker_wake(
    governed, policy, monkeypatch, phase
):
    committed, reached, release, wake = (threading.Event() for _ in range(4))
    original = sqlite3.connect

    def pause():
        reached.set()
        assert release.wait(2)

    class ObservedConnection(sqlite3.Connection):
        def commit(self):
            super().commit()
            committed.set()
            if phase == "before_policy":
                pause()

    monkeypatch.setattr(
        sqlite3,
        "connect",
        lambda *a, **kw: original(*a, **kw, factory=ObservedConnection),
    )

    def owned():
        if committed.is_set() and phase != "before_policy":
            pause()
            return phase != "owner_loss"
        return True

    ctl = replace(legacy.control(owned=owned), wake_event=wake)
    job = acquire(governed, control=ctl)
    try:
        assert reached.wait(1)
        assert governed.lifecycle_checkpoint_pending()
        assert job.outstanding
        assert job.poll(local_owned=True) is None
        assert not wake.is_set()
        (policy / "capabilities.json").write_text('{"allow":{}}')
    finally:
        release.set()
    assert wake.wait(1)
    assert not governed.lifecycle_checkpoint_pending()
    assert not job.outstanding
    result = job.poll(local_owned=True)
    if phase == "after_policy":
        assert result.value.token.writer_epoch == 1
        assert job.acceptance_closed
        expired = time.monotonic() + 2
        monkeypatch.setattr(time, "monotonic", lambda: expired)
        assert job.poll(local_owned=True) is result
        job.cancel()
        assert job.poll(local_owned=False) is result
    else:
        assert result.error_code == "uncertain"
        assert result.value is None
    assert governed.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (1,)


def test_cancelled_worker_owns_slot_until_real_completion(governed, monkeypatch):
    entered, release = legacy.blocked_audit(monkeypatch)
    job = acquire(governed)
    try:
        assert entered.wait(1)
        job.cancel()
        assert job.acceptance_closed
        assert job.outstanding
        assert job.poll(local_owned=True).error_code == "uncertain"
        refused = acquire(governed)
        assert not refused.admitted
        assert refused.acceptance_closed
        refused.cancel()
        done(refused, "busy")
    finally:
        release.set()
    done(job, "uncertain")
    assert governed.conn.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name='checkpoint_stream_heads'"
    ).fetchone() == (0,)


def test_acquired_payload_cannot_mutate_sealed_result(governed):
    first = done(acquire(governed))
    done(advance(governed, request(first.token, first.head, 1)))
    job = acquire(governed, "resume")
    accepted = done(job)
    accepted.checkpoint.payload["trust"]["subsystems"].clear()
    assert job.poll(local_owned=True).value.checkpoint.payload == legacy.payload(
        f"{1:032x}"
    )


@pytest.mark.parametrize(
    "ddl",
    [
        "CREATE TABLE checkpoint_stream_commits (id TEXT PRIMARY KEY)",
        "CREATE VIEW checkpoint_stream_heads AS SELECT id FROM memories",
    ],
)
def test_partial_or_impostor_schema_is_preserved(governed, ddl):
    governed.conn.execute(ddl)
    before = governed.conn.execute(
        "SELECT name,sql FROM sqlite_master ORDER BY name"
    ).fetchall()
    done(acquire(governed), "corrupt")
    assert (
        governed.conn.execute(
            "SELECT name,sql FROM sqlite_master ORDER BY name"
        ).fetchall()
        == before
    )


def test_expected_head_must_match_exact_rows(governed):
    first = done(acquire(governed))
    head = done(advance(governed, request(first.token, first.head, 1))).head
    mismatched = replace(head, metadata_digest="f" * 64)
    done(advance(governed, request(first.token, mismatched, 2)), "conflict")
    assert [r[0] for r in legacy.rows(governed)] == [head.record_id]


def test_refused_job_cannot_cancel_admitted_job_sharing_control(governed, monkeypatch):
    entered, release = legacy.blocked_audit(monkeypatch)
    ctl = legacy.control()
    active = acquire(governed, control=ctl)
    try:
        assert entered.wait(1)
        refused = acquire(governed, control=ctl)
        refused.cancel()
        done(refused, "busy")
    finally:
        release.set()
    assert done(active).token.writer_epoch == 1


def test_cancel_before_seal_latches_even_if_not_polled_until_drain(
    governed, monkeypatch
):
    entered, release = legacy.blocked_audit(monkeypatch)
    job = acquire(governed)
    try:
        assert entered.wait(1)
        job.cancel()
    finally:
        release.set()
    done(job, "uncertain")


@pytest.mark.parametrize("n", [True, 1, 101, 2.0])
def test_invalid_retention_is_not_admitted(governed, monkeypatch, n):
    legacy.forbid_open(monkeypatch)
    job = acquire(governed, retain=n)
    assert not job.admitted
    done(job, "invalid")


@pytest.fixture
def backends(governed, tmp_path, monkeypatch):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngineAdvanced,
    )

    monkeypatch.chdir(tmp_path)
    # Aetherra imports
    from aetherra_os_launcher import MemoryAdapter

    engine = AetherraMemoryEngineAdvanced()
    original = engine.core_memory
    try:
        yield MemoryAdapter(engine), engine, original
    finally:
        assert original.close()


def test_adapter_uses_only_original_advanced_core(governed, backends):
    adapter, engine, original = backends
    first = done(acquire(adapter))
    receipt = done(advance(adapter, request(first.token, first.head, 1)))
    assert [r[0] for r in legacy.rows(original)] == [receipt.head.record_id]
    engine.core_memory = governed
    for backend in (adapter, engine):
        refusal = acquire(backend)
        assert not refusal.admitted
        done(refusal, "unavailable")
    assert not legacy.rows(governed)


@pytest.mark.parametrize("target", ["adapter", "advanced"])
@pytest.mark.parametrize("operation", ["acquire", "advance", "prune"])
@pytest.mark.parametrize("phase", ["audit", "committed"])
def test_forwarding_chain_checked_through_handoff(
    governed, backends, monkeypatch, target, operation, phase, approved_prune
):
    adapter, engine, original = backends
    backend = adapter if target == "adapter" else engine
    reached, release, armed = (threading.Event() for _ in range(3))
    connect = sqlite3.connect

    class PausedCommit(sqlite3.Connection):
        def commit(self):
            super().commit()
            if armed.is_set():
                reached.set()
                assert release.wait(2)

    monkeypatch.setattr(
        sqlite3, "connect", lambda *a, **kw: connect(*a, **kw, factory=PausedCommit)
    )
    first = done(acquire(backend))
    if phase == "audit":
        reached, release = legacy.blocked_audit(monkeypatch)
    else:
        armed.set()
    if operation == "acquire":
        job = acquire(backend, "resume")
    elif operation == "advance":
        job = advance(backend, request(first.token, first.head, 1))
    else:
        job = approved_prune(backend, first, first.head, 10)
    try:
        assert reached.wait(1)
        if target == "adapter":
            adapter.impl = object()
        else:
            engine.core_memory = governed
        assert job.outstanding
    finally:
        release.set()
    done(job, "uncertain")
    expected = {"acquire": (2, 0), "advance": (1, 1), "prune": (1, 0)}[operation]
    assert original.conn.execute(
        "SELECT writer_epoch,generation FROM checkpoint_stream_heads"
    ).fetchone() == (expected if phase == "committed" else (1, 0))
    assert not legacy.rows(governed)


@pytest.mark.parametrize(
    "table", ["memories", "checkpoint_stream_commits", "checkpoint_stream_heads"]
)
def test_ignored_stream_insert_preserves_existing_state(governed, table):
    first = done(acquire(governed))
    head = done(advance(governed, request(first.token, first.head, 1))).head

    def state():
        return [
            governed.conn.execute(query).fetchall()
            for query in (
                "SELECT * FROM memories",
                "SELECT * FROM checkpoint_stream_commits",
                "SELECT * FROM checkpoint_stream_heads",
            )
        ]

    before = state()
    governed.conn.execute(
        f"CREATE TRIGGER refuse BEFORE INSERT ON {table} BEGIN SELECT RAISE(IGNORE); END"
    )
    if table == "checkpoint_stream_heads":
        new_key = replace(first.token.key, stream_id="d" * 32)
        job = governed.submit_acquire_checkpoint_stream(
            key=new_key,
            start_mode="create",
            retain_checkpoints=2,
            control=legacy.control(),
        )
    else:
        job = advance(governed, request(first.token, head, 2))
    done(job, "conflict")
    assert state() == before


@pytest.mark.parametrize("stage", ["request", "resume"])
def test_capture_time_preserves_raw_integer_precision(governed, stage):
    first = done(acquire(governed))
    req = request(first.token, first.head, 1)
    meta = replace(
        api().SnapshotMetadata.from_bytes(req.metadata_bytes), captured_at_unix_s=2**53
    )
    raw = json.loads(req.payload_bytes)
    raw["captured_at"] = 2**53 + 1
    data = json.dumps(raw).encode()
    attempt = replace(
        req.attempt,
        payload_digest=hashlib.sha256(data).hexdigest(),
        metadata_digest=hashlib.sha256(meta.to_bytes()).hexdigest(),
    )
    if stage == "request":
        with pytest.raises(legacy.api().CheckpointError, match="invalid"):
            api().AdvanceRequest(attempt, data, meta.to_bytes())
        return
    done(advance(governed, req))
    # A previously written catalog and payload agree on their hashes but disagree on capture time.
    governed.conn.execute("UPDATE memories SET content=?", (data.decode(),))
    governed.conn.execute(
        "UPDATE checkpoint_stream_commits SET metadata_bytes=?,metadata_digest=?,payload_digest=?",
        (meta.to_bytes(), attempt.metadata_digest, attempt.payload_digest),
    )
    governed.conn.execute(
        "UPDATE checkpoint_stream_heads SET metadata_digest=?,payload_digest=?",
        (attempt.metadata_digest, attempt.payload_digest),
    )
    governed.conn.commit()
    done(acquire(governed, "resume"), "corrupt")
    assert governed.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (1,)


def prune(db, acquired, head, retain=2, **kwargs):
    return db.submit_prune_checkpoint_stream(
        token=acquired.token,
        expected_head=head,
        retain_checkpoints=retain,
        control=legacy.control(**kwargs),
    )


@pytest.fixture
def approve_prune(monkeypatch):
    # Aetherra imports
    from Aetherra.guardian.approval import create_approval_request, resolve_approval
    from Aetherra.guardian.risk import assess_risk

    def approve(acquired, head, retain=2):
        intent = legacy.api()._stream_intent("prune", (acquired.token, head, retain))
        request = create_approval_request(intent, assess_risk(intent))
        resolution = resolve_approval(
            request.request_id, approved=True, approver="checkpoint-test"
        )
        assert resolution["state"] == "approved"
        monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", request.request_id)

    return approve


@pytest.fixture
def approved_prune(approve_prune):
    def submit(db, acquired, head, retain=2, **kwargs):
        approve_prune(acquired, head, retain)
        return prune(db, acquired, head, retain, **kwargs)

    return submit


def members(db):
    return db.conn.execute(
        "SELECT generation FROM checkpoint_stream_commits WHERE stream_id=? ORDER BY generation",
        ("b" * 32,),
    ).fetchall()


def fill(db, acquired, numbers):
    head = acquired.head
    for n in numbers:
        head = done(advance(db, request(acquired.token, head, n))).head
    return head


def test_prune_only_exact_members_and_preserve_restore_pin(governed, approved_prune):
    db = governed
    first = done(acquire(db, retain=2))
    pinned = fill(db, first, [1])
    restored = done(acquire(db, "resume", retain=2))
    head = fill(db, restored, [2, 3, 4])
    gone = db.conn.execute(
        "SELECT record_id FROM checkpoint_stream_commits WHERE generation=2"
    ).fetchone()[0]
    c2a = legacy.save(db).result(2)
    other = done(
        db.submit_acquire_checkpoint_stream(
            key=replace(first.token.key, stream_id="c" * 32),
            start_mode="create",
            retain_checkpoints=2,
            control=legacy.control(),
        )
    )
    foreign = fill(db, other, [500])
    for kind in ["temporal_history", "conversation"]:
        db.conn.execute(
            "INSERT INTO memories (id,content,importance,created_at,last_accessed,memory_type) "
            "VALUES (?,?,0,'t','t',?)",
            (kind, gone, kind),
        )
    db.conn.commit()
    before = legacy.rows(db)
    result = done(approved_prune(db, restored, head))
    assert result == api().PruneResult(head, 1, 2, 3)
    assert members(db) == [(1,), (3,), (4,)]
    assert legacy.rows(db) == [row for row in before if row[0] != gone]
    for kept in (pinned, head, foreign, c2a):
        assert legacy.load(db, kept.checkpoint_id).result(2).record_id == kept.record_id
    assert restored.checkpoint.payload == legacy.payload(pinned.checkpoint_id)
    assert done(approved_prune(db, restored, head)).deleted_count == 0
    fresh = done(acquire(db, "resume", retain=100))
    assert members(db) == [(1,), (3,), (4,)]
    assert done(approved_prune(db, fresh, head, 100)).pruned_through == 2


@pytest.mark.parametrize(
    "damage", ["metadata", "reference", "unlink", "watermark", "gap"]
)
def test_prune_preserves_all_rows_on_inconsistency(governed, damage, approved_prune):
    db = governed
    old = done(acquire(db))
    head = fill(db, old, range(1, 6))
    current = done(acquire(db, "resume", retain=2))
    if damage == "metadata":
        db.conn.execute(
            "UPDATE checkpoint_stream_commits SET metadata_bytes=? WHERE generation=2",
            (b"{}",),
        )
    elif damage == "reference":
        db.conn.execute(
            "UPDATE checkpoint_stream_commits SET record_id=? WHERE generation=2",
            ("e" * 32,),
        )
    elif damage == "unlink":
        db.conn.execute(
            "CREATE TRIGGER keep_row BEFORE DELETE ON checkpoint_stream_commits WHEN OLD.generation=2 BEGIN SELECT RAISE(IGNORE); END"
        )
    elif damage == "watermark":
        db.conn.execute(
            "CREATE TRIGGER keep_mark BEFORE UPDATE OF pruned_through ON checkpoint_stream_heads BEGIN SELECT RAISE(IGNORE); END"
        )
    else:
        db.conn.execute("DELETE FROM checkpoint_stream_commits WHERE generation=1")
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize("fault", ["size", "head", "revoke", "unsigned", "takeover"])
def test_prune_checks_epoch_head_policy_and_audit(
    governed, policy, monkeypatch, fault, approved_prune
):
    # Aetherra imports
    import Aetherra.guardian.core as guardian

    db = governed
    old = done(acquire(db, retain=2))
    head = fill(db, old, range(1, 4))
    before = legacy.rows(db)
    if fault == "takeover":
        reached, release = threading.Event(), threading.Event()

        def held():
            reached.set()
            return release.wait(2)

        with LyrixaMemorySystem(db.db_path) as other:
            job = approved_prune(db, old, head, owned=held)
            try:
                assert reached.wait(1)
                done(acquire(other, "resume", retain=2))
            finally:
                release.set()
            done(job, "writer_fenced")
    else:
        if fault == "revoke":
            caps = policy / "capabilities.json"
            value = json.loads(caps.read_text())
            value["allow"]["consciousness:core"].remove("memory:write")
            caps.write_text(json.dumps(value))
        elif fault == "unsigned":
            monkeypatch.setattr(guardian, "append_guardian_decision", lambda *args: "")
        done(
            approved_prune(
                db,
                old,
                old.head if fault == "head" else head,
                3 if fault == "size" else 2,
            ),
            {
                "size": "conflict",
                "head": "conflict",
                "revoke": "denied",
                "unsigned": "audit_failed",
            }[fault],
        )
    assert members(db) == [(1,), (2,), (3,)]
    assert legacy.rows(db) == before


def test_prune_revoked_after_deletion_before_commit(
    governed, policy, monkeypatch, approved_prune
):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    before = list(db.conn.iterdump())
    original = api()._prune

    def revoke(*args):
        receipt = original(*args)
        (policy / "capabilities.json").write_text('{"allow":{}}')
        return receipt

    monkeypatch.setattr(api(), "_prune", revoke)
    done(approved_prune(db, current, head), "denied")
    assert list(db.conn.iterdump()) == before


def test_increasing_retention_still_releases_obsolete_prior_pin(
    governed, approved_prune
):
    db = governed
    first = done(acquire(db, retain=2))
    fill(db, first, [1])
    current = done(acquire(db, "resume", retain=2))
    head = fill(db, current, [2, 3, 4])
    for n in range(5, 8):
        done(approved_prune(db, current, head))
        head = done(advance(db, request(current.token, head, n))).head
    done(approved_prune(db, current, head))
    assert members(db) == [(1,), (6,), (7,)]
    # The new epoch pins 7. Generation 1 lies outside the larger window.
    acquired = done(acquire(db, "resume", retain=3))
    assert acquired.retention_needed
    assert done(approved_prune(db, acquired, head, 3)).pruned_through == 5
    assert members(db) == [(6,), (7,)]


def test_prune_refuses_oversized_catalog_before_deleting(governed, approved_prune):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    for generation in range(4, 132):
        db.conn.execute(
            "INSERT INTO checkpoint_stream_commits SELECT owner,scope,stream_id,?,?,?,?,?,"
            "?,writer_epoch,?,predecessor_head_digest,metadata_bytes,audit_id "
            "FROM checkpoint_stream_commits WHERE generation=1",
            (
                generation,
                f"{generation:032x}",
                f"{generation + 200:032x}",
                "a" * 64,
                "b" * 64,
                f"{generation + 3000:032x}",
                generation - 1,
            ),
        )
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize("column", ["checkpoint_id", "record_id"])
def test_prune_preserves_member_aliased_by_damaged_foreign_head(
    governed, column, approved_prune
):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    other = done(
        db.submit_acquire_checkpoint_stream(
            key=replace(current.token.key, stream_id="c" * 32),
            start_mode="create",
            retain_checkpoints=2,
            control=legacy.control(),
        )
    )
    foreign = fill(db, other, [500])
    db.conn.execute(
        "DELETE FROM checkpoint_stream_commits WHERE record_id=?", (foreign.record_id,)
    )
    if column == "record_id":
        db.conn.execute(
            "UPDATE checkpoint_stream_heads SET record_id=(SELECT record_id FROM checkpoint_stream_commits WHERE generation=1) WHERE stream_id=?",
            (other.token.key.stream_id,),
        )
    else:
        db.conn.execute(
            "UPDATE checkpoint_stream_heads SET checkpoint_id=(SELECT checkpoint_id FROM checkpoint_stream_commits WHERE generation=1) WHERE stream_id=?",
            (other.token.key.stream_id,),
        )
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


def test_acquisition_installs_only_missing_head_indexes_on_v1_stream(governed):
    db = governed
    old = done(acquire(db))
    head = fill(db, old, [1, 2, 3])
    db.conn.execute("DROP INDEX IF EXISTS checkpoint_stream_heads_record_id")
    db.conn.execute("DROP INDEX IF EXISTS checkpoint_stream_heads_checkpoint_id")
    db.conn.commit()
    before = legacy.rows(db)
    acquired = done(acquire(db, "resume", retain=2))
    assert head == acquired.head
    # Inspect the durable schema on a fresh connection after the worker commits.
    with sqlite3.connect(db.db_path) as reader:
        plan = reader.execute(
            "EXPLAIN QUERY PLAN SELECT 1 FROM checkpoint_stream_heads INDEXED BY checkpoint_stream_heads_record_id "
            "WHERE record_id=? UNION ALL SELECT 1 FROM checkpoint_stream_heads "
            "INDEXED BY checkpoint_stream_heads_checkpoint_id WHERE checkpoint_id=? LIMIT 1",
            (head.record_id, head.checkpoint_id),
        ).fetchall()
    assert any(
        "SEARCH" in row[-1] and "checkpoint_stream_heads_record_id" in row[-1]
        for row in plan
    )
    assert any(
        "SEARCH" in row[-1] and "checkpoint_stream_heads_checkpoint_id" in row[-1]
        for row in plan
    )
    assert before == legacy.rows(db)


def test_prune_rejects_impossible_epoch_capacity_below_absolute_limit(
    governed, approved_prune
):
    db = governed
    current = done(acquire(db, retain=10))
    head = fill(db, current, range(1, 6))
    db.conn.execute("UPDATE checkpoint_stream_heads SET retain_checkpoints=2")
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize("claimed_pin", [0, 2, 4])
def test_prune_refuses_pin_contradicting_catalog_epochs(
    governed, claimed_pin, approved_prune
):
    db = governed
    old = done(acquire(db, retain=2))
    fill(db, old, [1])
    current = done(acquire(db, "resume", retain=2))
    head = fill(db, current, [2, 3, 4])
    db.conn.execute(
        "UPDATE checkpoint_stream_heads SET restore_pin_generation=?", (claimed_pin,)
    )
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize("index", ["missing", "wrong_column", "partial", "collation"])
def test_prune_requires_payload_equality_index_before_lookup(
    governed, monkeypatch, index, approved_prune
):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    db.conn.execute("DROP INDEX idx_memory_type")
    if index == "wrong_column":
        db.conn.execute("CREATE INDEX idx_memory_type ON memories(access_count)")
    elif index == "partial":
        db.conn.execute(
            "CREATE INDEX idx_memory_type ON memories(memory_type) WHERE importance>0"
        )
    elif index == "collation":
        db.conn.execute(
            "CREATE INDEX idx_memory_type ON memories(memory_type COLLATE NOCASE)"
        )
    db.conn.commit()
    before = list(db.conn.iterdump())
    reads = []
    worker = legacy.api().LifecycleCheckpointWorker
    original = worker._read_checkpoint

    def observe(*args, **kwargs):
        reads.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(worker, "_read_checkpoint", staticmethod(observe))
    done(approved_prune(db, current, head), "corrupt")
    assert reads == []
    assert list(db.conn.iterdump()) == before


def test_indexed_prune_refuses_duplicate_payload_handle(governed, approved_prune):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    db.conn.execute(
        "INSERT INTO memories SELECT ?,content,context,tags,importance,created_at,last_accessed,access_count,memory_type "
        "FROM memories WHERE memory_type=?",
        ("d" * 32, "consciousness_observer_checkpoint:" + f"{1:032x}"),
    )
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(approved_prune(db, current, head), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize(
    "approval_state",
    [
        "approved",
        "different_n",
        "different_epoch",
        "different_head",
        "expired",
        "revoked",
    ],
)
def test_irreversible_prune_requires_single_exact_signed_approval(
    governed, tmp_path, monkeypatch, approval_state
):
    # Aetherra imports
    from Aetherra.guardian import approval
    from Aetherra.guardian.approval import list_approval_statuses, resolve_approval
    from Aetherra.guardian.audit import list_guardian_audit_records

    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    before = list(db.conn.iterdump())
    done(prune(db, current, head), "denied")
    assert list(db.conn.iterdump()) == before
    details = list_guardian_audit_records(limit=1)[0]["details"]
    intent = details["intent"]
    assert intent["action"] == "consciousness.continuity_prune"
    assert intent["reversible"] is False
    assert intent["rollback_plan"] is None
    assert "permanently" in intent["expected_outcome"]
    expected_metadata = {
        "stream_id": current.token.key.stream_id,
        "writer_epoch": current.token.writer_epoch,
        "generation": head.generation,
        "expected_head_digest": head.digest(),
        "retain_checkpoints": 2,
        "operation": "prune",
        "schema": 1,
    }
    assert intent["metadata"] == {
        **expected_metadata,
        "expected_head_digest": "***REDACTED***",
    }
    decision = details["decision"]
    assert decision["status"] == "require_approval"
    assert decision["reason"] == "rollback_required"
    assert decision["details"]["approval_request_id"] == "***REDACTED***"
    (pending,) = list_approval_statuses()
    assert pending["state"] == "pending_user"
    assert pending["intent"]["metadata"] == expected_metadata
    reference = pending["request_id"]
    assert (
        resolve_approval(reference, approved=True, approver="checkpoint-test")["state"]
        == "approved"
    )
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", reference)
    if approval_state == "revoked":
        assert (
            resolve_approval(reference, approved=False, approver="checkpoint-test")[
                "state"
            ]
            == "denied"
        )
    elif approval_state == "expired":
        after_expiry = datetime.fromisoformat(pending["expires_at"]) + timedelta(
            seconds=1
        )

        class ExpiredClock(datetime):
            @classmethod
            def now(cls, tz=None):
                return after_expiry.astimezone(tz)

        monkeypatch.setattr(approval, "datetime", ExpiredClock)
    if approval_state == "approved":
        assert done(prune(db, current, head)).deleted_count == 1
        accepted = list_guardian_audit_records(limit=1)[0]["details"]["decision"]
        assert accepted["status"] == "allow_limited"
        assert accepted["details"]["approval_request_id"] == "***REDACTED***"
        assert list_approval_statuses()[0]["state"] == "consumed"
        assert set(accepted["constraints"]) == {
            "guardian_approval_consumed",
            "rollback_missing_user_approved",
        }
        before = list(db.conn.iterdump())
    target = (
        replace(
            current,
            token=replace(current.token, writer_epoch=current.token.writer_epoch + 1),
        )
        if approval_state == "different_epoch"
        else current
    )
    expected_head = (
        replace(head, record_id="f" * 32)
        if approval_state == "different_head"
        else head
    )
    done(
        prune(db, target, expected_head, 3 if approval_state == "different_n" else 2),
        "denied",
    )
    assert list(db.conn.iterdump()) == before
    assert (
        list_guardian_audit_records(limit=1)[0]["details"]["decision"]["status"]
        == "require_approval"
    )
    ledger = SecurityAuditLedger(tmp_path / ".aetherra/security/audit.jsonl")
    assert ledger.verify_integrity(require_signed_records=True)


def test_advance_reports_sparse_retained_pin_then_expired_gap(governed, approved_prune):
    db = governed
    first = done(acquire(db))
    fill(db, first, [1, 2, 3, 4])
    pinned = done(acquire(db, "resume", retain=2))
    done(approved_prune(db, pinned, pinned.head))
    head = pinned.head
    for generation in range(5, 12):
        receipt = done(advance(db, request(pinned.token, head, generation)))
        head = receipt.head
        if receipt.retention_needed:
            done(approved_prune(db, pinned, head))
    assert members(db) == [(4,), (10,), (11,)]
    current = done(acquire(db, "resume", retain=8))
    assert not current.retention_needed
    receipt = done(advance(db, request(current.token, head, 12)))
    assert receipt.retention_needed is True
    assert done(approved_prune(db, current, receipt.head, 8)).deleted_count == 1
    next_receipt = done(advance(db, request(current.token, receipt.head, 13)))
    assert next_receipt.retention_needed is False
    assert members(db) == [(10,), (11,), (12,), (13,)]


def test_prune_uses_indexed_duplicate_checked_lookup_for_every_member(
    governed, approved_prune, monkeypatch
):
    db = governed
    current = done(acquire(db, retain=2))
    head = fill(db, current, [1, 2, 3])
    module = legacy.api()
    original = module.LifecycleCheckpointWorker._read_checkpoint
    plans = []

    def observed(connection, checkpoint_id, *, indexed=False):
        assert indexed
        rows = connection.execute(
            "EXPLAIN QUERY PLAN " + module._READ_INDEXED_CHECKPOINT,
            (65536, 65536, "consciousness_observer_checkpoint:" + checkpoint_id),
        ).fetchall()
        plans.append([row[-1] for row in rows])
        return original(connection, checkpoint_id, indexed=indexed)

    monkeypatch.setattr(
        module.LifecycleCheckpointWorker, "_read_checkpoint", staticmethod(observed)
    )
    assert done(approved_prune(db, current, head)).deleted_count == 1
    assert (
        plans == [["SEARCH memories USING INDEX idx_memory_type (memory_type=?)"]] * 3
    )
