#!/usr/bin/env python3
"""
AetherraCode Duplicate Cleanup Script

This script executes the planned cleanup of confirmed duplicate files.
Executes in phases for safety.
"""

import os
import shutil
from pathlib import Path


def create_archive_structure():
    """Create archive directories for organizing moved files."""
    archive_dirs = ["archive/status_files", "archive/duplicates", "archive/empty_scripts"]

    for dir_path in archive_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created archive directory: {dir_path}")


def phase1_website_duplicates():
    """Remove confirmed identical website files from root."""
    print("\n🌐 PHASE 1: Removing confirmed website duplicates...")

    website_files = [
        "index.html",
        "styles.css",
        "script.js",
        "debug-test.html",
        "cache-buster-test.html",
        "link-audit.html",
    ]

    for file in website_files:
        if Path(file).exists():
            # Verify website version exists
            website_version = Path("website") / file
            if website_version.exists():
                os.remove(file)
                print(f"❌ Deleted root duplicate: {file}")
            else:
                print(f"⚠️  Skipped {file} - website version not found")
        else:
            print(f"ℹ️  {file} - already removed")


def phase2_empty_scripts():
    """Remove empty debug script files."""
#     print("\n🔧 PHASE 2: Removing empty debug scripts...")

    empty_scripts = [
        "scripts/parse_debug.py",
        "scripts/parse_debug2.py",
        "scripts/parse_debug3.py",
        "scripts/parse_debug4.py",
        "scripts/tokenize_debug.py",
        "scripts/quick_debug_test.py",
        "scripts/check_qt.py",
    ]

    for script in empty_scripts:
        script_path = Path(script)
        if script_path.exists():
            # Double-check it's actually empty
            if script_path.stat().st_size == 0:
                # Move to archive first for safety
                archive_path = Path("archive/empty_scripts") / script_path.name
                shutil.move(str(script_path), str(archive_path))
                print(f"📦 Archived empty script: {script} → archive/empty_scripts/")
            else:
                print(f"⚠️  Skipped {script} - not empty ({script_path.stat().st_size} bytes)")
        else:
            print(f"ℹ️  {script} - already removed")


def phase3_script_duplicates():
    """Remove confirmed script duplicates."""
    print("\n📜 PHASE 3: Removing script duplicates...")

    script_duplicates = ["scripts/update_overview_clean.py"]

    for script in script_duplicates:
        script_path = Path(script)
        if script_path.exists():
            # Move to archive for safety
            archive_path = Path("archive/duplicates") / script_path.name
            shutil.move(str(script_path), str(archive_path))
            print(f"📦 Archived duplicate script: {script} → archive/duplicates/")
        else:
            print(f"ℹ️  {script} - already removed")


def phase4_status_files():
    """Organize status files - move historical ones to archive."""
    print("\n📊 PHASE 4: Organizing status files...")

    status_files_to_archive = [
        "NEUROHUB_SUCCESS_SUMMARY.md",
        "NEUROHUB_CLEANUP_SUMMARY.md",
        "MODEST_PROFESSIONAL_SUMMARY.md",
        "MISSION_ACCOMPLISHED_SUMMARY.md",
        "FINAL_REPOSITORY_STATUS.md",
        "MISSION_COMPLETE.md",
    ]

    for file in status_files_to_archive:
        file_path = Path(file)
        if file_path.exists():
            archive_path = Path("archive/status_files") / file_path.name
            shutil.move(str(file_path), str(archive_path))
            print(f"📦 Archived status file: {file} → archive/status_files/")
        else:
            print(f"ℹ️  {file} - already moved or doesn't exist")

    # Handle CNAME duplicate - keep root version for GitHub Pages
    website_cname = Path("website/CNAME")
    if website_cname.exists():
        archive_path = Path("archive/duplicates") / "CNAME_website"
        shutil.move(str(website_cname), str(archive_path))
        print("📦 Archived duplicate CNAME: website/CNAME → archive/duplicates/CNAME_website")


def show_cleanup_summary():
    """Show what files remain vs what was cleaned up."""
    print("\n📋 CLEANUP SUMMARY:")
    print("✅ Kept in root:")
    print("   - PROJECT_OVERVIEW.md (main status)")
    print("   - SUCCESS_SUMMARY.md (final summary)")
    print("   - FINAL_ORGANIZATION_STATUS.md (organization status)")
    print("   - CNAME (for GitHub Pages)")

    print("\n🌐 Website files (organized in website/):")
    website_files = ["index.html", "styles.css", "script.js"]
    for file in website_files:
        if Path("website") / file:
            print(f"   ✅ website/{file}")

    print("\n📦 Archived in archive/:")
    archive_dirs = ["status_files", "duplicates", "empty_scripts"]
    for dir_name in archive_dirs:
        archive_dir = Path("archive") / dir_name
        if archive_dir.exists():
            files = list(archive_dir.iterdir())
            print(f"   📁 {dir_name}/: {len(files)} files")


def main():
    """Execute the cleanup phases."""
    print("🧹 AetherraCode Duplicate Cleanup")
    print("================================")

    # Create archive structure
    create_archive_structure()

    # Execute cleanup phases
    phase1_website_duplicates()
    phase2_empty_scripts()
    phase3_script_duplicates()
    phase4_status_files()

    # Show summary
    show_cleanup_summary()

    print("\n🎉 Cleanup complete!")
    print("📁 Duplicates archived in archive/ for safety")
    print("🔍 Review archive/ contents before final deletion")


if __name__ == "__main__":
    main()
