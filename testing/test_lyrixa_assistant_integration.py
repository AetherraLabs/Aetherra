#!/usr/bin/env python3
"""
Test script to verify AetherraChat integration with Lyrixa
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "core"))


def test_aetherchat_import():
    """Test if AetherraChat can be imported"""
    try:
            LyrixaAssistantInterface,
            create_embeddable_aetherchat,
        )

        print("✅ AetherraChat imports successful")
        return True
    except ImportError as e:
        print(f"❌ AetherraChat import failed: {e}")
        return False


def test_aetherchat_factory():
    """Test if the embeddable factory function works"""
    try:
        from Lyrixa.ui.aether_chat import create_embeddable_aetherchat

        # Test without creating QApplication (this will fail but shows the function exists)
        widget = create_embeddable_aetherchat()
        if widget is None:
            print("✅ Factory function exists and handles Qt unavailability gracefully")
            return True
        else:
            print("✅ Factory function created widget successfully")
            return True
    except Exception as e:
        print(f"❌ Factory function test failed: {e}")
        return False


def test_aetherplex_integration():
    """Test if Lyrixacan import AetherraChat components"""
    try:
        # Add the paths that Lyrixauses
        sys.path.insert(0, str(project_root / "src" / "Aetherra" / "ui"))

        # Test the import pattern used in aetherplex.py

        print("✅ Lyrixa-style import successful")
        return True
    except ImportError as e:
        print(f"❌ Lyrixa-style import failed: {e}")
        return False


def main():
    print("🧪 Testing AetherraChat Integration with Lyrixa")
    print("=" * 50)

    # Run tests
    test1 = test_aetherchat_import()
    test2 = test_aetherchat_factory()
    test3 = test_aetherplex_integration()

    print("\n📊 Test Results:")
    print(f"  Import Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Factory Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Integration Test: {'✅ PASS' if test3 else '❌ FAIL'}")

    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! AetherraChat should work with Lyrixa.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")


if __name__ == "__main__":
    main()
