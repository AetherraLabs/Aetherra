import json
import os
import runpy
from pathlib import Path


def test_apply_overrides_only_changes_unknown(tmp_path):
    mod = runpy.run_path("tools/license_report.py")
    apply_overrides = mod["apply_overrides"]
    rows = [
        {"name": "PkgA", "version": "1", "license": "UNKNOWN"},
        {"name": "PkgB", "version": "1", "license": "MIT"},
    ]
    overrides = {"PkgA": "Apache-2.0", "PkgB": "GPL-3.0"}
    changed = apply_overrides(rows, overrides)
    assert changed == 1
    assert rows[0]["license"] == "Apache-2.0"
    assert rows[1]["license"] == "MIT"


def test_enforce_trend_and_absmax(tmp_path):
    env = os.environ
    report = tmp_path / "licenses_report.json"
    history = tmp_path / "hist.json"
    report.write_text(json.dumps([{"name": "x", "license": "UNKNOWN", "version": "0"}]))
    history.write_text(json.dumps([{"ts": 0, "unknown": 0}]))
    env["LICENSE_REPORT_JSON"] = str(report)
    env["LICENSE_ENFORCE_HISTORY_FILE"] = str(history)
    env["LICENSE_UNKNOWN_TREND_FAIL"] = "1"
    env["LICENSE_UNKNOWN_TOLERANCE"] = "0"
    mod = runpy.run_path("tools/enforce_license_policy.py")
    main = mod["main"]
    rc = main()
    assert rc == 1  # trend regression
    # set absolute max and rerun (still failure, abs max triggers)
    env["LICENSE_UNKNOWN_FAIL_IF_GT"] = "0"
    rc2 = main()
    assert rc2 == 1
    # clean report
    report.write_text(json.dumps([{"name": "x", "license": "MIT", "version": "0"}]))
    rc3 = main()
    assert rc3 == 0
