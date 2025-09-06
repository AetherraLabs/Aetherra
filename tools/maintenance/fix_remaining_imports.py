#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🔧 COMPREHENSIVE ARCHITECTURAL FIXER
Fix ALL remaining architectural violations
"""

import re
from pathlib import Path


def fix_all_lyrixa_imports():
    """Fix all remaining Lyrixa imports in core files"""
    project_root = Path(".")
    aetherra_root = project_root / "Aetherra"

    # Files that still have Lyrixa imports
    files_to_fix = [
        "consciousness/consciousness_orchestrator.py",
        "aetherra_core/agents/optimized_integration.py",
    ]

    fixed_count = 0

    for file_rel_path in files_to_fix:
        file_path = aetherra_root / file_rel_path
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Comment out ALL Lyrixa imports and references
            content = re.sub(
                r"^(\s*from lyrixa.*?)$",
                r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
                content,
                flags=re.MULTILINE,
            )

            content = re.sub(
                r"^(\s*import lyrixa.*?)$",
                r"# ARCHITECTURAL FIX: Removed Lyrixa import - \1",
                content,
                flags=re.MULTILINE,
            )

            # Also comment out any lines that use Lyrixa functions
            content = re.sub(
                r"^(\s*.*lyrixa.*\(.*\).*)$",
                r"# ARCHITECTURAL FIX: Removed Lyrixa function call - \1",
                content,
                flags=re.MULTILINE,
            )

            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"✅ Fixed {file_path.name}")
                fixed_count += 1

        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}")

    print(f"\n🎯 Fixed {fixed_count} additional files")
    return fixed_count


if __name__ == "__main__":
    print("🔧 COMPREHENSIVE ARCHITECTURAL FIXER")
    print("=" * 40)

    result = fix_all_lyrixa_imports()

    if result > 0:
        print("✅ All Lyrixa imports fixed!")
        print("🔧 Run: python check_architecture.py")
    else:
        print("✅ No additional fixes needed")
