"""
Test Knowledge Responder after SQL fix
=====================================
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_knowledge_responder():
    """Test the Knowledge Responder with the SQL fix."""
    print("🧪 Testing Knowledge Responder after SQL fix...")

    try:
        from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
        from lyrixa.core.knowledge_responder import KnowledgeResponder

        # Create memory system
        memory = AdvancedMemorySystem()
        print("✅ Memory system created")

        # Create responder
        responder = KnowledgeResponder(memory)
        print("✅ Knowledge Responder created")

        # Test query
        query = "What is Python programming?"
        print(f"🔍 Testing query: {query}")

        result = await responder.answer_question(query)

        print(f"📝 Response: {result['response']}")
        print(f"📊 Confidence: {result['confidence']}")
        print(f"🎯 Quality: {result['quality']}")

        if "error" not in result:
            print("✅ No SQL binding errors detected!")
            return True
        else:
            print(f"❌ Error still present: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_knowledge_responder())
    print(
        f"\n{'🎉 SUCCESS' if success else '❌ FAILED'}: Knowledge Responder SQL fix test"
    )
