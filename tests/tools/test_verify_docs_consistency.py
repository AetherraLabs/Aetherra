import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "verify_docs_consistency.py"
DEBUG_JSON = ROOT / "docs" / "DOCS_CONSISTENCY_DEBUG.json"


def run(cmd, env=None):
    result = subprocess.run(
        [sys.executable, *cmd],
        cwd=ROOT,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
    )
    return result


def test_basic_run_exit_zero():
    r = run([str(SCRIPT)])
    assert r.returncode == 0, (
        f"Non-zero exit code. stdout=\n{r.stdout}\n--- stderr=\n{r.stderr}"
    )


def test_debug_flag_creates_json():
    if DEBUG_JSON.exists():
        DEBUG_JSON.unlink()
    r = run([str(SCRIPT), "--debug"])
    assert r.returncode == 0, "Debug run failed"
    assert DEBUG_JSON.exists(), "Expected debug JSON artifact not created"
    data = json.loads(DEBUG_JSON.read_text())
    # Minimal schema keys
    for key in [
        "timestamp",
        "code_envs_count",
        "doc_envs_count",
        "missing_envs",
        "raw_extra_envs",
        "suppressed_doc_only_envs",
        "extra_envs_reported",
        "code_routes_count",
        "doc_routes_count",
        "missing_routes",
        "extra_routes",
        "missing_consciousness_metrics",
    ]:
        assert key in data, f"Missing key in debug JSON: {key}"


def test_env_var_triggers_debug_json():
    if DEBUG_JSON.exists():
        DEBUG_JSON.unlink()
    env = os.environ.copy()
    env["AETHERRA_DOCS_DEBUG"] = "1"
    r = run([str(SCRIPT)], env=env)
    assert r.returncode == 0, "Env var debug run failed"
    assert DEBUG_JSON.exists(), "Expected debug JSON via env var not created"
    data = json.loads(DEBUG_JSON.read_text())
    assert isinstance(data.get("missing_envs"), list)
    assert isinstance(data.get("extra_routes"), list)
