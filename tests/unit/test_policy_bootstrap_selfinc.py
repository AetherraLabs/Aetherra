# Standard library imports
import importlib
from pathlib import Path
from typing import Any


def test_policy_bootstrap_selfinc(tmp_path: Path, monkeypatch: Any) -> None:
    # Point policy home to a temp directory
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path))
    mod = importlib.import_module("Aetherra.cli.policy_bootstrap")
    # Run main with --selfinc
    rc = mod.main(["--selfinc", "--force"])  # force to ensure write
    assert rc == 0
    out = tmp_path / "selfinc.json"
    assert out.exists(), "selfinc.json should be created"
    data = out.read_text(encoding="utf-8")
    assert '"version": ' in data
    assert "auto_integrate" in data
