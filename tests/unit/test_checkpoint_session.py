"""Exact fenced recovery through signed Memory and the owner-thread session."""

# Standard library imports
import json
import threading
import time
from dataclasses import asdict, replace

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness import runtime_observer as runtime

# Local imports
from . import test_memory_checkpoint_stream as stream

memory = stream.memory
policy = stream.policy
governed = stream.governed
done = stream.done


@pytest.fixture
def database(governed, policy):
    path = policy / "guardian.json"
    rules = json.loads(path.read_text())
    rules["allow"].append(
        dict(rules["allow"][0], action="consciousness.continuity_inspect")
    )
    path.write_text(json.dumps(rules))
    return governed


def seed(db, count):
    first = done(stream.acquire(db))
    head = first.head
    commits = []
    for n in range(1, count + 1):
        req = stream.request(first.token, head, n)
        receipt = done(stream.advance(db, req))
        commits.append(receipt)
        head = receipt.head
    return first, commits


def inspect(db, token, attempt):
    return db.submit_inspect_checkpoint_stream(
        token=token, attempt=attempt, control=stream.legacy.control()
    )


def prune_fixture(db, watermark, keep=()):
    # Simulate a previously committed retention transaction.
    rows = db.conn.execute(
        "SELECT generation, record_id FROM checkpoint_stream_commits WHERE generation<=?",
        (watermark,),
    ).fetchall()
    for generation, row in rows:
        if generation not in keep:
            db.conn.execute("DELETE FROM memories WHERE id=?", (row,))
            db.conn.execute(
                "DELETE FROM checkpoint_stream_commits WHERE generation=?",
                (generation,),
            )
    db.conn.execute("UPDATE checkpoint_stream_heads SET pruned_through=?", (watermark,))
    db.conn.commit()


@pytest.mark.parametrize(
    ("generation", "outcome"),
    [
        (4, "committed_current"),
        (3, "committed_superseded"),
        (2, "committed_superseded"),
        (1, "history_expired"),
        (0, "conflict"),
        (5, "not_committed"),
    ],
)
def test_exact_fenced_inspection_selects_current_head(database, generation, outcome):
    db = database
    old, commits = seed(db, 4)
    # Generation two survives below the watermark, without its predecessor.
    prune_fixture(db, 2, keep=(2,))
    acquired = done(stream.acquire(db, "resume"))
    if generation == 0:
        attempt = stream.request(old.token, commits[1].head, 9).attempt
    elif generation == 5:
        attempt = stream.request(old.token, commits[3].head, 9).attempt
    else:
        attempt = commits[generation - 1].attempt
    before = list(db.conn.iterdump())
    result = done(inspect(db, acquired.token, attempt))
    assert result.head == commits[-1].head
    assert result.outcome == outcome
    expected_row = (
        commits[generation - 1].head.record_id
        if outcome.startswith("committed")
        else None
    )
    assert result.matched_record_id == expected_row
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize(
    "damage",
    [
        "payload_digest",
        "metadata_digest",
        "predecessor",
        "epoch",
        "handle",
        "generation",
        "old_row",
        "old_metadata",
        "old_missing",
        "catalog_gap",
    ],
)
def test_inconsistent_retained_identity_or_join_blocks_inspection(database, damage):
    db = database
    old, commits = seed(db, 3)
    acquired = done(stream.acquire(db, "resume"))
    attempt = commits[1].attempt
    if damage in {"payload_digest", "metadata_digest"}:
        attempt = replace(attempt, **{damage: "f" * 64})
    elif damage == "predecessor":
        attempt = replace(
            attempt, expected_head=replace(attempt.expected_head, record_id="a" * 32)
        )
    elif damage == "epoch":
        db.conn.execute(
            "UPDATE checkpoint_stream_commits SET writer_epoch=2 WHERE generation=2"
        )
    elif damage == "handle":
        attempt = replace(attempt, checkpoint_id="a" * 32)
    elif damage == "generation":
        attempt = replace(attempt, expected_head=commits[-1].head)
    elif damage == "old_row":
        db.conn.execute(
            "UPDATE memories SET content='{}' WHERE id=?", (commits[1].head.record_id,)
        )
    elif damage == "old_metadata":
        db.conn.execute(
            "UPDATE checkpoint_stream_commits SET metadata_bytes=x'7b7d' WHERE generation=2"
        )
    elif damage == "old_missing":
        db.conn.execute("DELETE FROM memories WHERE id=?", (commits[1].head.record_id,))
    else:
        db.conn.execute("DELETE FROM checkpoint_stream_commits WHERE generation=1")
    db.conn.commit()
    before = list(db.conn.iterdump())
    done(inspect(db, acquired.token, attempt), "corrupt")
    assert list(db.conn.iterdump()) == before


