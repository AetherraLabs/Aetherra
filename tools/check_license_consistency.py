#!/usr/bin/env python3
"""
Quick license consistency checker.
- Verifies root LICENSE exists and mentions GPL-3.0
- Ensures pyproject.toml files declare GPL-3.0-or-later
- Scans README files for SPDX or license badges

Exits non-zero on mismatch unless --warn is passed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GPL_PAT = re.compile(r"GPL\s*-?3(\.0)?(\s*or\s*later)?", re.IGNORECASE)
PYPROJ_LICENSE_PAT = re.compile(
    r"license\s*=\s*\{\s*text\s*=\s*['\"]GPL-3.0-or-later['\"]\s*\}"
)
SPDX_PAT = re.compile(r"SPDX-License-Identifier:\s*GPL-3.0-", re.IGNORECASE)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true", help="Warn only (exit 0)")
    args = ap.parse_args()

    errors: list[str] = []

    # 1) Root LICENSE
    lic = ROOT / "LICENSE"
    if not lic.exists():
        errors.append("Missing root LICENSE file")
    else:
        try:
            txt = lic.read_text(encoding="utf-8", errors="ignore")
            if not GPL_PAT.search(txt):
                errors.append("Root LICENSE does not mention GPL-3.0")
        except Exception as e:
            errors.append(f"Failed to read LICENSE: {e}")

    # 2) pyproject.toml files
    for pyproj in [ROOT / "pyproject.toml", ROOT / "Aetherra" / "pyproject.toml"]:
        if pyproj.exists():
            txt = pyproj.read_text(encoding="utf-8", errors="ignore")
            if not PYPROJ_LICENSE_PAT.search(txt):
                errors.append(f"{pyproj} license must be 'GPL-3.0-or-later' text form")

    # 3) README files
    for readme in [ROOT / "README.md", ROOT / "Aetherra" / "README.md"]:
        if readme.exists():
            txt = readme.read_text(encoding="utf-8", errors="ignore")
            if not (SPDX_PAT.search(txt) or GPL_PAT.search(txt)):
                errors.append(f"{readme} missing SPDX or GPL mention")

    if errors:
        print("License consistency issues detected:\n- " + "\n- ".join(errors))
        return 0 if args.warn else 1

    print("License consistency: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
