#!/usr/bin/env python3
"""
🧪 Test Robust Fallback System for Lyrixa
==========================================

This script tests the complete robust fallback system:
1. Tests model failure tracking
2. Tests fallback chain progression
3. Tests Ollama integration
4. Tests smart fallback when all models fail
5. Tests model health monitoring
"""

import asyncio
import logging
import os
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


def test_imports():
    """Test that all required modules can be imported"""
    try:
        from lyrixa.conversation_manager import LyrixaConversationManager
        from src.aetherra.core.ai.multi_llm_manager import MultiLLMManager

        logger.info("✅ All imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False


def test_ollama_connection():
    """Test that Ollama is running and accessible"""
    try:
        import ollama

        client = ollama.Client()
        models = client.list()
        logger.info(
            f"✅ Ollama connection successful. Available models: {[m['name'] for m in models['models']]}"
        )
        return True
    except Exception as e:
        logger.error(f"❌ Ollama connection failed: {e}")
        return False


def test_multi_llm_manager():
    """Test MultiLLMManager initialization and model availability"""
    try:
        from src.aetherra.core.ai.multi_llm_manager import MultiLLMManager

        manager = MultiLLMManager()
        logger.info(
            f"✅ MultiLLMManager initialized. Available providers: {list(manager.providers.keys())}"
        )

        # Test model availability
        available_models = []
        for model_name, config in manager.model_configs.items():
            try:
                if hasattr(
                    manager.providers.get(config.provider), "is_model_available"
                ):
                    if manager.providers[config.provider].is_model_available(config):
                        available_models.append(model_name)
            except Exception as e:
                logger.warning(f"⚠️ Could not check availability for {model_name}: {e}")

        logger.info(f"✅ Available models: {available_models}")
        return True
    except Exception as e:
        logger.error(f"❌ MultiLLMManager test failed: {e}")
        return False


def test_conversation_manager():
    """Test LyrixaConversationManager initialization"""
    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        manager = LyrixaConversationManager(workspace_path=str(project_root))
        logger.info(f"✅ LyrixaConversationManager initialized")
        logger.info(f"📊 LLM enabled: {manager.llm_enabled}")
        logger.info(f"🎯 Current model: {manager.current_model}")
        logger.info(f"📝 Preferred models: {manager.preferred_models}")

        return True
    except Exception as e:
        logger.error(f"❌ LyrixaConversationManager test failed: {e}")
        return False


async def test_fallback_chain():
    """Test the complete fallback chain"""
    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        manager = LyrixaConversationManager(workspace_path=str(project_root))

        if not manager.llm_enabled:
            logger.warning("⚠️ LLM not enabled, skipping fallback chain test")
            return False

        # Test a simple query
        test_query = (
            "Hello, please respond with exactly: 'Fallback system working correctly'"
        )
        logger.info(f"🧪 Testing query: {test_query}")

        response = await manager.generate_response(test_query)
        logger.info(f"✅ Response received: {response[:100]}...")

        # Test model health reporting
        health = manager.get_model_health()
        logger.info(f"📊 Model health: {health}")

        return True
    except Exception as e:
        logger.error(f"❌ Fallback chain test failed: {e}")
        return False


async def test_ollama_fallback():
    """Test Ollama-specific fallback"""
    try:
        from lyrixa.conversation_manager import LyrixaConversationManager

        manager = LyrixaConversationManager(workspace_path=str(project_root))

        if not manager.llm_enabled:
            logger.warning("⚠️ LLM not enabled, skipping Ollama fallback test")
            return False

        # Simulate all cloud models failing by marking them as failed
        cloud_models = [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "claude-3-sonnet",
            "mistral",
        ]
        for model in cloud_models:
            manager.model_failures[model] = manager.max_retries_per_model

        logger.info("🧪 Simulated cloud model failures, testing local fallback...")

        # Try to generate a response - should use local models
        response = await manager.generate_response("Test local fallback")
        logger.info(f"✅ Local fallback response: {response[:100]}...")

        # Reset failures
        manager.reset_model_failures()
        logger.info("♻️ Model failures reset")

        return True
    except Exception as e:
        logger.error(f"❌ Ollama fallback test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("🚀 Starting Robust Fallback System Tests")

    tests = [
        ("Import Test", test_imports),
        ("Ollama Connection Test", test_ollama_connection),
        ("MultiLLMManager Test", test_multi_llm_manager),
        ("Conversation Manager Test", test_conversation_manager),
        ("Fallback Chain Test", test_fallback_chain),
        ("Ollama Fallback Test", test_ollama_fallback),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n{'=' * 50}")
        logger.info(f"🧪 Running: {test_name}")
        logger.info(f"{'=' * 50}")

        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")

    logger.info(f"\n{'=' * 50}")
    logger.info(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
    logger.info(f"{'=' * 50}")

    if passed == total:
        logger.info("🎉 All tests passed! Robust fallback system is working correctly.")
        return True
    else:
        logger.error("⚠️ Some tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
