"""Verify opt-in Temporal on the normal full CLI with disposable strict profiles."""

from __future__ import annotations

# Standard library imports
import argparse
import hashlib
import sqlite3
import subprocess
import sys
import threading
import time
import uuid
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

# Third party imports
import alpha_consciousness_automatic_smoke as automatic
import psutil
from alpha_consciousness_smoke import SOURCES, audit_summary
from alpha_integration_smoke import ROOT, child_environment, request_json, write_json


def source_hashes():
    names = (
        *SOURCES,
        "Aetherra/consciousness/temporal_observer.py",
        "Aetherra/consciousness/quantum/temporal_consciousness_system.py",
        "Aetherra/aetherra_core/memory/temporal_history.py",
        "Aetherra/aetherra_core/memory/temporal_history_store.py",
        "Aetherra/aetherra_core/memory/temporal_history_worker.py",
        "aetherra_hub/services/state.py",
        "Aetherra/lyrixa/gui/src/SubsystemEvidence.tsx",
        "tools/checkpoint_retention.py",
        "tools/alpha_temporal_smoke.py",
        "tests/acceptance/test_temporal_runtime_launch.py",
    )
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names
    }


def identity(record):
    return {
        "record_id": record.event.record_id,
        "kind": record.event.kind,
        "digest": record.digest,
        "ordinal": record.ordinal,
        "envelope_sha256": hashlib.sha256(record.to_bytes()).hexdigest(),
    }


def engine_state(observer):
    engine = observer._engine
    return {
        "moment_ids": list(engine.temporal_moments),
        "provenance": [identity(record) for record in engine.history_provenance],
    }


def install_sample_witness(stack, artifacts):
    # Aetherra imports
    from Aetherra.consciousness.temporal_observer import TemporalObserver

    sample = TemporalObserver._sample
    witnessed = False

    def observed(observer):
        nonlocal witnessed
        if not witnessed:
            assert threading.current_thread() is observer._thread
            write_json(
                artifacts / "before-first-sample.json",
                {"thread": threading.current_thread().name, **engine_state(observer)},
            )
            witnessed = True
        return sample(observer)

    stack.enter_context(patch.object(TemporalObserver, "_sample", observed))


def record_settlement(artifacts, core, temporal, memory):
    status = temporal.get_runtime_status()
    write_json(
        artifacts / "settlement.json",
        {
            "core": core.get_runtime_status(),
            "temporal": status,
            "engine": engine_state(temporal) if not status["thread_alive"] else None,
            "memory_owned": core._checkpoint_store is memory
            and temporal._memory is memory,
            "checkpoint_pending": memory.lifecycle_checkpoint_pending(),
            "history_pending": memory.temporal_history_pending(),
        },
    )


def configure(profile, stream, history, mode):
    fresh = not profile.exists()
    automatic.configure(
        profile, stream, "create" if fresh else "resume", interval=30, retain=2
    )
    config_path = profile / "launcher.json"
    config = automatic.read(config_path)
    config["temporal_observer"] = {
        "enabled": True,
        "history_id": history,
        "start_mode": mode,
    }
    write_json(config_path, config)
    if fresh:
        path = profile / "policy" / "guardian.json"
        policy = automatic.read(path)
        policy["allow"].extend(
            {
                "requester": "consciousness:core",
                "subsystem": "consciousness",
                "action": "consciousness.temporal_history_" + operation,
                "target": "memory:core",
            }
            for operation in ("acquire", "append", "read", "inspect")
        )
        write_json(path, policy)


