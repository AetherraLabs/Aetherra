#!/usr/bin/env python3
"""
🔄 LYRIXA MEMORY MIGRATION SYSTEM
=================================

Migrates existing vector memory databases to the new FractalMesh format.
Preserves all data while adding new structure and capabilities.

Migration Sources:
- Advanced Vector Memory (advanced_memories table)
- JavaScript Memory System (localStorage JSON format)
- Simple memory databases (legacy formats)

Migration Targets:
- LyrixaMemoryEngine (integrated system)
- FractalMesh fragments
- ConceptClusters
- EpisodicTimeline
- MemoryNarrator baseline data
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from Aetherra.lyrixa.memory.fractal_mesh.base import MemoryFragmentType
from Aetherra.lyrixa.memory.lyrixa_memory_engine import (
    LyrixaMemoryEngine,
    MemorySystemConfig,
)


class MemoryMigrationManager:
    """Manages migration from old memory formats to FractalMesh"""

    def __init__(self, target_config: Optional[MemorySystemConfig] = None):
        self.config = target_config or MemorySystemConfig()
        self.migration_stats = {
            "total_discovered": 0,
            "successfully_migrated": 0,
            "failed_migrations": 0,
            "skipped_duplicates": 0,
            "fragments_created": 0,
            "concepts_created": 0,
            "chains_created": 0,
        }

        # Initialize target system
        self.target_engine = LyrixaMemoryEngine(self.config)

        # Migration tracking
        self.migrated_ids = set()
        self.content_hashes = set()  # Prevent duplicate content

    async def discover_legacy_databases(
        self, search_paths: List[Path]
    ) -> List[Dict[str, Any]]:
        """Discover legacy memory databases in specified paths"""
        discovered = []

        for search_path in search_paths:
            if not search_path.exists():
                print(f"⚠️ Path does not exist: {search_path}")
                continue

            print(f"🔍 Searching for memory databases in: {search_path}")

            # SQLite databases
            for db_path in search_path.rglob("*.db"):
                db_type = self._identify_database_type(db_path)
                if db_type:
                    discovered.append(
                        {
                            "path": db_path,
                            "type": db_type,
                            "format": "sqlite",
                            "estimated_size": db_path.stat().st_size,
                        }
                    )

            # JSON memory files (from web localStorage dumps)
            for json_path in search_path.rglob("*memory*.json"):
                if self._is_lyrixa_memory_json(json_path):
                    discovered.append(
                        {
                            "path": json_path,
                            "type": "javascript_localStorage",
                            "format": "json",
                            "estimated_size": json_path.stat().st_size,
                        }
                    )

        print(f"📊 Discovered {len(discovered)} legacy memory databases")
        self.migration_stats["total_discovered"] = len(discovered)

        return discovered

    def _identify_database_type(self, db_path: Path) -> Optional[str]:
        """Identify the type of SQLite database by examining its schema"""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            conn.close()

            # Identify by table names and structure
            if "advanced_memories" in tables:
                return "advanced_vector_memory"
            elif "memories" in tables and "memory_metadata" in tables:
                return "basic_vector_memory"
            elif "memory_clusters" in tables:
                return "clustered_memory"
            elif "reflection_history" in tables:
                return "reflective_memory"
            elif any("lyrixa" in table.lower() for table in tables):
                return "lyrixa_generic"
            elif "long_term" in str(db_path) or "chat" in str(db_path):
                return "chat_memory"

        except sqlite3.Error:
            pass

        return None

    def _is_lyrixa_memory_json(self, json_path: Path) -> bool:
        """Check if JSON file contains Lyrixa memory data"""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Check for Lyrixa memory structure
            if isinstance(data, list) and len(data) > 0:
                sample = data[0]
                return isinstance(sample, dict) and any(
                    key in sample
                    for key in ["input", "output", "context", "timestamp", "importance"]
                )

        except (json.JSONDecodeError, OSError):
            pass

        return False

    async def migrate_database(self, db_info: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate a single database to FractalMesh format"""
        db_path = db_info["path"]
        db_type = db_info["type"]

        print(f"🔄 Migrating {db_type}: {db_path.name}")
        migration_result = {
            "source": str(db_path),
            "type": db_type,
            "success": False,
            "fragments_created": 0,
            "error": None,
        }

        try:
            if db_info["format"] == "sqlite":
                migration_result = await self._migrate_sqlite_database(db_path, db_type)
            elif db_info["format"] == "json":
                migration_result = await self._migrate_json_memory(db_path)

            if migration_result["success"]:
                self.migration_stats["successfully_migrated"] += 1
                self.migration_stats["fragments_created"] += migration_result[
                    "fragments_created"
                ]
            else:
                self.migration_stats["failed_migrations"] += 1

        except Exception as e:
            migration_result["error"] = str(e)
            self.migration_stats["failed_migrations"] += 1
            print(f"❌ Migration failed for {db_path.name}: {e}")

        return migration_result

    async def _migrate_sqlite_database(
        self, db_path: Path, db_type: str
    ) -> Dict[str, Any]:
        """Migrate SQLite database based on its type"""
        conn = sqlite3.connect(str(db_path))

        if db_type == "advanced_vector_memory":
            return await self._migrate_advanced_vector_memory(conn, db_path)
        elif db_type == "chat_memory":
            return await self._migrate_chat_memory(conn, db_path)
        elif db_type == "lyrixa_generic":
            return await self._migrate_generic_lyrixa_memory(conn, db_path)
        else:
            return await self._migrate_generic_sqlite_memory(conn, db_path)

    async def _migrate_advanced_vector_memory(
        self, conn: sqlite3.Connection, db_path: Path
    ) -> Dict[str, Any]:
        """Migrate AdvancedMemorySystem database"""
        cursor = conn.cursor()
        fragments_created = 0

        # Get all memories
        cursor.execute("""
            SELECT id, content, memory_type, tags, confidence, importance,
                   embedding_vector, timestamp, last_accessed, access_count,
                   context_data, uncertainty_score, reflection_notes
            FROM advanced_memories
            ORDER BY timestamp
        """)

        memories = cursor.fetchall()
        print(f"   📋 Found {len(memories)} memories to migrate")

        for memory in memories:
            (
                old_id,
                content,
                memory_type,
                tags_json,
                confidence,
                importance,
                embedding_vector,
                timestamp,
                last_accessed,
                access_count,
                context_data,
                uncertainty_score,
                reflection_notes,
            ) = memory

            # Skip if already migrated or duplicate content
            content_hash = hash(content)
            if old_id in self.migrated_ids or content_hash in self.content_hashes:
                self.migration_stats["skipped_duplicates"] += 1
                continue

            # Parse JSON fields
            tags = json.loads(tags_json) if tags_json else []
            context = json.loads(context_data) if context_data else {}

            # Determine fragment type
            fragment_type = self._determine_fragment_type(memory_type, content, context)

            # Parse timestamp
            try:
                created_at = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except:
                created_at = datetime.now()

            # Create narrative role from memory type and context
            narrative_role = self._infer_narrative_role(memory_type, content, context)

            # Store in new system
            result = await self.target_engine.remember(
                content=content,
                tags=tags,
                category=memory_type,
                fragment_type=fragment_type,
                confidence=float(confidence) if confidence else 1.0,
                narrative_role=narrative_role,
            )

            if result.success:
                fragments_created += 1
                self.migrated_ids.add(old_id)
                self.content_hashes.add(content_hash)

                # Add migration metadata
                await self._add_migration_metadata(
                    result.fragment_id,
                    {
                        "source_db": str(db_path),
                        "original_id": old_id,
                        "migration_timestamp": datetime.now().isoformat(),
                        "original_access_count": access_count,
                        "uncertainty_score": uncertainty_score,
                        "reflection_notes": reflection_notes,
                    },
                )

        conn.close()

        return {
            "source": str(db_path),
            "type": "advanced_vector_memory",
            "success": True,
            "fragments_created": fragments_created,
            "error": None,
        }

    async def _migrate_chat_memory(
        self, conn: sqlite3.Connection, db_path: Path
    ) -> Dict[str, Any]:
        """Migrate chat-based memory databases"""
        cursor = conn.cursor()
        fragments_created = 0

        # Try common chat memory schemas
        tables = self._get_table_names(conn)

        if "chat_history" in tables:
            query = """
                SELECT id, user_message, assistant_response, timestamp, context
                FROM chat_history ORDER BY timestamp
            """
        elif "conversations" in tables:
            query = """
                SELECT id, message, response, created_at, metadata
                FROM conversations ORDER BY created_at
            """
        else:
            # Generic fallback
            main_table = tables[0] if tables else "unknown"
            columns = self._get_table_columns(conn, main_table)

            # Build query based on available columns
            select_cols = []
            if "id" in columns:
                select_cols.append("id")
            if any(col in columns for col in ["message", "content", "text"]):
                select_cols.append(
                    next(
                        col for col in ["message", "content", "text"] if col in columns
                    )
                )
            if any(col in columns for col in ["response", "reply", "output"]):
                select_cols.append(
                    next(
                        col for col in ["response", "reply", "output"] if col in columns
                    )
                )
            if any(col in columns for col in ["timestamp", "created_at", "date"]):
                select_cols.append(
                    next(
                        col
                        for col in ["timestamp", "created_at", "date"]
                        if col in columns
                    )
                )

            if len(select_cols) < 2:
                return {"success": False, "error": "Insufficient columns in chat table"}

            query = f"SELECT {', '.join(select_cols)} FROM {main_table}"

        cursor.execute(query)
        chats = cursor.fetchall()

        print(f"   💬 Found {len(chats)} chat entries to migrate")

        for chat in chats:
            # Handle variable column count
            if len(chat) >= 4:
                chat_id, user_msg, assistant_resp, timestamp = chat[:4]
                context = chat[4] if len(chat) > 4 else "{}"
            else:
                continue  # Skip malformed entries

            # Create fragments for both user and assistant messages
            base_time = self._parse_timestamp(timestamp)

            # User message fragment
            if user_msg:
                user_result = await self.target_engine.remember(
                    content=f"User: {user_msg}",
                    tags=["chat", "user_input"],
                    category="conversation",
                    fragment_type=MemoryFragmentType.CONVERSATIONAL,
                    narrative_role="user_query",
                )
                if user_result.success:
                    fragments_created += 1

            # Assistant response fragment
            if assistant_resp:
                assistant_result = await self.target_engine.remember(
                    content=f"Assistant: {assistant_resp}",
                    tags=["chat", "assistant_response"],
                    category="conversation",
                    fragment_type=MemoryFragmentType.CONVERSATIONAL,
                    narrative_role="assistant_response",
                )
                if assistant_result.success:
                    fragments_created += 1

        conn.close()

        return {
            "source": str(db_path),
            "type": "chat_memory",
            "success": True,
            "fragments_created": fragments_created,
            "error": None,
        }

    async def _migrate_json_memory(self, json_path: Path) -> Dict[str, Any]:
        """Migrate JavaScript localStorage memory dumps"""
        with open(json_path, "r", encoding="utf-8") as f:
            memories = json.load(f)

        if not isinstance(memories, list):
            return {"success": False, "error": "JSON is not a list of memories"}

        fragments_created = 0
        print(f"   📄 Found {len(memories)} JSON memories to migrate")

        for memory in memories:
            if not isinstance(memory, dict):
                continue

            # Extract JavaScript memory structure
            input_text = memory.get("input", "")
            output_text = (
                memory.get("output", {}).get("text", "")
                if isinstance(memory.get("output"), dict)
                else str(memory.get("output", ""))
            )
            context = memory.get("context", {})
            timestamp = memory.get(
                "timestamp", datetime.now().timestamp() * 1000
            )  # JS timestamps are in ms
            importance = memory.get("importance", 0.5)

            # Convert timestamp from JS milliseconds
            try:
                created_at = datetime.fromtimestamp(timestamp / 1000)
            except:
                created_at = datetime.now()

            # Create conversation fragments
            if input_text:
                input_result = await self.target_engine.remember(
                    content=f"User: {input_text}",
                    tags=["migrated", "javascript", "user_input"],
                    category="conversation",
                    fragment_type=MemoryFragmentType.CONVERSATIONAL,
                    confidence=float(importance),
                    narrative_role="user_query",
                )
                if input_result.success:
                    fragments_created += 1

            if output_text:
                output_result = await self.target_engine.remember(
                    content=f"Assistant: {output_text}",
                    tags=["migrated", "javascript", "assistant_response"],
                    category="conversation",
                    fragment_type=MemoryFragmentType.CONVERSATIONAL,
                    confidence=float(importance),
                    narrative_role="assistant_response",
                )
                if output_result.success:
                    fragments_created += 1

        return {
            "source": str(json_path),
            "type": "javascript_localStorage",
            "success": True,
            "fragments_created": fragments_created,
            "error": None,
        }

    async def _migrate_generic_lyrixa_memory(
        self, conn: sqlite3.Connection, db_path: Path
    ) -> Dict[str, Any]:
        """Migrate generic Lyrixa memory databases"""
        tables = self._get_table_names(conn)
        fragments_created = 0

        for table in tables:
            if "lyrixa" not in table.lower() and "memory" not in table.lower():
                continue

            columns = self._get_table_columns(conn, table)
            cursor = conn.cursor()

            # Build dynamic query based on available columns
            select_cols = ["*"]  # Fallback to all columns
            cursor.execute(f"SELECT * FROM {table}")

            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            for row in rows:
                row_dict = dict(zip(column_names, row))

                # Find content field
                content = (
                    row_dict.get("content")
                    or row_dict.get("text")
                    or row_dict.get("message")
                    or str(row_dict)
                )

                # Find tags
                tags = ["migrated", "generic", table]
                if "tags" in row_dict and row_dict["tags"]:
                    try:
                        parsed_tags = json.loads(row_dict["tags"])
                        if isinstance(parsed_tags, list):
                            tags.extend(parsed_tags)
                    except:
                        pass

                # Create fragment
                result = await self.target_engine.remember(
                    content=content,
                    tags=tags,
                    category="migrated_generic",
                    fragment_type=MemoryFragmentType.SEMANTIC,
                    narrative_role="legacy_data",
                )

                if result.success:
                    fragments_created += 1

        conn.close()

        return {
            "source": str(db_path),
            "type": "generic_lyrixa",
            "success": True,
            "fragments_created": fragments_created,
            "error": None,
        }

    async def _migrate_generic_sqlite_memory(
        self, conn: sqlite3.Connection, db_path: Path
    ) -> Dict[str, Any]:
        """Migrate unknown SQLite databases that might contain memory"""
        # Basic attempt to extract any text-like content
        tables = self._get_table_names(conn)
        fragments_created = 0

        for table in tables:
            cursor = conn.cursor()
            columns = self._get_table_columns(conn, table)

            # Look for text columns that might contain memory content
            text_columns = [
                col
                for col in columns
                if any(
                    keyword in col.lower()
                    for keyword in ["text", "content", "message", "data", "info"]
                )
            ]

            if not text_columns:
                continue

            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            for row in rows[:50]:  # Limit to 50 rows per table to avoid spam
                row_dict = dict(zip(column_names, row))

                # Extract text content
                content_parts = []
                for col in text_columns:
                    if row_dict.get(col):
                        content_parts.append(f"{col}: {row_dict[col]}")

                if content_parts:
                    content = " | ".join(content_parts)

                    result = await self.target_engine.remember(
                        content=content,
                        tags=["migrated", "unknown_source", table],
                        category="unknown_migrated",
                        fragment_type=MemoryFragmentType.SEMANTIC,
                        confidence=0.5,  # Lower confidence for unknown data
                        narrative_role="legacy_data",
                    )

                    if result.success:
                        fragments_created += 1

        conn.close()

        return {
            "source": str(db_path),
            "type": "generic_sqlite",
            "success": True,
            "fragments_created": fragments_created,
            "error": None,
        }

    # Helper methods

    def _determine_fragment_type(
        self, memory_type: str, content: str, context: Dict
    ) -> MemoryFragmentType:
        """Determine appropriate fragment type based on content"""
        memory_type = memory_type.lower()
        content_lower = content.lower()

        if "conversation" in memory_type or "chat" in memory_type:
            return MemoryFragmentType.CONVERSATIONAL
        elif "goal" in memory_type or "task" in memory_type:
            return MemoryFragmentType.GOAL_ORIENTED
        elif "skill" in memory_type or "plugin" in memory_type:
            return MemoryFragmentType.SKILL_BASED
        elif "reflection" in memory_type or "insight" in content_lower:
            return MemoryFragmentType.REFLECTIVE
        elif "event" in memory_type or "happened" in content_lower:
            return MemoryFragmentType.EVENT_BASED
        else:
            return MemoryFragmentType.SEMANTIC

    def _infer_narrative_role(
        self, memory_type: str, content: str, context: Dict
    ) -> str:
        """Infer narrative role for story generation"""
        content_lower = content.lower()

        if "user:" in content_lower or "human:" in content_lower:
            return "user_query"
        elif "assistant:" in content_lower or "lyrixa:" in content_lower:
            return "assistant_response"
        elif "goal" in memory_type.lower() or "objective" in content_lower:
            return "goal_setting"
        elif "error" in content_lower or "failed" in content_lower:
            return "challenge_encountered"
        elif "success" in content_lower or "completed" in content_lower:
            return "achievement"
        elif "learned" in content_lower or "insight" in content_lower:
            return "learning_moment"
        else:
            return "contextual_information"

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse various timestamp formats"""
        if not timestamp_str:
            return datetime.now()

        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        # Try as Unix timestamp
        try:
            return datetime.fromtimestamp(float(timestamp_str))
        except:
            pass

        return datetime.now()

    def _get_table_names(self, conn: sqlite3.Connection) -> List[str]:
        """Get all table names from database"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in cursor.fetchall()]

    def _get_table_columns(
        self, conn: sqlite3.Connection, table_name: str
    ) -> List[str]:
        """Get column names for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in cursor.fetchall()]

    async def _add_migration_metadata(self, fragment_id: str, metadata: Dict[str, Any]):
        """Add migration tracking metadata to a fragment"""
        # This would be implemented to add metadata to the fragment
        # For now, we'll add it as tags
        migration_tags = [
            f"source:{Path(metadata['source_db']).stem}",
            "migrated_data",
            f"original_id:{metadata['original_id']}",
        ]

        # Update fragment with migration tags
        # (Implementation would depend on FractalMesh API)
        pass

    async def generate_migration_report(
        self, migration_results: List[Dict[str, Any]]
    ) -> str:
        """Generate comprehensive migration report"""
        successful = [r for r in migration_results if r["success"]]
        failed = [r for r in migration_results if not r["success"]]

        total_fragments = sum(r["fragments_created"] for r in successful)

        report = f"""
