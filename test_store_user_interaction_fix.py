#!/usr/bin/env python3
"""
Test to verify the _store_user_interaction method fix
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "lyrixa"))
sys.path.insert(0, str(project_root / "src"))


def test_store_user_interaction_fix():
    """Test that the _store_user_interaction method exists."""
    print("🧪 TESTING _store_user_interaction FIX")
    print("=" * 45)

    try:
        from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("✅ Enhanced Lyrixa window import successful")

        # Create window instance
        window = EnhancedLyrixaWindow()
        print("✅ Enhanced Lyrixa window created successfully")

        # Check if the method exists
        if hasattr(window, "_store_user_interaction"):
            print("✅ _store_user_interaction method found!")
        else:
            print("❌ _store_user_interaction method still missing")
            return False

        # Check if the other missing method exists
        if hasattr(window, "_get_memory_context"):
            print("✅ _get_memory_context method found!")
        else:
            print("❌ _get_memory_context method still missing")
            return False

        print("\n✅ MISSING METHODS FIXED!")
        print("   The '_store_user_interaction' error should be resolved")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_store_user_interaction_fix():
        print("\n🎯 STORE USER INTERACTION FIX VERIFIED")
        print("   The error should no longer occur in Lyrixa GUI")
    else:
        print("\n❌ STORE USER INTERACTION FIX FAILED")
        sys.exit(1)
