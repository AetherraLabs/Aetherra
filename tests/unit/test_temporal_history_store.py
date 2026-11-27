"""Contract tests for the Memory-owned Temporal codec and transaction functions."""

# Standard library imports
import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import FrozenInstanceError, replace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory import temporal_history, temporal_history_store
from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointError


@pytest.fixture
def model():
    return temporal_history


@pytest.fixture
def store():
    return temporal_history_store


@pytest.fixture
def db():
    with closing(sqlite3.connect(":memory:", isolation_level=None)) as connection:
        yield connection


def handle(n):
    return f"{n:032x}"


def key(m):
    return m.HistoryKey("consciousness:temporal", "temporal_history:v1", handle(1))


def source(m, **changes):
    return replace(m.TemporalSource(handle(9), 100, 1, 101, 1, 4, 5, 6), **changes)


def run(db, function, *args):
    db.execute("BEGIN IMMEDIATE")
    with db:
        return function(db, *args)


def make_request(m, selection, op, src, *kinds):
    events = tuple(
        m.TemporalEvent(handle(op * 10 + i), kind, src, 60 - i, reason)
        for i, (kind, reason) in enumerate(kinds)
    )
    return m.AppendRequest(selection.token, selection.head, handle(op), events)


START = ("session_start", "created")
RESUME = ("session_start", "resumed")
RESTART = ("gap", "restart")
CHANGE = ("gap", "source_changed")
UNAVAILABLE = ("gap", "source_unavailable")
OBS = ("observation", None)
END = ("session_end", "orderly_stop")


def opened(m, s, db):
    initial = run(db, s.acquire, key(m), "create")
    request = make_request(m, initial, 11, source(m), START, OBS)
    receipt = run(db, s.append, request, "signed-initial")
    return m.HistorySelection(initial.token, receipt.head), request, receipt


def test_request_canonical_bytes_freeze_and_digest(model):
    m = model
    sel = m.HistorySelection(m.HistoryToken(key(m), 1), m.HistoryHead(0, None, None))
    req = make_request(m, sel, 11, source(m), START, OBS)
    raw = req.to_bytes()
    assert (
        raw
        == json.dumps(json.loads(raw), sort_keys=True, separators=(",", ":")).encode()
    )
    assert m.AppendRequest.from_bytes(raw) == req
    assert req.digest() == hashlib.sha256(raw).hexdigest()
    copied = m.freeze(req, m.AppendRequest)
    assert copied == req
    assert copied is not req
    with pytest.raises(FrozenInstanceError):
        req.events[0].source.sequence = 2
    object.__setattr__(req.events[0].source, "sequence", False)
    with pytest.raises(CheckpointError, match="invalid"):
        m.freeze(req, m.AppendRequest)
    assert copied.events[0].source.sequence == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("session_id", "INVALID"),
        ("sequence", True),
        ("sequence", 0),
        ("observed_at_unix_s", float("nan")),
        ("observed_uptime_s", -1),
        ("session_started_at_unix_s", float("inf")),
        ("working_memory_count", False),
        ("active_intention_count", -1),
        ("focus_count", 2**63),
    ],
)
def test_source_rejects_invalid_scalars(model, field, value):
    with pytest.raises(CheckpointError, match="invalid"):
        source(model, **{field: value})


def test_event_rejects_unknown_shape_noncanonical_or_duplicate_fields(model):
    e = model.TemporalEvent(handle(1), "observation", source(model), 8)
    raw = e.to_bytes()
    for bad in [
        b" " + raw,
        raw.replace(b'"reason":null', b'"reason":null,"reason":null'),
        raw.replace(b'"reason":null', b'"extra":null'),
        raw + b"x" * 4096,
    ]:
        with pytest.raises(CheckpointError, match="invalid"):
            model.TemporalEvent.from_bytes(bad)
    for change in [
        {"kind": "thought"},
        {"reason": "restart"},
        {"captured_at_unix_s": True},
    ]:
        with pytest.raises(CheckpointError, match="invalid"):
            replace(e, **change)