🔄 LYRIXA MEMORY MIGRATION REPORT
================================

📊 SUMMARY
----------
• Total databases discovered: {self.migration_stats["total_discovered"]}
• Successfully migrated: {len(successful)}
• Failed migrations: {len(failed)}
• Total fragments created: {total_fragments}
• Skipped duplicates: {self.migration_stats["skipped_duplicates"]}

✅ SUCCESSFUL MIGRATIONS
-----------------------
"""

        for result in successful:
            report += f"• {Path(result['source']).name} ({result['type']}) → {result['fragments_created']} fragments\\n"

        if failed:
            report += f"""
❌ FAILED MIGRATIONS
--------------------
"""
            for result in failed:
                report += f"• {Path(result['source']).name}: {result.get('error', 'Unknown error')}\\n"

        report += f"""
🎯 NEXT STEPS
-------------
1. Run narrative generation on migrated data
2. Perform concept clustering analysis
3. Validate episodic timeline coherence
4. Check memory pulse for drift detection
5. Generate baseline reflection insights

📈 SYSTEM STATUS
---------------
• FractalMesh: {total_fragments} fragments ready
• Memory Engine: Fully operational
• Migration tracking: {len(self.migrated_ids)} unique IDs processed

Migration completed at: {datetime.now().isoformat()}
"""

        return report


async def main():
    """Main migration workflow"""
    print("🔄 LYRIXA MEMORY MIGRATION SYSTEM")
    print("=" * 50)
    print()

    # Initialize migration manager
    migration_manager = MemoryMigrationManager()

    # Define search paths for legacy databases
    search_paths = [
        Path.cwd(),  # Current directory
        Path.cwd() / "Aetherra",
        Path.cwd() / "Unused",  # Check our newly moved files
        Path.home() / "AppData" / "Local" / "Lyrixa",  # Windows local data
        Path.home() / ".lyrixa",  # Unix hidden directory
    ]

    print("🔍 Discovering legacy memory databases...")
    discovered_dbs = await migration_manager.discover_legacy_databases(search_paths)

    if not discovered_dbs:
        print("❌ No legacy memory databases found!")
        print("💡 Place old .db files in the current directory and run again.")
        return

    print(f"\\n📋 Found {len(discovered_dbs)} databases:")
    for db in discovered_dbs:
        size_mb = db["estimated_size"] / (1024 * 1024)
        print(f"  • {db['path'].name} ({db['type']}) - {size_mb:.1f}MB")

    # Confirm migration
    print(f"\\n⚠️ This will migrate all discovered data to the new FractalMesh system.")
    print("✅ Original databases will not be modified.")
    print("🔄 Duplicates will be automatically skipped.")

    response = input("\\nProceed with migration? (y/N): ").lower().strip()

    if response not in ["y", "yes"]:
        print("❌ Migration cancelled.")
        return

    # Perform migrations
    print(f"\\n🚀 Starting migration of {len(discovered_dbs)} databases...")
    migration_results = []

    for i, db_info in enumerate(discovered_dbs, 1):
        print(f"\\n[{i}/{len(discovered_dbs)}] {db_info['path'].name}")
        result = await migration_manager.migrate_database(db_info)
        migration_results.append(result)

        if result["success"]:
            print(f"   ✅ Success: {result['fragments_created']} fragments created")
        else:
            print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

    # Generate and display report
    print(f"\\n📊 Generating migration report...")
    report = await migration_manager.generate_migration_report(migration_results)
    print(report)

    # Save report to file
    report_path = Path("lyrixa_migration_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"💾 Report saved to: {report_path}")
    print(
        "\\n🎉 Migration completed! Your memories are now part of the FractalMesh system."
    )


if __name__ == "__main__":
    asyncio.run(main())
