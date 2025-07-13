#!/usr/bin/env python3
"""
Fast Lyrixa Initialization
Enables full AI capabilities without heavy local models
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def fast_initialize_lyrixa():
    """Initialize Lyrixa with minimal overhead for fast AI responses"""
    print("🚀 Fast Lyrixa Initialization")
    print("=" * 40)

    try:
        # Set environment variable to skip heavy components
        os.environ["LYRIXA_FAST_MODE"] = "1"
        os.environ["SKIP_LOCAL_MODELS"] = "1"

        from lyrixa import LyrixaAI

        print("✅ Lyrixa imported in fast mode")

        # Create instance with fast settings
        lyrixa = LyrixaAI(
            workspace_path=os.getcwd(),
            enable_local_ai=False,  # Skip local models
            enable_embeddings=False,  # Skip heavy embeddings
            fast_mode=True,
        )
        print("✅ Lyrixa created in fast mode")

        # Quick initialization (should be much faster)
        await asyncio.wait_for(lyrixa.initialize(), timeout=15.0)
        print("✅ Lyrixa initialized quickly!")

        return lyrixa

    except Exception as e:
        print(f"❌ Fast initialization failed: {e}")
        return None


def main():
    """Test fast initialization"""
    lyrixa = asyncio.run(fast_initialize_lyrixa())

    if lyrixa:
        print("\n🎉 Success! Lyrixa is ready with fast AI capabilities")
        print(
            "💡 This version skips heavy local models but enables full OpenAI integration"
        )
    else:
        print("\n❌ Fast initialization failed")
        print("💡 Will need to modify the launcher for OpenAI-only mode")


if __name__ == "__main__":
    main()
