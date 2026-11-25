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
