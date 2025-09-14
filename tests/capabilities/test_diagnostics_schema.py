# SPDX-License-Identifier: GPL-3.0-or-later
"""Diagnostics JSON schema contract test.
Ensures deterministic structure produced by tools/lyrixa_diagnostics.py --json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

DIAG_SCRIPT = Path("tools/lyrixa_diagnostics.py")


@pytest.mark.skipif(not DIAG_SCRIPT.exists(), reason="diagnostics script missing")
def test_diagnostics_json_schema_contract(tmp_path):
    # Run with --json and skip advanced for speed
    cmd = [sys.executable, str(DIAG_SCRIPT), "--json", "--skip-advanced"]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode in (0, 2, 1), (
        f"unexpected exit: {proc.returncode}\n{proc.stdout}\n{proc.stderr}"
    )
    # Parse JSON
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as e:  # pragma: no cover - critical failure surface
        raise AssertionError(f"Diagnostics did not emit JSON: {e}\nRaw:\n{proc.stdout}")

    # Top-level required keys
    required = [
        "schema",
        "schema_version",
        "critical_pass",
        "degraded",
        "results",
        "summary_lines",
    ]
    for key in required:
        assert key in data, f"missing key: {key}"

    assert data["schema"] == "lyrixa.diagnostics"
    assert isinstance(data["schema_version"], str)
    assert isinstance(data["critical_pass"], bool)
    assert isinstance(data["degraded"], bool)
    assert isinstance(data["results"], dict)
    # Results entries must have deterministic subkeys set {status, detail, duration_ms}
    for name, entry in data["results"].items():
        for sub in ["status", "detail", "duration_ms"]:
            assert sub in entry, f"result {name} missing {sub}"
        assert entry["status"] in {"PASS", "FAIL", "WARN", "SKIP"}
        assert isinstance(entry["duration_ms"], int)
    # Ensure summary_lines determinism corresponds to results ordering sorted by name
    expected_order = sorted(data["results"].keys())
    # summary_lines lines start with name; extract
    observed_order = [line.split()[0] for line in data["summary_lines"] if line]
    assert observed_order == expected_order, (
        f"summary order mismatch: {observed_order} != {expected_order}"
    )
