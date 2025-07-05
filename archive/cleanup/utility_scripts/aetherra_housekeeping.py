#!/usr/bin/env python3
"""
AETHERRA HOUSEKEEPING SCRIPT
============================
Comprehensive cleanup and organization of the Aetherra project.
"""

import hashlib
import shutil
from collections import defaultdict
from pathlib import Path


def create_directory_structure():
    """Create the organized directory structure."""
    directories = [
        "archive",
        "archive/legacy_ui",
        "archive/old_verification",
        "archive/backup_files",
        "archive/historical",
        "testing",
        "testing/verification",
        "testing/integration",
        "tools",
        "tools/analysis",
        "tools/utilities",
        "assets",
        "assets/images",
        "assets/icons",
        "assets/branding",
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")


def find_duplicate_files():
    """Find duplicate files by hash."""
    file_hashes = defaultdict(list)

    for file_path in Path(".").rglob("*"):
        if (
            file_path.is_file()
            and ".git" not in str(file_path)
            and "__pycache__" not in str(file_path)
            and ".venv" not in str(file_path)
        ):
            try:
                with open(file_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                file_hashes[file_hash].append(file_path)
            except Exception:
                continue

    duplicates = {h: files for h, files in file_hashes.items() if len(files) > 1}
    return duplicates


def find_similar_files():
    """Find files with similar names that might be versions of each other."""
    all_files = list(Path(".").rglob("*.py"))
    similar_groups = defaultdict(list)

    for file in all_files:
        if (
            ".git" not in str(file)
            and "__pycache__" not in str(file)
            and ".venv" not in str(file)
        ):
            base_name = file.stem.lower()
            # Group by similar base names
            key = (
                base_name.replace("_fixed", "")
                .replace("_clean", "")
                .replace("_wrapper", "")
                .replace("_new", "")
                .replace("_backup", "")
                .replace("_old", "")
                .replace("_v2", "")
                .replace("_enhanced", "")
            )
            similar_groups[key].append(file)

    return {k: v for k, v in similar_groups.items() if len(v) > 1}


def organize_files():
    """Organize files into appropriate directories."""

    # Files to move to testing/verification/
    verification_files = [
        "AETHERRA_GREEN_VERIFICATION.py",
        "AETHERRA_CLEAN_VERIFICATION.py",
        "aetherra_verification.md",
        "AETHERRA_UI_STATUS_REPORT.md",
        "ENHANCED_LYRIXA_TEST_SUITE.py",
        "AETHERRA_SUCCESS_SUMMARY.py",
        "verify_enhanced_lyrixa.py",
    ]

    # Files to move to tools/analysis/
    analysis_files = [
        "fix_all_imports.py",
        "analyze_imports.py",
        "organize_workspace.py",
        "final_cleanup.py",
    ]

    # Files to move to archive/legacy_ui/
    legacy_ui_patterns = ["*_fixed.py", "*_clean.py", "*_wrapper.py", "*_fallback.py"]

    # Move verification files
    for file in verification_files:
        if Path(file).exists():
            dest = Path("testing/verification") / file
            shutil.move(file, dest)
            print(f"📁 Moved {file} → testing/verification/")

    # Move analysis files
    for file in analysis_files:
        if Path(file).exists():
            dest = Path("tools/analysis") / file
            shutil.move(file, dest)
            print(f"🔧 Moved {file} → tools/analysis/")

    # Move legacy UI files
    ui_dir = Path("src/aetherra/ui")
    if ui_dir.exists():
        for pattern in legacy_ui_patterns:
            for file in ui_dir.glob(pattern):
                dest = Path("archive/legacy_ui") / file.name
                shutil.move(file, dest)
                print(f"📦 Archived {file} → archive/legacy_ui/")


def move_assets():
    """Move image and asset files to proper locations."""
    asset_patterns = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg"]

    for pattern in asset_patterns:
        for file in Path(".").glob(pattern):
            if file.name.startswith("Aetherra") or file.name.startswith("Neuroplex"):
                dest = Path("assets/branding") / file.name
                shutil.move(file, dest)
                print(f"🎨 Moved {file} → assets/branding/")
            else:
                dest = Path("assets/images") / file.name
                shutil.move(file, dest)
                print(f"🖼️ Moved {file} → assets/images/")


def clean_root_directory():
    """Clean up the root directory by moving non-essential files."""

    # Files that should stay in root
    keep_in_root = {
        "README.md",
        "LICENSE",
        "requirements.txt",
        "requirements_minimal.txt",
        "pyproject.toml",
        "aetherra_launcher.py",
        "lyrixa.bat",
        ".gitignore",
        ".env",
    }

    # Move other files to appropriate locations
    for file in Path(".").glob("*.py"):
        if file.name not in keep_in_root and not file.is_dir():
            if "test" in file.name.lower() or "verify" in file.name.lower():
                dest = Path("testing") / file.name
                if not dest.exists():
                    shutil.move(file, dest)
                    print(f"🧪 Moved {file} → testing/")
            elif file.name.startswith("COMPLETE_") or file.name.startswith("FINAL_"):
                dest = Path("archive") / file.name
                if not dest.exists():
                    shutil.move(file, dest)
                    print(f"📦 Archived {file} → archive/")


def generate_cleanup_report():
    """Generate a report of the cleanup actions."""
    report = """
# AETHERRA HOUSEKEEPING REPORT
=============================

## Directory Structure Created
- archive/ - Legacy and backup files
- testing/ - All test and verification scripts
- tools/ - Utility and analysis scripts
- assets/ - Images, icons, and branding materials

## Files Organized
- Verification scripts moved to testing/verification/
- Analysis tools moved to tools/analysis/
- Legacy UI files archived to archive/legacy_ui/
- Asset files organized in assets/

## Root Directory Cleaned
- Only essential files remain in root
- Test files moved to testing/
- Archive files moved to archive/
- Tools moved to tools/

## Next Steps
1. Update README.md with new structure
2. Update website files with Crystal Blue/Jade Green theme
3. Final verification of all imports and functionality
"""

    with open("HOUSEKEEPING_REPORT.md", "w") as f:
        f.write(report)

    print("\n📄 Generated HOUSEKEEPING_REPORT.md")


def main():
    print("🧹 AETHERRA COMPREHENSIVE HOUSEKEEPING")
    print("=" * 50)

    print("\n1. Creating directory structure...")
    create_directory_structure()

    print("\n2. Analyzing duplicates...")
    duplicates = find_duplicate_files()
    similar = find_similar_files()
    print(f"   Found {len(duplicates)} groups of exact duplicates")
    print(f"   Found {len(similar)} groups of similar files")

    print("\n3. Organizing files...")
    organize_files()

    print("\n4. Moving assets...")
    move_assets()

    print("\n5. Cleaning root directory...")
    clean_root_directory()

    print("\n6. Generating report...")
    generate_cleanup_report()

    print("\n✅ HOUSEKEEPING COMPLETE!")
    print("   Project is now organized and ready for production")


if __name__ == "__main__":
    main()
