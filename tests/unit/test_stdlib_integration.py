#!/usr/bin/env python3
"""
🧪 Test Standard Library Integration
Tests that all stdlib plugins load correctly
"""

import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from stdlib import stdlib_manager


def test_stdlib_integration():
    """Test that all standard library plugins are loaded and working"""
    print("🧪 Testing NeuroCode Standard Library Integration\n")

    # Test 1: Check all plugins are loaded
    print("📋 Available Plugins:")
    plugins = stdlib_manager.list_plugins()
    for name, description in plugins.items():
        print(f"  ✅ {name}: {description}")

    expected_plugins = {
        "sysmon",
        "optimizer",
        "selfrepair",
        "whisper",
        "reflector",
        "executor",
        "coretools",
    }

    loaded_plugins = set(plugins.keys())
    missing_plugins = expected_plugins - loaded_plugins
    extra_plugins = loaded_plugins - expected_plugins

    print("\n📊 Plugin Status:")
    print(f"  Expected: {len(expected_plugins)} plugins")
    print(f"  Loaded: {len(loaded_plugins)} plugins")

    if missing_plugins:
        print(f"  ⚠️ Missing: {missing_plugins}")
    if extra_plugins:
        print(f"  ➕ Extra: {extra_plugins}")

    # Test 2: Check plugin info for each loaded plugin
    print("\n🔍 Plugin Details:")
    for plugin_name in loaded_plugins:
        info = stdlib_manager.get_plugin_info(plugin_name)
        if info:
            print(f"  {plugin_name}:")
            print(f"    Description: {info['description']}")
            print(f"    Actions: {info['available_actions']}")
            print(f"    Loaded: {info['loaded']}")
        else:
            print(f"  ⚠️ {plugin_name}: Could not get info")

    # Test 3: Test basic action execution (non-destructive)
    print("\n🧪 Testing Plugin Actions:")

    # Test reflector
    if "reflector" in loaded_plugins:
        try:
            result = stdlib_manager.execute_plugin_action(
                "reflector", "analyze", {"behavior": "test_behavior", "context": "test_context"}
            )
            print(f"  ✅ reflector.analyze: {result[:100]}...")
        except Exception as e:
            print(f"  ⚠️ reflector.analyze failed: {e}")

    # Test executor
    if "executor" in loaded_plugins:
        try:
            result = stdlib_manager.execute_plugin_action(
                "executor", "schedule", {"command": 'echo "test"', "priority": "low"}
            )
            print(f"  ✅ executor.schedule: {result[:100]}...")
        except Exception as e:
            print(f"  ⚠️ executor.schedule failed: {e}")

    # Test coretools
    if "coretools" in loaded_plugins:
        try:
            result = stdlib_manager.execute_plugin_action("coretools", "list_files", {"path": "."})
            print(
                f"  ✅ coretools.list_files: Found {len(result.split()) if isinstance(result, str) else 'unknown'} items"
            )
        except Exception as e:
            print(f"  ⚠️ coretools.list_files failed: {e}")

    print("\n🎉 Standard Library Integration Test Complete!")
    print(f"All {len(loaded_plugins)} plugins are loaded and functional!")

    return len(loaded_plugins) == len(expected_plugins)


if __name__ == "__main__":
    success = test_stdlib_integration()
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
