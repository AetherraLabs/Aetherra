#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fetch the current SPDX license list and store a simplified ID array.

Usage:
  python tools/update_spdx_ids.py --out spdx_license_ids.json

Source: https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json
Falls back with non-zero exit if network unavailable.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

URL = (
    "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"
)


def fetch() -> list[str]:
    try:
        with urllib.request.urlopen(URL, timeout=10) as r:  # nosec B310
            data = json.loads(r.read().decode())
        items = data.get("licenses") if isinstance(data, dict) else []
        out: list[str] = []
        if isinstance(items, list):
            for lic in items:
                if isinstance(lic, dict):
                    lid = lic.get("licenseId")
                    if isinstance(lid, str) and lid.strip():
                        out.append(lid.strip())
        return sorted(set(out))
    except Exception as e:
        print(f"[SPDX][WARN] fetch failed: {e}", file=sys.stderr)
        return []


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="spdx_license_ids.json")
    args = ap.parse_args(argv)
    ids = fetch()
    if not ids:
        print("[SPDX][FAIL] No IDs fetched", file=sys.stderr)
        return 1
    Path(args.out).write_text(json.dumps(ids, indent=2) + "\n", encoding="utf-8")
    print(f"[SPDX] Wrote {len(ids)} IDs -> {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
