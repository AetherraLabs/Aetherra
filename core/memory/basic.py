"""
Basic Memory Interface
Simple memory operations for the AetherraCode system
"""

import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import MemoryEntry
from .storage import FileMemoryStorage, MemoryStorage


class BasicMemory:
    """
    Basic memory interface - compatible with original AetherraMemory
    Provides simple memory operations with backward compatibility
    """

    def __init__(self, storage: Optional[MemoryStorage] = None):
        if storage is None:
            storage = FileMemoryStorage()
        self.storage = storage

    @property
    def memory(self) -> List[Dict[str, Any]]:
        """Legacy compatibility: return memories as list of dicts"""
        memories = self.storage.load_memories()
        return [self._memory_to_legacy_dict(m) for m in memories]

    def _memory_to_legacy_dict(self, memory: MemoryEntry) -> Dict[str, Any]:
        """Convert MemoryEntry to legacy dictionary format"""
        return {
            "text": memory.text,
            "timestamp": memory.timestamp,
            "tags": memory.tags,
            "category": memory.category,
        }

    def load(self):
        """Load memories from persistent storage - compatibility method"""
        # Storage loads automatically, but keep this for compatibility
        pass

    def save(self):
        """Save memories to persistent storage - compatibility method"""
        # Storage saves automatically, but keep this for compatibility
        pass

    def remember(self, text: str, tags: Optional[List[str]] = None, category: str = "general"):
        """Store text in memory with optional tags and category"""
        if tags is None:
            tags = ["general"]

        memory = MemoryEntry(text=text, tags=tags, category=category)

        self.storage.save_memory(memory)

    def recall(
        self,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        time_filter: Optional[str] = None,
    ) -> List[str]:
        """Recall memories, optionally filtered by tags, category, or time"""
        memories = self.storage.load_memories()
        filtered_memories = []

        for memory in memories:
            # Check if memory matches tag filter
            tag_match = tags is None or any(tag in memory.tags for tag in tags)
            # Check if memory matches category filter
            category_match = category is None or memory.category == category
            # Check if memory matches time filter
            time_match = time_filter is None or self._matches_time_filter(memory, time_filter)

            if tag_match and category_match and time_match:
                filtered_memories.append(memory)

        # Sort by timestamp (newest first)
        filtered_memories.sort(key=lambda x: x.timestamp, reverse=True)

        # Apply limit if specified
        if limit and len(filtered_memories) > limit:
            filtered_memories = filtered_memories[:limit]

        return [m.text for m in filtered_memories]

    def _matches_time_filter(self, memory: MemoryEntry, time_filter: str) -> bool:
        """Check if a memory matches the time filter criteria"""
        if not time_filter:
            return True

        try:
            memory_time = datetime.fromisoformat(
                memory.timestamp.replace("Z", "+00:00").split("+")[0]
            )
        except (ValueError, AttributeError):
            return False

        now = datetime.now()

        if isinstance(time_filter, dict):
            # Advanced time filter with from/to dates
            from_time = time_filter.get("from")
            to_time = time_filter.get("to")

            if from_time:
                if isinstance(from_time, str):
                    from_time = datetime.fromisoformat(from_time)
                if memory_time < from_time:
                    return False

            if to_time:
                if isinstance(to_time, str):
                    to_time = datetime.fromisoformat(to_time)
                if memory_time > to_time:
                    return False

            return True

        elif isinstance(time_filter, str):
            # String-based time filter
            if time_filter == "today":
                return memory_time.date() == now.date()
            elif time_filter == "yesterday":
                yesterday = now - timedelta(days=1)
                return memory_time.date() == yesterday.date()
            elif time_filter == "this_week":
                week_start = now - timedelta(days=now.weekday())
                return memory_time >= week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_filter == "this_month":
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                return memory_time >= month_start
            elif time_filter.endswith("_hours"):
                hours = int(time_filter.split("_")[0])
                cutoff = now - timedelta(hours=hours)
                return memory_time >= cutoff
            elif time_filter.endswith("_days"):
                days = int(time_filter.split("_")[0])
                cutoff = now - timedelta(days=days)
                return memory_time >= cutoff

        return True

    def temporal_analysis(
        self, timeframe: str = "30_days", granularity: str = "daily"
    ) -> Dict[str, Any]:
        """Analyze memory patterns over time with specified granularity"""
        memories = self.storage.load_memories()
        now = datetime.now()

        if timeframe.endswith("_days"):
            days = int(timeframe.split("_")[0])
            cutoff = now - timedelta(days=days)
        elif timeframe.endswith("_hours"):
            hours = int(timeframe.split("_")[0])
            cutoff = now - timedelta(hours=hours)
        else:
            cutoff = now - timedelta(days=30)  # Default

        # Group memories by time periods
        time_groups = defaultdict(list)

        for memory in memories:
            try:
                memory_time = datetime.fromisoformat(
                    memory.timestamp.replace("Z", "+00:00").split("+")[0]
                )
                if memory_time >= cutoff:
                    # Determine time group key based on granularity
                    if granularity == "hourly":
                        time_key = memory_time.strftime("%Y-%m-%d %H:00")
                    elif granularity == "daily":
                        time_key = memory_time.strftime("%Y-%m-%d")
                    elif granularity == "weekly":
                        # Get start of week
                        week_start = memory_time - timedelta(days=memory_time.weekday())
                        time_key = week_start.strftime("%Y-W%U")
                    elif granularity == "monthly":
                        time_key = memory_time.strftime("%Y-%m")
                    else:
                        time_key = memory_time.strftime("%Y-%m-%d")  # Default to daily

                    time_groups[time_key].append(memory)
            except (ValueError, AttributeError):
                continue

        # Analyze patterns within each time period
        analysis = {
            "timeframe": timeframe,
            "granularity": granularity,
            "total_periods": len(time_groups),
            "periods": {},
        }

        for time_key, period_memories in time_groups.items():
            period_analysis = {
                "memory_count": len(period_memories),
                "categories": defaultdict(int),
                "tags": defaultdict(int),
                "avg_length": sum(len(m.text) for m in period_memories) / len(period_memories)
                if period_memories
                else 0,
            }

            for memory in period_memories:
                period_analysis["categories"][memory.category] += 1
                for tag in memory.tags:
                    period_analysis["tags"][tag] += 1

            analysis["periods"][time_key] = period_analysis

        return analysis

    def search(self, query: str, case_sensitive: bool = False) -> List[str]:
        """Search memories by content"""
        search_flags = 0 if case_sensitive else re.IGNORECASE

        try:
            pattern = re.compile(query, search_flags)
            results = []
            memories = self.storage.load_memories()

            for memory in memories:
                if pattern.search(memory.text):
                    results.append(memory.text)
            return results

        except re.error:
            # If regex compilation fails, treat as literal string
            query_processed = query if case_sensitive else query.lower()
            results = []
            memories = self.storage.load_memories()

            for memory in memories:
                text_to_search = memory.text if case_sensitive else memory.text.lower()
                if query_processed in text_to_search:
                    results.append(memory.text)
            return results

    def get_tags(self) -> List[str]:
        """Get all unique tags from memory"""
        memories = self.storage.load_memories()
        all_tags = set()
        for memory in memories:
            all_tags.update(memory.tags)
        return sorted(all_tags)

    def get_categories(self) -> List[str]:
        """Get all unique categories from memory"""
        memories = self.storage.load_memories()
        categories = set()
        for memory in memories:
            categories.add(memory.category)
        return sorted(categories)

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of memory organization"""
        memories = self.storage.load_memories()
        return {
            "total_memories": len(memories),
            "tags": self.get_tags(),
            "categories": self.get_categories(),
        }

    def patterns(self) -> Dict[str, Any]:
        """Analyze patterns in memory organization"""
        memories = self.storage.load_memories()
        tag_frequency = {}
        category_frequency = {}
        temporal_patterns = []

        for memory in memories:
            # Tag patterns
            for tag in memory.tags:
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1

            # Category patterns
            category_frequency[memory.category] = category_frequency.get(memory.category, 0) + 1

            # Temporal patterns
            temporal_patterns.append(memory.timestamp)

        return {
            "tag_frequency": tag_frequency,
            "category_frequency": category_frequency,
            "temporal_patterns": temporal_patterns,
            "most_frequent_tags": sorted(tag_frequency.items(), key=lambda x: x[1], reverse=True)[
                :5
            ],
            "most_frequent_categories": sorted(
                category_frequency.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }

    def get_memories_by_timeframe(self, hours: int = 24) -> List[str]:
        """Get memories from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []
        memories = self.storage.load_memories()

        for memory in memories:
            try:
                memory_time = datetime.fromisoformat(memory.timestamp.replace("Z", "+00:00"))
                if memory_time >= cutoff_time:
                    recent_memories.append(memory.text)
            except (ValueError, AttributeError):
                # Skip memories with invalid timestamps
                continue

        return recent_memories

    def delete_memories_by_tag(self, tag: str) -> int:
        """Delete memories containing a specific tag"""
        memories = self.storage.load_memories()
        deleted_count = 0

        for memory in memories:
            if tag in memory.tags:
                if self.storage.delete_memory(memory.id):
                    deleted_count += 1

        return deleted_count

    def get_memory_stats(self) -> str:
        """Get detailed statistics about memory usage"""
        memories = self.storage.load_memories()
        if not memories:
            return "No memories stored"

        patterns_data = self.patterns()
        recent_count = len(self.get_memories_by_timeframe(24))

        stats = f"""Memory Statistics:
📊 Total memories: {len(memories)}
🕐 Recent (24h): {recent_count}
🏷️  Unique tags: {len(self.get_tags())}
📂 Categories: {len(self.get_categories())}

Top Tags: {", ".join([f"{tag}({count})" for tag, count in patterns_data["most_frequent_tags"][:3]])}
Top Categories: {", ".join([f"{cat}({count})" for cat, count in patterns_data["most_frequent_categories"][:3]])}"""

        return stats
