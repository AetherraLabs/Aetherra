# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🧠 Enhanced Memory System
=========================
Enhanced memory system for Aetherra plugins.
"""

from typing import Any, Dict, List, Optional


class LyrixaEnhancedMemorySystem:
    """Enhanced memory system with advanced capabilities."""

    def __init__(self, *args, **kwargs):
        """Initialize the enhanced memory system."""
        self.memories = {}
        self.metadata = {}

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """Store a memory with optional metadata."""
        try:
            self.memories[key] = value
            if metadata:
                self.metadata[key] = metadata
            return True
        except Exception:
            return False

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory by key."""
        return self.memories.get(key)

    def search(self, query: str) -> List[Dict]:
        """Search memories by query."""
        results = []
        for key, value in self.memories.items():
            if query.lower() in str(value).lower() or query.lower() in key.lower():
                results.append(
                    {"key": key, "value": value, "metadata": self.metadata.get(key, {})}
                )
        return results

    def get_all_keys(self) -> List[str]:
        """Get all memory keys."""
        return list(self.memories.keys())

    def clear(self) -> bool:
        """Clear all memories."""
        try:
            self.memories.clear()
            self.metadata.clear()
            return True
        except Exception:
            return False
