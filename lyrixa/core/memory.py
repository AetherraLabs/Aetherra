#!/usr/bin/env python3
"""
🧠 LYRIXA MEMORY SYSTEM
======================

Lyrixa's memory capabilities for learning, context retention, and user preferences.
Manages conversational memory, project context, and long-term learning.
"""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

# from src.aetherra.core.webhook_manager import WebhookManager  # TODO: Fix this import


@dataclass
class Memory:
    """Represents a single memory entry"""

    id: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    tags: List[str]
    importance: float  # 0.0 to 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int
    memory_type: str  # conversation, project, preference, learning


@dataclass
class MemoryQuery:
    """Represents a memory search query"""

    text: Optional[str] = None
    tags: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    memory_type: Optional[str] = None
    importance_threshold: float = 0.0
    limit: int = 10
    time_range: Optional[Tuple[datetime, datetime]] = None


class LyrixaMemorySystem:
    """
    Lyrixa's comprehensive memory management system

    Handles conversation memory, project context, user preferences,
    and learning from interactions to provide better assistance.
    """

    def __init__(self, memory_db_path: str = ":memory:"):
        self.db_path = memory_db_path
        self.conn: Optional[sqlite3.Connection] = sqlite3.connect(
            self.db_path
        )  # Initialize connection
        self.memory_cache: Dict[str, Any] = {}
        self.consolidation_interval = 3600  # 1 hour in seconds
        # self.webhook_manager = WebhookManager()  # Initialize WebhookManager  # TODO: Fix this import

        # Initialize database synchronously
        self._initialize_database_sync()

    def ensure_connection(self) -> sqlite3.Connection:
        """Ensures the database connection is open and returns it."""
        if self.conn is None:
            print("🔄 Reopening database connection...")
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def _initialize_database_sync(self):
        """Initialize the SQLite database for memory storage (synchronous version)"""
        conn = self.ensure_connection()  # Ensure connection is open
        try:
            cursor = conn.cursor()

            # Create memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    context TEXT,
                    tags TEXT,
                    importance REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    memory_type TEXT NOT NULL
                )
            """)

            # Create indexes for efficient querying
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON memories(tags)")

            conn.commit()

            print("✅ Lyrixa memory system initialized")

        except Exception as e:
            print(f"❌ Failed to initialize memory database: {e}")

    def normalize_importance(self, value: Any) -> float:
        """Normalize importance to a float between 0.0 and 1.0."""
        try:
            return min(1.0, max(0.0, float(value)))
        except (TypeError, ValueError):
            return 0.0  # Safe fallback

    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize query parameters."""
        validated = {}
        validated["importance"] = self.normalize_importance(
            params.get("importance", 0.0)
        )
        validated["text"] = str(params.get("text", ""))
        validated["tags"] = (
            params.get("tags", []) if isinstance(params.get("tags"), list) else []
        )
        validated["context"] = (
            params.get("context", {}) if isinstance(params.get("context"), dict) else {}
        )
        return validated

    async def store_memory(
        self,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        memory_type: str = "conversation",
    ) -> str:
        """
        Store a new memory

        Args:
            content: The main content of the memory
            context: Additional context information
            tags: List of tags for categorization
            importance: Importance score (0.0 to 1.0)
            memory_type: Type of memory (conversation, project, preference, learning)

        Returns:
            Memory ID
        """
        memory_id = self._generate_memory_id(content, context)

        try:
            # Validate and normalize parameters
            validated_params = self.validate_params(
                {
                    "importance": importance,
                    "tags": tags,
                    "context": context,
                }
            )

            memory = Memory(
                id=memory_id,
                content=content,
                context=validated_params["context"],
                tags=validated_params["tags"],
                importance=validated_params["importance"],
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                memory_type=memory_type,
            )

            with self.db_session():
                cursor = self.ensure_connection().cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memories
                    (id, content, context, tags, importance, created_at, last_accessed, access_count, memory_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        memory.id,
                        json.dumps(memory.content),
                        json.dumps(memory.context),
                        json.dumps(memory.tags),
                        memory.importance,
                        memory.created_at.isoformat(),
                        memory.last_accessed.isoformat(),
                        memory.access_count,
                        memory.memory_type,
                    ),
                )
                self.ensure_connection().commit()

            # Cache the memory
            self.memory_cache[memory_id] = memory

            return memory_id

        except (ValueError, TypeError) as e:
            print(f"❌ Failed to store memory due to type error: {e}")
            return ""

        except Exception as e:
            print(f"❌ Failed to store memory: {e}")
            return ""

    async def recall_memories(
        self, query_text: str, limit: int = 5, memory_type: Optional[str] = None
    ) -> List[Memory]:
        """
        Recall memories based on text similarity and relevance

        Args:
            query_text: Text to search for
            limit: Maximum number of memories to return
            memory_type: Optional filter by memory type

        Returns:
            List of relevant memories
        """
        try:
            cursor = self.ensure_connection().cursor()

            # Build query
            sql = """
                SELECT id, content, context, tags, importance, created_at, last_accessed, access_count, memory_type
                FROM memories
                WHERE 1=1
            """
            params: List[Any] = []

            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)

            # Simple text matching (in a real implementation, use vector search)
            if query_text:
                sql += " AND (content LIKE ? OR tags LIKE ?)"
                params.extend([f"%{query_text}%", f"%{query_text}%"])

            sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            memories = []
            for row in rows:
                memory = Memory(
                    id=row[0],
                    content=json.loads(row[1]),
                    context=json.loads(row[2]) if row[2] else {},
                    tags=json.loads(row[3]) if row[3] else [],
                    importance=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    last_accessed=datetime.fromisoformat(row[6]),
                    access_count=row[7],
                    memory_type=row[8],
                )
                memories.append(memory)

                # Update access count
                await self._update_memory_access(memory.id)

            return memories

        except Exception as e:
            print(f"❌ Failed to recall memories: {e}")
            return []

    async def get_conversation_context(
        self, session_id: str, limit: int = 10
    ) -> List[Memory]:
        """Get recent conversation context for a session"""
        return await self.recall_memories(
            query_text=session_id, limit=limit, memory_type="conversation"
        )

    async def store_user_preference(
        self,
        preference_key: str,
        preference_value: Any,
        user_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a user preference"""
        content = {
            "preference_key": preference_key,
            "preference_value": preference_value,
        }

        return await self.store_memory(
            content=content,
            context=user_context or {},
            tags=["preference", preference_key],
            importance=0.8,
            memory_type="preference",
        )

    async def get_user_preferences(
        self, user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get user preferences"""
        memories = await self.recall_memories(
            query_text="", limit=100, memory_type="preference"
        )

        preferences = {}
        for memory in memories:
            if (
                "preference_key" in memory.content
                and "preference_value" in memory.content
            ):
                preferences[memory.content["preference_key"]] = memory.content[
                    "preference_value"
                ]

        return preferences

    async def store_project_context(
        self, project_name: str, context: Dict[str, Any]
    ) -> str:
        """Store project-specific context"""
        content = {"project_name": project_name, "context": context}

        return await self.store_memory(
            content=content,
            context={"project": project_name},
            tags=["project", project_name],
            importance=0.7,
            memory_type="project",
        )

    async def get_project_context(self, project_name: str) -> Dict[str, Any]:
        """Get project-specific context"""
        memories = await self.recall_memories(
            query_text=project_name, limit=50, memory_type="project"
        )

        project_context = {}
        for memory in memories:
            if memory.content.get("project_name") == project_name:
                project_context.update(memory.content.get("context", {}))

        return project_context

    async def store_learning(
        self,
        learning_content: Dict[str, Any],
        learning_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store learning from user interactions"""
        return await self.store_memory(
            content=learning_content,
            context=learning_context or {},
            tags=["learning"],
            importance=0.9,
            memory_type="learning",
        )

    async def consolidate_memories(self):
        """
        Consolidate and optimize memory storage

        This process:
        - Removes low-importance, old memories
        - Merges similar memories
        - Updates importance scores based on access patterns
        """
        try:
            cursor = self.ensure_connection().cursor()

            # Remove very old, low-importance memories
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute(
                """
                DELETE FROM memories
                WHERE importance < 0.3 AND created_at < ? AND access_count < 2
            """,
                (cutoff_date,),
            )

            # Update importance based on access patterns
            cursor.execute("""
                UPDATE memories
                SET importance = MIN(1.0, importance + (access_count * 0.1))
                WHERE access_count > 5
            """)

            self.ensure_connection().commit()

            print("🧠 Memory consolidation completed")

        except Exception as e:
            print(f"❌ Memory consolidation failed: {e}")

    async def _update_memory_access(self, memory_id: str):
        """Update memory access statistics"""
        self.ensure_connection()  # Ensure the connection is open
        try:
            cursor = self.ensure_connection().cursor()

            cursor.execute(
                """
                UPDATE memories
                SET last_accessed = ?, access_count = access_count + 1
                WHERE id = ?
                """,
                (datetime.now().isoformat(), memory_id),
            )

            self.ensure_connection().commit()

            # TODO: Trigger webhook for memory update
            # self.webhook_manager.trigger_webhook(
            #     "memory_update",
            #     {"memory_id": memory_id, "timestamp": datetime.now().isoformat()},
            # )

            print("🧠 Memory access updated")

        except Exception as e:
            print(f"❌ Memory access update failed: {e}")

    def _generate_memory_id(
        self, content: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a unique memory ID based on content and context"""
        content_str = json.dumps(content, sort_keys=True)
        context_str = json.dumps(context or {}, sort_keys=True)
        combined = f"{content_str}:{context_str}:{datetime.now().isoformat()}"
        return hashlib.md5(combined.encode()).hexdigest()

    async def search_memories(self, query: MemoryQuery) -> List[Memory]:
        """Advanced memory search with multiple criteria"""
        with self.db_session():
            try:
                cursor = self.ensure_connection().cursor()

                sql = """
                    SELECT id, content, context, tags, importance, created_at, last_accessed, access_count, memory_type
                    FROM memories
                    WHERE importance >= ?
                """
                params: List[Any] = [query.importance_threshold]

                if query.memory_type:
                    sql += " AND memory_type = ?"
                    params.append(str(query.memory_type))  # Cast to str explicitly

                if query.text:
                    sql += " AND (content LIKE ? OR tags LIKE ?)"

                    params.extend(
                        [f"%{query.text}%", f"%{query.text}%"]
                    )  # Cast to str explicitly

                if query.tags:
                    for tag in query.tags:
                        sql += " AND tags LIKE ?"
                        params.append(f"%{tag}%")  # Cast to str explicitly

                if query.time_range:
                    start_time, end_time = query.time_range
                    sql += " AND created_at BETWEEN ? AND ?"
                    params.extend(
                        [start_time.isoformat(), end_time.isoformat()]
                    )  # Cast to str explicitly

                if self.conn is None:
                    self.ensure_connection()  # Ensure connection is initialized

                # Validate and cast query parameters
                if query.memory_type:
                    sql += " AND memory_type = ?"
                    params.append(str(query.memory_type))  # Cast to str explicitly

                if query.text:
                    sql += " AND (content LIKE ? OR tags LIKE ?)"
                    params.extend(
                        [f"%{query.text}%", f"%{query.text}%"]
                    )  # Cast to str explicitly

                if query.tags:
                    for tag in query.tags:
                        sql += " AND tags LIKE ?"
                        params.append(f"%{tag}%")  # Cast to str explicitly

                if query.time_range:
                    start_time, end_time = query.time_range
                    sql += " AND created_at BETWEEN ? AND ?"
                    params.extend(
                        [start_time.isoformat(), end_time.isoformat()]
                    )  # Cast to str explicitly

                sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
                params.append(query.limit)

                cursor.execute(sql, params)
                rows = cursor.fetchall()

                memories = []
                for row in rows:
                    memory = Memory(
                        id=row[0],
                        content=json.loads(row[1]),
                        context=json.loads(row[2]) if row[2] else {},
                        tags=json.loads(row[3]) if row[3] else [],
                        importance=row[4],
                        created_at=datetime.fromisoformat(row[5]),
                        last_accessed=datetime.fromisoformat(row[6]),
                        access_count=row[7],
                        memory_type=row[8],
                    )
                    memories.append(memory)

                return memories

            except Exception as e:
                print(f"❌ Memory search failed: {e}")
                return []

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        try:
            cursor = self.ensure_connection().cursor()

            # Total memories
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]

            # Memories by type
            cursor.execute(
                "SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type"
            )
            by_type = dict(cursor.fetchall())

            # Average importance
            cursor.execute("SELECT AVG(importance) FROM memories")
            avg_importance = cursor.fetchone()[0] or 0

            # Recent activity
            recent_date = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute(
                "SELECT COUNT(*) FROM memories WHERE created_at >= ?", (recent_date,)
            )
            recent_memories = cursor.fetchone()[0]

            return {
                "total_memories": total_memories,
                "memories_by_type": by_type,
                "average_importance": avg_importance,
                "recent_memories": recent_memories,
                "cache_size": len(self.memory_cache),
            }

        except Exception as e:
            print(f"❌ Failed to get memory stats: {e}")
            return {}

    def _prepare_query_params(self, query):
        """Prepare query parameters with correct types."""
        params: List[Any] = []

        if query.memory_type:
            params.append(
                float(query.memory_type)
            )  # Ensure type matches expected float

        if query.text:
            params.extend(
                [float(query.text), float(query.text)]
            )  # Convert text to float if needed

        if query.tags:
            for tag in query.tags:
                params.append(float(tag))  # Convert tags to float

        if query.time_range:
            start_time, end_time = query.time_range
            params.extend(
                [start_time.timestamp(), end_time.timestamp()]
            )  # Use timestamps

        return params

    def export_memory(self, file_path: str):
        """Exports memory data to a file."""
        self.ensure_connection()  # Ensure the connection is open
        try:
            cursor = self.ensure_connection().cursor()
            cursor.execute("SELECT * FROM memories")
            memories = cursor.fetchall()

            with open(file_path, "w") as file:
                json.dump(memories, file)

            print(f"🧠 Memory exported to {file_path}")
        except Exception as e:
            print(f"❌ Memory export failed: {e}")

    def import_memory(self, file_path: str):
        """Imports memory data from a file."""
        self.ensure_connection()  # Ensure the connection is open
        try:
            with open(file_path, "r") as file:
                memories = json.load(file)

            cursor = self.ensure_connection().cursor()
            cursor.executemany(
                """
                INSERT OR REPLACE INTO memories (id, content, last_accessed, access_count)
                VALUES (?, ?, ?, ?)
                """,
                memories,
            )
            self.ensure_connection().commit()
            print(f"🧠 Memory imported from {file_path}")
        except Exception as e:
            print(f"❌ Memory import failed: {e}")

    def close_connection(self):
        """Closes the database connection if open."""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                print("✅ Database connection closed.")
        except Exception as e:
            print(f"❌ Failed to close database connection: {e}")

    @contextmanager
    def db_session(self):
        """Context manager for database session"""
        self.ensure_connection()
        cursor = None
        try:
            if self.conn:
                cursor = self.ensure_connection().cursor()
                yield cursor
            else:
                raise RuntimeError("Database connection is not initialized.")
        except Exception as e:
            print(f"❌ Database operation failed: {e}")
            if self.conn:
                self.conn.rollback()
        finally:
            if cursor:
                cursor.close()

    # Ensure all methods that use the database call close_connection at the end


# Backward compatibility alias
MemoryEngine = LyrixaMemorySystem
