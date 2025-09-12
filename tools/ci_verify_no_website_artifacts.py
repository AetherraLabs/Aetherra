#!/usr/bin/env python3
"""CI Guard: Prevent accidental website build artifacts from being committed.

Violations (unless AETHERRA_ALLOW_WEBSITE=1):
 - Directory 'aetherra-website/' present at repo root (should live in separate repo)
 - Build output directories (dist/, build/, site/) containing typical web assets (.html, .js, .css, assets/) with > threshold files
 - Presence of top-level index.html not under package paths

Exit codes:
 0 OK
 1 Violations detected
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
allow = os.getenv("AETHERRA_ALLOW_WEBSITE") == "1"
violations: list[str] = []

WEBSITE_DIR = ROOT / "aetherra-website"
if WEBSITE_DIR.exists() and not allow:
    violations.append(
        "'aetherra-website/' directory present (set AETHERRA_ALLOW_WEBSITE=1 to permit during deploy workflows)"
    )

BUILD_DIRS = ["dist", "build", "site"]
WEB_EXT = {".html", ".js", ".css", ".map"}
for d in BUILD_DIRS:
    p = ROOT / d
    if not p.is_dir():
        continue
    # Count web files
    count = 0
    for f in p.rglob("*"):
        if f.is_file() and f.suffix.lower() in WEB_EXT:
            count += 1
            if count > 25:  # threshold
                break
    if count > 25 and not allow:
        violations.append(
            f"Build directory '{d}/' contains >25 web assets (count={count})"
        )

# Top-level index.html guard
root_index = ROOT / "index.html"
if root_index.exists() and not allow:
    violations.append("Top-level index.html present (likely website artifact)")

if violations:
    print("[ci-website] FAIL:")
    for v in violations:
        print(" -", v)
    sys.exit(1)
print("[ci-website] OK (no website build artifacts)")
