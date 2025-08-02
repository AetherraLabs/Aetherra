#!/usr/bin/env python3
"""
🧪 Import Test Suite for Contributors
=====================================
Test script to verify that import issues have been resolved
after forking/cloning the Aetherra repository.

This script tests the most common import patterns that
contributors need to use.
"""

import sys
import traceback


def test_import(description, import_statement):
    """Test a single import statement."""
    try:
        exec(import_statement)
        print(f"✅ {description}: SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {description}: FAILED - {str(e)}")
        return False


def main():
    """Run all import tests."""
    print("🌌 Aetherra Import Test Suite")
    print("=" * 40)
    print(f"Python Version: {sys.version}")
    print(f"Python Path: {sys.executable}")
    print()

    tests = [
        (
            "Basic aetherra_core import",
            "from Aetherra.aetherra_core import get_system_status",
        ),
        (
            "Engine module import",
            "from Aetherra.aetherra_core.engine import get_engine_status",
        ),
        (
            "Memory module import",
            "from Aetherra.aetherra_core.memory import MEMORY_AVAILABLE",
        ),
        (
            "Config module import",
            "from Aetherra.aetherra_core.config import CONFIG_AVAILABLE",
        ),
        ("Core module import", "from Aetherra.core import get_package_status"),
        ("Plugins module import", "from Aetherra.plugins import get_package_status"),
        ("Runtime module import", "from Aetherra.runtime import get_package_status"),
        ("Kernel loop import", "from aetherra_kernel_loop import AetherraKernelLoop"),
        (
            "Service registry import",
            "from aetherra_service_registry import ServiceRegistry",
        ),
        ("OS launcher import", "import aetherra_os_launcher"),
        ("Startup script import", "import aetherra_startup"),
    ]

    passed = 0
    failed = 0

    print("Running import tests...")
    print("-" * 40)

    for description, import_statement in tests:
        if test_import(description, import_statement):
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 40)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All imports working! You're ready to contribute to Aetherra!")
    else:
        print("⚠️  Some imports failed. This is normal for optional modules.")
        print("   Key imports (aetherra_core, engine, core) should work.")
        print("   If basic imports fail, run: python fix_imports.py")

    print()
    print("Next steps:")
    print("1. Read CONTRIBUTING.md for development guidelines")
    print("2. Install VS Code extensions (see CONTRIBUTING.md)")
    print("3. Set up your .env file with API keys")
    print("4. Start coding! 🚀")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
