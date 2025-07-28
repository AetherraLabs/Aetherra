#!/usr/bin/env python3
"""
🧹 COMPREHENSIVE PROJECT CLEANUP
Remove all backup directories and reorganization tools
"""

import os
import shutil


def cleanup_backup_directories():
    """Remove all backup directories"""
    print("🗑️ REMOVING BACKUP DIRECTORIES:")
    print("=" * 50)

    backup_dirs = [
        "Aetherra_Core_Cleanup_Backup_20250727_003812",
        "Aetherra_v2_backup_20250726_230511",
        "Architecture_Correction_Backup_20250727_003348",
        "Lyrixa_Consolidation_Backup_20250727_002937",
        "Reorganization_Backup_20250727_001659",
        "Aetherra_Archive_20250726_224039",
        "archive",
    ]

    removed_count = 0
    for backup_dir in backup_dirs:
        if os.path.exists(backup_dir):
            try:
                shutil.rmtree(backup_dir)
                print(f"  ✅ Removed: {backup_dir}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {backup_dir}: {e}")
        else:
            print(f"  ⚪ Not found: {backup_dir}")

    print(f"\n📊 Backup directories removed: {removed_count}")


def cleanup_reorganization_tools():
    """Remove all reorganization and verification scripts"""
    print("\n🔧 REMOVING REORGANIZATION TOOLS:")
    print("=" * 50)

    tool_files = [
        "aetherra_core_cleanup.py",
        "aetherra_lyrixa_reorganizer.py",
        "cleanup_project.py",
        "final_aetherra_cleanup.py",
        "final_architecture_verification.py",
        "final_reorganization_strategy.py",
        "final_verification_before_cleanup.py",
        "lyrixa_consolidation_fixer.py",
        "project_safety_verification.py",
        "proper_architecture_verification.py",
        "safe_cleanup.py",
        "targeted_cleanup.py",
        "verify_lyrixa_consolidation.py",
        "verify_reorganization.py",
    ]

    removed_count = 0
    for tool_file in tool_files:
        if os.path.exists(tool_file):
            try:
                os.remove(tool_file)
                print(f"  ✅ Removed: {tool_file}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {tool_file}: {e}")
        else:
            print(f"  ⚪ Not found: {tool_file}")

    print(f"\n📊 Tool files removed: {removed_count}")


def cleanup_temporary_reports():
    """Remove temporary report files"""
    print("\n📋 REMOVING TEMPORARY REPORTS:")
    print("=" * 50)

    report_files = [
        "aetherra_core_cleanup_report_20250727_003813.json",
        "cleanup_report.json",
        "deployment_readiness_report.json",
        "enhanced_conflict_resolution_report.json",
        "final_reorganization_strategy.json",
        "launcher_status_report.json",
        "lyrixa_consolidation_report_20250727_002938.json",
        "meta_learning_tracker_report.json",
        "phase3_integration_demo_report.json",
        "real_agent_discovery_report.json",
        "reorganization_report_20250727_001659.json",
        "roadmap_validation_report.json",
        "self_directed_learning_loop_report.json",
    ]

    removed_count = 0
    for report_file in report_files:
        if os.path.exists(report_file):
            try:
                os.remove(report_file)
                print(f"  ✅ Removed: {report_file}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Failed to remove {report_file}: {e}")
        else:
            print(f"  ⚪ Not found: {report_file}")

    print(f"\n📊 Report files removed: {removed_count}")


def final_directory_count():
    """Count remaining directories for verification"""
    print("\n📊 FINAL DIRECTORY COUNT:")
    print("=" * 40)

    root_items = [item for item in os.listdir(".") if not item.startswith(".")]
    root_dirs = [item for item in root_items if os.path.isdir(item)]
    root_files = [item for item in root_items if os.path.isfile(item)]

    print(f"  📁 Root directories: {len(root_dirs)}")
    print(f"  📄 Root files: {len(root_files)}")

    # Show key remaining directories
    key_dirs = [
        d
        for d in root_dirs
        if d in ["Aetherra", "Aetherra_v2", "requirements", "docs", "tools"]
    ]
    print(f"  🎯 Key project dirs: {key_dirs}")

    # Check for any remaining cleanup candidates
    remaining_cleanup = []
    for item in root_items:
        if any(
            x in item.lower()
            for x in ["backup", "archive", "cleanup", "reorganiz", "verificat"]
        ):
            remaining_cleanup.append(item)

    if remaining_cleanup:
        print(f"  ⚠️ Remaining cleanup candidates: {remaining_cleanup}")
    else:
        print(f"  ✅ No remaining cleanup candidates found!")

    return len(root_dirs), len(remaining_cleanup)


def main():
    print("🧹 COMPREHENSIVE PROJECT CLEANUP")
    print("=" * 60)
    print("🎯 Goal: Remove all backup files and reorganization tools")

    # Perform cleanup
    cleanup_backup_directories()
    cleanup_reorganization_tools()
    cleanup_temporary_reports()

    # Final verification
    dir_count, remaining = final_directory_count()

    print(f"\n🏆 CLEANUP COMPLETE!")
    print("=" * 30)

    if remaining == 0:
        print("✅ All cleanup targets successfully removed")
        print("✅ Project directory is now clean and organized")
        print("✅ Core architecture preserved:")
        print("   • Aetherra/ - Core OS systems")
        print("   • Aetherra_v2/lyrixa/ - Lyrixa as interface")
        print("   • All backups and tools removed")
    else:
        print(f"⚠️ {remaining} cleanup items still remain")
        print("   Manual review may be needed")


if __name__ == "__main__":
    main()
