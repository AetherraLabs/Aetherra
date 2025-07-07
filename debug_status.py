#!/usr/bin/env python3
"""Quick debug script to check system status structure"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


async def main():
    from lyrixa import LyrixaAI

    lyrixa = LyrixaAI(workspace_path=str(current_dir))
    await lyrixa.initialize()

    status = await lyrixa.get_system_status()
    print("System status structure:")
    print(f"Keys: {list(status.keys())}")
    print(f"Full status: {status}")


if __name__ == "__main__":
    asyncio.run(main())
