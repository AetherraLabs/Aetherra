#!/usr/bin/env python3
"""
Reasoning Memory Layer
======================

Links past failures and successes to new decisions/goals. Provides retrieval of similar past cases and outcomes for reasoning.
Uses Aetherra backend NLP capabilities for advanced text understanding.
"""

import datetime
import os
import sys
from typing import Any, Dict, List

import numpy as np

# Add Aetherra backend to path
aetherra_path = os.path.join(os.path.dirname(__file__), "..", "src")
if aetherra_path not in sys.path:
    sys.path.insert(0, aetherra_path)

# Import Aetherra's advanced NLP capabilities
try:
    from aetherra.core.ai.local_ai import LocalAIEngine
    from aetherra.core.memory.vector import VectorMemorySystem

    AETHERRA_NLP_AVAILABLE = True
    print("[ReasoningMemory] ✅ Aetherra NLP capabilities loaded")
except ImportError as e:
    print(f"[ReasoningMemory] ⚠️  Aetherra NLP not available: {e}")
    AETHERRA_NLP_AVAILABLE = False

# Simple in-memory memory store (stub)
memory_store: List[Dict[str, Any]] = []

# Global instances for NLP
_vector_memory = None
_local_ai = None


def get_aetherra_vector_memory():
    """Get or initialize Aetherra vector memory system"""
    global _vector_memory
    if _vector_memory is None and AETHERRA_NLP_AVAILABLE:
        try:
            _vector_memory = VectorMemorySystem()
            print("[ReasoningMemory] ✅ Aetherra Vector Memory initialized")
        except Exception as e:
            print(f"[ReasoningMemory] ❌ Failed to initialize Vector Memory: {e}")
    return _vector_memory


def get_aetherra_local_ai():
    """Get or initialize Aetherra local AI engine"""
    global _local_ai
    if _local_ai is None and AETHERRA_NLP_AVAILABLE:
        try:
            _local_ai = LocalAIEngine()
            print("[ReasoningMemory] ✅ Aetherra Local AI initialized")
        except Exception as e:
            print(f"[ReasoningMemory] ❌ Failed to initialize Local AI: {e}")
    return _local_ai


# Dummy embedding function (replace with real model in production)
def embed(text: str) -> np.ndarray:
    """Generate embeddings using Aetherra's advanced NLP or fallback to simple hash"""
    # Try to use Aetherra's Local AI embedding model
    local_ai = get_aetherra_local_ai()
    if local_ai and hasattr(local_ai, "embedding_model") and local_ai.embedding_model:
        try:
            # Use Aetherra's embedding model
            embedding = local_ai.embedding_model.encode(text)
            return np.array(embedding)
        except Exception as e:
            print(f"[ReasoningMemory] Embedding error: {e}")

    # Try Aetherra's vector memory system
    vector_memory = get_aetherra_vector_memory()
    if vector_memory:
        try:
            # Use Aetherra's vector memory embedding
            embedding = vector_memory._create_embedding(text)
            return np.array(embedding)
        except Exception as e:
            print(f"[ReasoningMemory] Vector memory embedding error: {e}")

    # Fallback to hash-based pseudo-embedding (original implementation)
    print("[ReasoningMemory] Using fallback hash-based embeddings")
    return np.array(
        [hash(text) % 1000 / 1000.0 for _ in range(384)]
    )  # Match Aetherra's dimension


def reasoning_context_for_goal(goal: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Find related past events for a goal using vector similarity.
    Returns related memory entries and adds related_to links.
    Enhanced with Aetherra NLP capabilities when available.
    """
    # First try the enhanced version with Aetherra NLP
    if AETHERRA_NLP_AVAILABLE:
        try:
            return enhanced_reasoning_context_for_goal(goal, top_k)
        except Exception as e:
            print(f"[ReasoningMemory] Enhanced reasoning failed: {e}")

    # Fallback to original implementation with improved embeddings
    goal_vec = embed(goal)
    similarities = []
    for entry in memory_store:
        entry_vec = embed(entry.get("goal", ""))
        # Prevent division by zero
        goal_norm = np.linalg.norm(goal_vec)
        entry_norm = np.linalg.norm(entry_vec)
        if goal_norm == 0 or entry_norm == 0:
            sim = 0.0
        else:
            sim = float(np.dot(goal_vec, entry_vec) / (goal_norm * entry_norm))
        similarities.append((sim, entry))

    similarities.sort(reverse=True, key=lambda x: x[0])
    # Use lower threshold for semantic embeddings (0.3) vs hash embeddings (0.5)
    threshold = 0.3 if AETHERRA_NLP_AVAILABLE else 0.5
    related = [entry for sim, entry in similarities[:top_k] if sim > threshold]

    # Add related_to links
    for entry in related:
        entry.setdefault("related_to", []).append(goal)

    return {
        "goal": goal,
        "related_memories": related,
        "count": len(related),
        "status": "success",
        "nlp_engine": "aetherra_enhanced" if AETHERRA_NLP_AVAILABLE else "fallback",
    }


def enhanced_reasoning_context_for_goal(goal: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Enhanced reasoning context using Aetherra's NLP capabilities.
    Falls back to basic implementation if Aetherra NLP is not available.
    """
    # Try to use Aetherra's vector memory system for enhanced reasoning
    vector_memory = get_aetherra_vector_memory()
    if vector_memory:
        try:
            # Store the goal in Aetherra's memory system for future reference
            vector_memory.store_memory(
                content=goal,
                category="goal",
                metadata={
                    "type": "reasoning_query",
                    "timestamp": datetime.datetime.now().isoformat(),
                },
            )

            # Search for similar memories in Aetherra's system
            similar_memories = vector_memory.search_memories(
                query=goal,
                category="goal",
                limit=top_k,
                min_similarity=0.3,  # Lower threshold for semantic similarity
            )

            # Convert Aetherra format to our expected format
            related = []
            for memory in similar_memories:
                related.append(
                    {
                        "goal": memory.get("content", ""),
                        "metadata": memory.get("metadata", {}),
                        "similarity": memory.get("similarity", 0.0),
                        "related_to": [goal],
                    }
                )

            return {
                "goal": goal,
                "related_memories": related,
                "count": len(related),
                "status": "success",
                "nlp_engine": "aetherra_vector_memory",
            }

        except Exception as e:
            print(f"[ReasoningMemory] Aetherra vector memory error: {e}")

    # Fallback to original implementation with enhanced embeddings
    return reasoning_context_for_goal(goal, top_k)


if __name__ == "__main__":
    # Populate memory store with sample data
    memory_store.append({"goal": "Install plugin X", "result": "failed"})
    memory_store.append({"goal": "Install plugin Y", "result": "failed"})
    memory_store.append({"goal": "Upgrade plugin X", "result": "success"})
    print(reasoning_context_for_goal("Install plugin X"))
