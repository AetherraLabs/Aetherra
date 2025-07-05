#!/usr/bin/env python3
"""Test script to check all Aetherra imports and identify any issues."""

import os
import sys
import traceback

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


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
    #     print("Testing Aetherra imports...")
    print("=" * 50)

    # Test main package
    test_import("Aetherra", "Main package")

    # Test core modules
    test_import("Aetherra.core", "Core module")
    test_import("Aetherra.core.parser", "Parser module")
    test_import("Aetherra.core.interpreter", "Interpreter module")
    test_import("Aetherra.core.ai", "AI module")
    test_import("Aetherra.core.memory", "Memory module")
    test_import("Aetherra.core.utils", "Utils module")

    # Test UI modules
    test_import("Aetherra.ui", "UI module")

    # Test CLI modules
    test_import("Aetherra.cli", "CLI module")

    # Test plugins
    test_import("Aetherra.plugins", "Plugins module")

    # Test specific components
    test_import("Aetherra.core.parser.parser", "Core parser")
    test_import("Aetherra.core.interpreter.base", "Base interpreter")
    test_import("Aetherra.core.ai.runtime", "AI runtime")
    test_import("Aetherra.plugins.manager", "Plugin manager")

    print("=" * 50)
    print("Import testing complete.")


if __name__ == "__main__":
    main()
