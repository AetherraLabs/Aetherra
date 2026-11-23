"""Test teardown must preserve inherited native environment values for child tools."""

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]
PROBE = """
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

root = Path(sys.argv[1])
git = shutil.which("git")
assert git, "Git is required for the environment isolation regression"
subprocess.run([git, "init", "-q", str(root / "before")], check=True)
names = (
    "AETHERRA_SIGNING_STRICT", "AETHERRA_ALLOW_UNSIGNED_DEV", "AETHERRA_PROFILE",
    "AETHERRA_HUB_SKIP_OPTIONALS", "AETHERRA_HUB_STRICT", "AETHERRA_STRICT",
    "AETHERRA_HUB_CONTROL_TOKEN", "AETHERRA_ETHICS_PROFILE", "AETHERRA_ETHICS_THRESHOLD",
    "AETHERRA_WORKSPACE_ROOT", "AETHERRA_POLICY_HOME", "AETHERRA_REQUIRE_CAPABILITIES",
    "AETHERRA_GUARDIAN_MODE",
)
original = {name: os.environ.get(name) for name in names}

class Outcomes:
    passed = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call" and report.passed:
            self.passed += 1

outcomes = Outcomes()
result = pytest.main([
    "-q", "-o", "addopts=", "-p", "no:cacheprovider",
    "--basetemp", str(root / "nested"), *sys.argv[2:]
], plugins=[outcomes])
assert result == 0 and outcomes.passed, "fixture exercise did not pass"
assert {name: os.environ.get(name) for name in names} == original, "policy flags leaked"
# Inherit the native environment, as ordinary Git callers do. Passing an explicit
# env here would conceal Windows losing empty native values during teardown.
subprocess.run([git, "init", "-q", str(root / "after")], check=True)
"""


@pytest.mark.parametrize(
    "selectors",
    [
        ["tests/capabilities/test_hub_plugin_and_chat_integration.py"],
        ["tests/integration/test_ethics_audit_integration.py"],
        [
            "tests/legacy/root_standalone/test_hub_blueprints_standalone.py"
            "::TestInteractiveBlueprint"
        ],
        [
            "tests/unit/test_script_executor.py::TestScriptExecutorIntegration"
            "::test_execution_writes_guardian_audit",
            "tests/unit/test_script_executor.py::TestScriptExecutorIntegration"
            "::test_execution_blocked_by_guardian_missing_capability",
        ],
    ],
    ids=["hub", "ethics", "legacy-blueprints", "script-executor"],
)
def test_fixture_teardown_preserves_native_git_environment(tmp_path, selectors):
    environment = {
        name: value
        for name, value in os.environ.items()
        if name.upper() in {"SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "COMSPEC"}
        or name.upper().startswith("GIT_CONFIG_")
    }
    index = int(environment.get("GIT_CONFIG_COUNT", "0"))
    environment.update(
        {
            "GIT_CONFIG_COUNT": str(index + 1),
            f"GIT_CONFIG_KEY_{index}": "test.aetherraEmpty",
            f"GIT_CONFIG_VALUE_{index}": "",
        }
    )
    environment.update(
        HOME=str(tmp_path),
        USERPROFILE=str(tmp_path),
        AETHERRA_SKIP_DOTENV="1",
        AETHERRA_LYRIXA_FORCE_OFFLINE="1",
        AETHERRA_STATE_DIR=str(tmp_path / "state"),
        AETHERRA_WORKSPACE_ROOT=str(tmp_path / "workspace"),
        AETHERRA_POLICY_HOME=str(tmp_path / "policy"),
        AETHERRA_PROFILE="test",
        AETHERRA_SIGNING_STRICT="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        PYTHONPATH=str(ROOT),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONUTF8="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    result = subprocess.run(
        [sys.executable, "-c", PROBE, str(tmp_path), *selectors],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "after" / ".git").is_dir()
