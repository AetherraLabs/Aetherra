# Standard library imports
from pathlib import Path

# Aetherra imports
from tools.static_security_scan import scan_root


def test_static_security_scan_baseline(tmp_path):
    # Run scan against repo root
    root = Path(".").resolve()
    report = scan_root(root)
    data = report.to_dict()
    # Ensure structure
    assert "findings" in data and "summary" in data
    # We allow existing medium-level style issues, but no critical secrets should be present
    critical = [f for f in data["findings"] if f["severity"] == "critical"]
    assert not critical, (
        f"Critical secrets found: {critical[:3]}"
    )  # show a sample if fails
