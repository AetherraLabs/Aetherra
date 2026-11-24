"""Real SQLite, signed governance, and ownership contracts for checkpoint I/O."""

# Standard library imports
import json
import sqlite3
import threading
import time
from concurrent.futures import TimeoutError

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
from Aetherra.security.audit_ledger import SecurityAuditLedger

OWNER = "consciousness:observer"
SCOPE = "observer_continuity:v1"
HANDLE = "a" * 32


def payload(handle=HANDLE):
    return {
        "schema": 1,
        "checkpoint_id": handle,
        "owner": OWNER,
        "scope": SCOPE,
        "captured_at": 123.0,
        "qualia": {
            "valence": -0.4,
            "arousal": 0.2,
            "certainty": 0.3,
            "curiosity": 0.4,
            "care": 0.5,
            "fatigue": 0.6,
        },
        "trust": {
            "half_life_s": 3600.0,
            "subsystems": [
                {
                    "name": "checkpoint_only_sentinel",
                    "score": 40.0,
                    "last_event_ts": 120.0,
                    "history": [20.0, 40.0],
                }
            ],
        },
    }


def api():
    # Aetherra imports
    from Aetherra.aetherra_core.memory import lifecycle_checkpoint

    return lifecycle_checkpoint


def control(*, deadline=None, owned=lambda: True):
    return api().CheckpointJobControl(
        cancelled=threading.Event(),
        deadline=time.monotonic() + 1 if deadline is None else deadline,
        still_owned=owned,
    )


def save(system, *, data=None, handle=HANDLE, job=None, **kwargs):
    api()
    return system.submit_store_lifecycle_checkpoint(
        owner=OWNER,
        scope=SCOPE,
        checkpoint_id=handle,
        payload=payload(handle) if data is None else data,
        control=job or control(),
        **kwargs,
    )


def load(system, handle=HANDLE, job=None):
    api()
    return system.submit_load_lifecycle_checkpoint(
        owner=OWNER,
        scope=SCOPE,
        checkpoint_id=handle,
        control=job or control(),
    )


def error(future, code):
    with pytest.raises(api().CheckpointError) as caught:
        future.result(timeout=2)
    assert caught.value.code == code
    assert str(caught.value) == code


