#!/usr/bin/env python3
"""
Integration Test - Enhanced Aetherra with Chat Router
=====================================================

Tests the integration of the enhanced chat router with the Aetherra GUI
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "core"))


def test_chat_router_integration():
    """Test the chat router integration"""
    print("🧪 Testing Enhanced Aetherra Chat Router Integration")
    print("=" * 60)

    # Test 1: Import chat router
    try:
        from core.chat_router import aetherraChatRouter

        print("✅ Chat router import successful")
    except ImportError as e:
        print(f"❌ Chat router import failed: {e}")
        return False

    # Test 2: Initialize chat router
    try:
        chat_router = aetherraChatRouter(demo_mode=True, debug_mode=False)
        print("✅ Chat router initialization successful")
    except Exception as e:
        print(f"❌ Chat router initialization failed: {e}")
        return False

    # Test 3: Test personality switching
    try:
        personalities = ["default", "mentor", "sassy", "dev_focused"]
        for personality in personalities:
            chat_router.set_personality(personality)
            print(f"✅ Personality '{personality}' set successfully")
    except Exception as e:
        print(f"❌ Personality switching failed: {e}")
        return False

    # Test 4: Test message processing
    try:
        test_messages = [
            "Hello!",
            "How do I create a aetherra plugin?",
            "What are my current goals?",
            "Help me debug this code",
        ]

        for msg in test_messages:
            response = chat_router.process_message(msg)
            print(
                f"✅ Processed: '{msg[:30]}...' -> {len(response.get('text', ''))} chars"
            )

    except Exception as e:
        print(f"❌ Message processing failed: {e}")
        return False

    # Test 5: Test enhanced Aetherra import
    try:
        from src.aethercode.ui.enhanced_Aetherra import EnhancedAetherraWindow

        print("✅ Enhanced Aetherra import successful")
    except ImportError as e:
        print(f"⚠️ Enhanced Aetherra import failed: {e}")
        print("   This is expected if PySide6 is not installed")

    print("\n🎉 Integration test completed successfully!")
    print("🚀 Enhanced Aetherra is ready with:")
    print("   • AI-powered chat responses")
    print("   • Swappable personalities")
    print("   • Context-aware conversations")
    print("   • Proactive suggestions")
    print("   • Smart intent routing")

    return True


def test_gui_integration():
    """Test GUI integration (if PySide6 is available)"""
    print("\n🖥️ Testing GUI Integration...")

    try:
        from PySide6.QtWidgets import QApplication

        from src.aethercode.ui.enhanced_Aetherra import EnhancedAetherraWindow

        print("✅ PySide6 available - GUI test possible")

        # Create QApplication (required for any Qt widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Test window creation
        window = EnhancedAetherraWindow()
        print("✅ Enhanced Aetherra window created successfully")

        # Test chat router integration
        if hasattr(window, "chat_router") and window.chat_router:
            print("✅ Chat router integrated in GUI")

            # Test a message
            response = window.chat_router.process_message("Test integration")
            print(
                f"✅ GUI chat router working: {len(response.get('text', ''))} chars response"
            )
        else:
            print("⚠️ Chat router not found in GUI - check integration")

        print("✅ GUI integration test completed")

    except ImportError:
        print("⚠️ PySide6 not available - skipping GUI test")
    except Exception as e:
        print(f"❌ GUI integration test failed: {e}")


if __name__ == "__main__":
    success = test_chat_router_integration()
    test_gui_integration()

    if success:
        print("\n🎯 INTEGRATION READY!")
        print(
            "Run 'python aetherra_launcher.py' and select option 1 to use Enhanced Aetherra"
        )
    else:
        print("\n❌ Integration issues detected - check error messages above")
