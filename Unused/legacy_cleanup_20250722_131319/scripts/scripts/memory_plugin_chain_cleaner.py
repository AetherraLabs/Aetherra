#!/usr/bin/env python3
"""
Memory System Plugin Chain Cleaner
==================================

Cleans corrupted plugin chains from the Lyrixa memory system using the memory API.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import Lyrixa components
try:
    from lyrixa.core.enhanced_memory import LyrixaEnhancedMemorySystem
except ImportError:
    print("⚠️ Could not import LyrixaEnhancedMemorySystem")
    sys.exit(1)


class MemorySystemPluginChainCleaner:
    """Clean corrupted plugin chains from the memory system."""

    def __init__(self):
        self.memory_system = None
        self.cleaned_count = 0
        self.required_fields = {
            "name",
            "description",
            "plugins",
            "input_schema",
            "output_schema",
            "created_by",
        }

    async def initialize_memory_system(self):
        """Initialize the memory system."""
        try:
            db_path = os.path.join(os.getcwd(), "lyrixa_enhanced_memory.db")
            self.memory_system = LyrixaEnhancedMemorySystem(memory_db_path=db_path)
            print(f"✅ Memory system initialized with database: {db_path}")
        except Exception as e:
            print(f"❌ Failed to initialize memory system: {e}")
            return False
        return True

    async def clean_plugin_chains(self):
        """Clean corrupted plugin chains from memory."""
        print("🧹 MEMORY SYSTEM PLUGIN CHAIN CLEANER")
        print("=" * 50)

        if not await self.initialize_memory_system():
            return

        try:
            # Search for plugin chain memories
            chain_memories = await self.memory_system.search_memories(
                {"tags": ["plugin_chain"], "memory_type": "plugin_chain"}
            )

            print(f"🔍 Found {len(chain_memories)} plugin chain memories")

            corrupted_ids = []

            for memory in chain_memories:
                memory_id = getattr(memory, "id", None) or getattr(
                    memory, "memory_id", None
                )

                # Handle both dict and object memory structures
                if hasattr(memory, "content"):
                    content = memory.content
                else:
                    content = memory

                # Extract chain data from content
                if isinstance(content, dict):
                    chain_data = content.get("plugin_chain") or content
                else:
                    chain_data = content

                if chain_data and isinstance(chain_data, dict):
                    # Check for missing required fields
                    missing_fields = self.required_fields - chain_data.keys()

                    if missing_fields:
                        print(
                            f"   ❌ Corrupted chain found (ID: {memory_id}): Missing {', '.join(missing_fields)}"
                        )
                        if memory_id:
                            corrupted_ids.append(memory_id)
                    else:
                        print(
                            f"   ✅ Valid chain found: {chain_data.get('name', 'Unknown')}"
                        )
                else:
                    print(f"   ❌ Invalid chain data format (ID: {memory_id})")
                    if memory_id:
                        corrupted_ids.append(memory_id)

            # Delete corrupted entries
            for memory_id in corrupted_ids:
                try:
                    await self.memory_system.delete_memory(memory_id)
                    self.cleaned_count += 1
                    print(f"   🗑️ Deleted corrupted chain: {memory_id}")
                except Exception as e:
                    print(f"   ⚠️ Failed to delete {memory_id}: {e}")

            print("\n📊 Summary:")
            print(f"   🔍 Plugin chains checked: {len(chain_memories)}")
            print(f"   🧹 Corrupted entries cleaned: {self.cleaned_count}")

            if self.cleaned_count > 0:
                print("✅ Memory cleanup completed!")
            else:
                print("📝 No corrupted plugin chains found in memory.")

        except Exception as e:
            print(f"❌ Error during cleanup: {e}")


async def main():
    """Main function."""
    cleaner = MemorySystemPluginChainCleaner()
    await cleaner.clean_plugin_chains()


if __name__ == "__main__":
    asyncio.run(main())