def test_acquire_and_replay_preserve_original_receipt_and_epoch(model, store, db):
    m, s = model, store
    with pytest.raises(CheckpointError, match="missing"):
        run(db, s.acquire, key(m), "resume")
    assert db.execute("select count(*) from sqlite_schema").fetchone() == (0,)
    sel, req, receipt = opened(m, s, db)
    assert receipt.request_digest == req.digest()
    assert [r.ordinal for r in receipt.records] == [1, 2]
    assert receipt.records[1].prior_digest == receipt.records[0].digest
    assert receipt.head.digest == receipt.records[-1].digest
    assert run(db, s.append, req, "signed-replay") == receipt
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, s.append, replace(req, events=req.events[::-1]), "signed-changed")
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, s.acquire, key(m), "create")
    taken = run(db, s.acquire, key(m), "resume")
    assert taken.head == sel.head
    assert taken.token.writer_epoch == 2
    for func, args in [
        (s.append, (req, "signed")),
        (s.read, (sel.token, sel.head, 0, 1)),
        (s.inspect, (sel.token, req)),
    ]:
        with pytest.raises(CheckpointError, match="writer_fenced"):
            run(db, func, *args)
    result = run(db, s.inspect, taken.token, req)
    assert result.status == "committed_current"
    assert result.receipt == receipt


def test_resumed_empty_requires_resumed_marker(model, store, db):
    m, s = model, store
    run(db, s.acquire, key(m), "create")
    resumed = run(db, s.acquire, key(m), "resume")
    with pytest.raises(CheckpointError):
        run(db, s.append, make_request(m, resumed, 1, source(m), START, OBS), "audit")
    result = run(
        db, s.append, make_request(m, resumed, 1, source(m), RESUME, OBS), "audit"
    )
    assert result.head.ordinal == 2


def test_transitions_fence_source_boundaries_and_wall_clock_rollback(model, store, db):
    m, s = model, store
    sel, req, _ = opened(m, s, db)
    unchanged = source(m, sequence=5, observed_uptime_s=3)
    for src, kinds, code in [
        (unchanged, (OBS,), "unchanged"),
        (replace(unchanged, session_started_at_unix_s=2), (OBS,), "invalid"),
        (replace(unchanged, observed_uptime_s=0), (OBS,), "invalid"),
        (replace(unchanged, sequence=1), (UNAVAILABLE, OBS), "invalid"),
        (unchanged, (CHANGE, OBS), "invalid"),
        (replace(unchanged, session_id=handle(8)), (UNAVAILABLE, OBS), "invalid"),
        (replace(unchanged, session_id=handle(8)), (OBS,), "invalid"),
        (unchanged, (RESTART, OBS), "invalid"),
        (unchanged, (END,), "invalid"),
    ]:
        with pytest.raises(CheckpointError, match=code):
            run(db, s.append, make_request(m, sel, 12, src, *kinds), "audit")
    resumed = run(db, s.acquire, key(m), "resume")
    with pytest.raises(CheckpointError, match="invalid"):
        run(
            db,
            s.append,
            make_request(m, resumed, 12, source(m), RESUME, RESTART, OBS),
            "audit",
        )
    moved = replace(unchanged, observed_at_unix_s=2)
    first = run(
        db, s.append, make_request(m, resumed, 12, moved, RESUME, RESTART, OBS), "audit"
    )
    assert first.head.ordinal == 5
    sel = replace(resumed, head=first.head)
    new_source = source(m, session_id=handle(8))
    gap = run(db, s.append, make_request(m, sel, 13, new_source, CHANGE, OBS), "audit")
    sel = replace(sel, head=gap.head)
    with pytest.raises(CheckpointError, match="invalid"):
        run(db, s.append, make_request(m, sel, 14, unchanged, CHANGE, OBS), "audit")
    ended = run(db, s.append, make_request(m, sel, 14, new_source, END), "audit")
    with pytest.raises(CheckpointError, match="invalid"):
        run(
            db,
            s.append,
            make_request(m, replace(sel, head=ended.head), 15, moved, CHANGE, OBS),
            "audit",
        )
    assert run(db, s.inspect, resumed.token, req).status == "committed_superseded"


