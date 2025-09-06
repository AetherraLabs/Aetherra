# SPDX-License-Identifier: GPL-3.0-or-later
"""Unit test: enforce_license_policy emits metric line and trend log, applies overrides.

Creates a tiny synthetic licenses_report.json with three packages:
- one UNKNOWN (kept)
- one UNKNOWN but overridden (attrs)
- one explicit MIT
Verifies:
  * license_unknown_total reflects only the non-overridden UNKNOWN (1)
  * summary line present
  * trend log appended
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def run_script(cwd: Path, env: dict[str, str]) -> tuple[int, str, str]:
    proc = subprocess.Popen(
        [sys.executable, "tools/enforce_license_policy.py"],
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    out, err = proc.communicate(timeout=10)
    return proc.returncode, out, err


def test_license_metric_and_overrides(tmp_path: Path):
    # Prepare minimal project copy context: we only need the tool script & overrides file
    project_root = Path.cwd()
    # Write synthetic licenses_report.json
    report = {
        "rows": [
            {"name": "attrs", "license": "UNKNOWN"},  # overridden
            {"name": "someunknownpkg", "license": "UNKNOWN"},  # counts
            {"name": "simplejson", "license": "MIT"},  # normal
        ]
    }
    (tmp_path / "licenses_report.json").write_text(json.dumps(report), encoding="utf-8")

    # Copy enforcement script & overrides into temp dir to isolate side effects
    enforce_src = project_root / "tools" / "enforce_license_policy.py"
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "enforce_license_policy.py").write_text(
        enforce_src.read_text(encoding="utf-8"), encoding="utf-8"
    )
    # Create a fresh overrides file (space-indented) to avoid any formatting issues in repo file
    overrides_content = (
        "packages:\n"
        "  attrs:\n"
        "    license: Apache-2.0 OR MIT\n"
        "    reason: Test override for attrs UNKNOWN mapping.\n"
        "    approved_by: test\n"
    )
    (tmp_path / "license_overrides.yml").write_text(overrides_content, encoding="utf-8")

    env = os.environ.copy()
    env["LICENSE_REPORT_JSON"] = str(tmp_path / "licenses_report.json")
    env["PYTHONPATH"] = str(project_root)
    env["LICENSE_OVERRIDES_FILE"] = str(tmp_path / "license_overrides.yml")
    trend_log = tmp_path / "license_unknown_trend.log"
    env["LICENSE_TREND_LOG"] = str(trend_log)

    code, out, err = run_script(tmp_path, env)
    assert code == 0, f"expected success, got {code} err={err} out={out}"
    # Metric line
    m = re.search(r"license_unknown_total (\d+)", out)
    assert m, f"metric line missing: out={out}"
    assert m.group(1) == "1", (
        f"expected 1 unknown after overrides, got {m.group(1)} out={out}"
    )
    # Summary line
    assert "[LICENSE_ENFORCE]" in out
    # Trend log
    assert trend_log.is_file(), "trend log not created"
    log_lines = trend_log.read_text(encoding="utf-8").strip().splitlines()
    assert log_lines, "trend log empty"
    assert any("unknown=1" in ln for ln in log_lines), (
        f"trend log missing unknown=1 line: {log_lines}"
    )
