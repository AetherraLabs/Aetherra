"""
🌉 Memory API Bridge
Interface between Aetherra Core and Lyrixa memory access
"""

from typing import Dict, List, Any, Optional
from ..kernel.memory_kernel import MemoryKernel

class MemoryAPI:
    """Clean memory interface for Lyrixa"""
    
    def __init__(self):
        self.kernel = MemoryKernel()
    
    def store(self, content: str, context: Dict = None) -> str:
        """Store memory with context"""
        return self.kernel.store_memory(content, context or {})
    
    def recall(self, query: Dict, limit: int = 10) -> List[Dict]:
        """Recall memories matching query"""
        return self.kernel.recall_memories(query, limit)
    
    def search(self, text: str) -> List[Dict]:
        """Semantic search in memories"""
        return self.kernel.semantic_search(text)
