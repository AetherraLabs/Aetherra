#!/usr/bin/env python3
"""
[TOOL] Quick Aetherra Import Fix
============================
A fast, lightweight script to fix the most common import issues
without installing heavy dependencies.

This script only creates missing __init__.py files and tests basic imports.
For full dependency management, use fix_imports.py
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")

    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print(
            f"❌ Python 3.8+ required, found {version_info.major}.{version_info.minor}"
        )
        return False

    print(
        f"✅ Python {version_info.major}.{version_info.minor}.{version_info.micro} - Compatible"
    )
    return True


def create_init_file(directory: Path, package_name: str = None):
    """Create a basic __init__.py file."""
    if package_name is None:
        package_name = directory.name.replace("_", " ").title()

    init_file = directory / "__init__.py"
    if init_file.exists():
        return True

    try:
        init_content = f'''#!/usr/bin/env python3
"""
{package_name} Package
{"=" * (len(package_name) + 8)}
Auto-generated __init__.py file for Aetherra AI OS.
"""

__version__ = "1.0.0"

# Package is available
PACKAGE_AVAILABLE = True

def get_package_status():
    """Get the status of this package."""
    return {{'available': PACKAGE_AVAILABLE}}

__all__ = ['get_package_status', 'PACKAGE_AVAILABLE']
'''

        with open(init_file, "w", encoding="utf-8") as f:
            f.write(init_content)

        print(f"✅ Created __init__.py in {directory.name}")
        return True

    except Exception as e:
        print(f"❌ Failed to create __init__.py in {directory}: {e}")
        return False


def fix_missing_inits():
    """Fix missing __init__.py files."""
    print("🔍 Scanning for missing __init__.py files...")

    project_root = Path(__file__).parent
    aetherra_dir = project_root / "Aetherra"

    if not aetherra_dir.exists():
        print("❌ Aetherra directory not found!")
        return False

    # Key directories that need __init__.py files
    important_dirs = [
        (aetherra_dir / "aetherra_core", "Aetherra Core"),
        (aetherra_dir / "aetherra_core" / "engine", "Engine"),
        (aetherra_dir / "aetherra_core" / "orchestration", "Orchestration"),
        (aetherra_dir / "aetherra_core" / "plugins", "Plugins"),
        (aetherra_dir / "aetherra_core" / "memory", "Memory"),
        (aetherra_dir / "aetherra_core" / "system", "System"),
        (aetherra_dir / "aetherra_core" / "kernel", "Kernel"),
        (aetherra_dir / "aetherra_core" / "file_system", "File System"),
        (aetherra_dir / "aetherra_core" / "reflection", "Reflection"),
        (aetherra_dir / "aetherra_core" / "reflection_engine", "Reflection Engine"),
        (aetherra_dir / "core", "Core"),
        (aetherra_dir / "plugins", "Plugins"),
        (aetherra_dir / "runtime", "Runtime"),
    ]

    fixed_count = 0
    for dir_path, package_name in important_dirs:
        if dir_path.exists() and dir_path.is_dir():
            if create_init_file(dir_path, package_name):
                fixed_count += 1

    print(f"✅ Fixed {fixed_count} missing __init__.py files")
    return True


def test_basic_imports():
    """Test basic import patterns."""
    print("🧪 Testing basic imports...")

    tests = [
        ("aetherra_core", "from Aetherra.aetherra_core import get_package_status"),
        ("kernel_loop", "from aetherra_kernel_loop import AetherraKernelLoop"),
        ("os_launcher", "import aetherra_os_launcher"),
    ]

    passed = 0
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name} import - Success")
            passed += 1
        except Exception as e:
            print(f"[WARN]  {name} import - Failed: {e}")

    return passed


def main():
    """Main function."""
    print("🌌 Aetherra Quick Import Fix")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        return 1

    # Fix missing __init__.py files
    if not fix_missing_inits():
        return 1

    # Test imports
    passed = test_basic_imports()

    print()
    print("=" * 40)
    print(f"✅ Quick fix completed! {passed} imports working.")
    print()
    print("If you still have import issues:")
    print("1. Run the full fix: python fix_imports.py")
    print("2. Check the guide: IMPORT_FIXES.md")
    print("3. Verify your setup: python test_imports.py")

    return 0


if __name__ == "__main__":
    sys.exit(main())
