#!/usr/bin/env python3
"""
🧠 LYRIXA ADVANCED VECTOR MEMORY SYSTEM - PHASE 1
=================================================

Real vector embeddings with semantic search, confidence modeling,
and reflexive analysis capabilities.
"""

import asyncio
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer

    VECTOR_SUPPORT = True
except ImportError:
    VECTOR_SUPPORT = False
    logging.warning(
        "Vector support not available. Install sentence-transformers and faiss-cpu"
    )


class AdvancedMemorySystem:
    """Enhanced memory system with vector embeddings and semantic search"""

    def __init__(
        self,
        memory_db_path: str = "lyrixa_advanced_memory.db",
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.db_path = memory_db_path
        self.model_name = model_name

        # Vector search setup
        if VECTOR_SUPPORT:
            print("   🤖 Initializing embedding model...")
            self.embedding_model = SentenceTransformer(model_name)  # type: ignore
            print("   ✅ Vector embeddings enabled")
            print("   ✅ Confidence modeling active")
            print("   ✅ Reflexive analysis ready")
            self.embedding_dim = 384  # all-MiniLM-L6-v2 dimension
            self.index = faiss.IndexFlatIP(  # type: ignore
                self.embedding_dim
            )  # Inner product for similarity
        else:
            self.embedding_model = None
            self.index = None
            self.index = None

        # Memory storage
        self.memories = []
        self.memory_metadata = {}
        self.confidence_threshold = 0.7

        # Uncertainty patterns for confidence analysis
        self.uncertainty_patterns = [
            "I'm not sure",
            "unclear",
            "might be",
            "possibly",
            "uncertain",
            "I think",
            "maybe",
            "perhaps",
            "probably",
            "could be",
        ]

        # Initialize database
        self._initialize_database()

        print("🧠 Advanced Vector Memory System initialized")
        if VECTOR_SUPPORT:
            print(f"   📊 Model: {model_name}")
            print(f"   🔢 Embedding dimension: {self.embedding_dim}")
        else:
            print("   [WARN]  Vector support disabled (missing dependencies)")

    def _initialize_database(self):
        """Initialize the advanced memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Advanced memories table with vector support
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS advanced_memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT DEFAULT 'general',
                tags TEXT,
                confidence REAL DEFAULT 1.0,
                importance REAL DEFAULT 0.5,
                embedding_vector TEXT,
                timestamp TEXT,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                context_data TEXT,
                uncertainty_score REAL DEFAULT 0.0,
                reflection_notes TEXT
            )
        """)

        # Memory clusters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_clusters (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                center_vector TEXT,
                member_ids TEXT,
                created_at TEXT,
                last_updated TEXT
            )
        """)

        # Reflection history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reflection_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                reflection_content TEXT,
                memory_count INTEGER,
                confidence_score REAL,
                insights TEXT,
                patterns_found TEXT
            )
        """)

        conn.commit()
        conn.close()

    async def store_memory(
        self,
        content: str,
        memory_type: str = "general",
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store memory with vector embedding and confidence analysis"""

        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        tags = tags or []
        context = context or {}

        # Generate embedding if vector support is available
        embedding_vector = None
        if VECTOR_SUPPORT and self.embedding_model and self.index is not None:
            try:
                embedding = self.embedding_model.encode([content])[0]
                embedding_vector = json.dumps(embedding.tolist())

                # Add to FAISS index
                self.index.add(np.array([embedding]))  # type: ignore

            except Exception as e:
                print(f"Warning: Could not generate embedding: {e}")

        # Analyze uncertainty in content
        uncertainty_score = self._analyze_uncertainty(content)

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO advanced_memories
            (id, content, memory_type, tags, confidence, importance,
             embedding_vector, timestamp, last_accessed, access_count,
             context_data, uncertainty_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                memory_id,
                content,
                memory_type,
                json.dumps(tags),
                confidence,
                self._calculate_importance(content, context),
                embedding_vector,
                timestamp,
                timestamp,
                0,
                json.dumps(context),
                uncertainty_score,
            ),
        )

        conn.commit()
        conn.close()

        # Update in-memory storage
        memory_data = {
            "id": memory_id,
            "content": content,
            "type": memory_type,
            "tags": tags,
            "timestamp": timestamp,
            "confidence": confidence,
            "uncertainty_score": uncertainty_score,
            "context": context,
        }

        self.memories.append(memory_data)
        self.memory_metadata[memory_id] = memory_data

        print(f"💾 Stored memory: {content[:50]}..." if len(content) > 50 else content)

        return memory_id

    async def semantic_search(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Find semantically similar memories using vector embeddings"""

        if not VECTOR_SUPPORT or not self.embedding_model or self.index is None:
            return await self._fallback_search(query, top_k, memory_type)

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])

            # Search FAISS index
            scores, indices = self.index.search(query_embedding, top_k)  # type: ignore

            # Get corresponding memories from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build query with filters
            sql = "SELECT * FROM advanced_memories WHERE confidence >= ?"
            params: List[Any] = [min_confidence]

            if memory_type:
                sql += " AND memory_type = ?"
                params.append(memory_type)

            cursor.execute(sql, params)
            all_memories = cursor.fetchall()
            conn.close()

            # Match indices to memories and create results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(all_memories) and score > 0.3:  # Similarity threshold
                    memory_row = all_memories[idx]
                    memory_dict = {
                        "id": memory_row[0],
                        "content": memory_row[1],
                        "memory_type": memory_row[2],
                        "tags": json.loads(memory_row[3]) if memory_row[3] else [],
                        "confidence": memory_row[4],
                        "importance": memory_row[5],
                        "timestamp": memory_row[7],
                        "context": json.loads(memory_row[10]) if memory_row[10] else {},
                        "uncertainty_score": memory_row[11],
                        "similarity_score": float(score),
                    }
                    results.append(memory_dict)

            return sorted(results, key=lambda x: x["similarity_score"], reverse=True)

        except Exception as e:
            print(f"Error in semantic search: {e}")
            return await self._fallback_search(query, top_k, memory_type)

    async def _fallback_search(
        self, query: str, top_k: int, memory_type: Optional[str]
    ) -> List[Dict]:
        """Fallback text-based search when vector search is unavailable"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        sql = "SELECT * FROM advanced_memories WHERE content LIKE ?"
        params: List[Any] = [f"%{query}%"]

        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)

        sql += " ORDER BY importance DESC, timestamp DESC LIMIT ?"
        params.append(top_k)

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append(
                {
                    "id": row[0],
                    "content": row[1],
                    "memory_type": row[2],
                    "tags": json.loads(row[3]) if row[3] else [],
                    "confidence": row[4],
                    "similarity_score": 0.5,  # Default similarity for text search
                }
            )

        return results

    def _analyze_uncertainty(self, content: str) -> float:
        """Analyze uncertainty level in content"""
        uncertainty_score = 0.0
        content_lower = content.lower()

        # Check for uncertainty patterns
        pattern_count = 0
        for pattern in self.uncertainty_patterns:
            if pattern in content_lower:
                pattern_count += 1
                uncertainty_score += 0.2

        # Factor in question marks (questions might indicate uncertainty)
        question_count = content.count("?")
        uncertainty_score += min(question_count * 0.1, 0.3)

        # Factor in content length (very short responses might indicate uncertainty)
        if len(content.split()) < 5:
            uncertainty_score += 0.1

        return min(uncertainty_score, 1.0)

    def _calculate_importance(self, content: str, context: Dict[str, Any]) -> float:
        """Calculate memory importance score"""
        importance = 0.5  # Base importance

        # Longer content might be more important
        word_count = len(content.split())
        if word_count > 20:
            importance += 0.2
        elif word_count > 50:
            importance += 0.3

        # Context with many keys suggests rich information
        if context and len(context) > 3:
            importance += 0.2

        # Keywords that suggest importance
        important_keywords = [
            "goal",
            "decision",
            "plan",
            "important",
            "remember",
            "critical",
        ]
        for keyword in important_keywords:
            if keyword in content.lower():
                importance += 0.1
                break

        return min(importance, 1.0)

    async def analyze_confidence(
        self, response: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze confidence in a response and determine if clarification is needed"""

        confidence_score = 1.0
        uncertainty_indicators = []

        # Check for uncertainty patterns
        for pattern in self.uncertainty_patterns:
            if pattern.lower() in response.lower():
                confidence_score -= 0.15
                uncertainty_indicators.append(pattern)

        # Factor in response length (very short might indicate uncertainty)
        word_count = len(response.split())
        if word_count < 10:
            confidence_score -= 0.1
            uncertainty_indicators.append("short_response")

        # Factor in context richness
        relevant_memories = context.get("relevant_memories", [])
        if len(relevant_memories) < 2:
            confidence_score -= 0.1
            uncertainty_indicators.append("limited_context")

        # Check for hedging language
        hedging_words = ["seems", "appears", "likely", "probably", "might", "could"]
        hedging_count = sum(1 for word in hedging_words if word in response.lower())
        confidence_score -= min(hedging_count * 0.05, 0.2)

        confidence_score = max(0.0, confidence_score)
        needs_clarification = confidence_score < self.confidence_threshold

        # Generate clarification questions if needed
        clarification_questions = []
        if needs_clarification:
            if "limited_context" in uncertainty_indicators:
                clarification_questions.append(
                    "Could you provide more context about what you're working on?"
                )
            if "short_response" in uncertainty_indicators:
                clarification_questions.append(
                    "Would you like me to elaborate on any specific aspect?"
                )
            if uncertainty_indicators:
                clarification_questions.append(
                    "Is there anything specific you'd like me to clarify?"
                )

        return {
            "confidence_score": confidence_score,
            "needs_clarification": needs_clarification,
            "uncertainty_indicators": uncertainty_indicators,
            "clarification_questions": clarification_questions,
            "hedging_count": hedging_count,
        }

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Basic stats
        cursor.execute("SELECT COUNT(*) FROM advanced_memories")
        total_memories = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(confidence) FROM advanced_memories")
        avg_confidence = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT AVG(uncertainty_score) FROM advanced_memories")
        avg_uncertainty = cursor.fetchone()[0] or 0.0

        # Memory types breakdown
        cursor.execute(
            "SELECT memory_type, COUNT(*) FROM advanced_memories GROUP BY memory_type"
        )
        memory_types = dict(cursor.fetchall())

        # Recent activity
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM advanced_memories WHERE timestamp > ?", (week_ago,)
        )
        recent_memories = cursor.fetchone()[0]

        conn.close()

        return {
            "total_memories": total_memories,
            "average_confidence": round(avg_confidence, 3),
            "average_uncertainty": round(avg_uncertainty, 3),
            "memory_types": memory_types,
            "recent_memories_7days": recent_memories,
            "vector_support_enabled": VECTOR_SUPPORT,
            "confidence_threshold": self.confidence_threshold,
        }


