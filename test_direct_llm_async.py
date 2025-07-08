#!/usr/bin/env python3
"""
🧠 Test Direct LLM Manager Integration
=====================================

Test the MultiLLMManager directly to ensure it's working properly.
"""

import asyncio
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_llm_manager():
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
        print(f"📋 Available models: {list(models.keys())}")

        # Test setting a model
        if models:
            # Try to find gpt-3.5-turbo or another available model
            preferred_models = ["gpt-3.5-turbo", "gpt-4o-mini", "text-davinci-003"]
            test_model = None

            for model in preferred_models:
                if model in models:
                    test_model = model
                    break

            if not test_model:
                test_model = list(models.keys())[0]

            print(f"🎯 Testing model: {test_model}")
            if manager.set_model(test_model):
                print(f"✅ Model set successfully: {test_model}")

                # Test an async query
                print("💬 Testing async query...")
                try:
                    response = await manager.generate_response(
                        "Hello, what are you?", max_tokens=100, temperature=0.7
                    )
                    print(f"🎙️ Async Response: {response}")
                except Exception as e:
                    print(f"❌ Async error: {e}")

                # Test a sync query
                print("💬 Testing sync query...")
                try:
                    sync_response = manager.generate_response_sync(
                        "What is artificial intelligence?",
                        max_tokens=100,
                        temperature=0.7,
                    )
                    print(f"🎙️ Sync Response: {sync_response}")
                except Exception as e:
                    print(f"❌ Sync error: {e}")
            else:
                print(f"❌ Failed to set model: {test_model}")
        else:
            print("⚠️ No models available")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_llm_manager())
