"""Gate output handling and real CLI reports with isolated coverage fixtures."""

import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tools import quality_gates

ROOT = Path(__file__).resolve().parents[2]


def test_push_scanner_tooling_is_isolated():
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/ci_quality_gates.yml").read_text(encoding="utf-8")
    )
    steps = workflow["jobs"]["quality-gates"]["steps"]
    audit = next(
        (
            step
            for step in steps
            if step.get("name") == "Install isolated vulnerability tooling"
        ),
        None,
    )
    assert audit is not None
    assert audit["if"] == "github.event_name == 'push'"
    assert "python -m venv" in audit["run"]
    assert "$RUNNER_TEMP" in audit["run"]
    assert "$GITHUB_PATH" in audit["run"]
    assert "--system-site-packages" not in audit["run"]
    assert "pip-audit==2.10.1" in audit["run"]
    assert 'echo "$audit_env/bin"' not in audit["run"]
    assert 'ln -s "$audit_env/bin/pip-audit" "$audit_bin/pip-audit"' in audit["run"]
    gates = next(step for step in steps if step.get("name") == "Run quality gates")
    assert (
        gates["env"]["TEST_TARGETS"]
        == "tests/capabilities tests/unit tests/integration"
    )
    assert (
        gates["env"]["VULN_SCAN"] == "${{ github.event_name == 'push' && '1' || '0' }}"
    )


def test_requested_vulnerability_wrapper_missing_fails(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.lock").write_text("example==1.0\n", encoding="utf-8")
    monkeypatch.setenv("LOCK_FILE", "requirements.lock")
    monkeypatch.setenv("LOCK_ENFORCE", "0")
    monkeypatch.setenv("VULN_SCAN", "1")

    def unexpected_execution(*args, **kwargs):
        pytest.fail("Missing requested scanner must stop before subsequent stages")

    monkeypatch.setattr(quality_gates, "run", unexpected_execution)
    assert quality_gates.main() == 1


def test_vulnerability_gate_forwards_exact_pins_and_stops_on_failure(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.lock").write_text("example==1.0\n", encoding="utf-8")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools/vuln_scan.py").touch()
    monkeypatch.setenv("LOCK_FILE", "requirements.lock")
    monkeypatch.setenv("LOCK_ENFORCE", "0")
    monkeypatch.setenv("VULN_SCAN", "1")
    calls = []

    def failed_scan(command, **kwargs):
        calls.append(command)
        return 2, "unavailable"

    monkeypatch.setattr(quality_gates, "run", failed_scan)
    assert quality_gates.main() == 1
    assert len(calls) == 1
    assert "--exact-pins" in calls[0]


@pytest.mark.parametrize(
    ("code", "fatal", "expected"), [(0, True, True), (9, True, False), (9, False, True)]
)
def test_optional_tool_legacy_console(monkeypatch, code, fatal, expected):
    buffer = io.BytesIO()
    with io.TextIOWrapper(buffer, encoding="cp1252", errors="strict") as console:
        monkeypatch.setattr(quality_gates.sys, "stdout", console)
        monkeypatch.setattr(quality_gates, "run", lambda args: (code, "child \ufffd"))
        assert (
            quality_gates.run_optional_tool("fixture", ["fixture"], fatal) is expected
        )
        console.flush()
        output = buffer.getvalue().decode("cp1252")
        assert "child \\ufffd" in output
        assert (f"failed with exit {code}" in output) is (code != 0)


@pytest.mark.parametrize("code", [9, 124])
def test_main_legacy_console_preserves_failure(monkeypatch, tmp_path, code):
    monkeypatch.chdir(tmp_path)
    for name in ("LOCK_ENFORCE", "VULN_SCAN", "TEST_SELECTION"):
        monkeypatch.setenv(name, "0")
    monkeypatch.setenv("TEST_TARGETS", "fixture.py")
    monkeypatch.setenv("LICENSE_UNKNOWN_TREND_FAIL", "1")
    monkeypatch.setenv("LICENSE_UNKNOWN_TOLERANCE", "0")
    monkeypatch.setattr(
        quality_gates, "run", lambda args, timeout: (code, "pytest \ufffd")
    )
    buffer = io.BytesIO()
    with io.TextIOWrapper(buffer, encoding="cp1252", errors="strict") as console:
        monkeypatch.setattr(quality_gates.sys, "stdout", console)
        assert quality_gates.main() == code
        console.flush()
        assert "pytest \\ufffd" in buffer.getvalue().decode("cp1252")


@pytest.mark.parametrize("partial", [b"partial \xff", "partial text", None])
def test_timeout_output_is_text(monkeypatch, partial):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(["fixture"], 1, output=partial)

    monkeypatch.setattr(quality_gates.subprocess, "run", timeout)
    code, output = quality_gates.run(["fixture"], timeout=1)
    expected = (
        partial.decode("utf-8", errors="replace")
        if isinstance(partial, bytes)
        else partial or ""
    )
    assert code == 124
    assert output == expected + "\n[TIMEOUT] Command exceeded 1s: fixture"


@pytest.mark.parametrize("code", [0, 9])
def test_python_child_text_encoding_is_local(monkeypatch, code):
    monkeypatch.setenv("PYTHONIOENCODING", "ascii:strict")
    command = [
        sys.executable,
        "-c",
        f"import sys; print(chr(0x2603)); sys.exit({code})",
    ]
    actual, output = quality_gates.run(command, timeout=5)
    assert actual == code, output
    assert output.strip() == "\u2603"
    assert os.environ["PYTHONIOENCODING"] == "ascii:strict"


def test_real_python_timeout_preserves_partial_output():
    command = [
        sys.executable,
        "-c",
        "import time; print(chr(0x2603), flush=True); time.sleep(30)",
    ]
    code, output = quality_gates.run(command, timeout=2)
    assert code == 124
    assert output.startswith("\u2603\n")
    assert "[TIMEOUT] Command exceeded 2s:" in output


def test_console_configuration_supports_text_capture(monkeypatch):
    output = io.StringIO()
    monkeypatch.setattr(quality_gates.sys, "stdout", output)
    monkeypatch.setattr(quality_gates.sys, "stderr", io.StringIO())
    monkeypatch.setattr(quality_gates, "run", lambda args: (0, "child \ufffd"))
    assert quality_gates.run_optional_tool("fixture", ["fixture"])
    assert "child \ufffd" in output.getvalue()


def run_quality_gates(env: dict[str, str], cwd: Path) -> tuple[int, str]:
    child_env = os.environ.copy()
    child_env.update(env)
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "quality_gates.py")],
        cwd=cwd,
        env=child_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return result.returncode, result.stdout


