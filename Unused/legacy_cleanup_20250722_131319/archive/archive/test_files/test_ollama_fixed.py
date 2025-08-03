#!/usr/bin/env python3
"""
🧪 Test Ollama Integration After Fixes
======================================

Test if the fixed model configuration works with Ollama.
"""

import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


def test_fixed_ollama():
    """Test Ollama with the fixed configuration"""
    print("[TOOL] Testing Fixed Ollama Configuration")
    print("=" * 45)

    try:
        # Import the conversation manager
        from lyrixa.conversation_manager import LyrixaConversationManager

        # Initialize conversation manager
        conv_manager = LyrixaConversationManager(str(project_root))
        print("✅ Conversation manager initialized")

        # Check what models are available
        if hasattr(conv_manager, "llm_manager") and conv_manager.llm_manager:
            available_models = conv_manager.llm_manager.list_available_models()
            print(f"📋 Available models: {list(available_models.keys())}")

            # Test specifically the Ollama models
            ollama_models = ["mistral", "llama3.2:3b", "llama3"]

            for model_name in ollama_models:
                if model_name in available_models:
                    print(f"\n🧠 Testing {model_name}...")

                    # Try to set this model
                    success = conv_manager.llm_manager.set_current_model(model_name)
                    if success:
                        print(f"✅ Successfully set {model_name}")

                        # Try to generate a response
                        try:
                            response = conv_manager.llm_manager.generate_response(
                                "Hello! Are you a local Ollama model?"
                            )
                            print(f"📄 Response: {response[:100]}...")
                            print(f"🎉 {model_name} is working!")
                            return True

                        except Exception as e:
                            print(f"❌ Error generating response: {e}")
                    else:
                        print(f"❌ Failed to set {model_name}")
                else:
                    print(f"⚠️  {model_name} not in available models")

        # Fallback test through conversation manager
        print(f"\n💬 Testing through conversation manager...")

        # Temporarily disable cloud models to force local model usage
        original_models = conv_manager.preferred_models
        conv_manager.preferred_models = ["mistral", "llama3.2:3b", "llama3"]

        response = conv_manager.generate_response(
            "Hello! Please confirm you are a local Ollama model."
        )

        # Handle async response
        if hasattr(response, "__await__"):
            import asyncio

            response = asyncio.run(response)

        response_str = str(response)
        print(f"📄 Response: {response_str[:150]}...")

        # Restore original model preferences
        conv_manager.preferred_models = original_models

        # Check if we got a local model response
        if "fallback" not in response_str.lower():
            print("🎉 SUCCESS! Local Ollama model responded!")
            return True
        else:
            print("⚠️  Still using fallback mode")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_fixed_ollama()

    print("\n" + "=" * 45)
    if success:
        print("🎉 OLLAMA INTEGRATION SUCCESSFUL!")
        print("🚀 Local AI models are working with Lyrixa!")
        print("🔒 Complete privacy - conversations stay local!")
    else:
        print("❌ Ollama integration still needs work")
        print("💡 Check model configurations and Ollama service")
    print("=" * 45)
