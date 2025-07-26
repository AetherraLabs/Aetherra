#!/usr/bin/env python3
"""
🧹 Conservative Aetherra Cleanup
==============================

Safely move only obviously unused files while preserving project structure.
"""

import os
import shutil
from pathlib import Path


def conservative_cleanup():
    """Move only obviously safe-to-move files"""

    # Files that are definitely safe to move
    safe_patterns = [
        "demo_",
        "_demo",
        "test_",
        "_test",
        "example_",
        "_example",
        "backup_",
        "_backup",
        "old_",
        "_old",
        "legacy_",
        "_legacy",
        "temp_",
        "_temp",
        "tmp_",
        "_tmp",
    ]

    # Critical files to NEVER move
    never_move = {
        "__init__.py",
        "setup.py",
        "main.py",
        "app.py",
        "launcher.py",
        "aetherra_launcher.py",
        "aetherra_launcher_new.py",
        "server.py",
        "run.py",
        "__main__.py",
    }

    # Critical directories to avoid
    critical_dirs = {"scripts", ".github", "requirements", "src", "core"}

    files_to_move = []

    print("🔍 Finding safe files to move...")

    for root, dirs, files in os.walk("."):
        # Skip critical and backup directories
        dirs[:] = [
            d
            for d in dirs
            if not any(
                skip in d.lower()
                for skip in [
                    "unused",
                    "backup",
                    "legacy",
                    "__pycache__",
                    ".git",
                    ".venv",
                    "scripts",
                ]
            )
        ]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_lower = file.lower()

                # Skip critical files
                if file in never_move:
                    continue

                # Skip if in critical directory
                if any(critical_dir in root.lower() for critical_dir in critical_dirs):
                    continue

                # Only move files with safe patterns
                if any(pattern in file_lower for pattern in safe_patterns):
                    files_to_move.append(file_path)

    print(f"Found {len(files_to_move)} safe files to move")

    # Show some examples
    print("\n📄 Examples of files to move:")
    for i, file_path in enumerate(files_to_move[:20]):
        print(f"   {i + 1}. {file_path}")

    if len(files_to_move) > 20:
        print(f"   ... and {len(files_to_move) - 20} more")

    return files_to_move


def execute_cleanup(files_to_move, dry_run=True):
    """Execute the cleanup"""

    if dry_run:
        print(f"\n[DRY RUN] Would move {len(files_to_move)} files")
        return

    unused_dir = Path("unused_conservative")
    unused_dir.mkdir(exist_ok=True)

    moved = 0
    errors = 0

    print(f"\n🧹 Moving {len(files_to_move)} files...")

    for file_path in files_to_move:
        if os.path.exists(file_path):
            try:
                # Create relative path in unused directory
                rel_path = os.path.relpath(file_path)
                dest_path = unused_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                shutil.move(file_path, str(dest_path))
                print(f"✅ Moved: {rel_path}")
                moved += 1

            except Exception as e:
                print(f"❌ Error moving {file_path}: {e}")
                errors += 1
        else:
            print(f"⚠️  File not found: {file_path}")

    print("\n🎉 Cleanup complete!")
    print(f"   Moved: {moved} files")
    print(f"   Errors: {errors}")
    print(f"   Files saved to: {unused_dir}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Conservative Aetherra Cleanup")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually move files (default is dry run)",
    )

    args = parser.parse_args()

    print("🧹 Conservative Aetherra Cleanup")
    print("=" * 40)

    # Find safe files
    files_to_move = conservative_cleanup()

    # Execute cleanup
    execute_cleanup(files_to_move, dry_run=not args.execute)

    if not args.execute:
        print("\n🎯 To execute the cleanup:")
        print("   py scripts/conservative_cleanup.py --execute")
    else:
        print("\n✅ Files moved to unused_conservative/")
        print("   Review the results and commit if satisfied")


if __name__ == "__main__":
    main()
