"""Real CLI restart checks; generation alone uses a context-derived double."""

from __future__ import annotations

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

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
