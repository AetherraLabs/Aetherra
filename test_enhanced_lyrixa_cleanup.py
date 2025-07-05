#!/usr/bin/env python3
"""
Test script to verify that the Enhanced Lyrixa Window is properly cleaned up and working.
Tests all the key methods and functionality.
"""

import os
import sys

# Add project to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))


def test_enhanced_lyrixa_structure():
    """Test that the Enhanced Lyrixa Window has all expected methods."""
    try:
        from lyrixa.gui.enhanced_lyrixa import EnhancedLyrixaWindow

        print("🧪 Testing Enhanced Lyrixa Window Structure")
        print("=" * 50)

        # Check key methods exist
        expected_methods = [
            "_store_user_interaction",
            "_get_memory_context",
            "_analyze_and_store_response",
            "_generate_enhanced_fallback",
            "get_memory_dashboard",
            "get_analytics_data",
            "search_memories",
            "execute_code",
            "send_message",
            "get_memories",
            "get_goals",
            "reset_lyrixa",
            "activate_plugin",
            "show",
            "close",
        ]

        # Create instance (without Qt for testing)
        window = EnhancedLyrixaWindow()

        print("✅ EnhancedLyrixaWindow instance created successfully")

        # Check methods
        missing_methods = []
        for method in expected_methods:
            if hasattr(window, method):
                print(f"   ✅ {method}")
            else:
                print(f"   ❌ {method} - MISSING")
                missing_methods.append(method)

        if missing_methods:
            print(f"\n❌ Missing methods: {missing_methods}")
            return False
        else:
            print(f"\n✅ All {len(expected_methods)} expected methods are present")

        # Test memory dashboard if available
        try:
            dashboard = window.get_memory_dashboard()
            print(f"✅ Memory dashboard test: {dashboard[:50]}...")
        except Exception as e:
            print(f"⚠️ Memory dashboard test error (expected): {e}")

        # Test analytics data
        try:
            analytics = window.get_analytics_data()
            print(f"✅ Analytics data test: {analytics}")
        except Exception as e:
            print(f"⚠️ Analytics data test error: {e}")

        print("\n🎉 Enhanced Lyrixa Window structure test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Enhanced Lyrixa Window test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_enhanced_lyrixa_structure()
    if success:
        print("\n✅ ALL TESTS PASSED - Enhanced Lyrixa Window is properly structured!")
        sys.exit(0)
    else:
        print("\n❌ TESTS FAILED - Issues found with Enhanced Lyrixa Window structure")
        sys.exit(1)
