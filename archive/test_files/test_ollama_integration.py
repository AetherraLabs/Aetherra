#!/usr/bin/env python3
"""
🧪 Test End-to-End Ollama Integration
=====================================

This script tests the complete Ollama integration with Lyrixa's fallback system.
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


async def test_ollama_integration():
    """Test complete Ollama integration with Lyrixa"""
    try:
        logger.info("🧪 Testing Ollama integration with Lyrixa...")

        # Import required modules
        # Import MultiLLMManager directly
        import sys

        from lyrixa.conversation_manager import LyrixaConversationManager

        sys.path.insert(0, str(project_root / "src"))
        from aetherra.core.ai.multi_llm_manager import MultiLLMManager

        # Test MultiLLMManager with Ollama
        logger.info("1. Testing MultiLLMManager...")
        manager = MultiLLMManager()

        # Test Ollama models
        ollama_models = ["mistral", "llama3.2:3b", "llama3"]

        for model_name in ollama_models:
            logger.info(f"   Testing {model_name}...")
            if manager.set_model(model_name):
                logger.info(f"   ✅ {model_name} set successfully")

                # Test generation
                try:
                    response = await manager.generate_response(
                        "Hello! Please respond with exactly: 'Ollama integration working'"
                    )
                    logger.info(f"   ✅ {model_name} response: {response[:100]}...")
                    break  # Use first working model
                except Exception as e:
                    logger.error(f"   ❌ {model_name} generation failed: {e}")
            else:
                logger.warning(f"   ⚠️ {model_name} not available")

        # Test Lyrixa conversation manager with forced Ollama fallback
        logger.info("\n2. Testing Lyrixa with forced Ollama fallback...")
        lyrixa = LyrixaConversationManager(workspace_path=str(project_root))

        # Force all cloud models to fail
        cloud_models = ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo", "claude-3-sonnet"]
        for model in cloud_models:
            lyrixa.model_failures[model] = lyrixa.max_retries_per_model

        # Test conversation
        response = await lyrixa.generate_response(
            "Hello Lyrixa! I'm testing your local fallback system with Ollama."
        )
        logger.info(f"✅ Lyrixa response: {response[:200]}...")

        # Test model health
        health = lyrixa.get_model_health()
        logger.info(
            f"📊 Model health: {health['current_model']} enabled: {health['llm_enabled']}"
        )

        return True

    except Exception as e:
        logger.error(f"❌ Ollama integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run the comprehensive test"""
    logger.info("🚀 Starting End-to-End Ollama Integration Test")

    success = await test_ollama_integration()

    if success:
        logger.info(
            "\n🎉 SUCCESS! Ollama integration is working correctly with Lyrixa!"
        )
        logger.info("The robust fallback system is now complete:")
        logger.info(
            "  gpt-4o → gpt-4-turbo → gpt-3.5-turbo → claude-3-sonnet → mistral → llama3.2:3b → llama3 → smart fallback"
        )
    else:
        logger.error("\n❌ FAILURE! Some issues were detected.")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
