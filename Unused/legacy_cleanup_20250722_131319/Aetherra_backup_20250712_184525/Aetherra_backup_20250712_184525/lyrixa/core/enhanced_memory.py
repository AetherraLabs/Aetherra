#!/usr/bin/env python3
"""
🧠 LYRIXA ENHANCED MEMORY SYSTEM
================================

Advanced memory capabilities with visualization, clustering,
tagging, timeline navigation, and intelligent recall.
"""

import asyncio
import hashlib
import json
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MemoryCluster:
    """Represents a cluster of related memories"""

    id: str
    name: str
    description: str
    memories: List[str]  # Memory IDs
    center_vector: List[float]
    creation_date: datetime
    last_accessed: datetime
    access_count: int
    tags: List[str]


@dataclass
class MemoryTimeline:
    """Timeline representation of memories"""

    period: str  # daily, weekly, monthly
    start_date: datetime
    end_date: datetime
    memory_count: int
    memory_ids: List[str]
    key_events: List[Dict[str, Any]]
    summary: str


@dataclass
class MemoryVisualization:
    """Data structure for memory visualization"""

    memory_map: Dict[str, Dict[str, Any]]  # 2D coordinates for memories
    clusters: List[MemoryCluster]
    connections: List[Tuple[str, str, float]]  # (id1, id2, strength)
    timeline: List[MemoryTimeline]
    statistics: Dict[str, Any]


