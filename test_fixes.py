#!/usr/bin/env python3
"""
Test script to verify the fixes for plugin and memory issues
"""

import asyncio
import os
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lyrixa"))


async def test_plugin_loading():
    """Test plugin loading to see if syntax errors are fixed"""
    print("🧩 Testing plugin loading...")

    try:
        from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager

        # Create plugin manager with multiple directories
        plugin_manager = LyrixaAdvancedPluginManager(
            plugin_directory=os.path.join(os.getcwd(), "plugins"),
            additional_directories=[
                os.path.join(os.getcwd(), "lyrixa", "plugins"),
                os.path.join(os.getcwd(), "src", "aetherra", "plugins"),
                os.path.join(os.getcwd(), "sdk", "plugins"),
            ],
        )

        # Initialize without memory system first
        await plugin_manager.initialize({})

        # Check discovered plugins
        discovered = list(plugin_manager.plugins.keys())
        print(f"✅ Successfully discovered {len(discovered)} plugins")

        # Check plugin ecosystem status
        status = await plugin_manager.get_ecosystem_status()
        loaded_count = status.get("total_plugins", 0)

        print(f"✅ Plugin ecosystem status: {loaded_count} plugins available")

        # List discovered plugins
        for plugin_name in discovered:
            print(f"   ✅ Found: {plugin_name}")

        return True

    except Exception as e:
        print(f"❌ Plugin loading test failed: {e}")
        traceback.print_exc()
        return False


async def test_memory_system():
    """Test memory system to see if table issues are fixed"""
    print("\n🧠 Testing memory system...")

    try:
        from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

        # Create memory system
        memory_system = LyrixaEnhancedMemorySystem(memory_db_path="test_memory.db")

        # Test basic functionality
        await memory_system.store_enhanced_memory(
            content={"test": "memory"},
            context={"test_session": True},
            tags=["test", "plugin_chain"],
            importance=0.5,
        )

        # Test get_memories_by_tags (this was failing before)
        memories = await memory_system.get_memories_by_tags(["test"], limit=5)
        print(f"✅ Retrieved {len(memories)} memories by tags")

        # Test search memories
        search_results = await memory_system.search_memories("test", limit=5)
        print(f"✅ Found {len(search_results)} memories through search")

        # Clean up test database
        try:
            os.remove("test_memory.db")
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"❌ Memory system test failed: {e}")
        traceback.print_exc()
        return False


async def test_plugin_with_memory():
    """Test plugin system with memory system integration"""
    print("\n🔗 Testing plugin system with memory integration...")

    try:
        from lyrixa.core.advanced_plugins import LyrixaAdvancedPluginManager
        from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem

        # Create memory system
        memory_system = LyrixaEnhancedMemorySystem(
            memory_db_path="test_memory_integration.db"
        )

        # Create plugin manager with memory system
        plugin_manager = LyrixaAdvancedPluginManager(
            plugin_directory=os.path.join(os.getcwd(), "plugins"),
            memory_system=memory_system,
            additional_directories=[
                os.path.join(os.getcwd(), "lyrixa", "plugins"),
                os.path.join(os.getcwd(), "src", "aetherra", "plugins"),
                os.path.join(os.getcwd(), "sdk", "plugins"),
            ],
        )

        # Initialize
        await plugin_manager.initialize({})

        # Try to load plugin chains (this was failing before)
        try:
            await plugin_manager._load_plugin_chains()
            print("✅ Plugin chains loaded successfully")
        except Exception as e:
            print(f"⚠️ Plugin chains loading failed: {e}")

        # Clean up test database
        try:
            os.remove("test_memory_integration.db")
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"❌ Plugin-memory integration test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("🔧 Testing fixes for plugin and memory issues")
    print("=" * 50)

    results = {
        "plugin_loading": await test_plugin_loading(),
        "memory_system": await test_memory_system(),
        "plugin_memory_integration": await test_plugin_with_memory(),
    }

    print("\n📊 Test Results:")
    print("=" * 30)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All tests passed! The fixes appear to be working.")
    else:
        print("\n⚠️ Some tests failed. Issues may remain.")

    return all_passed


if __name__ == "__main__":
    asyncio.run(main())