def inventory(profile, stream, history):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.temporal_history import (
        AppendReceipt,
        HistoryRecord,
    )

    database = profile / "lyrixa_memory.db"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        db.execute("BEGIN")
        rows = db.execute(
            "SELECT ordinal,record_id,envelope FROM temporal_history_records WHERE history_id=? ORDER BY ordinal",
            (history,),
        ).fetchall()
        records = []
        prior = None
        for ordinal, record_id, raw in rows:
            record = HistoryRecord.from_bytes(raw)
            assert (record.ordinal, record.event.record_id, record.history_id) == (
                ordinal,
                record_id,
                history,
            )
            assert record.ordinal == len(records) + 1
            assert record.prior_digest == prior
            records.append(identity(record))
            prior = record.digest
        decisions = {
            row["audit_id"]
            for row in audit_summary(profile)
            if row["action"] == "consciousness.temporal_history_append"
            and row["decision"]["status"] in {"allow", "allow_limited"}
        }
        appended, audit_ids = [], []
        for (raw,) in db.execute(
            "SELECT receipt FROM temporal_history_receipts WHERE history_id=? ORDER BY last_ordinal",
            (history,),
        ):
            receipt = AppendReceipt.from_bytes(raw)
            assert receipt.audit_id in decisions
            audit_ids.append(receipt.audit_id)
            appended.extend(identity(record) for record in receipt.records)
        assert appended == records
        key = (automatic.OWNER, automatic.SCOPE, stream)
        head = db.execute(
            "SELECT generation,pruned_through FROM checkpoint_stream_heads WHERE owner=? AND scope=? AND stream_id=?",
            key,
        ).fetchone()
        generations = [
            row[0]
            for row in db.execute(
                "SELECT generation FROM checkpoint_stream_commits WHERE owner=? AND scope=? AND stream_id=? ORDER BY generation",
                key,
            )
        ]
        assert generations == list(range(head[1] + 1, head[0] + 1))
        return {
            "records": records,
            "append_audit_ids": audit_ids,
            "generation": head[0],
            "pruned_through": head[1],
            "generations": generations,
        }


def assert_absent_history(profile):
    database = profile / "lyrixa_memory.db"
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        names = {
            name
            for (name,) in db.execute(
                "SELECT name FROM sqlite_schema WHERE type='table'"
            )
        }
    assert "checkpoint_stream_heads" in names
    assert names.isdisjoint(
        {
            "temporal_history_heads",
            "temporal_history_records",
            "temporal_history_receipts",
        }
    )


def supervised_prune(profile, artifacts, stream, before):
    # Do not rewrite the caller's native environment. On Windows even restoring
    # an identical mapping deletes inherited empty values used by Git and others.
    code = """
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from alpha_temporal_smoke import _supervised_prune
_supervised_prune(Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], int(sys.argv[5]))
"""
    profile, artifacts = profile.resolve(), artifacts.resolve()
    with (artifacts / "supervised-prune.log").open("w", encoding="utf-8") as log:
        subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                code,
                str(ROOT / "tools"),
                str(profile),
                str(artifacts),
                stream,
                str(before["generation"]),
            ],
            cwd=str(profile),
            env=child_environment(profile, 0),
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=30,
            check=True,
        )


def _supervised_prune(profile, artifacts, stream, generation):
    if not __debug__:
        raise RuntimeError("Smoke verification requires Python assertions")
    # Aetherra imports
    from Aetherra.guardian import IntentDeclaration
    from Aetherra.guardian.approval import (
        approval_status,
        intent_fingerprint,
        resolve_approval,
    )
    from Aetherra.security.audit_ledger import SecurityAuditLedger
    from tools import checkpoint_retention

    events = []

    def review(event):
        events.append(event)
        if event["status"] != "approval_requested":
            return
        assert event["stream_id"] == stream
        assert event["generation"] == generation
        assert event["retain_checkpoints"] == 2
        item = approval_status(event["request_id"])
        assert item["state"] == "pending_user"
        intent = IntentDeclaration(**item["intent"])
        assert intent_fingerprint(intent) == event["intent_fingerprint"]
        assert intent.requester == "consciousness:core"
        assert intent.action == "consciousness.continuity_prune"
        assert intent.target == "memory:core"
        assert intent.reversible is False
        assert intent.rollback_plan is None
        for field in ("stream_id", "writer_epoch", "generation", "retain_checkpoints"):
            assert intent.metadata[field] == event[field]
        assert intent.metadata["expected_head_digest"] == event["head_digest"]
        result = resolve_approval(
            event["request_id"],
            approved=True,
            approver="synthetic-temporal-test-operator",
        )
        assert result["state"] == "approved"

    rc = checkpoint_retention.main(
        [
            "--profile",
            str(profile),
            "--database",
            "lyrixa_memory.db",
            "--stream-id",
            stream,
            "--retain",
            "2",
        ],
        emit=review,
    )
    write_json(artifacts / "supervised-prune.json", events)
    assert rc == 0
    result = events[-1]
    assert result["status"] == "pruned"
    assert result["closed_in_budget"]
    assert approval_status(result["request_id"])["state"] == "consumed"
    ledger = SecurityAuditLedger(profile / ".aetherra/security/audit.jsonl")
    assert ledger.verify_integrity(require_signed_records=True)


