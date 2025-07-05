#!/usr/bin/env python3
"""Test script to check all aetherra imports and identify any issues."""

import os
import sys
import traceback

# Add the current directory to path so we can import Aetherra
sys.path.insert(0, os.path.dirname(__file__))


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
    print("Testing aetherra imports...")
    print("=" * 50)

    # Test main package
    test_import("Aetherra", "Main package")

    # Test core modules
    test_import("Aetherra.core", "Core module")
    test_import("Aetherra.core.aetherra_parser", "Parser module")
    test_import("Aetherra.core.aetherra_interpreter", "Interpreter module")
    test_import("Aetherra.core.ai", "AI module")
    test_import("Aetherra.core.memory", "Memory module")
    test_import("Aetherra.core.chat_router", "Chat router module")

    # Test UI modules
    test_import("Aetherra.ui", "UI module")

    # Test plugins
    test_import("Aetherra.plugins", "Plugins module")

    # Test specific components
    test_import("Aetherra.core.aetherra_parser", "Core parser")
    test_import("Aetherra.core.interpreter.base", "Base interpreter")
    test_import("Aetherra.core.ai.multi_llm_manager", "Multi LLM manager")
    test_import("Aetherra.core.plugin_manager", "Plugin manager")

    print("=" * 50)
    print("Import testing complete.")


if __name__ == "__main__":
    main()
