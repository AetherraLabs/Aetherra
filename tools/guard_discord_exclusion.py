"""CI/packaging guard to ensure the internal Discord Bot directory is excluded.

Checks:
1. Directory named 'Discord Bot' must not be present in source tree for public builds (allowed if AETHERRA_ALLOW_DISCORD=1 explicitly set).
2. MANIFEST.in must contain a prune directive for 'Discord Bot'.
3. requirements.txt must not unconditionally include discord.py for prod builds unless AETHERRA_ALLOW_DISCORD=1.

Exit codes:
 0: All good
 1: Violation(s) found
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
violations: list[str] = []
allow_discord = os.environ.get("AETHERRA_ALLOW_DISCORD") == "1"


def check_directory():
    discord_dir = ROOT / "Discord Bot"
    if discord_dir.exists() and not allow_discord:
        violations.append(
            "Discord Bot directory present but AETHERRA_ALLOW_DISCORD not set."
        )


def check_manifest():
    manifest = ROOT / "MANIFEST.in"
    if not manifest.exists():
        return
    text = manifest.read_text(encoding="utf-8", errors="ignore")
    if "prune Discord Bot" not in text:
        violations.append("MANIFEST.in missing 'prune Discord Bot' directive.")


def check_requirements():
    req = ROOT / "requirements.txt"
    if not req.exists():
        return
    text = req.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line in text:
        if "discord.py" in line and not allow_discord:
            # Permit if line is commented
            if line.strip().startswith("#"):
                continue
            violations.append(
                "discord.py dependency present for public build (set AETHERRA_ALLOW_DISCORD=1 to allow)."
            )
            break


def main() -> int:
    check_directory()
    check_manifest()
    check_requirements()
    if violations:
        print("[discord-guard] FAIL:")
        for v in violations:
            print(f" - {v}")
        return 1
    print("[discord-guard] OK (discord artifacts excluded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
