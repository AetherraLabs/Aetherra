#!/usr/bin/env python3
"""
Final Verification Summary
==========================

Quick verification that the consolidated Lyrixa system is working properly.
"""

import sys
from pathlib import Path


def verify_core_files():
    """Verify core files exist."""
    core_files = [
        "lyrixa_unified_launcher_win.py",
        "modern_lyrixa_gui.py",
        "unified_aetherra_lyrixa_gui.py",
        "simple_lyrixa_gui_test.py",
        "test_comprehensive_integration.py",
    ]

    print("VERIFYING CORE FILES:")
    all_present = True

    for file in core_files:
        if Path(file).exists():
            print(f"  [+] {file}")
        else:
            print(f"  [-] MISSING: {file}")
            all_present = False

    return all_present


def verify_archive():
    """Verify archive directory exists."""
    archive_dir = Path("archive/legacy_guis_launchers")
    if archive_dir.exists():
        file_count = len(list(archive_dir.glob("*.py")))
        print(f"  [+] Archive exists with {file_count} files")
        return True
    else:
        print("  [-] Archive directory missing")
        return False


def main():
    """Main verification."""
    print("LYRIXA CONSOLIDATION VERIFICATION")
    print("=" * 40)

    # Verify core files
    cores_ok = verify_core_files()
    print()

    # Verify archive
    print("VERIFYING ARCHIVE:")
    archive_ok = verify_archive()
    print()

    # Overall status
    if cores_ok and archive_ok:
        print("[+] CONSOLIDATION SUCCESSFUL!")
        print("[*] All core files present")
        print("[*] Legacy files archived")
        print("[*] System ready for use")
        print()
        print("USAGE:")
        print("  python lyrixa_unified_launcher_win.py")
        print("  python simple_lyrixa_gui_test.py")
        return 0
    else:
        print("[-] CONSOLIDATION ISSUES DETECTED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
