#!/usr/bin/env python3
"""Test Selection Stub

Phase 1 placeholder: produces a candidate test list given a set of touched paths.
Usage:
  python tools/test_selection_stub.py path1 path2 ...

Heuristic:
  - If no args, prints default suite (capabilities + tests/ if present)
  - If any path is under tests/, returns that test directly
  - If source file touched, maps to tests with similar stem name

Outputs JSON structure:
    {
        "requested": [...],
        "candidates": [...],
        "strategy": "heuristic-v1",
        "fallback": bool,
        "confidence": 0.0-1.0,
        "reason": "short explanation"
    }
"""

from __future__ import annotations

# Standard library imports
import json
import os
import sys
from pathlib import Path


def find_tests_for(stem: str) -> list[str]:
    matches: list[str] = []
    for p in Path("tests").rglob(f"*{stem}*test*.py"):
        matches.append(str(p))
    return matches


def main(argv: list[str]) -> int:
    requested = argv[1:]
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print(
            json.dumps(
                {
                    "requested": requested,
                    "candidates": [],
                    "strategy": "heuristic-v1",
                    "fallback": True,
                    "confidence": 0.0,
                    "reason": "tests directory missing",
                }
            )
        )
        return 0

    candidates: list[str] = []
    # Directly include provided test paths
    for r in requested:
        rp = Path(r)
        if rp.is_file() and "tests" in rp.parts and rp.suffix == ".py":
            candidates.append(str(rp))

    # Heuristic mapping for source files
    for r in requested:
        rp = Path(r)
        if rp.is_file() and "tests" not in rp.parts and rp.suffix == ".py":
            stem = rp.stem
            mapped = find_tests_for(stem)
            candidates.extend(mapped)

    # Fallback if nothing selected: basic capabilities suite
    fallback = False
    if not candidates:
        fallback = True
        base = Path("tests/capabilities")
        if base.exists():
            candidates = [str(p) for p in base.rglob("test_*.py")]
        else:
            candidates = [str(p) for p in tests_dir.rglob("test_*.py")]

    # Confidence heuristic:
    # High (0.9) if we mapped each non-test source file to at least one test.
    # Medium (0.6) if we have candidates but some requested sources produced none.
    # Low (0.3) if fallback triggered.
    # Very low (0.0) if no tests dir (handled earlier) or empty (should not reach here).
    mapped_source_files = [
        r for r in requested if r.endswith(".py") and "tests" not in r.split(os.sep)
    ]
    mapped_counts = 0
    for r in mapped_source_files:
        stem = Path(r).stem
        if any(stem in Path(c).stem for c in candidates):
            mapped_counts += 1
    if fallback:
        confidence = 0.3 if candidates else 0.0
        reason = "fallback suite used"
    else:
        if mapped_source_files:
            ratio = mapped_counts / max(1, len(mapped_source_files))
            if ratio >= 1.0:
                confidence = 0.9
                reason = "all touched sources mapped to tests"
            elif ratio >= 0.5:
                confidence = 0.6
                reason = "partial source→test mapping"
            else:
                confidence = 0.4
                reason = "low source→test mapping"
        else:
            confidence = 0.5
            reason = "only test paths provided"

    # De-duplicate
    candidates = sorted(set(candidates))
    out = {
        "requested": requested,
        "candidates": candidates,
        "strategy": "heuristic-v1",
        "fallback": fallback,
        "confidence": round(confidence, 2),
        "reason": reason,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
