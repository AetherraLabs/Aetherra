#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Validate license_overrides.yml structure & SPDX expressions (basic heuristics).

Checks:
  * File parses as mapping of package -> license string
  * SPDX expression contains only allowed tokens (A-Z0-9-.+ and operators OR/AND/ WITH / parentheses)
  * Reject obviously invalid characters

Exit codes:
  0 success
  1 validation failure
  2 usage / parse error
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

TOKEN_RE = re.compile(r"^[A-Za-z0-9.+-]+$")
ALLOWED_OPS = {"OR", "AND", "WITH", "(", ")"}

# Canonical SPDX license ids (subset; full list can be fetched in future). Keeping a
# curated minimal set drastically reduces false positives while avoiding a large
# maintenance burden. Additional IDs can be appended as encountered.
CANONICAL_IDS = {
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "GPL-2.0-only",
    "GPL-2.0-or-later",
    "GPL-3.0-only",
    "GPL-3.0-or-later",
    "LGPL-2.1-only",
    "LGPL-2.1-or-later",
    "LGPL-3.0-only",
    "LGPL-3.0-or-later",
    "MPL-2.0",
    "CDDL-1.0",
    "EPL-2.0",
    "AGPL-3.0-only",
    "AGPL-3.0-or-later",
    "BSD-4-Clause",
    "Unlicense",
    "CC0-1.0",
    "ISC",
    "Zlib",
    "PSF-2.0",
}


def tokenize(expr: str) -> list[str]:
    # split on spaces and parentheses while keeping parens
    out: list[str] = []
    buf = ""
    for ch in expr:
        if ch in "()":
            if buf:
                out.append(buf)
                buf = ""
            out.append(ch)
        elif ch.isspace():
            if buf:
                out.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        out.append(buf)
    return out


def _expr_tokens(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in ALLOWED_OPS]


def valid_spdx(expr: str) -> bool:
    tokens = tokenize(expr)
    if not tokens:
        return False
    raw_ids = _expr_tokens(tokens)
    for t in tokens:
        if t in ALLOWED_OPS:
            continue
        if not TOKEN_RE.match(t):
            return False
    # At least one canonical ID must appear; every non-operator token must either be
    # a canonical ID or pass heuristic (legacy broad token) when env ALLOW_NON_CANONICAL=1
    allow_non = os.environ.get("LICENSE_ALLOW_NON_CANONICAL", "0") == "1"
    has_canon = any(t in CANONICAL_IDS for t in raw_ids)
    if not has_canon:
        return False
    if not allow_non and any(t not in CANONICAL_IDS for t in raw_ids):
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="license_overrides.yml")
    ap.add_argument(
        "--dump-ids", action="store_true", help="Print canonical SPDX IDs JSON and exit"
    )
    ap.add_argument(
        "--spdx-file",
        help="Path to JSON file containing additional SPDX IDs (array of strings)",
    )
    args = ap.parse_args()
    if args.dump_ids:
        extra = []
        if args.spdx_file and Path(args.spdx_file).is_file():
            try:
                extra = json.loads(Path(args.spdx_file).read_text(encoding="utf-8"))
            except Exception:
                extra = []
        merged = sorted(
            set(CANONICAL_IDS).union({e for e in extra if isinstance(e, str)})
        )
        print(json.dumps(merged, indent=2))
        return 0
    # Merge external list if provided for validation path
    if args.spdx_file and Path(args.spdx_file).is_file():
        try:
            extra = json.loads(Path(args.spdx_file).read_text(encoding="utf-8"))
            if isinstance(extra, list):
                for e in extra:
                    if isinstance(e, str) and e.strip():
                        CANONICAL_IDS.add(e.strip())
        except Exception:
            pass
    if yaml is None:
        print("[VALIDATE][FAIL] PyYAML not installed", file=sys.stderr)
        return 2
    p = Path(args.file)
    if not p.exists():
        print(f"[VALIDATE][FAIL] Missing {p}")
        return 2
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception as e:
        print(f"[VALIDATE][FAIL] Parse error: {e}")
        return 2
    if not isinstance(data, dict):
        print("[VALIDATE][FAIL] Top-level must be mapping of package->license")
        return 1
    failures = 0
    for pkg, expr in data.items():
        if not isinstance(expr, str):
            print(f"[VALIDATE][FAIL] {pkg}: value not string")
            failures += 1
            continue
        if not valid_spdx(expr):
            print(f"[VALIDATE][FAIL] {pkg}: invalid expression '{expr}'")
            failures += 1
    if failures:
        print(f"[VALIDATE] Completed with {failures} failures")
        return 1
    print(f"[VALIDATE] {p} OK ({len(data)} entries)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
