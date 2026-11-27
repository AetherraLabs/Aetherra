"""Durable typed history through actual Memory in separate interpreter processes."""

# Standard library imports
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]


def _profile(path):
    path.mkdir()
    policy = path / "policy"
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
                        "action": "consciousness.temporal_history_" + operation,
                    }
                    for operation in ("acquire", "append", "read", "inspect")
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
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    return path


def _environment(profile):
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.upper().startswith(
            (
                "AETH",
                "LYRIXA",
                "PYTHON",
                "OPENAI",
                "ANTHROPIC",
                "AZURE",
                "AWS",
                "GOOGLE",
            )
        )
        and not any(
            word in key.upper()
            for word in ("TOKEN", "SECRET", "KEY", "PASSWORD", "CREDENTIAL")
        )
    }
    env.update(
        PYTHONPATH=str(ROOT),
        PYTHONUTF8="1",
        PYTHONDONTWRITEBYTECODE="1",
        AETHERRA_SKIP_DOTENV="1",
        AETHERRA_GUARDIAN_ENABLED="1",
        AETHERRA_GUARDIAN_MODE="enforcing",
        AETHERRA_GUARDIAN_REQUIRE_POLICY="1",
        AETHERRA_REQUIRE_CAPABILITIES="1",
        AETHERRA_WORKSPACE_ROOT=str(profile),
        AETHERRA_POLICY_HOME=str(profile / "policy"),
        AETHERRA_GUARDIAN_POLICY=str(profile / "policy/guardian.json"),
        AETHERRA_GUARDIAN_STATE_DIR=str(profile / "guardian"),
        AETHERRA_PROFILE="test",
        AETHERRA_NET_STRICT="1",
        AETHERRA_SIGNING_STRICT="1",
        AETHERRA_SCRIPT_VERIFY_STRICT="1",
        AETHERRA_AUDIT="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
    )
    return env


def _run(profile, mode):
    run = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()), mode],
        cwd=profile,
        env=_environment(profile),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout.splitlines()[-1])


def test_history_ids_survive_process_restart_and_profile_isolation(tmp_path):
    profile = _profile(tmp_path / "original")
    saved = _run(profile, "save")
    restored = _run(profile, "resume")
    assert saved["pid"] != restored["pid"]
    assert saved["epoch"] == 1
    assert restored["epoch"] == 2
    assert saved["records"] == restored["records"]
    assert saved["head"] == restored["selected_head"]
    assert saved["head"]["ordinal"] == 4
    assert [r["kind"] for r in restored["records"]] == [
        "session_start",
        "observation",
        "observation",
        "session_end",
    ]
    # A backward wall clock is preserved in committed order, never sorted away.
    assert restored["records"][1]["observed_at"] == 100.0
    assert restored["records"][2]["observed_at"] == 95.0
    assert restored["records"][2]["sequence"] == 6
    assert restored["records"][2]["working_memory_count"] == 3
    assert restored["new_head"]["ordinal"] == 7
    assert restored["generic_memory_count"] == saved["generic_memory_count"] == 0
    assert saved["signed_audit_valid"]
    assert restored["signed_audit_valid"]
    separate = _run(_profile(tmp_path / "separate"), "missing")
    assert separate["error"] == "missing"
    assert separate["generic_memory_count"] == 0
    assert separate["record_ids"] == []
    (tmp_path / "history-restart-trace.json").write_text(
        json.dumps(
            {"write": saved, "restart": restored, "separate": separate}, indent=2
        ),
        encoding="utf-8",
    )


def test_missing_history_is_not_created_by_resume(tmp_path):
    profile = _profile(tmp_path / "missing")
    first = _run(profile, "missing")
    second = _run(profile, "missing")
    assert first["error"] == second["error"] == "missing"
    assert first["record_ids"] == second["record_ids"] == []
    assert not first["history_schema_created"]
    assert not second["history_schema_created"]


def _wait_file(path):
    deadline = time.monotonic() + 15
    while not path.exists() and time.monotonic() < deadline:
        time.sleep(0.001)
    assert path.exists(), f"worker handshake missing: {path.name}"