@pytest.fixture
def policy(monkeypatch, tmp_path):
    policy = tmp_path / "policy"
    policy.mkdir()
    (policy / "guardian.json").write_text(
        json.dumps(
            {
                "version": 1,
                "default": "deny",
                "allow": [
                    {
                        "requester": "consciousness:core",
                        "subsystem": "consciousness",
                        "target": "memory:core",
                        "action": "consciousness.continuity_save",
                    },
                    {
                        "requester": "consciousness:core",
                        "subsystem": "consciousness",
                        "target": "memory:core",
                        "action": "consciousness.continuity_restore",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (policy / "capabilities.json").write_text(
        json.dumps(
            {
                "allow": {
                    "consciousness:core": [
                        "consciousness:write",
                        "memory:read",
                        "memory:write",
                        "fs:read",
                        "fs:write",
                    ],
                }
            }
        ),
        encoding="utf-8",
    )
    for key, value in {
        "AETHERRA_GUARDIAN_ENABLED": "1",
        "AETHERRA_GUARDIAN_MODE": "enforcing",
        "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
        "AETHERRA_REQUIRE_CAPABILITIES": "1",
        "AETHERRA_SIGNING_STRICT": "1",
        "AETHERRA_SCRIPT_VERIFY_STRICT": "1",
        "AETHERRA_AUDIT": "1",
        "AETHERRA_PROFILE": "test",
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_POLICY_HOME": str(policy),
        "AETHERRA_GUARDIAN_POLICY": str(policy / "guardian.json"),
        "AETHERRA_GUARDIAN_STATE_DIR": str(tmp_path / "guardian"),
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("AETHERRA_PRINCIPAL", raising=False)
    monkeypatch.delenv("AETHERRA_PROD_UNSAFE_ALLOW", raising=False)
    monkeypatch.delenv("AETHERRA_GUARDIAN_APPROVAL_ID", raising=False)
    return policy


@pytest.fixture
def memory(policy, tmp_path):
    system = LyrixaMemorySystem(str(tmp_path / "memory.db"))
    yield system
    assert system.close() is not False


def rows(system):
    return system.conn.execute(
        "SELECT id, content, context, access_count, last_accessed FROM memories"
    ).fetchall()


def forbid_open(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("unauthorized checkpoint opened SQLite")

    monkeypatch.setattr(sqlite3, "connect", forbidden)


def test_signed_roundtrip_exact_row_no_access_mutation_or_payload_alias(
    memory, tmp_path
):
    saved = save(memory).result(timeout=2)
    assert saved.checkpoint_id == HANDLE
    assert saved.record_id != HANDLE
    assert len(saved.record_id) == 32
    before = rows(memory)
    saved.payload["qualia"]["valence"] = 1
    loaded = load(memory).result(timeout=2)
    assert loaded.record_id == saved.record_id
    assert loaded.payload == payload()
    assert rows(memory) == before
    ledger = tmp_path / ".aetherra/security/audit.jsonl"
    assert SecurityAuditLedger(ledger).verify_integrity(require_signed_records=True)
    entries = [
        json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()
    ]
    actions = [entry["details"]["intent"]["action"] for entry in entries]
    assert "consciousness.continuity_save" in actions
    assert "consciousness.continuity_restore" in actions
    assert "checkpoint_only_sentinel" not in ledger.read_text(encoding="utf-8")


def test_missing_is_explicit_and_read_does_not_use_broad_recall(memory, monkeypatch):
    async def forbidden(*args, **kwargs):
        pytest.fail("checkpoint used broad recall")

    monkeypatch.setattr(memory, "recall_memories", forbidden)
    error(load(memory), "missing")
    assert rows(memory) == []


def test_duplicate_insert_preserves_original(memory):
    saved = save(memory).result(timeout=2)
    before = rows(memory)
    error(save(memory), "ambiguous")
    assert rows(memory) == before
    assert load(memory).result(timeout=2).record_id == saved.record_id


@pytest.mark.parametrize(
    "corruption",
    [
        "duplicate",
        "json",
        "owner",
        "row_id",
        "handle",
        "oversize",
        "duplicate_key",
        "context_oversize",
    ],
)
def test_exact_load_rejects_ambiguous_malformed_and_foreign_rows(memory, corruption):
    save(memory).result(timeout=2)
    if corruption == "duplicate":
        memory.conn.execute(
            "INSERT INTO memories SELECT ?, content, context, tags, importance, created_at, last_accessed, access_count, memory_type FROM memories",
            ("b" * 32,),
        )
    elif corruption in {"owner", "row_id"}:
        context = json.loads(rows(memory)[0][2])
        context["owner" if corruption == "owner" else "record_id"] = "foreign"
        memory.conn.execute("UPDATE memories SET context=?", (json.dumps(context),))
    elif corruption == "context_oversize":
        memory.conn.execute("UPDATE memories SET context=?", (" " * 65537,))
    else:
        data = payload()
        data["checkpoint_id"] = "b" * 32
        content = {
            "json": "{",
            "handle": json.dumps(data),
            "oversize": " " * 65537,
            "duplicate_key": '{"schema":1,"schema":1}',
        }[corruption]
        memory.conn.execute("UPDATE memories SET content=?", (content,))
    memory.conn.commit()
    before = rows(memory)
    error(load(memory), "ambiguous" if corruption == "duplicate" else "invalid")
    assert rows(memory) == before


@pytest.mark.parametrize(
    ("field", "value"),
    [("owner", "foreign"), ("scope", "foreign"), ("checkpoint_id", "bad")],
)
def test_invalid_identity_rejected_before_open(memory, monkeypatch, field, value):
    api()
    forbid_open(monkeypatch)
    args = {
        "owner": OWNER,
        "scope": SCOPE,
        "checkpoint_id": HANDLE,
        "payload": payload(),
        "control": control(),
    }
    args[field] = value
    error(memory.submit_store_lifecycle_checkpoint(**args), "invalid")


@pytest.mark.parametrize(
    "change", ["principal", "caps", "guardian", "audit", "non_strict", "unsafe"]
)
def test_denied_or_unaudited_never_opens_checkpoint_database(
    memory, policy, monkeypatch, change
):
    api()
    if change == "principal":
        monkeypatch.setenv("AETHERRA_PRINCIPAL", OWNER)
    elif change == "caps":
        (policy / "capabilities.json").write_text('{"allow":{}}', encoding="utf-8")
    elif change == "guardian":
        (policy / "guardian.json").write_text(
            '{"version":1,"default":"deny"}', encoding="utf-8"
        )
    elif change == "audit":
        # Aetherra imports
        import Aetherra.guardian.core as guardian

        monkeypatch.setattr(guardian, "append_guardian_decision", lambda *args: None)
    elif change == "non_strict":
        monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "0")
    else:
        monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "1")
    forbid_open(monkeypatch)
    error(save(memory), "audit_failed" if change == "audit" else "denied")
    assert rows(memory) == []


def test_in_memory_database_is_unsupported(policy):
    with LyrixaMemorySystem() as system:
        error(save(system), "unavailable")


def blocked_audit(monkeypatch):
    # Aetherra imports
    import Aetherra.guardian.core as guardian

    entered, release = threading.Event(), threading.Event()
    original = guardian.append_guardian_decision

    def block(*args):
        entered.set()
        assert release.wait(5), "test did not release audit"
        return original(*args)

    monkeypatch.setattr(guardian, "append_guardian_decision", block)
    return entered, release


def test_blocked_audit_freezes_payload_and_retains_single_slot(memory, monkeypatch):
    entered, release = blocked_audit(monkeypatch)
    data = payload()
    future = save(memory, data=data)
    try:
        assert entered.wait(2)
        assert memory.lifecycle_checkpoint_pending()
        data["trust"]["subsystems"][0]["score"] = 99
        error(save(memory, handle="b" * 32), "busy")
        assert not memory.drain_lifecycle_checkpoints(timeout=0)
        assert memory.lifecycle_checkpoint_pending()
    finally:
        release.set()
    assert future.result(timeout=2).payload["trust"]["subsystems"][0]["score"] == 40
    assert memory.drain_lifecycle_checkpoints(timeout=2)
    error(save(memory, handle="b" * 32), "unavailable")
    assert len(rows(memory)) == 1


@pytest.mark.parametrize(
    "abandon", ["event", "future", "timeout", "ownership", "deadline"]
)
def test_abandon_during_audit_cannot_accept_late_result_or_write(
    memory, monkeypatch, abandon
):
    entered, release = blocked_audit(monkeypatch)
    owned = [True]
    clock = [time.monotonic()]
    job = control(owned=lambda: owned[0])
    future = save(memory, job=job)
    try:
        assert entered.wait(2)
        if abandon == "event":
            job.cancelled.set()
        elif abandon == "future":
            future.cancel()
        elif abandon == "timeout":
            with pytest.raises(TimeoutError):
                future.result(timeout=0)
        elif abandon == "ownership":
            owned[0] = False
        else:
            monkeypatch.setattr(api().time, "monotonic", lambda: clock[0] + 2)
        assert memory.lifecycle_checkpoint_pending()
        error(save(memory, handle="b" * 32), "busy")
    finally:
        release.set()
    error(future, "cancelled")
    assert rows(memory) == []


def test_concurrent_instances_duplicate_check_and_insert_are_atomic(memory):
    other = LyrixaMemorySystem(memory.db_path)
    try:
        futures = [save(memory), save(other)]
        successes, failures = [], []
        for future in futures:
            try:
                successes.append(future.result(timeout=2))
            except api().CheckpointError as exc:
                failures.append(exc.code)
        assert len(successes) == 1
        assert failures == ["ambiguous"]
        assert len(rows(memory)) == 1
    finally:
        other.close()


def test_sqlite_write_lock_is_bounded_without_retry(memory):
    locker = sqlite3.connect(memory.db_path)
    locker.execute("BEGIN IMMEDIATE")
    try:
        error(save(memory), "unavailable")
        assert not memory.lifecycle_checkpoint_pending()
    finally:
        locker.rollback()
        locker.close()
    assert rows(memory) == []


def test_cancellation_during_commit_reports_uncertain_and_keeps_committed_row(
    memory, monkeypatch
):
    entered, release = threading.Event(), threading.Event()
    original = sqlite3.connect

    class BlockCommit(sqlite3.Connection):
        def commit(self):
            entered.set()
            assert release.wait(5)
            return super().commit()

    monkeypatch.setattr(
        sqlite3,
        "connect",
        lambda *args, **kwargs: original(*args, **kwargs, factory=BlockCommit),
    )
    job = control()
    future = save(memory, job=job)
    try:
        assert entered.wait(2)
        job.cancelled.set()
        assert not memory.close()
        assert memory.lifecycle_checkpoint_pending()
        assert memory.conn is not None
    finally:
        release.set()
    error(future, "uncertain")
    assert len(rows(memory)) == 1
    assert memory.close()


def test_advanced_requires_owned_real_memory_backend_without_fallback(memory):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
        AetherraMemoryEngineAdvanced,
    )

    api()
    engine = object.__new__(AetherraMemoryEngineAdvanced)
    engine.core_memory = memory
    receipt = save(engine).result(timeout=2)
    assert load(engine).result(timeout=2).record_id == receipt.record_id
    engine.core_memory = None
    error(load(engine), "unavailable")


def test_completed_future_cannot_be_accepted_after_caller_cancellation(memory):
    done = threading.Event()
    job = control()
    future = save(memory, job=job)
    future.add_done_callback(lambda result: done.set())
    assert done.wait(2)
    assert len(rows(memory)) == 1
    job.cancelled.set()
    error(future, "uncertain")


def test_completed_restore_cannot_be_accepted_after_ownership_loss(memory):
    save(memory).result(timeout=2)
    done = threading.Event()
    owned = [True]
    job = control(owned=lambda: owned[0])
    future = load(memory, job=job)
    future.add_done_callback(lambda result: done.set())
    assert done.wait(2)
    owned[0] = False
    error(future, "cancelled")


def test_deadline_is_capped_at_one_second_even_if_caller_requests_longer(
    memory, monkeypatch
):
    entered, release = blocked_audit(monkeypatch)
    now = time.monotonic()
    job = control(deadline=now + 100)
    future = save(memory, job=job)
    try:
        assert entered.wait(2)
        monkeypatch.setattr(api().time, "monotonic", lambda: now + 2)
    finally:
        release.set()
    error(future, "cancelled")
    assert rows(memory) == []


def test_missing_database_is_not_created(memory, monkeypatch):
    # Standard library imports
    from pathlib import Path

    path = Path(memory.db_path)
    memory.conn.close()
    memory.conn = None
    path.unlink()
    error(save(memory), "unavailable")
    assert not path.exists()


@pytest.mark.parametrize(
    "path", ["", ":memory:", "file:memory.db?mode=rwc", "file::memory:?cache=shared"]
)
def test_unsupported_database_forms_rejected_without_open(policy, monkeypatch, path):
    helper = api().LifecycleCheckpointWorker(path)
    forbid_open(monkeypatch)
    error(
        helper.submit(
            operation="save",
            owner=OWNER,
            scope=SCOPE,
            checkpoint_id=HANDLE,
            payload=payload(),
            control=control(),
        ),
        "unavailable",
    )
    assert helper.shutdown()


def test_policy_revoked_during_audit_prevents_checkpoint_open(
    memory, policy, monkeypatch
):
    entered, release = blocked_audit(monkeypatch)
    future = save(memory)
    try:
        assert entered.wait(2)
        (policy / "capabilities.json").write_text('{"allow":{}}', encoding="utf-8")
        forbid_open(monkeypatch)
    finally:
        release.set()
    error(future, "denied")
    assert rows(memory) == []


def test_commit_failure_reports_uncertainty_without_retry(memory, monkeypatch):
    original = sqlite3.connect
    commits = []

    class FailCommit(sqlite3.Connection):
        def commit(self):
            commits.append(True)
            raise sqlite3.OperationalError("private failure detail")

    monkeypatch.setattr(
        sqlite3,
        "connect",
        lambda *args, **kwargs: original(*args, **kwargs, factory=FailCommit),
    )
    error(save(memory), "uncertain")
    assert commits == [True]
    assert rows(memory) == []


def test_one_dedicated_worker_connection_closed_on_its_owner_thread(
    memory, monkeypatch
):
    original = sqlite3.connect
    opened, closed = [], []

    class TraceConnection(sqlite3.Connection):
        def close(self):
            closed.append(threading.get_ident())
            return super().close()

    def connect(*args, **kwargs):
        opened.append((threading.get_ident(), kwargs.get("uri"), str(args[0])))
        return original(*args, **kwargs, factory=TraceConnection)

    monkeypatch.setattr(sqlite3, "connect", connect)
    receipt = save(memory).result(timeout=2)
    assert load(memory).result(timeout=2).record_id == receipt.record_id
    assert memory.drain_lifecycle_checkpoints(timeout=2)
    assert len(opened) == 1
    assert opened[0][0] != threading.get_ident()
    assert opened[0][1] is True
    assert opened[0][2].endswith("?mode=rw")
    assert closed == [opened[0][0]]


def test_relative_database_path_remains_bound_to_original_memory_file(
    policy, tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    system = LyrixaMemorySystem("relative.db")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    try:
        receipt = save(system).result(timeout=2)
        assert rows(system)[0][0] == receipt.record_id
        assert not (elsewhere / "relative.db").exists()
    finally:
        assert system.close()


@pytest.mark.parametrize("operation", ["save", "restore"])
def test_policy_revoked_after_completion_cannot_accept_receipt(
    memory, policy, operation
):
    if operation == "restore":
        save(memory).result(timeout=2)
    done = threading.Event()
    future = save(memory) if operation == "save" else load(memory)
    future.add_done_callback(lambda result: done.set())
    assert done.wait(2)
    (policy / "capabilities.json").write_text('{"allow":{}}', encoding="utf-8")
    error(future, "uncertain" if operation == "save" else "denied")
    assert len(rows(memory)) == 1


def test_submission_deadline_includes_validation_time(memory, monkeypatch):
    module = api()
    now = [time.monotonic()]
    original = module._freeze
    monkeypatch.setattr(module.time, "monotonic", lambda: now[0])

    def delayed_validation(*args):
        result = original(*args)
        now[0] += 2
        return result

    monkeypatch.setattr(module, "_freeze", delayed_validation)
    error(save(memory, job=control(deadline=now[0] + 100)), "cancelled")
    assert rows(memory) == []
