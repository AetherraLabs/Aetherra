#!/usr/bin/env python3

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lyrixa import LyrixaAI


async def test_lyrixa():
    # Initialize Lyrixa
    lyrixa = LyrixaAI()
    await lyrixa.initialize()

    # Test conversation
    response = await lyrixa.process_natural_language("status_report")
    print("Response:", response)

    # Test memory
    memory_result = await lyrixa.memory.recall_memories("What is Aetherra?")
    print("Memory Result:", memory_result)


if __name__ == "__main__":
    asyncio.run(test_lyrixa())
