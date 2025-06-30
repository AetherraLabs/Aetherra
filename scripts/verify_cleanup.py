#!/usr/bin/env python3
"""
NeuroCode Duplicate Cleanup Verification

Verifies that the duplicate cleanup was successful and the project
structure is now clean and organized.
"""

from pathlib import Path


def verify_cleanup():
    """Verify the cleanup was successful."""
    print("🔍 NeuroCode Duplicate Cleanup Verification")
    print("=" * 50)

    # Check website files are only in website/
    website_files = ["index.html", "styles.css", "script.js"]
    print("\n🌐 Website Files:")
    for file in website_files:
        root_exists = Path(file).exists()
        website_exists = Path(f"website/{file}").exists()

        if not root_exists and website_exists:
            print(f"   ✅ {file}: Only in website/ (correct)")
        elif root_exists and website_exists:
            print(f"   ❌ {file}: Duplicate in root and website/")
        elif root_exists and not website_exists:
            print(f"   ⚠️  {file}: Only in root (review needed)")
        else:
            print(f"   ❌ {file}: Missing entirely")

    # Check test files are only in tests/unit/
    print("\n🧪 Test Files:")
    tests_count = len(list(Path("tests").glob("test_*.py"))) if Path("tests").exists() else 0
    unit_count = (
        len(list(Path("tests/unit").glob("test_*.py"))) if Path("tests/unit").exists() else 0
    )

    print(f"   tests/ directory: {tests_count} test files")
    print(f"   tests/unit/ directory: {unit_count} test files")

    if tests_count == 0 and unit_count > 0:
        print("   ✅ All test files properly consolidated in tests/unit/")
    elif tests_count > 0:
        print(f"   ⚠️  {tests_count} test files still in tests/ (review needed)")

    # Check empty scripts are archived
    print("\n📜 Empty Scripts:")
    empty_scripts = [
        "scripts/parse_debug.py",
        "scripts/parse_debug2.py",
        "scripts/parse_debug3.py",
        "scripts/parse_debug4.py",
        "scripts/tokenize_debug.py",
        "scripts/quick_debug_test.py",
        "scripts/check_qt.py",
    ]

    remaining_empty = []
    for script in empty_scripts:
        if Path(script).exists():
            remaining_empty.append(script)

    if not remaining_empty:
        print("   ✅ All empty scripts removed/archived")
    else:
        print(f"   ⚠️  {len(remaining_empty)} empty scripts still present")

    # Check archive structure
    print("\n📦 Archive Structure:")
    archive_dirs = ["archive/status_files", "archive/duplicates", "archive/empty_scripts"]
    for dir_path in archive_dirs:
        archive_dir = Path(dir_path)
        if archive_dir.exists():
            file_count = len(list(archive_dir.iterdir()))
            print(f"   ✅ {dir_path}: {file_count} files archived")
        else:
            print(f"   ❌ {dir_path}: Directory missing")

    # Overall status
    print("\n🎯 Overall Status:")
    total_issues = 0

    # Count any remaining duplicates
    root_website_files = sum(1 for f in website_files if Path(f).exists())
    if root_website_files > 0:
        total_issues += root_website_files

    if tests_count > 0:
        total_issues += tests_count

    if remaining_empty:
        total_issues += len(remaining_empty)

    if total_issues == 0:
        print("   🎉 CLEANUP SUCCESSFUL! No duplicate files detected.")
        print("   ✅ Project structure is clean and organized.")
    else:
        print(f"   ⚠️  {total_issues} potential issues found (see above)")

    return total_issues == 0


if __name__ == "__main__":
    success = verify_cleanup()
    if success:
        print("\n🏆 Duplicate cleanup verification PASSED!")
    else:
        print("\n⚠️  Duplicate cleanup verification needs attention.")