def owned_hub_listener(launcher):
    hub = launcher._presence_owned_hub
    if hub is None or launcher.systems.get("aetherra_hub") is not hub:
        return None
    return list(hub._srv.socket.getsockname())


def verify_listener(child):
    boot = automatic.read(child.artifacts / "boot.json")
    expected = ("127.0.0.1", child.port)
    if (
        child.process.poll() is not None
        or boot["pid"] != child.process.pid
        or boot["owned_hub_listener"] != list(expected)
        or child.base != f"http://{expected[0]}:{expected[1]}"
    ):
        raise RuntimeError("Owned Hub listener address mismatch")
    proc = psutil.Process(child.process.pid)
    # psutil 5.9 used connections(); 6.0 introduced net_connections().
    sockets = getattr(proc, "net_connections", None) or proc.connections
    if not any(
        conn.status == psutil.CONN_LISTEN and tuple(conn.laddr) == expected
        for conn in sockets(kind="tcp4")
    ):
        raise RuntimeError("Launcher PID does not own the expected Hub listener")


def wait_http(child, isolated):
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        verify_listener(child)
        result = request_json(child.base, "/api/consciousness/state")
        status = result["body"]["runtime"]
        if isolated:
            if status["temporal_last_error_code"] == "missing":
                assert status["temporal_runtime_state"] == "blocked"
                return status
        elif (
            status["temporal_runtime_state"] == "running"
            and status["temporal_accepted_observations"]
        ):
            return status
        time.sleep(0.5)
    raise AssertionError(f"Temporal readiness timed out: {status}")


def hold(child, seconds):
    verify_listener(child)
    write_json(
        child.artifacts / "browser-ready.json",
        {"pid": child.process.pid, "base": child.base},
    )
    deadline = time.monotonic() + seconds
    while not (child.artifacts / "browser-release").is_file():
        verify_listener(child)
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Browser hold expired: {child.artifacts.name}")
        time.sleep(0.25)


