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
    "fallback": bool
  }
"""

from __future__ import annotations

import json
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

    # De-duplicate
    candidates = sorted(set(candidates))
    out = {
        "requested": requested,
        "candidates": candidates,
        "strategy": "heuristic-v1",
        "fallback": fallback,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
