#!/usr/bin/env python3
"""
Fix Enhanced Lyrixa Import Paths
=================================

Updates all files to use the correct import path:
OLD: from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow
NEW: from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow
"""

import os
import re
from pathlib import Path


def fix_import_paths():
    """Fix all enhanced_lyrixa import paths."""
    print("🔧 Fixing Enhanced Lyrixa Import Paths")
    print("=" * 50)

    # Define the search and replace patterns
    old_pattern = r"from\s+src\.aetherra\.ui\.enhanced_lyrixa\s+import"
    new_replacement = "from lyrixa.gui.enhanced_lyrixa import"

    # Get all Python files in the project (excluding some directories)
    project_root = Path(__file__).parent
    exclude_dirs = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        "archive",
        "backups",
    }

    files_updated = 0
    total_replacements = 0

    for file_path in project_root.rglob("*.py"):
        if any(exclude_dir in file_path.parts for exclude_dir in exclude_dirs):
            continue

        try:
            # Read the file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if it contains the old import
            if re.search(old_pattern, content):
                print(f"📝 Updating: {file_path.relative_to(project_root)}")

                # Replace the import
                new_content = re.sub(old_pattern, new_replacement, content)

                # Count replacements
                replacements = len(re.findall(old_pattern, content))
                total_replacements += replacements

                # Write back the file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                files_updated += 1
                print(f"   ✅ {replacements} import(s) updated")

        except Exception as e:
            print(f"   ❌ Error updating {file_path}: {e}")

    print(f"\n📊 SUMMARY:")
    print(f"   Files updated: {files_updated}")
    print(f"   Total replacements: {total_replacements}")

    if files_updated > 0:
        print(f"\n✅ Import paths successfully updated!")
        print(f"   OLD: from lyrixa.gui.enhanced_lyrixa import")
        print(f"   NEW: from lyrixa.gui.enhanced_lyrixa import")
    else:
        print(f"\n✅ No files needed updating!")


if __name__ == "__main__":
    fix_import_paths()
