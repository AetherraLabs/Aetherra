#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Repository Root Organizer (safe Phase 1)
- Moves non-core artifacts out of project root into modular folders.
- Skips core runtime files and known entrypoints.
- Generates a report of changes.

Usage:
  python tools/organize_repo.py --apply     # perform moves
  python tools/organize_repo.py             # dry run
"""

from __future__ import annotations

# Standard library imports
import argparse
import fnmatch
import json
import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Destinations
DEST = {
    "reports": ROOT / "docs" / "reports",
    "logs": ROOT / "logs",
    "data": ROOT / "data",
    "maint": ROOT / "tools" / "maintenance",
    "devops": ROOT / "scripts" / "devops",
}

CORE_KEEP = {
    # Core packages/dirs to never move
    "Aetherra",
    "docs",
    "tools",
    "tests",
    "plugins",
    "frontend",
    "deployments",
    "docker",
    "node_modules",
    "requirements",
    "templates",
    "aetherra_memory",
    "aetherra_os_web",
    "qfac_memory_system",
    "quantum_dashboard",
}

CORE_FILES = {
    # Core runtime files to keep at root (imported by launcher/runtime)
    "aetherra_os_launcher.py",
    "aetherra_kernel_loop.py",
    "aetherra_service_registry.py",
    # Legacy hub server file removed; compat layer lives under aetherra_hub/compat.py
    "aetherra_plugin_discovery.py",
    "aetherra_script_service.py",
    "aetherra_persistent_memory.py",
    "aetherra_adaptive_behavior.py",
    "aetherra_os.py",
    "restart_aetherra.py",
    "aetherra_hmr_controller.py",
}

# Patterns mapping (only matches files in ROOT)
PATTERNS: list[tuple[list[str], Path]] = [
    # Logs
    (["*.log"], DEST["logs"]),
    # Data
    (
        [
            "*.db",
            "*metrics*.json",
            "*analysis*.json",
            "*inspection*.json",
            "*usage*.json",
        ],
        DEST["data"],
    ),
    # Reports/Docs
    (
        [
            "*REPORT*.md",
            "*ANALYSIS*.md",
            "*SUMMARY*.md",
            "*PLAN*.md",
            "*STATUS.md",
            "*COMPLETE*.md",
            "*COMPLETION*.md",
            "*READINESS*.md",
            "*RELEASE*.md",
            "FILE_*md",
            "DIRECTORY_*md",
            "PROJECT_*md",
            "LYRIXA_*md",
            "ARCHITECTURE_*md",
            "API_DIRECTORY_ANALYSIS.md",
        ],
        DEST["reports"],
    ),
    # HTML debug
    (["debug.html", "test.html"], DEST["reports"]),
    # DevOps scripts
    (["build-website.*", "dev-website.*"], DEST["devops"]),
    # Maintenance scripts (one-off root utilities)
    (
        [
            "fix_*.py",
            "check_*.py",
            "verify_*.py",
            "generate_reports.py",
            "project_analyzer.py",
            "advanced_analyzer*.py",
            "complete_organizer.py",
            "final_*.py",
            "post_cleanup_import_updater.py",
            "quick_fix_imports.py",
            "focused_cleanup.py",
            "safe_cleanup.py",
            "smart_cleanup.py",
            "final_file_organizer.py",
            "validate_architecture.py",
            "create_documentation.py",
            "universal_directory_analyzer.py",
            "debug_registry_connection.py",
            "launch_monitor.py",
        ],
        DEST["maint"],
    ),
]

# Exclusions for JSON/data patterns to avoid moving config/manifests
JSON_EXCLUDE = {"config.json", "package.json", "package-lock.json", "pyproject.toml"}


@dataclass
class MoveAction:
    src: Path
    dest: Path


def should_skip_file(p: Path) -> bool:
    name = p.name
    if name.startswith("."):
        return True
    if name in CORE_FILES:
        return True
    # Skip top-level manifests and license/readme
    if name.lower() in {"readme.md", "license", "notice", "manifest.in"}:
        return True
    if name in JSON_EXCLUDE:
        return True
    return False


def plan_moves() -> list[MoveAction]:
    actions: list[MoveAction] = []
    for child in ROOT.iterdir():
        if child.is_dir():
            if child.name in CORE_KEEP or child.name.startswith("."):
                continue
            # leave other dirs alone for Phase 1
            continue
        if child.is_file():
            if should_skip_file(child):
                continue
            # Try to match patterns in order
            for pat_list, dest in PATTERNS:
                for pat in pat_list:
                    if fnmatch.fnmatch(child.name, pat):
                        # Additional guard for JSON patterns
                        if child.suffix == ".json" and child.name in JSON_EXCLUDE:
                            continue
                        actions.append(MoveAction(child, dest / child.name))
                        pat_list = []  # break outer
                        break
                else:
                    continue
                break
    return actions


def apply_moves(
    actions: list[MoveAction], dry_run: bool = True
) -> dict[str, list[str]]:
    report: dict[str, list[str]] = {}
    for act in actions:
        act.dest.parent.mkdir(parents=True, exist_ok=True)
        report.setdefault(str(act.dest.parent.relative_to(ROOT)), []).append(
            act.src.name
        )
        if dry_run:
            continue
        try:
            # If destination exists, add numeric suffix
            target = act.dest
            if target.exists():
                stem, suf = target.stem, target.suffix
                i = 1
                while target.exists():
                    target = target.with_name(f"{stem}_{i}{suf}")
                    i += 1
            shutil.move(str(act.src), str(target))
        except Exception as e:
            print(f"[WARN] Failed to move {act.src} -> {act.dest}: {e}")
    return report


def main():
    ap = argparse.ArgumentParser(
        description="Organize repository root by moving non-core artifacts."
    )
    ap.add_argument(
        "--apply", action="store_true", help="Execute moves (default: dry run)"
    )
    args = ap.parse_args()

    actions = plan_moves()
    report = apply_moves(actions, dry_run=not args.apply)

    out = {
        "root": str(ROOT),
        "moved_count": sum(len(v) for v in report.values()),
        "destinations": list(report.keys()),
        "by_destination": report,
        "dry_run": (not args.apply),
    }
    out_path = ROOT / (
        "PROJECT_CLEANUP_PLAN.json"
        if not args.apply
        else "PROJECT_CLEANUP_APPLIED.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(
        ("[DRY]" if not args.apply else "[APPLIED]"),
        f"Organized {out['moved_count']} files. Report: {out_path}",
    )


if __name__ == "__main__":
    main()
