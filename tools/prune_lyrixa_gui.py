#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Prune Aetherra/lyrixa/gui to keep only the new React GUI.

Keeps (React/Vite app essentials):
- package.json
- package-lock.json (if present)
- index.html
- src/ (React source)
- assets/ (static assets used by React)
- postcss.config.cjs
- tailwind.config.cjs
- tailwind.config.js
- vite.config.js
- README.md (project doc)
- PHASE3_README.md, PHASE3_IMPLEMENTATION_COMPLETE.md (docs)

Everything else under Aetherra/lyrixa/gui will be removed, including Python GUI files,
legacy web_panels/widgets, and the legacy frontend/ folder.

Additionally removes the legacy directory Aetherra/lyrixa/ui entirely.

Run with --apply to actually delete; default is dry-run.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LYRIXA_DIR = ROOT / "Aetherra" / "lyrixa"
GUI_DIR = LYRIXA_DIR / "gui"
LEGACY_UI_DIR = LYRIXA_DIR / "ui"
LEGACY_FILES = [
    LYRIXA_DIR / "lyrixa_basic_gui.py",
]

KEEP_FILES = {
    "package.json",
    "package-lock.json",
    "index.html",
    "postcss.config.cjs",
    "tailwind.config.cjs",
    "tailwind.config.js",
    "vite.config.js",
    "README.md",
    "PHASE3_README.md",
    "PHASE3_IMPLEMENTATION_COMPLETE.md",
}
KEEP_DIRS = {
    "src",
    "assets",
}


def prune_gui(apply: bool) -> tuple[list[str], list[str]]:
    removed: list[str] = []
    kept: list[str] = []
    if not GUI_DIR.exists():
        return removed, kept

    for entry in GUI_DIR.iterdir():
        name = entry.name
        if name in KEEP_FILES or name in KEEP_DIRS or name == "__pycache__":
            kept.append(str(entry))
            continue
        if apply:
            try:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
                removed.append(str(entry))
            except Exception as e:
                removed.append(f"FAILED: {entry} -> {e}")
        else:
            removed.append(f"DRY-RUN: {entry}")
    return removed, kept


def remove_legacy_ui(apply: bool) -> tuple[list[str], bool]:
    removed: list[str] = []
    if not LEGACY_UI_DIR.exists():
        return removed, False
    if apply:
        try:
            shutil.rmtree(LEGACY_UI_DIR, ignore_errors=True)
            removed.append(str(LEGACY_UI_DIR))
        except Exception as e:
            removed.append(f"FAILED: {LEGACY_UI_DIR} -> {e}")
            return removed, False
        return removed, True
    removed.append(f"DRY-RUN: {LEGACY_UI_DIR}")
    return removed, True


def main() -> int:
    ap = argparse.ArgumentParser(description="Prune Lyrixa GUI to only React app")
    ap.add_argument(
        "--apply", action="store_true", help="Actually delete files (not dry-run)"
    )
    args = ap.parse_args()

    if not GUI_DIR.exists():
        print(f"Lyrixa GUI directory not found: {GUI_DIR}")
        return 1

    removed_gui, kept = prune_gui(apply=args.apply)
    removed_ui, ui_existed = remove_legacy_ui(apply=args.apply)

    # Remove specific legacy files at Lyrixa root
    removed_files: list[str] = []
    for f in LEGACY_FILES:
        if f.exists():
            if args.apply:
                try:
                    f.unlink(missing_ok=True)
                    removed_files.append(str(f))
                except Exception as e:
                    removed_files.append(f"FAILED: {f} -> {e}")
            else:
                removed_files.append(f"DRY-RUN: {f}")

    print("Lyrixa GUI prune summary:")
    print("- Kept:")
    for s in sorted(kept):
        print(f"  • {s}")
    print("- Removed:")
    for r in sorted(removed_gui + removed_ui + removed_files):
        print(f"  • {r}")

    if not args.apply:
        print("\nRun with --apply to perform deletions.")
    if args.apply and ui_existed:
        print("\nRemoved legacy Lyrixa/ui directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
