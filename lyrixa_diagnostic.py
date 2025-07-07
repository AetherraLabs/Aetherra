#!/usr/bin/env python3
"""
🔍 LYRIXA ERROR DIAGNOSTIC
========================

Quick diagnostic to find any errors in the lyrixa system.
"""

import sys
import traceback
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def test_imports():
    """Test all critical imports."""
    errors = []

    try:
        print("🔍 Testing core imports...")
        from lyrixa.core import conversation, goals, memory, plugin_system

        print("   ✅ Core modules imported")
    except Exception as e:
        errors.append(f"Core imports failed: {e}")
        traceback.print_exc()

    try:
        print("🔍 Testing GUI imports...")
        from lyrixa.gui import configuration_manager, enhanced_lyrixa

        print("   ✅ GUI modules imported")
    except Exception as e:
        errors.append(f"GUI imports failed: {e}")
        traceback.print_exc()

    try:
        print("🔍 Testing plugin imports...")
        from lyrixa.plugins import enhanced_plugin_manager, plugin_analytics

        print("   ✅ Plugin modules imported")
    except Exception as e:
        errors.append(f"Plugin imports failed: {e}")
        traceback.print_exc()

    try:
        print("🔍 Testing interface imports...")
        from lyrixa.interfaces import lyrixa, lyrixa_assistant

        print("   ✅ Interface modules imported")
    except Exception as e:
        errors.append(f"Interface imports failed: {e}")
        traceback.print_exc()

    return errors


def test_basic_functionality():
    """Test basic functionality."""
    errors = []

    try:
        print("🔍 Testing memory system...")
        from lyrixa.core.memory import LyrixaMemorySystem

        memory_system = LyrixaMemorySystem()
        print("   ✅ Memory system created")
    except Exception as e:
        errors.append(f"Memory system failed: {e}")
        traceback.print_exc()

    try:
        print("🔍 Testing plugin system...")
        from lyrixa.core.plugin_system import LyrixaPluginSystem

        plugin_system = LyrixaPluginSystem()
        print("   ✅ Plugin system created")
    except Exception as e:
        errors.append(f"Plugin system failed: {e}")
        traceback.print_exc()

    try:
        print("🔍 Testing confidence system...")
        from lyrixa.core.plugin_confidence_system import PluginScorer

        scorer = PluginScorer()
        print("   ✅ Confidence system created")
    except Exception as e:
        errors.append(f"Confidence system failed: {e}")
        traceback.print_exc()

    return errors


def main():
    print("🔍 LYRIXA ERROR DIAGNOSTIC")
    print("=" * 40)

    all_errors = []

    # Test imports
    import_errors = test_imports()
    all_errors.extend(import_errors)

    # Test basic functionality
    func_errors = test_basic_functionality()
    all_errors.extend(func_errors)

    print("\n" + "=" * 40)
    if not all_errors:
        print("🎉 NO ERRORS FOUND!")
        print("✅ All systems operational")
    else:
        print(f"❌ {len(all_errors)} ERRORS FOUND:")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")

    return len(all_errors)


if __name__ == "__main__":
    main()
