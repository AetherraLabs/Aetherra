#!/usr/bin/env python3
"""
🎯 AETHERRA POST-CLEANUP SCRIPT
===============================

Run this AFTER closing the Aetherra application to complete the cleanup.
This will remove the remaining 767MB Lib directory and other locked files.
"""

import os
import shutil
import subprocess
from pathlib import Path


def post_cleanup():
    """Complete the cleanup after closing the application"""

    print("🎯 AETHERRA POST-CLEANUP STARTING...")

    # Directories to remove after app closure
    cleanup_dirs = [
        "Lib",  # 767 MB - Python packages in use
        "__pycache__",  # Python cache
        ".pytest_cache",  # Test cache
    ]

    # Files to clean up
    cleanup_files = [
        "*.log",  # Log files
        "*.tmp",  # Temporary files
        "*.temp",  # Temporary files
        "api_server_startup.log",
        "backend_startup.log",
    ]

    total_freed = 0

    print("🗑️  REMOVING REMAINING BLOAT...")

    # Remove directories
    for dir_name in cleanup_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                size_mb = get_dir_size(dir_path) / (1024 * 1024)
                print(f"🔥 Removing {dir_name} ({size_mb:.1f} MB)...")

                # Force remove with Windows command for stubborn directories
                if os.name == "nt":  # Windows
                    os.system(f'rmdir /s /q "{dir_name}"')
                else:
                    shutil.rmtree(dir_path)

                total_freed += size_mb
                print(f"✅ Removed {dir_name}")
            except Exception as e:
                print(f"[ERROR] Failed to remove {dir_name}: {e}")

    # Remove individual files
    for pattern in cleanup_files:
        try:
            files = list(Path(".").glob(pattern))
            for file_path in files:
                if file_path.exists():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    file_path.unlink()
                    total_freed += size_mb
                    print(f"🗑️  Removed {file_path}")
        except Exception as e:
            print(f"[ERROR] Failed to remove {pattern}: {e}")

    # Final file count
    try:
        final_count = sum(1 for _ in Path(".").rglob("*") if _.is_file())
        print(f"\n🎉 POST-CLEANUP COMPLETE!")
        print(f"💾 Additional space freed: {total_freed:.1f} MB")
        print(f"📁 Final file count: {final_count:,}")

        if final_count < 5000:
            print("✅ Repository size is now REASONABLE!")
        else:
            print("[WARN]  Still some bloat remaining. Check large directories.")

    except Exception as e:
        print(f"[ERROR] Error counting files: {e}")

    print("\n📋 RECOMMENDED NEXT STEPS:")
    print("1. Create new virtual environment: py -m venv .venv")
    print("2. Activate it: .venv\\Scripts\\activate")
    print("3. Install requirements: pip install -r requirements.txt")
    print("4. Test Aetherra: py aetherra_hybrid_launcher.py")
    print(
        "5. Commit cleanup: git add -A && git commit -m 'Complete cleanup: removed 3+ GB bloat'"
    )


def get_dir_size(path):
    """Calculate directory size in bytes"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    total += os.path.getsize(file_path)
                except Exception:
                    pass
    except Exception:
        pass
    return total


if __name__ == "__main__":
    print("[WARN]  Make sure Aetherra application is CLOSED before running this!")
    response = input("Application closed and ready for final cleanup? (yes/no): ")

    if response.lower() == "yes":
        post_cleanup()
    else:
        print("[ERROR] Post-cleanup cancelled.")
        print("💡 Close Aetherra application first, then run this script")
