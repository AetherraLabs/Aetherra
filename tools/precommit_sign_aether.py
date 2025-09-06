#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
pre-commit helper: sign changed .aether files passed as args.

This wraps tools/sign_aether.py and only targets files with .aether extension.
It is safe and idempotent. If no .aether files are in the staged set, exits 0.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    aethers = [a for a in argv if a.lower().endswith(".aether") and Path(a).exists()]
    if not aethers:
        return 0
    cmd = [sys.executable, str(Path("tools") / "sign_aether.py"), *aethers]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
