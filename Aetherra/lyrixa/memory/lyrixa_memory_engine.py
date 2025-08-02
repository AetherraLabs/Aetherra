"""
🧠 Lyrixa Memory Engine
=======================

Core memory management system for the Aetherra AI OS.
Handles various types of memory storage, retrieval, and organization.
"""

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""

    id: str
    content: Any
    memory_type: str
    timestamp: datetime
    importance: float = 0.5
    tags: List[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class LyrixaMemoryEngine:
    """
    Core memory engine for Lyrixa AI.

    Provides:
    - Multi-type memory storage (episodic, semantic, working)
    - Intelligent retrieval and search
    - Memory consolidation and organization
    - Importance-based memory management
    """

    def __init__(self, max_working_memory: int = 100, max_episodic_memory: int = 10000):
        """
        Initialize the memory engine.

        Args:
            max_working_memory: Maximum working memory entries
            max_episodic_memory: Maximum episodic memory entries
        """
        self.working_memory: List[MemoryEntry] = []
        self.episodic_memory: List[MemoryEntry] = []
        self.semantic_memory: Dict[str, MemoryEntry] = {}
        self.memory_index: Dict[str, List[str]] = {}  # Tag-based index

        self.max_working_memory = max_working_memory
        self.max_episodic_memory = max_episodic_memory

        self.total_memories = 0
        self.last_consolidation = datetime.now()

    def store_memory(
        self,
        content: Any,
        memory_type: str = "episodic",
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Store a new memory entry.

        Args:
            content: Memory content
            memory_type: Type of memory (episodic, semantic, working)
            importance: Importance score (0.0 to 1.0)
            tags: Optional tags for categorization
            metadata: Optional metadata

        Returns:
            Memory ID
        """
        memory_id = str(uuid.uuid4())

        memory_entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )

        # Store in appropriate memory system
        if memory_type == "working":
            self._store_working_memory(memory_entry)
        elif memory_type == "episodic":
            self._store_episodic_memory(memory_entry)
        elif memory_type == "semantic":
            self._store_semantic_memory(memory_entry)

        # Update index
        self._update_memory_index(memory_entry)

        self.total_memories += 1

        # Trigger consolidation if needed
        if self._should_consolidate():
            self._consolidate_memories()

        return memory_id

    def retrieve_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory entry if found
        """
        # Search in all memory systems
        for memory_list in [self.working_memory, self.episodic_memory]:
            for memory in memory_list:
                if memory.id == memory_id:
                    return memory

        if memory_id in self.semantic_memory:
            return self.semantic_memory[memory_id]

        return None

    def search_memories(
        self,
        query: str = "",
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        time_range: Optional[tuple] = None,
        importance_threshold: float = 0.0,
        limit: int = 50,
    ) -> List[MemoryEntry]:
        """
        Search memories based on various criteria.

        Args:
            query: Text query to search in content
            memory_type: Filter by memory type
            tags: Filter by tags
            time_range: Filter by time range (start, end)
            importance_threshold: Minimum importance score
            limit: Maximum results to return

        Returns:
            List of matching memory entries
        """
        candidates = []

        # Collect candidates from relevant memory systems
        if not memory_type or memory_type == "working":
            candidates.extend(self.working_memory)
        if not memory_type or memory_type == "episodic":
            candidates.extend(self.episodic_memory)
        if not memory_type or memory_type == "semantic":
            candidates.extend(self.semantic_memory.values())

        # Filter candidates
        results = []

        for memory in candidates:
            # Check importance threshold
            if memory.importance < importance_threshold:
                continue

            # Check time range
            if time_range:
                start_time, end_time = time_range
                if not (start_time <= memory.timestamp <= end_time):
                    continue

            # Check tags
            if tags and not any(tag in memory.tags for tag in tags):
                continue

            # Check query in content
            if query:
                content_str = str(memory.content).lower()
                if query.lower() not in content_str:
                    continue

            results.append(memory)

        # Sort by relevance (importance + recency)
        results.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)

        return results[:limit]

    def get_recent_memories(
        self, hours: int = 24, limit: int = 20
    ) -> List[MemoryEntry]:
        """
        Get recent memories from specified time period.

        Args:
            hours: Hours back to search
            limit: Maximum memories to return

        Returns:
            List of recent memories
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        return self.search_memories(
            time_range=(cutoff_time, datetime.now()), limit=limit
        )

    def get_important_memories(
        self, threshold: float = 0.7, limit: int = 50
    ) -> List[MemoryEntry]:
        """
        Get high-importance memories.

        Args:
            threshold: Minimum importance threshold
            limit: Maximum memories to return

        Returns:
            List of important memories
        """
        return self.search_memories(importance_threshold=threshold, limit=limit)

    def get_memories_by_tags(
        self, tags: List[str], limit: int = 50
    ) -> List[MemoryEntry]:
        """
        Get memories matching specific tags.

        Args:
            tags: Tags to search for
            limit: Maximum memories to return

        Returns:
            List of tagged memories
        """
        return self.search_memories(tags=tags, limit=limit)

    def update_memory_importance(self, memory_id: str, new_importance: float):
        """
        Update the importance score of a memory.

        Args:
            memory_id: Memory to update
            new_importance: New importance score
        """
        memory = self.retrieve_memory(memory_id)
        if memory:
            memory.importance = max(0.0, min(1.0, new_importance))

    def add_memory_tags(self, memory_id: str, new_tags: List[str]):
        """
        Add tags to an existing memory.

        Args:
            memory_id: Memory to update
            new_tags: Tags to add
        """
        memory = self.retrieve_memory(memory_id)
        if memory:
            memory.tags.extend(tag for tag in new_tags if tag not in memory.tags)
            self._update_memory_index(memory)

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "total_memories": self.total_memories,
            "working_memory_count": len(self.working_memory),
            "episodic_memory_count": len(self.episodic_memory),
            "semantic_memory_count": len(self.semantic_memory),
            "memory_index_size": len(self.memory_index),
            "last_consolidation": self.last_consolidation.isoformat(),
            "capacity_usage": {
                "working_memory": f"{len(self.working_memory)}/{self.max_working_memory}",
                "episodic_memory": f"{len(self.episodic_memory)}/{self.max_episodic_memory}",
            },
        }

    def _store_working_memory(self, memory: MemoryEntry):
        """Store memory in working memory with capacity management."""
        self.working_memory.append(memory)

        # Manage capacity
        if len(self.working_memory) > self.max_working_memory:
            # Remove least important or oldest memories
            self.working_memory.sort(key=lambda m: (m.importance, m.timestamp))
            removed = self.working_memory.pop(0)

            # Promote important working memories to episodic
            if removed.importance > 0.6:
                removed.memory_type = "episodic"
                self._store_episodic_memory(removed)

    def _store_episodic_memory(self, memory: MemoryEntry):
        """Store memory in episodic memory with capacity management."""
        self.episodic_memory.append(memory)

        # Manage capacity
        if len(self.episodic_memory) > self.max_episodic_memory:
            # Remove least important memories
            self.episodic_memory.sort(key=lambda m: m.importance)
            self.episodic_memory.pop(0)

    def _store_semantic_memory(self, memory: MemoryEntry):
        """Store memory in semantic memory (concept-based)."""
        # Use content hash as key for semantic memories
        key = f"sem_{hash(str(memory.content))}"
        self.semantic_memory[key] = memory

    def _update_memory_index(self, memory: MemoryEntry):
        """Update the memory index with tags."""
        for tag in memory.tags:
            if tag not in self.memory_index:
                self.memory_index[tag] = []
            if memory.id not in self.memory_index[tag]:
                self.memory_index[tag].append(memory.id)

    def _should_consolidate(self) -> bool:
        """Check if memory consolidation should be triggered."""
        time_since_consolidation = datetime.now() - self.last_consolidation

        return (
            time_since_consolidation > timedelta(hours=1)
            or len(self.working_memory) > self.max_working_memory * 0.8
        )

    def _consolidate_memories(self):
        """Perform memory consolidation."""
        # This is a simplified consolidation process
        # In a real implementation, this would be more sophisticated

        # Promote important working memories
        promoted = []
        for memory in self.working_memory[:]:
            if memory.importance > 0.7:
                memory.memory_type = "episodic"
                self.episodic_memory.append(memory)
                promoted.append(memory)

        # Remove promoted memories from working memory
        for memory in promoted:
            self.working_memory.remove(memory)

        # Update consolidation timestamp
        self.last_consolidation = datetime.now()

    def clear_memory_type(self, memory_type: str):
        """Clear all memories of a specific type."""
        if memory_type == "working":
            self.working_memory.clear()
        elif memory_type == "episodic":
            self.episodic_memory.clear()
        elif memory_type == "semantic":
            self.semantic_memory.clear()

    def export_memories(self, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Export memories to a serializable format.

        Args:
            memory_type: Type to export, or None for all

        Returns:
            Exported memory data
        """
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "memory_statistics": self.get_memory_statistics(),
        }

        if not memory_type or memory_type == "working":
            export_data["working_memory"] = [
                self._serialize_memory(m) for m in self.working_memory
            ]

        if not memory_type or memory_type == "episodic":
            export_data["episodic_memory"] = [
                self._serialize_memory(m) for m in self.episodic_memory
            ]

        if not memory_type or memory_type == "semantic":
            export_data["semantic_memory"] = {
                k: self._serialize_memory(v) for k, v in self.semantic_memory.items()
            }

        return export_data

    def _serialize_memory(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Serialize a memory entry for export."""
        return {
            "id": memory.id,
            "content": memory.content,
            "memory_type": memory.memory_type,
            "timestamp": memory.timestamp.isoformat(),
            "importance": memory.importance,
            "tags": memory.tags,
            "metadata": memory.metadata,
        }
