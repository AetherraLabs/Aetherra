#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Prune Aetherra/gui directory to keep only the minimal OS GUI.

Keeps:
- aetherra_os_gui.py
- launch_enhanced_neural_os.py (compat wrapper -> os_gui)
- run_aetherra_os.py (compat wrapper -> os_gui)
- README.md
- __init__.py
- GUI_CURATION_PLAN.md

Deletes everything else in Aetherra/gui, including subfolders like web_* and dashboards.
Use --apply to actually delete; otherwise runs in dry-run mode.
"""

from __future__ import annotations

# Standard library imports
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = ROOT / "Aetherra" / "gui"
KEEP = {
    "aetherra_os_gui.py",
    "launch_enhanced_neural_os.py",
    "run_aetherra_os.py",
    "README.md",
    "__init__.py",
    "GUI_CURATION_PLAN.md",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune Aetherra/gui to minimal GUI")
    parser.add_argument(
        "--apply", action="store_true", help="Actually delete files (not just dry-run)"
    )
    args = parser.parse_args()

    if not GUI_DIR.exists():
        print(f"GUI directory not found: {GUI_DIR}")
        return 1

    removed = []
    skipped = []

    for entry in GUI_DIR.iterdir():
        name = entry.name
        if name in KEEP or name == "__pycache__":
            skipped.append(str(entry))
            continue
        if args.apply:
            try:
                if entry.is_dir():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()
                removed.append(str(entry))
            except Exception as e:
                print(f"Failed to remove {entry}: {e}")
        else:
            removed.append(f"DRY-RUN: {entry}")

    print("Prune summary:")
    print("- Kept:")
    for s in sorted(skipped):
        print(f"  • {s}")
    print("- Removed:")
    for r in sorted(removed):
        print(f"  • {r}")

    if not args.apply:
        print("\nRun with --apply to perform deletions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
