"""
Aetherra Memory Manager
Advanced memory management system for AI operations and data persistence.
"""

import asyncio
import json
import logging
import pickle
import sqlite3
import threading
import uuid
import zlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage"""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    WORKING = "working"
    CACHE = "cache"
    PERSISTENT = "persistent"


class MemoryPriority(Enum):
    """Memory priority levels"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryEntry:
    """Individual memory entry"""

    entry_id: str
    key: str
    value: Any
    memory_type: MemoryType
    priority: MemoryPriority
    created_at: datetime
    accessed_at: datetime
    access_count: int
    ttl: Optional[timedelta]
    tags: List[str]
    size_bytes: int
    compressed: bool = False


class MemoryIndex:
    """Index for efficient memory retrieval"""

    def __init__(self):
        self.key_index: Dict[str, str] = {}  # key -> entry_id
        self.tag_index: Dict[str, Set[str]] = {}  # tag -> set of entry_ids
        self.type_index: Dict[MemoryType, Set[str]] = {}  # type -> set of entry_ids
        self.access_time_index: List[tuple] = []  # (access_time, entry_id) sorted list

    def add_entry(self, entry: MemoryEntry):
        """Add entry to index"""
        self.key_index[entry.key] = entry.entry_id

        # Add to type index
        if entry.memory_type not in self.type_index:
            self.type_index[entry.memory_type] = set()
        self.type_index[entry.memory_type].add(entry.entry_id)

        # Add to tag index
        for tag in entry.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(entry.entry_id)

        # Add to access time index
        self.access_time_index.append((entry.accessed_at, entry.entry_id))
        self.access_time_index.sort()

    def remove_entry(self, entry: MemoryEntry):
        """Remove entry from index"""
        if entry.key in self.key_index:
            del self.key_index[entry.key]

        # Remove from type index
        if entry.memory_type in self.type_index:
            self.type_index[entry.memory_type].discard(entry.entry_id)

        # Remove from tag index
        for tag in entry.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(entry.entry_id)

        # Remove from access time index
        self.access_time_index = [
            (timestamp, eid)
            for timestamp, eid in self.access_time_index
            if eid != entry.entry_id
        ]

    def find_by_key(self, key: str) -> Optional[str]:
        """Find entry ID by key"""
        return self.key_index.get(key)

    def find_by_tags(self, tags: List[str]) -> Set[str]:
        """Find entry IDs by tags"""
        if not tags:
            return set()

        result = self.tag_index.get(tags[0], set())
        for tag in tags[1:]:
            result = result.intersection(self.tag_index.get(tag, set()))

        return result

    def find_by_type(self, memory_type: MemoryType) -> Set[str]:
        """Find entry IDs by memory type"""
        return self.type_index.get(memory_type, set())

    def get_lru_entries(self, count: int) -> List[str]:
        """Get least recently used entry IDs"""
        return [eid for _, eid in self.access_time_index[:count]]


class CompressionManager:
    """Manages memory compression"""

    @staticmethod
    def compress_data(data: Any) -> bytes:
        """Compress data using zlib"""
        serialized = pickle.dumps(data)
        compressed = zlib.compress(serialized)
        return compressed

    @staticmethod
    def decompress_data(compressed_data: bytes) -> Any:
        """Decompress data"""
        decompressed = zlib.decompress(compressed_data)
        return pickle.loads(decompressed)

    @staticmethod
    def calculate_size(data: Any) -> int:
        """Calculate size of data in bytes"""
        try:
            return len(pickle.dumps(data))
        except Exception:
            return 0

    @staticmethod
    def should_compress(data: Any, threshold: int = 1024) -> bool:
        """Determine if data should be compressed"""
        size = CompressionManager.calculate_size(data)
        return size > threshold


class MemoryEvictionPolicy:
    """Memory eviction policies"""

    @staticmethod
    def lru_eviction(entries: Dict[str, MemoryEntry], target_size: int) -> List[str]:
        """Least Recently Used eviction"""
        sorted_entries = sorted(
            entries.values(), key=lambda e: (e.priority.value, e.accessed_at)
        )

        evict_ids = []
        current_size = sum(e.size_bytes for e in entries.values())

        for entry in sorted_entries:
            if current_size <= target_size:
                break
            evict_ids.append(entry.entry_id)
            current_size -= entry.size_bytes

        return evict_ids

    @staticmethod
    def priority_eviction(
        entries: Dict[str, MemoryEntry], target_size: int
    ) -> List[str]:
        """Priority-based eviction"""
        sorted_entries = sorted(
            entries.values(),
            key=lambda e: (e.priority.value, e.access_count, e.accessed_at),
        )

        evict_ids = []
        current_size = sum(e.size_bytes for e in entries.values())

        for entry in sorted_entries:
            if current_size <= target_size:
                break
            if entry.priority != MemoryPriority.CRITICAL:
                evict_ids.append(entry.entry_id)
                current_size -= entry.size_bytes

        return evict_ids

    @staticmethod
    def ttl_eviction(entries: Dict[str, MemoryEntry]) -> List[str]:
        """Time-to-live eviction"""
        now = datetime.now()
        evict_ids = []

        for entry in entries.values():
            if entry.ttl and (now - entry.created_at) > entry.ttl:
                evict_ids.append(entry.entry_id)

        return evict_ids


