#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Create (or print) an annotated git tag embedding release provenance.

Alpha helper; intentionally simple and self‑contained. Responsibilities:
  * Read an existing release manifest (default: dist/release-manifest.json OR dist/release_manifest.json)
  * Compute SHA256 of manifest
  * Compute SHA256 of requirements.lock (if present)
  * Include presence of signature + key hint (if manifest.signing present)
  * Emit deterministic tag body (sorted key assumptions) to stdout OR apply with `git tag -a` when --apply provided

If the manifest file is missing, a minimal synthetic manifest summary is produced by hashing any artifacts found under dist/ (* .whl / *.tar.gz). This is a best‑effort fallback so CI can still create a traceable tag after a partial build.

Example (print only):
  python tools/create_annotated_tag.py --version 0.1.0-alpha.1

Example (apply):
  python tools/create_annotated_tag.py --version 0.1.0-alpha.1 --tag v0.1.0-alpha.1 --apply

Exit codes:
  0 success
  2 invalid input / missing required file (and no fallback artifacts)
  3 git tagging failed

Future (Beta+): integrate build provenance (SLSA style), builder identity, transparency log reference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime
from typing import Optional, Tuple

TOOL_VERSION = "alpha"

# ------------------ helpers ------------------


def _sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_manifest(path_hint: Optional[str]) -> Optional[pathlib.Path]:
    if path_hint:
        p = pathlib.Path(path_hint)
        if p.is_file():
            return p
    for cand in ("dist/release-manifest.json", "dist/release_manifest.json"):
        pc = pathlib.Path(cand)
        if pc.is_file():
            return pc
    return None


def _load_manifest(p: pathlib.Path) -> Tuple[Optional[dict], str]:
    try:
        data = json.loads(p.read_text("utf-8"))
        return data, _sha256_file(p)
    except Exception as e:  # pragma: no cover - defensive
        print(f"[WARN] Failed to parse manifest {p}: {e}", file=sys.stderr)
        return None, _sha256_file(p)


def _synthesize_manifest(dist_dir: pathlib.Path) -> Optional[dict]:
    if not dist_dir.is_dir():
        return None
    artifacts = []
    for art in dist_dir.iterdir():
        if art.suffix in (".whl", ".gz") and art.is_file():
            try:
                artifacts.append({"path": art.name, "sha256": _sha256_file(art)})
            except Exception:
                pass
    if not artifacts:
        return None
    return {
        "version": "unknown",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "artifacts": artifacts,
        "synthetic": True,
    }


def build_tag_body(
    version: str,
    manifest: Optional[dict],
    manifest_hash: Optional[str],
    lock_path: pathlib.Path,
) -> str:
    lock_hash = _sha256_file(lock_path) if lock_path.is_file() else None
    sig_line = "signature: none"
    if manifest and isinstance(manifest, dict):
        sign = manifest.get("signing") or {}
        if sign:
            sig_line = f"signature: present (key_hint={sign.get('key_hint', '?')})"
    lines = [
        f"Aetherra Release {version}",
        "",  # blank
    ]
    if manifest_hash:
        lines.append(f"manifest_sha256: {manifest_hash}")
    if manifest:
        art_count = len(manifest.get("artifacts", []) or [])
        lines.append(f"artifacts: {art_count}")
        if manifest.get("synthetic"):
            lines.append("manifest_origin: synthetic")
    if lock_hash:
        lines.append(f"requirements_lock_sha256: {lock_hash}")
    lines.append(sig_line)
    lines.append(
        f"generated_at: {datetime.utcnow().replace(microsecond=0).isoformat()}Z"
    )
    lines.append(f"tool: create_annotated_tag.py@{TOOL_VERSION}")
    lines.append("")
    lines.append("# Verify manifest + artifacts example:")
    lines.append(
        "# python tools/verify_release_manifest.py --manifest dist/release-manifest.json --dist dist --pubkey <hex>"
    )
    return "\n".join(lines)


# ------------------ main ------------------


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Create or print an annotated provenance tag"
    )
    ap.add_argument("--version", required=True, help="Release version (semantic)")
    ap.add_argument(
        "--manifest", help="Path to release manifest (optional if in dist/)"
    )
    ap.add_argument(
        "--lock",
        default="requirements.lock",
        help="Path to requirements.lock (default: requirements.lock)",
    )
    ap.add_argument("--tag", help="Git tag name (required if --apply)")
    ap.add_argument(
        "--apply", action="store_true", help="If set, create annotated git tag"
    )
    ap.add_argument(
        "--print-only", action="store_true", help="Always print body even when applying"
    )
    args = ap.parse_args(argv)

    manifest_path = _find_manifest(args.manifest)
    manifest_data: Optional[dict] = None
    manifest_hash: Optional[str] = None

    if manifest_path:
        manifest_data, manifest_hash = _load_manifest(manifest_path)
    else:
        synth = _synthesize_manifest(pathlib.Path("dist"))
        if synth:
            manifest_data = synth
            # create a stable synthetic hash from artifact sha256 list sorted
            try:
                joined = "|".join(
                    sorted(
                        a["sha256"] for a in synth.get("artifacts", []) if "sha256" in a
                    )
                )
                manifest_hash = hashlib.sha256(joined.encode()).hexdigest()
            except Exception:
                manifest_hash = None
        else:
            print(
                "[ERROR] No manifest found and no artifacts to synthesize from",
                file=sys.stderr,
            )
            return 2

    lock_path = pathlib.Path(args.lock)
    body = build_tag_body(args.version, manifest_data, manifest_hash, lock_path)

    if args.apply:
        if not args.tag:
            print("[ERROR] --tag is required when using --apply", file=sys.stderr)
            return 2
        try:
            subprocess.run(["git", "tag", "-a", args.tag, "-m", body], check=True)
            print(f"[OK] Created annotated tag {args.tag}")
        except (
            subprocess.CalledProcessError
        ) as e:  # pragma: no cover - external failure path
            print(f"[ERROR] git tag failed: {e}", file=sys.stderr)
            return 3
    print(body)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
