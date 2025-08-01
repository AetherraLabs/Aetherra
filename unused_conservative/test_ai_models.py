#!/usr/bin/env python3
"""
Test script to diagnose AI model recognition issues
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def load_env_file():
    """Load environment variables from .env file"""
    env_file = project_root / ".env"
    if env_file.exists():
        print("🔍 Loading .env file...")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

        # Check which API keys are loaded
        api_keys = {
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
            "GOOGLE_API_KEY": os.environ.get("GOOGLE_API_KEY"),
        }

        print("📋 API Keys status:")
        for key, value in api_keys.items():
            status = "✅ Set" if value else "❌ Missing"
            masked_value = f"{value[:10]}..." if value else "None"
            print(f"  {key}: {status} ({masked_value})")
        print()
    else:
        print("❌ No .env file found")


def test_multi_llm_manager():
    """Test the MultiLLMManager to see what models are available"""
    print("🔍 Testing MultiLLMManager...")

    try:
        from Aetherra.core.ai.multi_llm_manager import MultiLLMManager

        print("✅ Successfully imported MultiLLMManager")

        manager = MultiLLMManager()
        print("✅ Manager initialized")

        print("\n📋 Available providers:")
        for provider_name, provider in manager.providers.items():
            print(f"  {provider_name}: {type(provider).__name__}")

        print("\n🤖 Available models:")
        models = manager.list_available_models()
        if models:
            for model_name, details in models.items():
                print(f"  ✅ {model_name}: {details['provider']}")
        else:
            print("  ❌ No models found!")

        print(f"\n🎯 Current model: {manager.current_model}")

        # Test setting a model
        if models:
            first_model = list(models.keys())[0]
            print(f"\n🔄 Testing model switch to: {first_model}")
            success = manager.set_model(first_model)
            print(f"  Result: {'✅ Success' if success else '❌ Failed'}")

            # Test each provider
            print("\n🧪 Testing providers:")
            for provider_name in ["ollama", "openai", "anthropic", "gemini"]:
                provider_models = [
                    m for m, d in models.items() if d["provider"] == provider_name
                ]
                if provider_models:
                    test_model = provider_models[0]
                    print(f"  Testing {provider_name} with {test_model}...")
                    success = manager.set_model(test_model)
                    print(f"    {'✅ Success' if success else '❌ Failed'}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


def test_ollama_direct():
    """Test Ollama directly"""
    print("\n🔍 Testing Ollama directly...")

    try:
        import requests

        response = requests.get("http://127.0.0.1:11434/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"✅ Ollama running with {len(models)} models:")
            for model in models:
                print(f"  - {model['name']}")
        else:
            print(f"❌ Ollama returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")


def test_conversation_manager():
    """Test how conversation manager sees models"""
    print("\n🔍 Testing Conversation Manager model detection...")

    try:
        from Aetherra.lyrixa.conversation_manager import LyrixaConversationManager

        print("✅ Successfully imported LyrixaConversationManager")

        # This might fail if conversation manager has issues
        manager = LyrixaConversationManager(workspace_path=".")
        print("✅ LyrixaConversationManager initialized")

        # Check if it has model information
        if hasattr(manager, "llm_manager"):
            print("✅ ConversationManager has llm_manager")
            if hasattr(manager.llm_manager, "list_available_models"):
                models = manager.llm_manager.list_available_models()
                print(f"📋 Models from ConversationManager: {list(models.keys())}")
            else:
                print("❌ LLM manager missing list_available_models method")
        else:
            print("❌ ConversationManager missing llm_manager")

    except Exception as e:
        print(f"❌ Error with ConversationManager: {e}")


if __name__ == "__main__":
    print("🚀 AI Model Recognition Diagnostic Test")
    print("=" * 50)

    # Load environment variables first
    load_env_file()

    test_multi_llm_manager()
    test_ollama_direct()
    test_conversation_manager()

    print("\n✅ Diagnostic complete!")
