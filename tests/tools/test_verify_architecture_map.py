"""Architecture policy evidence must use the active, isolated Security API."""

import functools
import http.client
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools import verify_architecture_map as verifier


@pytest.mark.parametrize(
    ("status", "transport_error"), [(200, False), (302, False), (500, False), (0, True)]
)
def test_hub_probe_uses_direct_local_http_and_closes_connections(
    monkeypatch, status, transport_error
):
    server = SimpleNamespace(start_server=lambda: True, stop_server=Mock())
    monkeypatch.setitem(
        sys.modules,
        "aetherra_hub.compat",
        SimpleNamespace(AetherraHubServer=lambda port: server),
    )
    monkeypatch.setattr(verifier.time, "sleep", lambda delay: None)
    connections = []

    def connect(host, port, timeout):
        response = SimpleNamespace(
            status=status,
            getheader=lambda name, default: "application/json",
            read=lambda: b"{}",
        )
        connection = SimpleNamespace(
            request=Mock(
                side_effect=OSError("PRIVATE_HTTP_DETAIL") if transport_error else None
            ),
            getresponse=lambda: response,
            close=Mock(),
        )
        connections.append((host, port, timeout, connection))
        return connection

    def forbidden_url_open(*args, **kwargs):
        pytest.fail("Generic URL open must not follow redirects or use proxy schemes")

    monkeypatch.setattr(http.client, "HTTPConnection", connect)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden_url_open)
    result = verifier.check_hub_minimal_api_probe(port=31415, timeout=0.25)
    assert result["ok"] is (status == 200)
    assert "PRIVATE_HTTP_DETAIL" not in json.dumps(result)
    assert result["details"] == {"health": status, "plugins": status, "metrics": status}
    assert len(connections) == 3
    paths = ["/health", "/api/plugins", "/metrics"]
    for (host, port, timeout, connection), path in zip(connections, paths, strict=True):
        assert (host, port, timeout) == ("localhost", 31415, 0.25)
        connection.request.assert_called_once_with("GET", path)
        connection.close.assert_called_once_with()
    server.stop_server.assert_called_once_with()


def test_standalone_tool_resolves_repository_packages(tmp_path):
    script = """
import json, runpy, sys
module = runpy.run_path(sys.argv[1], run_name="architecture_cli_test")
print(json.dumps(module["_try_import"]("Aetherra.security.capabilities")))
"""
    env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in {"PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP"}
    }
    result = subprocess.run(
        [sys.executable, "-I", "-c", script, str(Path(verifier.__file__).resolve())],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout) == [True, None]


@pytest.fixture
def isolated_probe(tmp_path, monkeypatch):
    monkeypatch.setattr(
        tempfile,
        "TemporaryDirectory",
        functools.partial(tempfile.TemporaryDirectory, dir=tmp_path),
    )
    return tmp_path


def test_current_policy_probe_is_isolated(isolated_probe):
    before = dict(os.environ)
    result = verifier.check_capability_policies_and_deny_defaults()
    assert result["ok"] is True
    assert result["matrix"]["strict_dev"]["allowed"] is True
    assert result["matrix"]["strict_dev"]["ungranted"] is False
    assert result["matrix"]["strict_dev"]["unknown_principal"] is False
    assert result["matrix"]["missing_policy"]["allowed"] is False
    assert result["matrix"]["malformed_policy"]["allowed"] is False
    assert dict(os.environ) == before
    assert list(isolated_probe.iterdir()) == []


@pytest.mark.parametrize(
    "failure", ["allow_unknown", "allow_ungranted", "deny_granted"]
)
def test_incorrect_policy_behavior_fails(isolated_probe, monkeypatch, failure):
    data = {
        "allowed": failure != "deny_granted",
        "ungranted": failure == "allow_ungranted",
        "unknown_principal": failure == "allow_unknown",
    }
    monkeypatch.setattr(
        subprocess,
        "run",
        Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(data), "")),
    )
    assert verifier.check_capability_policies_and_deny_defaults()["ok"] is False


@pytest.mark.parametrize(
    "response",
    [
        subprocess.CompletedProcess([], 2, "", "PRIVATE_FAILURE"),
        subprocess.CompletedProcess([], 0, "INVALID_PRIVATE_OUTPUT", ""),
    ],
)
def test_unusable_evidence_is_sanitized(isolated_probe, monkeypatch, response):
    monkeypatch.setattr(subprocess, "run", Mock(return_value=response))
    result = verifier.check_capability_policies_and_deny_defaults()
    assert result["ok"] is False
    assert "PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize(
    "error",
    [
        subprocess.TimeoutExpired("probe", 15),
        OSError("PRIVATE_FAILURE"),
        UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid output"),
    ],
)
def test_probe_execution_error_is_failure(isolated_probe, monkeypatch, error):
    monkeypatch.setattr(subprocess, "run", Mock(side_effect=error))
    result = verifier.check_capability_policies_and_deny_defaults()
    assert result["ok"] is False
    assert list(isolated_probe.iterdir()) == []


def test_probe_does_not_borrow_credentials_or_unsafe_flags(isolated_probe, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "1")
    execute = subprocess.run
    calls = []

    def record(command, **kwargs):
        calls.append(kwargs)
        return execute(command, **kwargs)

    monkeypatch.setattr(subprocess, "run", record)
    assert verifier.check_capability_policies_and_deny_defaults()["ok"] is True
    assert len(calls) == 5
    for call in calls:
        assert "OPENAI_API_KEY" not in call["env"]
        assert call["env"]["AETHERRA_PROD_UNSAFE_ALLOW"] == "0"
        assert call["timeout"] == 15
    assert os.environ["AETHERRA_PROD_UNSAFE_ALLOW"] == "1"
