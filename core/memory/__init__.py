"""
AetherraCode Memory System
Modular memory system with semantic search, pattern analysis, and reflection capabilities
"""

from .basic import BasicMemory
from .models import (
    DailyReflection,
    MemoryEntry,
    MemoryPattern,
    SessionMemory,
    VectorMemoryEntry,
)
from .patterns import PatternAnalyzer
from .reflection import DailyReflectionManager
from .session import SessionManager
from .storage import (
    DailyReflectionStorage,
    FileMemoryStorage,
    MemoryStorage,
    PatternStorage,
    SessionStorage,
)
from .vector import VectorMemory

# Backward compatibility alias
AetherraMemory = BasicMemory

__all__ = [
    # Core models
    "MemoryEntry",
    "VectorMemoryEntry",
    "SessionMemory",
    "DailyReflection",
    "MemoryPattern",
    # Storage interfaces
    "MemoryStorage",
    "FileMemoryStorage",
    "SessionStorage",
    "DailyReflectionStorage",
    "PatternStorage",
    # Memory systems
    "BasicMemory",
    "VectorMemory",
    "SessionManager",
    "DailyReflectionManager",
    "PatternAnalyzer",
    # Backward compatibility
    "AetherraMemory",
]

# Version info
__version__ = "1.0.0"
__author__ = "AetherraCode Project"
__description__ = "Modular memory system for the AetherraCode programming language"


def create_memory_system(memory_type: str = "basic", **kwargs):
    """
    Factory function to create memory systems

    Args:
        memory_type: Type of memory system ('basic', 'vector', 'session')
        **kwargs: Additional arguments for the memory system

    Returns:
        Configured memory system instance
    """
    if memory_type == "basic":
        return BasicMemory(**kwargs)
    elif memory_type == "vector":
        return VectorMemory(**kwargs)
    elif memory_type == "session":
        return SessionManager(**kwargs)
    elif memory_type == "reflection":
        return DailyReflectionManager(**kwargs)
    elif memory_type == "patterns":
        return PatternAnalyzer(**kwargs)
    else:
        raise ValueError(f"Unknown memory type: {memory_type}")


def get_unified_memory_interface():
    """
    Get a unified interface that combines all memory capabilities

    Returns:
        UnifiedMemoryInterface instance
    """
    return UnifiedMemoryInterface()


class UnifiedMemoryInterface:
    """
    Unified interface that combines all memory system capabilities
    Provides a single entry point for all memory operations
    """

    def __init__(self):
        self.basic_memory = BasicMemory()
        self.vector_memory = VectorMemory()
        self.session_manager = SessionManager()
        self.reflection_manager = DailyReflectionManager()
        self.pattern_analyzer = PatternAnalyzer()

    # Basic memory operations
    def remember(self, text: str, tags=None, category: str = "general"):
        """Store a memory using the basic memory system"""
        return self.basic_memory.remember(text, tags, category)

    def recall(self, tags=None, category=None, limit=None, time_filter=None):
        """Recall memories using the basic memory system"""
        return self.basic_memory.recall(tags, category, limit, time_filter)

    # Semantic search operations
    def semantic_remember(
        self, content: str, tags=None, category: str = "general", metadata=None
    ):
        """Store a memory with semantic embedding"""
        return self.vector_memory.remember(content, tags, category, metadata)

    def semantic_recall(
        self, query: str, limit: int = 5, similarity_threshold: float = 0.3
    ):
        """Recall memories using semantic similarity"""
        return self.vector_memory.semantic_recall(query, limit, similarity_threshold)

    def hybrid_search(self, query: str, tags=None, category=None, limit: int = 5):
        """Combined semantic and metadata search"""
        return self.vector_memory.hybrid_search(query, tags, category, limit)

    # Session management
    def start_session(self, metadata=None):
        """Start a new memory session"""
        return self.session_manager.start_session(metadata)

    def end_session(self, session_id=None):
        """End a memory session"""
        return self.session_manager.end_session(session_id)

    def get_session_memories(self, session_id: str):
        """Get memories from a specific session"""
        return self.session_manager.get_session_memories(session_id)

    # Daily reflection
    def generate_daily_reflection(self, date=None):
        """Generate a daily reflection"""
        return self.reflection_manager.generate_daily_reflection(date)

    def get_reflection(self, date: str):
        """Get a daily reflection"""
        return self.reflection_manager.get_reflection(date)

    def get_weekly_summary(self, start_date=None):
        """Get a weekly summary of reflections"""
        return self.reflection_manager.generate_weekly_summary(start_date)

    # Pattern analysis
    def detect_patterns(self, timeframe_days: int = 30):
        """Run comprehensive pattern analysis"""
        return self.pattern_analyzer.run_full_analysis(timeframe_days)

    def get_memory_stats(self):
        """Get comprehensive memory statistics"""
        basic_stats = self.basic_memory.get_memory_stats()
        vector_stats = self.vector_memory.get_statistics()

        return {
            "basic_memory": basic_stats,
            "vector_memory": vector_stats,
            "recent_sessions": len(self.session_manager.get_recent_sessions()),
            "pattern_analysis": "Available",
        }

    # Advanced operations
    def search(self, query: str, use_semantic: bool = True, **kwargs):
        """
        Universal search across all memory systems

        Args:
            query: Search query
            use_semantic: Whether to use semantic search
            **kwargs: Additional search parameters
        """
        results = {"basic_results": self.basic_memory.search(query), "query": query}

        if use_semantic:
            results["semantic_results"] = self.vector_memory.semantic_recall(
                query,
                limit=kwargs.get("limit", 5),
                similarity_threshold=kwargs.get("similarity_threshold", 0.3),
            )

        return results

    def get_comprehensive_summary(self):
        """Get a comprehensive summary of all memory systems"""
        return {
            "basic_memory_summary": self.basic_memory.get_memory_summary(),
            "vector_memory_stats": self.vector_memory.get_statistics(),
            "recent_sessions": [
                self.session_manager.get_session_statistics(s.session_id)
                for s in self.session_manager.get_recent_sessions(5)
            ],
            "recent_reflections": [
                r.to_dict() for r in self.reflection_manager.get_recent_reflections(7)
            ],
            "system_info": {
                "version": __version__,
                "capabilities": [
                    "Basic Memory Storage",
                    "Semantic Vector Search",
                    "Session Management",
                    "Daily Reflection",
                    "Pattern Analysis",
                ],
            },
        }