class SemanticSearch:
    """Semantic search capabilities for memory"""

    def __init__(self):
        self.embeddings: Dict[str, List[float]] = {}

    def add_embedding(self, entry_id: str, text: str):
        """Add text embedding for semantic search"""
        # Simple word-based embedding (in production, use proper embeddings)
        words = text.lower().split()
        embedding = self._simple_embedding(words)
        self.embeddings[entry_id] = embedding

    def _simple_embedding(self, words: List[str]) -> List[float]:
        """Simple word-based embedding"""
        # Create a simple hash-based embedding
        embedding = [0.0] * 100
        for word in words:
            hash_val = hash(word) % 100
            embedding[hash_val] += 1.0

        # Normalize
        total = sum(embedding)
        if total > 0:
            embedding = [x / total for x in embedding]

        return embedding

    def search_similar(self, query: str, top_k: int = 10) -> List[str]:
        """Search for semantically similar entries"""
        query_embedding = self._simple_embedding(query.lower().split())

        similarities = []
        for entry_id, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((similarity, entry_id))

        # Sort by similarity and return top k
        similarities.sort(reverse=True)
        return [entry_id for _, entry_id in similarities[:top_k]]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity"""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)


class MemoryManager:
    """
    Advanced memory management system for Aetherra AI
    """

    def __init__(self, db_path: str = "memory_manager.db", max_memory_mb: int = 512):
        self.db_path = Path(db_path)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.entries: Dict[str, MemoryEntry] = {}
        self.index = MemoryIndex()
        self.compression_manager = CompressionManager()
        self.semantic_search = SemanticSearch()
        self.eviction_policy = MemoryEvictionPolicy()
        self.access_lock = threading.RLock()
        self.cleanup_active = False
        self.cleanup_task = None
        self._init_database()

    def _init_database(self):
        """Initialize memory database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    entry_id TEXT PRIMARY KEY,
                    key_name TEXT NOT NULL,
                    value_data BLOB NOT NULL,
                    memory_type TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    accessed_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    ttl_seconds INTEGER,
                    tags TEXT,
                    size_bytes INTEGER NOT NULL,
                    compressed BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_key ON memory_entries(key_name)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_entries(memory_type)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_accessed ON memory_entries(accessed_at)
            """)

            conn.commit()
        finally:
            conn.close()

    async def start_cleanup_cycle(self):
        """Start automatic memory cleanup cycle"""
        if self.cleanup_active:
            return

        self.cleanup_active = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Memory cleanup cycle started")

    async def stop_cleanup_cycle(self):
        """Stop automatic memory cleanup cycle"""
        if not self.cleanup_active:
            return

        self.cleanup_active = False

        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Memory cleanup cycle stopped")

    async def _cleanup_loop(self):
        """Memory cleanup loop"""
        try:
            while self.cleanup_active:
                await self._perform_cleanup()
                await asyncio.sleep(60)  # Run every minute

        except asyncio.CancelledError:
            logger.info("Memory cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Memory cleanup error: {e}")

    async def _perform_cleanup(self):
        """Perform memory cleanup operations"""
        with self.access_lock:
            # TTL-based eviction
            ttl_evict_ids = self.eviction_policy.ttl_eviction(self.entries)
            for entry_id in ttl_evict_ids:
                await self._evict_entry(entry_id)

            # Size-based eviction if over memory limit
            current_size = sum(e.size_bytes for e in self.entries.values())
            if current_size > self.max_memory_bytes:
                target_size = int(self.max_memory_bytes * 0.8)  # Target 80% of max
                evict_ids = self.eviction_policy.lru_eviction(self.entries, target_size)

                for entry_id in evict_ids:
                    await self._evict_entry(entry_id)

            logger.debug(
                f"Memory cleanup completed. Current size: {current_size / 1024 / 1024:.1f}MB"
            )

    async def store(
        self,
        key: str,
        value: Any,
        memory_type: MemoryType = MemoryType.WORKING,
        priority: MemoryPriority = MemoryPriority.NORMAL,
        ttl: Optional[timedelta] = None,
        tags: List[str] | None = None,
        enable_search: bool = False,
    ) -> str:
        """Store data in memory"""

        entry_id = str(uuid.uuid4())
        now = datetime.now()
        tags = tags or []

        # Calculate size and compression
        should_compress = self.compression_manager.should_compress(value)
        if should_compress:
            stored_value = self.compression_manager.compress_data(value)
            size_bytes = len(stored_value)
        else:
            stored_value = value
            size_bytes = self.compression_manager.calculate_size(value)

        # Create memory entry
        entry = MemoryEntry(
            entry_id=entry_id,
            key=key,
            value=stored_value,
            memory_type=memory_type,
            priority=priority,
            created_at=now,
            accessed_at=now,
            access_count=1,
            ttl=ttl,
            tags=tags,
            size_bytes=size_bytes,
            compressed=should_compress,
        )

        with self.access_lock:
            # Remove existing entry with same key
            existing_id = self.index.find_by_key(key)
            if existing_id and existing_id in self.entries:
                await self._evict_entry(existing_id)

            # Store new entry
            self.entries[entry_id] = entry
            self.index.add_entry(entry)

            # Add to semantic search if enabled
            if enable_search and isinstance(value, str):
                self.semantic_search.add_embedding(entry_id, value)

        # Persist to database
        await self._persist_entry(entry)

        logger.debug(
            f"Stored {key} in {memory_type.value} memory (compressed: {should_compress})"
        )
        return entry_id

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve data from memory"""
        with self.access_lock:
            entry_id = self.index.find_by_key(key)

            if not entry_id or entry_id not in self.entries:
                # Try loading from database
                entry = await self._load_entry_by_key(key)
                if not entry:
                    return None
                self.entries[entry.entry_id] = entry
                self.index.add_entry(entry)
                entry_id = entry.entry_id

            entry = self.entries[entry_id]

            # Update access information
            entry.accessed_at = datetime.now()
            entry.access_count += 1

            # Decompress if needed
            if entry.compressed:
                return self.compression_manager.decompress_data(entry.value)
            else:
                return entry.value

    async def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Search entries by tags"""
        with self.access_lock:
            entry_ids = self.index.find_by_tags(tags)

            results = []
            for entry_id in entry_ids:
                if entry_id in self.entries:
                    entry = self.entries[entry_id]
                    results.append(
                        {
                            "key": entry.key,
                            "memory_type": entry.memory_type.value,
                            "created_at": entry.created_at.isoformat(),
                            "tags": entry.tags,
                            "access_count": entry.access_count,
                        }
                    )

            return results

    async def semantic_search_memory(
        self, query: str, top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on memory"""
        entry_ids = self.semantic_search.search_similar(query, top_k)

        results = []
        with self.access_lock:
            for entry_id in entry_ids:
                if entry_id in self.entries:
                    entry = self.entries[entry_id]
                    value = entry.value
                    if entry.compressed:
                        value = self.compression_manager.decompress_data(value)

                    results.append(
                        {
                            "key": entry.key,
                            "value": value,
                            "memory_type": entry.memory_type.value,
                            "score": 1.0,  # Placeholder for similarity score
                            "tags": entry.tags,
                        }
                    )

        return results

    async def get_memory_by_type(self, memory_type: MemoryType) -> List[Dict[str, Any]]:
        """Get all entries of specific memory type"""
        with self.access_lock:
            entry_ids = self.index.find_by_type(memory_type)

            results = []
            for entry_id in entry_ids:
                if entry_id in self.entries:
                    entry = self.entries[entry_id]
                    results.append(
                        {
                            "key": entry.key,
                            "size_bytes": entry.size_bytes,
                            "created_at": entry.created_at.isoformat(),
                            "access_count": entry.access_count,
                            "tags": entry.tags,
                        }
                    )

            return results

    async def delete(self, key: str) -> bool:
        """Delete entry from memory"""
        with self.access_lock:
            entry_id = self.index.find_by_key(key)

            if entry_id and entry_id in self.entries:
                await self._evict_entry(entry_id)
                return True

            return False

    async def _evict_entry(self, entry_id: str):
        """Evict entry from memory"""
        if entry_id not in self.entries:
            return

        entry = self.entries[entry_id]

        # Remove from indexes
        self.index.remove_entry(entry)

        # Remove from semantic search
        if entry_id in self.semantic_search.embeddings:
            del self.semantic_search.embeddings[entry_id]

        # Remove from memory
        del self.entries[entry_id]

        # Remove from database
        await self._delete_entry_from_db(entry_id)

        logger.debug(f"Evicted entry {entry.key} from memory")

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        with self.access_lock:
            total_entries = len(self.entries)
            total_size = sum(e.size_bytes for e in self.entries.values())

            type_stats = {}
            for memory_type in MemoryType:
                type_entries = len(self.index.find_by_type(memory_type))
                type_size = sum(
                    e.size_bytes
                    for e in self.entries.values()
                    if e.memory_type == memory_type
                )
                type_stats[memory_type.value] = {
                    "entries": type_entries,
                    "size_mb": type_size / 1024 / 1024,
                }

            return {
                "total_entries": total_entries,
                "total_size_mb": total_size / 1024 / 1024,
                "max_size_mb": self.max_memory_bytes / 1024 / 1024,
                "usage_percent": (total_size / self.max_memory_bytes) * 100,
                "type_breakdown": type_stats,
                "compressed_entries": len(
                    [e for e in self.entries.values() if e.compressed]
                ),
            }

    async def _persist_entry(self, entry: MemoryEntry):
        """Persist entry to database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Serialize value
            if entry.compressed:
                value_data = entry.value
            else:
                value_data = pickle.dumps(entry.value)

            ttl_seconds = int(entry.ttl.total_seconds()) if entry.ttl else None

            conn.execute(
                """
                INSERT OR REPLACE INTO memory_entries
                (entry_id, key_name, value_data, memory_type, priority, created_at,
                 accessed_at, access_count, ttl_seconds, tags, size_bytes, compressed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    entry.entry_id,
                    entry.key,
                    value_data,
                    entry.memory_type.value,
                    entry.priority.value,
                    entry.created_at.isoformat(),
                    entry.accessed_at.isoformat(),
                    entry.access_count,
                    ttl_seconds,
                    json.dumps(entry.tags),
                    entry.size_bytes,
                    entry.compressed,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def _load_entry_by_key(self, key: str) -> Optional[MemoryEntry]:
        """Load entry from database by key"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """
                SELECT * FROM memory_entries WHERE key_name = ?
            """,
                (key,),
            )

            row = cursor.fetchone()
            if not row:
                return None

            # Reconstruct entry
            (
                entry_id,
                key_name,
                value_data,
                memory_type,
                priority,
                created_at,
                accessed_at,
                access_count,
                ttl_seconds,
                tags,
                size_bytes,
                compressed,
            ) = row

            # Deserialize value
            if compressed:
                value = value_data
            else:
                value = pickle.loads(value_data)

            ttl = timedelta(seconds=ttl_seconds) if ttl_seconds else None

            return MemoryEntry(
                entry_id=entry_id,
                key=key_name,
                value=value,
                memory_type=MemoryType(memory_type),
                priority=MemoryPriority(priority),
                created_at=datetime.fromisoformat(created_at),
                accessed_at=datetime.fromisoformat(accessed_at),
                access_count=access_count,
                ttl=ttl,
                tags=json.loads(tags),
                size_bytes=size_bytes,
                compressed=compressed,
            )

        finally:
            conn.close()

    async def _delete_entry_from_db(self, entry_id: str):
        """Delete entry from database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("DELETE FROM memory_entries WHERE entry_id = ?", (entry_id,))
            conn.commit()
        finally:
            conn.close()


# Testing function
async def test_memory_manager():
    """Test the memory manager"""
    manager = MemoryManager(max_memory_mb=1)  # 1MB limit for testing

    # Start cleanup cycle
    await manager.start_cleanup_cycle()

    # Store various types of data
    await manager.store(
        "user_preferences",
        {"theme": "dark", "language": "en"},
        MemoryType.PERSISTENT,
        MemoryPriority.HIGH,
        tags=["user", "settings"],
    )

    await manager.store(
        "temp_calculation",
        [1, 2, 3, 4, 5] * 100,  # Large data to trigger compression
        MemoryType.CACHE,
        MemoryPriority.LOW,
        ttl=timedelta(seconds=30),
    )

    await manager.store(
        "search_text",
        "This is a sample text for semantic search testing",
        MemoryType.WORKING,
        enable_search=True,
        tags=["text", "search"],
    )

    # Retrieve data
    preferences = await manager.retrieve("user_preferences")
    print(f"Retrieved preferences: {preferences}")

    # Search by tags
    search_results = await manager.search_by_tags(["user"])
    print(f"Search by tags: {search_results}")

    # Semantic search
    semantic_results = await manager.semantic_search_memory("sample text")
    print(f"Semantic search: {len(semantic_results)} results")

    # Get memory stats
    stats = manager.get_memory_stats()
    print(f"Memory stats: {stats}")

    # Stop cleanup cycle
    await manager.stop_cleanup_cycle()


if __name__ == "__main__":
    asyncio.run(test_memory_manager())
