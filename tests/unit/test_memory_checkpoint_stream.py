"""Atomic stream transactions against the actual governed Memory database."""

# Standard library imports
import hashlib
import json
import sqlite3
import threading
import time
from dataclasses import asdict, replace

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
    for operation in ("acquire", "advance"):
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


@pytest.mark.parametrize(
    ("phase", "generation", "error"),
    [
        ("precommit", 0, "denied"),
        ("postcommit", 1, "uncertain"),
    ],
)
@pytest.mark.parametrize(
    "ledger",
    [
        pytest.param(None, id="active"),
        pytest.param("{", id="invalid-json"),
        pytest.param("[]", id="non-object"),
        pytest.param('{"event":"created"}', id="missing-id"),
        pytest.param(
            '{"event":"created","containment_id":"cnt_bad","intent":[]}',
            id="invalid-intent",
        ),
        pytest.param("", id="read-error"),
    ],
)
def test_advance_resamples_containment_at_commit_boundaries(
    governed, tmp_path, monkeypatch, phase, generation, error, ledger
):
    # Aetherra imports
    from Aetherra.guardian import ContainmentAction, IntentDeclaration
    from Aetherra.guardian.containment import record_containment

    def change_containment():
        if ledger is not None:
            state = tmp_path / "guardian" / "containment.jsonl"
            state.parent.mkdir(exist_ok=True)
            if ledger:
                state.write_text(ledger, encoding="utf-8")
            else:
                state.mkdir()
            return
        record_containment(
            IntentDeclaration(
                requester="consciousness:core",
                subsystem="consciousness",
                action="consciousness.continuity_advance",
                target="memory:core",
                purpose="Pause checkpoint advances",
            ),
            ContainmentAction.BLOCK_ACTION,
            reason="test_containment",
        )

    connect = sqlite3.connect
    armed = False

    class ObservedConnection(sqlite3.Connection):
        def commit(self):
            super().commit()
            if armed and phase == "postcommit":
                change_containment()

    monkeypatch.setattr(
        sqlite3,
        "connect",
        lambda *a, **kw: connect(*a, **kw, factory=ObservedConnection),
    )
    acquired = acquire(governed)
    first = done(acquired)
    armed = True
    original_advance = api()._advance

    def advance_before_recheck(*args):
        receipt = original_advance(*args)
        if phase == "precommit":
            change_containment()
        return receipt

    monkeypatch.setattr(api(), "_advance", advance_before_recheck)
    assert done(advance(governed, request(first.token, first.head, 1)), error) is None
    assert len(legacy.rows(governed)) == generation
    assert governed.conn.execute(
        "SELECT generation, (SELECT COUNT(*) FROM checkpoint_stream_commits) "
        "FROM checkpoint_stream_heads"
    ).fetchone() == (generation, generation)
    assert acquired.poll(local_owned=True).value is first


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
