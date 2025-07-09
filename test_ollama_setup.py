#!/usr/bin/env python3
"""
Test Ollama Configuration for Aetherra
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_ollama_installation():
    """Test if Ollama is properly installed and accessible"""

    print("🔍 Testing Ollama Configuration...")
    print("=" * 50)

    # Test 1: Check if Ollama Python package is installed
    try:
        import ollama

        print("✅ Ollama Python package installed")
    except ImportError as e:
        print(f"❌ Ollama Python package not installed: {e}")
        print("   Run: pip install ollama")
        return False

    # Test 2: Check if Ollama service is running
    try:
        client = ollama.Client()
        models = client.list()
        print("✅ Ollama service is running")
        print(f"   Service URL: http://localhost:11434")
    except Exception as e:
        print(f"❌ Ollama service not accessible: {e}")
        print("   Make sure Ollama is installed and running:")
        print("   - Download from: https://ollama.ai/download")
        print("   - Or run: ollama serve")
        return False

    # Test 3: Check available models
    try:
        available_models = models.get("models", [])
        if available_models:
            print(f"✅ Found {len(available_models)} Ollama models:")
            for model in available_models:
                model_name = model.get("name", "unknown")
                size = model.get("size", 0) / (1024**3)  # Convert to GB
                print(f"   - {model_name} ({size:.1f}GB)")
        else:
            print("⚠️  No models downloaded yet")
            print("   Download a model with: ollama pull llama2:7b")
            return False
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return False

    # Test 4: Test model response
    try:
        # Use the first available model for testing
        test_model = available_models[0]["name"].split(":")[0]
        print(f"\n🧪 Testing model '{test_model}'...")

        response = client.chat(
            model=test_model,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Can you respond with just 'Ollama is working'?",
                }
            ],
            options={"temperature": 0.1, "num_predict": 10},
        )

        response_text = response["message"]["content"].strip()
        print(f"✅ Model response: {response_text}")

    except Exception as e:
        print(f"❌ Error testing model: {e}")
        return False

    print("\n🎉 Ollama is fully configured and ready!")
    return True


def test_aetherra_integration():
    """Test if Aetherra can detect and use Ollama"""

    print("\n🔍 Testing Aetherra Integration...")
    print("=" * 50)

    try:
        # Import Aetherra's MultiLLMManager
        from Aetherra.core.ai.multi_llm_manager import LLMProvider, MultiLLMManager

        # Initialize the manager
        manager = MultiLLMManager()

        # Check if Ollama provider is available
        if LLMProvider.OLLAMA in manager.providers:
            print("✅ Aetherra detected Ollama provider")

            # List available models through Aetherra
            available_models = manager.list_available_models()
            ollama_models = [
                name
                for name, config in available_models.items()
                if config.provider == LLMProvider.OLLAMA
            ]

            if ollama_models:
                print(f"✅ Available Ollama models in Aetherra: {ollama_models}")

                # Test setting an Ollama model
                test_model = ollama_models[0]
                if manager.set_model(test_model):
                    print(f"✅ Successfully set model: {test_model}")
                else:
                    print(f"❌ Failed to set model: {test_model}")

            else:
                print("⚠️  No Ollama models available in Aetherra")

        else:
            print("❌ Aetherra did not detect Ollama provider")
            return False

    except ImportError as e:
        print(f"❌ Could not import Aetherra components: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing Aetherra integration: {e}")
        return False

    print("🎉 Aetherra integration successful!")
    return True


if __name__ == "__main__":
    print("🚀 Ollama Configuration Test for Aetherra")
    print("=" * 50)

    # Run tests
    ollama_ok = test_ollama_installation()
    if ollama_ok:
        aetherra_ok = test_aetherra_integration()

        if ollama_ok and aetherra_ok:
            print("\n🌟 ALL TESTS PASSED!")
            print("Ollama is ready to use with Lyrixa as a fallback model.")
            print("\nNow when OpenAI models fail, Lyrixa will automatically")
            print("fall back to your local Ollama models! 🎯")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
    else:
        print("\n❌ Ollama setup incomplete. Please fix the issues above.")
