#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Packaging smoke test.

Build wheel, install into isolated ephemeral venv, exercise imports and
CLI entry points to catch obvious packaging errors *before* publishing.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"


def run(
    cmd: list[str], env=None, check=True, cwd: Path | None = None
) -> subprocess.CompletedProcess:
    p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    if check and p.returncode != 0:
        print("[PKG][ERR]", " ".join(cmd))
        print(p.stdout)
        print(p.stderr)
        raise SystemExit(p.returncode)
    return p


def build_wheel() -> Path:
    DIST.mkdir(exist_ok=True)
    cmd = [sys.executable, "-m", "pip", "wheel", ".", "-w", str(DIST), "--no-deps"]
    print("[PKG] Building wheel:", " ".join(cmd))
    run(cmd)
    wheels = sorted(DIST.glob("aetherra-*.whl"))
    if not wheels:
        print("[PKG][FAIL] No wheel produced")
        raise SystemExit(1)
    print(f"[PKG] Wheel: {wheels[-1].name}")
    return wheels[-1]


def create_venv(tmp: Path) -> Path:
    venv_dir = tmp / "venv"
    run([sys.executable, "-m", "venv", str(venv_dir)])
    py = (
        venv_dir
        / ("Scripts" if os.name == "nt" else "bin")
        / ("python.exe" if os.name == "nt" else "python")
    )
    return py


def install_and_probe(py: Path, wheel: Path):
    run([str(py), "-m", "pip", "install", str(wheel)])
    # Basic imports
    run([str(py), "-c", "import aetherra, Aetherra.cli; print('imports_ok')"])
    # Console scripts (entry points) help output
    scripts_dir = py.parent
    aetherra_cmd = scripts_dir / ("aetherra.exe" if os.name == "nt" else "aetherra")
    lyrixa_cmd = scripts_dir / ("lyrixa.exe" if os.name == "nt" else "lyrixa")
    run([str(aetherra_cmd), "--help"], check=True)
    run([str(lyrixa_cmd), "--help"], check=True)


def main() -> int:
    wheel = build_wheel()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        py = create_venv(tmp)
        install_and_probe(py, wheel)
    print("[PKG] Smoke test PASSED")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
