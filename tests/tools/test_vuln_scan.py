"""Security scanning must distinguish clean evidence from missing evidence."""

import json
import subprocess
import sys
from unittest.mock import Mock

import pytest

from tools import vuln_scan


def test_exact_pins_disable_resolution(tmp_path, monkeypatch):
    lock = tmp_path / "requirements.lock"
    lock.write_text("example==1.0\n", encoding="utf-8")
    execute = Mock(return_value=(0, '[{"name":"example","version":"1.0","vulns":[]}]'))
    monkeypatch.setattr(
        vuln_scan.shutil, "which", lambda name: name if name == "pip-audit" else None
    )
    monkeypatch.setattr(vuln_scan, "run", execute)
    monkeypatch.setattr(sys, "argv", ["vuln_scan", "--lock", str(lock), "--exact-pins"])
    assert vuln_scan.main() == 0
    command = execute.call_args.args[0]
    assert "--no-deps" in command
    assert "--disable-pip" in command


@pytest.mark.parametrize(
    "requirement",
    [
        "example>=1.0",
        "example==1.*",
        "example @ https://example.com/package.whl",
        "example==1.0; python_version >= '3.11'",
        "-r other.txt",
        "example==1.0\nexample==2.0",
        "# empty",
    ],
)
def test_exact_pins_reject_incomplete_locks(tmp_path, monkeypatch, requirement):
    lock = tmp_path / "requirements.lock"
    lock.write_text(requirement, encoding="utf-8")
    execute = Mock()
    monkeypatch.setattr(
        vuln_scan.shutil, "which", lambda name: name if name == "pip-audit" else None
    )
    monkeypatch.setattr(vuln_scan, "run", execute)
    monkeypatch.setattr(sys, "argv", ["vuln_scan", "--lock", str(lock), "--exact-pins"])
    assert vuln_scan.main() == 2
    execute.assert_not_called()


@pytest.mark.parametrize(
    "dependencies",
    [
        [{"name": "other", "version": "1.0", "vulns": []}],
        [{"name": "example", "version": "2.0", "vulns": []}],
    ],
)
def test_exact_scan_must_match_lock(tmp_path, monkeypatch, dependencies):
    lock = tmp_path / "requirements.lock"
    lock.write_text("example==1.0\n", encoding="utf-8")
    monkeypatch.setattr(
        vuln_scan.shutil, "which", lambda name: name if name == "pip-audit" else None
    )
    monkeypatch.setattr(
        vuln_scan, "run", Mock(return_value=(0, json.dumps(dependencies)))
    )
    monkeypatch.setattr(sys, "argv", ["vuln_scan", "--lock", str(lock), "--exact-pins"])
    assert vuln_scan.main() == 2


@pytest.fixture
def invoke(tmp_path, monkeypatch):
    lock = tmp_path / "requirements.lock"
    lock.write_text("example==1.0\n", encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["vuln_scan", "--lock", str(lock)])

    def call(payload, code=0, scanner="pip-audit"):
        monkeypatch.setattr(
            vuln_scan.shutil, "which", lambda name: name if name == scanner else None
        )
        monkeypatch.setattr(vuln_scan, "run", lambda command: (code, payload))
        return vuln_scan.main()

    return call


def test_missing_scanners_fail(invoke):
    assert invoke("", scanner=None) == 2


@pytest.mark.parametrize("payload", ["[]", '{"dependencies": []}'])
def test_empty_dependency_evidence_fails(invoke, payload):
    assert invoke(payload) == 2


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        "{}",
        "null",
        '{"dependencies": {}}',
        '[{"name":"example","skip_reason":"unresolved"}]',
    ],
)
def test_invalid_or_incomplete_scan_fails(invoke, payload):
    assert invoke(payload) == 2


@pytest.mark.parametrize("current", [False, True])
def test_valid_clean_pip_audit_formats(invoke, current):
    dependencies = [{"name": "example", "version": "1.0", "vulns": []}]
    payload = {"dependencies": dependencies, "fixes": []} if current else dependencies
    assert invoke(json.dumps(payload)) == 0


@pytest.mark.parametrize("severity", [None, "unknown", "CVSS_V3", "high", "critical"])
def test_unconfirmed_or_high_findings_block(invoke, severity):
    finding = {"id": "TEST-1", "fix_versions": ["2.0"], "severity": severity}
    payload = {
        "dependencies": [{"name": "example", "version": "1.0", "vulns": [finding]}]
    }
    assert invoke(json.dumps(payload), code=1) == 1


def test_confirmed_low_finding_respects_threshold(invoke):
    payload = [
        {
            "name": "example",
            "version": "1.0",
            "vulns": [{"id": "TEST-1", "severity": "low", "fix_versions": []}],
        }
    ]
    assert invoke(json.dumps(payload), code=1) == 0


@pytest.mark.parametrize("code", [1, 2, 127])
def test_unsuccessful_clean_response_fails(invoke, code):
    assert invoke('[{"name":"example","version":"1.0","vulns":[]}]', code=code) == 2


def test_invalid_output_is_not_exposed(invoke, capsys):
    assert invoke("PRIVATE_SCANNER_OUTPUT") == 2
    assert "PRIVATE_SCANNER_OUTPUT" not in capsys.readouterr().out


def test_malformed_osv_fails(invoke):
    assert invoke("{}", scanner="osv-scanner") == 2


def test_clean_osv(invoke):
    assert invoke('{"results":[]}', scanner="osv-scanner") == 0


@pytest.mark.parametrize(
    "error", [OSError("private detail"), subprocess.TimeoutExpired("scanner", 300)]
)
def test_execution_failure_is_sanitized(monkeypatch, error):
    monkeypatch.setattr(vuln_scan.subprocess, "run", Mock(side_effect=error))
    with pytest.raises(
        vuln_scan.ScanError, match="scanner execution failed or timed out"
    ):
        vuln_scan.run(["scanner"])


def test_stdout_is_separate_and_execution_is_bounded(monkeypatch):
    execute = Mock(
        return_value=subprocess.CompletedProcess(["scanner"], 0, "{}", "notice")
    )
    monkeypatch.setattr(vuln_scan.subprocess, "run", execute)
    assert vuln_scan.run(["scanner"]) == (0, "{}")
    assert execute.call_args.kwargs["timeout"] == 300
    assert execute.call_args.kwargs["capture_output"] is True


def test_osv_vector_does_not_become_low_risk(invoke):
    payload = {
        "results": [
            {
                "packages": [
                    {
                        "package": {"name": "example"},
                        "vulnerabilities": [
                            {
                                "id": "TEST-1",
                                "severity": [
                                    {"type": "CVSS_V3", "score": "CVSS:3.1/AV:N"}
                                ],
                            }
                        ],
                    }
                ]
            }
        ]
    }
    assert invoke(json.dumps(payload), code=1, scanner="osv-scanner") == 1


def test_finding_with_success_exit_is_invalid(invoke):
    payload = [
        {
            "name": "example",
            "version": "1.0",
            "vulns": [{"id": "TEST-1", "severity": "low"}],
        }
    ]
    assert invoke(json.dumps(payload)) == 2
