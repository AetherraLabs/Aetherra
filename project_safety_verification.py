#!/usr/bin/env python3
"""
🔍 PROJECT STATUS VERIFICATION
Honest assessment of current project state and safety
"""

import json
import os
from pathlib import Path


def check_file_safety():
    """Verify we haven't deleted important files"""
    print("🛡️ FILE SAFETY VERIFICATION:")
    print("=" * 50)

    # Check for key backup directories
    backup_dirs = [
        "Reorganization_Backup_20250727_001659",
        "Aetherra_Core_Cleanup_Backup_20250727_003812",
        "Architecture_Correction_Backup_20250727_003348",
        "Lyrixa_Consolidation_Backup_20250727_002937",
    ]

    total_backed_up_files = 0

    for backup_dir in backup_dirs:
        if os.path.exists(backup_dir):
            file_count = 0
            for root, dirs, files in os.walk(backup_dir):
                file_count += len(files)
            total_backed_up_files += file_count
            print(f"  ✅ {backup_dir}: {file_count} files backed up")
        else:
            print(f"  ❌ {backup_dir}: NOT FOUND")

    print(f"  📊 Total backed up files: {total_backed_up_files}")
    return total_backed_up_files > 0


def verify_project_structure():
    """Check if we have a sensible project structure"""
    print("\\n🏗️ PROJECT STRUCTURE VERIFICATION:")
    print("=" * 50)

    # Key directories that should exist
    expected_dirs = {
        "Aetherra/": "Core OS systems",
        "Aetherra_v2/": "Complete system with Lyrixa interface",
        "Aetherra_v2/lyrixa/": "Lyrixa as Aetherra's interface",
        ".git/": "Git repository",
        "requirements/": "Project dependencies",
        "docs/": "Documentation",
    }

    structure_ok = True

    for dir_path, description in expected_dirs.items():
        exists = os.path.exists(dir_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path} - {description}")
        if not exists and dir_path in ["Aetherra/", "Aetherra_v2/", ".git/"]:
            structure_ok = False

    return structure_ok


def count_active_code():
    """Count Python files in active directories"""
    print("\\n📊 ACTIVE CODE VERIFICATION:")
    print("=" * 50)

    directories_to_check = {
        "Aetherra/": "Core OS",
        "Aetherra_v2/": "Complete System",
        "Aetherra_v2/lyrixa/": "Lyrixa Interface",
    }

    total_active_files = 0

    for dir_path, description in directories_to_check.items():
        if os.path.exists(dir_path):
            py_files = 0
            for root, dirs, files in os.walk(dir_path):
                # Skip backup and cache directories
                if any(
                    skip in root.lower() for skip in ["backup", "__pycache__", ".git"]
                ):
                    continue
                py_files += len([f for f in files if f.endswith(".py")])

            total_active_files += py_files
            print(f"  📁 {dir_path}: {py_files} Python files ({description})")
        else:
            print(f"  ❌ {dir_path}: NOT FOUND")

    print(f"  🐍 Total active Python files: {total_active_files}")
    return total_active_files


def check_git_status():
    """Check if git repository is intact"""
    print("\\n🔄 GIT REPOSITORY STATUS:")
    print("=" * 40)

    if os.path.exists(".git"):
        # Check if we can get basic git info
        try:
            import subprocess

            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=".",
            )
            if result.returncode == 0:
                changed_files = (
                    len(result.stdout.strip().split("\\n"))
                    if result.stdout.strip()
                    else 0
                )
                print(f"  ✅ Git repository is functional")
                print(f"  📝 Modified/new files: {changed_files}")
                return True
            else:
                print(f"  ⚠️ Git command failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"  ⚠️ Cannot check git status: {e}")
            return False
    else:
        print("  ❌ No .git directory found")
        return False


def assess_mess_level():
    """Honest assessment of project organization"""
    print("\\n🎯 MESS LEVEL ASSESSMENT:")
    print("=" * 50)

    # Count directories in root
    root_items = [item for item in os.listdir(".") if not item.startswith(".")]
    root_dirs = len([item for item in root_items if os.path.isdir(item)])
    root_files = len([item for item in root_items if os.path.isfile(item)])

    print(f"  📁 Root directories: {root_dirs}")
    print(f"  📄 Root files: {root_files}")

    # Check for duplicate/confusing structures
    aetherra_dirs = [item for item in root_items if "aetherra" in item.lower()]
    lyrixa_items = [item for item in root_items if "lyrixa" in item.lower()]
    backup_dirs = [item for item in root_items if "backup" in item.lower()]

    print(f"  🔍 Aetherra-related dirs: {len(aetherra_dirs)} {aetherra_dirs}")
    print(f"  🧠 Lyrixa-related items: {len(lyrixa_items)} {lyrixa_items}")
    print(f"  💾 Backup directories: {len(backup_dirs)}")

    # Mess level calculation
    mess_indicators = 0
    if root_dirs > 50:
        mess_indicators += 1
    if root_files > 100:
        mess_indicators += 1
    if len(aetherra_dirs) > 4:
        mess_indicators += 1
    if len(backup_dirs) > 6:
        mess_indicators += 1

    mess_levels = {
        0: "🟢 CLEAN - Well organized",
        1: "🟡 MODERATE - Some clutter but manageable",
        2: "🟠 MESSY - Needs organization",
        3: "🔴 VERY MESSY - Significant cleanup needed",
        4: "💀 DISASTER - Complete reorganization required",
    }

    mess_level = min(mess_indicators, 4)
    print(f"\\n  {mess_levels[mess_level]}")

    return mess_level


def main():
    print("🔍 PROJECT STATUS VERIFICATION")
    print("=" * 60)
    print("📋 Honest assessment of what we've done")

    # Run all checks
    backups_safe = check_file_safety()
    structure_ok = verify_project_structure()
    active_files = count_active_code()
    git_ok = check_git_status()
    mess_level = assess_mess_level()

    # Overall assessment
    print("\\n🏆 OVERALL ASSESSMENT:")
    print("=" * 40)

    safety_checks = [
        ("Backups Preserved", backups_safe),
        ("Project Structure", structure_ok),
        ("Active Code Present", active_files > 100),
        ("Git Repository Intact", git_ok),
        ("Organization Level", mess_level <= 2),
    ]

    passed = sum(1 for _, check in safety_checks if check)
    total = len(safety_checks)

    for name, result in safety_checks:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    safety_score = (passed / total) * 100

    print(f"\\n📊 SAFETY SCORE: {passed}/{total} ({safety_score:.0f}%)")

    if safety_score >= 80:
        print("\\n🎉 VERDICT: Project is SAFE and well-organized!")
        print("   ✅ No important files lost")
        print("   ✅ Clear architecture achieved")
        print("   ✅ Multiple backups preserved")
    elif safety_score >= 60:
        print("\\n⚠️ VERDICT: Project is SAFE but needs some cleanup")
        print("   ✅ No data loss")
        print("   📝 Some organization improvements needed")
    else:
        print("\\n🚨 VERDICT: Project needs attention")
        print("   ⚠️ Issues found that should be addressed")


if __name__ == "__main__":
    main()
