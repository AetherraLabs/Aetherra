#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a provenance tag (lightweight or annotated) referencing integrity manifest.

Intended for future provenance / attestation expansion. For now it mirrors the
annotated tag script but uses a distinct message prefix and supports `--lightweight`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args: str) -> str:
    out = subprocess.check_output(["git", *args], stderr=subprocess.STDOUT)
    return out.decode().strip()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--manifest", default="integrity-manifest.json")
    ap.add_argument("--lightweight", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)

    try:
        existing = git("rev-parse", "-q", "--verify", f"refs/tags/{args.tag}")
        if existing and not args.force:
            print(
                f"[PROV] Tag {args.tag} already exists; use --force to recreate",
                file=sys.stderr,
            )
            return 1
    except subprocess.CalledProcessError:
        existing = None

    manifest_path = Path(args.manifest)
    manifest_hash = sha256_file(manifest_path) if manifest_path.is_file() else None
    entries = 0
    if manifest_hash:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entries = len(data.get("artifacts", [])) if isinstance(data, dict) else 0
        except Exception:
            pass

    if args.lightweight:
        if existing and args.force:
            git("tag", "-d", args.tag)
        git("tag", args.tag)
        print(f"[PROV] Created lightweight tag {args.tag}")
        if manifest_hash:
            print(
                f"[PROV] (lightweight) manifest hash: {manifest_hash} entries={entries}"
            )
        return 0

    msg = [f"Provenance {args.tag}", "", "Type: provenance"]
    if manifest_hash:
        msg.append(f"INTEGRITY_MANIFEST_SHA256={manifest_hash}")
        msg.append(f"INTEGRITY_MANIFEST_ENTRIES={entries}")
    msg.append("Generated-by: create_provenance_tag.py")

    if existing and args.force:
        git("tag", "-d", args.tag)
    git("tag", "-a", args.tag, "-m", "\n".join(msg))
    print(f"[PROV] Created provenance tag {args.tag}")
    if manifest_hash:
        print(f"[PROV] Embedded manifest hash {manifest_hash}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
