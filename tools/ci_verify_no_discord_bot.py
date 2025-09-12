#!/usr/bin/env python3
"""CI Verification: ensure internal Discord bot artifacts are not present.

Stricter wrapper around guard_discord_exclusion:
- Fails if 'Discord Bot/' dir exists (unless AETHERRA_ALLOW_DISCORD=1)
- Fails if any file containing 'discord.py' import appears outside excluded paths
- Ensures MANIFEST.in prune line present

Exit codes:
 0 OK
 1 Violations
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
violations: list[str] = []
allow = os.getenv("AETHERRA_ALLOW_DISCORD") == "1"

DISCORD_DIR = ROOT / "Discord Bot"
if DISCORD_DIR.exists() and not allow:
    violations.append(
        "'Discord Bot/' directory present (set AETHERRA_ALLOW_DISCORD=1 to permit in private builds)"
    )

manifest = ROOT / "MANIFEST.in"
if manifest.exists():
    txt = manifest.read_text(encoding="utf-8", errors="ignore")
    if "prune Discord Bot" not in txt:
        violations.append("MANIFEST.in missing 'prune Discord Bot'")
else:
    violations.append("MANIFEST.in missing (required for pruning Discord Bot)")

# Scan imports
pattern = re.compile(r"\bimport\s+discord|from\s+discord\s+import")
for py in ROOT.rglob("*.py"):
    if "Discord Bot" in py.parts:
        continue
    try:
        text = py.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if pattern.search(text):
        violations.append(f"discord import detected in {py}")
        if len(violations) > 25:
            break

if violations:
    print("[ci-discord] FAIL:")
    for v in violations:
        print(" -", v)
    sys.exit(1)
print("[ci-discord] OK (no discord artifacts)")
