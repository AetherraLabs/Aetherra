# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Quarantine Unused Engines
=========================
Reads engine_usage_matrix.json and prepares to move OS-unreferenced engine files
into Aetherra/legacy/, excluding Lyrixa paths. Supports dry-run and execute modes.

Usage:
  python tools/quarantine_unused_engines.py --dry-run   # list planned moves
  python tools/quarantine_unused_engines.py --execute   # perform moves
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIR = REPO_ROOT / "Aetherra" / "legacy"
MATRIX_JSON = REPO_ROOT / "engine_usage_matrix.json"

EXCLUDE_PREFIXES = [
    str(Path("Aetherra") / "lyrixa") + os.sep,  # Don't move Lyrixa UI code
]


def plan_moves() -> list[tuple[Path, Path]]:
    data = json.loads(MATRIX_JSON.read_text(encoding="utf-8"))
    moves: list[tuple[Path, Path]] = []
    for item in data:
        file_rel = item.get("file")
        used_by_os = item.get("used_by_os", False)
        used_by_lyrixa = item.get("used_by_lyrixa", False)
        notes = (item.get("notes") or "").lower()
        if not file_rel:
            continue
        # Normalize
        file_rel_norm = file_rel.replace(str(REPO_ROOT) + os.sep, "")
        # Skip excluded paths
        if any(file_rel_norm.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            continue
        # Only consider .py files under repo
        src = REPO_ROOT / file_rel_norm
        if not src.exists() or src.suffix != ".py":
            continue
        # Candidate: no references by OS and Lyrixa, or explicitly noted
        if (not used_by_os and not used_by_lyrixa) or "candidate for removal" in notes:
            dst = LEGACY_DIR / file_rel_norm.replace(os.sep, "__")
            moves.append((src, dst))
    return moves


def ensure_legacy_dir():
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Perform moves")
    parser.add_argument("--dry-run", action="store_true", help="Print moves only")
    args = parser.parse_args()

    if not MATRIX_JSON.exists():
        print(
            "engine_usage_matrix.json not found. Run tools/engine_usage_matrix.py first."
        )
        return 2

    ensure_legacy_dir()
    moves = plan_moves()

    if not moves:
        print("No unused engine files to quarantine.")
        return 0

    print(f"Planned moves to {LEGACY_DIR}:")
    for src, dst in moves:
        print(f" - {src.relative_to(REPO_ROOT)} -> {dst.relative_to(REPO_ROOT)}")

    if args.execute:
        for src, dst in moves:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        print(f"Moved {len(moves)} files to {LEGACY_DIR}")
    else:
        print("(dry-run) No files moved. Re-run with --execute to apply.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
