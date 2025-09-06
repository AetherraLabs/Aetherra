#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""Verify README version badge matches declared version.

Heuristics:
 - Extract version from README 'Version: **X**' line OR shield badge URL with /Version-X/
 - Compare against pyproject.toml version if present; else fallback to CHANGELOG latest heading.

Exit codes:
 0 match / soft warn
 1 mismatch
 2 unable to determine expected version
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


def read(path: str) -> str:
    p = Path(path)
    return p.read_text(encoding="utf-8") if p.exists() else ""


README = read("README.md")
pyproj = read("pyproject.toml")
changelog = read("CHANGELOG.md")

badge_version = None
m = re.search(r"Version:\s*\*\*([0-9A-Za-z_.-]+)\*\*", README)
if m:
    badge_version = m.group(1)
else:
    m = re.search(r"Version-([0-9A-Za-z_.-]+)-", README)
    if m:
        badge_version = m.group(1)

project_version = None
m = re.search(r'^version\s*=\s*"([0-9A-Za-z_.-]+)"', pyproj, re.MULTILINE)
if m:
    project_version = m.group(1)
else:
    # CHANGELOG heading like ## [0.1.0-alpha.2]
    m = re.search(r"^##\s*\[?([0-9A-Za-z_.-]+)\]?\s*", changelog, re.MULTILINE)
    if m:
        project_version = m.group(1)

if not badge_version or not project_version:
    print(
        "[VERSION_BADGE][WARN] Could not determine versions badge=%r project=%r"
        % (badge_version, project_version)
    )
    sys.exit(2)

if badge_version == project_version:
    print(f"[VERSION_BADGE] OK badge={badge_version} project={project_version}")
    sys.exit(0)
print(f"[VERSION_BADGE][FAIL] badge={badge_version} project={project_version}")
sys.exit(1)
