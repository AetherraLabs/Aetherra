"""
Memory Adapter Implementation - Connect all memory systems
Real implementation for memory integration across all databases
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class MemoryAdapterImpl:
    """Real memory adapter connecting all migrated databases"""

    def __init__(self, aetherra_v2_root: Path):
        self.aetherra_v2_root = Path(aetherra_v2_root)
        self.db_paths = {
            "core": self.aetherra_v2_root / "data" / "databases" / "core",
            "lyrixa": self.aetherra_v2_root / "data" / "databases" / "lyrixa",
            "shared": self.aetherra_v2_root / "data" / "databases" / "shared",
        }
        self.connections = {}

    def connect_all_databases(self) -> Dict[str, bool]:
        """Connect to all available databases"""
        connection_status = {}

        for category, db_dir in self.db_paths.items():
            if db_dir.exists():
                db_files = list(db_dir.glob("*.db"))
                for db_file in db_files:
                    try:
                        conn = sqlite3.connect(str(db_file))
                        conn.row_factory = sqlite3.Row  # Enable column access by name
                        self.connections[db_file.stem] = conn
                        connection_status[db_file.stem] = True
                    except Exception as e:
                        connection_status[db_file.stem] = False
                        print(f"Failed to connect to {db_file.stem}: {e}")

        return connection_status

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of all memory systems"""
        summary = {
            "total_databases": len(self.connections),
            "categories": {},
            "memory_counts": {},
            "total_entries": 0,
        }

        for category, db_dir in self.db_paths.items():
            if db_dir.exists():
                db_files = list(db_dir.glob("*.db"))
                category_entries = 0

                for db_file in db_files:
                    db_name = db_file.stem
                    if db_name in self.connections:
                        try:
                            conn = self.connections[db_name]
                            cursor = conn.cursor()

                            # Get all tables
                            cursor.execute(
                                "SELECT name FROM sqlite_master WHERE type='table';"
                            )
                            tables = cursor.fetchall()

                            db_entries = 0
                            for table in tables:
                                table_name = table["name"]
                                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                                count = cursor.fetchone()[0]
                                db_entries += count

                            category_entries += db_entries
                            summary["memory_counts"][db_name] = db_entries

                        except Exception as e:
                            print(f"Error reading {db_name}: {e}")

                summary["categories"][category] = {
                    "databases": len(db_files),
                    "entries": category_entries,
                }
                summary["total_entries"] += category_entries

        return summary

    def store_context(self, context_type: str, context_data: Dict) -> bool:
        """Store context across appropriate databases"""
        try:
            # Choose appropriate database based on context type
            target_db = self._select_target_database(context_type)

            if target_db and target_db in self.connections:
                conn = self.connections[target_db]
                cursor = conn.cursor()

                # Create context table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS context_storage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        context_type TEXT,
                        timestamp TEXT,
                        data TEXT
                    )
                """)

                # Insert context data
                cursor.execute(
                    """
                    INSERT INTO context_storage (context_type, timestamp, data)
                    VALUES (?, ?, ?)
                """,
                    (
                        context_type,
                        datetime.now().isoformat(),
                        json.dumps(context_data),
                    ),
                )

                conn.commit()
                return True

        except Exception as e:
            print(f"Error storing context: {e}")

        return False

    def retrieve_context(self, context_type: str, limit: int = 10) -> List[Dict]:
        """Retrieve context from databases"""
        contexts = []

        # Search across all connected databases
        for db_name, conn in self.connections.items():
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT * FROM context_storage
                    WHERE context_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """,
                    (context_type, limit),
                )

                rows = cursor.fetchall()
                for row in rows:
                    contexts.append(
                        {
                            "id": row["id"],
                            "context_type": row["context_type"],
                            "timestamp": row["timestamp"],
                            "data": json.loads(row["data"]),
                            "source_db": db_name,
                        }
                    )

            except Exception:
                # Table might not exist in this database
                continue

        # Sort by timestamp and return most recent
        contexts.sort(key=lambda x: x["timestamp"], reverse=True)
        return contexts[:limit]

    def sync_memories(self) -> Dict[str, int]:
        """Synchronize memories between databases"""
        sync_results = {}

        # Get memories from main Lyrixa database
        if "lyrixa_memory" in self.connections:
            try:
                conn = self.connections["lyrixa_memory"]
                cursor = conn.cursor()

                # Get recent memories
                cursor.execute("""
                    SELECT * FROM memory_entries
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)

                memories = cursor.fetchall()
                sync_results["source_memories"] = len(memories)

                # Sync to shared memory systems
                synced_count = 0
                for memory in memories:
                    if self._sync_single_memory(memory):
                        synced_count += 1

                sync_results["synced_memories"] = synced_count

            except Exception as e:
                sync_results["error"] = str(e)

        return sync_results

    def _select_target_database(self, context_type: str) -> Optional[str]:
        """Select appropriate database for context type"""
        # Map context types to database preferences
        context_mapping = {
            "lyrixa": "lyrixa_memory",
            "aetherra": "reasoning_engine",
            "agent": "agent_orchestrator",
            "memory": "hybrid_memory",
            "async": "async_memory",
            "fractal": "fractal_memory",
        }

        for key, db_name in context_mapping.items():
            if key in context_type.lower() and db_name in self.connections:
                return db_name

        # Default to first available shared database
        for db_name in self.connections:
            if any(shared_db in db_name for shared_db in ["shared", "hybrid", "async"]):
                return db_name

        return None

    def _sync_single_memory(self, memory) -> bool:
        """Sync a single memory to appropriate databases"""
        try:
            # Store in fractal memory if available
            if "fractal_memory" in self.connections:
                conn = self.connections["fractal_memory"]
                cursor = conn.cursor()

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS synced_memories (
                        id INTEGER PRIMARY KEY,
                        original_id INTEGER,
                        content TEXT,
                        timestamp TEXT,
                        source_db TEXT
                    )
                """)

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO synced_memories
                    (original_id, content, timestamp, source_db)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        memory["id"],
                        memory.get("content", ""),
                        memory.get("timestamp", ""),
                        "lyrixa_memory",
                    ),
                )

                conn.commit()
                return True

        except Exception:
            pass

        return False

    def get_database_health(self) -> Dict[str, Any]:
        """Get health status of all databases"""
        health = {
            "connected_databases": len(self.connections),
            "database_status": {},
            "total_size_mb": 0,
        }

        for db_name, conn in self.connections.items():
            try:
                cursor = conn.cursor()

                # Get database info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                # Calculate total entries
                total_entries = 0
                for table in tables:
                    table_name = table["name"]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_entries += count

                health["database_status"][db_name] = {
                    "tables": len(tables),
                    "entries": total_entries,
                    "status": "healthy",
                }

            except Exception as e:
                health["database_status"][db_name] = {
                    "status": "error",
                    "error": str(e),
                }

        return health

    def close_all_connections(self):
        """Close all database connections"""
        for db_name, conn in self.connections.items():
            try:
                conn.close()
            except Exception:
                pass

        self.connections.clear()

    def test_memory_integration(self) -> Dict[str, Any]:
        """Test memory integration functionality"""
        test_results = {
            "connection_test": False,
            "context_storage_test": False,
            "memory_sync_test": False,
            "health_check_test": False,
        }

        try:
            # Test connections
            connections = self.connect_all_databases()
            test_results["connection_test"] = len(connections) > 0

            # Test context storage
            test_context = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "phase": "integration_test",
            }

            if self.store_context("integration_test", test_context):
                retrieved = self.retrieve_context("integration_test", 1)
                test_results["context_storage_test"] = len(retrieved) > 0

            # Test memory sync
            sync_results = self.sync_memories()
            test_results["memory_sync_test"] = "error" not in sync_results

            # Test health check
            health = self.get_database_health()
            test_results["health_check_test"] = health["connected_databases"] > 0

        except Exception as e:
            test_results["error"] = str(e)

        return test_results


def main():
    """Test memory adapter implementation"""
    workspace = Path(r"c:\Users\enigm\Desktop\Aetherra Project")
    aetherra_v2 = workspace / "Aetherra_v2"

    print("🧠 TESTING MEMORY ADAPTER IMPLEMENTATION")
    print("=" * 50)

    adapter = MemoryAdapterImpl(aetherra_v2)

    # Run integration test
    test_results = adapter.test_memory_integration()

    print("📊 Test Results:")
    for test_name, result in test_results.items():
        if test_name != "error":
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}: {result}")
        else:
            print(f"  ❌ Error: {result}")

    # Get memory summary
    if test_results["connection_test"]:
        summary = adapter.get_memory_summary()
        print(f"\n📈 Memory Summary:")
        print(f"  🗄️ Total databases: {summary['total_databases']}")
        print(f"  📊 Total entries: {summary['total_entries']}")

        for category, info in summary["categories"].items():
            print(
                f"  📂 {category}: {info['databases']} databases, {info['entries']} entries"
            )

    adapter.close_all_connections()
    print("\n✅ Memory adapter test complete!")


if __name__ == "__main__":
    main()
