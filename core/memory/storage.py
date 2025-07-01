"""
Memory Storage Interface
Abstract storage interface and implementations for the memory system
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .models import DailyReflection, MemoryEntry, MemoryPattern, SessionMemory


class MemoryStorage(ABC):
    """Abstract base class for memory storage implementations"""

    @abstractmethod
    def save_memory(self, memory: MemoryEntry) -> bool:
        """Save a single memory entry"""
        pass

    @abstractmethod
    def load_memories(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Load memory entries"""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        pass

    @abstractmethod
    def search_memories(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content"""
        pass


class FileMemoryStorage(MemoryStorage):
    """File-based memory storage implementation"""

    def __init__(self, storage_file: str = "memory_store.json"):
        self.storage_file = storage_file
        self.memories: List[MemoryEntry] = []
        self.load_from_file()

    def load_from_file(self):
        """Load memories from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        # Legacy format - list of memory dicts
                        self.memories = [self._convert_legacy_memory(m) for m in data]
                    else:
                        # New format - structured data
                        memory_data = data.get("memories", [])
                        self.memories = [MemoryEntry.from_dict(m) for m in memory_data]
            except (json.JSONDecodeError, FileNotFoundError):
                self.memories = []

    def _convert_legacy_memory(self, legacy_memory: Dict[str, Any]) -> MemoryEntry:
        """Convert legacy memory format to new MemoryEntry"""
        return MemoryEntry(
            text=legacy_memory.get("text", ""),
            timestamp=legacy_memory.get("timestamp", str(datetime.now())),
            tags=legacy_memory.get("tags", []),
            category=legacy_memory.get("category", "general"),
        )

    def save_to_file(self):
        """Save memories to file"""
        try:
            data = {
                "version": "1.0",
                "memories": [m.to_dict() for m in self.memories],
                "metadata": {
                    "total_count": len(self.memories),
                    "last_updated": str(datetime.now()),
                },
            }
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except (PermissionError, OSError):
            # Silently handle file permission issues for robustness
            pass

    def save_memory(self, memory: MemoryEntry) -> bool:
        """Save a single memory entry"""
        self.memories.append(memory)
        self.save_to_file()
        return True

    def load_memories(self, limit: Optional[int] = None) -> List[MemoryEntry]:
        """Load memory entries"""
        if limit:
            return self.memories[-limit:]
        return self.memories

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        original_count = len(self.memories)
        self.memories = [m for m in self.memories if m.id != memory_id]
        deleted = len(self.memories) < original_count
        if deleted:
            self.save_to_file()
        return deleted

    def search_memories(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories by content"""
        query_lower = query.lower()
        matches = []

        for memory in self.memories:
            if query_lower in memory.text.lower():
                matches.append(memory)

        return matches[:limit]


class SessionStorage:
    """Storage manager for session-based memories"""

    def __init__(self, base_path: str = "data/memory/sessions"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save_session(self, session: SessionMemory) -> bool:
        """Save a session to file"""
        try:
            session_file = os.path.join(self.base_path, f"{session.session_id}.json")
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, OSError):
            return False

    def load_session(self, session_id: str) -> Optional[SessionMemory]:
        """Load a session by ID"""
        try:
            session_file = os.path.join(self.base_path, f"{session_id}.json")
            if os.path.exists(session_file):
                with open(session_file, encoding="utf-8") as f:
                    data = json.load(f)
                return SessionMemory.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    def list_sessions(self) -> List[str]:
        """List all session IDs"""
        sessions = []
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith(".json"):
                    sessions.append(filename[:-5])  # Remove .json extension
        except OSError:
            pass
        return sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            session_file = os.path.join(self.base_path, f"{session_id}.json")
            if os.path.exists(session_file):
                os.remove(session_file)
                return True
        except OSError:
            pass
        return False


class DailyReflectionStorage:
    """Storage manager for daily reflections"""

    def __init__(self, base_path: str = "data/memory/daily"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save_reflection(self, reflection: DailyReflection) -> bool:
        """Save a daily reflection"""
        try:
            reflection_file = os.path.join(self.base_path, f"{reflection.date}.json")
            with open(reflection_file, "w", encoding="utf-8") as f:
                json.dump(reflection.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, OSError):
            return False

    def load_reflection(self, date: str) -> Optional[DailyReflection]:
        """Load a daily reflection by date"""
        try:
            reflection_file = os.path.join(self.base_path, f"{date}.json")
            if os.path.exists(reflection_file):
                with open(reflection_file, encoding="utf-8") as f:
                    data = json.load(f)
                return DailyReflection.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    def list_reflections(self) -> List[str]:
        """List all reflection dates"""
        dates = []
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith(".json"):
                    dates.append(filename[:-5])  # Remove .json extension
        except OSError:
            pass
        return sorted(dates)


class PatternStorage:
    """Storage manager for memory patterns"""

    def __init__(self, base_path: str = "data/memory/patterns"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save_pattern(self, pattern: MemoryPattern) -> bool:
        """Save a memory pattern"""
        try:
            pattern_file = os.path.join(self.base_path, f"{pattern.pattern_id}.json")
            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(pattern.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except (PermissionError, OSError):
            return False

    def load_pattern(self, pattern_id: str) -> Optional[MemoryPattern]:
        """Load a pattern by ID"""
        try:
            pattern_file = os.path.join(self.base_path, f"{pattern_id}.json")
            if os.path.exists(pattern_file):
                with open(pattern_file, encoding="utf-8") as f:
                    data = json.load(f)
                return MemoryPattern.from_dict(data)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    def list_patterns(self) -> List[MemoryPattern]:
        """List all patterns"""
        patterns = []
        try:
            for filename in os.listdir(self.base_path):
                if filename.endswith(".json"):
                    pattern_id = filename[:-5]  # Remove .json extension
                    pattern = self.load_pattern(pattern_id)
                    if pattern:
                        patterns.append(pattern)
        except OSError:
            pass
        return patterns

    def delete_pattern(self, pattern_id: str) -> bool:
        """Delete a pattern"""
        try:
            pattern_file = os.path.join(self.base_path, f"{pattern_id}.json")
            if os.path.exists(pattern_file):
                os.remove(pattern_file)
                return True
        except OSError:
            pass
        return False
