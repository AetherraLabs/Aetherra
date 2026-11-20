"""The legacy style allowance must never hide new code or tool failures."""

# Standard library imports
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

GIT = shutil.which("git")
SCRIPT = Path(__file__).resolve().parents[2] / "tools/python_quality.py"


def run_quality(root, *args):
    env = {**os.environ, "NO_COLOR": "1", "PYTHONUTF8": "1"}
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
        check=False,
    )


@pytest.fixture
def legacy(tmp_path):
    subprocess.run([GIT, "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.ruff.lint]\nselect = ["F"]\n', encoding="utf-8"
    )
    (tmp_path / "old.py").write_text("import os\nx=1\n", encoding="utf-8")
    subprocess.run([GIT, "add", "old.py", "pyproject.toml"], cwd=tmp_path, check=True)
    baseline = tmp_path / "baseline.json"
    result = run_quality(tmp_path, "--write-baseline", str(baseline))
    assert result.returncode == 0, result.stdout + result.stderr
    return tmp_path, baseline


def test_exact_legacy_source_passes_without_rewriting_baseline(legacy):
    root, baseline = legacy
    before = baseline.read_bytes()
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 0, result.stdout + result.stderr
    assert baseline.read_bytes() == before


@pytest.mark.parametrize("name", ["old.py", "new.py"])
def test_edited_or_new_source_cannot_borrow_a_legacy_allowance(legacy, name):
    root, baseline = legacy
    (root / name).write_text("import os\nimport sys\nx=1\n", encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 1, result.stdout + result.stderr
    assert name in result.stdout


def test_cleaned_source_is_allowed_and_removed_debt_is_reported(legacy):
    root, baseline = legacy
    (root / "old.py").write_text("x = 1\n", encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "resolved" in result.stdout


def test_invalid_python_cannot_be_baselined(tmp_path):
    (tmp_path / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    baseline = tmp_path / "baseline.json"
    result = run_quality(tmp_path, "--write-baseline", str(baseline))
    assert result.returncode != 0
    assert not baseline.exists()
    assert "critical" in result.stdout.lower()


def test_weaker_configuration_cannot_reuse_the_baseline(legacy):
    root, baseline = legacy
    (root / "pyproject.toml").write_text(
        "[tool.ruff.lint]\nselect = []\n", encoding="utf-8"
    )
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode != 0
    assert "configuration" in result.stdout.lower()


def test_missing_or_different_tool_version_fails_closed(legacy):
    root, baseline = legacy
    data = json.loads(baseline.read_text(encoding="utf-8"))
    data["versions"]["ruff"] = "0.0.0"
    baseline.write_text(json.dumps(data), encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode != 0
    assert "version" in result.stdout.lower()


def test_windows_line_endings_do_not_change_the_allowance(legacy):
    root, baseline = legacy
    (root / "old.py").write_bytes(b"import os\r\nx=1\r\n")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 0, result.stdout + result.stderr


def test_generated_ignored_fixture_is_not_repository_source(legacy):
    root, baseline = legacy
    (root / ".gitignore").write_text("generated/\n", encoding="utf-8")
    generated = root / "generated"
    generated.mkdir()
    (generated / "fixture.py").write_text("def broken(:\n", encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 0, result.stdout + result.stderr


def test_gitignore_cannot_hide_tracked_critical_error(legacy):
    root, baseline = legacy
    (root / ".gitignore").write_text("old.py\n", encoding="utf-8")
    (root / "old.py").write_text("def broken(:\n", encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode != 0
    assert "critical" in result.stdout.lower()


def test_nested_configuration_cannot_hide_a_new_violation(legacy):
    root, baseline = legacy
    nested = root / "package"
    nested.mkdir()
    (nested / "pyproject.toml").write_text(
        "[tool.ruff.lint]\nselect = []\n", encoding="utf-8"
    )
    (nested / "new.py").write_text("import os\n\nx = 1\n", encoding="utf-8")
    result = run_quality(root, "--baseline", str(baseline))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "package/new.py: ruff" in result.stdout


def test_source_archive_includes_hidden_python_files(tmp_path):
    # Aetherra imports
    from tools.python_quality import source_files

    (tmp_path / ".hidden.py").write_text("x = 1\n", encoding="utf-8")
    assert source_files(tmp_path) == [".hidden.py"]
