"""
📝 Advanced Memory Logger
========================

Enhanced logging system for NeuroCode memory with structured storage,
automatic categorization, and real-time memory insights.
"""

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import MemoryEntry
from .storage import FileMemoryStorage


class MemoryType(Enum):
    """Types of memory entries"""

    GOAL = "goal"
    FACT = "fact"
    EXPERIENCE = "experience"
    LEARNING = "learning"
    DECISION = "decision"
    INSIGHT = "insight"
    ERROR = "error"
    SUCCESS = "success"
    INTERACTION = "interaction"
    CODE_EXECUTION = "code_execution"
    AI_RESPONSE = "ai_response"
    USER_INPUT = "user_input"
    SYSTEM_EVENT = "system_event"


class MemoryImportance(Enum):
    """Importance levels for memories"""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


@dataclass
class EnhancedMemoryEntry(MemoryEntry):
    """Enhanced memory entry with logging features"""

    memory_type: MemoryType = MemoryType.FACT
    importance: MemoryImportance = MemoryImportance.MEDIUM
    source: str = "user"
    context: Dict[str, Any] = field(default_factory=dict)
    related_entries: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with enhanced fields"""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "memory_type": self.memory_type.value,
                "importance": self.importance.value,
                "source": self.source,
                "context": self.context,
                "related_entries": self.related_entries,
                "access_count": self.access_count,
                "last_accessed": self.last_accessed,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancedMemoryEntry":
        """Create from dictionary with enhanced fields"""
        memory_type = MemoryType(data.get("memory_type", "fact"))
        importance = MemoryImportance(data.get("importance", 3))

        entry = cls(
            id=data.get("id") or str(uuid.uuid4()),
            text=data.get("text", ""),
            timestamp=data.get("timestamp") or str(datetime.now()),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            metadata=data.get("metadata", {}),
            memory_type=memory_type,
            importance=importance,
            source=data.get("source", "user"),
            context=data.get("context", {}),
            related_entries=data.get("related_entries", []),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed"),
        )
        return entry


@dataclass
class MemorySession:
    """Represents a memory session with tracking"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    entries: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "entries": self.entries,
            "context": self.context,
        }


