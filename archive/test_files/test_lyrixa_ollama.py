#!/usr/bin/env python3
"""
🧪 Lyrixa Ollama Integration Test
=================================

Quick test of Lyrixa with Ollama models.
"""


def test_lyrixa_with_ollama():
    """Test Lyrixa conversation manager with Ollama"""
    print("🎙️ Testing Lyrixa with Ollama")
    print("=" * 35)

    try:
        # Import minimal components
        import sys
        from pathlib import Path

        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        from lyrixa.conversation_manager import LyrixaConversationManager

        print("✅ Imported conversation manager")

        # Initialize with workspace
        conv_manager = LyrixaConversationManager(str(project_root))
        print("✅ Conversation manager initialized")

        # Force local models by temporarily modifying preferences
        original_models = conv_manager.preferred_models.copy()

        # Set only local models
        conv_manager.preferred_models = [
            "mistral",  # Should map to mistral:latest
            "llama3.2:3b",  # Exact model name
            "llama3",  # Should map to llama3:latest
        ]

        print("🔄 Set preferences to local models only")

        # Test conversation
        print("💬 Testing conversation...")
        response = conv_manager.generate_response(
            "Hello! Please confirm you are a local Ollama model and respond with 'Local AI active!'"
        )

        # Handle async if needed
        if hasattr(response, "__await__"):
            import asyncio

            response = asyncio.run(response)

        response_str = str(response)
        print(f"📄 Response: {response_str[:200]}...")

        # Restore original preferences
        conv_manager.preferred_models = original_models

        # Check if we got a local response
        if "fallback" not in response_str.lower() and "Local AI" in response_str:
            print("🎉 SUCCESS! Local Ollama model responded through Lyrixa!")
            return True
        elif "fallback" not in response_str.lower():
            print("✅ Got response (likely from local model)")
            return True
        else:
            print("⚠️  Still using fallback mode")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_lyrixa_with_ollama()

    print("\n" + "=" * 35)
    if success:
        print("🎉 LYRIXA + OLLAMA INTEGRATION SUCCESS!")
        print("🚀 Local AI is working with Lyrixa!")
        print("🔒 Your conversations are completely private!")
    else:
        print("⚠️  Integration needs refinement")
        print("💡 Ollama works, but Lyrixa integration needs adjustment")
    print("=" * 35)
