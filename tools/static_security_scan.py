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

# Standard library imports
import ast
import json
import re
import sys
from contextlib import suppress
from dataclasses import asdict, dataclass
from pathlib import Path

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
    findings: list[Finding]
    summary: dict[str, int]

    def to_dict(self):  # pragma: no cover - trivial
        return {
            "findings": [asdict(f) for f in self.findings],
            "summary": self.summary,
        }


def load_allowlist(root: Path) -> list[re.Pattern]:
    allowlist_file = root / ".aetherra_scan_allowlist"
    patterns: list[re.Pattern] = []
    if allowlist_file.exists():
        for line in allowlist_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            with suppress(re.error):
                patterns.append(re.compile(line))
    return patterns


def is_allowed(line: str, allow_patterns: list[re.Pattern]) -> bool:
    return any(p.search(line) for p in allow_patterns)


def has_nosec(lines: list[str], line_number: int) -> bool:
    """Return True when the line or immediately preceding line has a nosec marker."""

    start = max(0, line_number - 2)
    end = min(len(lines), line_number + 1)
    return any("nosec" in lines[idx].lower() for idx in range(start, end))


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        parts = [node.func.attr]
        current = node.func.value
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))
    return ""


def _is_subprocess_shell_true(node: ast.Call) -> bool:
    call_name = _call_name(node)
    if not call_name.startswith("subprocess."):
        return False
    return any(
        keyword.arg == "shell"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value is True
        for keyword in node.keywords
    )


def scan_unsafe_calls(path: Path, text: str, lines: list[str]) -> list[Finding]:
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        line_number = getattr(node, "lineno", 0)
        if line_number <= 0 or has_nosec(lines, line_number):
            continue

        pattern = ""
        call_name = _call_name(node)
        if call_name == "eval":
            pattern = "eval_call"
        elif call_name == "exec":
            pattern = "exec_call"
        elif _is_subprocess_shell_true(node):
            pattern = "subprocess_shell_true"

        if not pattern:
            continue
        findings.append(
            Finding(
                file=str(path),
                line=line_number,
                severity="high",
                category="unsafe_call",
                pattern=pattern,
                excerpt=lines[line_number - 1].strip()[:180],
            )
        )
    return findings


def scan_file(path: Path, allow_patterns: list[re.Pattern]) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings: list[Finding] = []
    lines = text.splitlines()
    findings.extend(scan_unsafe_calls(path, text, lines))

    # Secrets
    for idx, line in enumerate(lines, start=1):
        if is_allowed(line, allow_patterns):
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(line):
                severity = "critical"
                if name == "password_assignment":
                    lowered = line.lower()
                    # Skip obvious redaction mappings and scanner keyword lists.
                    if any(
                        ph in lowered
                        for ph in [
                            "[redacted]",
                            "for keyword in",
                        ]
                    ):
                        continue
                    # Downgrade if obviously a placeholder.
                    if any(
                        ph in lowered
                        for ph in [
                            "changeme",
                            "example",
                            "placeholder",
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
    findings: list[Finding] = []
    for path in root.rglob("*.py"):
        # Skip virtual envs or build dirs
        if any(part in {".venv", "venv", "build", "dist"} for part in path.parts):
            continue
        findings.extend(scan_file(path, allow_patterns))

    summary: dict[str, int] = {}
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
    # Standard library imports
    import argparse

    parser = argparse.ArgumentParser(description="Static security scanner")
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", default="security_scan_report.json")
    parser.add_argument("--md", default="security_scan_report.md")
    args = parser.parse_args()

    # Windows consoles may use a legacy code page. Replace unsupported status
    # glyphs instead of failing after the scan and reports have completed.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")

    root = Path(args.root).resolve()
    report = scan_root(root)
    write_reports(report, Path(args.json), Path(args.md))
    # Critical exit if any critical secret findings
    critical = any(f.severity == "critical" for f in report.findings)
    if critical:
        print("Critical security findings detected")
        sys.exit(1)
    print("Security scan completed with no critical findings")


if __name__ == "__main__":
    main()
