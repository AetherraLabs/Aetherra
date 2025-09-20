#!/usr/bin/env python3
"""
Fix duplicate SPDX license blocks in files.

SPDX-License-Identifier: GPL-3.0-or-later
SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""

# Standard library imports
import re
from pathlib import Path


def fix_duplicate_spdx_blocks(file_path: Path) -> bool:
    """Fix duplicate SPDX blocks in a file, keeping only one."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        # Pattern to match SPDX license + copyright blocks (only comment format for duplicates)
        spdx_pattern = r"<!--\s*SPDX-License-Identifier:\s*GPL-3\.0-or-later\s*-->\s*\n<!--\s*SPDX-FileCopyrightText:\s*2025\s+Aetherra\s+Labs\s+and\s+Contributors\s*-->"

        matches = list(re.finditer(spdx_pattern, content, re.MULTILINE | re.IGNORECASE))

        if len(matches) <= 1:
            return False  # No duplicates found

        # Keep only the first occurrence and remove the rest
        for match in reversed(matches[1:]):  # Reverse to preserve indices
            start, end = match.span()
            content = content[:start] + content[end:]

        # Clean up extra newlines that might be left
        content = re.sub(r"\n\n\n+", "\n\n", content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")

    return False


def find_files_with_multiple_spdx(root_dir: Path) -> list[Path]:
    """Find all files with multiple SPDX comment blocks."""
    files_with_duplicates = []

    for file_path in root_dir.rglob("*.md"):
        if any(
            skip in str(file_path) for skip in [".git", "node_modules", "__pycache__"]
        ):
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            # Only count comment format as potential duplicates
            spdx_comment_count = content.count("<!-- SPDX-License-Identifier")

            if spdx_comment_count > 1:
                files_with_duplicates.append(file_path)

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return files_with_duplicates


def main():
    """Fix duplicate SPDX blocks across the project."""
    root_dir = Path(__file__).parent.parent
    print(f"Scanning for duplicate SPDX blocks in: {root_dir}")

    files_with_duplicates = find_files_with_multiple_spdx(root_dir)

    if not files_with_duplicates:
        print("No files with duplicate SPDX blocks found.")
        return

    print(f"Found {len(files_with_duplicates)} files with duplicate SPDX blocks:")

    fixed_count = 0
    for file_path in files_with_duplicates:
        relative_path = file_path.relative_to(root_dir)
        print(f"  Fixing: {relative_path}")

        if fix_duplicate_spdx_blocks(file_path):
            fixed_count += 1

    print(f"\nFixed {fixed_count} files with duplicate SPDX blocks.")


if __name__ == "__main__":
    main()
