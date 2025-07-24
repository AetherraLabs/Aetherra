#!/usr/bin/env python3
"""
🚨 EMERGENCY REPOSITORY CLEANUP 🚨
==================================

This script will clean up the massive file bloat in the Aetherra repository.
Current status: ~80,000+ files (should be ~500-1000 for a typical project)

DANGEROUS OPERATIONS - REVIEW BEFORE RUNNING!
"""

import os
import shutil
import subprocess
from pathlib import Path


def emergency_cleanup():
    """Remove massive file bloat from repository"""

    print("🚨 AETHERRA EMERGENCY CLEANUP STARTING...")
    print("Current working directory:", os.getcwd())

    # Directories to COMPLETELY REMOVE (not needed in repo)
    dangerous_dirs = [
        ".venv",  # 2.56 GB - Virtual environment
        "Lib",  # 767 MB - Python library files
        "__pycache__",  # Python cache
        "*.egg-info",  # Python packaging
        "build",  # Build artifacts
        "dist",  # Distribution files
        ".pytest_cache",  # Test cache
    ]

    # Large files/patterns to remove
    file_patterns = [
        "*.pyc",  # Compiled Python
        "*.pyo",  # Optimized Python
        "*.pyd",  # Python DLL
        "*.so",  # Shared objects
        "*.dll",  # Windows libraries
        "*.log",  # Log files
        "*.tmp",  # Temporary files
        "*.temp",  # Temporary files
        "node_modules",  # Node.js packages
    ]

    # Backup critical files first
    critical_files = [
        "aetherra_hybrid_launcher.py",
        "Aetherra/lyrixa/gui/hybrid_window.py",
        "Aetherra/lyrixa/launcher.py",
        ".gitignore",
        "README.md",
        "requirements.txt",
    ]

    print("\n📁 Creating safety backup of critical files...")
    backup_dir = Path("EMERGENCY_BACKUP")
    backup_dir.mkdir(exist_ok=True)

    for file_path in critical_files:
        if Path(file_path).exists():
            dest = backup_dir / Path(file_path).name
            shutil.copy2(file_path, dest)
            print(f"✅ Backed up: {file_path}")

    print("\n🗑️  REMOVING BLOATED DIRECTORIES...")
    total_freed = 0

    for dir_name in dangerous_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            try:
                size_mb = get_dir_size(dir_path) / (1024 * 1024)
                print(f"🔥 Removing {dir_name} ({size_mb:.1f} MB)...")
                shutil.rmtree(dir_path)
                total_freed += size_mb
                print(f"✅ Removed {dir_name}")
            except Exception as e:
                print(f"❌ Failed to remove {dir_name}: {e}")

    print(f"\n🎉 CLEANUP COMPLETE!")
    print(f"💾 Total space freed: {total_freed:.1f} MB")
    print(f"📂 Critical files backed up to: {backup_dir}")

    # Update .gitignore to prevent future bloat
    update_gitignore()

    print("\n📋 RECOMMENDED NEXT STEPS:")
    print("1. Run: git status (check what's changed)")
    print(
        "2. Run: git add -A && git commit -m 'Emergency cleanup: removed 2.5GB bloat'"
    )
    print("3. Run: git push (after verifying everything works)")
    print("4. Recreate virtual environment: python -m venv .venv")
    print(
        "5. Install requirements: .venv\\Scripts\\activate && pip install -r requirements.txt"
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
                except:
                    pass
    except:
        pass
    return total


def update_gitignore():
    """Ensure .gitignore has all necessary exclusions"""
    gitignore_additions = """
# === EMERGENCY ADDITIONS TO PREVENT BLOAT ===
# Virtual environments (CRITICAL!)
.venv/
venv/
env/
ENV/
Lib/
Scripts/
Include/
pyvenv.cfg

# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
*.whl

# IDE and OS
.vscode/settings.json
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Runtime/Cache
*.log
*.tmp
*.temp
.pytest_cache/
.coverage
htmlcov/

# Large binaries
*.dll
*.so
*.dylib
*.pyd
node_modules/
"""

    try:
        with open(".gitignore", "a", encoding="utf-8") as f:
            f.write(gitignore_additions)
        print("✅ Updated .gitignore with bloat prevention rules")
    except Exception as e:
        print(f"❌ Failed to update .gitignore: {e}")


if __name__ == "__main__":
    print("⚠️  WARNING: This will delete 2.5+ GB of files!")
    print("⚠️  Make sure you have backups of important work!")
    response = input("\nProceed with emergency cleanup? (yes/no): ")

    if response.lower() == "yes":
        emergency_cleanup()
    else:
        print("❌ Cleanup cancelled. Repository remains bloated.")
        print("💡 Consider manually removing .venv/ and Lib/ directories")
