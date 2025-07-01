"""
Session Memory Management
Session-based memory organization and management
"""

import uuid
from typing import List, Optional

from .models import MemoryEntry, SessionMemory
from .storage import SessionStorage


class SessionManager:
    """
    Manages session-based memory organization
    Groups memories into logical sessions for better organization
    """

    def __init__(self, storage: Optional[SessionStorage] = None):
        if storage is None:
            storage = SessionStorage()
        self.storage = storage
        self.current_session: Optional[SessionMemory] = None

    def start_session(self, session_metadata: Optional[dict] = None) -> str:
        """Start a new memory session"""
        session_id = str(uuid.uuid4())

        self.current_session = SessionMemory(
            session_id=session_id, session_metadata=session_metadata or {}
        )

        return session_id

    def add_memory_to_session(self, memory: MemoryEntry, session_id: Optional[str] = None) -> bool:
        """Add a memory to a specific session"""
        if session_id:
            # Add to specific session
            session = self.storage.load_session(session_id)
            if session:
                session.add_memory(memory)
                return self.storage.save_session(session)
        elif self.current_session:
            # Add to current session
            self.current_session.add_memory(memory)
            return True

        return False

    def end_session(self, session_id: Optional[str] = None) -> bool:
        """End a memory session and save it"""
        if session_id:
            # End specific session
            session = self.storage.load_session(session_id)
            if session:
                session.close_session()
                return self.storage.save_session(session)
        elif self.current_session:
            # End current session
            self.current_session.close_session()
            success = self.storage.save_session(self.current_session)
            self.current_session = None
            return success

        return False

    def get_session(self, session_id: str) -> Optional[SessionMemory]:
        """Get a session by ID"""
        return self.storage.load_session(session_id)

    def list_all_sessions(self) -> List[str]:
        """List all session IDs"""
        return self.storage.list_sessions()

    def get_session_memories(self, session_id: str) -> List[MemoryEntry]:
        """Get all memories from a specific session"""
        session = self.storage.load_session(session_id)
        if session:
            return session.memories
        return []

    def search_sessions_by_memory(self, query: str) -> List[SessionMemory]:
        """Search sessions that contain memories matching the query"""
        matching_sessions = []
        query_lower = query.lower()

        for session_id in self.storage.list_sessions():
            session = self.storage.load_session(session_id)
            if session:
                for memory in session.memories:
                    if query_lower in memory.text.lower():
                        matching_sessions.append(session)
                        break  # Found match in this session

        return matching_sessions

    def get_recent_sessions(self, limit: int = 10) -> List[SessionMemory]:
        """Get most recent sessions"""
        sessions = []

        for session_id in self.storage.list_sessions():
            session = self.storage.load_session(session_id)
            if session:
                sessions.append(session)

        # Sort by start time (most recent first)
        sessions.sort(key=lambda s: s.start_time, reverse=True)

        return sessions[:limit]

    def get_session_statistics(self, session_id: str) -> dict:
        """Get statistics for a specific session"""
        session = self.storage.load_session(session_id)
        if not session:
            return {}

        stats = {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "memory_count": len(session.memories),
            "categories": {},
            "tags": {},
            "total_text_length": 0,
        }

        for memory in session.memories:
            # Count categories
            category = memory.category
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

            # Count tags
            for tag in memory.tags:
                stats["tags"][tag] = stats["tags"].get(tag, 0) + 1

            # Total text length
            stats["total_text_length"] += len(memory.text)

        # Calculate average text length
        if session.memories:
            stats["avg_text_length"] = stats["total_text_length"] / len(session.memories)
        else:
            stats["avg_text_length"] = 0

        return stats

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its memories"""
        return self.storage.delete_session(session_id)

    def merge_sessions(
        self, session_ids: List[str], new_session_metadata: Optional[dict] = None
    ) -> Optional[str]:
        """Merge multiple sessions into a new session"""
        if not session_ids:
            return None

        # Create new session
        new_session_id = self.start_session(new_session_metadata)
        if not new_session_id:
            return None

        # Load and merge all memories
        all_memories = []
        for session_id in session_ids:
            session = self.storage.load_session(session_id)
            if session:
                all_memories.extend(session.memories)

        # Sort memories by timestamp
        all_memories.sort(key=lambda m: m.timestamp)

        # Add all memories to new session
        for memory in all_memories:
            self.add_memory_to_session(memory, new_session_id)

        # End the new session
        self.end_session(new_session_id)

        return new_session_id

    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """Export a session in specified format"""
        session = self.storage.load_session(session_id)
        if not session:
            return None

        if format == "json":
            import json

            return json.dumps(session.to_dict(), indent=2)

        elif format == "text":
            lines = [
                f"Session: {session.session_id}",
                f"Start Time: {session.start_time}",
                f"End Time: {session.end_time or 'Active'}",
                f"Memory Count: {len(session.memories)}",
                "=" * 50,
                "",
            ]

            for i, memory in enumerate(session.memories, 1):
                lines.extend(
                    [
                        f"Memory {i}:",
                        f"  Text: {memory.text}",
                        f"  Tags: {', '.join(memory.tags)}",
                        f"  Category: {memory.category}",
                        f"  Timestamp: {memory.timestamp}",
                        "",
                    ]
                )

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_current_session_id(self) -> Optional[str]:
        """Get the ID of the current active session"""
        return self.current_session.session_id if self.current_session else None

    def is_session_active(self) -> bool:
        """Check if there's an active session"""
        return self.current_session is not None
