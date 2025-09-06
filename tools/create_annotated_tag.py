#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create an annotated release tag embedding integrity manifest hash.

Usage:
  python tools/create_annotated_tag.py vX.Y.Z [--manifest integrity-manifest.json]

Steps:
 1. Load integrity manifest JSON (if present) and compute SHA256 of file.
 2. Compose annotated tag message including INTEGRITY_MANIFEST_SHA256 line.
 3. git tag -a <tag> -m <message>

Exit codes:
 0 success
 1 failure (git/IO)

Safe to run repeatedly; refuses if tag already exists.
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
    try:
        out = subprocess.check_output(["git", *args], stderr=subprocess.STDOUT)
        return out.decode().strip()
    except subprocess.CalledProcessError as e:  # pragma: no cover - external tool
        print(e.output.decode(), file=sys.stderr)
        raise


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--manifest", default="integrity-manifest.json")
    ap.add_argument("--force", action="store_true", help="Overwrite existing tag")
    args = ap.parse_args(argv)

    # Already exists?
    try:
        existing = git("rev-parse", "-q", "--verify", f"refs/tags/{args.tag}")
        if existing and not args.force:
            print(
                f"[TAG] Tag {args.tag} already exists at {existing}; pass --force to recreate",
                file=sys.stderr,
            )
            return 1
    except Exception:
        existing = None

    manifest_path = Path(args.manifest)
    manifest_hash = None
    manifest_entries = 0
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_entries = (
                len(data.get("artifacts", [])) if isinstance(data, dict) else 0
            )
        except Exception:
            pass
        try:
            manifest_hash = sha256_file(manifest_path)
        except Exception:
            pass

    msg_lines = [
        f"Release {args.tag}",
        "",  # blank
        "Integrity Manifest: present"
        if manifest_hash
        else "Integrity Manifest: missing",
    ]
    if manifest_hash:
        msg_lines.append(f"INTEGRITY_MANIFEST_SHA256={manifest_hash}")
        msg_lines.append(f"INTEGRITY_MANIFEST_ENTRIES={manifest_entries}")
    msg_lines.append("Generated-by: create_annotated_tag.py")

    try:
        if existing and args.force:
            git("tag", "-d", args.tag)
        git("tag", "-a", args.tag, "-m", "\n".join(msg_lines))
        print(f"[TAG] Created annotated tag {args.tag}")
        if manifest_hash:
            print(f"[TAG] Embedded manifest hash {manifest_hash}")
    except Exception as e:  # pragma: no cover - external command failure
        print(f"[TAG][FAIL] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
