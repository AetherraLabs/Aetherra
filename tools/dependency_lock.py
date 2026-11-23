#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Generate a dependency lock from explicit inputs or an existing environment.

Strategy (alpha):
- Assumes project (and optional extras) already installed in current venv
- Runs `pip freeze` and filters out editable local project path lines (-e .)
- Writes deterministic sorted list to requirements.lock

Usage:
  python tools/dependency_lock.py            # writes requirements.lock
  python tools/dependency_lock.py --output custom.lock
  python tools/dependency_lock.py -r requirements.txt -c requirements-ci.lock

Notes:
- For reproducible builds in CI, commit the produced lock file.
- Explicit inputs resolve with pip, ignoring installed packages. Use this mode
  for the supported desktop lock; the legacy freeze mode preserves existing callers.
"""

from __future__ import annotations

# Standard library imports
import argparse
import json
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve(requirements: list[str], constraints: list[str]) -> list[str]:
    """Resolve a complete graph without installing or freezing ambient packages."""
    with tempfile.TemporaryDirectory(prefix="aetherra-lock-") as directory:
        report = Path(directory) / "report.json"
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--dry-run",
            "--ignore-installed",
            "--disable-pip-version-check",
            "--report",
            str(report),
        ]
        for path in requirements:
            command.extend(["-r", path])
        for path in constraints:
            command.extend(["-c", path])
        subprocess.run(command, check=True)
        data = json.loads(report.read_text(encoding="utf-8"))
    if data.get("version") != "1" or not data.get("install"):
        raise ValueError("pip did not report a complete dependency resolution")
    pins = {}
    for item in data["install"]:
        if item.get("is_direct"):
            raise ValueError("direct URLs cannot be represented by this exact-pin lock")
        metadata = item["metadata"]
        name, version = metadata["name"], metadata["version"]
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9.!+_-]*", version
        ):
            raise ValueError("pip returned an invalid package name or version")
        key = re.sub(r"[-_.]+", "-", name).lower()
        if key in pins:
            raise ValueError("pip returned a duplicate package")
        pins[key] = f"{name}=={version}"
    return [pins[key] for key in sorted(pins)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default="requirements.lock")
    ap.add_argument("-r", "--requirements", action="append", default=[])
    ap.add_argument("-c", "--constraint", action="append", default=[])
    args = ap.parse_args()

    if args.constraint and not args.requirements:
        ap.error("--constraint requires explicit --requirements")
    if args.requirements:
        try:
            pins = resolve(args.requirements, args.constraint)
        except (
            OSError,
            ValueError,
            KeyError,
            TypeError,
            subprocess.CalledProcessError,
        ) as exc:
            print(f"[LOCK][FAIL] resolution failed: {exc}")
            return 1
        header = [
            "# Resolved from explicit requirements; excludes unrelated installed packages.",
            f"# Target: {sys.platform}, Python {platform.python_version()}, {platform.machine()}.",
            "# Inputs: " + ", ".join(args.requirements),
            "# Constraints: " + (", ".join(args.constraint) or "none"),
        ]
        Path(args.output).write_text(
            "\n".join([*header, *pins]) + "\n", encoding="utf-8"
        )
        print(f"[LOCK] Wrote {args.output} ({len(pins)} resolved entries)")
        return 0

    cmd = [sys.executable, "-m", "pip", "freeze"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    out, _ = proc.communicate()
    if proc.returncode != 0:
        print("[LOCK][FAIL] pip freeze failed")
        return proc.returncode

    lines = []
    for line in out.splitlines():
        if not line or line.startswith("#"):
            continue
        if line.startswith("-e ") and (
            "aetherra" in line.lower() or line.endswith(".")
        ):
            continue  # skip editable project reference
        lines.append(line)

    lines = sorted(set(lines), key=str.lower)
    Path(args.output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[LOCK] Wrote {args.output} ({len(lines)} entries)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
