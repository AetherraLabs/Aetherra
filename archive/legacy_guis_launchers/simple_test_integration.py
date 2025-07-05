#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa.core.advanced_vector_memory import AdvancedMemorySystem
from lyrixa.core.conversation import LyrixaConversationalEngine


async def simple_test():
    print("🧪 SIMPLE KNOWLEDGE INTEGRATION TEST")

    # Initialize memory system
    memory = AdvancedMemorySystem()

    # Store test memory
    await memory.store_memory(
        content="Aetherra is an AI coding platform.",
        memory_type="project_info",
        tags=["aetherra", "platform"],
    )

    # Initialize conversation engine
    engine = LyrixaConversationalEngine(memory_system=memory)
    await engine.initialize_conversation("test_session")

    # Test query
    response = await engine.process_conversation_turn("What is Aetherra?")
    print(f"Response: {response['text']}")

    if "adaptation_notes" in response:
        print(f"Notes: {response['adaptation_notes']}")


if __name__ == "__main__":
    asyncio.run(simple_test())
