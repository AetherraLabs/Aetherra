"""Analysis Interfaces (Phase 0 stub)

Future responsibilities:
  - Impact analysis (blast radius of changes)
  - Test selection (subset tests based on touched code)
  - Risk scoring for autonomy decisions

Current: placeholder functions returning defaults.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ImpactReport:
    touched_files: list[Path]
    suggested_tests: list[str]
    risk_level: str  # low|medium|high


def analyze_patch(diff_text: str) -> ImpactReport:
    touched: list[Path] = []
    for line in diff_text.splitlines():
        if line.startswith("*** Update File:") or line.startswith("*** Add File:"):
            p = Path(line.split(":", 1)[1].strip())
            touched.append(p)
    # Very naive heuristics: more than 5 files -> medium risk
    risk = "low"
    if len(touched) > 5:
        risk = "medium"
    if len(touched) > 12:
        risk = "high"
    suggested_tests = ["pytest -q -k smoke"] if touched else []
    return ImpactReport(
        touched_files=touched, suggested_tests=suggested_tests, risk_level=risk
    )
