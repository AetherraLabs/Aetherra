#!/usr/bin/env python3
"""
🧹 AETHERRA PROJECT CLEANUP
===========================

This script identifies unused files and moves them to an "Unused" folder
to clean up the project structure.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Set


def get_currently_used_files() -> Set[str]:
    """Define files that are currently being used in the active system"""
    used_files = {
        # Core active system files
        "Aetherra/",  # Main project folder
        "demo_memory_chat_integration.py",  # Our new demo
        "demo_memory_system.py",  # Memory system demo
        "LYRIXA_MEMORY_INTEGRATION_GUIDE.md",  # Integration guide
        "MEMORY_SYSTEM_ROADMAP.md",  # Current roadmap
        # Essential project files
        "README.md",
        "LICENSE",
        "requirements.txt",
        ".gitignore",
        ".env.template",
        # Git and version control
        ".git/",
        ".github/",
        # Python environment
        ".venv/",
        "__pycache__/",
        ".pytest_cache/",
        # IDE and tools
        ".vscode/",
        # Current launcher (if still used)
        "aetherra_launcher.py",
        # Documentation that's current
        "docs/",
    }

    # Add Aetherra subfolder essentials
    aetherra_used = {
        "Aetherra/lyrixa/",  # Active conversation system
        "Aetherra/memory/",  # New memory system
        "Aetherra/core/",  # Core functionality
        "Aetherra/api/",  # API system
        "Aetherra/cli/",  # CLI tools
        "Aetherra/ui/",  # User interface
        "Aetherra/plugins/",  # Plugin system
        "Aetherra/runtime/",  # Runtime components
        "Aetherra/scripts/",  # Utility scripts
        "Aetherra/tests/",  # Test suite
        "Aetherra/README.md",
        "Aetherra/LICENSE",
        "Aetherra/pyproject.toml",
        "Aetherra/__init__.py",
        "Aetherra/Aetherra Memory System Evolution Roadmap.md",
    }

    used_files.update(aetherra_used)
    return used_files


def get_unused_files(project_root: str) -> List[str]:
    """Identify files that are not currently being used"""
    used_files = get_currently_used_files()
    unused_files = []

    # Walk through project directory
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories entirely
        skip_dirs = {
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            "Unused",
        }
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), project_root)
            file_path_normalized = file_path.replace("\\\\", "/")

            # Check if this file or its parent directory is in used files
            is_used = False
            for used_pattern in used_files:
                if (
                    file_path_normalized == used_pattern
                    or file_path_normalized.startswith(used_pattern)
                    or any(
                        file_path_normalized.startswith(used_pattern.rstrip("/"))
                        for used_pattern in used_files
                        if used_pattern.endswith("/")
                    )
                ):
                    is_used = True
                    break

            # Additional checks for patterns that should be kept
            if (
                (
                    file_path_normalized.endswith(".md")
                    and "README" in file_path_normalized.upper()
                )
                or (
                    file_path_normalized.endswith(".txt")
                    and "requirements" in file_path_normalized
                )
                or file_path_normalized.startswith("Aetherra/")
            ):
                is_used = True

            if not is_used:
                unused_files.append(file_path_normalized)

    return unused_files


def identify_legacy_files(project_root: str) -> List[str]:
    """Identify specific legacy files that should be moved"""
    legacy_patterns = [
        # Old demo and test files
        "*_demo.py",
        "*_test.py",
        "test_*.py",
        "*_backup.py",
        # Old documentation/summaries
        "*_COMPLETE.md",
        "*_COMPLETE.py",
        "*_SUMMARY.md",
        "*_FIX*.md",
        "*_INTEGRATION*.md",
        "*_IMPLEMENTATION*.md",
        # Old databases and caches
        "*.db",
        "*.json",
        # Old launcher files
        "*launcher*.py",
        "*launcher*.bat",
        # Old API servers
        "*api_server*.py",
        "*server*.py",
        # Old plugin files in root
        "*plugin*.py",
        "enhanced_*.py",
        "comprehensive_*.py",
        "final_*.py",
        # Build and deployment files
        "build-*.bat",
        "*.html",
        "*.svg",
        "*.xml",
        # Old directories that might be legacy
        "archive/",
        "backups/",
        "testing/",
        "development/",
        "examples/",
        "demos/",
        "documentation/",
        "operations/",
        "continue/",
        "config/",
        "data/",
        "deployments/",
        "developer_tools/",
        "media/",
        "sdk/",
        "scripts/",
        "system/",
        "web/",
        "aetherra_hub/",
        "lyrixa_plugins/",
    ]

    legacy_files = []

    for root, dirs, files in os.walk(project_root):
        # Skip essential directories
        if any(skip in root for skip in [".git", ".venv", "__pycache__", "Aetherra/"]):
            continue

        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), project_root)
            file_path_normalized = file_path.replace("\\\\", "/")

            # Check against legacy patterns
            for pattern in legacy_patterns:
                if pattern.endswith("/"):
                    if file_path_normalized.startswith(pattern):
                        legacy_files.append(file_path_normalized)
                        break
                else:
                    import fnmatch

                    if fnmatch.fnmatch(os.path.basename(file), pattern):
                        legacy_files.append(file_path_normalized)
                        break

    # Add specific legacy directories
    legacy_dirs = [
        "Aetherra_backup_20250712_184525/",
        ".backups/",
        ".safe_backups/",
        "test_backups/",
        ".plugin_history/",
        ".aetherra/",
        ".aether/",
        "assets/",
        "test_workspace/",
        "tools/",
        "utilities/",
    ]

    for legacy_dir in legacy_dirs:
        legacy_dir_path = os.path.join(project_root, legacy_dir)
        if os.path.exists(legacy_dir_path):
            for root, dirs, files in os.walk(legacy_dir_path):
                for file in files:
                    file_path = os.path.relpath(os.path.join(root, file), project_root)
                    legacy_files.append(file_path.replace("\\\\", "/"))

    return legacy_files


def move_files_to_unused(project_root: str, files_to_move: List[str]) -> bool:
    """Move specified files to the Unused folder"""
    unused_dir = os.path.join(project_root, "Unused")

    # Create Unused directory if it doesn't exist
    os.makedirs(unused_dir, exist_ok=True)

    # Create timestamp for this cleanup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleanup_dir = os.path.join(unused_dir, f"cleanup_{timestamp}")
    os.makedirs(cleanup_dir, exist_ok=True)

    moved_count = 0

    for file_path in files_to_move:
        source_path = os.path.join(project_root, file_path)

        if not os.path.exists(source_path):
            continue

        # Create destination directory structure
        dest_path = os.path.join(cleanup_dir, file_path)
        dest_dir = os.path.dirname(dest_path)
        os.makedirs(dest_dir, exist_ok=True)

        try:
            if os.path.isdir(source_path):
                shutil.move(source_path, dest_path)
            else:
                shutil.move(source_path, dest_path)
            moved_count += 1
            print(f"Moved: {file_path}")
        except Exception as e:
            print(f"Error moving {file_path}: {e}")

    return moved_count > 0


def update_gitignore(project_root: str):
    """Add Unused folder to gitignore"""
    gitignore_path = os.path.join(project_root, ".gitignore")

    # Read existing gitignore
    gitignore_content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()

    # Add Unused folder if not already present
    if "Unused/" not in gitignore_content:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            f.write("\\n# Unused/legacy files moved during cleanup\\n")
            f.write("Unused/\\n")
            f.write("*.unused\\n")
        print("✅ Updated .gitignore to exclude Unused/ folder")
    else:
        print("ℹ️ Unused/ already in .gitignore")


def main():
    """Main cleanup function"""
    project_root = os.getcwd()
    print(f"🧹 Starting Aetherra project cleanup in: {project_root}")
    print("=" * 60)

    # Get legacy files to move
    print("🔍 Identifying legacy and unused files...")
    legacy_files = identify_legacy_files(project_root)

    print(f"📋 Found {len(legacy_files)} potential files to move:")
    for file in sorted(legacy_files)[:20]:  # Show first 20
        print(f"  • {file}")
    if len(legacy_files) > 20:
        print(f"  ... and {len(legacy_files) - 20} more")

    # Confirm before moving
    print("\\n⚠️ This will move the above files to the 'Unused' folder.")
    response = input("Continue? (y/N): ").lower().strip()

    if response in ["y", "yes"]:
        print("\\n🚀 Moving files...")
        success = move_files_to_unused(project_root, legacy_files)

        if success:
            print("\\n📝 Updating .gitignore...")
            update_gitignore(project_root)

            print("\\n✅ Cleanup completed successfully!")
            print(
                f"📁 Legacy files moved to: Unused/cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}/"
            )
            print(
                "\\n🎯 Your project is now cleaner with only active files in main directories."
            )
        else:
            print("\\n❌ No files were moved.")
    else:
        print("\\n❌ Cleanup cancelled.")


if __name__ == "__main__":
    main()
