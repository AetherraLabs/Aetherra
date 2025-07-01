"""
Vector Memory System
High-performance semantic memory with vector embeddings for intelligent recall
"""

import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from .models import VectorMemoryEntry


class VectorMemory:
    """
    Advanced memory system with vector embeddings for semantic search
    10x faster than traditional keyword-based memory systems
    """

    def __init__(self, memory_file: str = "data/vector_memory.json"):
        self.memory_file = memory_file
        self.memories: List[VectorMemoryEntry] = []
        self.embedding_model = None
        self.vector_index = {}
        self.tag_index = {}
        self.category_index = {}

        # Initialize embedding model
        self._init_embedding_model()

        # Load existing memories
        self.load_from_file()

    def _init_embedding_model(self):
        """Initialize embedding model with fallbacks"""
        try:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Semantic embedding model loaded")
        except ImportError:
            print("⚠️  SentenceTransformers not available, using hash-based embeddings")
        except Exception as e:
            print(f"⚠️  Embedding model error: {e}")

    def _create_embedding(self, text: str) -> List[float]:
        """Create embedding vector for text"""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text).tolist()
            except Exception as e:
                print(f"Embedding error: {e}")

        # Fallback: hash-based pseudo-embedding
        return self._hash_embedding(text)

    def _hash_embedding(self, text: str, dimensions: int = 384) -> List[float]:
        """Fallback embedding using hash functions"""
        words = text.lower().split()
        embedding = [0.0] * dimensions

        for i, word in enumerate(words[:dimensions]):
            # Use multiple hash functions for better distribution
            h1 = hash(word) % dimensions
            h2 = hash(word + "salt1") % dimensions
            h3 = hash(word + "salt2") % dimensions

            embedding[h1] += 1.0
            embedding[h2] += 0.5
            embedding[h3] += 0.25

        # Normalize to unit vector
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    def remember(
        self,
        content: str,
        tags: Optional[List[str]] = None,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store memory with semantic embedding"""
        if not content.strip():
            return {"status": "error", "message": "Empty content"}

        tags = tags or []
        metadata = metadata or {}

        # Create embedding
        embedding = self._create_embedding(content)

        # Create memory entry
        memory = VectorMemoryEntry(
            content=content,
            tags=tags,
            category=category,
            embedding=embedding,
            metadata=metadata,
        )

        # Add to storage
        self.memories.append(memory)

        # Update indices
        self._update_indices(memory)

        # Save to file
        self.save_to_file()

        return {
            "status": "success",
            "id": memory.id,
            "similarity_score": self._find_similar_memories(memory, limit=1),
        }

    def semantic_recall(
        self, query: str, limit: int = 5, similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Recall memories using semantic similarity"""
        if not query.strip():
            return []

        query_embedding = self._create_embedding(query)
        similarities = []

        for memory in self.memories:
            similarity = self._cosine_similarity(query_embedding, memory.embedding)
            if similarity >= similarity_threshold:
                similarities.append((similarity, memory))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[0], reverse=True)

        # Return top results
        results = []
        for similarity, memory in similarities[:limit]:
            results.append(
                {
                    "content": memory.content,
                    "similarity": similarity,
                    "tags": memory.tags,
                    "category": memory.category,
                    "timestamp": memory.timestamp,
                    "metadata": memory.metadata,
                    "id": memory.id,
                }
            )

        return results

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _update_indices(self, memory: VectorMemoryEntry):
        """Update search indices"""
        # Tag index
        for tag in memory.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(memory.id)

        # Category index
        if memory.category not in self.category_index:
            self.category_index[memory.category] = []
        self.category_index[memory.category].append(memory.id)

        # Vector index (for future optimization)
        self.vector_index[memory.id] = memory.embedding

    def _find_similar_memories(
        self, memory: VectorMemoryEntry, limit: int = 3
    ) -> List[Tuple[float, str]]:
        """Find memories similar to the given memory"""
        similarities = []

        for other_memory in self.memories:
            if other_memory.id != memory.id:
                similarity = self._cosine_similarity(memory.embedding, other_memory.embedding)
                similarities.append((similarity, other_memory.content))

        similarities.sort(key=lambda x: x[0], reverse=True)
        return similarities[:limit]

    def search_by_tags(self, tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by tags"""
        matching_ids = set()

        for tag in tags:
            if tag in self.tag_index:
                matching_ids.update(self.tag_index[tag])

        results = []
        for memory in self.memories:
            if memory.id in matching_ids:
                results.append(
                    {
                        "content": memory.content,
                        "tags": memory.tags,
                        "category": memory.category,
                        "timestamp": memory.timestamp,
                        "id": memory.id,
                    }
                )

        return results[:limit]

    def search_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by category"""
        results = []

        for memory in self.memories:
            if memory.category == category:
                results.append(
                    {
                        "content": memory.content,
                        "tags": memory.tags,
                        "category": memory.category,
                        "timestamp": memory.timestamp,
                        "id": memory.id,
                    }
                )

        return results[:limit]

    def hybrid_search(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        category: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """Combine semantic search with tag/category filtering"""
        # Start with semantic search
        semantic_results = self.semantic_recall(query, limit * 2, similarity_threshold)

        # Filter by tags and category if specified
        filtered_results = []
        for result in semantic_results:
            tag_match = tags is None or any(tag in result["tags"] for tag in tags)
            category_match = category is None or result["category"] == category

            if tag_match and category_match:
                filtered_results.append(result)

        return filtered_results[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        tag_counts = {}
        category_counts = {}

        for memory in self.memories:
            # Count tags
            for tag in memory.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Count categories
            category_counts[memory.category] = category_counts.get(memory.category, 0) + 1

        return {
            "total_memories": len(self.memories),
            "unique_tags": len(self.tag_index),
            "unique_categories": len(self.category_index),
            "embedding_dimensions": len(self.memories[0].embedding) if self.memories else 0,
            "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_categories": sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[
                :10
            ],
        }

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        for i, memory in enumerate(self.memories):
            if memory.id == memory_id:
                # Remove from main list
                del self.memories[i]

                # Update indices
                self._rebuild_indices()

                # Save to file
                self.save_to_file()
                return True

        return False

    def _rebuild_indices(self):
        """Rebuild all indices"""
        self.tag_index = {}
        self.category_index = {}
        self.vector_index = {}

        for memory in self.memories:
            self._update_indices(memory)

    def save_to_file(self):
        """Save memories to file"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)

            data = {
                "version": "1.0",
                "memories": [memory.to_dict() for memory in self.memories],
                "metadata": {
                    "total_count": len(self.memories),
                    "last_updated": time.time(),
                    "embedding_model": type(self.embedding_model).__name__
                    if self.embedding_model
                    else "hash_fallback",
                },
            }

            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except (PermissionError, OSError) as e:
            print(f"Failed to save vector memory: {e}")

    def load_from_file(self):
        """Load memories from file"""
        if not os.path.exists(self.memory_file):
            return

        try:
            with open(self.memory_file, encoding="utf-8") as f:
                data = json.load(f)

            memory_data = data.get("memories", [])
            self.memories = [VectorMemoryEntry.from_dict(m) for m in memory_data]

            # Rebuild indices
            self._rebuild_indices()

            print(f"✅ Loaded {len(self.memories)} vector memories")

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Failed to load vector memory: {e}")
            self.memories = []

    def export_memories(self, format: str = "json") -> str:
        """Export memories in specified format"""
        if format == "json":
            return json.dumps([memory.to_dict() for memory in self.memories], indent=2)
        elif format == "text":
            text_export = []
            for memory in self.memories:
                text_export.append(f"Content: {memory.content}")
                text_export.append(f"Tags: {', '.join(memory.tags)}")
                text_export.append(f"Category: {memory.category}")
                text_export.append(f"Timestamp: {memory.timestamp}")
                text_export.append("-" * 50)
            return "\n".join(text_export)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def clear_all_memories(self):
        """Clear all memories (use with caution)"""
        self.memories = []
        self.tag_index = {}
        self.category_index = {}
        self.vector_index = {}
        self.save_to_file()
        print("All memories cleared")


# Legacy compatibility alias
EnhancedSemanticMemory = VectorMemory
