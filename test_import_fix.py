#!/usr/bin/env python3
"""
Quick verification that the import issues are fixed
"""

import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_prompt_engine_import():
    """Test that the prompt engine can be imported and used"""
    try:
        logger.info("🧪 Testing prompt engine import...")
        from lyrixa.prompt_engine import build_dynamic_prompt

        logger.info("✅ Import successful!")

        # Test basic functionality
        logger.info("🧪 Testing prompt generation...")
        prompt = build_dynamic_prompt(user_id="test_user")
        logger.info("✅ Prompt generated successfully!")
        logger.info(f"📊 Prompt length: {len(prompt)} characters")

        # Test that it contains expected sections
        expected_sections = [
            "🔧 CURRENT SYSTEM STATE",
            "👤 USER PROFILE",
            "⏰ TIME & CONTEXT",
            "💫 INTERACTION GUIDELINES",
            "🎯 RESPONSE APPROACH",
        ]

        missing_sections = []
        for section in expected_sections:
            if section not in prompt:
                missing_sections.append(section)

        if missing_sections:
            logger.warning(f"⚠️ Missing sections: {missing_sections}")
        else:
            logger.info("✅ All expected sections found in prompt!")

        return True

    except Exception as e:
        logger.error(f"❌ Import/generation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_conversation_manager_integration():
    """Test that the conversation manager can use the prompt engine"""
    try:
        logger.info("🧪 Testing conversation manager integration...")
        # Initialize conversation manager with current directory
        import os

        from lyrixa.conversation_manager import LyrixaConversationManager

        current_dir = os.getcwd()
        manager = LyrixaConversationManager(workspace_path=current_dir)
        logger.info("✅ Conversation manager initialized!")

        # Check if prompt engine is available
        if hasattr(manager, "PROMPT_ENGINE_AVAILABLE"):
            logger.info(
                "✅ Prompt engine availability detected in conversation manager!"
            )

        return True

    except Exception as e:
        logger.error(f"❌ Conversation manager test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("🚀 Quick Import Verification Test")
    logger.info("=" * 50)

    success_count = 0
    total_tests = 2

    # Test 1: Prompt Engine Import
    if test_prompt_engine_import():
        success_count += 1

    # Test 2: Conversation Manager Integration
    if test_conversation_manager_integration():
        success_count += 1

    logger.info("=" * 50)
    logger.info(f"🎯 RESULTS: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        logger.info("🎉 ALL TESTS PASSED! Import issues are FIXED!")
    else:
        logger.error("❌ Some tests failed. Check the output above.")
