#!/usr/bin/env python3
"""
🚀 Simple File Counter and Basic Cleanup
=======================================

Ultra-lightweight script to count files and do basic cleanup.
No complex analysis - just identify obvious unused files.
"""

import os
import time


def count_files():
    """Just count Python files quickly"""
    print("🔍 Counting Python files...")

    total_files = 0
    exclude_patterns = [
        "unused",
        "backup",
        "legacy",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
    ]

    start_time = time.time()

    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not any(pattern in d.lower() for pattern in exclude_patterns)
        ]

        for file in files:
            if file.endswith(".py"):
                total_files += 1
                if total_files % 500 == 0:
                    elapsed = time.time() - start_time
                    print(f"   Found {total_files} files so far... ({elapsed:.1f}s)")

    elapsed = time.time() - start_time
    print(f"✅ Total Python files: {total_files} (took {elapsed:.1f}s)")
    return total_files


def find_obvious_unused():
    """Find obviously unused files by name patterns"""
    print("\n🗑️ Finding obviously unused files...")

    unused_patterns = [
        "test_",
        "_test",
        "demo_",
        "_demo",
        "example_",
        "backup_",
        "_backup",
        "old_",
        "_old",
        "legacy_",
        "temp_",
        "_temp",
        "tmp_",
        "_tmp",
    ]

    unused_files = []
    exclude_dirs = {
        "unused",
        "backup",
        "legacy",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "Scripts",
    }

    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_lower = file.lower()
                if any(pattern in file_lower for pattern in unused_patterns):
                    file_path = os.path.join(root, file)
                    unused_files.append(file_path)

    print(f"Found {len(unused_files)} obviously unused files")

    # Show first 20
    for i, file_path in enumerate(unused_files[:20]):
        print(f"   {i + 1}. {file_path}")

    if len(unused_files) > 20:
        print(f"   ... and {len(unused_files) - 20} more")

    return unused_files


def find_duplicate_files():
    """Find files with very similar names (likely duplicates)"""
    print("\n🔄 Finding potential duplicate files...")

    files_by_base = {}

    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if "unused" not in d.lower()
            and "__pycache__" not in d.lower()
            and ".venv" not in d.lower()
        ]

        for file in files:
            if file.endswith(".py"):
                # Get base name without common suffixes
                base_name = file.replace(".py", "")
                for suffix in ["_copy", "_backup", "_old", "_new", "_2", "_test"]:
                    if base_name.endswith(suffix):
                        base_name = base_name[: -len(suffix)]
                        break

                if base_name not in files_by_base:
                    files_by_base[base_name] = []

                files_by_base[base_name].append(os.path.join(root, file))

    duplicates = []
    for base_name, file_list in files_by_base.items():
        if len(file_list) > 1:
            # Sort by path length (keep shortest)
            file_list.sort(key=len)
            duplicates.extend(file_list[1:])  # All except the first (shortest)

    print(f"Found {len(duplicates)} potential duplicate files")
    for i, dup in enumerate(duplicates[:10]):
        print(f"   {i + 1}. {dup}")

    if len(duplicates) > 10:
        print(f"   ... and {len(duplicates) - 10} more")

    return duplicates


def create_simple_cleanup_script(unused_files, duplicates):
    """Create a simple script to move files"""

    all_files_to_move = list(set(unused_files + duplicates))

    script_content = '''#!/usr/bin/env python3
"""
🧹 Simple Cleanup Script
Generated automatically
"""

import os
import shutil
from pathlib import Path

def move_files():
    """Move files to unused directory"""

    files_to_move = [
'''

    for file_path in sorted(all_files_to_move):
        # Make path relative and escape quotes
        rel_path = os.path.relpath(file_path).replace("\\", "/")
        script_content += f'        "{rel_path}",\n'

    script_content += """    ]

    unused_dir = Path("unused_simple")
    unused_dir.mkdir(exist_ok=True)

    moved = 0
    errors = 0

    for file_path in files_to_move:
        if os.path.exists(file_path):
            try:
                dest_path = unused_dir / file_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(file_path, str(dest_path))
                print(f"✅ Moved: {file_path}")
                moved += 1
            except Exception as e:
                print(f"❌ Error moving {file_path}: {e}")
                errors += 1
        else:
            print(f"⚠️  File not found: {file_path}")

    print(f"\\n🎉 Moved {moved} files, {errors} errors")

if __name__ == "__main__":
    print("🧹 Starting simple cleanup...")
    move_files()
"""

    with open("scripts/simple_cleanup.py", "w", encoding="utf-8") as f:
        f.write(script_content)

    print(f"\n✅ Created cleanup script for {len(all_files_to_move)} files")
    print("📝 Run: py scripts/simple_cleanup.py")


def main():
    """Main function"""
    print("🚀 Simple Aetherra File Audit")
    print("=" * 40)

    # Step 1: Count files
    total_files = count_files()

    # Step 2: Find obvious unused files
    unused_files = find_obvious_unused()

    # Step 3: Find duplicates
    duplicates = find_duplicate_files()

    # Step 4: Create cleanup script
    create_simple_cleanup_script(unused_files, duplicates)

    print("\n" + "=" * 40)
    print("📊 SUMMARY:")
    print(f"   Total Python files: {total_files}")
    print(f"   Obviously unused: {len(unused_files)}")
    print(f"   Potential duplicates: {len(duplicates)}")
    print(f"   Ready to move: {len(set(unused_files + duplicates))}")

    print("\n🎯 Next steps:")
    print("1. Review the files listed above")
    print("2. Run: py scripts/simple_cleanup.py")
    print("3. Check the results in unused_simple/ directory")


if __name__ == "__main__":
    main()
