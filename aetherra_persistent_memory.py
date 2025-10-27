#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Persistent Memory System
=================================

A true AI-native persistent memory system that maintains cognitive state
across sessions and enables continuous learning and adaptation.

This system provides:
- Persistent storage of cognitive experiences
- Contextual memory retrieval
- Learning pattern recognition
- Cross-session state maintenance
- Adaptive memory organization
"""

# Standard library imports
import hashlib
import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Aetherra imports
from Aetherra.aetherra_core.memory.quantum.qhash import hamming_distance, simhash_text
from Aetherra.aetherra_core.memory.quantum.random_features import (
    RandomFeatureMap,
    cosine_similarity,
)

logger = logging.getLogger(__name__)

# Simple rate-limited error logger (shared semantic with intelligence layer)
_mem_last_error: dict[str, float] = {}


def _mem_rate_limited(key: str, msg: str, min_interval: float = 10.0):
    now = time.time()
    last = _mem_last_error.get(key, 0)
    if now - last >= min_interval:
        _mem_last_error[key] = now
        logger.error(msg)
    else:
        logger.debug(f"(suppressed repeat) {msg}")


class AetherraMemoryNode:
    """Individual memory node with cognitive metadata."""

    def __init__(
        self,
        content: Any,
        memory_type: str = "general",
        context: dict | None = None,
        importance: float = 0.5,
    ):
        self.id = self._generate_id(content)
        self.content = content
        self.memory_type = memory_type
        self.context = context or {}
        self.importance = importance
        self.created_at = datetime.now()
        self.last_accessed = datetime.now()
        self.access_count = 0
        self.connections = set()  # Connected memory IDs
        self.tags = set()

        # Cognitive metadata
        self.emotional_weight = 0.0
        self.confidence = 1.0
        self.source = "user"
        self.verified = False

    def _generate_id(self, content: Any) -> str:
        """Generate unique ID for memory content."""
        content_str = str(content) + str(time.time())
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def access(self):
        """Mark memory as accessed."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def add_connection(self, memory_id: str):
        """Add connection to another memory."""
        self.connections.add(memory_id)

    def add_tag(self, tag: str):
        """Add descriptive tag."""
        self.tags.add(tag)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "context": self.context,
            "importance": self.importance,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "connections": list(self.connections),
            "tags": list(self.tags),
            "emotional_weight": self.emotional_weight,
            "confidence": self.confidence,
            "source": self.source,
            "verified": self.verified,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AetherraMemoryNode":
        """Create from dictionary."""
        node = cls(
            content=data["content"],
            memory_type=data["memory_type"],
            context=data.get("context", {}),
            importance=data.get("importance", 0.5),
        )
        node.id = data["id"]
        node.created_at = datetime.fromisoformat(data["created_at"])
        node.last_accessed = datetime.fromisoformat(data["last_accessed"])
        node.access_count = data.get("access_count", 0)
        node.connections = set(data.get("connections", []))
        node.tags = set(data.get("tags", []))
        node.emotional_weight = data.get("emotional_weight", 0.0)
        node.confidence = data.get("confidence", 1.0)
        node.source = data.get("source", "user")
        node.verified = data.get("verified", False)
        return node


