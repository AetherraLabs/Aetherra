#!/usr/bin/env python3
"""
[TOOL] Chat Panel Intelligence Patch Verification
==================================================

Test script to verify that Lyrixa's full intelligence patch
has been applied correctly to the chat panel.
"""

import os
import sys
import traceback

def test_chat_panel_patch():
    """Test that the chat panel patch was applied correctly"""

    print("[TOOL] Testing Chat Panel Intelligence Patch...")
    print("=" * 50)

    try:
        # Test import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        from Aetherra.lyrixa.gui.panels.chat_panel import ChatPanel
        print("✅ Chat panel import successful")

        # Test that new labels exist in __init__
        import inspect
        init_source = inspect.getsource(ChatPanel.__init__)

        required_elements = [
            "self.goal_label",
            "self.personality_label",
            "layout.addWidget(self.goal_label)",
            "layout.addWidget(self.personality_label)"
        ]

        for element in required_elements:
            if element in init_source:
                print(f"✅ Found required element: {element}")
            else:
                print(f"[ERROR] Missing required element: {element}")
                return False

        # Test that process_input_async was enhanced
        process_source = inspect.getsource(ChatPanel.process_input_async)

        intelligence_features = [
            "persona_name",
            "🧠 Reasoning:",
            "🎯 Goal:",
            "🎭 Personality:"
        ]

        for feature in intelligence_features:
            if feature in process_source:
                print(f"✅ Intelligence feature found: {feature}")
            else:
                print(f"[ERROR] Missing intelligence feature: {feature}")
                return False

        print("\n🎉 Chat Panel Intelligence Patch Verification SUCCESSFUL!")
        print("\nEnhanced Features:")
        print("• 🎯 Goal display label")
        print("• 🎭 Personality indicator")
        print("• 🧠 Reasoning/thought display")
        print("• 🧠 Persona-aware responses")
        print("• [TOOL] Robust error handling")

        print("\n🚀 Ready to test in Aetherra!")
        print("Usage:")
        print("1. Launch Aetherra")
        print("2. Open Chat panel")
        print("3. See goal and personality indicators")
        print("4. Chat with Lyrixa and see reasoning")

        return True

    except ImportError as e:
        print(f"[ERROR] Import failed: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chat_panel_patch()

    if success:
        print("\n" + "=" * 50)
        print("🎯 PATCH STATUS: APPLIED SUCCESSFULLY")
        print("🧠 Lyrixa's full intelligence is now enabled in chat!")
    else:
        print("\n" + "=" * 50)
        print("[ERROR] PATCH STATUS: VERIFICATION FAILED")
        print("[WARN] Please check the patch application")

    sys.exit(0 if success else 1)
