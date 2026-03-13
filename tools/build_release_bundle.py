#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""One-shot build + SBOM + manifest helper.

Steps:
 1. Clean dist/
 2. Build wheel + sdist (requires 'build' package)
 3. Generate SBOM (tools/generate_sbom.py)
 4. Emit and optionally sign release manifest (tools/sign_release_manifest.py)

Usage:
  python tools/build_release_bundle.py --version 0.1.0-alpha.1

Environment:
  AETHERRA_RELEASE_PRIVKEY (optional ed25519 hex) for signing
"""

from __future__ import annotations

# Standard library imports
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def run(cmd: list[str]):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out, _ = p.communicate()
    print(out)
    if p.returncode != 0:
        raise SystemExit(p.returncode)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--skip-sbom", action="store_true")
    ap.add_argument("--skip-manifest", action="store_true")
    args = ap.parse_args()

    # 1. Clean
    shutil.rmtree(DIST, ignore_errors=True)
    DIST.mkdir(parents=True, exist_ok=True)

    # 2. Build
    run(
        [sys.executable, "-m", "pip", "install", "--quiet", "build>=1.0.0"]
    )  # ensure build tool
    run([sys.executable, "-m", "build"])  # places artifacts in dist/

    sbom_path = DIST / "aetherra-sbom.json"
    if not args.skip_sbom:
        run(
            [
                sys.executable,
                "tools/generate_sbom.py",
                "--out",
                str(sbom_path),
            ]
        )

    if not args.skip_manifest:
        manifest_args = [
            sys.executable,
            "tools/sign_release_manifest.py",
            "--dist",
            str(DIST),
            "--version",
            args.version,
        ]
        if sbom_path.exists():
            manifest_args += ["--sbom", str(sbom_path)]
        run(manifest_args)

    print("[BUILD_BUNDLE] Completed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
