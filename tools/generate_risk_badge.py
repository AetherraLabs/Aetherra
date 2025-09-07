#!/usr/bin/env python3
"""Generate Shields.io endpoint JSON for total .aether static risk score.

Writes badge/aether_risk.json with schemaVersion=1 consumed by
https://img.shields.io/endpoint?url=... raw GitHub URL.

Color rules:
  score == 0        -> brightgreen
  1 <= score <= 2   -> yellow
  else              -> red

Exits 0 always (badge generation shouldn't fail CI), but prints score.
"""

from __future__ import annotations

import json
from pathlib import Path

from Aetherra.analysis.static_risk import analyze_paths  # type: ignore

IGNORE_DIRS = {".git", "dist", "build", "venv", ".venv", "__pycache__"}


def collect_aether(root: Path):
    return [
        p
        for p in root.rglob("*.aether")
        if p.is_file() and not any(part in IGNORE_DIRS for part in p.parts)
    ]


def main() -> int:
    root = Path.cwd()
    files = collect_aether(root)
    result = analyze_paths(files) if files else {"total_score": 0}
    score = int(result.get("total_score", 0))
    if score == 0:
        color = "brightgreen"
    elif score <= 2:
        color = "yellow"
    else:
        color = "red"
    badge = {
        "schemaVersion": 1,
        "label": "aether risk",
        "message": str(score),
        "color": color,
    }
    out_dir = root / "badge"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "aether_risk.json"
    existing = out_file.read_text(encoding="utf-8") if out_file.exists() else ""
    new = json.dumps(badge, separators=(",", ":")) + "\n"
    if existing != new:
        out_file.write_text(new, encoding="utf-8")
        print(f"Updated badge file: score={score}")
    else:
        print(f"Badge unchanged: score={score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
