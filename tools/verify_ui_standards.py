#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Verify UI standards for Lyrixa/Aetherra.

This lightweight checker scans a directory for UI-related Python files and reports:
- PySide6 usage (flags PySide2/QtWebKit as violations)
- Presence of hard-coded blocking calls in UI code (basic heuristics)
- Large modules (>1500 LOC) that may need splitting

Exit code is 0 even on findings to remain CI-friendly unless --strict is set.
"""

from __future__ import annotations

# Standard library imports
import argparse
import pathlib
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class Finding:
    file: pathlib.Path
    line: int
    level: str  # INFO|WARN|ERROR
    message: str


def scan_file(path: pathlib.Path) -> List[Finding]:
    findings: List[Finding] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        return [Finding(path, 0, "ERROR", f"Cannot read file: {e}")]

    # Heuristics
    for i, line in enumerate(text, start=1):
        s = line.strip()
        if "PySide2" in s or "from PySide2" in s:
            findings.append(
                Finding(path, i, "ERROR", "PySide2 import found; use PySide6")
            )
        if "QtWebKit" in s:
            findings.append(
                Finding(path, i, "ERROR", "Deprecated QtWebKit usage detected")
            )
        if "time.sleep(" in s:
            findings.append(Finding(path, i, "WARN", "Blocking time.sleep in UI code"))
        if "requests.get(" in s and "QThread" not in "\n".join(
            text[max(0, i - 10) : i + 10]
        ):
            findings.append(
                Finding(
                    path, i, "WARN", "Potential blocking network request in UI thread"
                )
            )

    # Module size warning
    if len(text) > 1500:
        findings.append(
            Finding(
                path, 0, "WARN", f"Large module ({len(text)} LOC); consider refactor"
            )
        )

    return findings


def write_report(
    output: pathlib.Path,
    root: pathlib.Path,
    scanned: List[pathlib.Path],
    findings: List[Finding],
) -> None:
    lines: List[str] = []
    lines.append("# UI Standards Report")
    lines.append("")
    lines.append(f"Scanned directory: `{root}`")
    lines.append(f"Files scanned: {len(scanned)}")
    lines.append(f"Findings: {len(findings)}")
    lines.append("")

    if findings:
        lines.append("## Findings")
        for f in findings:
            rel = f.file.as_posix()
            lines.append(f"- [{f.level}] {rel}:{f.line} — {f.message}")
        lines.append("")
    else:
        lines.append("No issues detected by heuristic checks.")

    output.write_text("\n".join(lines), encoding="utf-8")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory to scan")
    parser.add_argument("--output", required=True, help="Markdown report output path")
    parser.add_argument("--strict", action="store_true", help="Fail on ERROR findings")
    args = parser.parse_args(argv)

    root = pathlib.Path(args.dir)
    out = pathlib.Path(args.output)

    # Ensure output parent exists
    out.parent.mkdir(parents=True, exist_ok=True)

    # Resolve a sensible default directory if requested root is missing
    if not root.exists():
        candidates = [
            pathlib.Path("Aetherra/lyrixa/gui"),
            pathlib.Path("Aetherra/lyrixa"),
        ]
        chosen = None
        for c in candidates:
            if c.exists():
                chosen = c
                break
        if chosen is None:
            # Write a stub report and succeed
            out.write_text(
                f"# UI Standards Report\n\nDirectory `{root}` not found. No files scanned.\n",
                encoding="utf-8",
            )
            print(f"[INFO] Directory not found: {root}. Wrote stub report to {out}")
            return 0
        else:
            print(f"[INFO] Directory `{root}` not found. Scanning fallback: `{chosen}`")
            root = chosen

    scanned: List[pathlib.Path] = []
    findings: List[Finding] = []

    for p in root.rglob("*.py"):
        scanned.append(p)
        findings.extend(scan_file(p))

    write_report(out, root, scanned, findings)
    errors = [f for f in findings if f.level == "ERROR"]

    print(f"[OK] UI standards report written to: {out}")
    print(
        f"[SUMMARY] Files: {len(scanned)} | Findings: {len(findings)} | Errors: {len(errors)}"
    )

    if args.strict and errors:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