@pytest.mark.parametrize(
    "problem", ["current", "future", "foreign", "malformed", "takeover"]
)
def test_inspection_requires_confirmed_current_fence_and_older_descriptor(
    database, problem
):
    db = database
    old, commits = seed(db, 1)
    current = done(stream.acquire(db, "resume"))
    attempt = commits[0].attempt
    if problem == "takeover":
        done(stream.acquire(db, "resume"))
    elif problem == "foreign":
        attempt = replace(
            attempt,
            token=replace(old.token, key=replace(old.token.key, stream_id="f" * 32)),
        )
    elif problem == "malformed":
        attempt = asdict(attempt)
    else:
        attempt = replace(
            attempt,
            token=replace(old.token, writer_epoch=2 if problem == "current" else 3),
        )
    done(
        inspect(db, current.token, attempt),
        "writer_fenced" if problem == "takeover" else "invalid",
    )


@pytest.mark.parametrize("fault", ["deny", "audit", "read_only"])
def test_inspection_requires_its_own_signed_read_authorization(
    database, policy, monkeypatch, fault
):
    # Aetherra imports
    import Aetherra.guardian.core as guardian

    old, commits = seed(database, 1)
    current = done(stream.acquire(database, "resume"))
    if fault == "deny":
        (policy / "guardian.json").write_text('{"version":1,"default":"deny"}')
    elif fault == "audit":
        monkeypatch.setattr(guardian, "append_guardian_decision", lambda *args: " ")
    else:
        (policy / "capabilities.json").write_text(
            json.dumps(
                {
                    "allow": {
                        "consciousness:core": [
                            "memory:read",
                            "consciousness:write",
                            "fs:read",
                        ]
                    }
                }
            )
        )
    result = done(
        inspect(database, current.token, commits[0].attempt),
        {"deny": "denied", "audit": "audit_failed"}.get(fault),
    )
    if result:
        assert result.outcome == "committed_current"


AUTO = {"enabled": True, "start_mode": "resume", "stream_id": "b" * 32}


def settings(automatic, **extra):
    return runtime.continuity_settings(
        {
            "consciousness_enabled": True,
            "consciousness_continuity": {
                "enabled": True,
                "automatic": automatic,
                **extra,
            },
        }
    )


def test_automatic_opt_in_defaults_and_disabled_c2a():
    assert settings({"enabled": False}) == {
        "enabled": True,
        "restore_checkpoint_id": None,
    }
    assert settings(AUTO)["automatic"] == {
        **AUTO,
        "save_interval_seconds": 300,
        "retain_checkpoints": 10,
    }


@pytest.mark.parametrize(
    ("field", "good", "bad"),
    [
        ("save_interval_seconds", (30, 86400), (29, 86401, True, 30.0)),
        ("retain_checkpoints", (2, 100), (1, 101, False, 2.0)),
    ],
)
def test_closed_strict_automatic_bounds(field, good, bad):
    for value in good:
        assert settings(dict(AUTO, **{field: value}))["automatic"][field] == value
    for value in bad:
        with pytest.raises(ValueError, match="consciousness_config_invalid"):
            settings(dict(AUTO, **{field: value}))


