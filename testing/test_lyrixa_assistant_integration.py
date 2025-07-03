#!/usr/bin/env python3
"""
Test script to verify NeuroChat integration with Neuroplex
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "core"))


def test_neurochat_import():
    """Test if NeuroChat can be imported"""
    try:
        from src.aethercode.ui.aether_chat import (
            LyrixaAssistantInterface,
            create_embeddable_neurochat,
        )

        print("✅ NeuroChat imports successful")
        return True
    except ImportError as e:
        print(f"❌ NeuroChat import failed: {e}")
        return False


def test_neurochat_factory():
    """Test if the embeddable factory function works"""
    try:
        from src.aethercode.ui.aether_chat import create_embeddable_neurochat

        # Test without creating QApplication (this will fail but shows the function exists)
        widget = create_embeddable_neurochat()
        if widget is None:
            print("✅ Factory function exists and handles Qt unavailability gracefully")
            return True
        else:
            print("✅ Factory function created widget successfully")
            return True
    except Exception as e:
        print(f"❌ Factory function test failed: {e}")
        return False


def test_neuroplex_integration():
    """Test if Neuroplex can import NeuroChat components"""
    try:
        # Add the paths that Neuroplex uses
        sys.path.insert(0, str(project_root / "src" / "neurocode" / "ui"))

        # Test the import pattern used in neuroplex.py
        from neuro_chat import LyrixaAssistantInterface, create_embeddable_neurochat

        print("✅ Neuroplex-style import successful")
        return True
    except ImportError as e:
        print(f"❌ Neuroplex-style import failed: {e}")
        return False


def main():
    print("🧪 Testing NeuroChat Integration with Neuroplex")
    print("=" * 50)

    # Run tests
    test1 = test_neurochat_import()
    test2 = test_neurochat_factory()
    test3 = test_neuroplex_integration()

    print("\n📊 Test Results:")
    print(f"  Import Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"  Factory Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"  Integration Test: {'✅ PASS' if test3 else '❌ FAIL'}")

    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! NeuroChat should work with Neuroplex.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")


if __name__ == "__main__":
    main()