def test_selected_pages_preserve_committed_prefix(model, store, db):
    m, s = model, store
    sel, _, start = opened(m, s, db)
    later = run(
        db,
        s.append,
        make_request(m, sel, 12, source(m, sequence=2, focus_count=2), OBS),
        "audit",
    )
    page = run(db, s.read, sel.token, sel.head, 0, 1)
    assert (page.selected_head, page.records, page.next_ordinal) == (
        sel.head,
        start.records[:1],
        1,
    )
    assert run(db, s.read, sel.token, sel.head, 1, 64).records == start.records[1:]
    assert run(db, s.read, sel.token, sel.head, 2, 1).records == ()
    assert run(db, s.read, sel.token, later.head, 2, 1).records == later.records
    for head, after, limit in [
        (sel.head, 3, 1),
        (sel.head, 1, 65),
        (replace(sel.head, digest="0" * 64), 0, 1),
        (
            m.HistoryHead(1, start.records[0].event.record_id, start.records[0].digest),
            0,
            1,
        ),
    ]:
        with pytest.raises(CheckpointError):
            run(db, s.read, sel.token, head, after, limit)


def test_inspection_proves_absence_and_detects_occupied_range(model, store, db):
    m, s = model, store
    sel, _, _ = opened(m, s, db)
    req = make_request(m, sel, 12, source(m, sequence=4, focus_count=7), OBS)
    claimed = run(db, s.append, replace(req, operation_id=handle(13)), "signed")
    missing = make_request(
        m, replace(sel, head=claimed.head), 15, source(m, sequence=8), OBS
    )
    taken = run(db, s.acquire, key(m), "resume")
    assert run(db, s.inspect, taken.token, missing).status == "not_committed"
    bad = replace(missing, expected_head=replace(claimed.head, digest="0" * 64))
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, s.inspect, taken.token, bad)
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, s.inspect, taken.token, req)
    with pytest.raises(CheckpointError, match="corrupt"):
        run(
            db,
            s.inspect,
            taken.token,
            replace(missing, expected_head=replace(claimed.head, ordinal=20)),
        )


@pytest.mark.parametrize(
    "damage",
    [
        "DELETE FROM temporal_history_receipts",
        "DELETE FROM temporal_history_records WHERE ordinal=1",
        "UPDATE temporal_history_records SET envelope=x'007b' WHERE ordinal=1",
        "UPDATE temporal_history_records SET envelope=zeroblob(1000000) WHERE ordinal=2",
        "UPDATE temporal_history_records SET session_id='wrong' WHERE ordinal=1",
        "ALTER TABLE temporal_history_records ADD COLUMN unexpected TEXT",
    ],
)
def test_corrupt_storage_fails_closed(model, store, db, damage):
    sel, req, _ = opened(model, store, db)
    taken = run(db, store.acquire, key(model), "resume")
    db.execute(damage)
    for func, args in [
        (store.acquire, (key(model), "resume")),
        (store.read, (taken.token, sel.head, 0, 1)),
        (store.inspect, (taken.token, req)),
    ]:
        with pytest.raises(CheckpointError, match="corrupt"):
            run(db, func, *args)


def test_caller_rollback_discards_entire_append(model, store, db):
    m, s = model, store
    sel = run(db, s.acquire, key(m), "create")
    req = make_request(m, sel, 11, source(m), START, OBS)
    db.execute("BEGIN IMMEDIATE")
    assert s.append(db, req, "signed").head.ordinal == 2
    db.rollback()
    assert run(db, s.read, sel.token, sel.head, 0, 1).records == ()
    assert run(db, s.append, req, "signed-again").head.ordinal == 2


def test_same_epoch_cannot_prove_uncertain_append(model, store, db):
    sel, request, _ = opened(model, store, db)
    with pytest.raises(CheckpointError, match="invalid"):
        run(db, store.inspect, sel.token, request)


def test_changed_replay_is_conflict_even_with_a_future_claimed_head(model, store, db):
    sel, request, _ = opened(model, store, db)
    changed = replace(request, expected_head=replace(sel.head, ordinal=20))
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, store.append, changed, "signed")


