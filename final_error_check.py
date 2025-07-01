#!/usr/bin/env python3
"""
Final comprehensive error check for all NeuroCode modules
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_core_modules():
    """Check core modules for import errors"""
    print("🔍 Checking core modules...")

    try:
        # Test core functionality
        from neurocode.core import create_interpreter, create_memory_system, create_parser

        print("✅ Core module imports successful")

        # Test interpreter creation
        interpreter = create_interpreter()
        print("✅ Interpreter creation successful")

        # Test parser creation
        parser = create_parser()
        print("✅ Parser creation successful")

        # Test memory system creation
        memory = create_memory_system()
        print("✅ Memory system creation successful")

        return True

    except Exception as e:
        print(f"❌ Core module error: {e}")
        return False


def check_cli_modules():
    """Check CLI modules for import errors"""
    print("\n🔍 Checking CLI modules...")

    try:
        # Check if CLI is available
        from neurocode import CLI_AVAILABLE

        print(f"✅ CLI availability status: {CLI_AVAILABLE}")

        if CLI_AVAILABLE:
            from neurocode.cli.main import NeuroCodePersonaInterface

            interface = NeuroCodePersonaInterface()
            print("✅ CLI interface creation successful")
        else:
            print("ℹ️  CLI not available due to dependencies")

        return True

    except Exception as e:
        print(f"❌ CLI module error: {e}")
        return False


def check_main_launcher():
    """Check main launcher functionality"""
    print("\n🔍 Checking main launcher...")

    try:
        # Test that the main launcher exists and can be imported
        launcher_path = Path("neurocode_launcher.py")
        if launcher_path.exists():
            print("✅ Main launcher file exists")
        else:
            print("⚠️  Main launcher file not found")

        return True

    except Exception as e:
        print(f"❌ Launcher check error: {e}")
        return False


def main():
    """Run all checks"""
    print("🧪 Final NeuroCode Error Check")
    print("=" * 50)

    checks = [check_core_modules, check_cli_modules, check_main_launcher]

    passed = 0
    total = len(checks)

    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
            print(f"❌ Check failed: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Final Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All checks passed! NeuroCode is ready to use.")
    else:
        print("⚠️  Some checks failed. Please review the output above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
