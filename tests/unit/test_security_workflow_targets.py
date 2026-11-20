"""Security CI must exercise the active read-only interface, not retired Qt UI."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_security_sanity_checks_active_runtime_ui_without_failure_fallback():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/security-sanity.yml").read_text(encoding="utf-8"),
    )
    job = workflow["jobs"]["security"]
    steps = job["steps"]
    targets = {
        "tests/unit/test_runtime_ui_contract.py",
        "tests/unit/test_runtime_ui_manifest.py",
    }
    ui_steps = [
        step for step in steps if "runtime_ui_contract.py" in step.get("run", "")
    ]
    assert len(ui_steps) == 1
    step = ui_steps[0]
    command = step["run"]
    assert "python -m pytest -q -o addopts=" in command
    for target in targets:
        assert (ROOT / target).is_file()
        assert target in command
    assert "||" not in command
    assert "continue-on-error" not in step
    assert "continue-on-error" not in job
    assert "test_gui_smoke.py" not in str(steps)
    assert job["strategy"]["matrix"]["os"] == ["ubuntu-latest", "windows-latest"]
    assert job["env"]["AETHERRA_SIGNING_STRICT"] == "1"
    assert job["env"]["AETHERRA_SCRIPT_VERIFY_STRICT"] == "1"


def test_security_script_verification_cannot_mask_failure():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/security-sanity.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["security"]["steps"]
    step = next(
        step for step in steps if "tools/verify_aether_scripts.py" in step.get("run", "")
    )
    assert "--strict" in step["run"]
    assert "||" not in step["run"]
    assert "continue-on-error" not in step
