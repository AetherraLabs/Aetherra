#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Prune Aetherra/lyrixa/gui to keep only the new React GUI.

Keeps (React/Vite app essentials + transition docs/config):
- package.json
- package-lock.json (if present)
- index.html
- src/ (React source)
- assets/ (static assets used by React)
- postcss.config.cjs / postcss.config.js
- tailwind.config.cjs / tailwind.config.js
- tailwind.config.js
- vite.config.js / vite.config.ts
- tsconfig.json / tsconfig.node.json
- .gitignore
- README.md (project doc)
- QUICKSTART.md, SETUP.md, STARTUP.md, SUMMARY.md, CHANGELOG.md
- main_window.py (temporary compatibility shim)
- PHASE3_README.md, PHASE3_IMPLEMENTATION_COMPLETE.md (docs)

Everything else under Aetherra/lyrixa/gui will be removed, including Python GUI files,
legacy web_panels/widgets, and the legacy frontend/ folder.

Additionally removes the legacy directory Aetherra/lyrixa/ui entirely.

This script is intentionally conservative by default during migration. It does not
remove `node_modules/` or editor metadata directories in dry-run/apply mode; those
can be deleted later once the Lyrixa GUI is fully retired.

Run with --apply to actually delete; default is dry-run.
"""

from __future__ import annotations

import argparse
import hashlib
import os
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
    "postcss.config.js",
    "tailwind.config.cjs",
    "tailwind.config.js",
    "vite.config.js",
    "vite.config.ts",
    "tsconfig.json",
    "tsconfig.node.json",
    ".gitignore",
    "README.md",
    "QUICKSTART.md",
    "SETUP.md",
    "STARTUP.md",
    "SUMMARY.md",
    "CHANGELOG.md",
    "main_window.py",
    "PHASE3_README.md",
    "PHASE3_IMPLEMENTATION_COMPLETE.md",
}
KEEP_DIRS = {
    "src",
    "assets",
    "node_modules",
    ".vscode",
}


def _hash_path(path: Path) -> str:
    return hashlib.sha256(str(path).encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:delete",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _planned_delete_metadata() -> dict[str, object]:
    gui_delete_hashes = []
    if GUI_DIR.exists():
        gui_delete_hashes = [
            _hash_path(entry)
            for entry in GUI_DIR.iterdir()
            if entry.name not in KEEP_FILES
            and entry.name not in KEEP_DIRS
            and entry.name != "__pycache__"
        ]
    legacy_file_hashes = [_hash_path(path) for path in LEGACY_FILES if path.exists()]
    return {
        "gui_dir_hash": _hash_path(GUI_DIR),
        "legacy_ui_dir_hash": _hash_path(LEGACY_UI_DIR),
        "gui_delete_count": len(gui_delete_hashes),
        "gui_delete_hashes": tuple(sorted(gui_delete_hashes)[:20]),
        "legacy_ui_exists": LEGACY_UI_DIR.exists(),
        "legacy_file_count": len(legacy_file_hashes),
        "legacy_file_hashes": tuple(sorted(legacy_file_hashes)),
    }


def _guardian_preflight_apply():
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.lyrixa_gui_prune",
            target="maintenance:lyrixa_gui_cleanup",
            purpose="Prune legacy Lyrixa GUI files while keeping the React GUI allow-list",
            capabilities=("maintenance:cleanup", "fs:delete"),
            expected_outcome="Legacy Lyrixa GUI files are deleted according to the curated keep-list",
            reversible=False,
            rollback_plan="restore deleted GUI files from version control or a prior workspace backup",
            metadata=_planned_delete_metadata(),
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


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

    if args.apply:
        decision = _guardian_preflight_apply()
        if not decision.allowed:
            print(f"Guardian denied Lyrixa GUI prune: {decision.reason}")
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
