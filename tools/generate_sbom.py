#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate a CycloneDX SBOM (JSON) for the current environment/project.

Lightweight approach to avoid external dependency tools in alpha:
- Uses `pip list --format=json` to capture direct + installed deps
- Hashes distribution files when available in site-packages (best-effort)
- Emits minimal CycloneDX 1.5 compliant structure (bomFormat, specVersion, components)

Usage:
  python tools/generate_sbom.py --output dist/aetherra-sbom.json

Future:
- Replace with proper library (cyclonedx-bom) when dependency policy finalized
- Add license attribution aggregation
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


def hash_dist_files(dist_name: str) -> list[dict[str, str]]:
    """Attempt to hash top-level .dist-info RECORD listed files (best-effort)."""
    results: list[dict[str, str]] = []
    try:
        import importlib.metadata as im  # py3.8+

        for dist in im.distributions():
            if dist.metadata["Name"].lower() == dist_name.lower():
                record = None
                for f in dist.files or []:
                    if f.name == "RECORD" and f.parent.name.endswith(".dist-info"):
                        record = dist.locate_file(f)
                        break
                if not record or not record.exists():
                    return results
                # Use explicit open to avoid issues with some path-like objects missing errors param
                with open(record, "r", encoding="utf-8", errors="replace") as rf:  # type: ignore[arg-type]
                    lines = rf.read().splitlines()
                for line in lines:
                    parts = line.split(",")
                    if len(parts) < 2:
                        continue
                    rel_path = parts[0]
                    file_path = Path(dist.locate_file(rel_path))  # type: ignore[arg-type]
                    if not file_path.exists() or not file_path.is_file():
                        continue
                    try:
                        h = hashlib.sha256(file_path.read_bytes()).hexdigest()
                        results.append({"path": rel_path, "sha256": h})
                    except Exception:
                        continue
                break
    except Exception:
        return results
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="dist/aetherra-sbom.json")
    ap.add_argument("--name", default="aetherra")
    ap.add_argument("--version", default=os.getenv("AETHERRA_VERSION", "0.0.0"))
    args = ap.parse_args()

    # Ensure dist directory
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Collect package list
    code, out = subprocess.getstatusoutput(
        f"{sys.executable} -m pip list --format=json"
    )
    if code != 0:
        print("[SBOM] Failed to list packages")
        return 2
    try:
        pkgs = json.loads(out)
    except Exception:
        print("[SBOM] Failed to parse pip output")
        return 2

    components: List[Dict[str, Any]] = []
    for p in pkgs:
        name = p.get("name")
        version = p.get("version")
        purl = f"pkg:pypi/{name}@{version}" if name and version else None
        comp: Dict[str, Any] = {
            "type": "library",
            "name": name,
            "version": version,
        }
        if purl:
            comp["purl"] = purl
        hashes = hash_dist_files(name) if name else []
        if hashes:
            comp["evidence"] = {"hashes": hashes[:25]}  # cap to keep file small
        components.append(comp)

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "version": 1,
        "metadata": {
            "component": {
                "type": "application",
                "name": args.name,
                "version": args.version,
            }
        },
        "components": components,
    }

    Path(args.output).write_text(json.dumps(bom, indent=2))
    print(f"[SBOM] Wrote {args.output} with {len(components)} components")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