def test_new_process_fences_live_writer_blocked_before_sql(tmp_path):
    profile = _profile(tmp_path / "takeover")
    saved = _run(profile, "save")
    old = subprocess.Popen(
        [sys.executable, "-B", str(Path(__file__).resolve()), "fence_old"],
        cwd=profile,
        env=_environment(profile),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    try:
        _wait_file(profile / "old-before-sql")
        assert old.poll() is None
        takeover = _run(profile, "fence_new")
        assert old.poll() is None
        assert takeover["epoch"] == 3
        assert takeover["head"] == saved["head"]
        assert takeover["inspection"] == "not_committed"
    finally:
        (profile / "release-old").write_text("release", encoding="utf-8")
        try:
            stdout, stderr = old.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            old.kill()
            stdout, stderr = old.communicate(timeout=5)
            raise AssertionError("old test process failed to settle") from None
    assert old.returncode == 0, stderr
    refused = json.loads(stdout.splitlines()[-1])
    assert refused["error"] == "writer_fenced"
    assert refused["epoch"] == 2
    verified = _run(profile, "fence_inspect")
    assert verified["epoch"] == 4
    assert verified["head"] == saved["head"]
    assert verified["inspection"] == "not_committed"
    assert verified["records"] == saved["records"]
    (tmp_path / "history-live-fence-trace.json").write_text(
        json.dumps(
            {
                "saved": saved,
                "takeover": takeover,
                "old": refused,
                "verified": verified,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _worker(mode):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import temporal_history as h
    from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointJobControl
    from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
    from Aetherra.security.audit_ledger import SecurityAuditLedger

    def control():
        return CheckpointJobControl(
            threading.Event(), time.monotonic() + 1, lambda: True
        )

    def done(job, expected=None):
        until = time.monotonic() + 3
        while job.outstanding and time.monotonic() < until:
            time.sleep(0.001)
        assert not job.outstanding
        completion = job.poll(local_owned=True)
        assert completion.error_code == expected, completion.error_code
        return completion.value

    def record(row):
        return {
            "id": row.event.record_id,
            "digest": row.digest,
            "ordinal": row.ordinal,
            "kind": row.event.kind,
            "sequence": row.event.source.sequence,
            "observed_at": row.event.source.observed_at_unix_s,
            "working_memory_count": row.event.source.working_memory_count,
        }

    def head(value):
        return {"ordinal": value.ordinal, "id": value.record_id, "digest": value.digest}

    memory = LyrixaMemorySystem("memory.db")
    key = h.HistoryKey(h.OWNER, h.SCOPE, "a" * 32)
    try:
        if mode in ("fence_old", "fence_new", "fence_inspect"):
            selected = done(
                memory.submit_acquire_temporal_history(
                    key=key, start_mode="resume", control=control()
                )
            )
            source = h.TemporalSource("c" * 32, 200.0, 1, 201.0, 1.0, 3, 1, 1)
            original = h.AppendRequest(
                h.HistoryToken(key, 2),
                selected.head,
                "8" * 32,
                (
                    h.TemporalEvent(
                        "9" * 32, "session_start", source, 201.1, "resumed"
                    ),
                    h.TemporalEvent("d" * 32, "gap", source, 201.1, "restart"),
                    h.TemporalEvent("e" * 32, "observation", source, 201.1),
                ),
            )
            if mode == "fence_old":
                # Isolate writer fencing from wall-clock scheduling of process startup.
                # Storage, policy, audit and SQL fencing remain the real implementation;
                # separate worker tests exercise actual deadline expiry.
                # Aetherra imports
                from Aetherra.aetherra_core.memory import (
                    lifecycle_checkpoint,
                    temporal_history_worker,
                )

                fixed = time.monotonic()
                old_control_time = lifecycle_checkpoint.time
                old_worker_time = temporal_history_worker.time
                lifecycle_checkpoint.time = SimpleNamespace(monotonic=lambda: fixed)
                temporal_history_worker.time = SimpleNamespace(monotonic=lambda: fixed)
                recheck = temporal_history_worker._recheck_policy
                held = False

                def hold_once(intent):
                    nonlocal held
                    recheck(intent)
                    if (
                        intent.action == "consciousness.temporal_history_append"
                        and not held
                    ):
                        held = True
                        Path("old-before-sql").write_text("blocked", encoding="utf-8")
                        _wait_file(Path("release-old"))

                temporal_history_worker._recheck_policy = hold_once
                try:
                    job = memory.submit_append_temporal_history(
                        request=original, control=control()
                    )
                    until = time.monotonic() + 15
                    while job.outstanding and time.monotonic() < until:
                        time.sleep(0.001)
                    done(job, "writer_fenced")
                    return {
                        "pid": os.getpid(),
                        "epoch": selected.token.writer_epoch,
                        "error": "writer_fenced",
                    }
                finally:
                    lifecycle_checkpoint.time = old_control_time
                    temporal_history_worker.time = old_worker_time
                    temporal_history_worker._recheck_policy = recheck
            inspection = done(
                memory.submit_inspect_temporal_append(
                    token=selected.token, request=original, control=control()
                )
            )
            page = done(
                memory.submit_read_temporal_history(
                    token=selected.token,
                    selected_head=selected.head,
                    after_ordinal=0,
                    limit=64,
                    control=control(),
                )
            )
            return {
                "pid": os.getpid(),
                "epoch": selected.token.writer_epoch,
                "head": head(selected.head),
                "inspection": inspection.status,
                "records": [record(row) for row in page.records],
            }
        if mode == "missing":
            done(
                memory.submit_acquire_temporal_history(
                    key=key, start_mode="resume", control=control()
                ),
                "missing",
            )
            names = [
                row[0]
                for row in memory.conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            ]
            return {
                "pid": os.getpid(),
                "error": "missing",
                "record_ids": [],
                "generic_memory_count": memory.conn.execute(
                    "SELECT count(*) FROM memories"
                ).fetchone()[0],
                "history_schema_created": any(
                    name.startswith("temporal_history") for name in names
                ),
            }
        selected = done(
            memory.submit_acquire_temporal_history(
                key=key,
                start_mode="create" if mode == "save" else "resume",
                control=control(),
            )
        )
        source = h.TemporalSource("b" * 32, 90.0, 1, 100.0, 10.0, 2, 1, 1)
        changed = h.TemporalSource("b" * 32, 90.0, 6, 95.0, 15.0, 3, 1, 1)
        if mode == "save":
            opening = h.AppendRequest(
                selected.token,
                selected.head,
                "1" * 32,
                (
                    h.TemporalEvent(
                        "2" * 32, "session_start", source, 100.1, "created"
                    ),
                    h.TemporalEvent("3" * 32, "observation", source, 100.1),
                ),
            )
            receipt = done(
                memory.submit_append_temporal_history(
                    request=opening, control=control()
                )
            )
            change = h.AppendRequest(
                selected.token,
                receipt.head,
                "4" * 32,
                (h.TemporalEvent("5" * 32, "observation", changed, 95.1),),
            )
            receipt = done(
                memory.submit_append_temporal_history(request=change, control=control())
            )
            end = h.AppendRequest(
                selected.token,
                receipt.head,
                "6" * 32,
                (
                    h.TemporalEvent(
                        "7" * 32, "session_end", changed, 96.0, "orderly_stop"
                    ),
                ),
            )
            receipt = done(
                memory.submit_append_temporal_history(request=end, control=control())
            )
            selected_head = receipt.head
        else:
            selected_head = selected.head
        records = []
        after = 0
        while after < selected_head.ordinal:
            page = done(
                memory.submit_read_temporal_history(
                    token=selected.token,
                    selected_head=selected_head,
                    after_ordinal=after,
                    limit=2,
                    control=control(),
                )
            )
            records.extend(record(row) for row in page.records)
            assert page.selected_head == selected_head
            assert page.next_ordinal > after
            after = page.next_ordinal
        result = {
            "pid": os.getpid(),
            "epoch": selected.token.writer_epoch,
            "records": records,
            "head" if mode == "save" else "selected_head": head(selected_head),
            "generic_memory_count": memory.conn.execute(
                "SELECT count(*) FROM memories"
            ).fetchone()[0],
        }
        if mode == "resume":
            next_source = h.TemporalSource("c" * 32, 200.0, 1, 201.0, 1.0, 3, 1, 1)
            request = h.AppendRequest(
                selected.token,
                selected_head,
                "8" * 32,
                (
                    h.TemporalEvent(
                        "9" * 32, "session_start", next_source, 201.1, "resumed"
                    ),
                    h.TemporalEvent("d" * 32, "gap", next_source, 201.1, "restart"),
                    h.TemporalEvent("e" * 32, "observation", next_source, 201.1),
                ),
            )
            receipt = done(
                memory.submit_append_temporal_history(
                    request=request, control=control()
                )
            )
            result["new_head"] = head(receipt.head)
        result["signed_audit_valid"] = SecurityAuditLedger(
            Path(".aetherra/security/audit.jsonl")
        ).verify_integrity(require_signed_records=True)
        return result
    finally:
        assert memory.close()


if __name__ == "__main__":
    print(json.dumps(_worker(sys.argv[1])))
