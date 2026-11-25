"""Automatic continuity evidence using the normal launcher and a disposable core DB."""

from __future__ import annotations

# Standard library imports
import hashlib
import json
import socket
import sqlite3
import subprocess
import sys
import time
import uuid
from contextlib import closing, contextmanager

# Third party imports
import alpha_consciousness_continuity_smoke as smoke
from alpha_consciousness_smoke import hashes
from alpha_integration_smoke import ROOT, child_environment, write_json

IDENTITY = (
    "generation",
    "checkpoint_id",
    "record_id",
    "payload_digest",
    "metadata_digest",
)
OWNER, SCOPE = "consciousness:observer", "observer_continuity:v1"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def configure(
    profile, stream, mode, *, interval=None, retain=None, recovery=None, live=False
):
    operations = ("acquire", "advance", "inspect")
    if retain == 2:
        operations += ("prune",)
    smoke.configure(
        profile, fresh=not profile.exists(), live=live, operations=operations
    )
    config = read(profile / "launcher.json")
    settings = {"enabled": True, "stream_id": stream, "start_mode": mode}
    if interval is not None:
        settings["save_interval_seconds"] = interval
    if retain is not None:
        settings["retain_checkpoints"] = retain
    continuity = config["consciousness_continuity"]
    continuity["automatic"] = settings
    if recovery is not None:
        continuity["recovery_attempt"] = recovery
    write_json(profile / "launcher.json", config)


def inventory(database, stream, *, candidate=None):
    """Check the catalog, payload, immutable metadata and head on one read snapshot."""
    key = (OWNER, SCOPE, stream)
    with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        db.execute("BEGIN")
        head = None
        rows = []
        if db.execute(
            "SELECT 1 FROM sqlite_master WHERE name='checkpoint_stream_heads'"
        ).fetchone():
            record = db.execute(
                "SELECT * FROM checkpoint_stream_heads WHERE owner=? AND scope=? AND stream_id=?",
                key,
            ).fetchone()
            head = dict(record) if record else None
            rows = [
                dict(r)
                for r in db.execute(
                    "SELECT * FROM checkpoint_stream_commits WHERE owner=? AND scope=? AND stream_id=? ORDER BY generation",
                    key,
                )
            ]
        previous = dict.fromkeys(IDENTITY)
        previous["generation"] = 0
        for row in rows:
            assert row["generation"] == previous["generation"] + 1
            assert row["predecessor_generation"] == previous["generation"]
            assert row["predecessor_head_digest"] == smoke.digest(previous)
            matches = db.execute(
                "SELECT id, content, context FROM memories WHERE memory_type=?",
                (smoke.CHECKPOINT_TYPE + row["checkpoint_id"],),
            ).fetchall()
            assert len(matches) == 1
            item = matches[0]
            assert item["id"] == row["record_id"]
            assert json.loads(item["context"]) == {
                "owner": OWNER,
                "scope": SCOPE,
                "schema": 1,
                "record_id": row["record_id"],
                "checkpoint_id": row["checkpoint_id"],
            }
            assert (
                hashlib.sha256(item["content"].encode()).hexdigest()
                == row["payload_digest"]
            )
            assert (
                hashlib.sha256(row["metadata_bytes"]).hexdigest()
                == row["metadata_digest"]
            )
            row["metadata"] = json.loads(row.pop("metadata_bytes"))
            row["payload"] = json.loads(item["content"])
            assert row["payload"]["checkpoint_id"] == row["checkpoint_id"]
            assert (
                row["payload"]["captured_at"] == row["metadata"]["captured_at_unix_s"]
            )
            previous = {k: row[k] for k in IDENTITY}
        if head:
            assert {k: head[k] for k in IDENTITY} == previous
        else:
            assert not rows
        candidate_ids = []
        if candidate:
            candidate_ids = [
                r[0]
                for r in db.execute(
                    "SELECT id FROM memories WHERE id=? OR memory_type=?",
                    (
                        candidate["record_id"],
                        smoke.CHECKPOINT_TYPE + candidate["attempt"]["checkpoint_id"],
                    ),
                )
            ]
        return {"head": head, "rows": rows, "candidate_ids": candidate_ids}


