#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate minimal SBOM (alpha) from license_report JSON.

Simple in-repo tool to provide early supply-chain visibility without
adding heavy external dependencies. Not CycloneDX compliant yet.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--license-json", default="licenses_report.json")
    ap.add_argument("--out", default="sbom.json")
    args = ap.parse_args()
    src = Path(args.license_json)
    if not src.exists():
        print(f"[SBOM][FAIL] missing license report: {src}")
        return 2
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
    except Exception as e:  # pragma: no cover
        print(f"[SBOM][FAIL] parse error: {e}")
        return 2
    comps = [
        {
            "name": r.get("name"),
            "version": r.get("version"),
            "license": r.get("license"),
        }
        for r in data
    ]
    bom = {
        "bomFormat": "Aetherra-SBOM",
        "specVersion": "0.1-alpha",
        "metadata": {
            "generated": datetime.now(timezone.utc).isoformat(),
            "tool": "generate_sbom.py",
            "source": str(src),
            "env": {
                k: v
                for k, v in os.environ.items()
                if k.startswith("AETHERRA_") or k.startswith("LICENSE_UNKNOWN_")
            },
        },
        "components": comps,
    }
    out = Path(args.out)
    out.write_text(json.dumps(bom, indent=2), encoding="utf-8")
    print(f"[SBOM] wrote {out} ({len(comps)} components)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
