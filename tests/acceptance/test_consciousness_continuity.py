"""Real CLI restart checks; generation alone uses a context-derived double."""

from __future__ import annotations

# Standard library imports
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_selected_checkpoint_restores_before_ticks_and_stays_out_of_chat(tmp_path):
    """Catch lost/partial restore, cross-profile leakage and checkpoint chat evidence."""
    output = tmp_path / "continuity-evidence"
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools" / "alpha_consciousness_smoke.py"),
            "--continuity",
            "--observe-seconds",
            "5",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"Continuity smoke failed; inspect {output}:\n"
        f"{result.stdout[-5000:]}\n{result.stderr[-5000:]}"
    )
    summary = json.loads((output / "summary.json").read_text(encoding="utf-8"))
    assert summary["passed"] is True
    assert summary["source_unchanged"] is True
    assert summary["mode"] == "continuity"
    assert summary["process_exits"] == [0, 0, 0]
    assert summary["ports_closed"] == [True, True, True]
    assert summary["signed_audits_verified"] == [True, True, True]
    checkpoint = summary["checkpoint"]
    assert checkpoint["saved_record_id"] == checkpoint["restored_record_id"]
    assert checkpoint["checkpoint_id"] != checkpoint["saved_record_id"]
    assert checkpoint["exact_state_match"] is True
    assert checkpoint["pre_first_tick_count"] == 0
    assert checkpoint["nontrivial_trust_observations"] == 5
    assert checkpoint["nontrivial_trust_score"] == 40.0
    assert checkpoint["nontrivial_qualia_dimensions"] == 6
    assert checkpoint["negative_valence_restored"] is True
    assert summary["checkpoint_records_after_a"] == 1
    assert summary["checkpoint_records_after_b"] == 2
    assert summary["checkpoint_records_after_c"] == 0
    assert summary["foreign_restore_state"] == "blocked"
    assert summary["foreign_restore_error"] == "missing"
    assert summary["foreign_restore_ticks"] == 0
    assert summary["checkpoint_excluded_from_chat"] is True
    assert summary["fresh_chat_history"] == [True, True, True]
    assert summary["personal_recall_verified"] == [True, True]
    assert summary["honest_unknown_verified"] == [True, True, True]
    assert summary["live_provider_verified"] is False


@pytest.mark.skipif(
    sys.platform != "win32", reason="Windows asyncio Runner SIGINT path"
)
def test_windows_cli_sigint_saves_and_restores_without_observer_stop(
    tmp_path, monkeypatch
):
    """Catch a first Ctrl+C being mistaken for unrelated task cancellation."""
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    # Third party imports
    import alpha_consciousness_continuity_smoke as smoke

    profile = tmp_path / "profile"
    smoke.configure(profile, fresh=True)
    first_row = None
    pids = []
    for phase in ("a", "b"):
        artifacts = tmp_path / phase
        artifacts.mkdir()
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        base = f"http://127.0.0.1:{port}"
        before = len(smoke.audit_summary(profile)) if phase == "b" else 0
        with (artifacts / "runtime.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "tools/alpha_consciousness_smoke.py"),
                    "--continuity",
                    "--worker",
                    str(profile),
                    "--artifacts",
                    str(artifacts),
                    "--phase",
                    phase,
                ],
                cwd=profile,
                env=smoke.child_environment(profile, port),
                stdout=log,
                stderr=log,
            )
            pids.append(process.pid)
            try:
                boot = smoke.wait_file(artifacts / "boot.json", process)
                assert boot["readiness"]["status"] == "ready"
                assert boot["guardian_mode"] == "enforcing"
                assert set(boot["strict_flags"].values()) == {"1"}
                smoke.wait_file(artifacts / "settled.json", process, 125)
                deadline = time.monotonic() + 15
                while True:
                    metrics = smoke.snapshot(base)["ui"]["body"]["subsystem"]["metrics"]
                    if metrics["ticks_completed"] > 0:
                        break
                    assert time.monotonic() < deadline, "No completed observer tick"
                    time.sleep(0.05)
                assert metrics["continuity_state"] == (
                    "fresh" if phase == "a" else "restored"
                )
                assert len(smoke.checkpoint_rows(profile)) == (0 if phase == "a" else 1)
                # Only the CLI SIGINT path may save. Never issue stop-observer.
                (artifacts / "stop-runtime").touch()
                assert process.wait(timeout=30) == 0
            finally:
                (artifacts / "stop-runtime").touch()
                if process.poll() is None:
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()  # This disposable test child only.
                        process.wait(timeout=5)
        assert not (artifacts / "stop-observer").exists()
        assert not (artifacts / "observer-stopped.json").exists()
        provider = json.loads((artifacts / "provider.json").read_text(encoding="utf-8"))
        observer = provider["final_observer"]
        assert observer["continuity"]["state"] == "saved", observer
        assert observer["thread_alive"] is False
        assert observer["continuity"]["outstanding"] is False
        assert provider["launcher_stopped"] is True
        assert provider["signed_audit_verified"] is True
        assert provider["legacy_access_attempts"] == []
        rows = smoke.checkpoint_rows(profile)
        assert len(rows) == (1 if phase == "a" else 2)
        receipt = observer["continuity"]
        saved_row = next(
            row for row in rows if row["record_id"] == receipt["saved_record_id"]
        )
        assert saved_row["payload"]["checkpoint_id"] == receipt["saved_checkpoint_id"]
        actions = [row["action"] for row in smoke.audit_summary(profile)[before:]]
        assert actions.count("consciousness.continuity_save") == 1
        assert actions.count("consciousness.continuity_restore") == (
            0 if phase == "a" else 1
        )
        with socket.socket() as probe:
            probe.settimeout(2)
            assert probe.connect_ex(("127.0.0.1", port)) != 0
        runtime_log = (artifacts / "runtime.log").read_text(encoding="utf-8")
        assert "Graceful shutdown complete" in runtime_log
        assert smoke.SENTINEL not in runtime_log
        if phase == "a":
            first_row = saved_row
            payload = first_row["payload"]
            trust = next(
                item
                for item in payload["trust"]["subsystems"]
                if item["name"] == smoke.SENTINEL
            )
            assert trust["score"] == 40.0
            assert trust["history"] == [88.0, 76.0, 64.0, 52.0, 40.0]
            assert trust["last_event_ts"] > 0
            assert set(payload["qualia"]) == {
                "valence",
                "arousal",
                "certainty",
                "curiosity",
                "care",
                "fatigue",
            }
            assert -0.4 < payload["qualia"]["valence"] < 0
            assert all(
                value > 0
                for name, value in payload["qualia"].items()
                if name != "valence"
            )
            smoke.configure(profile, payload["checkpoint_id"])
        else:
            assert first_row in rows
            restored = json.loads(
                (artifacts / "private-restored.json").read_text(encoding="utf-8")
            )
            first_tick = json.loads(
                (artifacts / "private-before-first-tick.json").read_text(
                    encoding="utf-8"
                )
            )
            assert (
                restored["thread"] == first_tick["thread"] == "consciousness-observer"
            )
            assert restored["tick_count"] == first_tick["tick_count"] == 0
            assert restored["events_processed"] == first_tick["events_processed"] == 0
            assert (
                restored["aggregate"]
                == first_tick["aggregate"]
                == smoke.aggregate(first_row["payload"])
            )
            assert receipt["restored_record_id"] == first_row["record_id"]
            assert (
                receipt["selected_checkpoint_id"]
                == first_row["payload"]["checkpoint_id"]
            )
    assert len(set(pids)) == 2
