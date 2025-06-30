#!/usr/bin/env python3
"""
Test File Duplicate Cleanup

Identifies and cleans up duplicate test files between tests/ and tests/unit/
directories, keeping the version with actual content.
"""

import os
import shutil
from pathlib import Path


def analyze_test_duplicates():
    """Find and analyze test file duplicates."""
    tests_dir = Path("tests")
    unit_dir = Path("tests/unit")

    if not tests_dir.exists() or not unit_dir.exists():
        print("❌ Required test directories not found")
        return

    duplicates = []

    # Find all test files in tests/ directory
    for test_file in tests_dir.glob("test_*.py"):
        unit_equivalent = unit_dir / test_file.name

        if unit_equivalent.exists():
            # Get file sizes
            main_size = test_file.stat().st_size
            unit_size = unit_equivalent.stat().st_size

            duplicates.append(
                {
                    "main_file": test_file,
                    "unit_file": unit_equivalent,
                    "main_size": main_size,
                    "unit_size": unit_size,
                    "recommendation": "move_to_unit" if main_size > unit_size else "keep_main",
                }
            )

    return duplicates


def show_duplicate_analysis(duplicates):
    """Display analysis of duplicate test files."""
    print("🧪 TEST FILE DUPLICATE ANALYSIS")
    print("=" * 50)

    if not duplicates:
        print("✅ No test file duplicates found!")
        return

    empty_unit_files = 0
    content_conflicts = 0

    for dup in duplicates:
        main_size = dup["main_size"]
        unit_size = dup["unit_size"]

        print(f"\n📄 {dup['main_file'].name}")
        print(f"   tests/{dup['main_file'].name}: {main_size} bytes")
        print(f"   tests/unit/{dup['unit_file'].name}: {unit_size} bytes")

        if unit_size == 0 and main_size > 0:
            print("   ✅ RECOMMENDATION: Move main to unit (unit is empty)")
            empty_unit_files += 1
        elif main_size == 0 and unit_size > 0:
            print("   ✅ RECOMMENDATION: Delete empty main file")
        elif main_size > 0 and unit_size > 0:
            print("   ⚠️  MANUAL REVIEW: Both files have content")
            content_conflicts += 1
        else:
            print("   ℹ️  Both files are empty")

    print("\n📊 SUMMARY:")
    print(f"   Total duplicates: {len(duplicates)}")
    print(f"   Empty unit files: {empty_unit_files}")
    print(f"   Content conflicts: {content_conflicts}")

    return duplicates


def execute_test_cleanup(duplicates, execute=False):
    """Execute the test cleanup plan."""
    if not execute:
        print("\n💡 Add --execute flag to perform cleanup")
        return

    print("\n🧹 EXECUTING TEST CLEANUP...")

    moved_count = 0
    deleted_count = 0

    for dup in duplicates:
        main_file = dup["main_file"]
        unit_file = dup["unit_file"]
        main_size = dup["main_size"]
        unit_size = dup["unit_size"]

        if unit_size == 0 and main_size > 0:
            # Move main to unit, delete main
            shutil.copy2(str(main_file), str(unit_file))
            os.remove(str(main_file))
            print(f"✅ Moved {main_file.name}: tests/ → tests/unit/")
            moved_count += 1

        elif main_size == 0 and unit_size > 0:
            # Delete empty main file
            os.remove(str(main_file))
            print(f"❌ Deleted empty file: {main_file}")
            deleted_count += 1

        elif main_size == 0 and unit_size == 0:
            # Delete both empty files
            os.remove(str(main_file))
            os.remove(str(unit_file))
            print(f"❌ Deleted both empty files: {main_file.name}")
            deleted_count += 2

    print("\n📊 CLEANUP COMPLETE:")
    print(f"   Files moved to unit/: {moved_count}")
    print(f"   Empty files deleted: {deleted_count}")


def main():
    import sys

    execute = "--execute" in sys.argv

    print("🔍 Analyzing test file duplicates...")
    duplicates = analyze_test_duplicates()

    if duplicates:
        show_duplicate_analysis(duplicates)
        execute_test_cleanup(duplicates, execute)
    else:
        print("✅ No test file duplicates found!")


if __name__ == "__main__":
    main()
