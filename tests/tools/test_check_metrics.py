"""Metrics diagnostics are explicit, bounded, and fail truthfully."""

# Standard library imports
import runpy
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest
import requests

SCRIPT = Path(__file__).resolve().parents[2] / "tools/ops/check_metrics.py"


def load_script(monkeypatch, response=None, error=None):
    calls = []

    def get(url, **kwargs):
        calls.append((url, kwargs))
        if error is not None:
            raise error
        return response or SimpleNamespace(status_code=200, text="")

    monkeypatch.setattr(requests, "get", get)
    namespace = runpy.run_path(str(SCRIPT))
    return namespace, calls


def test_import_does_not_make_a_metrics_request(monkeypatch):
    _, calls = load_script(monkeypatch)
    assert calls == []


def test_main_reports_real_metrics_with_bounded_local_request(monkeypatch, capsys):
    response = SimpleNamespace(
        status_code=200,
        text='# HELP ignored\naetherra_storm_reads_total 2\naetherra_requests_total{kind="test"} 3\nprocess_cpu_seconds_total 4\n',
    )
    namespace, calls = load_script(monkeypatch, response)
    assert namespace["main"]() == 0
    assert calls == [
        ("http://127.0.0.1:3001/metrics", {"timeout": 5, "allow_redirects": False})
    ]
    output = capsys.readouterr().out
    assert "Total metrics: 3" in output
    assert "Found 1 STORM metrics" in output
    assert "Found 2 aetherra_ metrics" in output
    assert 'aetherra_requests_total{kind="test"} 3' in output


@pytest.mark.parametrize("status", [302, 503])
def test_main_rejects_redirects_and_server_errors(monkeypatch, capsys, status):
    namespace, _ = load_script(
        monkeypatch, SimpleNamespace(status_code=status, text="private error details")
    )
    assert namespace["main"]() == 1
    captured = capsys.readouterr()
    assert str(status) in captured.err
    assert "private error details" not in captured.err
    assert "Total metrics" not in captured.out


def test_main_reports_sanitized_transport_failure(monkeypatch, capsys):
    namespace, calls = load_script(
        monkeypatch, error=requests.Timeout("private network details")
    )
    assert namespace["main"]() == 1
    captured = capsys.readouterr()
    assert "Timeout" in captured.err
    assert "private network details" not in captured.err
    assert len(calls) == 1


def test_main_ignores_whitespace_only_lines_and_indented_comments(monkeypatch, capsys):
    namespace, _ = load_script(
        monkeypatch,
        SimpleNamespace(
            status_code=200,
            text="aetherra_requests_total 3\n   \n\t\n   # HELP ignored\n",
        ),
    )
    assert namespace["main"]() == 0
    output = capsys.readouterr().out
    assert "Total metrics: 1" in output
    assert "Found 1 aetherra_ metrics" in output
