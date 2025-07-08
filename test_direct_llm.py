#!/usr/bin/env python3
"""
🧠 Test Direct LLM Manager Integration
=====================================

Test the MultiLLMManager directly to ensure it's working properly.
"""

import os
import sys
from pathlib import Path

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from Aetherra.core.ai.multi_llm_manager import MultiLLMManager

    print("✅ MultiLLMManager imported successfully")

    # Initialize the manager
    print("🔄 Initializing MultiLLMManager...")
    manager = MultiLLMManager()
    print("✅ MultiLLMManager initialized")

    # Check available models
    print("🔍 Checking available models...")
    models = manager.list_available_models()
    print(f"📋 Available models: {models}")

    # Test setting a model
    if models:
        first_model = list(models.keys())[0]
        print(f"🎯 Testing model: {first_model}")
        if manager.set_model(first_model):
            print(f"✅ Model set successfully: {first_model}")

            # Test a simple query
            print("💬 Testing query...")
            response = manager.generate_response(
                "Hello, what are you?", max_tokens=100, temperature=0.7
            )
            print(f"🎙️ Response: {response}")
        else:
            print(f"❌ Failed to set model: {first_model}")
    else:
        print("⚠️ No models available")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
