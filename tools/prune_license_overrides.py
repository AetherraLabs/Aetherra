#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Prune stale entries from license_overrides.yml.

Logic:
 1. Load current licenses_report.json (regenerate first if needed).
 2. Identify overrides whose package now has a non-UNKNOWN license in report.
 3. Remove those entries (unless --dry-run) and write updated file.
 4. Print a summary including counts removed/kept.

Usage:
  python tools/prune_license_overrides.py [--overrides license_overrides.yml] [--report licenses_report.json] [--dry-run]

Exit codes:
  0 success (even if nothing pruned)
  1 failure (I/O or parse error)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_yaml(path: Path):
    if yaml is None:
        raise RuntimeError("PyYAML not installed; cannot prune overrides")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--overrides", default="license_overrides.yml")
    ap.add_argument("--report", default="licenses_report.json")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    overrides_path = Path(args.overrides)
    report_path = Path(args.report)

    if not overrides_path.exists():
        print(f"[PRUNE] Overrides file missing: {overrides_path}")
        return 1
    if not report_path.exists():
        print(f"[PRUNE] Report file missing: {report_path} (run license_report first)")
        return 1

    try:
        overrides = load_yaml(overrides_path)
    except Exception as e:
        print(f"[PRUNE][FAIL] Could not parse overrides: {e}")
        return 1
    if not isinstance(overrides, dict):
        print("[PRUNE][FAIL] Overrides YAML is not a mapping")
        return 1

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[PRUNE][FAIL] Could not parse report JSON: {e}")
        return 1

    license_map = {r["name"].lower(): (r.get("license") or "").strip() for r in report}

    stale = {}
    kept = {}
    for pkg, expr in overrides.items():
        lic = license_map.get(pkg.lower(), "UNKNOWN").upper()
        if lic != "UNKNOWN" and lic:
            # license now resolved upstream -> stale
            stale[pkg] = expr
        else:
            kept[pkg] = expr

    print(
        f"[PRUNE] Overrides total: {len(overrides)} | stale: {len(stale)} | kept: {len(kept)}"
    )
    if stale:
        print("[PRUNE] Stale entries:")
        for k, v in sorted(stale.items()):
            print(f"  - {k}: {v}")

    if stale and not args.dry_run:
        # Write back kept + stale commented for audit (optional approach: just keep kept)
        new_lines = []
        for k, v in sorted(kept.items()):
            new_lines.append(f'"{k}": {v}')
        if kept and stale:
            new_lines.append("")
        if stale:
            new_lines.append(
                "# Stale (auto-pruned) below; retained for audit, remove manually if desired:"
            )
            for k, v in sorted(stale.items()):
                new_lines.append(f'# "{k}": {v}')
        overrides_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"[PRUNE] Updated {overrides_path} (stale commented out)")
    elif stale and args.dry_run:
        print("[PRUNE] Dry run: no changes written")
    else:
        print("[PRUNE] No stale entries detected")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
