#!/usr/bin/env python3
"""
🔧 Chat Enhancements Test - Script & Model Commands
====================================================

Test script to verify that the new chat features have been
added correctly to the chat panel.
"""

import os
import sys
import traceback

def test_chat_enhancements():
    """Test that the chat enhancements were applied correctly"""

    print("🔧 Testing Chat Panel Enhancements...")
    print("=" * 50)

    try:
        # Test import
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))

        from Aetherra.lyrixa.gui.panels.chat_panel import ChatPanel
        print("✅ Chat panel import successful")

        # Test that new commands exist in handle_slash_command
        import inspect
        slash_command_source = inspect.getsource(ChatPanel.handle_slash_command)

        required_script_features = [
            "/run_script",
            "script_executor",
            "🧠 Executing .aether script:"
        ]

        required_model_features = [
            "/set_model",
            "/current_model",
            "openai|ollama|local",
            "🤖 Switching to"
        ]

        required_help_updates = [
            "🔧 Script & Model Commands:",
            "Execute .aether script",
            "Switch AI model"
        ]

        print("\n🧪 Testing Script Execution Features:")
        for feature in required_script_features:
            if feature in slash_command_source:
                print(f"✅ Found script feature: {feature}")
            else:
                print(f"❌ Missing script feature: {feature}")
                return False

        print("\n🤖 Testing Model Switching Features:")
        for feature in required_model_features:
            if feature in slash_command_source:
                print(f"✅ Found model feature: {feature}")
            else:
                print(f"❌ Missing model feature: {feature}")
                return False

        print("\n📋 Testing Help Command Updates:")
        for feature in required_help_updates:
            if feature in slash_command_source:
                print(f"✅ Found help update: {feature}")
            else:
                print(f"❌ Missing help update: {feature}")
                return False

        # Test that LyrixaEngine has model methods
        from Aetherra.lyrixa.engine.lyrixa_engine import LyrixaEngine
        print("\n🔧 Testing Engine Model Methods:")

        engine_methods = ['set_model', 'get_current_model']
        for method in engine_methods:
            if hasattr(LyrixaEngine, method):
                print(f"✅ Engine has method: {method}")
            else:
                print(f"❌ Engine missing method: {method}")
                return False

        print("\n🎉 Chat Enhancement Verification SUCCESSFUL!")
        print("\nNew Features Added:")
        print("• 🔧 /run_script [script_name] - Execute .aether scripts")
        print("• 🤖 /set_model [openai|ollama|local] - Switch AI models")
        print("• 🔍 /current_model - Show current AI model")
        print("• 📋 Updated /help with new commands")
        print("• 🧠 Engine model management methods")

        print("\n🚀 Ready to test in Aetherra!")
        print("Usage Examples:")
        print("/run_script hello_world")
        print("/set_model openai")
        print("/set_model ollama")
        print("/current_model")
        print("/help")

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chat_enhancements()

    if success:
        print("\n" + "=" * 50)
        print("🎯 ENHANCEMENT STATUS: APPLIED SUCCESSFULLY")
        print("🔧 Script execution and model switching enabled!")
    else:
        print("\n" + "=" * 50)
        print("❌ ENHANCEMENT STATUS: VERIFICATION FAILED")
        print("⚠️ Please check the implementation")

    sys.exit(0 if success else 1)
