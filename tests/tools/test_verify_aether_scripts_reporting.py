# Standard library imports
import os
import sys
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
from tools import verify_aether_scripts as verifier


@pytest.fixture(autouse=True)
def restore_profile_environment(monkeypatch):
    for name in ("AETHERRA_PROFILE", "AETHERRA_DETERMINISTIC", "PYTHONHASHSEED"):
        if name in os.environ:
            monkeypatch.setenv(name, os.environ[name])
        else:
            monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("backend", ["Python", "NumPy"])
def test_seed_failure_has_sanitized_diagnostic(monkeypatch, capsys, backend):
    def fail(*args, **kwargs):
        raise RuntimeError("private seed detail")

    monkeypatch.setattr(
        verifier.random, "seed", fail if backend == "Python" else lambda _: None
    )
    monkeypatch.setattr(
        verifier,
        "_np",
        (
            SimpleNamespace(random=SimpleNamespace(seed=fail))
            if backend == "NumPy"
            else None
        ),
    )
    verifier._apply_profile("test")
    output = capsys.readouterr().err
    assert f"{backend} random seed failed (RuntimeError)" in output
    assert "private seed detail" not in output


def test_non_test_profile_does_not_seed(monkeypatch):
    calls = []
    monkeypatch.setattr(verifier.random, "seed", lambda value: calls.append(value))
    verifier._apply_profile("production")
    assert calls == []


@pytest.mark.parametrize(
    ("score", "strict", "expected"), [(5, False, 0), (6, False, 1), (0, True, 1)]
)
def test_report_retains_strict_risk_threshold(
    monkeypatch, tmp_path, score, strict, expected
):
    source = tmp_path / "synthetic.aether"
    source.write_text("# synthetic", encoding="utf-8")
    output = tmp_path / "report.md"
    monkeypatch.setenv("AETHERRA_SCRIPT_VERIFY_STRICT", "0")
    monkeypatch.setenv("AETHERRA_PROFILE", "production")
    monkeypatch.setattr(
        verifier,
        "analyze_paths",
        lambda files: {
            "total_score": score,
            "files": {
                str(source): {
                    "score": score,
                    "findings": [
                        {"kind": "synthetic", "line": line, "snippet": "synthetic"}
                        for line in (1, 2, 3)
                    ],
                }
            },
        },
    )
    arguments = [
        "verify",
        "--root",
        str(tmp_path),
        "--output",
        str(output),
        "--risk-threshold",
        "5",
        "--max-findings-per-file",
        "2",
    ]
    if strict:
        arguments.append("--strict")
    monkeypatch.setattr(sys, "argv", arguments)
    assert verifier.main() == expected
    report = output.read_text(encoding="utf-8")
    assert "L1: [synthetic]" in report
    assert "L2: [synthetic]" in report
    assert "L3: [synthetic]" not in report
    assert "...and 1 more lines (capped)" in report
    if strict:
        assert "## Signature Verification (strict)" in report
        assert ": FAIL (" in report
