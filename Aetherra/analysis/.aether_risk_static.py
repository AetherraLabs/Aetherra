# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Static risk analysis for .aether workflows.

- Scans .aether files for risky constructs (network ops, shell exec, file writes).
- No execution; provides a score and finding list.
- Intended for preflight checks in CI and before running untrusted workflows.
"""

from __future__ import annotations

# Standard library imports
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List

RISKY_PATTERNS = [
    (re.compile(r"\bexec\b|\beval\b", re.I), "dynamic-eval"),
    (re.compile(r"\bcurl\b|\bwget\b|\bhttp[s]?://", re.I), "network-call"),
    (re.compile(r"\bos\.system\(|subprocess\.", re.I), "shell-exec"),
    (re.compile(r"\bopen\(.*,'w'\)|\bwrite\(", re.I), "file-write"),
]


@dataclass
class RiskFinding:
    kind: str
    line: int
    snippet: str


def analyze_file(path: Path) -> List[RiskFinding]:
    findings: List[RiskFinding] = []
    text = path.read_text(encoding="utf-8", errors="ignore")
    for i, line in enumerate(text.splitlines(), start=1):
        for rx, kind in RISKY_PATTERNS:
            if rx.search(line):
                findings.append(RiskFinding(kind=kind, line=i, snippet=line.strip()[:200]))
    return findings


def risk_score(findings: List[RiskFinding]) -> int:
    weights = {"dynamic-eval": 5, "network-call": 2, "shell-exec": 4, "file-write": 2}
    return sum(weights.get(f.kind, 1) for f in findings)


def analyze_paths(paths: List[Path]) -> dict:
    all_findings = {}
    total = 0
    for p in paths:
        f = analyze_file(p)
        s = risk_score(f)
        all_findings[str(p)] = {"score": s, "findings": [f.__dict__ for f in f]}
        total += s
    return {"total_score": total, "files": all_findings}
