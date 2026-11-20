#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""Run the CI-friendly alpha boot validation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _main() -> int:
    from Aetherra.alpha_boot_validation import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
