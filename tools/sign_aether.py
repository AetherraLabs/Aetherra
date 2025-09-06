#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Sign .aether scripts in-place by embedding an HMAC-SHA256 header as first line.

Usage:
  python tools/sign_aether.py <file1.aether> [<file2.aether> ...]

Notes:
  - Uses Aetherra.security.script_signing.embed_signature
  - Skips empty files and prints a note
  - Idempotent: re-computes signature over the body; any existing header is replaced
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

from Aetherra.security.script_signing import embed_signature  # type: ignore


def sign_file(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    # Allow signing empty files; header-only signature is valid and verifiable
    signed = embed_signature(text)
    path.write_text(signed, encoding="utf-8")
    return f"OK signed: {path}"


def main(argv: Iterable[str]) -> int:
    args = list(argv)
    if not args:
        print("Usage: python tools/sign_aether.py <file1.aether> [<file2.aether> ...]")
        return 2
    status = 0
    for a in args:
        p = Path(a)
        if not p.exists():
            print(f"NOT FOUND: {p}")
            status = 1
            continue
        try:
            print(sign_file(p))
        except Exception as e:
            print(f"ERROR signing {p}: {e}")
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
