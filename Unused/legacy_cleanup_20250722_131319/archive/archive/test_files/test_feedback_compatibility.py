#!/usr/bin/env python3
"""Test the feedback system compatibility with enhanced memory system"""

import asyncio

from lyrixa.core.conversation import PersonalityProcessor
from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
from lyrixa.core.feedback_system import (
    FeedbackRating,
    FeedbackType,
    LyrixaFeedbackSystem,
)


async def test_feedback_system_compatibility():
    """Test feedback system with enhanced memory system"""
    print("🧪 Testing Feedback System with Enhanced Memory...")

    # Initialize systems
    memory = LyrixaEnhancedMemorySystem()
    personality = PersonalityProcessor()
    feedback_system = LyrixaFeedbackSystem(memory, personality)

    print(f"✅ Systems initialized:")
    print(f"   Memory type: {type(memory).__name__}")
    print(f"   Has store_memory: {hasattr(memory, 'store_memory')}")
    print(f"   Has recall_memories: {hasattr(memory, 'recall_memories')}")
    print(f"   Has store_enhanced_memory: {hasattr(memory, 'store_enhanced_memory')}")

    # Test feedback collection
    try:
        feedback_id = await feedback_system.collect_feedback(
            feedback_type=FeedbackType.SUGGESTION_RATING,
            rating=FeedbackRating.GOOD,
            context={"test": "compatibility_test"},
            user_comment="Testing compatibility",
        )
        print(f"✅ Feedback collected successfully: {feedback_id}")
    except Exception as e:
        print(f"❌ Error collecting feedback: {e}")
        return False

    # Test memory search
    try:
        search_results = await feedback_system._search_memory_for_patterns(
            "compatibility_test"
        )
        print(f"✅ Memory search completed, found {len(search_results)} results")
    except Exception as e:
        print(f"❌ Error searching memory: {e}")
        return False

    print("✅ All compatibility tests passed!")
    return True


if __name__ == "__main__":
    asyncio.run(test_feedback_system_compatibility())
