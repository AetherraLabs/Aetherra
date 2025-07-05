#!/usr/bin/env python3

import json
import sqlite3


def check_database():
    print("🔍 CHECKING DATABASE DIRECTLY")

    try:
        conn = sqlite3.connect("lyrixa_advanced_memory.db")
        cursor = conn.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='advanced_memories'"
        )
        table_exists = cursor.fetchone()

        if not table_exists:
            print("❌ Table 'advanced_memories' does not exist")
            return

        print("✅ Table exists")

        # Count total memories
        cursor.execute("SELECT COUNT(*) FROM advanced_memories")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total memories in database: {total_count}")

        if total_count > 0:
            # Get first few memories
            cursor.execute(
                "SELECT id, content, memory_type, tags FROM advanced_memories LIMIT 5"
            )
            memories = cursor.fetchall()

            print(f"\n📋 Sample memories:")
            for i, (mem_id, content, mem_type, tags) in enumerate(memories, 1):
                print(f"  {i}. ID: {mem_id}")
                print(f"     Type: {mem_type}")
                print(f"     Content: {content[:100]}...")
                print(f"     Tags: {tags}")
                print()

            # Search for Aetherra specifically
            cursor.execute(
                "SELECT id, content FROM advanced_memories WHERE content LIKE ? LIMIT 3",
                ("%Aetherra%",),
            )
            aetherra_memories = cursor.fetchall()

            print(f"🔍 Memories containing 'Aetherra': {len(aetherra_memories)}")
            for mem_id, content in aetherra_memories:
                print(f"  - {mem_id}: {content[:100]}...")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    check_database()