class MemoryLogger:
    """Advanced memory logging system"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or os.path.expanduser("~/.aethercode/memory")
        self.storage = FileMemoryStorage(self.storage_path)

        # Create enhanced storage paths
        self.logs_path = Path(self.storage_path) / "logs"
        self.sessions_path = Path(self.storage_path) / "sessions"
        self.analytics_path = Path(self.storage_path) / "analytics"

        # Ensure directories exist
        for path in [self.logs_path, self.sessions_path, self.analytics_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Memory tracking
        self.current_session: Optional[MemorySession] = None
        self.auto_categorize = True
        self.auto_relate = True
        self.log_all_operations = True

        # Memory statistics
        self.stats = {
            "total_entries": 0,
            "entries_by_type": {},
            "entries_by_importance": {},
            "sessions_count": 0,
            "last_cleanup": None,
        }

        self._load_stats()

    def _load_stats(self):
        """Load memory statistics"""
        stats_file = Path(self.analytics_path) / "stats.json"
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    self.stats.update(json.load(f))
            except Exception as e:
                print(f"Warning: Could not load memory stats: {e}")

    def _save_stats(self):
        """Save memory statistics"""
        stats_file = Path(self.analytics_path) / "stats.json"
        try:
            with open(stats_file, "w") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory stats: {e}")

    def start_session(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Start a new memory session"""
        session_id = f"session_{int(time.time())}_{hash(str(datetime.now())) % 10000}"

        self.current_session = MemorySession(
            session_id=session_id, start_time=datetime.now(), context=context or {}
        )

        self.stats["sessions_count"] += 1
        self._save_stats()

        # Log session start
        if self.log_all_operations:
            self._log_operation(
                "session_start", {"session_id": session_id, "context": context}
            )

        return session_id

    def end_session(self) -> Optional[Dict[str, Any]]:
        """End the current memory session"""
        if not self.current_session:
            return None

        self.current_session.end_time = datetime.now()

        # Save session
        session_file = self.sessions_path / f"{self.current_session.session_id}.json"
        try:
            with open(session_file, "w") as f:
                json.dump(self.current_session.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save session: {e}")

        # Log session end
        if self.log_all_operations:
            duration = (
                self.current_session.end_time - self.current_session.start_time
            ).total_seconds()
            self._log_operation(
                "session_end",
                {
                    "session_id": self.current_session.session_id,
                    "duration_seconds": duration,
                    "entries_count": len(self.current_session.entries),
                },
            )

        session_summary = {
            "session_id": self.current_session.session_id,
            "duration": (
                self.current_session.end_time - self.current_session.start_time
            ).total_seconds(),
            "entries_count": len(self.current_session.entries),
        }

        self.current_session = None
        return session_summary

    def log_memory(
        self,
        text: str,
        memory_type: MemoryType = MemoryType.FACT,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        source: str = "user",
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Log a new memory entry"""

        # Auto-categorize if enabled
        if self.auto_categorize and not category:
            category = self._auto_categorize(text, memory_type)

        # Auto-generate tags if not provided
        if not tags:
            tags = self._auto_generate_tags(text, memory_type)

        # Create enhanced memory entry
        entry = EnhancedMemoryEntry(
            text=text,
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            category=category or "general",
            source=source,
            context=context or {},
        )

        # Find related entries if enabled
        if self.auto_relate:
            entry.related_entries = self._find_related_entries(entry)

        # Store the entry
        self.storage.save_memory(entry)

        # Update session if active
        if self.current_session:
            self.current_session.entries.append(entry.id)

        # Update statistics
        self.stats["total_entries"] += 1
        self.stats["entries_by_type"][memory_type.value] = (
            self.stats["entries_by_type"].get(memory_type.value, 0) + 1
        )
        self.stats["entries_by_importance"][importance.value] = (
            self.stats["entries_by_importance"].get(importance.value, 0) + 1
        )
        self._save_stats()

        # Log the operation
        if self.log_all_operations:
            self._log_operation(
                "memory_stored",
                {
                    "entry_id": entry.id,
                    "memory_type": memory_type.value,
                    "importance": importance.value,
                    "category": entry.category,
                    "tags": entry.tags,
                },
            )

        return entry.id

    def log_goal(self, goal_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Log a goal memory"""
        return self.log_memory(
            text=goal_text,
            memory_type=MemoryType.GOAL,
            importance=MemoryImportance.HIGH,
            category="goals",
            context=context,
        )

    def log_learning(
        self, learning_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a learning experience"""
        return self.log_memory(
            text=learning_text,
            memory_type=MemoryType.LEARNING,
            importance=MemoryImportance.MEDIUM,
            category="learning",
            context=context,
        )

    def log_error(
        self, error_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log an error for learning"""
        return self.log_memory(
            text=error_text,
            memory_type=MemoryType.ERROR,
            importance=MemoryImportance.HIGH,
            category="errors",
            context=context,
        )

    def log_success(
        self, success_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log a successful outcome"""
        return self.log_memory(
            text=success_text,
            memory_type=MemoryType.SUCCESS,
            importance=MemoryImportance.MEDIUM,
            category="successes",
            context=context,
        )

    def log_interaction(
        self, interaction_text: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Log user interaction"""
        return self.log_memory(
            text=interaction_text,
            memory_type=MemoryType.INTERACTION,
            importance=MemoryImportance.LOW,
            category="interactions",
            context=context,
        )

    def access_memory(self, entry_id: str) -> Optional[EnhancedMemoryEntry]:
        """Access a memory entry and update access tracking"""
        # Find the entry by ID in loaded memories
        for entry in self.storage.load_memories():
            if entry.id == entry_id and isinstance(entry, EnhancedMemoryEntry):
                entry.access_count += 1
                entry.last_accessed = datetime.now().isoformat()
                # Note: This doesn't update the stored entry in the current storage system
                # Would need to enhance the storage interface for proper updates

                if self.log_all_operations:
                    self._log_operation(
                        "memory_accessed",
                        {"entry_id": entry_id, "access_count": entry.access_count},
                    )

                return entry
        return None

    def search_memories(
        self,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        importance_min: Optional[MemoryImportance] = None,
        limit: int = 10,
    ) -> List[EnhancedMemoryEntry]:
        """Search memories with enhanced filtering"""
        all_entries = self.storage.load_memories()
        results = []

        query_lower = query.lower()

        for entry in all_entries:
            if not isinstance(entry, EnhancedMemoryEntry):
                continue

            # Filter by memory type
            if memory_types and entry.memory_type not in memory_types:
                continue

            # Filter by importance
            if importance_min and entry.importance.value < importance_min.value:
                continue

            # Search in text, tags, and metadata
            if (
                query_lower in entry.text.lower()
                or any(query_lower in tag.lower() for tag in entry.tags)
                or any(query_lower in str(v).lower() for v in entry.metadata.values())
            ):
                results.append(entry)

        # Sort by relevance (importance + access count + recency)
        def relevance_score(entry):
            recency_score = 1.0
            if entry.timestamp:
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    days_old = (datetime.now() - entry_time).days
                    recency_score = max(
                        0.1, 1.0 - (days_old / 365)
                    )  # Decay over a year
                except Exception:
                    pass

            return (
                entry.importance.value * 0.4
                + min(entry.access_count, 10) * 0.3
                + recency_score * 0.3
            )

        results.sort(key=relevance_score, reverse=True)

        if self.log_all_operations:
            self._log_operation(
                "memory_search",
                {
                    "query": query,
                    "results_count": len(results[:limit]),
                    "filters": {
                        "memory_types": [t.value for t in memory_types]
                        if memory_types
                        else None,
                        "importance_min": importance_min.value
                        if importance_min
                        else None,
                    },
                },
            )

        return results[:limit]

    def get_memory_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get insights about memory patterns"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_entries = []

        for entry in self.storage.load_memories():
            if isinstance(entry, EnhancedMemoryEntry) and entry.timestamp:
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    if entry_time >= cutoff_date:
                        recent_entries.append(entry)
                except Exception:
                    continue

        insights = {
            "period_days": days,
            "total_entries": len(recent_entries),
            "memory_types": {},
            "importance_distribution": {},
            "most_accessed": [],
            "frequent_tags": {},
            "categories": {},
        }

        # Analyze memory types
        for entry in recent_entries:
            insights["memory_types"][entry.memory_type.value] = (
                insights["memory_types"].get(entry.memory_type.value, 0) + 1
            )
            insights["importance_distribution"][entry.importance.value] = (
                insights["importance_distribution"].get(entry.importance.value, 0) + 1
            )
            insights["categories"][entry.category] = (
                insights["categories"].get(entry.category, 0) + 1
            )

            for tag in entry.tags:
                insights["frequent_tags"][tag] = (
                    insights["frequent_tags"].get(tag, 0) + 1
                )

        # Most accessed memories
        accessed_entries = [e for e in recent_entries if e.access_count > 0]
        accessed_entries.sort(key=lambda x: x.access_count, reverse=True)
        insights["most_accessed"] = [
            {"id": e.id, "text": e.text[:100], "access_count": e.access_count}
            for e in accessed_entries[:5]
        ]

        return insights

    def cleanup_old_memories(
        self,
        days_threshold: int = 365,
        importance_threshold: MemoryImportance = MemoryImportance.TRIVIAL,
    ):
        """Clean up old, low-importance memories"""
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        removed_count = 0

        for entry in self.storage.load_memories():
            if isinstance(entry, EnhancedMemoryEntry):
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    if (
                        entry_time < cutoff_date
                        and entry.importance.value <= importance_threshold.value
                        and entry.access_count == 0
                    ):
                        self.storage.delete_memory(entry.id)
                        removed_count += 1
                except Exception:
                    continue

        self.stats["last_cleanup"] = datetime.now().isoformat()
        self._save_stats()

        if self.log_all_operations:
            self._log_operation(
                "memory_cleanup",
                {
                    "removed_count": removed_count,
                    "days_threshold": days_threshold,
                    "importance_threshold": importance_threshold.value,
                },
            )

        return removed_count

    def _auto_categorize(self, text: str, memory_type: MemoryType) -> str:
        """Automatically categorize memory based on content"""
        text_lower = text.lower()

        # Keywords for different categories
        categories = {
            "learning": ["learn", "understand", "figure out", "discovered", "realized"],
            "goals": ["goal", "objective", "want to", "need to", "plan to"],
            "errors": ["error", "mistake", "failed", "wrong", "bug"],
            "successes": ["success", "completed", "achieved", "accomplished"],
            "code": ["function", "class", "variable", "code", "program"],
            "ai": ["ai", "artificial intelligence", "model", "llm"],
            "system": ["system", "os", "computer", "hardware", "software"],
        }

        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return memory_type.value

    def _auto_generate_tags(self, text: str, memory_type: MemoryType) -> List[str]:
        """Automatically generate tags based on content"""
        tags = [memory_type.value]
        text_lower = text.lower()

        # Common tag patterns
        tag_patterns = {
            "programming": ["code", "program", "function", "class", "variable"],
            "ai": ["ai", "artificial intelligence", "model", "llm", "neural"],
            "learning": ["learn", "study", "understand", "knowledge"],
            "problem": ["problem", "issue", "challenge", "difficulty"],
            "solution": ["solution", "fix", "resolve", "answer"],
            "important": ["important", "critical", "crucial", "vital"],
            "question": ["question", "ask", "wonder", "curious"],
        }

        for tag, keywords in tag_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                tags.append(tag)

        return list(set(tags))  # Remove duplicates

    def _find_related_entries(self, entry: EnhancedMemoryEntry) -> List[str]:
        """Find related memory entries"""
        related = []
        entry_words = set(entry.text.lower().split())

        for existing_entry in self.storage.load_memories():
            if existing_entry.id == entry.id:
                continue

            existing_words = set(existing_entry.text.lower().split())
            overlap = entry_words.intersection(existing_words)

            # Consider entries related if they share enough words or tags
            if len(overlap) >= 3 or set(entry.tags).intersection(
                set(existing_entry.tags)
            ):
                related.append(existing_entry.id)
                if len(related) >= 5:  # Limit related entries
                    break

        return related

    def _log_operation(self, operation: str, data: Dict[str, Any]):
        """Log memory operations for analytics"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "data": data,
        }

        # Write to daily log file
        log_date = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs_path / f"operations_{log_date}.jsonl"

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Warning: Could not log operation: {e}")

    def export_memories(
        self,
        filepath: str,
        memory_types: Optional[List[MemoryType]] = None,
        date_range: Optional[tuple] = None,
    ):
        """Export memories to file"""
        entries_to_export = []

        for entry in self.storage.load_memories():
            if not isinstance(entry, EnhancedMemoryEntry):
                continue

            # Filter by memory type
            if memory_types and entry.memory_type not in memory_types:
                continue

            # Filter by date range
            if date_range:
                try:
                    entry_time = datetime.fromisoformat(
                        entry.timestamp.replace("Z", "+00:00")
                    )
                    if not (date_range[0] <= entry_time <= date_range[1]):
                        continue
                except Exception:
                    continue

            entries_to_export.append(entry.to_dict())

        with open(filepath, "w") as f:
            json.dump(
                {
                    "export_timestamp": datetime.now().isoformat(),
                    "total_entries": len(entries_to_export),
                    "entries": entries_to_export,
                },
                f,
                indent=2,
            )

        return len(entries_to_export)
