"""Static Security Scan Tool

Scans the repository for:
  1. Potential secrets (API keys, tokens, private keys, passwords)
  2. Unsafe dynamic code execution patterns (eval/exec, subprocess shell=True)
  3. Disallowed imports (e.g., wildcard imports) that reduce auditability

Outputs a JSON report plus an optional markdown summary. Exit codes:
  0 = no critical findings
  1 = critical findings present

This lightweight scanner is intentionally conservative (low false negatives) while
attempting to keep false positives manageable. Allowlisting via patterns is supported
through an optional .aetherra_scan_allowlist file (one regex per line, # comments ok).

License: GPL-3.0-or-later
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

SECRET_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic_api_key": re.compile(
        r"api[_-]?key['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]", re.I
    ),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9\._\-]{20,}"),
    "private_key_header": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    # password= assignments are noisy; treat separately so we can downgrade common placeholders
    "password_assignment": re.compile(r"password\s*[:=]\s*['\"][^'\"]+['\"]", re.I),
}

UNSAFE_PATTERNS = {
    "eval_call": re.compile(r"(^|[^A-Za-z0-9_])eval\s*\(", re.M),
    "exec_call": re.compile(r"(^|[^A-Za-z0-9_])exec\s*\(", re.M),
    "subprocess_shell_true": re.compile(r"subprocess\.\w+\(.*shell\s*=\s*True", re.S),
}

DISALLOWED_IMPORTS = {
    "wildcard_import": re.compile(r"from\s+\S+\s+import\s+\*"),
}


@dataclass
class Finding:
    file: str
    line: int
    severity: str
    category: str
    pattern: str
    excerpt: str


@dataclass
class ScanReport:
    findings: List[Finding]
    summary: Dict[str, int]

    def to_dict(self):  # pragma: no cover - trivial
        return {
            "findings": [asdict(f) for f in self.findings],
            "summary": self.summary,
        }


def load_allowlist(root: Path) -> List[re.Pattern]:
    allowlist_file = root / ".aetherra_scan_allowlist"
    patterns: List[re.Pattern] = []
    if allowlist_file.exists():
        for line in allowlist_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                patterns.append(re.compile(line))
            except re.error:
                pass
    return patterns


def is_allowed(line: str, allow_patterns: List[re.Pattern]) -> bool:
    return any(p.search(line) for p in allow_patterns)


def scan_file(path: Path, allow_patterns: List[re.Pattern]) -> List[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings: List[Finding] = []
    lines = text.splitlines()
    # Secrets
    for idx, line in enumerate(lines, start=1):
        if is_allowed(line, allow_patterns):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                severity = "critical"
                if name == "password_assignment":
                    lowered = line.lower()
                    # Downgrade if obviously a placeholder or redacted / mapping spec line
                    if any(
                        ph in lowered
                        for ph in [
                            "[redacted]",
                            "changeme",
                            "example",
                            "placeholder",
                            "for keyword in",
                        ]
                    ):
                        severity = "medium"
                findings.append(
                    Finding(
                        file=str(path),
                        line=idx,
                        severity=severity,
                        category="secret",
                        pattern=name,
                        excerpt=line.strip()[:180],
                    )
                )
        for name, pattern in UNSAFE_PATTERNS.items():
            if pattern.search(line):
                findings.append(
                    Finding(
                        file=str(path),
                        line=idx,
                        severity="high",
                        category="unsafe_call",
                        pattern=name,
                        excerpt=line.strip()[:180],
                    )
                )
        for name, pattern in DISALLOWED_IMPORTS.items():
            if pattern.search(line):
                findings.append(
                    Finding(
                        file=str(path),
                        line=idx,
                        severity="medium",
                        category="import_style",
                        pattern=name,
                        excerpt=line.strip()[:180],
                    )
                )
    return findings


def scan_root(root: Path) -> ScanReport:
    allow_patterns = load_allowlist(root)
    findings: List[Finding] = []
    for path in root.rglob("*.py"):
        # Skip virtual envs or build dirs
        if any(part in {".venv", "venv", "build", "dist"} for part in path.parts):
            continue
        findings.extend(scan_file(path, allow_patterns))

    summary: Dict[str, int] = {}
    for f in findings:
        summary[f.category] = summary.get(f.category, 0) + 1
    summary["total"] = len(findings)
    return ScanReport(findings=findings, summary=summary)


def write_reports(report: ScanReport, json_path: Path, md_path: Path | None = None):
    json_path.write_text(json.dumps(report.to_dict(), indent=2))
    if md_path:
        lines = ["# Static Security Scan Report", ""]
        lines.append(f"Total Findings: {report.summary.get('total', 0)}")
        lines.append("")
        if report.findings:
            lines.append("| Severity | Category | File | Line | Pattern | Excerpt |")
            lines.append("|----------|----------|------|------|---------|---------|")
            for f in report.findings[:200]:  # cap table size
                lines.append(
                    f"| {f.severity} | {f.category} | {Path(f.file).name} | {f.line} | {f.pattern} | {f.excerpt.replace('|', ' ')} |"
                )
        else:
            lines.append("No findings detected.")
        md_path.write_text("\n".join(lines))


def main():  # pragma: no cover - CLI wrapper
    import argparse

    parser = argparse.ArgumentParser(description="Static security scanner")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", default="security_scan_report.json")
    parser.add_argument("--md", default="security_scan_report.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    report = scan_root(root)
    write_reports(report, Path(args.json), Path(args.md))
    # Critical exit if any critical secret findings
    critical = any(f.severity == "critical" for f in report.findings)
    if critical:
        print("❌ Critical security findings detected")
        sys.exit(1)
    print("✅ Security scan completed with no critical findings")


if __name__ == "__main__":
    main()
