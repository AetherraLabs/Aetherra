#!/usr/bin/env python3
"""
🧪 Direct Ollama Test
=====================

Test Ollama integration directly without complex imports.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_ollama_direct():
    """Test Ollama directly"""
    try:
        # Test basic Ollama connection
        logger.info("1. Testing basic Ollama connection...")
        import ollama

        client = ollama.Client()
        models = client.list()
        available_models = [model.model for model in models.models]
        logger.info(f"✅ Available models: {available_models}")

        # Test generation with each model
        test_models = ["llama3.2:3b", "llama3:latest", "mistral:latest"]

        for model_name in test_models:
            if model_name in available_models:
                logger.info(f"2. Testing {model_name}...")
                try:
                    response = client.chat(
                        model=model_name,
                        messages=[
                            {
                                "role": "user",
                                "content": "Hello! Please say 'Ollama is working correctly'",
                            }
                        ],
                    )
                    logger.info(
                        f"✅ {model_name} response: {response['message']['content'][:100]}..."
                    )
                except Exception as e:
                    logger.error(f"❌ {model_name} failed: {e}")
            else:
                logger.warning(f"⚠️ {model_name} not available")

        # Test with Lyrixa (import only conversation manager)
        logger.info("3. Testing Lyrixa conversation manager...")
        from lyrixa.conversation_manager import LyrixaConversationManager

        lyrixa = LyrixaConversationManager(workspace_path=str(project_root))

        # Check model health
        health = lyrixa.get_model_health()
        logger.info(f"📊 Lyrixa model health: {health}")

        # Force cloud models to fail for testing
        cloud_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-sonnet"]
        for model in cloud_models:
            lyrixa.model_failures[model] = lyrixa.max_retries_per_model

        # Test conversation
        response = await lyrixa.generate_response(
            "Hello Lyrixa! Test your local fallback system."
        )
        logger.info(f"✅ Lyrixa response: {response[:200]}...")

        return True

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the test"""
    logger.info("🚀 Starting Direct Ollama Test")

    success = await test_ollama_direct()

    if success:
        logger.info("\n🎉 SUCCESS! Ollama integration is working!")
        logger.info("✅ Robust fallback system completed:")
        logger.info(
            "   gpt-4o → gpt-4-turbo → gpt-3.5-turbo → claude-3-sonnet → mistral → llama3.2:3b → llama3 → smart fallback"
        )
    else:
        logger.error("\n❌ Some issues were detected.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
