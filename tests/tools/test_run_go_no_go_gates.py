# SPDX-License-Identifier: GPL-3.0-or-later
# Lightweight test for tools/run_go_no_go_gates.py
# Verifies: script runs (subset), emits artifacts with expected keys.

import json
import os
import subprocess
from pathlib import Path

SCRIPT = Path("tools/run_go_no_go_gates.py")


def test_gate_script_enumeration_and_artifacts(tmp_path, monkeypatch):
    assert SCRIPT.exists(), "run_go_no_go_gates.py missing"
    # Use temp working dir for artifacts but keep project root on PYTHONPATH
    monkeypatch.chdir(tmp_path)
    env = os.environ.copy()
    env.setdefault("AETHERRA_PROFILE", "test")
    # Run only two quick gates to keep test fast (launcher + policy, which start minimal hub instances)
    cmd = ["python", str(SCRIPT), "--gates", "launcher_smoke", "policy_privacy"]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    # Non-zero may occur if a gate fails; still assert artifacts exist to surface partial failures.
    assert (tmp_path / "gate_results.json").exists(), proc.stderr + proc.stdout
    assert (tmp_path / "gate_sign_off.md").exists(), "sign off artifact missing"
    data = json.loads((tmp_path / "gate_results.json").read_text())
    assert "launcher_smoke" in data, "launcher smoke result missing"
    assert "policy_privacy" in data, "policy privacy result missing"
    # Required metadata keys
    meta = data.get("_meta") or {}
    assert "profile" in meta and meta.get("profile") == env["AETHERRA_PROFILE"]
    # Ensure each included gate result has ok/manual keys
    for k in ("launcher_smoke", "policy_privacy"):
        r = data.get(k) or {}
        assert "ok" in r and "manual" in r