class ReflexiveAnalysisEngine:
    """Self-reflection and improvement suggestions"""

    def __init__(self, memory_system: AdvancedMemorySystem):
        self.memory = memory_system
        self.reflection_history = []

    async def daily_reflection(self) -> Dict[str, Any]:
        """Analyze recent activities and provide insights"""

        # Get recent memories (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT content, memory_type, confidence, uncertainty_score, context_data
            FROM advanced_memories
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        """,
            (yesterday,),
        )

        recent_memories = cursor.fetchall()
        conn.close()

        if not recent_memories:
            return {
                "reflection": "No recent activity to analyze.",
                "insights": [],
                "suggestions": [],
                "confidence": 1.0,
            }

        # Analyze patterns
        memory_types = {}
        total_confidence = 0
        total_uncertainty = 0
        low_confidence_count = 0

        for memory in recent_memories:
            content, mem_type, confidence, uncertainty, context_str = memory

            # Count memory types
            memory_types[mem_type] = memory_types.get(mem_type, 0) + 1

            # Aggregate confidence and uncertainty
            total_confidence += confidence
            total_uncertainty += uncertainty

            if confidence < 0.7:
                low_confidence_count += 1

        avg_confidence = total_confidence / len(recent_memories)
        avg_uncertainty = total_uncertainty / len(recent_memories)

        # Generate insights
        insights = []
        suggestions = []

        # Pattern analysis
        most_common_type = max(memory_types.items(), key=lambda x: x[1])
        insights.append(
            f"Most active area: {most_common_type[0]} ({most_common_type[1]} interactions)"
        )

        # Confidence analysis
        if avg_confidence < 0.6:
            insights.append(f"Average confidence is low ({avg_confidence:.2f})")
            suggestions.append(
                "Consider asking for more context or clarification in conversations"
            )

        if low_confidence_count > len(recent_memories) * 0.3:
            insights.append(f"{low_confidence_count} interactions had low confidence")
            suggestions.append("Improve knowledge base or ask clarifying questions")

        # Uncertainty analysis
        if avg_uncertainty > 0.5:
            insights.append(f"High uncertainty detected ({avg_uncertainty:.2f})")
            suggestions.append("Focus on gathering more definitive information")

        # Activity patterns
        if len(recent_memories) < 5:
            suggestions.append(
                "Consider more active engagement or proactive assistance"
            )
        elif len(recent_memories) > 20:
            insights.append("High activity period - good engagement")

        reflection_data = {
            "timestamp": datetime.now().isoformat(),
            "memory_count": len(recent_memories),
            "average_confidence": round(avg_confidence, 3),
            "average_uncertainty": round(avg_uncertainty, 3),
            "memory_types": memory_types,
            "insights": insights,
            "suggestions": suggestions,
            "low_confidence_count": low_confidence_count,
            "reflection_confidence": min(avg_confidence + 0.2, 1.0),
        }

        # Store reflection in database
        await self._store_reflection(reflection_data)

        self.reflection_history.append(reflection_data)

        return reflection_data

    async def _store_reflection(self, reflection_data: Dict[str, Any]):
        """Store reflection in database"""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        reflection_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO reflection_history
            (id, timestamp, reflection_content, memory_count, confidence_score, insights, patterns_found)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                reflection_id,
                reflection_data["timestamp"],
                json.dumps(reflection_data),
                reflection_data["memory_count"],
                reflection_data["average_confidence"],
                json.dumps(reflection_data["insights"]),
                json.dumps(reflection_data["memory_types"]),
            ),
        )

        conn.commit()
        conn.close()

    async def get_reflection_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent reflection history"""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT reflection_content FROM reflection_history
            ORDER BY timestamp DESC LIMIT ?
        """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [json.loads(row[0]) for row in rows]


# Example usage and testing
async def test_advanced_memory():
    """Test the advanced memory system"""

    print("🧪 Testing Advanced Vector Memory System")
    print("=" * 50)

    # Initialize systems
    memory = AdvancedMemorySystem()
    reflection_engine = ReflexiveAnalysisEngine(memory)

    # Test storing memories
    print("\n1. Storing test memories...")

    memories_to_store = [
        (
            "User prefers Python for scripting tasks",
            "preference",
            ["python", "scripting"],
        ),
        (
            "Working on the Aetherra AI project with vector embeddings",
            "project",
            ["aetherra", "ai", "vectors"],
        ),
        (
            "I'm not sure about the best approach for memory clustering",
            "question",
            ["memory", "clustering"],
        ),
        ("Created a new goal to improve code quality", "goal", ["goals", "code"]),
        (
            "Need help with debugging the memory system",
            "request",
            ["debugging", "memory"],
        ),
    ]

    for content, mem_type, tags in memories_to_store:
        memory_id = await memory.store_memory(content, mem_type, tags)
        print(f"   ✅ Stored: {memory_id[:8]}...")

    # Test semantic search
    print("\n2. Testing semantic search...")
    results = await memory.semantic_search("python programming help", top_k=3)
    print(f"   Found {len(results)} relevant memories:")
    for result in results:
        print(
            f"   📝 {result['content'][:60]}... (similarity: {result.get('similarity_score', 0):.3f})"
        )

    # Test confidence analysis
    print("\n3. Testing confidence analysis...")
    test_responses = [
        "I think this might work, but I'm not entirely sure about the implementation.",
        "The advanced memory system is fully operational and working correctly.",
        "Maybe we should try a different approach?",
        "Based on the analysis, I can confidently recommend using vector embeddings for semantic search.",
    ]

    for response in test_responses:
        confidence_analysis = await memory.analyze_confidence(
            response, {"relevant_memories": []}
        )
        print(
            f"   📊 '{response[:40]}...' - Confidence: {confidence_analysis['confidence_score']:.3f}"
        )
        if confidence_analysis["needs_clarification"]:
            print(
                f"      💭 Needs clarification: {confidence_analysis['clarification_questions'][0]}"
            )

    # Test daily reflection
    print("\n4. Testing daily reflection...")
    reflection = await reflection_engine.daily_reflection()
    print("   🧠 Reflection insights:")
    for insight in reflection["insights"]:
        print(f"      • {insight}")
    if reflection["suggestions"]:
        print("   💡 Suggestions:")
        for suggestion in reflection["suggestions"]:
            print(f"      • {suggestion}")

    # Get memory statistics
    print("\n5. Memory statistics...")
    stats = await memory.get_memory_statistics()
    print(f"   📊 Total memories: {stats['total_memories']}")
    print(f"   📊 Average confidence: {stats['average_confidence']}")
    print(f"   📊 Vector support: {stats['vector_support_enabled']}")
    print(f"   📊 Memory types: {stats['memory_types']}")

    print("\n✅ Advanced Memory System test complete!")
    return memory, reflection_engine


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        asyncio.run(test_advanced_memory())
