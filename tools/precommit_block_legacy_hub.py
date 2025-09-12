#!/usr/bin/env python3
"""Pre-commit hook: block new imports of deprecated aetherra_hub_server.
Allows override via env LEGACY_HUB_IMPORT_ALLOW=1.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ALLOW = os.getenv("LEGACY_HUB_IMPORT_ALLOW", "0") == "1"
if ALLOW:
    sys.exit(0)

bad: list[str] = []
for path in Path(".").rglob("*.py"):
    if path.name == "aetherra_hub_server.py":
        continue  # shim itself allowed
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if "import aetherra_hub_server" in text or "from aetherra_hub_server" in text:
        bad.append(str(path))

if bad:
    print("[HOOK] Blocked commit: deprecated aetherra_hub_server import(s) found:")
    for b in bad[:20]:
        print(f"  - {b}")
    print(
        '\nFix: replace with "from aetherra_hub import compat" or module invocation (python -m aetherra_hub.compat).'
    )
    print("Override (not recommended): set LEGACY_HUB_IMPORT_ALLOW=1")
    sys.exit(1)

sys.exit(0)