@pytest.mark.parametrize(
    "invalid",
    [
        {"enabled": False},
        {"restore_checkpoint_id": "a" * 32},
        {"automatic": dict(AUTO, extra=True)},
        {"automatic": dict(AUTO, start_mode="latest")},
        {"automatic": dict(AUTO, stream_id="A" * 32)},
        {"automatic": None},
        {"automatic": {"enabled": 1}},
        {"automatic": dict(AUTO, recovery_attempt={})},
    ],
)
def test_config_rejects_mixed_or_invalid_automatic(invalid):
    with pytest.raises(ValueError, match="consciousness_config_invalid"):
        settings(**{"automatic": AUTO, **invalid})


def test_config_decodes_only_exact_opaque_same_stream_resume_descriptor(database):
    old, commits = seed(database, 1)
    attempt = commits[0].attempt
    assert (
        settings(AUTO, recovery_attempt=asdict(attempt))["recovery_attempt"] == attempt
    )
    for automatic, descriptor in [
        (dict(AUTO, start_mode="create"), asdict(attempt)),
        (dict(AUTO, stream_id="a" * 32), asdict(attempt)),
        ({"enabled": False}, asdict(attempt)),
        (AUTO, {"operation_id": "a" * 32}),
        (AUTO, dict(asdict(attempt), payload="private")),
        (AUTO, dict(asdict(attempt), expected_head={})),
        (AUTO, dict(asdict(attempt), token=dict(asdict(old.token), writer_epoch=True))),
    ]:
        with pytest.raises(ValueError, match="consciousness_config_invalid"):
            settings(automatic, recovery_attempt=descriptor)


def make_session(
    db, *, mode="resume", attempt=None, wall=lambda: 345726, owned=lambda: True
):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint_session import ObserverCheckpointSession

    return ObserverCheckpointSession(
        db,
        dict(AUTO, start_mode=mode),
        recovery_attempt=attempt,
        wall_clock=wall,
        monotonic_clock=time.monotonic,
        still_owned=owned,
    )


def finish(session, *, local=True):
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        session.poll(local_owned=local)
        status = session.get_cached_status()
        if status["state"] != "restoring" and not status["outstanding"]:
            return status
        time.sleep(0.001)
    pytest.fail("startup did not finish")


@pytest.mark.parametrize(
    ("mode", "exists", "code"),
    [("create", True, "conflict"), ("resume", False, "missing")],
)
def test_unsuccessful_start_stays_blocked(database, mode, exists, code):
    if exists:
        seed(database, 0)
    session = make_session(database, mode=mode)
    session.begin_start()
    assert finish(session)["last_error_code"] == code
    assert session.take_restore() is None
    session.begin_start()
    assert finish(session)["last_error_code"] == code


def test_lost_acquire_receipt_has_no_restore_or_new_epoch(database):
    session = make_session(database, mode="create")
    session.begin_start()
    deadline = time.monotonic() + 3
    while database.lifecycle_checkpoint_pending() and time.monotonic() < deadline:
        time.sleep(0.001)
    assert finish(session, local=False)["last_error_code"] == "uncertain"
    assert session.take_restore() is None
    session.begin_start()
    finish(session)
    assert database.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (1,)


@pytest.mark.parametrize(
    ("wall", "gap", "state"),
    [(345726, 345600, "host_wall_clock_estimate"), (120, None, "clock_inconsistent")],
)
def test_monday_friday_gap_is_not_offline_experience(database, wall, gap, state):
    _, commits = seed(database, 1)
    session = make_session(database, attempt=commits[0].attempt, wall=lambda: wall)
    session.begin_start()
    status = finish(session)
    assert status["recovery_method"] == "exact_inspection"
    assert status["recovery_outcome"] == "committed_current"
    assert status["previous_save_acceptance"] == "unknown"
    assert status["last_verified_observation_at_unix_s"] == 126
    assert status["captured_at_unix_s"] == 123
    assert status["session_started_at_unix_s"] == wall
    assert status["observation_gap_seconds"] == gap
    assert status["observation_gap_state"] == state
    assert status["offline_duration_seconds"] is None
    assert status["offline_duration_state"] == "unknown"
    restored = session.take_restore()
    assert restored.head == commits[0].head
    assert restored.metadata.session_started_at_unix_s == 140
    assert session.take_restore() is None


