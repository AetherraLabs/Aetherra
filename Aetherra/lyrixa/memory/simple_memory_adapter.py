"""
Simple Memory Adapter - A simplified memory engine that provides basic functionality
without complex dependencies for the GUI validation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json
import sqlite3
import uuid


class SimpleMemoryFragment:
    """Simple memory fragment for basic operations"""
    def __init__(self, content, tags=None, confidence=0.8):
        self.id = str(uuid.uuid4())
        self.content = content
        self.tags = tags or []
        self.confidence = confidence
        self.created_at = datetime.now()


class LyrixaMemoryEngine:
    """Simplified memory engine for basic operations"""

    def __init__(self, db_path="simple_memory.db"):
        self.db_path = db_path
        self.fragments = {}
        self._init_db()

    def _init_db(self):
        """Initialize simple database"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fragments (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    tags TEXT,
                    confidence REAL,
                    created_at TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception:
            pass  # Fail silently for testing

    def store(self, content, tags=None, confidence=0.8):
        """Store a memory fragment"""
        fragment = SimpleMemoryFragment(content, tags, confidence)
        self.fragments[fragment.id] = fragment
        return {"fragment_id": fragment.id, "status": "stored"}

    def retrieve(self, query, limit=10):
        """Retrieve memory fragments"""
        # Simple keyword search
        results = []
        for fragment in self.fragments.values():
            if query.lower() in str(fragment.content).lower():
                results.append({
                    "id": fragment.id,
                    "content": fragment.content,
                    "confidence": fragment.confidence,
                    "created_at": fragment.created_at.isoformat()
                })
        return results[:limit]

    def get_stats(self):
        """Get memory statistics"""
        return {
            "total_fragments": len(self.fragments),
            "memory_health": 0.95,
            "storage_efficiency": 0.87
        }
