#!/usr/bin/env python3
"""
System Optimization Script - aetherra Project
Removes cache files, temporary files, and performs final optimizations for pristine workspace.
"""

import shutil
import sys
from datetime import datetime
from pathlib import Path


def clean_cache_files(root_path):
    """Remove Python cache files and directories"""
    print("🧹 Cleaning Python cache files...")

    # Remove root __pycache__
    pycache_root = root_path / "__pycache__"
    if pycache_root.exists():
        shutil.rmtree(pycache_root)
        print(f"  ✅ Removed {pycache_root}")

    # Find and remove all __pycache__ directories
    removed_count = 0
    for pycache_dir in root_path.rglob("__pycache__"):
        if pycache_dir.is_dir():
            try:
                shutil.rmtree(pycache_dir)
                print(f"  ✅ Removed {pycache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"  ⚠️ Could not remove {pycache_dir}: {e}")

    # Remove .pyc files
    pyc_count = 0
    for pyc_file in root_path.rglob("*.pyc"):
        try:
            pyc_file.unlink()
            pyc_count += 1
        except Exception as e:
            print(f"  ⚠️ Could not remove {pyc_file}: {e}")

    if pyc_count > 0:
        print(f"  ✅ Removed {pyc_count} .pyc files")

    if removed_count == 0 and pyc_count == 0:
        print("  ✨ No cache files found - already clean!")


def clean_temp_files(root_path):
    """Remove temporary files"""
    print("\n🗑️ Cleaning temporary files...")

    temp_patterns = ["*.tmp", "*.temp", "*.bak", "*.swp", "*.swo", "*~"]
    removed_count = 0

    for pattern in temp_patterns:
        for temp_file in root_path.rglob(pattern):
            if temp_file.is_file():
                try:
                    temp_file.unlink()
                    print(f"  ✅ Removed {temp_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ⚠️ Could not remove {temp_file}: {e}")

    if removed_count == 0:
        print("  ✨ No temporary files found - already clean!")


def clean_log_files(root_path):
    """Clean old log files but preserve recent ones"""
    print("\n📋 Cleaning old log files...")

    logs_dir = root_path / "logs"
    if not logs_dir.exists():
        print("  ✨ No logs directory found - already clean!")
        return

    removed_count = 0
    for log_file in logs_dir.rglob("*.log"):
        if log_file.is_file():
            # Keep recent logs (less than 7 days old)
            file_age = datetime.now().timestamp() - log_file.stat().st_mtime
            if file_age > 7 * 24 * 3600:  # 7 days
                try:
                    log_file.unlink()
                    print(f"  ✅ Removed old log: {log_file}")
                    removed_count += 1
                except Exception as e:
                    print(f"  ⚠️ Could not remove {log_file}: {e}")

    if removed_count == 0:
        print("  ✨ No old log files found - already optimized!")


def optimize_vscode_settings(root_path):
    """Optimize VS Code settings for better performance"""
    print("\n⚙️ Optimizing VS Code settings...")

    vscode_dir = root_path / ".vscode"
    if not vscode_dir.exists():
        vscode_dir.mkdir()

    settings_file = vscode_dir / "settings.json"

    # Optimal VS Code settings for large Python projects
    optimal_settings = """{
    "python.defaultInterpreterPath": "./venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.analysis.autoImportCompletions": true,
    "python.analysis.typeCheckingMode": "basic",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/node_modules": true,
        "**/.git": true,
        "**/.DS_Store": true,
        "**/Thumbs.db": true,
        "**/*.tmp": true,
        "**/*.temp": true
    },
    "search.exclude": {
        "**/node_modules": true,
        "**/bower_components": true,
        "**/*.code-search": true,
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/logs": true,
        "**/temp": true
    },
    "files.watcherExclude": {
        "**/.git/objects/**": true,
        "**/.git/subtree-cache/**": true,
        "**/node_modules/*/**": true,
        "**/__pycache__/**": true,
        "**/logs/**": true,
        "**/temp/**": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit"
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}"""

    try:
        with open(settings_file, "w", encoding="utf-8") as f:
            f.write(optimal_settings)
        print(f"  ✅ Optimized VS Code settings: {settings_file}")
    except Exception as e:
        print(f"  ⚠️ Could not update VS Code settings: {e}")


def generate_optimization_report(root_path):
    """Generate a summary report of the optimization"""
    print("\n📊 Generating optimization report...")

    report_dir = root_path / "documentation" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report_path = report_dir / "system_optimization_report.md"

    report_content = f"""# 🚀 System Optimization Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Status**: ✅ Complete

## Optimization Summary

### Performance Improvements
- 🧹 **Cache Cleanup**: Removed Python `__pycache__` directories and `.pyc` files
- 🗑️ **Temporary Files**: Cleared `.tmp`, `.temp`, `.bak`, and editor swap files
- 📋 **Log Management**: Cleaned old log files (keeping recent ones)
- ⚙️ **VS Code Settings**: Optimized for better indexing and performance

### Benefits Achieved
- 🚀 **Faster Startup**: Reduced file indexing time
- 🔍 **Better Search**: Optimized search exclusions
- 💾 **Disk Space**: Freed up unnecessary storage
- 🧭 **Navigation**: Cleaner file tree and faster browsing
- ⚡ **Performance**: Improved VS Code responsiveness

### Configuration Optimizations
- Python interpreter path configured
- File exclusions for better performance
- Search exclusions for relevant results
- Watcher exclusions to reduce CPU usage
- Auto-formatting and import organization enabled

## Recommended Next Steps
1. **Restart VS Code** to apply all optimizations
2. **Reload Window** if experiencing any issues
3. **Check Python Environment** is properly detected
4. **Verify Extensions** are working correctly

---
*Generated by system_optimization.py*
"""

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"  ✅ Report saved to: {report_path}")
    except Exception as e:
        print(f"  ⚠️ Could not save report: {e}")


def main():
    """Main optimization function"""
    print("🚀 aetherra System Optimization - Starting...")
    print("=" * 60)

    # Get the project root
    root_path = Path(r"c:\Users\enigm\Desktop\aetherra Project")

    if not root_path.exists():
        print(f"❌ Project root not found: {root_path}")
        sys.exit(1)

    print(f"📁 Optimizing workspace: {root_path}")

    # Perform optimization operations
    clean_cache_files(root_path)
    clean_temp_files(root_path)
    clean_log_files(root_path)
    optimize_vscode_settings(root_path)
    generate_optimization_report(root_path)

    print("\n" + "=" * 60)
    print("✨ System optimization complete!")
    print("🚀 Your workspace is now optimized for maximum performance!")
    print("\n💡 Tip: Restart VS Code to apply all optimizations")


if __name__ == "__main__":
    main()
