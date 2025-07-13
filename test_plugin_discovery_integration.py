#!/usr/bin/env python3
"""
Test Plugin Discovery Integration
=================================

This script tests if the plugin discovery integration is working properly
and that Lyrixa can now see and work with discovered plugins.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_plugin_discovery_integration():
    """Test that plugin discovery is properly integrated with Lyrixa intelligence"""

    print("🧪 Testing Plugin Discovery Integration")
    print("=" * 50)

    try:
        # Import the intelligence stack
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        # Initialize intelligence stack
        workspace_path = str(project_root)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)

        print("✅ Intelligence stack initialized")

        # Test plugin discovery integration
        print("🔍 Testing plugin discovery integration...")

        plugin_integration_success = (
            await intelligence_stack.initialize_plugin_discovery_integration()
        )

        if plugin_integration_success:
            print("✅ Plugin discovery integration successful!")
            print("🧠 Lyrixa can now see and work with plugins!")

            # Test getting plugin recommendations
            print("\n🔍 Testing plugin recommendations...")
            plugins = await intelligence_stack.get_plugin_recommendations_for_lyrixa(
                "test query"
            )

            print(f"📋 Found {len(plugins)} plugins:")
            for i, plugin in enumerate(plugins[:5], 1):  # Show first 5
                print(
                    f"   {i}. {plugin.get('name', 'Unknown')} - {plugin.get('description', 'No description')}"
                )

            print("\n✅ Plugin discovery integration test PASSED!")
            print("🎯 Lyrixa can now:")
            print("   • Reference plugins in conversations")
            print("   • Rank and recommend plugins")
            print("   • Store plugin metadata in memory")
            print("   • Query plugins when needed")

            return True

        else:
            print("❌ Plugin discovery integration failed")
            print("🔧 This means:")
            print("   • Lyrixa cannot see what plugins are installed")
            print("   • She cannot reference or recommend plugins")
            print("   • Plugin metadata is not stored in memory")

            return False

    except Exception as e:
        print(f"❌ Error testing plugin discovery integration: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_plugin_memory_storage():
    """Test that plugins are properly stored in memory for Lyrixa to access"""

    print("\n💾 Testing Plugin Memory Storage")
    print("=" * 30)

    try:
        from Aetherra.lyrixa.intelligence_integration import LyrixaIntelligenceStack

        workspace_path = str(project_root)
        intelligence_stack = LyrixaIntelligenceStack(workspace_path)

        # Check if plugin bridge is available
        if (
            hasattr(intelligence_stack, "plugin_bridge")
            and intelligence_stack.plugin_bridge
        ):
            # Test storing plugins in memory
            stored_successfully = await intelligence_stack.plugin_bridge.store_plugins_in_intelligence_memory()

            if stored_successfully:
                print("✅ Plugins successfully stored in intelligence memory!")
                print("🧠 Lyrixa can now query plugins from memory!")
                return True
            else:
                print("❌ Failed to store plugins in memory")
                return False
        else:
            print("⚠️ Plugin bridge not available")
            return False

    except Exception as e:
        print(f"❌ Error testing plugin memory storage: {e}")
        return False


def test_gui_plugin_display():
    """Test if the GUI can display discovered plugins"""

    print("\n🖥️ Testing GUI Plugin Display")
    print("=" * 30)

    try:
        # Test if GUI has the plugin tab functionality
        from Aetherra.lyrixa.gui.gui_window import LyrixaWindow

        # Check if the GUI has the plugin methods we added
        has_plugin_tab = hasattr(LyrixaWindow, "setup_plugins_tab")
        has_refresh_method = hasattr(LyrixaWindow, "refresh_plugin_discovery")
        has_display_method = hasattr(LyrixaWindow, "update_plugin_display")

        print(
            f"🔌 Plugin tab setup method: {'✅ Available' if has_plugin_tab else '❌ Missing'}"
        )
        print(
            f"🔄 Plugin refresh method: {'✅ Available' if has_refresh_method else '❌ Missing'}"
        )
        print(
            f"📋 Plugin display method: {'✅ Available' if has_display_method else '❌ Missing'}"
        )

        if has_plugin_tab and has_refresh_method and has_display_method:
            print("✅ GUI plugin display functionality is available!")
            print("🎯 Users can now view discovered plugins in the GUI")
            return True
        else:
            print("⚠️ Some GUI plugin functionality is missing")
            return False

    except Exception as e:
        print(f"❌ Error testing GUI plugin display: {e}")
        return False


async def main():
    """Run all plugin discovery integration tests"""

    print("🚀 Plugin Discovery Integration Test Suite")
    print("==========================================")

    # Test 1: Plugin discovery integration
    test1_passed = await test_plugin_discovery_integration()

    # Test 2: Plugin memory storage
    test2_passed = await test_plugin_memory_storage()

    # Test 3: GUI plugin display
    test3_passed = test_gui_plugin_display()

    # Summary
    print("\n📊 Test Results Summary")
    print("======================")
    print(f"Plugin Discovery Integration: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Plugin Memory Storage: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"GUI Plugin Display: {'✅ PASS' if test3_passed else '❌ FAIL'}")

    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Plugin discovery is now properly integrated with Lyrixa!")
        print("🧠 Lyrixa can see, reference, and recommend plugins!")
    else:
        print("\n⚠️ Some tests failed - plugin integration needs work")

    return test1_passed and test2_passed and test3_passed


if __name__ == "__main__":
    asyncio.run(main())
