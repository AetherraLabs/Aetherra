#!/usr/bin/env python3
"""Test script to check all neurocode imports and identify any issues."""

import os
import sys
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_import(module_name, description=""):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✅ {module_name} - {description}")
        return True
    except Exception as e:
        print(f"❌ {module_name} - {description}")
        print(f"   Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run comprehensive import tests."""
#     print("Testing NeuroCode imports...")
    print("=" * 50)

    # Test main package
    test_import("neurocode", "Main package")

    # Test core modules
    test_import("neurocode.core", "Core module")
    test_import("neurocode.core.parser", "Parser module")
    test_import("neurocode.core.interpreter", "Interpreter module")
    test_import("neurocode.core.ai", "AI module")
    test_import("neurocode.core.memory", "Memory module")
    test_import("neurocode.core.utils", "Utils module")

    # Test UI modules
    test_import("neurocode.ui", "UI module")

    # Test CLI modules
    test_import("neurocode.cli", "CLI module")

    # Test plugins
    test_import("neurocode.plugins", "Plugins module")

    # Test specific components
    test_import("neurocode.core.parser.parser", "Core parser")
    test_import("neurocode.core.interpreter.base", "Base interpreter")
    test_import("neurocode.core.ai.runtime", "AI runtime")
    test_import("neurocode.plugins.manager", "Plugin manager")

    print("=" * 50)
    print("Import testing complete.")

if __name__ == "__main__":
    main()
