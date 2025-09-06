#!/usr/bin/env python3
"""Create an annotated git tag embedding release provenance metadata.

Alpha helper: Generates (or prints) a recommended `git tag -a <tag>` message body
containing:
- Release version
- SHA256 of release-manifest.json
- Line for SBOM file name
- Optional lock file hash (requirements.lock)
- Timestamp (UTC ISO8601)
- Tool version marker

Usage (typical after building + signing):
  python tools/create_provenance_tag.py --version 0.1.0-alpha.1 \
      --manifest dist/release-manifest.json --sbom dist/aetherra-sbom.json \
      --lock requirements.lock --tag v0.1.0-alpha.1 --apply

If --apply provided and git is available, performs:
  git tag -a <tag> -m <generated body>

Otherwise prints the proposed tag body to stdout.

Exit codes:
  0 success
  2 missing required input files
  3 git operation failed (when --apply specified)

Future (Beta+): include builder identity, reproducible build hash, SLSA attestation link.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

TOOL_VERSION = "alpha"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate provenance tag body")
    p.add_argument("--version", required=True, help="Release version string")
    p.add_argument("--manifest", required=True, help="Path to release-manifest.json")
    p.add_argument("--sbom", required=True, help="Path to SBOM file")
    p.add_argument(
        "--lock",
        default="requirements.lock",
        help="Path to lock file (default: requirements.lock)",
    )
    p.add_argument("--tag", help="Tag name to create (with --apply)")
    p.add_argument(
        "--apply", action="store_true", help="Actually create the annotated git tag"
    )
    p.add_argument(
        "--print-only",
        action="store_true",
        help="Force printing even if --apply specified (debug)",
    )
    args = p.parse_args(argv)

    manifest_path = pathlib.Path(args.manifest)
    sbom_path = pathlib.Path(args.sbom)
    lock_path = pathlib.Path(args.lock)

    missing = [str(p) for p in [manifest_path, sbom_path] if not p.is_file()]
    if missing:
        print(
            f"[ERROR] Required file(s) missing: {', '.join(missing)}", file=sys.stderr
        )
        return 2

    try:
        manifest_json = json.loads(manifest_path.read_text())
    except Exception as e:
        print(f"[WARN] Unable to parse manifest JSON: {e}", file=sys.stderr)
        manifest_json = None

    manifest_hash = sha256_file(manifest_path)
    sbom_hash = sha256_file(sbom_path)
    lock_hash = sha256_file(lock_path) if lock_path.is_file() else None

    ts = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    body_lines = [
        f"Aetherra Release {args.version}",
        "",  # blank
        f"manifest: {manifest_path} (sha256:{manifest_hash})",
        f"sbom: {sbom_path} (sha256:{sbom_hash})",
    ]
    if lock_hash:
        body_lines.append(f"lock: {lock_path} (sha256:{lock_hash})")
    if manifest_json and "signing" in manifest_json:
        sk = manifest_json["signing"].get("key_hint", "<unknown>")
        body_lines.append(f"signature: present (key_hint={sk})")
    else:
        body_lines.append("signature: none")
    body_lines += [
        f"generated_at: {ts}",
        f"tool: create_provenance_tag.py@{TOOL_VERSION}",
        "",
        "# Importable verification snippet:",
        "# python tools/verify_release_manifest.py --manifest dist/release-manifest.json --dist dist --pubkey <hex>",
    ]

    tag_body = "\n".join(body_lines)

    if args.apply:
        if not args.tag:
            print("[ERROR] --tag required when using --apply", file=sys.stderr)
            return 2
        if not args.print_only:
            try:
                subprocess.run(
                    ["git", "tag", "-a", args.tag, "-m", tag_body], check=True
                )
                print(f"[OK] Created annotated tag {args.tag}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] git tag failed: {e}", file=sys.stderr)
                return 3
    print(tag_body)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
