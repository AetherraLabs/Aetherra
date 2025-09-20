#!/usr/bin/env python3
"""Normalize CHANGELOG.md formatting after semantic-release.

Features:
- Collapse duplicate version headers if any (rare edge case)
- Ensure single blank line between sections
- Trim trailing whitespace
"""

from __future__ import annotations

# Standard library imports
import re
from pathlib import Path

CHANGELOG = Path("CHANGELOG.md")

HEADER_RE = re.compile(r"^## \[(?P<ver>[^\]]+)\]", re.MULTILINE)


def load() -> str:
    if not CHANGELOG.exists():
        return ""
    return CHANGELOG.read_text(encoding="utf-8")


def collapse_duplicate_versions(text: str) -> str:
    seen = set()
    out_lines = []
    pending_block = []
    current_ver = None
    for line in text.splitlines():
        m = HEADER_RE.match(line)
        if m:
            ver = m.group("ver")
            if current_ver is not None and pending_block:
                if current_ver not in seen:
                    out_lines.extend(pending_block)
                    seen.add(current_ver)
                # else drop duplicate
                pending_block = []
            current_ver = ver
            pending_block = [line]
        else:
            if pending_block is not None:
                pending_block.append(line)
    # flush last
    if current_ver is not None and pending_block:
        if current_ver not in seen:
            out_lines.extend(pending_block)
    return "\n".join(out_lines)


def normalize_blank_lines(text: str) -> str:
    # Ensure max one blank line between non-empty lines
    cleaned = []
    blank = 0
    for line in text.splitlines():
        if line.strip():
            blank = 0
            cleaned.append(line.rstrip())
        else:
            blank += 1
            if blank <= 1:
                cleaned.append("")
    return "\n".join(cleaned).strip() + "\n"


def main():
    raw = load()
    if not raw:
        return
    step1 = collapse_duplicate_versions(raw)
    step2 = normalize_blank_lines(step1)
    if step2 != raw:
        CHANGELOG.write_text(step2, encoding="utf-8")
        print("Changelog normalized")
    else:
        print("Changelog already normalized")


if __name__ == "__main__":
    main()
