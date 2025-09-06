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

import argparse
import json
import re
from importlib import metadata
from pathlib import Path

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

    print(f"[LICENSE] {len(rows)} packages scanned")
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
