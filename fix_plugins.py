#!/usr/bin/env python3
"""
Quick fix script for plugin syntax errors
"""

import os
import re
from pathlib import Path


def fix_multiline_strings(file_path):
    """Fix multiline string literals in plugin files"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find and fix multiline ai_description strings
        # Pattern: ai_description="text,\n    more text,\n    and more text.",
        pattern = r'ai_description="([^"]*),\s*\n\s*([^"]*),\s*\n\s*([^"]*)\."'

        def replace_multiline(match):
            part1 = match.group(1).strip()
            part2 = match.group(2).strip()
            part3 = match.group(3).strip()
            return f'ai_description="{part1}, {part2}, {part3}."'

        content = re.sub(pattern, replace_multiline, content)

        # Also fix 4-part multiline strings
        pattern4 = r'ai_description="([^"]*),\s*\n\s*([^"]*),\s*\n\s*([^"]*),\s*\n\s*([^"]*)\."'

        def replace_multiline4(match):
            parts = [match.group(i).strip() for i in range(1, 5)]
            return f'ai_description="{", ".join(parts)}."'

        content = re.sub(pattern4, replace_multiline4, content)

        # Fix f-strings with placeholders that don't have placeholders
        content = re.sub(
            r'f"([^"]*)"',
            lambda m: f'"{m.group(1)}"' if "{" not in m.group(1) else m.group(0),
            content,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Fixed: {file_path}")
        return True

    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix all plugin files"""
    print("🔧 Fixing plugin syntax errors...")

    # Plugin directories to check
    plugin_dirs = [Path("src/aetherra/plugins"), Path("Aetherra/plugins")]

    fixed_count = 0
    error_count = 0

    for plugin_dir in plugin_dirs:
        if not plugin_dir.exists():
            continue

        print(f"\n📁 Checking {plugin_dir}")

        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name == "__init__.py":
                continue

            if fix_multiline_strings(plugin_file):
                fixed_count += 1
            else:
                error_count += 1

    print(f"\n🎉 Summary:")
    print(f"✅ Fixed: {fixed_count} files")
    print(f"❌ Errors: {error_count} files")


if __name__ == "__main__":
    main()