backends = stream.backends


@pytest.mark.parametrize("target", ["advanced", "adapter"])
def test_before_apply_retains_bound_backend_identity(database, backends, target):
    adapter, engine, _ = backends
    backend = engine if target == "advanced" else adapter
    _, commits = seed(backend, 1)
    session = make_session(backend, attempt=commits[0].attempt)
    session.begin_start()
    finish(session)
    assert session.take_restore().head == commits[0].head
    if target == "advanced":
        engine.core_memory = database
    else:
        adapter.impl = object()
    with pytest.raises(stream.legacy.api().CheckpointError):
        session.check_before_apply()


@pytest.mark.parametrize(
    "outcome", ["fresh", "conflict", "not_committed", "history_expired"]
)
def test_session_preserves_current_selection_and_unknown_old_acceptance(
    database, outcome
):
    old, commits = seed(
        database, 3 if outcome == "history_expired" else int(outcome == "conflict")
    )
    expected = commits[-1].head if commits else old.head
    if outcome == "history_expired":
        prune_fixture(database, 1)
        attempt = commits[0].attempt
    elif outcome == "fresh":
        attempt = None
    else:
        attempt = stream.request(old.token, old.head, 99).attempt
    owner = threading.get_ident()
    callbacks = []

    def owned():
        callbacks.append(threading.get_ident())
        return True

    session = make_session(database, attempt=attempt, owned=owned)
    session.begin_start()
    status = finish(session)
    for _ in range(3):
        session.poll(local_owned=True)
        assert session.get_cached_status() == status
    assert callbacks
    assert owner not in callbacks
    assert status["recovery_outcome"] == outcome
    assert status["recovery_method"] == (
        "new_stream" if attempt is None else "exact_inspection"
    )
    assert status["previous_save_acceptance"] == "unknown"
    assert status["previous_shutdown_evidence"] == "unknown"
    assert status["session_uptime_seconds"] == 0
    assert session.take_restore().head == expected
    assert session.take_restore() is None


@pytest.fixture
def writing(database):
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import decode_checkpoint
    from Aetherra.consciousness.checkpoint_session import ObserverCheckpointSession

    clock = [time.monotonic()]
    session = ObserverCheckpointSession(
        database,
        dict(AUTO, start_mode="create", save_interval_seconds=30),
        wall_clock=lambda: 500,
        monotonic_clock=lambda: clock[0],
        still_owned=lambda: True,
    )
    session.begin_start()
    assert finish(session)["state"] == "selected"
    assert session.take_restore().head.generation == 0
    state = decode_checkpoint(stream.legacy.payload())

    def tick(elapsed, wall=500):
        clock[0] = session.started_monotonic + elapsed
        session.on_completed_tick(
            replace(state, captured_at=wall + 0.25),
            observation_wall=wall,
            observation_uptime=elapsed,
            capture_uptime=elapsed,
        )

    return session, clock, tick


def test_periodic_spacing_freezes_one_new_completed_tick(
    writing, database, monkeypatch
):
    session, clock, tick = writing
    tick(29)
    session.poll(local_owned=True)
    assert stream.legacy.rows(database) == []
    tick(30, wall=490)
    entered, release = stream.legacy.blocked_audit(monkeypatch)
    session.poll(local_owned=True)
    try:
        assert entered.wait(1)
        tick(30.5, wall=480)
        for _ in range(5):
            session.poll(local_owned=True)
            assert session.get_cached_status()["outstanding"]
    finally:
        release.set()
    assert finish(session)["last_save_acceptance"] == "acknowledged"
    meta = database.conn.execute(
        "SELECT metadata_bytes FROM checkpoint_stream_commits"
    ).fetchone()[0]
    assert json.loads(meta)["last_verified_observation_at_unix_s"] == 490
    assert json.loads(meta)["captured_at_unix_s"] == 490.25
    assert json.loads(meta)["observation_uptime_s"] == 30
    clock[0] += 300
    session.poll(local_owned=True)
    assert len(stream.legacy.rows(database)) == 1
    tick(331)
    assert finish(session)["observed_generation"] == 2
    clock[0] += 30
    session.poll(local_owned=True)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    assert finish(session)["observed_generation"] == 2


