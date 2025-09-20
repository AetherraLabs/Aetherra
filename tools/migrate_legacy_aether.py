#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
Migrate legacy .aether syntax to current idioms.

Focus: Non-destructive, idempotent transformations with dry-run diff summary.

Supported transforms (Phase 1):
  - Replace legacy 'intent:' with 'goal:'
  - Normalize quotes around goal strings (goal: "text")
  - Collapse multiple consecutive blank lines to max 2
  - Trim trailing whitespace

Planned (Phase 2 - TODO markers left):
  - Convert 'remember:' blocks to 'memory:'
  - Update deprecated function names (e.g., analyze_plugins() -> available_plugins())

Usage:
  Dry run (no changes):
    python tools/migrate_legacy_aether.py path/to/file_or_dir --dry-run
  Apply in-place:
    python tools/migrate_legacy_aether.py path/to/workflows --apply

Artifacts:
  - migration_report.md (summary of changes when multiple files processed)
Exit codes:
  0 success (even if some files unchanged)
  1 fatal error
"""

from __future__ import annotations

# Standard library imports
import argparse
import difflib
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Each transform takes the file text and returns (updated_text, changes)
TRANSFORMS: list[
    Callable[[str], tuple[str, list[str]]]
] = []  # populated after definitions


def t(
    fn: Callable[[str], tuple[str, list[str]]],
) -> Callable[[str], tuple[str, list[str]]]:
    TRANSFORMS.append(fn)
    return fn


@t
def transform_intent(goal: str) -> tuple[str, list[str]]:
    changed: list[str] = []
    lines = goal.splitlines()
    out = []
    for line in lines:
        if line.strip().startswith("intent:"):
            new_line = line.replace("intent:", "goal:", 1)
            if new_line != line:
                changed.append(f"intent->goal: {line.strip()} => {new_line.strip()}")
            line = new_line
        out.append(line)
    return "\n".join(out), changed


@t
def normalize_goal_quotes(text: str) -> tuple[str, list[str]]:
    changed: list[str] = []
    lines = text.splitlines()
    out = []
    for line in lines:
        if line.strip().startswith("goal:"):
            rest = line.split("goal:", 1)[1].strip()
            if (
                rest
                and not (rest.startswith('"') and rest.endswith('"'))
                and not (rest.startswith("'") and rest.endswith("'"))
            ):
                # Avoid backslash escapes inside f-string expressions (Py311-compatible)
                rest_stripped = rest.strip("\"'")
                new_line = f'goal: "{rest_stripped}"'
                if new_line != line:
                    changed.append(
                        f"quote-normalize: {line.strip()} => {new_line.strip()}"
                    )
                line = new_line
        out.append(line)
    return "\n".join(out), changed


@t
def collapse_blank_lines(text: str) -> tuple[str, list[str]]:
    changed: list[str] = []
    lines = text.splitlines()
    out = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                out.append(line)
        else:
            blank_run = 0
            out.append(line.rstrip())
    result = "\n".join(out)
    if result != text:
        changed.append("whitespace-normalized")
    return result, changed


def apply_transforms(original: str) -> tuple[str, list[str]]:
    cumulative_changes: list[str] = []
    current = original
    for fn in TRANSFORMS:
        current, changes = fn(current)
        cumulative_changes.extend(changes)
    return current, cumulative_changes


def migrate_file(path: Path, dry_run: bool) -> tuple[bool, list[str], str]:
    try:
        original = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return False, [f"read-error: {e}"], ""
    updated, changes = apply_transforms(original)
    if not changes:
        return True, [], ""
    if not dry_run:
        path.write_text(updated, encoding="utf-8")
    diff = "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile=str(path),
            tofile=str(path) + ".new",
            lineterm="",
        )
    )
    return True, changes, diff


def enumerate_targets(target: Path) -> list[Path]:
    if target.is_file() and target.suffix == ".aether":
        return [target]
    files: list[Path] = []
    for p in target.rglob("*.aether"):
        if p.is_file():
            files.append(p)
    return sorted(files)


def write_report(entries: list[dict[str, Any]], output: Path) -> None:
    lines = ["# .aether Migration Report", ""]
    for info in entries:
        path = info["path"]
        changes = info["changes"]
        if not changes:
            continue
        lines.append(f"## {path}")
        for c in changes:
            lines.append(f"- {c}")
        if info.get("diff"):
            lines.append("\n<details><summary>Diff</summary>\n\n````diff")
            lines.append(info["diff"])
            lines.append("````\n</details>\n")
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="File or directory containing .aether workflows")
    ap.add_argument("--dry-run", action="store_true", help="Show diffs only; no writes")
    ap.add_argument("--apply", action="store_true", help="Apply changes in-place")
    ap.add_argument(
        "--report",
        default="migration_report.md",
        help="Write aggregated report (only if multiple files)",
    )
    args = ap.parse_args()

    if args.dry_run and args.apply:
        print("Cannot use --dry-run and --apply together")
        return 2
    if not args.dry_run and not args.apply:
        print("Specify either --dry-run or --apply")
        return 2

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"Target not found: {target}")
        return 2

    files = enumerate_targets(target)
    if not files:
        print("No .aether files found.")
        return 0

    entries = []
    for f in files:
        ok, changes, diff = migrate_file(f, dry_run=args.dry_run)
        entries.append({"path": str(f), "changes": changes, "diff": diff})
        if changes:
            print(
                f"{f}: {'DRY-RUN' if args.dry_run else 'UPDATED'} ({len(changes)} changes)"
            )
        else:
            print(f"{f}: unchanged")

    if len(files) > 1:
        write_report(entries, Path(args.report))
        print(f"Report: {args.report}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
