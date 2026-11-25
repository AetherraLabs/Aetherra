"""Foreground maintenance against isolated governed Memory and real Guardian decisions."""

# Standard library imports
import json
import os
import subprocess
import sys
import threading
import time
from dataclasses import asdict, replace
from datetime import datetime, timedelta
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.guardian import approval
from Aetherra.guardian.audit import list_guardian_audit_records
from Aetherra.security.audit_ledger import SecurityAuditLedger

# Local imports
from . import test_memory_checkpoint_stream as streams

memory = streams.memory
policy = streams.policy
governed = streams.governed


def arguments(profile, *more):
    return [
        "--profile",
        str(profile),
        "--database",
        "memory.db",
        "--stream-id",
        "b" * 32,
        "--retain",
        "2",
        *more,
    ]


def test_command_resumes_once_without_victim_or_approval(governed, tmp_path):
    streams.done(streams.acquire(governed, retain=2))
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
    run = subprocess.run(
        [sys.executable, "-m", "tools.checkpoint_retention", *arguments(tmp_path)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == 0, run.stderr
    assert json.loads(run.stdout.splitlines()[-1])["status"] == "no_victim"
    assert approval.list_approval_events() == []
    assert governed.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (2,)


def seed(db):
    acquired = streams.done(streams.acquire(db, retain=2))
    req = streams.request(acquired.token, acquired.head, 1)
    victim = streams.done(streams.advance(db, req)).head
    head = victim
    for n in (2, 3):
        head = streams.done(
            streams.advance(db, streams.request(acquired.token, head, n))
        ).head
    db.conn.execute(
        "INSERT INTO memories(id,content,importance,created_at,last_accessed,memory_type) "
        "VALUES ('history',?,0,'t','t','temporal_history')",
        (b"history\x00\xff" + victim.record_id.encode(),),
    )
    db.conn.commit()
    return req.attempt, victim, head


def rows(db):
    return db.conn.execute("SELECT * FROM memories ORDER BY id").fetchall()


def resolve(request_id, approved=True):
    result = approval.resolve_approval(
        request_id, approved=approved, approver="synthetic-operator"
    )
    assert result["state"] == ("approved" if approved else "denied")


def test_exact_inspection_before_approval_and_prune(
    governed, policy, tmp_path, monkeypatch
):
    # Aetherra imports
    from tools import checkpoint_retention as operator

    attempt, victim, head = seed(governed)
    guardian = policy / "guardian.json"
    rules = json.loads(guardian.read_text())
    rules["allow"].append(
        dict(rules["allow"][0], action="consciousness.continuity_inspect")
    )
    guardian.write_text(json.dumps(rules))
    descriptor = tmp_path / "attempt.json"
    descriptor.write_text(json.dumps(asdict(attempt)))
    before = rows(governed)
    events = []
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", "previous")

    def observe(event):
        events.append(event)
        if event["status"] == "approval_requested":
            assert events[0]["outcome"] == "committed_superseded"
            assert events[0]["matched_record_id"] == victim.record_id
            pending = approval.approval_status(event["request_id"])
            assert pending["state"] == "pending_user"
            assert pending["intent"]["reversible"] is False
            assert event["head_digest"] == head.digest()
            assert event["writer_epoch"] == 2
            assert event["retain_checkpoints"] == 2
            resolve(event["request_id"])

    rc = operator.main(
        arguments(tmp_path, "--prior-attempt", str(descriptor)), emit=observe
    )
    assert rc == 0
    receipt = events[-1]
    assert receipt["status"] == "pruned"
    assert (
        receipt["deleted_count"],
        receipt["pruned_through"],
        receipt["retained_count"],
    ) == (1, 1, 2)
    assert approval.approval_status(receipt["request_id"])["state"] == "consumed"
    assert streams.members(governed) == [(2,), (3,)]
    assert rows(governed) == [row for row in before if row[0] != victim.record_id]
    assert governed.conn.execute(
        "SELECT generation,restore_pin_generation,pruned_through FROM checkpoint_stream_heads"
    ).fetchone() == (3, 3, 1)
    assert os.environ["AETHERRA_GUARDIAN_APPROVAL_ID"] == "previous"
    details = list_guardian_audit_records(limit=1)[0]["details"]
    assert details["decision"]["status"] == "allow_limited"
    assert details["decision"]["details"]["approval_request_id"] == "***REDACTED***"
    assert SecurityAuditLedger(
        tmp_path / ".aetherra/security/audit.jsonl"
    ).verify_integrity(require_signed_records=True)


@pytest.mark.parametrize(
    ("decision", "reason"),
    [
        ("denied", "approval_denied"),
        ("cancel", "cancelled"),
        ("takeover", "writer_fenced"),
        ("expired", "approval_expired"),
        ("consumed", "approval_already_consumed"),
        ("mismatch", "approval_intent_mismatch"),
    ],
)
def test_unapproved_or_fenced_attempt_preserves_rows(
    governed, tmp_path, monkeypatch, decision, reason
):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.lifecycle_checkpoint import _stream_intent
    from tools import checkpoint_retention as operator

    _, _, head = seed(governed)
    before = rows(governed)
    if decision == "mismatch":

        def different_request(intent, risk):
            other = replace(
                intent, metadata={**intent.metadata, "retain_checkpoints": 3}
            )
            return approval.create_approval_request(other, risk)

        monkeypatch.setattr(operator, "create_approval_request", different_request)

    cancel = threading.Event()
    events = []

    def observe(event):
        events.append(event)
        if event["status"] != "approval_requested":
            return
        reference = event["request_id"]
        if decision == "cancel":
            cancel.set()
        elif decision == "expired":
            expires = datetime.fromisoformat(
                approval.approval_status(reference)["expires_at"]
            )

            class ExpiredClock(datetime):
                @classmethod
                def now(cls, tz=None):
                    return (expires + timedelta(seconds=1)).astimezone(tz)

            monkeypatch.setattr(approval, "datetime", ExpiredClock)
        else:
            resolve(reference, approved=decision != "denied")
            if decision == "takeover":
                streams.done(streams.acquire(governed, "resume", retain=2))
            if decision == "consumed":
                token = streams.api().StreamToken(
                    streams.api().StreamKey(
                        streams.legacy.OWNER, streams.legacy.SCOPE, "b" * 32
                    ),
                    2,
                )
                intent = _stream_intent("prune", (token, head, 2))
                assert approval.consume_approval(reference, intent).valid

    assert operator.main(arguments(tmp_path), emit=observe, cancelled=cancel) != 0
    assert events[-1]["reason"] == reason
    assert rows(governed) == before
    assert streams.members(governed) == [(1,), (2,), (3,)]
    assert governed.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (3 if decision == "takeover" else 2,)


def test_missing_database_never_creates_profile(policy, tmp_path):
    # Aetherra imports
    from tools import checkpoint_retention as operator

    assert operator.main(arguments(tmp_path)) != 0
    assert not (tmp_path / "memory.db").exists()
    assert approval.list_approval_events() == []


def test_expired_receipt_waits_for_actual_worker_close(governed, tmp_path, monkeypatch):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import lifecycle_checkpoint
    from tools import checkpoint_retention as operator

    seed(governed)
    release = threading.Event()
    original = lifecycle_checkpoint._recheck_policy

    def hold(intent):
        if intent.action == "consciousness.continuity_prune":
            assert release.wait(10)
        return original(intent)

    monkeypatch.setattr(lifecycle_checkpoint, "_recheck_policy", hold)
    monkeypatch.setenv("AETHERRA_GUARDIAN_APPROVAL_ID", "previous")
    events = []

    def observe(event):
        events.append(event)
        if event["status"] == "approval_requested":
            resolve(event["request_id"])
        elif event["status"] == "close_pending":
            assert (
                os.environ["AETHERRA_GUARDIAN_APPROVAL_ID"] == events[0]["request_id"]
            )
            release.set()

    try:
        assert operator.main(arguments(tmp_path), emit=observe) != 0
    finally:
        release.set()
    assert "close_pending" in [event["status"] for event in events]
    assert events[-1]["reason"] == "uncertain"
    assert events[-1]["closed"] is True
    assert events[-1]["closed_in_budget"] is False
    assert streams.members(governed) == [(1,), (2,), (3,)]
    assert os.environ["AETHERRA_GUARDIAN_APPROVAL_ID"] == "previous"


def test_approved_foreground_command_waits_for_external_guardian(governed, tmp_path):
    _, victim, _ = seed(governed)
    before = rows(governed)
    output = tmp_path / "operator.log"
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]))
    with output.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, "-m", "tools.checkpoint_retention", *arguments(tmp_path)],
            cwd=tmp_path,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    try:
        cutoff = time.monotonic() + 20
        while time.monotonic() < cutoff:
            lines = output.read_text().splitlines(keepends=True)
            pending = next(
                (
                    json.loads(line)
                    for line in lines
                    if line.startswith("{")
                    and line.endswith("\n")
                    and '"approval_requested"' in line
                ),
                None,
            )
            if pending:
                break
            assert process.poll() is None, lines
            time.sleep(0.05)
        assert pending
        assert (
            approval.approval_status(pending["request_id"])["state"] == "pending_user"
        )
        assert rows(governed) == before
        # Human decision time can exceed an entire transaction attempt.
        time.sleep(1.1)
        resolve(pending["request_id"])
        assert process.wait(timeout=10) == 0
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
    result = json.loads(output.read_text().splitlines()[-1])
    assert result["status"] == "pruned"
    assert result["request_id"] == pending["request_id"]
    assert rows(governed) == [row for row in before if row[0] != victim.record_id]
    assert "checkpoint_only_sentinel" not in output.read_text()


