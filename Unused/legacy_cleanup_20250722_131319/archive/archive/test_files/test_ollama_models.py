#!/usr/bin/env python3
"""
Quick test to verify Ollama models are properly configured
"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Aetherra.core.multi_llm_manager import MultiLLMManager

def test_ollama_models():
    print("🧪 Testing Ollama model configuration...")

    # Initialize MultiLLM Manager
    llm_manager = MultiLLMManager()

    # List all available models
    available_models = llm_manager.list_available_models()
    print(f"\n📋 Available models: {list(available_models.keys())}")

    # Test Ollama models specifically
    ollama_models = [name for name, info in available_models.items() if info.get('provider') == 'ollama']
    print(f"🦙 Ollama models: {ollama_models}")

    # Test switching to each Ollama model
    for model_name in ollama_models:
        print(f"\n🔄 Testing switch to {model_name}...")
        success = llm_manager.set_model(model_name)
        if success:
            current_info = llm_manager.get_current_model_info()
            print(f"✅ Successfully switched to {current_info['model_name']} ({current_info['provider']})")
        else:
            print(f"❌ Failed to switch to {model_name}")

    print(f"\n🎯 Test complete! Found {len(ollama_models)} working Ollama models")

if __name__ == "__main__":
    test_ollama_models()
