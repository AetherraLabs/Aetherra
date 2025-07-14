# test_plugin_intelligence_fix.py
# 🔧 Test the Plugin Intelligence Bridge Fix

import sys
from pathlib import Path

# Add lyrixa to path
sys.path.insert(0, str(Path(__file__).parent / "Aetherra" / "lyrixa"))

def test_plugin_intelligence_bridge_validation():
    """Test that the plugin intelligence bridge validation is fixed"""
    print("🔧 Testing Plugin Intelligence Bridge Validation Fix")
    print("=" * 60)

    try:
        # Import the fixed bridge
        from Aetherra.lyrixa.core.plugin_intelligence_bridge import PluginIntelligenceBridge

        # Create bridge instance
        bridge = PluginIntelligenceBridge()

        # Test validation logic
        print("📋 Testing manager validation logic...")

        # Create a mock system manager with correct methods
        class MockSystemManager:
            def list_plugins(self):
                return {"test_plugin": "test_data"}

            def get_plugin_info(self, name):
                return {"name": name, "version": "1.0.0"}

        mock_manager = MockSystemManager()

        # Test validation
        is_valid = bridge._validate_manager_connection("system", mock_manager)

        print(f"✅ System manager validation result: {is_valid}")

        if is_valid:
            print("🎉 Fix successful! System manager validation now passes")
        else:
            print("❌ Fix failed - validation still failing")

        # Test with missing methods
        class MockInvalidManager:
            def some_other_method(self):
                pass

        invalid_manager = MockInvalidManager()
        is_invalid = bridge._validate_manager_connection("system", invalid_manager)

        print(f"✅ Invalid manager validation result: {is_invalid}")

        if not is_invalid:
            print("✅ Correctly rejects invalid managers")
        else:
            print("⚠️ Still accepting invalid managers")

        print("\n🔍 Summary:")
        print(f"   Valid manager passes: {is_valid}")
        print(f"   Invalid manager rejected: {not is_invalid}")

        if is_valid and not is_invalid:
            print("✅ Plugin Intelligence Bridge validation is working correctly!")
        else:
            print("❌ Validation logic needs more work")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plugin_intelligence_bridge_validation()