class LyrixaEnhancedMemorySystem:
    """
    Enhanced memory system with advanced features:
    - Memory clustering and similarity detection
    - Visual memory maps and timelines
    - Intelligent tagging and categorization
    - Pattern recognition and insights
    - Memory consolidation and cleanup
    """

    def __init__(self, memory_db_path: str = "lyrixa_enhanced_memory.db"):
        self.db_path = memory_db_path
        self.clusters: Dict[str, MemoryCluster] = {}
        self.memory_vectors: Dict[str, List[float]] = {}
        self.tag_relationships: Dict[str, List[str]] = defaultdict(list)

        # Initialize database
        self._initialize_database_sync()

        print("🧠 Lyrixa Enhanced Memory System initialized")

    def _initialize_database_sync(self):
        """Initialize the enhanced memory database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Enhanced memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_memories (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    context TEXT,
                    tags TEXT,
                    importance REAL,
                    created_at TEXT,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    memory_type TEXT,
                    embedding_vector TEXT,
                    cluster_id TEXT,
                    emotional_valence REAL DEFAULT 0.0,
                    cognitive_load REAL DEFAULT 0.0,
                    retention_strength REAL DEFAULT 1.0,
                    source_context TEXT,
                    related_memories TEXT
                )
            """)

            # Memory clusters table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_clusters (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    center_vector TEXT,
                    creation_date TEXT,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 0,
                    tags TEXT,
                    memory_count INTEGER DEFAULT 0
                )
            """)

            # Memory relationships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_relationships (
                    id TEXT PRIMARY KEY,
                    memory_id_1 TEXT,
                    memory_id_2 TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    created_at TEXT,
                    FOREIGN KEY (memory_id_1) REFERENCES enhanced_memories (id),
                    FOREIGN KEY (memory_id_2) REFERENCES enhanced_memories (id)
                )
            """)

            # Memory timeline table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_timeline (
                    id TEXT PRIMARY KEY,
                    period_type TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    memory_ids TEXT,
                    key_events TEXT,
                    summary TEXT,
                    created_at TEXT
                )
            """)

            # Create enhanced indexes
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_enhanced_memory_type ON enhanced_memories(memory_type)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_enhanced_importance ON enhanced_memories(importance)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_enhanced_created_at ON enhanced_memories(created_at)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_enhanced_cluster_id ON enhanced_memories(cluster_id)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_enhanced_tags ON enhanced_memories(tags)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_emotional_valence ON enhanced_memories(emotional_valence)"
            )

            conn.commit()
            conn.close()

            print("✅ Enhanced memory database initialized")

        except Exception as e:
            print(f"[ERROR] Failed to initialize enhanced memory database: {e}")

    async def query_memories(
        self, query: str, tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search memories based on a query and optional tags."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build SQL query
            sql_query = (
                "SELECT id, content, tags FROM enhanced_memories WHERE content LIKE ?"
            )
            params = [f"%{query}%"]

            if tags:
                sql_query += " AND ("
                sql_query += " OR ".join(["tags LIKE ?" for _ in tags])
                sql_query += ")"
                params.extend([f"%{tag}%" for tag in tags])

            cursor.execute(sql_query, params)
            results = cursor.fetchall()
            conn.close()

            # Format results
            memories = [
                {
                    "id": row[0],
                    "content": json.loads(row[1]),
                    "tags": json.loads(row[2]),
                }
                for row in results
            ]

            return memories

        except Exception as e:
            print(f"[ERROR] Failed to search memories: {e}")
            return []

    async def store_enhanced_memory(
        self,
        content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        importance: float = 0.5,
        emotional_valence: float = 0.0,
        cognitive_load: float = 0.5,
    ) -> str:
        """Store memory with enhanced metadata and automatic clustering."""
        memory_id = self._generate_memory_id(content, context)
        now = datetime.now().isoformat()
        memory_type = "general"  # Default memory type

        # Generate embedding vector for clustering
        embedding_vector = await self._generate_embedding(content, context)

        # Find or create appropriate cluster
        cluster_id = await self._find_or_create_cluster(
            embedding_vector, tags or [], memory_type
        )

        # Detect related memories
        related_memories = await self._find_related_memories(
            embedding_vector, memory_id
        )

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO enhanced_memories
                (id, content, context, tags, importance, created_at, last_accessed,
                 access_count, memory_type, embedding_vector, cluster_id,
                 emotional_valence, cognitive_load, retention_strength,
                 source_context, related_memories)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    memory_id,
                    json.dumps(content),
                    json.dumps(context or {}),
                    json.dumps(tags or []),
                    importance,
                    now,
                    now,
                    1,
                    "general",  # Default memory type
                    json.dumps(embedding_vector),
                    cluster_id,
                    emotional_valence,
                    cognitive_load,
                    1.0,  # Initial retention strength
                    json.dumps(context or {}),
                    json.dumps(related_memories),
                ),
            )

            conn.commit()
            conn.close()

            # Update memory vectors cache
            self.memory_vectors[memory_id] = embedding_vector

            # Update tag relationships
            if tags:
                for tag in tags:
                    self.tag_relationships[tag].append(memory_id)

            # Create relationships with related memories
            await self._create_memory_relationships(memory_id, related_memories)

            print(f"🧠 Enhanced memory stored: {memory_id}")
            return memory_id

        except Exception as e:
            print(f"[ERROR] Failed to store enhanced memory: {e}")
            return ""

    async def _generate_embedding(
        self, content: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> List[float]:
        """Generate embedding vector for memory content (simplified implementation)"""

        # Convert content to text
        text = ""
        if isinstance(content, dict):
            text = " ".join(str(v) for v in content.values())
        else:
            text = str(content)

        if context:
            text += " " + " ".join(str(v) for v in context.values())

        # Simple hash-based embedding (in production, use proper embeddings)
        words = text.lower().split()
        vector = [0.0] * 128  # 128-dimensional vector

        for i, word in enumerate(words[:64]):  # Use first 64 words
            hash_val = hash(word) % 1000000
            vector[i % 128] += hash_val / 1000000.0
            vector[(i + 64) % 128] += len(word) / 20.0

        # Normalize vector
        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]

        return vector

    async def _find_or_create_cluster(
        self, embedding_vector: List[float], tags: List[str], memory_type: str
    ) -> str:
        """Find appropriate cluster or create new one"""

        # Calculate similarity to existing clusters
        best_cluster = None
        best_similarity = 0.7  # Threshold for cluster membership

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, center_vector, tags FROM memory_clusters")

        for cluster_id, center_vector_json, cluster_tags_json in cursor.fetchall():
            center_vector = json.loads(center_vector_json)
            cluster_tags = json.loads(
                cluster_tags_json
            )  # Ensure correct variable usage

            # Calculate cosine similarity
            similarity = self._cosine_similarity(embedding_vector, center_vector)

            # Boost similarity if tags match
            tag_overlap = len(set(tags) & set(cluster_tags))
            if tag_overlap > 0:
                similarity += tag_overlap * 0.1

            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster = cluster_id

        conn.close()

        if best_cluster:
            # Update cluster center (moving average)
            await self._update_cluster_center(best_cluster, embedding_vector)
            return best_cluster
        else:
            # Create new cluster
            return await self._create_new_cluster(embedding_vector, tags)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def _create_new_cluster(
        self, center_vector: List[float], tags: List[str]
    ) -> str:
        """Create a new memory cluster"""
        cluster_id = f"cluster_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(center_vector)) % 10000}"
        cluster_name = "Cluster "

        if tags:
            cluster_name += f" ({', '.join(tags[:2])})"

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO memory_clusters
                (id, name, description, center_vector, creation_date, last_accessed, tags, memory_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    cluster_id,
                    cluster_name,
                    "Auto-generated cluster for memories",
                    json.dumps(center_vector),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    json.dumps(tags),
                    1,
                ),
            )

            conn.commit()
            conn.close()

            print(f"🧩 Created new memory cluster: {cluster_name}")
            return cluster_id

        except Exception as e:
            print(f"[ERROR] Failed to create cluster: {e}")
            return "default_cluster"

    async def _update_cluster_center(self, cluster_id: str, new_vector: List[float]):
        """Update cluster center using moving average"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current cluster data
            cursor.execute(
                "SELECT center_vector, memory_count FROM memory_clusters WHERE id = ?",
                (cluster_id,),
            )
            result = cursor.fetchone()

            if result:
                current_center = json.loads(result[0])
                memory_count = result[1]

                # Calculate new center (moving average)
                alpha = 1.0 / (memory_count + 1)  # Learning rate
                new_center = [
                    (1 - alpha) * old + alpha * new
                    for old, new in zip(current_center, new_vector)
                ]

                # Update cluster
                cursor.execute(
                    """
                    UPDATE memory_clusters
                    SET center_vector = ?, memory_count = memory_count + 1, last_accessed = ?
                    WHERE id = ?
                """,
                    (json.dumps(new_center), datetime.now().isoformat(), cluster_id),
                )

                conn.commit()

            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to update cluster center: {e}")

    async def _find_related_memories(
        self, embedding_vector: List[float], current_memory_id: str, limit: int = 5
    ) -> List[str]:
        """Find memories related to the current one"""
        related = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, embedding_vector FROM enhanced_memories WHERE id != ?",
                (current_memory_id,),
            )

            similarities = []
            for memory_id, vector_json in cursor.fetchall():
                vector = json.loads(vector_json)
                similarity = self._cosine_similarity(embedding_vector, vector)
                if similarity > 0.6:  # Similarity threshold
                    similarities.append((memory_id, similarity))

            # Sort by similarity and return top matches
            similarities.sort(key=lambda x: x[1], reverse=True)
            related = [mem_id for mem_id, _ in similarities[:limit]]

            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to find related memories: {e}")

        return related

    async def _create_memory_relationships(
        self, memory_id: str, related_memory_ids: List[str]
    ):
        """Create relationships between memories"""
        if not related_memory_ids:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            for related_id in related_memory_ids:
                relationship_id = f"rel_{memory_id}_{related_id}"

                # Calculate relationship strength
                strength = self._cosine_similarity(
                    self.memory_vectors.get(memory_id, []),
                    self.memory_vectors.get(related_id, []),
                )

                cursor.execute(
                    """
                    INSERT OR REPLACE INTO memory_relationships
                    (id, memory_id_1, memory_id_2, relationship_type, strength, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        relationship_id,
                        memory_id,
                        related_id,
                        "similarity",
                        strength,
                        datetime.now().isoformat(),
                    ),
                )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to create memory relationships: {e}")

    async def recall_with_clustering(
        self, query: str, cluster_filter: Optional[str] = None, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Enhanced recall with cluster-aware search"""

        # Generate query embedding
        query_vector = await self._generate_embedding({"query": query}, None)

        results = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Build query with optional cluster filter
            sql = """
                SELECT id, content, context, tags, importance, created_at,
                       embedding_vector, cluster_id, emotional_valence
                FROM enhanced_memories
            """
            params = []

            if cluster_filter:
                sql += " WHERE cluster_id = ?"
                params.append(cluster_filter)

            cursor.execute(sql, params)

            similarities = []
            for row in cursor.fetchall():
                (
                    memory_id,
                    content,
                    context,
                    tags,
                    importance,
                    created_at,
                    vector_json,
                    cluster_id,
                    emotional_valence,
                ) = row

                memory_vector = json.loads(vector_json)
                similarity = self._cosine_similarity(query_vector, memory_vector)

                # Boost score based on importance and recency
                days_old = (datetime.now() - datetime.fromisoformat(created_at)).days
                recency_boost = max(0, 1 - days_old / 365)  # Decay over a year

                final_score = similarity * 0.7 + importance * 0.2 + recency_boost * 0.1

                if final_score > 0.3:  # Relevance threshold
                    similarities.append(
                        (
                            final_score,
                            {
                                "id": memory_id,
                                "content": json.loads(content),
                                "context": json.loads(context),
                                "tags": json.loads(tags),
                                "importance": importance,
                                "created_at": created_at,
                                "cluster_id": cluster_id,
                                "emotional_valence": emotional_valence,
                                "similarity_score": similarity,
                                "final_score": final_score,
                            },
                        )
                    )

            # Sort by final score and return top results
            similarities.sort(key=lambda x: x[0], reverse=True)
            results = [item[1] for item in similarities[:limit]]

            conn.close()

            # Update access counts
            for result in results:
                await self._update_memory_access(result["id"])

        except Exception as e:
            print(f"[ERROR] Failed to recall memories: {e}")

        return results

    async def get_memory_visualization(self) -> MemoryVisualization:
        """Generate visualization data for memories"""

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all memories with their vectors
            cursor.execute("""
                SELECT id, embedding_vector, cluster_id, tags, importance, created_at, emotional_valence
                FROM enhanced_memories
            """)

            memories = cursor.fetchall()

            # Generate 2D coordinates using simple projection
            memory_map = {}
            for (
                memory_id,
                vector_json,
                cluster_id,
                tags_json,
                importance,
                created_at,
                emotional_valence,
            ) in memories:
                vector = json.loads(vector_json)

                # Simple 2D projection (PCA-like)
                x = sum(vector[i] for i in range(0, len(vector), 2)) / (
                    len(vector) // 2
                )
                y = sum(vector[i] for i in range(1, len(vector), 2)) / (
                    len(vector) // 2
                )

                memory_map[memory_id] = {
                    "x": x,
                    "y": y,
                    "cluster_id": cluster_id,
                    "tags": json.loads(tags_json),
                    "importance": importance,
                    "created_at": created_at,
                    "emotional_valence": emotional_valence,
                }

            # Get clusters
            cursor.execute(
                "SELECT id, name, description, tags, memory_count FROM memory_clusters"
            )
            clusters = []
            for (
                cluster_id,
                name,
                description,
                tags_json,
                memory_count,
            ) in cursor.fetchall():
                clusters.append(
                    MemoryCluster(
                        id=cluster_id,
                        name=name,
                        description=description,
                        memories=[
                            mid
                            for mid, data in memory_map.items()
                            if data["cluster_id"] == cluster_id
                        ],
                        center_vector=[],  # Simplified
                        creation_date=datetime.now(),
                        last_accessed=datetime.now(),
                        access_count=memory_count,
                        tags=json.loads(tags_json),
                    )
                )

            # Get relationships
            cursor.execute(
                "SELECT memory_id_1, memory_id_2, strength FROM memory_relationships"
            )
            connections = [
                (id1, id2, strength) for id1, id2, strength in cursor.fetchall()
            ]

            conn.close()

            # Generate timeline
            timeline = await self._generate_memory_timeline()

            # Calculate statistics
            statistics = {
                "total_memories": len(memories),
                "total_clusters": len(clusters),
                "total_connections": len(connections),
                "average_importance": sum(
                    data["importance"] for data in memory_map.values()
                )
                / len(memory_map)
                if memory_map
                else 0,
                "emotional_distribution": self._calculate_emotional_distribution(
                    memory_map
                ),
                "memory_growth": await self._calculate_memory_growth(),
            }

            return MemoryVisualization(
                memory_map=memory_map,
                clusters=clusters,
                connections=connections,
                timeline=timeline,
                statistics=statistics,
            )

        except Exception as e:
            print(f"[ERROR] Failed to generate memory visualization: {e}")
            return MemoryVisualization({}, [], [], [], {})

    async def _generate_memory_timeline(self) -> List[MemoryTimeline]:
        """Generate timeline representation of memories"""
        timelines = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate daily timeline for last 7 days
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)

                cursor.execute(
                    """
                    SELECT id, content, importance FROM enhanced_memories
                    WHERE created_at BETWEEN ? AND ?
                """,
                    (start_date.isoformat(), end_date.isoformat()),
                )

                day_memories = cursor.fetchall()

                if day_memories:
                    memory_ids = [mem[0] for mem in day_memories]

                    # Extract key events (high importance memories)
                    key_events = [
                        {
                            "memory_id": mem[0],
                            "content_summary": str(json.loads(mem[1]))[:100] + "...",
                            "importance": mem[2],
                        }
                        for mem in day_memories
                        if mem[2] > 0.7
                    ]

                    # Generate summary
                    summary = f"{len(day_memories)} memories created"
                    if key_events:
                        summary += f", {len(key_events)} important events"

                    timelines.append(
                        MemoryTimeline(
                            period="daily",
                            start_date=start_date,
                            end_date=end_date,
                            memory_count=len(day_memories),
                            memory_ids=memory_ids,
                            key_events=key_events,
                            summary=summary,
                        )
                    )

            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to generate timeline: {e}")

        return timelines

    def _calculate_emotional_distribution(
        self, memory_map: Dict[str, Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of emotional valences"""
        distribution = {"positive": 0, "neutral": 0, "negative": 0}

        for data in memory_map.values():
            valence = data.get("emotional_valence", 0.0)
            if valence > 0.1:
                distribution["positive"] += 1
            elif valence < -0.1:
                distribution["negative"] += 1
            else:
                distribution["neutral"] += 1

        return distribution

    async def _calculate_memory_growth(self) -> List[Dict[str, Any]]:
        """Calculate memory growth over time"""
        growth = []

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get memory counts by day for last 30 days
            for i in range(30):
                date = datetime.now() - timedelta(days=i)
                start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=1)

                cursor.execute(
                    """
                    SELECT COUNT(*) FROM enhanced_memories
                    WHERE created_at BETWEEN ? AND ?
                """,
                    (start_date.isoformat(), end_date.isoformat()),
                )

                count = cursor.fetchone()[0]
                growth.append({"date": start_date.strftime("%Y-%m-%d"), "count": count})

            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to calculate memory growth: {e}")

        return growth[::-1]  # Reverse to get chronological order

    async def _update_memory_access(self, memory_id: str):
        """Update memory access statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                UPDATE enhanced_memories
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), memory_id),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"[ERROR] Failed to update memory access: {e}")

    async def consolidate_memories(self):
        """Advanced memory consolidation with clustering optimization"""
        print("🧠 Starting advanced memory consolidation...")

        try:
            # Remove low-importance, old memories
            await self._cleanup_old_memories()

            # Optimize clusters
            await self._optimize_clusters()

            # Strengthen important relationships
            await self._strengthen_relationships()

            # Update retention strengths
            await self._update_retention_strengths()

            print("✅ Memory consolidation completed")

        except Exception as e:
            print(f"[ERROR] Memory consolidation failed: {e}")

    async def _cleanup_old_memories(self):
        """Remove old, unimportant memories"""
        cutoff_date = datetime.now() - timedelta(days=365)  # 1 year ago

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM enhanced_memories
                WHERE created_at < ? AND importance < 0.3 AND access_count < 2
            """,
                (cutoff_date.isoformat(),),
            )

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            print(f"🗑️ Cleaned up {deleted_count} old memories")

        except Exception as e:
            print(f"[ERROR] Failed to cleanup memories: {e}")

    async def _optimize_clusters(self):
        """Optimize memory clusters by merging similar ones"""
        # Implementation would involve clustering algorithms
        print("🧩 Optimizing memory clusters...")

    async def _strengthen_relationships(self):
        """Strengthen relationships between frequently accessed memories"""
        print("🔗 Strengthening memory relationships...")

    async def _update_retention_strengths(self):
        """Update retention strengths based on access patterns"""
        print("💪 Updating retention strengths...")

    async def get_memory_insights(self) -> Dict[str, Any]:
        """Generate insights about memory patterns and usage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Most accessed memories
            cursor.execute("""
                SELECT content, access_count FROM enhanced_memories
                ORDER BY access_count DESC LIMIT 5
            """)
            most_accessed = [
                {"content": json.loads(content)[:100], "access_count": count}
                for content, count in cursor.fetchall()
            ]

            # Memory type distribution
            cursor.execute(
                "SELECT memory_type, COUNT(*) FROM enhanced_memories GROUP BY memory_type"
            )
            type_distribution = dict(cursor.fetchall())

            # Emotional trend
            cursor.execute(
                """
                SELECT AVG(emotional_valence) FROM enhanced_memories
                WHERE created_at > ?
            """,
                ((datetime.now() - timedelta(days=7)).isoformat(),),
            )

            recent_emotional_avg = cursor.fetchone()[0] or 0.0

            conn.close()

            return {
                "most_accessed_memories": most_accessed,
                "memory_type_distribution": type_distribution,
                "recent_emotional_trend": recent_emotional_avg,
                "total_clusters": len(self.clusters),
                "memory_network_density": await self._calculate_network_density(),
                "learning_velocity": await self._calculate_learning_velocity(),
            }

        except Exception as e:
            print(f"[ERROR] Failed to generate insights: {e}")
            return {}

    async def _calculate_network_density(self) -> float:
        """Calculate density of memory relationship network"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM enhanced_memories")
            total_memories = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM memory_relationships")
            total_relationships = cursor.fetchone()[0]

            conn.close()

            if total_memories < 2:
                return 0.0

            max_possible = total_memories * (total_memories - 1) / 2
            return total_relationships / max_possible if max_possible > 0 else 0.0

        except Exception as e:
            print(f"[ERROR] Failed to calculate network density: {e}")
            return 0.0

    async def _calculate_learning_velocity(self) -> float:
        """Calculate rate of new memory formation"""
        try:
            week_ago = datetime.now() - timedelta(days=7)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*) FROM enhanced_memories
                WHERE created_at > ?
            """,
                (week_ago.isoformat(),),
            )

            recent_memories = cursor.fetchone()[0]
            conn.close()

            return recent_memories / 7.0  # Memories per day

        except Exception as e:
            print(f"[ERROR] Failed to calculate learning velocity: {e}")
            return 0.0

    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""

        def _get_stats():
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Count total memories
            cursor.execute("SELECT COUNT(*) FROM enhanced_memories")
            total_memories = cursor.fetchone()[0]

            # Count clusters
            cursor.execute("SELECT COUNT(*) FROM memory_clusters")
            total_clusters = cursor.fetchone()[0]

            # Get memory by type
            cursor.execute(
                "SELECT memory_type, COUNT(*) FROM enhanced_memories GROUP BY memory_type"
            )
            memory_by_type = dict(cursor.fetchall())

            # Get recent activity
            cursor.execute(
                "SELECT COUNT(*) FROM enhanced_memories WHERE created_at > datetime('now', '-24 hours')"
            )
            recent_memories = cursor.fetchone()[0]

            conn.close()
            return {
                "total_memories": total_memories,
                "total_clusters": total_clusters,
                "memory_by_type": memory_by_type,
                "recent_memories_24h": recent_memories,
            }

        return await asyncio.to_thread(_get_stats)

    # Compatibility methods for main assistant
    async def recall_memories(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Compatibility method - delegates to recall_with_clustering"""
        return await self.recall_with_clustering(query, limit=limit)

    async def store_memory(
        self, content: Any, context: Dict[str, Any], tags: List[str], importance: float
    ) -> str:
        """Compatibility method - delegates to store_enhanced_memory"""
        return await self.store_enhanced_memory(
            content=content,
            context=context,
            tags=tags,
            importance=importance,
        )

    async def search_memories(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Compatibility method for plugin system"""
        return await self.recall_memories(query, limit=limit)

    async def get_memories_by_tags(
        self, tags: List[str], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get memories filtered by tags"""

        def _query_by_tags():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Build query to search for tags in the tags field (stored as JSON)
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])

            cursor.execute(
                f"""
                SELECT *
                FROM enhanced_memories
                WHERE ({tag_conditions})
                ORDER BY importance DESC, last_accessed DESC
                LIMIT ?
                """,
                [f"%{tag}%" for tag in tags] + [limit],
            )

            rows = cursor.fetchall()
            conn.close()
            return rows

        rows = await asyncio.to_thread(_query_by_tags)
        memories = []
        for row in rows:
            memory_data = dict(row)
            memory_data["content"] = json.loads(memory_data["content"])
            memory_data["context"] = json.loads(memory_data["context"])
            memory_data["tags"] = (
                json.loads(memory_data["tags"]) if memory_data["tags"] else []
            )
            memories.append(memory_data)

        return memories

    async def get_memory_clusters(self) -> List[MemoryCluster]:
        """Get all memory clusters"""

        def _query_clusters():
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT c.*, GROUP_CONCAT(cm.memory_id) as memory_ids
                FROM memory_clusters c
                LEFT JOIN cluster_memories cm ON c.id = cm.cluster_id
                GROUP BY c.id
                ORDER BY c.last_accessed DESC
            """)

            rows = cursor.fetchall()
            conn.close()
            return rows

        rows = await asyncio.to_thread(_query_clusters)
        clusters = []
        for row in rows:
            cluster_data = dict(row)
            clusters.append(
                MemoryCluster(
                    id=cluster_data["id"],
                    name=cluster_data["name"],
                    description=cluster_data["description"],
                    memories=cluster_data["memory_ids"].split(",")
                    if cluster_data["memory_ids"]
                    else [],
                    center_vector=json.loads(cluster_data["center_vector"]),
                    creation_date=datetime.fromisoformat(cluster_data["creation_date"]),
                    last_accessed=datetime.fromisoformat(cluster_data["last_accessed"]),
                    access_count=cluster_data["access_count"],
                    tags=cluster_data["tags"].split(",")
                    if cluster_data["tags"]
                    else [],
                )
            )

        return clusters

    async def get_memory_timeline(self, days: int = 7) -> List[MemoryTimeline]:
        """Get memory timeline for the specified number of days"""
        return await self._generate_memory_timeline()

    def _generate_memory_id(
        self, content: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate unique memory ID based on content and context"""
        content_str = json.dumps(content, sort_keys=True)
        context_str = json.dumps(context or {}, sort_keys=True)
        combined = f"{content_str}:{context_str}:{datetime.now().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
