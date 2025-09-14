"""Prepare a curated release bundle directory (and optional zip).

Collects core artifacts for archival / distribution:
  * README.md, LICENSE, NOTICE
  * BETA_READINESS_REPORT.md (generate first externally)
  * RELEASE_NOTES* matching version substring
  * Core doc indices (docs/INDEX.md, docs/SYSTEM_INDEX.md, docs/DOCS_ARCHITECTURE.md)
  * Selected policies (THREAT_MODEL.md, COVERAGE_POLICY.md, GO_NO_GO_GATES.md)

Produces:
  dist/release_bundle_<version>/
    manifest.json
    files copied preserving relative simple paths
Optionally zips with --zip.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections.abc import Iterable
from pathlib import Path

DEFAULT_DOCS = [
    "docs/INDEX.md",
    "docs/SYSTEM_INDEX.md",
    "docs/DOCS_ARCHITECTURE.md",
    "docs/GO_NO_GO_GATES.md",
    "docs/COVERAGE_POLICY.md",
    "docs/THREAT_MODEL.md",
]

ROOT_FILES = ["README.md", "LICENSE", "NOTICE", "BETA_READINESS_REPORT.md"]


def existing(paths: Iterable[str]) -> list[str]:
    out = []
    for p in paths:
        if Path(p).exists():
            out.append(p)
    return out


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Prepare release bundle")
    parser.add_argument("--version", required=True)
    parser.add_argument("--zip", action="store_true")
    parser.add_argument(
        "--extra", nargs="*", default=[], help="Additional relative paths to include"
    )
    args = parser.parse_args()

    root = Path.cwd()
    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    bundle_dir = dist / f"release_bundle_{args.version}"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir()

    files: list[str] = []
    files.extend(existing(ROOT_FILES))
    files.extend(existing(DEFAULT_DOCS))
    # Release notes any matching version substring
    for rn in root.glob(f"RELEASE_NOTES*{args.version}*.md"):
        files.append(rn.name)
    files.extend(existing(args.extra))

    copied: list[str] = []
    for rel in files:
        src = root / rel
        if not src.exists():
            continue
        target = bundle_dir / src.name
        shutil.copy2(src, target)
        copied.append(rel)

    manifest = {
        "version": args.version,
        "files": copied,
    }
    (bundle_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(f"Release bundle prepared: {bundle_dir} ({len(copied)} files)")

    if args.zip:
        archive_path = shutil.make_archive(str(bundle_dir), "zip", root_dir=bundle_dir)
        print(f"Archive created: {archive_path}")


if __name__ == "__main__":
    main()
