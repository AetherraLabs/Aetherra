#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Audit a dependency lock; missing or incomplete evidence fails closed."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

from packaging.requirements import InvalidRequirement, Requirement
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

SEVERITY_ORDER = ["low", "moderate", "medium", "high", "critical"]


class ScanError(Exception):
    """The scanner did not produce usable, complete evidence."""


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ScanError("scanner execution failed or timed out") from exc
    return result.returncode, result.stdout


def _decode(code: int, output: str):
    if code not in (0, 1):
        raise ScanError("scanner returned an unexpected exit code")
    try:
        return json.loads(output)
    except (ValueError, TypeError) as exc:
        raise ScanError("scanner returned invalid JSON") from exc


def _object(value) -> dict:
    if not isinstance(value, dict):
        raise ScanError("scanner returned an invalid record")
    return value


def _list(value) -> list:
    if not isinstance(value, list):
        raise ScanError("scanner returned an invalid collection")
    return value


def _text(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScanError("scanner omitted a required identifier")
    return value


def _exit_matches(code: int, findings: list[dict]) -> list[dict]:
    if (code == 1) != bool(findings):
        raise ScanError("scanner exit code contradicts its findings")
    return findings


def _read_exact_pins(lock_path: Path) -> dict[str, Version]:
    pins = {}
    try:
        for line in lock_path.read_text(encoding="utf-8").splitlines():
            line = line.partition("#")[0].strip()
            if not line:
                continue
            requirement = Requirement(line)
            specs = list(requirement.specifier)
            if (
                requirement.url
                or requirement.marker
                or requirement.extras
                or len(specs) != 1
            ):
                raise ScanError("exact scan requires plain version pins")
            spec = specs[0]
            if spec.operator != "==" or "*" in spec.version:
                raise ScanError("exact scan requires plain version pins")
            name = canonicalize_name(requirement.name)
            if name in pins:
                raise ScanError("exact scan rejects duplicate pins")
            pins[name] = Version(spec.version)
    except (OSError, UnicodeError, InvalidRequirement, InvalidVersion) as exc:
        raise ScanError("exact scan lock is unreadable or invalid") from exc
    if not pins:
        raise ScanError("exact scan requires at least one dependency")
    return pins


def pip_audit(lock_path: Path, *, exact_pins: bool = False) -> list[dict]:
    expected = _read_exact_pins(lock_path) if exact_pins else None
    executable = shutil.which("pip-audit")
    if not executable:
        return []
    command = [
        executable,
        "-r",
        str(lock_path),
        "-f",
        "json",
        "--strict",
        "--timeout",
        "30",
        "--progress-spinner",
        "off",
    ]
    if exact_pins:
        command.extend(["--no-deps", "--disable-pip"])
    code, output = run(command)
    data = _decode(code, output)
    dependencies = data.get("dependencies") if isinstance(data, dict) else data
    dependencies = _list(dependencies)
    if not dependencies:
        raise ScanError("scanner reported no audited dependencies")
    findings = []
    audited = {}
    for raw in dependencies:
        entry = _object(raw)
        if "skip_reason" in entry:
            raise ScanError("scanner skipped a dependency")
        name = _text(entry.get("name"))
        version = _text(entry.get("version"))
        if expected is not None:
            canonical_name = canonicalize_name(name)
            if canonical_name in audited:
                raise ScanError("scanner duplicated a dependency")
            try:
                audited[canonical_name] = Version(version)
            except InvalidVersion as exc:
                raise ScanError("scanner returned an invalid version") from exc
        for raw_finding in _list(entry.get("vulns")):
            finding = _object(raw_finding)
            severity = finding.get("severity") or "unknown"
            if not isinstance(severity, str):
                raise ScanError("scanner returned an invalid severity")
            fixes = _list(finding.get("fix_versions", []))
            for fix in fixes:
                _text(fix)
            findings.append(
                {
                    "name": name,
                    "version": version,
                    "id": _text(finding.get("id")),
                    "fix_versions": fixes,
                    "severity": severity.lower(),
                }
            )
    if expected is not None and audited != expected:
        raise ScanError("scanner dependency coverage does not match the lock")
    return _exit_matches(code, findings)


def osv_scan(lock_path: Path) -> list[dict]:
    executable = shutil.which("osv-scanner")
    if not executable:
        return []
    code, output = run(
        [
            executable,
            "--format",
            "json",
            "--requirements",
            str(lock_path),
        ]
    )
    data = _object(_decode(code, output))
    findings = []
    for raw_result in _list(data.get("results")):
        result = _object(raw_result)
        for raw_package in _list(result.get("packages")):
            package = _object(raw_package)
            name = _text(_object(package.get("package")).get("name"))
            for raw_finding in _list(package.get("vulnerabilities")):
                finding = _object(raw_finding)
                # OSV CVSS vectors do not establish a categorical severity here.
                findings.append(
                    {
                        "name": name,
                        "id": _text(finding.get("id")),
                        "severity": "unknown",
                    }
                )
    return _exit_matches(code, findings)


def worst_or_unknown(vulns: list[dict]) -> str:
    severities = [finding.get("severity", "unknown") for finding in vulns]
    if any(severity not in SEVERITY_ORDER for severity in severities):
        return "unknown"
    return max(severities, key=SEVERITY_ORDER.index, default="low")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", default="requirements.lock")
    parser.add_argument("--exact-pins", action="store_true")
    parser.add_argument(
        "--fail-level",
        choices=SEVERITY_ORDER,
        default=os.getenv("VULN_FAIL_LEVEL", "high"),
    )
    args = parser.parse_args()
    if args.fail_level not in SEVERITY_ORDER:
        print("[VULN][FAIL] invalid severity threshold")
        return 2
    lock_path = Path(args.lock)
    if not lock_path.is_file():
        print("[VULN][FAIL] lock file missing")
        return 2
    if not any(shutil.which(name) for name in ("pip-audit", "osv-scanner")):
        print("[VULN][FAIL] no vulnerability scanner available")
        return 2
    try:
        if args.exact_pins and not shutil.which("pip-audit"):
            raise ScanError("exact-pin scanning requires pip-audit")
        findings = pip_audit(lock_path, exact_pins=args.exact_pins) + osv_scan(
            lock_path
        )
    except ScanError as exc:
        print(f"[VULN][FAIL] {exc}")
        return 2
    if not findings:
        print("[VULN][OK] no vulnerabilities found")
        return 0
    for finding in findings:
        # JSON encoding prevents control characters in external identifiers.
        print("[VULN] " + json.dumps(finding, ensure_ascii=True))
    worst = worst_or_unknown(findings)
    if worst == "unknown":
        print("[VULN][FAIL] finding severity could not be confirmed")
        return 1
    if SEVERITY_ORDER.index(worst) >= SEVERITY_ORDER.index(args.fail_level):
        print(f"[VULN][FAIL] worst severity {worst} >= {args.fail_level}")
        return 1
    print(f"[VULN][OK] worst severity {worst} < {args.fail_level}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
