#!/usr/bin/env python3
"""
Plugin Chaining Backup Verification Script
Verifies the integrity and completeness of the plugin chaining system backup.
"""

import os
import sys
from pathlib import Path


def verify_backup(backup_path):
    """Verify the backup contains all required files."""

    backup_dir = Path(backup_path)
    if not backup_dir.exists():
        print(f"❌ Backup directory not found: {backup_path}")
        return False

    print(f"🔍 Verifying backup at: {backup_path}")
    print("=" * 50)

    # Define required files
    required_files = [
        # Core implementation
        "lyrixa/core/plugin_chainer.py",
        "lyrixa/core/plugins.py",
        "lyrixa/core/plugin_state_memory.py",
        "lyrixa/core/semantic_plugin_discovery.py",
        # Tests
        "test_plugin_chaining_integration.py",
        "test_direct_chaining.py",
        "test_simple_chaining.py",
        # Demo
        "demo_plugin_chaining.py",
        # Documentation
        "PLUGIN_CHAINING_INTEGRATION_COMPLETE.md",
        "PLUGIN_CHAINING_SUCCESS_SUMMARY.md",
        "PHASE4_COMPLETE_REPORT.md",
        "PHASE4_IMPLEMENTATION_PROGRESS.md",
        # Backup info
        "BACKUP_SUMMARY.md",
    ]

    missing_files = []
    present_files = []

    for file_path in required_files:
        full_path = backup_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path} ({size:,} bytes)")
            present_files.append(file_path)
        else:
            print(f"❌ MISSING: {file_path}")
            missing_files.append(file_path)

    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION SUMMARY")
    print(f"Files present: {len(present_files)}/{len(required_files)}")
    print(f"Files missing: {len(missing_files)}")

    if missing_files:
        print(f"\n❌ BACKUP INCOMPLETE - Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print(f"\n✅ BACKUP COMPLETE - All required files present!")

        # Check for additional files
        all_files = list(backup_dir.rglob("*"))
        all_files = [f for f in all_files if f.is_file()]

        print(f"\n📁 Total files in backup: {len(all_files)}")
        print(
            f"📁 Total backup size: {sum(f.stat().st_size for f in all_files):,} bytes"
        )

        return True


def main():
    """Main verification function."""

    # Default backup path - latest backup
    backup_path = (
        "backups/plugin_chaining_complete/plugin_chaining_final_20250706_221504"
    )

    if len(sys.argv) > 1:
        backup_path = sys.argv[1]

    print("🔗 Plugin Chaining System Backup Verification")
    print("=" * 50)

    success = verify_backup(backup_path)

    if success:
        print("\n🎉 Backup verification PASSED!")
        print("[DISC] The plugin chaining system backup is complete and ready for use.")
        sys.exit(0)
    else:
        print("\n[FAIL] Backup verification FAILED!")
        print("⚠️  Some files are missing from the backup.")
        sys.exit(1)


if __name__ == "__main__":
    main()
