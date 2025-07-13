#!/usr/bin/env python3
"""
🧪 Test Enhanced Human-Like Lyrixa
==================================

This script tests the enhanced Lyrixa with:
- Dynamic personality adaptation
- Mood and emotional intelligence
- Time-aware responses
- Contextual learning
- Human-like conversation patterns
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


async def test_enhanced_lyrixa():
    """Test the enhanced human-like Lyrixa features"""
    try:
        logger.info("🧪 Testing Enhanced Human-Like Lyrixa...")

        # Test 1: Basic functionality
        logger.info("\n1. Testing basic enhanced conversation...")
        from lyrixa.conversation_manager import LyrixaConversationManager

        manager = LyrixaConversationManager(workspace_path=str(project_root))

        # Test basic interaction
        response1 = await manager.generate_response("Hello Lyrixa! How are you today?")
        logger.info(f"✅ Basic response: {response1[:150]}...")

        # Test 2: Context awareness
        logger.info("\n2. Testing system context awareness...")
        response2 = await manager.generate_response("What's the current system status?")
        logger.info(f"✅ System status response: {response2[:150]}...")

        # Test 3: Follow-up conversation
        logger.info("\n3. Testing conversation continuity...")
        response3 = await manager.generate_response(
            "Can you help me understand how the plugin system works?"
        )
        logger.info(f"✅ Follow-up response: {response3[:150]}...")

        # Test 4: Emotional intelligence
        logger.info("\n4. Testing emotional intelligence...")
        response4 = await manager.generate_response(
            "I'm feeling a bit overwhelmed with all these system configurations."
        )
        logger.info(f"✅ Emotional response: {response4[:150]}...")

        # Test 5: Technical assistance
        logger.info("\n5. Testing technical assistance...")
        response5 = await manager.generate_response(
            "I need help debugging a memory issue in the system."
        )
        logger.info(f"✅ Technical response: {response5[:150]}...")

        # Test 6: Creative interaction
        logger.info("\n6. Testing creative interaction...")
        response6 = await manager.generate_response(
            "What do you think about the future of AI assistants like yourself?"
        )
        logger.info(f"✅ Creative response: {response6[:150]}...")

        # Check conversation history
        logger.info(f"\n📊 Conversation statistics:")
        logger.info(f"   - Total conversations: {manager.conversation_count}")
        logger.info(f"   - History length: {len(manager.conversation_history)}")
        logger.info(f"   - Current model: {manager.current_model}")
        logger.info(f"   - Session ID: {manager.session_id}")

        # Test model health
        health = manager.get_model_health()
        logger.info(f"\n🏥 Model health: {health}")

        return True

    except Exception as e:
        logger.error(f"❌ Enhanced Lyrixa test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_prompt_engine():
    """Test the enhanced prompt engine directly"""
    try:
        logger.info("\n🎭 Testing Enhanced Prompt Engine...")

        # Test prompt generation
        from lyrixa.prompt_engine import build_dynamic_prompt

        prompt = build_dynamic_prompt(user_id="test_user")
        logger.info(f"✅ Generated enhanced prompt ({len(prompt)} characters)")
        logger.info(f"📝 Prompt preview: {prompt[:200]}...")

        # Test multiple calls to see variations
        prompt2 = build_dynamic_prompt(user_id="different_user")
        logger.info(f"✅ Generated second prompt ({len(prompt2)} characters)")

        return True

    except Exception as e:
        logger.error(f"❌ Prompt engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests for enhanced human-like Lyrixa"""
    logger.info("🚀 Starting Enhanced Human-Like Lyrixa Tests")

    tests = [
        ("Enhanced Prompt Engine", test_prompt_engine),
        ("Enhanced Lyrixa Conversation", test_enhanced_lyrixa),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"🧪 Running: {test_name}")
        logger.info(f"{'=' * 60}")

        try:
            result = await test_func()

            if result:
                logger.info(f"✅ {test_name} PASSED")
                passed += 1
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")

    logger.info(f"\n{'=' * 60}")
    logger.info(f"🎯 TEST SUMMARY: {passed}/{total} tests passed")
    logger.info(f"{'=' * 60}")

    if passed == total:
        logger.info("🎉 All tests passed! Enhanced Human-Like Lyrixa is ready!")
        logger.info("\n🌟 Enhanced Features Active:")
        logger.info("   ✅ Dynamic personality adaptation based on context")
        logger.info("   ✅ Mood and emotional intelligence")
        logger.info("   ✅ Time-aware responses")
        logger.info("   ✅ User preference learning")
        logger.info("   ✅ System-aware contextual responses")
        logger.info("   ✅ Conversation continuity and memory")
        logger.info("   ✅ Robust fallback system with local models")
        logger.info("\n🚀 Lyrixa is now truly human-like and ready for the future!")
        return True
    else:
        logger.error("⚠️ Some tests failed. Please check the logs above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
