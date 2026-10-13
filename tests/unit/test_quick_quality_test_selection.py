"""Exercise PowerShell argument expansion using a real disposable pytest run."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TARGET = "test_edit_plan_mirrors_suggestions_and_confidence_defaults"


@pytest.mark.parametrize(
    ("test_passes", "lint_exit", "expected_exit"),
    [(True, 0, 0), (False, 0, 1), (True, 9, 1)],
)
def test_quick_quality_selects_only_its_smoke_test(
    tmp_path, test_passes, lint_exit, expected_exit
):
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell is required to exercise the existing quality script")
    tests = tmp_path / "tests/capabilities"
    tests.mkdir(parents=True)
    (tests / "test_lyrixa_chat_bridge_schema.py").write_text(
        f"def {TARGET}():\n    assert {test_passes!r}\n",
        encoding="utf-8",
    )
    (tmp_path / "test_unrelated.py").write_text(
        "def test_unrelated():\n    raise AssertionError('unexpected collection')\n",
        encoding="utf-8",
    )
    interpreter = sys.executable.replace("'", "''")
    script = str(ROOT / "tools/quick_quality_check.ps1").replace("'", "''")
    driver = tmp_path / "driver.ps1"
    driver.write_text(
        f"function global:ruff {{ $global:LASTEXITCODE = {lint_exit} }}\n"
        "function global:black { $global:LASTEXITCODE = 0 }\n"
        "function global:isort { $global:LASTEXITCODE = 0 }\n"
        "function global:python { $global:LASTEXITCODE = 0 }\n"
        f"function global:pytest {{ & '{interpreter}' -m pytest @args -p no:cacheprovider; "
        "$global:LASTEXITCODE = $LASTEXITCODE }\n"
        f"& '{script}'\nexit $LASTEXITCODE\n",
        encoding="utf-8",
    )
    env = {
        key: value
        for key, value in os.environ.items()
        if not any(
            word in key.upper()
            for word in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
        )
    }
    env.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTEST_ADDOPTS="",
        PYTEST_PLUGINS="",
        PYTHONDONTWRITEBYTECODE="1",
        AETHERRA_SKIP_DOTENV="1",
    )
    result = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(driver)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    output = result.stdout + result.stderr
    assert "test_unrelated" not in output, output
    assert result.returncode == expected_exit, output
    assert ("1 passed" if test_passes else "1 failed") in output, output
    assert ("One or more checks failed" in output) is (expected_exit != 0)
