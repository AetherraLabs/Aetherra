"""Diagnostics belong to the selected quality pytest, not its nested invocations."""

# Standard library imports
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from tools import quality_gates

REPO = Path(quality_gates.__file__).resolve().parent.parent


def selected_command(monkeypatch, tmp_path, target, *, cwd=REPO):
    monkeypatch.chdir(cwd)
    for name, value in {
        "LOCK_ENFORCE": "0",
        "VULN_SCAN": "0",
        "TEST_SELECTION": "0",
        "TEST_TARGETS": str(target),
        "MIN_COVERAGE": "0",
        "TEST_TIMEOUT": "900",
        "COVERAGE_BASELINE_FILE": str(tmp_path / "baseline"),
    }.items():
        monkeypatch.setenv(name, value)
    calls = []

    def run(command, timeout=None):
        calls.append((command, timeout))
        return 124, "synthetic pytest timeout"

    monkeypatch.setattr(quality_gates, "run", run)
    assert quality_gates.main() == 124
    assert len(calls) == 1
    return calls[0]


@pytest.mark.parametrize("enabled", [False, True])
@pytest.mark.parametrize("source_checkout", [False, True])
def test_opt_in_preserves_selection_timeout_and_autoload_environment(
    monkeypatch, tmp_path, enabled, source_checkout
):
    if enabled:
        monkeypatch.setenv("AETHERRA_CI_DIAGNOSTICS", str(tmp_path / "diagnostics"))
    else:
        monkeypatch.delenv("AETHERRA_CI_DIAGNOSTICS", raising=False)
    monkeypatch.setenv("PYTEST_ADDOPTS", "--tb=short")
    monkeypatch.setenv("PYTEST_PLUGINS", "existing_plugin")
    command, timeout = selected_command(
        monkeypatch,
        tmp_path,
        "selected_test.py",
        cwd=REPO if source_checkout else tmp_path,
    )
    expected = enabled and source_checkout
    assert command[:3] == [sys.executable, "-m", "pytest"]
    assert command[-1] == "selected_test.py"
    assert "--cov=." in command
    assert "--cov-fail-under=0" in command
    assert timeout == 900
    assert ("tools.ci_capabilities_phase" in command) is expected
    assert ("faulthandler_timeout=60" in command) is expected
    assert os.environ["PYTEST_ADDOPTS"] == "--tb=short"
    assert os.environ["PYTEST_PLUGINS"] == "existing_plugin"


def test_selected_pytest_loads_phase_plugin_without_infecting_nested_pytest(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("AETHERRA_CI_DIAGNOSTICS", str(tmp_path / "diagnostics"))
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"):
        monkeypatch.delenv(name, raising=False)
    target = tmp_path / "test_selected.py"
    target.write_text(
        "import os, subprocess, sys\n"
        "def test_selected(tmp_path):\n"
        "    assert 'tools.ci_capabilities_phase' in sys.modules\n"
        "    nested = tmp_path / 'independent-repository'\n"
        "    nested.mkdir()\n"
        "    (nested / 'test_nested.py').write_text(\"import sys\\n"
        "def test_nested():\\n"
        "    assert 'tools.ci_capabilities_phase' not in sys.modules\\n\")\n"
        "    result = subprocess.run(\n"
        "        [sys.executable, '-m', 'pytest', '-q', '-o', 'addopts=', 'test_nested.py'],\n"
        "        cwd=nested, env=os.environ.copy(), capture_output=True, text=True, timeout=15)\n"
        "    assert result.returncode == 0, result.stdout + result.stderr\n",
        encoding="utf-8",
    )
    command, _ = selected_command(monkeypatch, tmp_path, os.path.relpath(target, REPO))
    result = subprocess.run(
        command,
        cwd=REPO,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "diagnostics" / "phases.jsonl").exists()


def test_diagnostic_parent_preserves_nested_quality_gate_reports(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_CI_DIAGNOSTICS", str(tmp_path / "diagnostics"))
    for name in ("PYTEST_ADDOPTS", "PYTEST_PLUGINS", "PYTHONPATH"):
        monkeypatch.delenv(name, raising=False)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-o",
            "addopts=",
            "-p",
            "tools.ci_capabilities_phase",
            "tests/tools/test_quality_gates_pr_description.py::test_pr_description_generation",
        ],
        cwd=REPO,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "2 passed" in result.stdout
    assert (tmp_path / "diagnostics" / "phases.jsonl").exists()