def run(output, *, browser_hold_seconds=0):
    if not __debug__:
        raise RuntimeError("Smoke verification requires Python assertions")
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    stream, history = uuid.uuid4().hex, uuid.uuid4().hex
    report = {
        "passed": False,
        "history_id": history,
        "stream_id": stream,
        "phases": [],
        "source_sha256": source_hashes(),
    }
    write_json(output / "receipt.json", report)
    previous = None
    for name in ("temporal-create", "temporal-resume", "temporal-isolated"):
        isolated = name == "temporal-isolated"
        resume = name == "temporal-resume"
        profile = output / ("isolated" if isolated else "primary")
        artifacts = output / name
        configure(
            profile,
            stream,
            history,
            "create" if name == "temporal-create" else "resume",
        )
        started = datetime.now(UTC).isoformat()
        with automatic.launched(
            profile,
            artifacts,
            name,
            temporal_witness=True,
            port=3001 if browser_hold_seconds else 0,
        ) as child:
            status = wait_http(child, isolated)
            write_json(artifacts / "http-runtime.json", status)
            if not isolated:
                first = child.wait("before-first-sample.json")
                assert first["thread"] == "temporal-observer"
                expected = previous["records"] if resume else []
                assert first["provenance"] == expected
                observations = [
                    r["record_id"] for r in expected if r["kind"] == "observation"
                ]
                assert set(first["moment_ids"]) == set(observations)
                if resume:
                    assert observations
                    assert (
                        status["temporal_restored_record_id"]
                        == expected[-1]["record_id"]
                    )
                    report["restored_observation_ids"] = observations
                # Get a normal periodic commit in both processes, allowing shutdown
                # to advance C2b again and independently exercise bounded retention.
                child.until(
                    (
                        (lambda s: s["continuity"]["last_save_trigger"] == "periodic")
                        if resume
                        else (lambda s: s["continuity"]["state"] == "retention_blocked")
                    ),
                    140,
                )
            if browser_hold_seconds:
                hold(child, browser_hold_seconds)
        settled = automatic.read(artifacts / "settlement.json")
        assert settled["memory_owned"]
        assert not settled["checkpoint_pending"]
        assert not settled["history_pending"]
        assert not settled["core"]["thread_alive"]
        assert not settled["core"]["continuity"]["outstanding"]
        assert not settled["temporal"]["thread_alive"]
        assert not settled["temporal"]["outstanding"]
        if isolated:
            assert_absent_history(profile)
            write_json(artifacts / "inventory.json", {"history_schema_absent": True})
            assert settled["temporal"]["last_error_code"] == "missing"
            assert settled["engine"] == {
                "moment_ids": [],
                "provenance": [],
            }
            assert not (artifacts / "before-first-sample.json").exists()
        else:
            inv = inventory(profile, stream, history)
            write_json(artifacts / "inventory.json", inv)
            assert settled["temporal"]["runtime_state"] == "stopped"
            assert inv["records"][-1]["kind"] == "session_end"
            assert (
                settled["temporal"]["saved_record_id"]
                == inv["records"][-1]["record_id"]
            )
            if resume:
                assert inv["records"][: len(previous["records"])] == previous["records"]
                assert inv["pruned_through"] >= previous["pruned_through"]
                assert inv["generation"] > previous["generation"]
                report["pruned_through"] = inv["pruned_through"]
            else:
                assert settled["core"]["continuity"]["last_error_code"] == "denied"
                denied = [
                    row["audit_id"]
                    for row in audit_summary(profile)
                    if row["action"] == "consciousness.continuity_prune"
                    and row["decision"]["status"] == "require_approval"
                    and row["decision"]["reason"] == "rollback_required"
                ]
                assert denied
                report["automatic_prune_approval_required_audit_ids"] = denied
                supervised_prune(profile, artifacts, stream, inv)
                after = inventory(profile, stream, history)
                assert after["records"] == inv["records"]
                assert after["pruned_through"] > inv["pruned_through"]
                assert after["generation"] == inv["generation"]
                write_json(artifacts / "after-prune.json", after)
                inv = after
            previous = inv
        exit_info = automatic.read(artifacts / "exit.json")
        assert exit_info["closed"]
        assert not exit_info["cleanup_kill"]
        assert exit_info["exit_code"] == 0
        report["phases"].append(
            {
                "name": name,
                **exit_info,
                "start_utc": started,
                "end_utc": datetime.now(UTC).isoformat(),
                "signed_audit_verified": child.provider["signed_audit_verified"],
            }
        )
        write_json(output / "receipt.json", report)
    report["passed"] = True
    write_json(output / "receipt.json", report)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--browser-hold-seconds", type=int, default=0)
    args = parser.parse_args()
    if not 0 <= args.browser_hold_seconds <= 900:
        parser.error("browser hold must be between 0 and 900 seconds per phase")
    sys.path.insert(0, str(ROOT))
    run(args.output, browser_hold_seconds=args.browser_hold_seconds)