class Launch:
    def __init__(self, profile, artifacts, phase, *, live=False, **options):
        self.profile = profile
        self.artifacts = artifacts
        self.artifacts.mkdir(parents=True, exist_ok=False)
        write_json(artifacts / "harness.json", options)
        self.sample_count = 0
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            self.port = reservation.getsockname()[1]
        self.base = f"http://127.0.0.1:{self.port}"
        self.forced = False
        self.stop_method = None
        self.provider = None
        env = child_environment(profile, self.port, live=live)
        executable = sys.executable
        if sys.platform == "win32" and sys.prefix != sys.base_prefix:
            # Spawn CPython directly, retaining venv sites. A venv redirector PID
            # is not the process that owns the SQLite transaction on Windows.
            executable = sys._base_executable
            env["__PYVENV_LAUNCHER__"] = sys.executable
        with (artifacts / "runtime.log").open("w", encoding="utf-8") as log:
            self.process = subprocess.Popen(
                [
                    executable,
                    str(ROOT / "tools/alpha_consciousness_smoke.py"),
                    "--continuity",
                    "--automatic-stream",
                    "--worker",
                    str(profile),
                    "--artifacts",
                    str(artifacts),
                    "--phase",
                    phase,
                    *(["--live"] if live else []),
                ],
                cwd=profile,
                env=env,
                stdout=log,
                stderr=log,
            )

    def ready(self):
        boot = self.wait("boot.json")
        assert boot["pid"] == self.process.pid
        assert boot["interpreter"] == {
            "version": list(sys.version_info[:3]),
            "prefix": sys.prefix,
            "executable": sys.executable,
            "argv": [
                str(ROOT / "aetherra_os_launcher.py"),
                "--mode",
                "full",
                "--no-gui",
                "--config",
                str(self.profile / "launcher.json"),
            ],
        }
        assert boot["readiness"]["status"] == "ready"
        assert boot["guardian_mode"] == "enforcing"
        assert set(boot["strict_flags"].values()) == {"1"}
        assert boot["session_id"] is None
        assert boot["initial_context"] == {}
        self.selection = self.wait("selection.json")
        self.wait("settled.json", 125)
        return self

    def wait(self, name, seconds=180):
        return smoke.wait_file(self.artifacts / name, self.process, seconds)

    def sample(self):
        self.sample_count += 1
        (self.artifacts / f"request-{self.sample_count}").touch()
        return self.wait(f"sample-{self.sample_count}.json", 10)

    def until(self, predicate, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            sample = self.sample()
            if predicate(sample["status"]):
                return sample
            time.sleep(0.25)
        raise AssertionError(f"Observer condition timed out in {self.artifacts.name}")

    def kill_at_cut(self):
        cut = self.wait("cut.json", 25)
        assert cut["pid"] == self.process.pid
        assert self.process.poll() is None
        self.stop_method = "parent_kill_at_witness"
        self.process.kill()
        assert self.process.wait(timeout=10) != 0
        return cut

    def finish(self):
        try:
            if self.stop_method != "parent_kill_at_witness":
                assert self.process.poll() is None, "unexpected launcher exit"
                self.stop_method = "harness_sigint"
                (self.artifacts / "stop-runtime").touch()
                assert self.process.wait(timeout=65) == 0
                self.provider = read(self.artifacts / "provider.json")
                assert self.provider["signed_audit_verified"] is True
                assert self.provider["launcher_stopped"]
                assert self.provider["exit_code"] == 0
                assert not self.provider["legacy_access_attempts"]
                assert not self.provider["final_observer"]["thread_alive"]
                assert "Graceful shutdown complete" in (
                    self.artifacts / "runtime.log"
                ).read_text(encoding="utf-8")
        finally:
            if self.process.poll() is None:
                self.forced = True
                self.process.kill()
                self.process.wait(timeout=10)
            with socket.socket() as probe:
                probe.settimeout(2)
                closed = probe.connect_ex(("127.0.0.1", self.port)) != 0
            write_json(
                self.artifacts / "exit.json",
                {
                    "pid": self.process.pid,
                    "port": self.port,
                    "closed": closed,
                    "exit_code": self.process.returncode,
                    "cleanup_kill": self.forced,
                    "stop_method": self.stop_method,
                },
            )
            assert closed


@contextmanager
def launched(profile, artifacts, phase, **options):
    child = Launch(profile, artifacts, phase, **options)
    try:
        yield child.ready()
    finally:
        child.finish()


def restored(child, row, *, outcome="restored"):
    before = child.selection
    status = before["status"]["continuity"]
    assert (
        status["previous_save_acceptance"]
        == status["previous_shutdown_evidence"]
        == "unknown"
    )
    assert status["recovery_outcome"] == outcome
    assert status["recovery_method"] == (
        "durable_head" if outcome == "restored" else "exact_inspection"
    )
    assert status["observed_writer_epoch"] > row["writer_epoch"]
    assert status["observed_generation"] == row["generation"]
    assert status["restored_record_id"] == row["record_id"]
    assert status["selected_checkpoint_id"] == row["checkpoint_id"]
    assert status["session_id"] != row["metadata"]["session_id"]
    assert status["last_save_acceptance"] == "none"
    assert before["core_ticks"] == before["core_events"] == 0
    assert [s["operation"] for s in before["submissions"]] == (
        ["acquire"] if outcome == "restored" else ["acquire", "inspect"]
    )
    applied = child.wait("private-restored.json")
    first = child.wait("private-before-first-tick.json")
    assert applied["thread"] == first["thread"] == "consciousness-observer"
    assert applied["tick_count"] == first["tick_count"] == 0
    assert applied["events_processed"] == first["events_processed"] == 0
    assert applied["aggregate"] == first["aggregate"] == smoke.aggregate(row["payload"])
    return status


def acknowledged(status, row, trigger, profile):
    assert status["last_save_acceptance"] == "acknowledged"
    assert (
        status["saved_trigger"]
        == status["last_save_trigger"]
        == row["metadata"]["save_trigger"]
        == trigger
    )
    assert status["stream_id"] == row["stream_id"]
    assert status["session_id"] == row["metadata"]["session_id"]
    assert status["observed_writer_epoch"] == row["writer_epoch"]
    for field in ("generation", "operation_id", "checkpoint_id", "record_id"):
        assert status[f"saved_{field}"] == row[field]
    assert any(
        d["action"] == "consciousness.continuity_advance"
        and d["decision"]["status"] in {"allow", "allow_limited"}
        and d["audit_id"] == row["audit_id"]
        for d in smoke.audit_summary(profile)
    )
    return {
        k: status[k]
        for k in (
            "stream_id",
            "session_id",
            "observed_writer_epoch",
            "saved_generation",
            "saved_operation_id",
            "saved_checkpoint_id",
            "saved_record_id",
            "last_save_trigger",
            "last_save_acceptance",
        )
    }


def run(output, observe_seconds, *, live=False):
    output.mkdir(parents=True, exist_ok=False)
    summary = {
        "mode": "automatic_stream",
        "passed": False,
        "live_provider_verified": False,
        "source_hashes_before": hashes(),
    }
    stream = uuid.uuid4().hex
    primary, foreign = output / "primary", output / "foreign"
    database = primary / "lyrixa_memory.db"
    records, stops = [], []
    try:
        for phase, profile in (("a", primary), ("b", primary), ("c", foreign)):
            if phase == "b":
                before_resume = inventory(database, stream)
                assert (
                    before_resume["head"]["record_id"] == stops[-1]["saved_record_id"]
                )
            configure(
                profile, stream, "create" if phase == "a" else "resume", live=live
            )
            artifacts = output / f"run-{phase}"
            with launched(
                profile, artifacts, phase, live=live, history_fixture=phase == "b"
            ) as child:
                selected = child.selection["status"]["continuity"]
                if phase == "a":
                    assert selected["recovery_outcome"] == "fresh"
                    assert selected["observed_generation"] == 0
                elif phase == "b":
                    selected = restored(child, before_resume["rows"][-1])
                    summary["restored_record_id"] = selected["restored_record_id"]
                    history_id = child.wait("history-fixture.json")["record_id"]
                else:
                    assert selected["last_error_code"] == "missing"
                    assert child.selection["status"]["ticks_completed"] == 0
                    assert selected["state"] == "blocked"
                    summary["foreign_error"] = selected["last_error_code"]
                if phase != "c":
                    start = child.until(lambda s: s["ticks_completed"] > 0, 15)
                if phase == "a":
                    time.sleep(observe_seconds)
                    latest = child.sample()["status"]
                    assert (
                        latest["ticks_completed"] > start["status"]["ticks_completed"]
                    )
                messages = (
                    [smoke.FACT, *smoke.COMPETITORS] if phase == "a" else []
                ) + [smoke.QUESTION, smoke.UNKNOWN]
                turns = [smoke.chat(child.base, msg, live=live) for msg in messages]
                records.append(
                    {"pid": child.process.pid, "turns": turns, "messages": messages}
                )
                write_json(artifacts / "private-turns.json", turns)
            final = child.provider["final_observer"]
            if phase == "c":
                assert final["ticks_completed"] == 0
                assert final["continuity"]["saved_record_id"] is None
                assert [x["operation"] for x in child.provider["submissions"]] == [
                    "acquire"
                ]
                assert not inventory(foreign / "lyrixa_memory.db", stream)["head"]
                continue
            rows = inventory(database, stream)["rows"]
            stops.append(
                acknowledged(final["continuity"], rows[-1], "orderly_stop", profile)
            )
            if phase == "a":
                periodic = [
                    r for r in rows if r["metadata"]["save_trigger"] == "periodic"
                ]
                receipts = [
                    acknowledged(
                        read(artifacts / f"periodic-{r['operation_id']}.json"),
                        r,
                        "periodic",
                        profile,
                    )
                    for r in periodic
                ]
                requests = {s["operation_id"]: s for s in child.provider["submissions"]}
                for receipt, row in zip(receipts, periodic, strict=True):
                    submission = requests[row["operation_id"]]
                    due, submitted = (
                        submission["periodic_due_monotonic"],
                        submission["monotonic"],
                    )
                    accepted, deadline = (
                        submission["acknowledged_monotonic"],
                        submission["deadline"],
                    )
                    assert due <= submitted <= accepted < deadline
                    receipt.update(
                        observation_uptime_s=row["metadata"]["observation_uptime_s"],
                        eligible_monotonic=due,
                        submission_monotonic=submitted,
                        acknowledged_monotonic=accepted,
                        attempt_deadline_monotonic=deadline,
                    )
                if observe_seconds >= 660:
                    assert len(receipts) >= 2
                summary["periodic_acknowledgments"] = receipts
        assert len({r["pid"] for r in records}) == 3
        forbidden = {
            smoke.SENTINEL,
            smoke.CHECKPOINT_TYPE,
            stream,
            SCOPE,
            "last_verified_observation_at_unix_s",
            "capture_uptime_s",
            "observation_uptime_s",
            "predecessor_head_digest",
            "pruned_through",
            "saved_checkpoint_id",
            "temporal_only_sentinel40",
        }
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True)) as db:
            stored = db.execute(
                "SELECT memory_type,content FROM memories WHERE id=?", (history_id,)
            ).fetchone()
            assert stored[0] == "synthetic_temporal_history"
            assert json.loads(stored[1]) == {"content": "temporal_only_sentinel40"}
        forbidden.add(history_id)
        for row in rows:
            forbidden.update(
                row[k]
                for k in (
                    "record_id",
                    "operation_id",
                    "checkpoint_id",
                    "payload_digest",
                    "metadata_digest",
                    "audit_id",
                    "predecessor_head_digest",
                )
            )
            forbidden.update(set(row["metadata"]) - {"schema"})
            forbidden.update(
                str(row["metadata"][k])
                for k in (
                    "session_id",
                    "captured_at_unix_s",
                    "last_verified_observation_at_unix_s",
                )
            )
        fact_id = records[0]["turns"][0]["body"]["result"]["memory_id"]
        traces = []
        for phase, record in zip("abc", records, strict=True):
            trace = smoke.check_chat(
                record,
                output / f"run-{phase}",
                None if phase == "c" else fact_id,
                forbidden,
                live=live,
            )
            traces.append(
                {k: trace[k] for k in ("record_ids", "provider_evidence_ids", "llm")}
            )
        summary.update(
            passed=True,
            stops=stops,
            recall=traces,
            live_provider_verified=live,
            process_ids=[r["pid"] for r in records],
            observation_seconds=observe_seconds,
            interval_seconds=300,
            retention_limit=10,
            checkpoint_excluded_from_chat=True,
            stop_method="harness_sigint",
            signed_audits_verified=True,
        )
    except Exception as exc:
        summary["error"] = type(exc).__name__
        raise
    finally:
        summary["source_hashes_after"] = hashes()
        summary["source_unchanged"] = (
            summary["source_hashes_before"] == summary["source_hashes_after"]
        )
        summary["passed"] &= summary["source_unchanged"]
        write_json(output / "summary.json", summary)
        print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1
