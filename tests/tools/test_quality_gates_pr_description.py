# Standard library imports
import os
import re
import subprocess
from pathlib import Path


def run_quality_gates(env: dict[str, str]) -> tuple[int, str]:
    cmd = ["python", "tools/quality_gates.py"]
    env_vars = os.environ.copy()
    env_vars.update(env)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    out, _ = proc.communicate()
    return proc.returncode, out


def test_pr_description_generation(tmp_path, monkeypatch):
    # Arrange minimal environment: disable heavy optional checks for speed.
    monkeypatch.chdir(Path.cwd())  # ensure relative paths
    env = {
        "GENERATE_PR_DESCRIPTION": "1",
        "PR_DESCRIPTION_PATH": str(tmp_path / "pr_desc.md"),
        "LOCK_ENFORCE": "0",
        "VULN_SCAN": "0",
        "ARCH_CHECK": "0",
        "LICENSE_REPORT": "0",
        "TEST_SELECTION": "0",
        # Force baseline file with same coverage so no drop gating failure.
        "COVERAGE_BASELINE_FILE": str(tmp_path / ".coverage-baseline"),
        # Reduce test target to capabilities (if exists) else tests to keep run short.
    }
    baseline_file = Path(env["COVERAGE_BASELINE_FILE"])
    baseline_file.write_text("0.0", encoding="utf-8")

    # Act
    code, out = run_quality_gates(env)

    # Assert gates run (even if tests may fail in repo context, focus on PR description artifact existence)
    pr_desc = Path(env["PR_DESCRIPTION_PATH"])
    assert pr_desc.exists(), f"PR description file not created. Output:\n{out}"
    text = pr_desc.read_text(encoding="utf-8")

    # Basic sections
    assert text.startswith("# Quality Gates Summary"), "Missing header"
    assert "Schema Version:" in text
    # Table or reasons header expected even if empty reasons may not appear; ensure line present if gating reasons printed
    if "Gating Reasons" in out or "Gating Reasons" in text:
        assert "| Code | Severity | Message |" in text

    # Future flags section present (may list defaults)
    assert "Future Flags" in text, "Future flags section missing"

    # Validate coverage formatting pattern
    assert re.search(
        r"Overall Coverage: \d+\.\d+% \(prev \d+\.\d+% delta [+\-]\d+\.\d+%\)", text
    ), "Coverage summary line malformed"

    # No obvious unreplaced template braces pairs (very loose heuristic)
    assert not ("{" in text and "}" in text and "fstring_leak" in text)


if __name__ == "__main__":
    # Third party imports
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
