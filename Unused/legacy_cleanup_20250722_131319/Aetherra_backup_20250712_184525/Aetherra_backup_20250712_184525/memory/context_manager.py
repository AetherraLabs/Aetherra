"""
Aetherra Context Manager
Advanced context management and memory operations for maintaining conversational and operational context.
"""

import asyncio
import json
import logging
import threading
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of context that can be managed"""

    CONVERSATIONAL = "conversational"
    OPERATIONAL = "operational"
    PERSISTENT = "persistent"
    TEMPORARY = "temporary"
    SESSION = "session"
    GLOBAL = "global"


class ContextPriority(Enum):
    """Priority levels for context items"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ContextItem:
    """Individual context item with metadata"""

    id: str
    content: Any
    context_type: ContextType
    priority: ContextPriority
    created_at: datetime
    last_accessed: datetime
    expires_at: Optional[datetime] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class ContextManager:
    """
    Advanced context management system for Aetherra
    Handles multiple types of context with persistence, expiration, and smart retrieval
    """

    def __init__(self, storage_path: str = "memory/context_storage"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory context storage
        self.contexts: Dict[str, ContextItem] = {}
        self.context_index: Dict[str, List[str]] = {}  # Tag to context IDs mapping
        self.access_history: List[Tuple[str, datetime]] = []

        # Threading for concurrent access
        self.lock = threading.RLock()

        # Configuration
        self.max_memory_items = 10000
        self.default_ttl = timedelta(hours=24)
        self.cleanup_interval = timedelta(minutes=30)

        # Load existing contexts
        asyncio.create_task(self._load_persistent_contexts())

        # Start cleanup task
        asyncio.create_task(self._periodic_cleanup())

    async def store_context(
        self,
        content: Any,
        context_type: ContextType = ContextType.TEMPORARY,
        priority: ContextPriority = ContextPriority.MEDIUM,
        tags: Optional[List[str]] = None,
        ttl: Optional[timedelta] = None,
        context_id: Optional[str] = None,
    ) -> str:
        """
        Store context with specified parameters

        Args:
            content: The context content to store
            context_type: Type of context
            priority: Priority level
            tags: Associated tags for indexing
            ttl: Time to live (expires after this duration)
            context_id: Optional specific ID (generates one if not provided)

        Returns:
            str: The context ID
        """
        with self.lock:
            if context_id is None:
                context_id = str(uuid.uuid4())

            now = datetime.now()
            expires_at = (
                now + (ttl or self.default_ttl) if ttl != timedelta(0) else None
            )

            context_item = ContextItem(
                id=context_id,
                content=content,
                context_type=context_type,
                priority=priority,
                created_at=now,
                last_accessed=now,
                expires_at=expires_at,
                tags=tags or [],
                metadata={"size": len(str(content))},
            )

            # Store in memory
            self.contexts[context_id] = context_item

            # Update index
            for tag in context_item.tags or []:
                if tag not in self.context_index:
                    self.context_index[tag] = []
                self.context_index[tag].append(context_id)

            # Persist if necessary
            if context_type in [ContextType.PERSISTENT, ContextType.GLOBAL]:
                await self._persist_context(context_item)

            # Enforce memory limits
            await self._enforce_memory_limits()

            logger.debug(f"Stored context {context_id} with type {context_type.value}")
            return context_id

    async def retrieve_context(self, context_id: str) -> Optional[ContextItem]:
        """
        Retrieve context by ID

        Args:
            context_id: The context ID to retrieve

        Returns:
            ContextItem or None if not found/expired
        """
        with self.lock:
            if context_id not in self.contexts:
                # Try loading from persistent storage
                context_item = await self._load_context_from_storage(context_id)
                if context_item:
                    self.contexts[context_id] = context_item
                else:
                    return None
            else:
                context_item = self.contexts[context_id]

            # Check expiration
            if context_item.expires_at and datetime.now() > context_item.expires_at:
                await self.remove_context(context_id)
                return None

            # Update access time
            context_item.last_accessed = datetime.now()
            self.access_history.append((context_id, context_item.last_accessed))

            logger.debug(f"Retrieved context {context_id}")
            return context_item

    async def search_contexts(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        context_type: Optional[ContextType] = None,
        priority: Optional[ContextPriority] = None,
        limit: int = 100,
    ) -> List[ContextItem]:
        """
        Search contexts based on various criteria

        Args:
            query: Text to search in content
            tags: Tags to filter by
            context_type: Type filter
            priority: Priority filter
            limit: Maximum results to return

        Returns:
            List of matching ContextItems
        """
        with self.lock:
            results = []

            for context_item in self.contexts.values():
                # Check expiration
                if context_item.expires_at and datetime.now() > context_item.expires_at:
                    continue

                # Apply filters
                if context_type and context_item.context_type != context_type:
                    continue

                if priority and context_item.priority != priority:
                    continue

                if tags and not any(tag in (context_item.tags or []) for tag in tags):
                    continue

                if query and query.lower() not in str(context_item.content).lower():
                    continue

                results.append(context_item)

            # Sort by priority and recency
            results.sort(
                key=lambda x: (x.priority.value, x.last_accessed), reverse=True
            )

            return results[:limit]

    async def get_related_contexts(
        self, context_id: str, limit: int = 10
    ) -> List[ContextItem]:
        """
        Get contexts related to the given context ID

        Args:
            context_id: Reference context ID
            limit: Maximum results

        Returns:
            List of related ContextItems
        """
        context_item = await self.retrieve_context(context_id)
        if not context_item:
            return []

        # Find contexts with shared tags
        related_ids = set()
        for tag in context_item.tags or []:
            if tag in self.context_index:
                related_ids.update(self.context_index[tag])

        # Remove the original context
        related_ids.discard(context_id)

        # Retrieve and filter related contexts
        related_contexts = []
        for rel_id in related_ids:
            rel_context = await self.retrieve_context(rel_id)
            if rel_context:
                related_contexts.append(rel_context)

        # Sort by relevance (shared tags count and recency)
        def relevance_score(item):
            shared_tags = len(set(item.tags or []) & set(context_item.tags or []))
            recency = (datetime.now() - item.last_accessed).total_seconds()
            return shared_tags * 1000 - recency

        related_contexts.sort(key=relevance_score, reverse=True)
        return related_contexts[:limit]

    async def update_context(
        self,
        context_id: str,
        content: Any = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update existing context

        Args:
            context_id: Context to update
            content: New content (optional)
            tags: New tags (optional)
            metadata: New metadata (optional)

        Returns:
            bool: Success status
        """
        with self.lock:
            context_item = await self.retrieve_context(context_id)
            if not context_item:
                return False

            # Update fields
            if content is not None:
                context_item.content = content
                if context_item.metadata is None:
                    context_item.metadata = {}
                context_item.metadata["size"] = len(str(content))

            if tags is not None:
                # Remove from old tag index
                for old_tag in context_item.tags or []:
                    if old_tag in self.context_index:
                        self.context_index[old_tag].remove(context_id)

                context_item.tags = tags

                # Add to new tag index
                for tag in tags:
                    if tag not in self.context_index:
                        self.context_index[tag] = []
                    self.context_index[tag].append(context_id)

            if metadata is not None:
                if context_item.metadata is None:
                    context_item.metadata = {}
                context_item.metadata.update(metadata)

            context_item.last_accessed = datetime.now()

            # Persist if necessary
            if context_item.context_type in [
                ContextType.PERSISTENT,
                ContextType.GLOBAL,
            ]:
                await self._persist_context(context_item)

            logger.debug(f"Updated context {context_id}")
            return True

    async def remove_context(self, context_id: str) -> bool:
        """
        Remove context from memory and storage

        Args:
            context_id: Context to remove

        Returns:
            bool: Success status
        """
        with self.lock:
            if context_id not in self.contexts:
                return False

            context_item = self.contexts[context_id]

            # Remove from tag index
            for tag in context_item.tags or []:
                if tag in self.context_index:
                    self.context_index[tag].remove(context_id)
                    if not self.context_index[tag]:
                        del self.context_index[tag]

            # Remove from memory
            del self.contexts[context_id]

            # Remove from persistent storage
            storage_file = self.storage_path / f"{context_id}.json"
            if storage_file.exists():
                storage_file.unlink()

            logger.debug(f"Removed context {context_id}")
            return True

    async def get_context_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the context manager

        Returns:
            Dict with various statistics
        """
        with self.lock:
            total_contexts = len(self.contexts)
            type_counts = {}
            priority_counts = {}
            total_size = 0

            for context_item in self.contexts.values():
                # Count by type
                type_name = context_item.context_type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1

                # Count by priority
                priority_name = context_item.priority.value
                priority_counts[priority_name] = (
                    priority_counts.get(priority_name, 0) + 1
                )

                # Total size
                total_size += (context_item.metadata or {}).get("size", 0)

            return {
                "total_contexts": total_contexts,
                "type_distribution": type_counts,
                "priority_distribution": priority_counts,
                "total_size_bytes": total_size,
                "unique_tags": len(self.context_index),
                "memory_utilization": f"{(total_contexts / self.max_memory_items) * 100:.1f}%",
            }

    async def clear_expired_contexts(self) -> int:
        """
        Clear all expired contexts

        Returns:
            int: Number of contexts cleared
        """
        with self.lock:
            now = datetime.now()
            expired_ids = []

            for context_id, context_item in self.contexts.items():
                if context_item.expires_at and now > context_item.expires_at:
                    expired_ids.append(context_id)

            for context_id in expired_ids:
                await self.remove_context(context_id)

            logger.info(f"Cleared {len(expired_ids)} expired contexts")
            return len(expired_ids)

    async def _persist_context(self, context_item: ContextItem):
        """Persist context to storage"""
        try:
            storage_file = self.storage_path / f"{context_item.id}.json"

            # Convert to serializable format
            data = asdict(context_item)
            data["created_at"] = context_item.created_at.isoformat()
            data["last_accessed"] = context_item.last_accessed.isoformat()
            if context_item.expires_at:
                data["expires_at"] = context_item.expires_at.isoformat()
            data["context_type"] = context_item.context_type.value
            data["priority"] = context_item.priority.value

            with open(storage_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to persist context {context_item.id}: {e}")

    async def _load_context_from_storage(
        self, context_id: str
    ) -> Optional[ContextItem]:
        """Load context from persistent storage"""
        try:
            storage_file = self.storage_path / f"{context_id}.json"
            if not storage_file.exists():
                return None

            with open(storage_file, "r") as f:
                data = json.load(f)

            # Convert back to ContextItem
            data["created_at"] = datetime.fromisoformat(data["created_at"])
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
            if data["expires_at"]:
                data["expires_at"] = datetime.fromisoformat(data["expires_at"])
            data["context_type"] = ContextType(data["context_type"])
            data["priority"] = ContextPriority(data["priority"])

            return ContextItem(**data)

        except Exception as e:
            logger.error(f"Failed to load context {context_id}: {e}")
            return None

    async def _load_persistent_contexts(self):
        """Load all persistent contexts at startup"""
        try:
            for storage_file in self.storage_path.glob("*.json"):
                context_id = storage_file.stem
                context_item = await self._load_context_from_storage(context_id)
                if context_item:
                    self.contexts[context_id] = context_item

                    # Update index
                    for tag in context_item.tags or []:
                        if tag not in self.context_index:
                            self.context_index[tag] = []
                        self.context_index[tag].append(context_id)

            logger.info(f"Loaded {len(self.contexts)} persistent contexts")

        except Exception as e:
            logger.error(f"Failed to load persistent contexts: {e}")

    async def _enforce_memory_limits(self):
        """Enforce memory limits by removing least recently used items"""
        if len(self.contexts) <= self.max_memory_items:
            return

        # Get non-persistent contexts sorted by last access
        removable_contexts = [
            (context_id, context_item)
            for context_id, context_item in self.contexts.items()
            if context_item.context_type
            not in [ContextType.PERSISTENT, ContextType.GLOBAL]
        ]

        removable_contexts.sort(key=lambda x: x[1].last_accessed)

        # Remove oldest until within limits
        to_remove = len(self.contexts) - self.max_memory_items
        for i in range(min(to_remove, len(removable_contexts))):
            context_id = removable_contexts[i][0]
            await self.remove_context(context_id)

    async def _periodic_cleanup(self):
        """Periodic cleanup of expired contexts"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                await self.clear_expired_contexts()
            except Exception as e:
                logger.error(f"Cleanup error: {e}")


# Global context manager instance
_context_manager = None


def get_context_manager() -> ContextManager:
    """Get the global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


# Convenience functions
async def store_context(content: Any, **kwargs) -> str:
    """Store context using the global manager"""
    return await get_context_manager().store_context(content, **kwargs)


async def retrieve_context(context_id: str) -> Optional[ContextItem]:
    """Retrieve context using the global manager"""
    return await get_context_manager().retrieve_context(context_id)


async def search_contexts(**kwargs) -> List[ContextItem]:
    """Search contexts using the global manager"""
    return await get_context_manager().search_contexts(**kwargs)