@pytest.mark.parametrize("cut", ["deadline", "cancel", "owner"])
def test_sealed_periodic_receipt_closes_before_consumption(writing, database, cut):
    session, clock, tick = writing
    tick(30)
    session.poll(local_owned=True)
    end = time.monotonic() + 2
    while database.lifecycle_checkpoint_pending() and time.monotonic() < end:
        time.sleep(0.001)
    assert len(stream.legacy.rows(database)) == 1
    if cut == "cancel":
        session.cancel()
    elif cut == "deadline":
        clock[0] += 1
    session.poll(local_owned=cut != "owner")
    state = session.get_cached_status()
    assert state["last_save_acceptance"] == "unacknowledged"
    assert state["saved_record_id"] is None
    assert state["last_error_code"] == "uncertain"
    tick(100)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    assert finish(session)["observed_generation"] == 0
    assert len(stream.legacy.rows(database)) == 1


def test_busy_before_admission_skips_interval_but_fenced_write_latches(
    writing, database, monkeypatch
):
    session, clock, tick = writing
    entered, release = stream.legacy.blocked_audit(monkeypatch)
    occupied = stream.legacy.save(database)
    try:
        assert entered.wait(1)
        tick(30)
        assert finish(session)["last_save_acceptance"] == "none"
        assert session.get_cached_status()["last_error_code"] is None
    finally:
        release.set()
    occupied.result(1)
    tick(59)
    assert finish(session)["observed_generation"] == 0
    tick(60)
    accepted = finish(session)
    assert accepted["observed_generation"] == 1
    newer = done(stream.acquire(database, "resume"))
    tick(90)
    rejected = finish(session)
    assert rejected["ownership_state"] == "lost"
    assert rejected["last_error_code"] == "writer_fenced"
    assert rejected["saved_record_id"] == accepted["saved_record_id"]
    tick(150)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    assert finish(session)["ownership_state"] == "lost"
    assert database.conn.execute(
        "SELECT writer_epoch, generation FROM checkpoint_stream_heads"
    ).fetchone() == (newer.token.writer_epoch, 1)


@pytest.mark.parametrize("new_tick", [False, True])
def test_orderly_stop_drains_periodic_then_saves_only_newer_tick(
    writing, database, monkeypatch, new_tick
):
    session, clock, tick = writing
    tick(30)
    entered, release = stream.legacy.blocked_audit(monkeypatch)
    session.poll(local_owned=True)
    try:
        assert entered.wait(1)
        if new_tick:
            tick(30.5, wall=501)
        session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
        session.begin_stop(deadline=clock[0] + 20, save_checkpoint=True)
        assert session.get_cached_status()["outstanding"]
    finally:
        release.set()
    accepted = finish(session)
    assert accepted["observed_generation"] == 1 + int(new_tick)
    assert accepted["last_save_acceptance"] == "acknowledged"
    rows = database.conn.execute(
        "SELECT metadata_bytes FROM checkpoint_stream_commits ORDER BY generation"
    ).fetchall()
    assert [json.loads(row[0])["save_trigger"] for row in rows] == (
        ["periodic", "orderly_stop"] if new_tick else ["periodic"]
    )


def test_admitted_busy_latches_failure_while_preserving_exact_prior_receipt(
    writing, database, monkeypatch
):
    session, clock, tick = writing
    tick(30)
    first = finish(session)
    assert first["last_save_acceptance"] == "acknowledged"
    initial = dict(first["current_attempt"])
    first["current_attempt"]["token"]["writer_epoch"] = 999
    assert session.get_cached_status()["current_attempt"]["token"]["writer_epoch"] == 1
    calls = []

    def busy(connection, request, audit):
        calls.append(request.attempt)
        raise stream.legacy.api().CheckpointError("busy")

    monkeypatch.setattr(stream.api(), "_advance", busy)
    tick(60)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    state = finish(session)
    assert state["last_error_code"] == "busy"
    assert state["last_save_trigger"] == "orderly_stop"
    assert state["last_save_acceptance"] == "unacknowledged"
    assert state["saved_record_id"] == first["saved_record_id"]
    assert state["saved_operation_id"] == initial["operation_id"]
    assert state["saved_generation"] == 1
    assert state["saved_trigger"] == "periodic"
    assert state["current_attempt"]["operation_id"] == calls[0].operation_id
    assert state["current_attempt"]["checkpoint_id"] != state["saved_checkpoint_id"]
    tick(100)
    finish(session)
    assert len(calls) == 1


