"""Exact fenced recovery through signed Memory and the owner-thread session."""

# Standard library imports
import json
from dataclasses import asdict, replace

# Third party imports
import pytest

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
