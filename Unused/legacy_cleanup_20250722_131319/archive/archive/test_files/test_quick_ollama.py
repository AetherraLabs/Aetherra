#!/usr/bin/env python3
"""
🧪 Quick Ollama Fix Test
=======================

Test the Ollama availability fix directly.
"""


def test_ollama_fix():
    """Test the fixed Ollama model availability"""
    print("[TOOL] Testing Ollama Model Availability Fix")
    print("=" * 40)

    try:
        import sys

        sys.path.insert(0, "src")

        # Import just what we need
        from aetherra.core.ai.multi_llm_manager import (
            LLMConfig,
            LLMProvider,
            OllamaProvider,
        )

        # Create provider
        provider = OllamaProvider()
        print("✅ Ollama provider created")

        # Test mistral config
        mistral_config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="mistral:latest",
            base_url="http://localhost:11434",
            context_window=4096,
        )

        # Test availability
        is_available = provider.is_model_available(mistral_config)
        print(f"🧠 mistral:latest available: {is_available}")

        if is_available:
            print("🎉 SUCCESS! Ollama model detection fixed!")
            return True
        else:
            print("❌ Still not detecting models")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_ollama_fix()
    if success:
        print("\n✅ OLLAMA INTEGRATION FIXED!")
        print("🚀 Now test with Lyrixa!")
    else:
        print("\n❌ Still needs work")
