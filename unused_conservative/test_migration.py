#!/usr/bin/env python3
"""
🧪 MEMORY MIGRATION TEST SCRIPT
===============================

Simple test to verify the migration script works with sample data.
Creates mock legacy databases and tests migration functionality.
"""

import asyncio
import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path


# Create test legacy databases
def create_test_advanced_memory_db(db_path: Path):
    """Create a test advanced memory database"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Create the schema
    cursor.execute("""
        CREATE TABLE advanced_memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            memory_type TEXT DEFAULT 'general',
            tags TEXT,
            confidence REAL DEFAULT 1.0,
            importance REAL DEFAULT 0.5,
            embedding_vector TEXT,
            timestamp TEXT,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0,
            context_data TEXT,
            uncertainty_score REAL DEFAULT 0.0,
            reflection_notes TEXT
        )
    """)

    # Insert test data
    test_memories = [
        (
            "test_001",
            "User asked about the weather today",
            "conversation",
            '["weather", "user_query"]',
            0.9,
            0.7,
            None,
            "2024-01-15T10:30:00",
            "2024-01-15T10:30:00",
            1,
            '{"topic": "weather", "intent": "information_request"}',
            0.1,
            "Clear user intent",
        ),
        (
            "test_002",
            "Successfully helped user understand plugin system",
            "achievement",
            '["plugin", "success", "learning"]',
            1.0,
            0.9,
            None,
            "2024-01-15T11:45:00",
            "2024-01-15T11:45:00",
            1,
            '{"outcome": "positive", "domain": "technical"}',
            0.0,
            "Good teaching moment",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO advanced_memories
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        test_memories,
    )

    conn.commit()
    conn.close()


def create_test_chat_memory_db(db_path: Path):
    """Create a test chat memory database"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY,
            user_message TEXT,
            assistant_response TEXT,
            timestamp TEXT,
            context TEXT
        )
    """)

    test_chats = [
        (
            1,
            "What's the capital of France?",
            "The capital of France is Paris.",
            "2024-01-15T09:00:00",
            "{}",
        ),
        (
            2,
            "How do I install Python?",
            "You can install Python by downloading it from python.org...",
            "2024-01-15T09:15:00",
            "{}",
        ),
    ]

    cursor.executemany("INSERT INTO chat_history VALUES (?, ?, ?, ?, ?)", test_chats)

    conn.commit()
    conn.close()


def create_test_json_memory(json_path: Path):
    """Create a test JSON memory file"""
    test_memories = [
        {
            "input": "Tell me about machine learning",
            "output": {
                "text": "Machine learning is a subset of AI that enables computers to learn without explicit programming..."
            },
            "context": {"topic": "AI", "intent": "education"},
            "timestamp": 1642248000000,  # JS timestamp
            "importance": 0.8,
        },
        {
            "input": "What's your favorite color?",
            "output": {
                "text": "I don't have personal preferences, but I find the concept of color fascinating..."
            },
            "context": {"topic": "personal", "intent": "casual"},
            "timestamp": 1642251600000,
            "importance": 0.3,
        },
    ]

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(test_memories, f)


async def test_migration():
    """Test the migration functionality"""
    print("🧪 MEMORY MIGRATION TEST")
    print("=" * 30)

    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test databases
        print("📝 Creating test legacy databases...")

        advanced_db = temp_path / "test_advanced_memory.db"
        chat_db = temp_path / "test_chat_history.db"
        json_memory = temp_path / "test_memory_export.json"

        create_test_advanced_memory_db(advanced_db)
        create_test_chat_memory_db(chat_db)
        create_test_json_memory(json_memory)

        print(f"   ✅ Created {advanced_db.name}")
        print(f"   ✅ Created {chat_db.name}")
        print(f"   ✅ Created {json_memory.name}")

        # Import and test migration
        try:
            from memory_migration_script_fixed import MemoryMigrationManager

            # Initialize migration manager
            print("\\n🔄 Initializing migration manager...")
            migration_manager = MemoryMigrationManager()

            # Discover test databases
            print("🔍 Discovering test databases...")
            discovered = await migration_manager.discover_legacy_databases([temp_path])

            print(f"   📊 Found {len(discovered)} test databases")
            for db in discovered:
                print(f"      • {db['path'].name} ({db['type']})")

            # Test migration
            if discovered:
                print("\\n🚀 Testing migration...")
                results = []

                for db_info in discovered:
                    print(f"   🔄 Migrating {db_info['path'].name}...")
                    result = await migration_manager.migrate_database(db_info)
                    results.append(result)

                    if result["success"]:
                        print(
                            f"      ✅ Success: {result['fragments_created']} fragments"
                        )
                    else:
                        print(
                            f"      ❌ Failed: {result.get('error', 'Unknown error')}"
                        )

                # Generate test report
                print("\\n📊 Generating test report...")
                report = await migration_manager.generate_migration_report(results)
                print(report)

                # Summary
                successful = sum(1 for r in results if r["success"])
                total_fragments = sum(
                    r["fragments_created"] for r in results if r["success"]
                )

                print(f"\\n🎯 TEST SUMMARY")
                print(f"   • Databases tested: {len(discovered)}")
                print(f"   • Successful migrations: {successful}")
                print(f"   • Total fragments created: {total_fragments}")

                if successful == len(discovered) and total_fragments > 0:
                    print("   ✅ All tests passed!")
                    return True
                else:
                    print("   ❌ Some tests failed!")
                    return False
            else:
                print("   ❌ No test databases discovered!")
                return False

        except ImportError as e:
            print(f"❌ Could not import migration script: {e}")
            print("💡 Make sure the migration script is in the same directory")
            return False
        except Exception as e:
            print(f"❌ Migration test failed: {e}")
            return False


if __name__ == "__main__":
    success = asyncio.run(test_migration())
    if success:
        print("\\n🎉 Migration system is ready!")
        print("💡 Run 'python memory_migration_script_fixed.py' to migrate real data")
    else:
        print("\\n⚠️ Migration system needs attention")
        print("🔧 Check the errors above and fix before proceeding")
