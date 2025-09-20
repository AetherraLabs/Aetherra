#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate a license report for Python dependencies.

Reads requirements.lock (or provided file) and attempts to extract license
information via importlib.metadata or pkg_resources fallback.

Outputs a simple table + JSON file (licenses_report.json) summarizing:
  name | version | license | home-page

Non-resolved licenses are marked as UNKNOWN.

Exit code:
  0 always (non-enforcing). Future: optional enforcement flag.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
import re
from importlib import metadata
from pathlib import Path

try:
    # Third party imports
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

LOCK_LINE_RE = re.compile(r"^([A-Za-z0-9_.\-]+)==([A-Za-z0-9_.\-]+)$")


def parse_lock(lock_path: Path):
    for line in lock_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = LOCK_LINE_RE.match(line)
        if m:
            yield m.group(1), m.group(2)


def dist_meta(name: str):
    try:
        md = metadata.metadata(name)
    except Exception:
        return {}
    info = {}
    for key in ("Name", "Version", "License", "Home-page"):
        info[key.lower()] = md.get(key)
    if not info.get("license"):
        # Some packages embed license in classifiers
        classifiers = md.get_all("Classifier") or []
        lic = [c.split(":")[-1].strip() for c in classifiers if c.startswith("License")]
        if lic:
            info["license"] = "; ".join(sorted(set(lic)))
    return info


def normalize_license(lic: str | None) -> str:
    if not lic:
        return "UNKNOWN"
    lic = lic.replace("(MIT)", "MIT").strip()
    lic = lic.replace("License", "").strip()
    return lic[:120]


def compress_multiline(lic: str) -> str:
    """Collapse whitespace/newlines for display & JSON stability.

    Keeps length reasonable while preserving original semantic tokens.
    """
    if "\n" not in lic:
        return lic
    # Replace all whitespace (including newlines) with single spaces
    # Standard library imports
    import re as _re  # local import to avoid top-level cost

    compact = _re.sub(r"\s+", " ", lic).strip()
    # Cap at 160 chars for readability
    if len(compact) > 160:
        compact = compact[:157].rstrip() + "..."
    return compact


def load_overrides(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    if yaml is None:
        print("[LICENSE][WARN] PyYAML not available; ignoring overrides file")
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        print(f"[LICENSE][WARN] Failed to parse overrides file {path}: {e}")
        return {}
    if not isinstance(data, dict):
        return {}
    # Normalize keys to canonical package name form (case-insensitive)
    return {str(k).strip(): str(v).strip() for k, v in data.items() if v}


def apply_overrides(rows: list[dict[str, str]], overrides: dict[str, str]) -> int:
    """Apply overrides; returns count of changes made."""
    changed = 0
    if not overrides:
        return 0
    # Build lookup with lowercase keys for matching
    lower_map = {k.lower(): v for k, v in overrides.items()}
    for r in rows:
        ov = lower_map.get(r["name"].lower())
        if ov and r.get("license") == "UNKNOWN":
            r["license"] = ov
            changed += 1
    return changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", default="requirements.lock")
    ap.add_argument("--json", default="licenses_report.json")
    ap.add_argument(
        "--deny",
        nargs="*",
        default=[],
        help="License identifiers to deny (case-insensitive substring match)",
    )
    ap.add_argument(
        "--overrides",
        default="license_overrides.yml",
        help="YAML file mapping package name -> license expression to override UNKNOWN entries",
    )
    ap.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="Fail if any package has UNKNOWN license",
    )
    args = ap.parse_args()

    lock_path = Path(args.lock)
    if not lock_path.exists():
        print(f"[LICENSE][FAIL] lock file missing: {lock_path}")
        return 2

    rows = []
    for name, version in parse_lock(lock_path):
        meta = dist_meta(name)
        lic = normalize_license(meta.get("license"))
        rows.append(
            {
                "name": name,
                "version": version,
                "license": lic,
                "home_page": meta.get("home-page"),
            }
        )

    rows.sort(key=lambda r: r["name"].lower())

    # Apply overrides (only to UNKNOWN to avoid masking real classifier values)
    overrides_path = Path(args.overrides)
    overrides = load_overrides(overrides_path)
    applied_names: set[str] = set()
    if overrides:
        before_unknown = {r["name"].lower() for r in rows if r["license"] == "UNKNOWN"}
        changed = apply_overrides(rows, overrides)
        after_unknown = {r["name"].lower() for r in rows if r["license"] == "UNKNOWN"}
        applied_names = before_unknown - after_unknown
        if changed:
            print(
                f"[LICENSE] Overrides applied to {changed} previously UNKNOWN package(s) from {overrides_path.name}"
            )
        # Identify unused overrides (candidate retirement)
        unused = []
        for name, expr in overrides.items():
            if name.lower() not in applied_names:
                # Find row for extra context
                match = next(
                    (r for r in rows if r["name"].lower() == name.lower()), None
                )
                if match and match.get("license") and match["license"] != "UNKNOWN":
                    unused.append((name, expr, match["license"]))
        if unused:
            print(
                "[LICENSE] Override retirement candidates (metadata already present):"
            )
            for name, expr, current in sorted(unused):
                print(f"  - {name}: current='{current}' override='{expr}'")

    print(f"[LICENSE] {len(rows)} packages scanned")
    # Optional compression of multi-line license strings
    if os.getenv("LICENSE_COMPRESS_MULTILINE", "0") == "1":
        for r in rows:
            if isinstance(r.get("license"), str):
                r["license"] = compress_multiline(r["license"])

    unknown = [r for r in rows if r["license"] == "UNKNOWN"]
    if unknown:
        print(f"[LICENSE][WARN] {len(unknown)} packages with UNKNOWN license metadata")

    deny_list = [d.lower() for d in (args.deny or [])]
    denied = []
    if deny_list:
        for r in rows:
            lic_l = (r["license"] or "").lower()
            if any(d in lic_l for d in deny_list):
                denied.append(r)
    if denied:
        print(f"[LICENSE][FAIL] {len(denied)} packages match deny list")
        for r in denied[:25]:  # limit spam
            print(f"  - {r['name']} {r['version']} ({r['license']})")

    # Pretty table
    print("name,version,license,home_page")
    for r in rows:
        hp = (r["home_page"] or "").replace(",", " ")
        print(f"{r['name']},{r['version']},{r['license']},{hp}")

    Path(args.json).write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"[LICENSE] JSON written to {args.json}")

    fail = False
    if denied:
        fail = True
    if args.fail_on_unknown and unknown:
        fail = True
    return 1 if fail else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
