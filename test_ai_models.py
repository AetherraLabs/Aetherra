"""
Test AI Model System
Quick test to verify Ollama models are working properly
"""

try:
    import asyncio

    from Aetherra.core.ai.multi_llm_manager import MultiLLMManager

    async def test_models():
        print("🧠 Testing Multi-LLM Manager...")

        # Initialize the manager
        manager = MultiLLMManager()

        # List available models
        available_models = manager.list_available_models()
        print(f"📋 Available models: {list(available_models.keys())}")

        # Test each Ollama model
        ollama_models = ["mistral", "llama3", "llama3.2:3b"]

        for model_name in ollama_models:
            print(f"\n🔍 Testing {model_name}...")

            # Try to set the model
            success = manager.set_model(model_name)
            if success:
                print(f"✅ {model_name} set successfully")

                # Try a simple generation
                try:
                    response = await manager.generate_response(
                        "Hello! Can you respond with just 'Working!'"
                    )
                    print(f"✅ {model_name} generated response: {response[:50]}...")
                except Exception as e:
                    print(f"❌ {model_name} generation failed: {e}")
            else:
                print(f"❌ {model_name} failed to set")

        print("\n🎯 Model test complete!")

    # Run the async test
    asyncio.run(test_models())

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback

    traceback.print_exc()
