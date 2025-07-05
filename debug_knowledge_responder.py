"""
Debug Knowledge Responder
========================
Quick test to debug the Knowledge Responder error.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def debug_responder():
    """Debug the Knowledge Responder issue."""
    print("🐛 DEBUGGING KNOWLEDGE RESPONDER")
    print("=" * 40)

    try:
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.conversation import PersonalityType, ToneMode
        from lyrixa.core.knowledge_responder import KnowledgeResponder

        print("✅ All imports successful")

        # Test enum creation
        print(f"✅ PersonalityType.DEFAULT: {PersonalityType.DEFAULT}")
        print(f"✅ PersonalityType.DEFAULT value: {PersonalityType.DEFAULT.value}")

        # Create memory system
        memory = AdvancedMemorySystem()
        print("✅ Memory system created")

        # Create responder
        responder = KnowledgeResponder(memory)
        print("✅ Knowledge Responder created")

        # Test with minimal context
        print("\n🧪 Testing with minimal context...")
        result = await responder.answer_question("What is Python?")
        print(f"📝 Response: {result['response']}")
        print(f"📊 Confidence: {result['confidence']}")

        # Test with explicit context
        print("\n🧪 Testing with explicit context...")
        context = {"personality": "default", "tone_mode": "adaptive"}
        result = await responder.answer_question("What is machine learning?", context)
        print(f"📝 Response: {result['response']}")
        print(f"📊 Confidence: {result['confidence']}")

        return True

    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(debug_responder())
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Debug session")
