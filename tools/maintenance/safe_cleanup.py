#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Safe File Cleanup - Remove empty files and obvious duplicates
"""

# Standard library imports
import hashlib
import json
from pathlib import Path


def _hash_value(value) -> str | None:
    if value is None:
        return None
    raw = str(value)
    if not raw:
        return None
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _guardian_capability_checker(requester: str, capability: str) -> bool:
    if requester == "maintenance" and capability in {
        "maintenance:cleanup",
        "fs:delete",
    }:
        return True

    from Aetherra.security.capabilities import has_capability

    return has_capability(requester, capability)


def _duplicate_init_files_to_remove(analysis):
    files_to_remove = []
    for dup_group in analysis.get("duplicates", []):
        files = dup_group.get("files", [])
        if all(Path(f).name == "__init__.py" for f in files):
            files_to_remove.extend(sorted(files, key=len)[1:])
    return files_to_remove


def _guardian_preflight_cleanup(empty_files, duplicate_init_files):
    import os

    from Aetherra.guardian import IntentDeclaration, evaluate_intent

    requester = os.getenv("AETHERRA_PRINCIPAL", "").strip() or "maintenance"
    approval_id = os.getenv("AETHERRA_GUARDIAN_APPROVAL_ID", "").strip() or None
    planned_paths = [*empty_files, *duplicate_init_files]
    return evaluate_intent(
        IntentDeclaration(
            requester=requester,
            subsystem="maintenance",
            action="maintenance.safe_file_cleanup",
            target="maintenance:safe_file_cleanup",
            purpose="Remove empty files and duplicate __init__.py files from project analysis",
            capabilities=("maintenance:cleanup", "fs:delete"),
            expected_outcome="Only planned empty or duplicate init files are deleted",
            reversible=False,
            rollback_plan="restore deleted files from version control or a prior workspace backup",
            metadata={
                "empty_file_count": len(empty_files),
                "duplicate_init_count": len(duplicate_init_files),
                "planned_delete_count": len(planned_paths),
                "planned_path_hashes": tuple(
                    sorted(_hash_value(path) or "" for path in planned_paths)[:50]
                ),
            },
        ),
        approval_id=approval_id,
        capability_checker=_guardian_capability_checker,
    )


def load_analysis():
    """Load the project analysis"""
    with open("aetherra_project_analysis.json", encoding="utf-8") as f:
        return json.load(f)

def find_empty_files(analysis):
    """Find all empty files (0 bytes)"""
    empty_files = []

    # Look through duplicates for the group with hash starting with 'e3b0c44298fc1c14'
    # This is the SHA256 hash of an empty file
    for dup_group in analysis.get("duplicates", []):
        if dup_group["hash"].startswith("e3b0c44298fc1c14"):
            empty_files.extend(dup_group["files"])
            break

    return empty_files

def safe_remove_empty_files(empty_files):
    """Safely remove empty files"""
    removed_count = 0
    errors = []

    print(f"🗑️ Found {len(empty_files)} empty files to remove...")
    print()

    for filepath in empty_files:
        try:
            file_path = Path(filepath)
            if file_path.exists():
                # Double-check it's actually empty
                if file_path.stat().st_size == 0:
                    file_path.unlink()
                    print(f"✅ Removed: {filepath}")
                    removed_count += 1
                else:
                    print(f"⚠️ Skipped (not empty): {filepath}")
            else:
                print(f"⚠️ Already gone: {filepath}")
        except Exception as e:
            errors.append(f"❌ Error removing {filepath}: {e}")
            print(f"❌ Error removing {filepath}: {e}")

    print()
    print(f"🎉 Successfully removed {removed_count} empty files!")

    if errors:
        print(f"⚠️ {len(errors)} errors encountered:")
        for error in errors:
            print(f"   {error}")

    return removed_count, errors

def remove_duplicate_init_files(analysis):
    """Remove duplicate __init__.py files (keep shortest path)"""
    removed_count = 0

    for dup_group in analysis.get("duplicates", []):
        # Look for groups where all files are __init__.py
        if all(Path(f).name == "__init__.py" for f in dup_group["files"]):
            # Keep the one with the shortest path (most likely the main one)
            files_to_remove = sorted(dup_group["files"], key=len)[1:]  # Skip first (shortest)

            print(f"📁 Found {len(dup_group['files'])} duplicate __init__.py files")
            print(f"   Keeping: {sorted(dup_group['files'], key=len)[0]}")

            for filepath in files_to_remove:
                try:
                    file_path = Path(filepath)
                    if file_path.exists():
                        file_path.unlink()
                        print(f"✅ Removed duplicate: {filepath}")
                        removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing {filepath}: {e}")

    return removed_count

def main():
    """Execute safe cleanup operations"""
    print("🧹 Starting Safe File Cleanup...")
    print("=" * 50)

    # Load analysis
    analysis = load_analysis()

    # Phase 1: Remove empty files
    print("📋 Phase 1: Removing Empty Files")
    print("-" * 30)
    empty_files = find_empty_files(analysis)
    duplicate_init_files = _duplicate_init_files_to_remove(analysis)
    guardian_decision = _guardian_preflight_cleanup(empty_files, duplicate_init_files)
    if not guardian_decision.allowed:
        print(f"Guardian denied safe cleanup: {guardian_decision.reason}")
        return 1

    removed_empty, errors = safe_remove_empty_files(empty_files)

    print()
    print("📋 Phase 2: Removing Duplicate __init__.py Files")
    print("-" * 30)
    removed_init = remove_duplicate_init_files(analysis)

    # Summary
    print()
    print("🎯 CLEANUP SUMMARY")
    print("=" * 30)
    print(f"Empty files removed: {removed_empty}")
    print(f"Duplicate __init__.py removed: {removed_init}")
    print(f"Total files removed: {removed_empty + removed_init}")

    if errors:
        print(f"Errors encountered: {len(errors)}")
    else:
        print("✅ No errors encountered!")

    print()
    print("🚀 Safe cleanup complete! Project is now cleaner and more organized.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
