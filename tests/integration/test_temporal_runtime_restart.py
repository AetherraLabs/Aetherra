"""Process-level collector tests using signed, strict, file-backed Memory."""

# Standard library imports
import asyncio
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# Third party imports
from test_temporal_history_restart import _environment, _profile


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


def test_durable_observation_reaches_real_engine_before_resume_sampling(tmp_path):
    profile = _profile(tmp_path / "original")
    first = _run(profile, "create")
    resumed = _run(profile, "resume")
    assert resumed["pid"] != first["pid"]
    assert resumed["moments"] == first["moments"]
    assert resumed["moments"] == [first["observation"]]
    assert resumed["head"] == first["head"]
    assert resumed["epoch"] == 2
    assert resumed["accepted"] == 0
    assert resumed["before_first_sample"] == first["moments"]
    advanced = _run(profile, "resume_fresh")
    assert advanced["before_first_sample"] == first["moments"]
    assert advanced["accepted"] == 1
    assert advanced["kinds"][-4:] == [
        "session_start",
        "gap",
        "observation",
        "session_end",
    ]
    assert advanced["moments"] == first["moments"] + [advanced["observation"]]
    missing = _run(_profile(tmp_path / "other"), "missing")
    assert missing["error"] == "missing"
    assert missing["moments"] == []


def test_invalid_live_utc_never_reaches_memory(tmp_path):
    profile = _profile(tmp_path / "invalid")
    assert _run(profile, "invalid")["error"] == "invalid"
    assert _run(profile, "empty")["moments"] == []


def test_unchanged_source_probes_real_writer_fence(tmp_path):
    assert _run(_profile(tmp_path / "fence"), "fence")["error"] == "writer_fenced"


def test_strict_denial_closes_collector(tmp_path):
    profile = _profile(tmp_path / "denied")
    (profile / "policy/guardian.json").write_text(
        '{"version":1,"default":"deny","allow":[]}', encoding="utf-8"
    )
    assert _run(profile, "denied")["error"] == "denied"


def _worker(mode):
    # Aetherra imports
    from Aetherra.aetherra_core.memory import temporal_history as h
    from Aetherra.aetherra_core.memory.lifecycle_checkpoint import CheckpointJobControl
    from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
    from Aetherra.consciousness.temporal_observer import TemporalObserver
    from Aetherra.security.audit_ledger import SecurityAuditLedger

    def wait(predicate):
        deadline = time.monotonic() + 15
        while not predicate():
            assert time.monotonic() < deadline, observer.get_status()
            time.sleep(0.005)

    sampled = threading.Event()
    before_first_sample = []

    class Source:
        def get_temporal_observation(self):
            if not sampled.is_set():
                before_first_sample.extend(observer._engine.temporal_moments)
                sampled.set()
            if mode == "empty":
                return None
            return {
                "session_id": "b" * 32,
                "sequence": 2 if mode == "resume_fresh" else 1,
                "session_started_at_unix_s": 100.0,
                "observed_at_unix_s": 1e20 if mode == "invalid" else 101.0,
                "observed_uptime_s": 1.0,
                "working_memory_count": 1,
                "focus_count": 2,
                "active_intention_count": 0,
            }

    memory = LyrixaMemorySystem("memory.db")
    observer = TemporalObserver(
        Source(),
        memory,
        settings={
            "enabled": True,
            "history_id": "a" * 32,
            "start_mode": (
                "create"
                if mode in ("create", "invalid", "fence", "denied")
                else "resume"
            ),
        },
        local_owned=lambda: True,
        readiness=lambda: None,
    )
    status = observer.get_status
    try:
        observer.start()
        if mode in ("create", "fence", "resume_fresh"):
            wait(lambda: status()["accepted_observations"] == 1)
        elif mode in ("resume", "empty"):
            wait(sampled.is_set)
        if mode == "fence":
            control = CheckpointJobControl(
                threading.Event(), time.monotonic() + 1, lambda: True
            )
            takeover = memory.submit_acquire_temporal_history(
                key=h.HistoryKey(h.OWNER, h.SCOPE, "a" * 32),
                start_mode="resume",
                control=control,
            )
            wait(lambda: not takeover.outstanding)
            assert takeover.poll(local_owned=True).value.token.writer_epoch == 2
        if mode in ("missing", "invalid", "denied", "fence"):
            wait(lambda: status()["runtime_state"] == "blocked")
            assert not observer.start()
        observation = status()["saved_record_id"]
        assert asyncio.run(observer.stop(save_history=True))
        final = status()
        if mode not in ("denied", "missing"):
            assert SecurityAuditLedger(
                Path(".aetherra/security/audit.jsonl")
            ).verify_integrity(require_signed_records=True)
        return {
            "pid": os.getpid(),
            "before_first_sample": before_first_sample,
            "kinds": [r.event.kind for r in observer._engine.history_provenance],
            "moments": list(observer._engine.temporal_moments),
            "epoch": final["writer_epoch"],
            "head": final["selected_head_record_id"],
            "observation": observation,
            "accepted": final["accepted_observations"],
            "error": final["last_error_code"],
        }
    finally:
        assert memory.close()


if __name__ == "__main__":
    print(json.dumps(_worker(sys.argv[1])))