def test_malformed_advance_receipt_blocks_without_publishing_or_retry(
    writing, database, monkeypatch
):
    session, clock, tick = writing
    advance = stream.api()._advance

    def malformed(connection, request, audit):
        receipt = advance(connection, request, audit)
        return replace(receipt, head=None)

    monkeypatch.setattr(stream.api(), "_advance", malformed)
    tick(30)
    status = finish(session)
    assert status["last_error_code"] == "corrupt"
    assert status["saved_record_id"] is None
    assert len(stream.legacy.rows(database)) == 1
    tick(100)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    assert finish(session)["last_save_acceptance"] == "unacknowledged"
    assert len(stream.legacy.rows(database)) == 1


def test_real_drain_racing_expiry_poll_releases_outstanding_status(
    writing, database, monkeypatch
):
    session, clock, tick = writing
    tick(30)
    entered, release = stream.legacy.blocked_audit(monkeypatch)
    session.poll(local_owned=True)
    job_type = stream.api().StreamJob
    actual = job_type.outstanding.fget

    def sampled(job):
        was_pending = actual(job)
        if was_pending and job.acceptance_closed and not release.is_set():
            release.set()
            deadline = time.monotonic() + 2
            while actual(job) and time.monotonic() < deadline:
                time.sleep(0.001)
            assert not actual(job)
        return was_pending

    try:
        assert entered.wait(1)
        monkeypatch.setattr(job_type, "outstanding", property(sampled))
        clock[0] += 1
        session.poll(local_owned=True)
        session.poll(local_owned=True)
        status = session.get_cached_status()
        assert status["last_save_acceptance"] == "unacknowledged"
        assert not status["outstanding"]
    finally:
        release.set()


@pytest.mark.parametrize("prior_acknowledged", [False, True])
@pytest.mark.parametrize("fault", ["refused", "encoding", "submission"])
def test_before_admission_failure_preserves_all_admitted_evidence(
    writing, database, monkeypatch, prior_acknowledged, fault
):
    # Aetherra imports
    from Aetherra.consciousness import checkpoint_session

    session, clock, tick = writing
    if prior_acknowledged:
        tick(30)
        assert finish(session)["last_save_acceptance"] == "acknowledged"
    historical = session.get_cached_status()
    calls = []

    def fail(*args, **kwargs):
        calls.append(fault)
        if fault == "refused":
            return stream.api().StreamJob.refused("unavailable")
        if fault == "encoding":
            raise ValueError("invalid checkpoint")
        raise RuntimeError("adapter unavailable")

    if fault == "encoding":
        monkeypatch.setattr(checkpoint_session, "dump_checkpoint_json", fail)
    else:
        monkeypatch.setattr(database, "submit_advance_checkpoint_stream", fail)
    tick(60)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    blocked = finish(session)
    assert blocked["state"] == "blocked"
    assert blocked["last_error_code"] == (
        "invalid" if fault == "encoding" else "unavailable"
    )
    for field in (
        "last_save_acceptance",
        "last_save_trigger",
        "current_attempt",
        "saved_operation_id",
        "saved_record_id",
        "saved_checkpoint_id",
        "saved_generation",
        "saved_trigger",
        "stop_save_submitted",
        "observed_generation",
    ):
        assert blocked[field] == historical[field], field
    tick(120)
    session.begin_stop(deadline=clock[0] + 2, save_checkpoint=True)
    session.poll(local_owned=True)
    assert calls == [fault]
    assert len(stream.legacy.rows(database)) == int(prior_acknowledged)
