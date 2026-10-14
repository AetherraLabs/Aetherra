# Standard library imports
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest
import requests

# Aetherra imports
from tools import quality_gates


@pytest.fixture(autouse=True)
def restore_gate_environment(monkeypatch):
    for name in ("LICENSE_UNKNOWN_TREND_FAIL", "LICENSE_UNKNOWN_TOLERANCE"):
        if name in os.environ:
            monkeypatch.setenv(name, os.environ[name])
        else:
            monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("output", [b"partial\xff", "partial", None])
def test_timeout_returns_failure_with_decoded_output(monkeypatch, output):
    def expire(*args, **kwargs):
        raise subprocess.TimeoutExpired(["synthetic"], 1, output=output)

    monkeypatch.setattr(quality_gates.subprocess, "run", expire)
    code, diagnostic = quality_gates.run(["synthetic"], timeout=1)
    assert code == 124
    assert "[TIMEOUT]" in diagnostic
    if output is not None:
        assert diagnostic.startswith("partial")


@pytest.mark.parametrize("value", ["broken", "", "nan", "inf", "-1", "101"])
def test_invalid_baseline_fails_gate_without_overwriting(monkeypatch, tmp_path, value):
    baseline = tmp_path / "baseline"
    baseline.write_text(value, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    for name, setting in {
        "COVERAGE_BASELINE_FILE": str(baseline),
        "LOCK_ENFORCE": "0",
        "VULN_SCAN": "0",
        "TEST_SELECTION": "0",
        "TEST_TARGETS": "synthetic",
        "MIN_COVERAGE": "0",
    }.items():
        monkeypatch.setenv(name, setting)
    monkeypatch.setattr(quality_gates, "run", lambda *a, **kw: (0, "TOTAL 10 0 100%"))
    assert quality_gates.main() == 1
    assert baseline.read_text(encoding="utf-8") == value


@pytest.mark.parametrize("value", ["0", "83.5", "100"])
def test_valid_baseline_is_read(tmp_path, value):
    baseline = tmp_path / "baseline"
    baseline.write_text(value, encoding="utf-8")
    assert quality_gates.read_coverage_baseline(baseline) == float(value)


def test_missing_baseline_allows_initial_run(tmp_path):
    assert quality_gates.read_coverage_baseline(tmp_path / "absent") is None


def test_unreadable_baseline_does_not_become_missing(monkeypatch, tmp_path):
    def denied(*args, **kwargs):
        raise PermissionError("private filesystem detail")

    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(OSError, match="Cannot read coverage baseline") as failure:
        quality_gates.read_coverage_baseline(tmp_path / "baseline")
    assert "private filesystem detail" not in str(failure.value)


@pytest.fixture
def synthetic_gate(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name, setting in {
        "COVERAGE_BASELINE_FILE": str(tmp_path / "baseline"),
        "LOCK_ENFORCE": "0",
        "VULN_SCAN": "0",
        "TEST_SELECTION": "0",
        "TEST_TARGETS": "synthetic",
        "MIN_COVERAGE": "0",
        "ARCH_CHECK": "0",
        "LICENSE_REPORT": "0",
        "COVERAGE_FILE_LEVEL": "0",
        "PACKAGE_SMOKE": "0",
        "PUBLISH_ARTIFACTS": "0",
        "CONSCIOUSNESS_METRICS_CHECK": "0",
        "GENERATE_PR_DESCRIPTION": "0",
    }.items():
        monkeypatch.setenv(name, setting)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/THREAT_MODEL.md").write_text("synthetic", encoding="utf-8")
    (tmp_path / "LICENSE_POLICY.md").write_text("synthetic", encoding="utf-8")
    monkeypatch.setattr(quality_gates, "run", lambda *a, **kw: (0, "TOTAL 10 2 80%"))
    return tmp_path / "baseline"


def test_first_success_creates_baseline(synthetic_gate):
    assert quality_gates.main() == 0
    assert synthetic_gate.read_text(encoding="utf-8") == "80.0"


def test_coverage_drop_preserves_existing_baseline(synthetic_gate):
    synthetic_gate.write_text("90", encoding="utf-8")
    assert quality_gates.main() == 1
    assert synthetic_gate.read_text(encoding="utf-8") == "90"


def test_baseline_write_failure_fails_closed(synthetic_gate, monkeypatch, capsys):
    original_write = Path.write_text

    def denied(path, *args, **kwargs):
        if path == synthetic_gate:
            raise PermissionError("private filesystem detail")
        return original_write(path, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", denied)
    assert quality_gates.main() == 1
    assert "private filesystem detail" not in capsys.readouterr().out


def test_invalid_utf8_baseline_fails_without_replacement(synthetic_gate, capsys):
    synthetic_gate.write_bytes(b"\xff")
    assert quality_gates.main() == 1
    assert synthetic_gate.read_bytes() == b"\xff"
    assert "Coverage baseline unavailable or invalid" in capsys.readouterr().out


def test_unreadable_baseline_fails_main_with_sanitized_output(
    synthetic_gate, monkeypatch, capsys
):
    def denied(*args, **kwargs):
        raise PermissionError("private filesystem detail")

    monkeypatch.setattr(Path, "read_text", denied)
    assert quality_gates.main() == 1
    output = capsys.readouterr().out
    assert "Coverage baseline unavailable or invalid" in output
    assert "private filesystem detail" not in output


@pytest.mark.parametrize(
    "url", ["file:///private", "ftp://example.invalid", "https://"]
)
def test_metrics_fetch_rejects_non_http_endpoint_before_transport(monkeypatch, url):
    calls = []
    monkeypatch.setattr(requests, "get", lambda *a, **kw: calls.append((a, kw)))
    with pytest.raises(ValueError, match="Invalid metrics endpoint"):
        quality_gates.fetch_metrics(url)
    assert calls == []


@pytest.mark.parametrize("status", [301, 302, 403, 500])
def test_metrics_fetch_rejects_redirect_and_error_responses(monkeypatch, status):
    calls = []

    def transport(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(status_code=status, content=b"not metrics")

    monkeypatch.setattr(requests, "get", transport)
    with pytest.raises(ValueError, match="Metrics endpoint returned non-success"):
        quality_gates.fetch_metrics("http://127.0.0.1:9109/metrics")
    assert calls == [
        ("http://127.0.0.1:9109/metrics", {"timeout": 3, "allow_redirects": False})
    ]


def test_metrics_fetch_retains_utf8_replacement(monkeypatch):
    monkeypatch.setattr(
        requests,
        "get",
        lambda *a, **kw: SimpleNamespace(status_code=200, content=b"metric 1\n\xff"),
    )
    assert quality_gates.fetch_metrics("https://example.invalid/metrics") == (
        "metric 1\n" + chr(0xFFFD)
    )