def test_denied_prior_inspection_does_not_request_prune(governed, tmp_path):
    # Aetherra imports
    from tools import checkpoint_retention as operator

    attempt, _, _ = seed(governed)
    before = rows(governed)
    descriptor = tmp_path / "attempt.json"
    descriptor.write_text(json.dumps(asdict(attempt)))
    events = []
    assert (
        operator.main(
            arguments(tmp_path, "--prior-attempt", str(descriptor)), emit=events.append
        )
        != 0
    )
    assert events[-1]["reason"] == "denied"
    assert approval.list_approval_events() == []
    assert rows(governed) == before


@pytest.mark.parametrize("field", ["operation_id", "stream_id"])
def test_duplicate_attempt_identifier_blocks_before_resume(governed, tmp_path, field):
    # Aetherra imports
    from tools import checkpoint_retention as operator

    attempt, _, _ = seed(governed)
    raw = json.dumps(asdict(attempt))
    member = json.dumps(field) + ":"
    assert raw.count(member) == 1
    descriptor = tmp_path / "ambiguous.json"
    other = json.dumps("f" * 32)
    descriptor.write_text(raw.replace(member, f"{member} {other}, {member}"))

    events = []
    rc = operator.main(
        arguments(tmp_path, "--prior-attempt", str(descriptor)), emit=events.append
    )
    assert rc != 0
    assert events == [{"status": "blocked", "reason": "invalid_inputs"}]
    assert governed.conn.execute(
        "SELECT writer_epoch FROM checkpoint_stream_heads"
    ).fetchone() == (attempt.token.writer_epoch,)
    assert approval.list_approval_events() == []
