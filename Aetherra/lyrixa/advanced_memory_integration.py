"""
🧠 ADVANCED MEMORY INTEGRATION
=============================

This module provides advanced memory integration for the Aetherra AI OS,
connecting the conversation manager with quantum-enhanced memory systems
and providing sophisticated memory operations.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

try:
    from Aetherra.aetherra_core.memory.quantum_memory_integration import (
        create_quantum_enhanced_memory_engine,
    )

    QUANTUM_MEMORY_AVAILABLE = True
    logger.info("✅ Quantum Enhanced Memory Engine available")
except ImportError as e:
    QUANTUM_MEMORY_AVAILABLE = False
    logger.warning(f"⚠️ Quantum Enhanced Memory Engine not available: {e}")
    create_quantum_enhanced_memory_engine = None

try:
    from Aetherra.lyrixa.memory.lyrixa_memory_engine import LyrixaMemoryEngine

    LYRIXA_MEMORY_AVAILABLE = True
    logger.info("✅ Lyrixa Memory Engine available")
except ImportError as e:
    LYRIXA_MEMORY_AVAILABLE = False
    logger.warning(f"⚠️ Lyrixa Memory Engine not available: {e}")
    LyrixaMemoryEngine = None


class AdvancedMemoryManager:
    """
    🧠 Advanced Memory Manager for Aetherra AI OS

    Integrates multiple memory systems:
    - Quantum-enhanced long-term memory
    - Episodic conversation memory
    - Contextual short-term memory
    - Pattern-based association memory
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Memory engines
        self.quantum_memory = None
        self.episodic_memory = []
        self.context_memory = {}
        self.pattern_memory = {}

        # Memory statistics
        self.memory_stats = {
            "quantum_operations": 0,
            "episodic_entries": 0,
            "context_updates": 0,
            "pattern_discoveries": 0,
            "total_recall_operations": 0,
            "average_recall_time": 0.0,
        }

        # Configuration
        self.max_episodic_entries = self.config.get("max_episodic_entries", 1000)
        self.max_context_entries = self.config.get("max_context_entries", 100)
        self.quantum_threshold = self.config.get("quantum_threshold", 0.7)

        logger.info("🧠 AdvancedMemoryManager initialized")

    async def initialize(self):
        """Initialize memory systems"""
        try:
            # Initialize quantum-enhanced memory if available
            if QUANTUM_MEMORY_AVAILABLE and create_quantum_enhanced_memory_engine:
                self.quantum_memory = create_quantum_enhanced_memory_engine()
                logger.info("✅ Quantum memory engine initialized")
            else:
                logger.warning("⚠️ Quantum memory not available, using fallback")

            return True

        except Exception as e:
            logger.error(f"❌ Memory system initialization failed: {e}")
            return False

    async def store_conversation_memory(
        self,
        message: str,
        response: str,
        user_id: str = "default",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Store conversation exchange in advanced memory systems"""

        try:
            storage_start = time.time()
            context = context or {}

            # Create memory entry
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "message": message,
                "response": response,
                "context": context,
                "memory_type": "conversation",
            }

            # Store in episodic memory
            await self._store_episodic_memory(memory_entry)

            # Store in quantum memory if available and important enough
            quantum_result = None
            if self.quantum_memory and self._should_store_quantum(memory_entry):
                quantum_result = await self._store_quantum_memory(memory_entry)

            # Update context memory
            await self._update_context_memory(user_id, memory_entry)

            # Discover patterns
            patterns = await self._discover_patterns(memory_entry)

            storage_time = time.time() - storage_start

            result = {
                "success": True,
                "storage_time": storage_time,
                "episodic_stored": True,
                "quantum_stored": quantum_result is not None,
                "patterns_discovered": len(patterns),
                "memory_entry_id": memory_entry.get("id"),
                "timestamp": datetime.now().isoformat(),
            }

            self.memory_stats["episodic_entries"] += 1
            if quantum_result:
                self.memory_stats["quantum_operations"] += 1

            logger.info(
                f"💾 Conversation memory stored (quantum: {quantum_result is not None})"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Failed to store conversation memory: {e}")
            return {"success": False, "error": str(e)}

    async def recall_memory(
        self,
        query: str,
        user_id: str = "default",
        strategy: str = "quantum_hybrid",
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Advanced memory recall with multiple strategies"""

        try:
            recall_start = time.time()

            results = {
                "query": query,
                "strategy": strategy,
                "results": [],
                "metadata": {},
            }

            # Quantum-enhanced recall
            if strategy in ["quantum_hybrid", "quantum"] and self.quantum_memory:
                quantum_results = await self._quantum_recall(query, limit)
                results["results"].extend(quantum_results)
                results["metadata"]["quantum_results"] = len(quantum_results)

            # Episodic memory recall
            if strategy in ["quantum_hybrid", "episodic", "contextual"]:
                episodic_results = await self._episodic_recall(query, user_id, limit)
                results["results"].extend(episodic_results)
                results["metadata"]["episodic_results"] = len(episodic_results)

            # Context-aware recall
            if strategy in ["quantum_hybrid", "contextual"]:
                context_results = await self._context_recall(query, user_id, limit)
                results["results"].extend(context_results)
                results["metadata"]["context_results"] = len(context_results)

            # Pattern-based recall
            pattern_results = await self._pattern_recall(query, limit)
            results["results"].extend(pattern_results)
            results["metadata"]["pattern_results"] = len(pattern_results)

            # Remove duplicates and sort by relevance
            results["results"] = self._deduplicate_and_rank(results["results"], limit)

            recall_time = time.time() - recall_start
            results["recall_time"] = recall_time
            results["total_results"] = len(results["results"])

            # Update statistics
            self.memory_stats["total_recall_operations"] += 1
            self.memory_stats["average_recall_time"] = (
                self.memory_stats["average_recall_time"]
                * (self.memory_stats["total_recall_operations"] - 1)
                + recall_time
            ) / self.memory_stats["total_recall_operations"]

            logger.info(
                f"🔍 Memory recall completed: {len(results['results'])} results in {recall_time:.3f}s"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Memory recall failed: {e}")
            return {"query": query, "results": [], "error": str(e)}

    async def _store_episodic_memory(self, memory_entry: Dict[str, Any]):
        """Store in episodic memory buffer"""
        memory_entry["id"] = f"episodic_{len(self.episodic_memory)}_{int(time.time())}"
        self.episodic_memory.append(memory_entry)

        # Maintain buffer size
        if len(self.episodic_memory) > self.max_episodic_entries:
            self.episodic_memory = self.episodic_memory[-self.max_episodic_entries :]

    async def _store_quantum_memory(
        self, memory_entry: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Store important memories in quantum-enhanced system"""
        if not self.quantum_memory:
            return None

        try:
            # Prepare content for quantum storage
            content = f"User: {memory_entry['message']} | Response: {memory_entry['response']}"
            tags = ["conversation", memory_entry.get("user_id", "default")]

            # Add context-based tags
            if memory_entry.get("context", {}).get("importance") == "high":
                tags.append("important")

            result = await self.quantum_memory.remember(
                content=content, tags=tags, category="conversation", confidence=0.8
            )

            return {"success": True, "quantum_id": result.fragment_id}

        except Exception as e:
            logger.error(f"Quantum storage failed: {e}")
            return None

    async def _update_context_memory(self, user_id: str, memory_entry: Dict[str, Any]):
        """Update contextual memory for user"""
        if user_id not in self.context_memory:
            self.context_memory[user_id] = []

        # Add context entry
        context_entry = {
            "timestamp": memory_entry["timestamp"],
            "summary": memory_entry["message"][:100],
            "topics": self._extract_topics(memory_entry),
            "sentiment": self._analyze_sentiment(memory_entry),
        }

        self.context_memory[user_id].append(context_entry)

        # Maintain context buffer
        if len(self.context_memory[user_id]) > self.max_context_entries:
            self.context_memory[user_id] = self.context_memory[user_id][
                -self.max_context_entries :
            ]

        self.memory_stats["context_updates"] += 1

    async def _discover_patterns(
        self, memory_entry: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover patterns in memory entries"""
        patterns = []

        try:
            # Topic patterns
            topics = self._extract_topics(memory_entry)
            for topic in topics:
                if topic not in self.pattern_memory:
                    self.pattern_memory[topic] = {"count": 0, "contexts": []}

                self.pattern_memory[topic]["count"] += 1
                self.pattern_memory[topic]["contexts"].append(
                    {
                        "timestamp": memory_entry["timestamp"],
                        "user_id": memory_entry["user_id"],
                        "context": memory_entry.get("context", {}),
                    }
                )

                # If pattern is emerging, record it
                if self.pattern_memory[topic]["count"] >= 3:
                    patterns.append(
                        {
                            "type": "topic_pattern",
                            "topic": topic,
                            "frequency": self.pattern_memory[topic]["count"],
                            "strength": min(
                                self.pattern_memory[topic]["count"] / 10, 1.0
                            ),
                        }
                    )

            self.memory_stats["pattern_discoveries"] += len(patterns)
            return patterns

        except Exception as e:
            logger.error(f"Pattern discovery failed: {e}")
            return []

    async def _quantum_recall(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Recall using quantum-enhanced memory"""
        if not self.quantum_memory:
            return []

        try:
            results = await self.quantum_memory.recall(
                query=query, recall_strategy="quantum_hybrid", limit=limit
            )

            return [
                {
                    "content": result.get("content", ""),
                    "source": "quantum",
                    "relevance": result.get("relevance_score", 0.0),
                    "quantum_coherence": result.get("quantum_coherence", 0.0),
                    "type": "quantum_memory",
                }
                for result in results
            ]

        except Exception as e:
            logger.error(f"Quantum recall failed: {e}")
            return []

    async def _episodic_recall(
        self, query: str, user_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Recall from episodic memory buffer"""
        query_lower = query.lower()
        results = []

        for entry in reversed(self.episodic_memory[-100:]):  # Search recent entries
            if user_id == "all" or entry.get("user_id") == user_id:
                # Simple relevance scoring
                message_match = self._calculate_text_similarity(
                    query_lower, entry["message"].lower()
                )
                response_match = self._calculate_text_similarity(
                    query_lower, entry["response"].lower()
                )
                relevance = max(message_match, response_match)

                if relevance > 0.3:  # Threshold
                    results.append(
                        {
                            "content": f"Q: {entry['message']} | A: {entry['response']}",
                            "source": "episodic",
                            "relevance": relevance,
                            "timestamp": entry["timestamp"],
                            "type": "conversation_memory",
                        }
                    )

        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]

    async def _context_recall(
        self, query: str, user_id: str, limit: int
    ) -> List[Dict[str, Any]]:
        """Recall using contextual memory"""
        if user_id not in self.context_memory:
            return []

        query_lower = query.lower()
        results = []

        for context_entry in self.context_memory[user_id]:
            # Check topic matches
            topic_match = any(
                topic.lower() in query_lower
                for topic in context_entry.get("topics", [])
            )
            summary_match = self._calculate_text_similarity(
                query_lower, context_entry["summary"].lower()
            )

            if topic_match or summary_match > 0.4:
                relevance = 0.8 if topic_match else summary_match
                results.append(
                    {
                        "content": context_entry["summary"],
                        "source": "context",
                        "relevance": relevance,
                        "timestamp": context_entry["timestamp"],
                        "topics": context_entry.get("topics", []),
                        "type": "context_memory",
                    }
                )

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]

    async def _pattern_recall(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Recall using discovered patterns"""
        query_lower = query.lower()
        results = []

        for topic, pattern_data in self.pattern_memory.items():
            if topic.lower() in query_lower or query_lower in topic.lower():
                results.append(
                    {
                        "content": f"Pattern discovered: '{topic}' mentioned {pattern_data['count']} times",
                        "source": "pattern",
                        "relevance": min(pattern_data["count"] / 10, 1.0),
                        "pattern_strength": min(pattern_data["count"] / 10, 1.0),
                        "frequency": pattern_data["count"],
                        "type": "pattern_memory",
                    }
                )

        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]

    def _should_store_quantum(self, memory_entry: Dict[str, Any]) -> bool:
        """Determine if memory should be stored in quantum system"""
        # Store if high importance or contains certain keywords
        context = memory_entry.get("context", {})
        if context.get("importance") == "high":
            return True

        # Store if message is long (likely important)
        if len(memory_entry["message"]) > 100:
            return True

        # Store if contains quantum-worthy keywords
        quantum_keywords = [
            "remember",
            "important",
            "quantum",
            "aetherra",
            "ai",
            "learning",
        ]
        message_lower = memory_entry["message"].lower()
        if any(keyword in message_lower for keyword in quantum_keywords):
            return True

        return False

    def _extract_topics(self, memory_entry: Dict[str, Any]) -> List[str]:
        """Extract topics from memory entry"""
        text = memory_entry["message"] + " " + memory_entry["response"]
        words = text.lower().split()

        # Simple topic extraction (could be enhanced with NLP)
        topics = []
        topic_keywords = {
            "ai": ["ai", "artificial", "intelligence", "machine", "learning"],
            "quantum": ["quantum", "superposition", "entanglement"],
            "programming": ["code", "programming", "python", "javascript"],
            "memory": ["memory", "remember", "recall", "storage"],
            "aetherra": ["aetherra", "lyrixa", "system", "os"],
        }

        for topic, keywords in topic_keywords.items():
            if any(keyword in words for keyword in keywords):
                topics.append(topic)

        return topics

    def _analyze_sentiment(self, memory_entry: Dict[str, Any]) -> str:
        """Simple sentiment analysis"""
        text = memory_entry["message"].lower()

        positive_words = [
            "good",
            "great",
            "excellent",
            "amazing",
            "love",
            "like",
            "happy",
        ]
        negative_words = [
            "bad",
            "terrible",
            "hate",
            "dislike",
            "sad",
            "angry",
            "frustrated",
        ]

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _deduplicate_and_rank(
        self, results: List[Dict[str, Any]], limit: int
    ) -> List[Dict[str, Any]]:
        """Remove duplicates and rank by relevance"""
        # Simple deduplication by content similarity
        unique_results = []
        seen_content = set()

        # Sort by relevance first
        results.sort(key=lambda x: x.get("relevance", 0.0), reverse=True)

        for result in results:
            content_key = result.get("content", "")[:100]  # Use first 100 chars as key
            if content_key not in seen_content:
                seen_content.add(content_key)
                unique_results.append(result)

                if len(unique_results) >= limit:
                    break

        return unique_results

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        return {
            "memory_stats": self.memory_stats.copy(),
            "system_status": {
                "quantum_memory_available": self.quantum_memory is not None,
                "episodic_entries": len(self.episodic_memory),
                "context_users": len(self.context_memory),
                "discovered_patterns": len(self.pattern_memory),
            },
            "performance_metrics": {
                "average_recall_time": self.memory_stats["average_recall_time"],
                "total_operations": sum(
                    [
                        self.memory_stats["quantum_operations"],
                        self.memory_stats["episodic_entries"],
                        self.memory_stats["context_updates"],
                        self.memory_stats["total_recall_operations"],
                    ]
                ),
            },
            "pattern_analysis": {
                pattern: {
                    "frequency": data["count"],
                    "strength": min(data["count"] / 10, 1.0),
                }
                for pattern, data in self.pattern_memory.items()
            },
        }

    async def cleanup_old_memories(self, days_old: int = 30):
        """Clean up old memories to maintain performance"""
        cutoff_date = datetime.now() - timedelta(days=days_old)

        # Clean episodic memory
        original_count = len(self.episodic_memory)
        self.episodic_memory = [
            entry
            for entry in self.episodic_memory
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_date
        ]

        cleaned_count = original_count - len(self.episodic_memory)
        logger.info(f"🧹 Cleaned {cleaned_count} old episodic memories")

        return {"cleaned_episodic": cleaned_count}


# Convenience function for easy integration
def create_advanced_memory_manager(
    config: Optional[Dict[str, Any]] = None,
) -> AdvancedMemoryManager:
    """Create and initialize an advanced memory manager"""
    return AdvancedMemoryManager(config)


__all__ = ["AdvancedMemoryManager", "create_advanced_memory_manager"]
