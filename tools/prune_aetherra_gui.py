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
import hashlib
import os
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
    delete_hashes = []
    if GUI_DIR.exists():
        delete_hashes = [
            _hash_path(entry)
            for entry in GUI_DIR.iterdir()
            if entry.name not in KEEP and entry.name != "__pycache__"
        ]
    return {
        "gui_dir_hash": _hash_path(GUI_DIR),
        "delete_count": len(delete_hashes),
        "delete_hashes": tuple(sorted(delete_hashes)[:20]),
        "keep_count": len(KEEP),
    }


def _guardian_preflight_apply():
    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.aetherra_gui_prune",
            target="maintenance:aetherra_gui_cleanup",
            purpose="Prune legacy Aetherra GUI files while keeping the minimal OS GUI allow-list",
            capabilities=("maintenance:cleanup", "fs:delete"),
            expected_outcome="Legacy Aetherra GUI files are deleted according to the curated keep-list",
            reversible=False,
            rollback_plan="restore deleted GUI files from version control or a prior workspace backup",
            metadata=_planned_delete_metadata(),
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prune Aetherra/gui to minimal GUI")
    parser.add_argument(
        "--apply", action="store_true", help="Actually delete files (not just dry-run)"
    )
    args = parser.parse_args()

    if not GUI_DIR.exists():
        print(f"GUI directory not found: {GUI_DIR}")
        return 1

    if args.apply:
        decision = _guardian_preflight_apply()
        if not decision.allowed:
            print(f"Guardian denied Aetherra GUI prune: {decision.reason}")
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
