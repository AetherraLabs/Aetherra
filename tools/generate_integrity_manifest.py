#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate integrity manifest for release artifacts.

Computes SHA256 for selected project files (lock file, sbom, license report, wheel artifacts)
and emits a JSON manifest plus a plain-text summary suitable for signing.

Usage:
  python tools/generate_integrity_manifest.py --dist dist --out integrity-manifest.json

Exit codes:
 0 success
 2 invalid input

Future (Beta): integrate with provenance attestation & signature creation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DEFAULT_FILES = [
    "requirements.lock",
    "licenses_report.json",
    "sbom.json",
]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def gather(dist: Path) -> list[dict]:
    items = []
    for f in DEFAULT_FILES:
        p = Path(f)
        if p.is_file():
            items.append({"path": f, "sha256": sha256_file(p)})
    if dist.is_dir():
        for art in dist.iterdir():
            if art.suffix in (".whl", ".gz") and art.is_file():
                items.append({"path": str(art), "sha256": sha256_file(art)})
    return items


def run(out: Path, dist: Path) -> int:
    items = gather(dist)
    data = {"artifacts": items}
    try:
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:  # pragma: no cover - file system failure
        print(f"[INTEGRITY][ERROR] write failed: {e}", file=sys.stderr)
        return 2
    print(f"[INTEGRITY] manifest wrote {len(items)} entries -> {out}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dist", default="dist")
    ap.add_argument("--out", default="integrity-manifest.json")
    args = ap.parse_args(argv)
    return run(Path(args.out), Path(args.dist))


if __name__ == "__main__":
    raise SystemExit(main())