def test_large_history_reads_only_its_window_and_head_batch(model, store, db):
    m, s = model, store
    sel, _, _ = opened(m, s, db)
    for i in range(2, 76):
        change = make_request(
            m, sel, 100 + i, source(m, sequence=i, focus_count=i), OBS
        )
        sel = replace(sel, head=run(db, s.append, change, "signed").head)
    page = run(db, s.read, sel.token, sel.head, 0, 64)
    assert [r.ordinal for r in page.records] == list(range(1, 65))
    assert page.next_ordinal == 64
    assert run(db, s.read, sel.token, sel.head, 64, 64).next_ordinal == 76
    # A historical hole is detected when its range is actually restored. Resume
    # must continue to validate only the bounded tail or it will scan the archive.
    db.execute("DELETE FROM temporal_history_records WHERE ordinal=12")
    taken = run(db, s.acquire, key(m), "resume")
    with pytest.raises(CheckpointError, match="corrupt"):
        run(db, s.read, taken.token, taken.head, 8, 8)
    assert run(db, s.read, taken.token, taken.head, 60, 64).records[-1].ordinal == 76


def test_mixed_batch_sources_and_duplicate_event_ids_are_rejected(model, store, db):
    m, s = model, store
    sel, _, original = opened(m, s, db)
    fresh = source(m, sequence=2)
    req = make_request(m, sel, 18, fresh, UNAVAILABLE, OBS)
    with pytest.raises(CheckpointError, match="invalid"):
        replace(req, events=(req.events[0], req.events[0]))
    mixed = replace(
        req, events=(replace(req.events[0], source=source(m)), req.events[1])
    )
    with pytest.raises(CheckpointError, match="invalid"):
        run(db, s.append, mixed, "signed")
    reused_id = replace(req.events[1], record_id=original.records[0].event.record_id)
    with pytest.raises(CheckpointError, match="conflict"):
        run(db, s.append, replace(req, events=(req.events[0], reused_id)), "signed")
    assert run(db, s.append, req, "signed").head.ordinal == 4


@pytest.mark.parametrize(
    "damage",
    [
        "UPDATE temporal_history_records SET envelope=zeroblob(8388608) WHERE ordinal=2",
        "UPDATE temporal_history_heads SET seal=CAST(zeroblob(8388608) AS TEXT)",
    ],
)
def test_oversized_stored_value_cannot_advance_epoch(model, store, db, damage):
    selected, _, _ = opened(model, store, db)
    db.execute(damage)
    db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 32 * 1024)
    with pytest.raises(CheckpointError, match="^corrupt$"):
        run(db, store.acquire, selected.token.key, "resume")
    assert db.getlimit(sqlite3.SQLITE_LIMIT_LENGTH) == 32 * 1024
    assert db.execute("SELECT writer_epoch FROM temporal_history_heads").fetchone() == (
        1,
    )


def test_all_operations_bound_sqlite_values_and_restore_the_callers_limit(
    model, store, db
):
    observed = []
    category = sqlite3.SQLITE_LIMIT_LENGTH
    db.setlimit(category, 4 * 1024 * 1024)

    def trace(sql):
        if sql.startswith(("SELECT ", "UPDATE ", "INSERT ", "CREATE ")):
            observed.append(db.getlimit(category))

    def guarded(function, *args):
        observed.clear()
        db.set_trace_callback(trace)
        try:
            return run(db, function, *args)
        finally:
            db.set_trace_callback(None)
            assert observed
            assert max(observed) <= 64 * 1024
            assert db.getlimit(category) == 4 * 1024 * 1024

    selected = guarded(store.acquire, key(model), "create")
    request = make_request(model, selected, 11, source(model), START, OBS)
    receipt = guarded(store.append, request, "signed")
    guarded(store.read, selected.token, receipt.head, 0, 2)
    taken = guarded(store.acquire, key(model), "resume")
    assert guarded(store.inspect, taken.token, request).receipt == receipt
    with pytest.raises(CheckpointError, match="conflict"):
        guarded(store.acquire, key(model), "create")
