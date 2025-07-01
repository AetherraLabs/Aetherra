"""
Memory Models and Data Structures
Core data models for the NeuroCode memory system
"""

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """Basic memory entry with text, tags, and metadata"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    timestamp: str = field(default_factory=lambda: str(datetime.now()))
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "text": self.text,
            "timestamp": self.timestamp,
            "tags": self.tags,
            "category": self.category,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            text=data.get("text", ""),
            timestamp=data.get("timestamp", str(datetime.now())),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class VectorMemoryEntry:
    """Memory entry with vector embedding for semantic search"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    tags: List[str] = field(default_factory=list)
    category: str = "general"
    timestamp: float = field(default_factory=time.time)
    embedding: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "content": self.content,
            "tags": self.tags,
            "category": self.category,
            "timestamp": self.timestamp,
            "embedding": self.embedding,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VectorMemoryEntry":
        """Create from dictionary"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data.get("content", ""),
            tags=data.get("tags", []),
            category=data.get("category", "general"),
            timestamp=data.get("timestamp", time.time()),
            embedding=data.get("embedding", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SessionMemory:
    """Session-specific memory container"""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: str = field(default_factory=lambda: str(datetime.now()))
    end_time: Optional[str] = None
    memories: List[MemoryEntry] = field(default_factory=list)
    session_metadata: Dict[str, Any] = field(default_factory=dict)

    def add_memory(self, memory: MemoryEntry):
        """Add a memory to this session"""
        self.memories.append(memory)

    def close_session(self):
        """Mark session as closed"""
        self.end_time = str(datetime.now())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "memories": [m.to_dict() for m in self.memories],
            "session_metadata": self.session_metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SessionMemory":
        """Create from dictionary"""
        session = cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            start_time=data.get("start_time", str(datetime.now())),
            end_time=data.get("end_time"),
            session_metadata=data.get("session_metadata", {}),
        )

        # Load memories
        for memory_data in data.get("memories", []):
            session.memories.append(MemoryEntry.from_dict(memory_data))

        return session


@dataclass
class DailyReflection:
    """Daily reflection and memory summary"""

    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    total_memories: int = 0
    categories: Dict[str, int] = field(default_factory=dict)
    tags: Dict[str, int] = field(default_factory=dict)
    session_count: int = 0
    insights: List[str] = field(default_factory=list)
    key_memories: List[str] = field(default_factory=list)
    reflection_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "date": self.date,
            "total_memories": self.total_memories,
            "categories": self.categories,
            "tags": self.tags,
            "session_count": self.session_count,
            "insights": self.insights,
            "key_memories": self.key_memories,
            "reflection_summary": self.reflection_summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailyReflection":
        """Create from dictionary"""
        return cls(
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            total_memories=data.get("total_memories", 0),
            categories=data.get("categories", {}),
            tags=data.get("tags", {}),
            session_count=data.get("session_count", 0),
            insights=data.get("insights", []),
            key_memories=data.get("key_memories", []),
            reflection_summary=data.get("reflection_summary", ""),
        )


@dataclass
class MemoryPattern:
    """Detected memory pattern"""

    pattern_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pattern_name: str = ""
    description: str = ""
    frequency: int = 0
    confidence: float = 0.0
    first_seen: str = field(default_factory=lambda: str(datetime.now()))
    last_seen: str = field(default_factory=lambda: str(datetime.now()))
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_name": self.pattern_name,
            "description": self.description,
            "frequency": self.frequency,
            "confidence": self.confidence,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "examples": self.examples,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryPattern":
        """Create from dictionary"""
        return cls(
            pattern_id=data.get("pattern_id", str(uuid.uuid4())),
            pattern_name=data.get("pattern_name", ""),
            description=data.get("description", ""),
            frequency=data.get("frequency", 0),
            confidence=data.get("confidence", 0.0),
            first_seen=data.get("first_seen", str(datetime.now())),
            last_seen=data.get("last_seen", str(datetime.now())),
            examples=data.get("examples", []),
            metadata=data.get("metadata", {}),
        )
