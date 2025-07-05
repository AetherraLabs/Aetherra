#!/usr/bin/env python3
"""Fix import paths in test files"""

import glob
import os
import re

# Define replacement patterns
replacements = [
    (r"from src\.aethercode\.ui", "from Lyrixa.ui"),
    (r"from src\.aetherra\.", "from Aetherra."),
    (r"from core\.", "from Aetherra.core."),
    (r"import src\.aethercode\.", "import Lyrixa."),
    (r"import src\.aetherra\.", "import Aetherra."),
    (r"import core\.", "import Aetherra.core."),
    # Fix specific wrong class names
    (r"AetherraChatRouter", "AetherraChatRouter"),
    (r"from launchers\.launch_Lyrixa import", "from launchers.launch_lyrixa import"),
]


def fix_file(filepath):
    """Fix imports in a single file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply all replacements
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)

        # Only write if changes were made
        if content != original_content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Updated {filepath}")
            return True
        else:
            print(f"⚪ No changes needed in {filepath}")
            return False

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False


def main():
    """Fix all test files"""
    print("🔧 Fixing test file imports...")

    # Find all test files
    test_files = []
    for pattern in ["test_*.py", "**/*test_*.py", "**/test_*.py"]:
        test_files.extend(glob.glob(pattern, recursive=True))

    # Remove duplicates
    test_files = list(set(test_files))

    print(f"Found {len(test_files)} test files")

    updated_count = 0
    for test_file in test_files:
        if fix_file(test_file):
            updated_count += 1

    print(f"\n🎉 Updated {updated_count} out of {len(test_files)} test files")


if __name__ == "__main__":
    main()