class AetherraMemoryIndex:
    """Intelligent memory indexing and retrieval system."""

    def __init__(self):
        self.content_index = {}  # content hash -> memory_id
        self.tag_index = {}  # tag -> set of memory_ids
        self.type_index = {}  # memory_type -> set of memory_ids
        self.time_index = {}  # date -> set of memory_ids
        self.importance_index = {}  # importance_level -> set of memory_ids

    def index_memory(self, memory: AetherraMemoryNode):
        """Add memory to indices."""
        # Content index
        content_hash = hashlib.sha256(str(memory.content).encode()).hexdigest()
        self.content_index[content_hash] = memory.id

        # Tag index
        for tag in memory.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = set()
            self.tag_index[tag].add(memory.id)

        # Type index
        if memory.memory_type not in self.type_index:
            self.type_index[memory.memory_type] = set()
        self.type_index[memory.memory_type].add(memory.id)

        # Time index (by date)
        date_key = memory.created_at.date().isoformat()
        if date_key not in self.time_index:
            self.time_index[date_key] = set()
        self.time_index[date_key].add(memory.id)

        # Importance index
        importance_level = int(memory.importance * 10)  # 0-10 scale
        if importance_level not in self.importance_index:
            self.importance_index[importance_level] = set()
        self.importance_index[importance_level].add(memory.id)

    def find_by_tag(self, tag: str) -> set:
        """Find memories by tag."""
        return self.tag_index.get(tag, set())

    def find_by_type(self, memory_type: str) -> set:
        """Find memories by type."""
        return self.type_index.get(memory_type, set())

    def find_by_content_similarity(self, query: str) -> set:
        """Find memories with similar content."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        # Simple similarity - in production would use embedding similarity
        similar_ids = set()
        for content_hash, memory_id in self.content_index.items():
            if any(c in content_hash for c in query_hash[:8]):
                similar_ids.add(memory_id)
        return similar_ids


class AetherraPerśistentMemorySystem:
    """
    Advanced persistent memory system for Aetherra AI OS.

    Provides cognitive-level memory management with:
    - Cross-session persistence
    - Intelligent retrieval
    - Adaptive organization
    - Learning pattern recognition
    """

    def __init__(self, memory_dir: str = "aetherra_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        self.db_path = self.memory_dir / "cognitive_memory.db"
        self.memories = {}  # memory_id -> AetherraMemoryNode
        self.index = AetherraMemoryIndex()
        self.session_id = self._generate_session_id()

        # Cognitive state
        self.learning_patterns = {}
        self.cognitive_state = {
            "session_count": 0,
            "total_memories": 0,
            "last_session": None,
            "cognitive_growth_rate": 0.0,
            "memory_efficiency": 0.0,
        }

        # Initialize database
        self._init_database()

        logger.info("[MEMORY] Aetherra Persistent Memory System initialized")
        logger.info(f"[MEMORY] Session ID: {self.session_id}")

    def _generate_session_id(self) -> str:
        """Generate unique session identifier."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}_{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]}"

    def _init_database(self):
        """Initialize SQLite database for persistent storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    memory_type TEXT,
                    context TEXT,
                    importance REAL,
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER,
                    connections TEXT,
                    tags TEXT,
                    emotional_weight REAL,
                    confidence REAL,
                    source TEXT,
                    verified BOOLEAN,
                    session_id TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    started_at TEXT,
                    ended_at TEXT,
                    memory_count INTEGER,
                    cognitive_events TEXT
                )
            """
            )

            conn.commit()
            conn.close()

            # Load existing memories and state
            self._load_persistent_state()

        except Exception as e:
            _mem_rate_limited("db_init", f"[MEMORY] Database initialization error: {e}")

    async def initialize(self):
        """Initialize the memory system."""
        try:
            # Load existing memories
            await self._load_memories()

            # Ensure core, verified system facts exist (idempotent)
            try:
                await self._ensure_core_facts()
            except Exception as se:
                logger.warning(f"[MEMORY] Skipping core facts seed: {se}")

            # Update cognitive state
            self.cognitive_state["session_count"] += 1
            self.cognitive_state["last_session"] = datetime.now().isoformat()

            # Save session start
            await self._save_session_start()

            logger.info(
                f"[MEMORY] Memory system initialized with {len(self.memories)} memories"
            )
            logger.info(
                f"[MEMORY] Session count: {self.cognitive_state['session_count']}"
            )

            return True

        except Exception as e:
            _mem_rate_limited("init", f"[MEMORY] Initialization error: {e}")
            return False

    async def store(
        self,
        content: Any,
        context: dict | None = None,
        memory_type: str = "general",
        importance: float = 0.5,
        tags: list[str] | None = None,
    ) -> str | None:
        """Store new memory with cognitive metadata."""
        try:
            # Create memory node
            memory = AetherraMemoryNode(
                content=content,
                memory_type=memory_type,
                context=context or {},
                importance=importance,
            )

            # Add tags
            if tags:
                for tag in tags:
                    memory.add_tag(tag)

            # Auto-generate tags based on content
            auto_tags = self._generate_auto_tags(content, context)
            for tag in auto_tags:
                memory.add_tag(tag)

            # Quantum fingerprint (QHash) cached into context for faster recall scoring
            try:
                qhash_bits = int(os.environ.get("AETHERRA_QHASH_BITS", "64"))
                qhash_value = simhash_text(str(content), bits=qhash_bits)
                qctx = dict(memory.context.get("quantum", {}))
                qctx.update(
                    {
                        "qhash": int(qhash_value),
                        "bits": qhash_bits,
                    }
                )
                memory.context["quantum"] = qctx
            except Exception as qe:
                logger.debug(f"[MEMORY] QHash compute skipped: {qe}")

            # Store in memory
            self.memories[memory.id] = memory

            # Update index
            self.index.index_memory(memory)

            # Find and create connections
            await self._create_memory_connections(memory)

            # Save to database
            await self._save_memory_to_db(memory)

            # Update cognitive state
            self.cognitive_state["total_memories"] = len(self.memories)
            await self._update_cognitive_state()

            logger.info(f"[MEMORY] Stored memory: {memory.id} (type: {memory_type})")
            return memory.id

        except Exception as e:
            _mem_rate_limited("store", f"[MEMORY] Storage error: {e}")
            return None

    async def retrieve(
        self, query: str, limit: int = 10, memory_type: str | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve memories based on query with cognitive ranking."""
        try:
            logger.info(f"[MEMORY] Retrieving memories for query: {query}")

            # Find candidate memories
            candidates = set()

            # Search by content similarity
            content_matches = self.index.find_by_content_similarity(query)
            candidates.update(content_matches)

            # Search by tags (query words as potential tags)
            query_words = query.lower().split()
            for word in query_words:
                tag_matches = self.index.find_by_tag(word)
                candidates.update(tag_matches)

            # Filter by type if specified
            if memory_type:
                type_matches = self.index.find_by_type(memory_type)
                candidates = candidates.intersection(type_matches)

            # If no candidates, get recent important memories
            if not candidates:
                candidates = self._get_recent_important_memories(limit)

            # Rank candidates by relevance
            ranked_memories = await self._rank_memories(candidates, query)

            # Limit results
            results = ranked_memories[:limit]

            # Mark memories as accessed
            for memory_data in results:
                memory_id = memory_data["id"]
                if memory_id in self.memories:
                    self.memories[memory_id].access()
                    await self._update_memory_in_db(self.memories[memory_id])

            logger.info(f"[MEMORY] Retrieved {len(results)} memories")
            return results

        except Exception as e:
            _mem_rate_limited("retrieve", f"[MEMORY] Retrieval error: {e}")
            return []

    async def recall_by_tag(self, tag: str, limit: int = 10) -> list[dict[str, Any]]:
        """Recall memories by specific tag."""
        try:
            memory_ids = self.index.find_by_tag(tag)

            results = []
            for memory_id in list(memory_ids)[:limit]:
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    memory.access()
                    results.append(memory.to_dict())
                    await self._update_memory_in_db(memory)

            return results

        except Exception as e:
            logger.error(f"[MEMORY] Tag recall error: {e}")
            return []

    async def get_cognitive_state(self) -> dict[str, Any]:
        """Get current cognitive state and memory statistics."""
        try:
            # Calculate memory efficiency
            total_accesses = sum(m.access_count for m in self.memories.values())
            total_memories = len(self.memories)

            if total_memories > 0:
                self.cognitive_state["memory_efficiency"] = (
                    total_accesses / total_memories
                )

            # Calculate cognitive growth rate
            recent_memories = self._get_recent_memories(hours=24)
            self.cognitive_state["cognitive_growth_rate"] = len(recent_memories)

            state = {
                **self.cognitive_state,
                "active_memories": total_memories,
                "session_id": self.session_id,
                "memory_types": self._get_memory_type_distribution(),
                "recent_activity": self._get_recent_activity_summary(),
                "connection_density": self._calculate_connection_density(),
            }

            return state

        except Exception as e:
            logger.error(f"[MEMORY] Cognitive state error: {e}")
            return {}

    async def optimize_memory(self):
        """Optimize memory storage and connections."""
        try:
            logger.info("[MEMORY] Starting memory optimization...")

            # Remove low-importance, rarely accessed memories
            removed_count = await self._cleanup_stale_memories()

            # Strengthen important memory connections
            await self._strengthen_memory_connections()

            # Update indices
            await self._rebuild_indices()

            # Save optimized state
            await self._save_cognitive_state()

            logger.info(
                f"[MEMORY] Memory optimization complete. Removed {removed_count} stale memories"
            )

        except Exception as e:
            logger.error(f"[MEMORY] Memory optimization error: {e}")

    def _generate_auto_tags(
        self, content: Any, context: dict | None = None
    ) -> list[str]:
        """Generate automatic tags based on content analysis."""
        tags = []

        content_str = str(content).lower()

        # Common AI OS concepts
        ai_concepts = [
            "memory",
            "cognitive",
            "consciousness",
            "intelligence",
            "learning",
            "system",
            "service",
            "plugin",
            "agent",
            "goal",
            "task",
        ]

        for concept in ai_concepts:
            if concept in content_str:
                tags.append(concept)

        # Context-based tags
        if context:
            if "source" in context:
                tags.append(f"source_{context['source']}")
            if "session_id" in context:
                tags.append(f"session_{context['session_id']}")

        return tags

    async def _create_memory_connections(self, memory: AetherraMemoryNode):
        """Create connections to related memories."""
        try:
            # Find similar memories
            similar_memories = self.index.find_by_content_similarity(
                str(memory.content)
            )

            # Connect to most similar memories
            for similar_id in list(similar_memories)[:5]:
                if similar_id != memory.id and similar_id in self.memories:
                    memory.add_connection(similar_id)
                    self.memories[similar_id].add_connection(memory.id)

            # Connect by shared tags
            for tag in memory.tags:
                tagged_memories = self.index.find_by_tag(tag)
                for tagged_id in list(tagged_memories)[:3]:
                    if tagged_id != memory.id and tagged_id in self.memories:
                        memory.add_connection(tagged_id)
                        self.memories[tagged_id].add_connection(memory.id)

        except Exception as e:
            logger.error(f"[MEMORY] Connection creation error: {e}")

    async def _rank_memories(
        self, candidate_ids: set, query: str
    ) -> list[dict[str, Any]]:
        """Rank memories by relevance to query."""
        try:
            scored_memories = []

            # Optional quantum-enhanced scoring
            use_quantum = os.environ.get("AETHERRA_QUANTUM_RECALL", "0") in (
                "1",
                "true",
                "True",
            )
            qhash_bits = int(os.environ.get("AETHERRA_QHASH_BITS", "64"))
            qhash_weight = float(os.environ.get("AETHERRA_QHASH_WEIGHT", "0.5"))
            rfm_weight = float(os.environ.get("AETHERRA_RFM_WEIGHT", "0.3"))
            rfm_in = int(os.environ.get("AETHERRA_RFM_IN", "128"))
            rfm_out = int(os.environ.get("AETHERRA_RFM_OUT", "32"))
            rfm_seed = int(os.environ.get("AETHERRA_RFM_SEED", "42"))
            quantum_audit = os.environ.get("AETHERRA_QUANTUM_AUDIT", "0") in (
                "1",
                "true",
                "True",
            )

            # Initialize defaults to satisfy type checkers
            query_qhash: int | None = None
            rfm: RandomFeatureMap | None = None
            q_proj: list[float] | None = None
            if use_quantum:
                try:
                    query_qhash = simhash_text(query, bits=qhash_bits)
                except Exception:
                    query_qhash = None
                # Prepare Random Feature Map for query
                try:
                    rfm = RandomFeatureMap(
                        in_dim=rfm_in, out_dim=rfm_out, seed=rfm_seed
                    )
                    q_vec = self._hashed_bow_vector(query, rfm_in)
                    q_proj = rfm.transform(q_vec)
                except Exception:
                    rfm = None
                    q_proj = None

            for memory_id in candidate_ids:
                if memory_id not in self.memories:
                    continue

                memory = self.memories[memory_id]
                score = 0.0
                q_audit: dict[str, Any] = {}

                # Content relevance
                content_str = str(memory.content).lower()
                query_words = query.lower().split()
                for word in query_words:
                    if word in content_str:
                        score += 1.0

                # Importance weight
                score += memory.importance * 2.0

                # Recency bonus
                days_old = (datetime.now() - memory.created_at).days
                recency_bonus = max(0, 1.0 - days_old / 30.0)  # Decay over 30 days
                score += recency_bonus

                # Access frequency bonus
                access_bonus = min(memory.access_count * 0.1, 1.0)
                score += access_bonus

                # Quantum-enhanced components
                if use_quantum:
                    try:
                        # QHash similarity (1 - normalized Hamming distance)
                        mh: int | None = None
                        if isinstance(memory.context, dict):
                            qctx = memory.context.get("quantum")
                            if (
                                isinstance(qctx, dict)
                                and ("qhash" in qctx)
                                and qctx["qhash"] is not None
                            ):
                                try:
                                    mh = int(qctx["qhash"])  # ensure int type
                                except Exception:
                                    mh = None
                        if mh is None:
                            mh = simhash_text(str(memory.content), bits=qhash_bits)
                        if query_qhash is not None and mh is not None:
                            dist = hamming_distance(int(mh), int(query_qhash))
                            qsim = 1.0 - (float(dist) / float(qhash_bits))
                            score += qhash_weight * qsim
                            if quantum_audit:
                                q_audit["qhash"] = {
                                    "distance": dist,
                                    "similarity": qsim,
                                    "bits": qhash_bits,
                                }
                    except Exception as qe:
                        if quantum_audit:
                            q_audit["qhash_error"] = str(qe)

                    # Random Feature Map similarity
                    try:
                        if rfm is not None and q_proj is not None:
                            m_vec = self._hashed_bow_vector(str(memory.content), rfm_in)
                            m_proj = rfm.transform(m_vec)
                            sim = cosine_similarity(q_proj, m_proj)
                            # Map from [-1,1] to [0,1]
                            sim01 = (sim + 1.0) / 2.0
                            score += rfm_weight * sim01
                            if quantum_audit:
                                q_audit["rfm"] = {
                                    "cosine": sim,
                                    "similarity01": sim01,
                                    "in": rfm_in,
                                    "out": rfm_out,
                                }
                    except Exception as re:
                        if quantum_audit:
                            q_audit["rfm_error"] = str(re)

                mem_dict = memory.to_dict()
                if quantum_audit and q_audit:
                    mem_dict.setdefault("audit", {})["quantum"] = q_audit
                scored_memories.append((score, mem_dict))

            # Sort by score descending
            scored_memories.sort(key=lambda x: x[0], reverse=True)

            return [memory_data for _, memory_data in scored_memories]

        except Exception as e:
            logger.error(f"[MEMORY] Ranking error: {e}")
            return []

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        if not text:
            return []
        return [
            t
            for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split()
            if t
        ]

    def _hashed_bow_vector(self, text: str, dim: int) -> list[float]:
        vec = [0.0] * dim
        tokens = self._tokenize(text)
        if not tokens:
            return vec
        for tok in tokens:
            h = int(hashlib.sha256(tok.encode("utf-8")).hexdigest()[:8], 16)
            idx = h % dim
            vec[idx] += 1.0
        # L2 normalize to avoid length bias
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def _get_recent_important_memories(self, limit: int) -> set:
        """Get recent high-importance memories as fallback."""
        try:
            candidates = set()

            # Get high-importance memories
            for importance_level in range(7, 11):  # 0.7-1.0 importance
                if importance_level in self.index.importance_index:
                    candidates.update(self.index.importance_index[importance_level])

            # If not enough, add recent memories
            if len(candidates) < limit:
                recent_date = (datetime.now() - timedelta(days=7)).date().isoformat()
                for date_key, memory_ids in self.index.time_index.items():
                    if date_key >= recent_date:
                        candidates.update(memory_ids)

            return candidates

        except Exception as e:
            logger.error(f"[MEMORY] Recent memories error: {e}")
            return set()

    def _get_recent_memories(self, hours: int = 24) -> list[AetherraMemoryNode]:
        """Get memories from recent time period."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent = []

            for memory in self.memories.values():
                if memory.created_at >= cutoff_time:
                    recent.append(memory)

            return recent

        except Exception as e:
            logger.error(f"[MEMORY] Recent memories error: {e}")
            return []

    def _get_memory_type_distribution(self) -> dict[str, int]:
        """Get distribution of memory types."""
        try:
            distribution = {}
            for memory in self.memories.values():
                memory_type = memory.memory_type
                distribution[memory_type] = distribution.get(memory_type, 0) + 1
            return distribution
        except Exception as e:
            logger.error(f"[MEMORY] Type distribution error: {e}")
            return {}

    def _get_recent_activity_summary(self) -> dict[str, Any]:
        """Get summary of recent memory activity."""
        try:
            recent = self._get_recent_memories(hours=24)

            return {
                "memories_created_24h": len(recent),
                "most_common_type": max(
                    self._get_memory_type_distribution().items(), key=lambda x: x[1]
                )[0]
                if self.memories
                else None,
                "average_importance": sum(m.importance for m in recent) / len(recent)
                if recent
                else 0.0,
            }
        except Exception as e:
            logger.error(f"[MEMORY] Activity summary error: {e}")
            return {}

    def _calculate_connection_density(self) -> float:
        """Calculate how connected memories are."""
        try:
            if not self.memories:
                return 0.0

            total_connections = sum(len(m.connections) for m in self.memories.values())
            max_connections = len(self.memories) * (len(self.memories) - 1)

            return total_connections / max_connections if max_connections > 0 else 0.0

        except Exception as e:
            logger.error(f"[MEMORY] Connection density error: {e}")
            return 0.0

    async def _load_memories(self):
        """Load memories from persistent storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM memories")
            rows = cursor.fetchall()

            for row in rows:
                memory_data = {
                    "id": row[0],
                    "content": row[1],
                    "memory_type": row[2],
                    "context": json.loads(row[3]) if row[3] else {},
                    "importance": row[4],
                    "created_at": row[5],
                    "last_accessed": row[6],
                    "access_count": row[7],
                    "connections": json.loads(row[8]) if row[8] else [],
                    "tags": json.loads(row[9]) if row[9] else [],
                    "emotional_weight": row[10],
                    "confidence": row[11],
                    "source": row[12],
                    "verified": row[13],
                }

                memory = AetherraMemoryNode.from_dict(memory_data)
                self.memories[memory.id] = memory
                self.index.index_memory(memory)

            conn.close()

        except Exception as e:
            logger.error(f"[MEMORY] Load memories error: {e}")

    async def _save_memory_to_db(self, memory: AetherraMemoryNode):
        """Save memory to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO memories
                (id, content, memory_type, context, importance, created_at,
                 last_accessed, access_count, connections, tags, emotional_weight,
                 confidence, source, verified, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory.id,
                    str(memory.content),
                    memory.memory_type,
                    json.dumps(memory.context),
                    memory.importance,
                    memory.created_at.isoformat(),
                    memory.last_accessed.isoformat(),
                    memory.access_count,
                    json.dumps(list(memory.connections)),
                    json.dumps(list(memory.tags)),
                    memory.emotional_weight,
                    memory.confidence,
                    memory.source,
                    memory.verified,
                    self.session_id,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"[MEMORY] Save memory error: {e}")

    async def _update_memory_in_db(self, memory: AetherraMemoryNode):
        """Update existing memory in database."""
        await self._save_memory_to_db(memory)  # Same operation for SQLite

    async def _ensure_core_facts(self):
        """Seed core, verified facts that should always be available.

        Idempotent: checks DB for an equivalent fact before inserting.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Ownership fact for Aetherra Labs
            ownership_text = "Aetherra Labs is founded and owned by Timothy Holdorff. It is an independent, open-source project."

            cursor.execute(
                """
                SELECT id FROM memories
                WHERE memory_type = ?
                  AND verified = 1
                  AND content LIKE ?
                LIMIT 1
                """,
                ("fact", "%Aetherra Labs is founded and owned by%"),
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                return  # Already present

            # Insert via normal store path to keep indices in sync
            node = AetherraMemoryNode(
                content=ownership_text,
                memory_type="fact",
                context={
                    "source": "system",
                    "category": "ownership",
                    "domain": "aetherra",
                },
                importance=0.95,
            )
            node.verified = True
            node.source = "system"
            node.confidence = 1.0
            node.add_tag("ownership")
            node.add_tag("aetherra")
            node.add_tag("labs")
            node.add_tag("core_fact")

            # Save in-memory, index, and persist
            self.memories[node.id] = node
            self.index.index_memory(node)
            await self._save_memory_to_db(node)

            logger.info("[MEMORY] Seeded core fact: ownership (Aetherra Labs)")

        except Exception as e:
            logger.warning(f"[MEMORY] Core facts seed error: {e}")

    def _load_persistent_state(self):
        """Load persistent cognitive state."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT key, value FROM cognitive_state")
            rows = cursor.fetchall()

            for key, value in rows:
                try:
                    self.cognitive_state[key] = json.loads(value)
                except Exception:
                    self.cognitive_state[key] = value

            conn.close()

        except Exception as e:
            logger.error(f"[MEMORY] Load state error: {e}")

    async def _save_cognitive_state(self):
        """Save cognitive state to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for key, value in self.cognitive_state.items():
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO cognitive_state (key, value, updated_at)
                    VALUES (?, ?, ?)
                """,
                    (key, json.dumps(value), datetime.now().isoformat()),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"[MEMORY] Save state error: {e}")

    async def _update_cognitive_state(self):
        """Update cognitive state metrics."""
        await self._save_cognitive_state()

    async def _save_session_start(self):
        """Record session start."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO sessions (session_id, started_at, memory_count)
                VALUES (?, ?, ?)
            """,
                (self.session_id, datetime.now().isoformat(), len(self.memories)),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"[MEMORY] Session start error: {e}")

    async def _cleanup_stale_memories(self) -> int:
        """Remove stale, low-importance memories."""
        try:
            removed_count = 0
            cutoff_date = datetime.now() - timedelta(days=30)

            to_remove = []
            for memory_id, memory in self.memories.items():
                # Remove if old, low importance, and rarely accessed
                if (
                    memory.created_at < cutoff_date
                    and memory.importance < 0.3
                    and memory.access_count < 2
                ):
                    to_remove.append(memory_id)

            # Remove from memory and database
            for memory_id in to_remove:
                del self.memories[memory_id]
                removed_count += 1

                # Remove from database
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
                conn.commit()
                conn.close()

            # Rebuild indices
            await self._rebuild_indices()

            return removed_count

        except Exception as e:
            logger.error(f"[MEMORY] Cleanup error: {e}")
            return 0

    async def _strengthen_memory_connections(self):
        """Strengthen connections between frequently accessed memories."""
        try:
            # Find highly accessed memories
            high_access_memories = [
                m for m in self.memories.values() if m.access_count > 5
            ]

            # Create additional connections between them
            for i, memory1 in enumerate(high_access_memories):
                for memory2 in high_access_memories[i + 1 :]:
                    # Check for content similarity or shared tags
                    shared_tags = memory1.tags.intersection(memory2.tags)
                    if shared_tags or memory1.memory_type == memory2.memory_type:
                        memory1.add_connection(memory2.id)
                        memory2.add_connection(memory1.id)

                        # Save updates
                        await self._update_memory_in_db(memory1)
                        await self._update_memory_in_db(memory2)

        except Exception as e:
            logger.error(f"[MEMORY] Connection strengthening error: {e}")

    async def _rebuild_indices(self):
        """Rebuild memory indices."""
        try:
            self.index = AetherraMemoryIndex()

            for memory in self.memories.values():
                self.index.index_memory(memory)

        except Exception as e:
            logger.error(f"[MEMORY] Index rebuild error: {e}")

    async def shutdown(self):
        """Graceful shutdown with state persistence."""
        try:
            logger.info("[MEMORY] Shutting down persistent memory system...")

            # Save final cognitive state
            await self._save_cognitive_state()

            # Update session end
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sessions
                SET ended_at = ?, memory_count = ?
                WHERE session_id = ?
            """,
                (datetime.now().isoformat(), len(self.memories), self.session_id),
            )
            conn.commit()
            conn.close()

            logger.info(
                f"[MEMORY] Session {self.session_id} ended with {len(self.memories)} memories"
            )

        except Exception as e:
            logger.error(f"[MEMORY] Shutdown error: {e}")


# Singleton instance (lazy initialization)
_persistent_memory_instance = None


# Factory function for service integration
async def get_persistent_memory_system():
    """Factory function to get or create the persistent memory system singleton."""
    global _persistent_memory_instance
    if _persistent_memory_instance is None:
        _persistent_memory_instance = AetherraPerśistentMemorySystem()
        await _persistent_memory_instance.initialize()
    return _persistent_memory_instance