@pytest.mark.parametrize("previous", [0.0, 100.0])
def test_pr_description_generation(tmp_path, previous):
    leaf = tmp_path / "test_report_leaf.py"
    leaf.write_text(
        "def covered():\n    return 3\n\n"
        "def not_exercised():\n    return 7\n\n"
        "def test_leaf():\n    assert covered() == 3\n",
        encoding="utf-8",
    )
    (tmp_path / "coverage.ini").write_text("[run]\nsource = .\n", encoding="utf-8")
    baseline = tmp_path / ".coverage-baseline"
    baseline.write_text(str(previous), encoding="utf-8")
    env = dict.fromkeys(
        (
            "LOCK_ENFORCE",
            "VULN_SCAN",
            "ARCH_CHECK",
            "LICENSE_REPORT",
            "TEST_SELECTION",
            "COVERAGE_FILE_LEVEL",
            "REPO_SECURITY_SCAN",
            "DISCORD_EXCLUSION_CHECK",
            "WEBSITE_ARTIFACT_CHECK",
            "STATIC_SECURITY_SCAN",
            "FRAGMENTATION_CHECK",
            "SBOM_GENERATE",
            "REQUIRE_THREAT_MODEL",
            "REQUIRE_LICENSE_POLICY",
            "PACKAGE_SMOKE",
            "PUBLISH_ARTIFACTS",
            "CONSCIOUSNESS_METRICS_CHECK",
        ),
        "0",
    )
    env.update(
        {
            "GENERATE_PR_DESCRIPTION": "1",
            "PR_DESCRIPTION_PATH": "pr_desc.md",
            "COVERAGE_REPORT_JSON": "coverage_gate_report.json",
            "COVERAGE_BASELINE_FILE": str(baseline),
            "MIN_COVERAGE": "0",
            "TEST_TARGETS": leaf.name,
            "TEST_TIMEOUT": "15",
            "COVERAGE_FILE": str(tmp_path / ".coverage"),
            "PYTEST_ADDOPTS": (
                "--cov-config=coverage.ini "
                f'-o cache_dir="{(tmp_path / ".pytest_cache").as_posix()}"'
            ),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTEST_PLUGINS": "pytest_cov.plugin",
            "AETHERRA_SKIP_DOTENV": "1",
            "AETHERRA_LYRIXA_FORCE_OFFLINE": "1",
        }
    )
    code, output = run_quality_gates(env, tmp_path)
    drop = previous == 100.0
    assert code == int(drop), output
    description = tmp_path / "pr_desc.md"
    assert description.is_file(), output
    text = description.read_text(encoding="utf-8")
    report = json.loads(
        (tmp_path / "coverage_gate_report.json").read_text(encoding="utf-8")
    )
    assert 0 < report["coverage"] < 100
    assert report["drop"] is drop
    assert report["updated_baseline"] is not drop
    assert report["targets"] == [leaf.name]
    assert report["previous"] == previous
    assert report["delta"] == report["coverage"] - previous
    assert text.startswith("# Quality Gates Summary")
    assert f"Schema Version: {report['schema_version']}" in text
    assert "Future Flags" in text
    assert f"Gate Result: {'FAIL' if drop else 'PASS'}" in text
    summary = re.search(
        r"Overall Coverage: (\d+\.\d+)% \(prev (\d+\.\d+)% delta ([+\-]\d+\.\d+)%\)",
        text,
    )
    assert summary is not None
    assert tuple(float(value) for value in summary.groups()) == (
        report["coverage"],
        report["previous"],
        report["delta"],
    )
    for name, value in report["future"].items():
        assert f"* {name}: {value}" in text
    if drop:
        assert "## Gating Reasons" in text
        assert "| Code | Severity | Message |" in text
        for reason in report["gating_reasons"]:
            message = reason["message"].replace("|", "/")
            assert f"| {reason['code']} | {reason['severity']} | {message} |" in text
        assert float(baseline.read_text(encoding="utf-8")) == previous
    else:
        assert float(baseline.read_text(encoding="utf-8")) == report["coverage"]
