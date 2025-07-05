"""
🧠 AetherraCode Enhanced Memory System
Advanced memory architecture with vector embeddings and semantic search
"""

import hashlib
import json
import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

# Set up logging
logger = logging.getLogger(__name__)


class VectorMemorySystem:
    """Advanced memory system with vector embeddings and semantic search"""

    def __init__(self, data_dir: Path, embedding_dim: int = 384):
        self.data_dir = data_dir
        self.embedding_dim = embedding_dim

        # Memory storage files
        self.episodic_file = data_dir / "episodic_memory.json"
        self.semantic_file = data_dir / "semantic_memory.json"
        self.procedural_file = data_dir / "procedural_memory.json"
        self.vector_file = data_dir / "memory_vectors.pkl"
        self.index_file = data_dir / "memory_index.json"

        # Memory stores
        self.episodic_memories = []
        self.semantic_memories = {}
        self.procedural_memories = {}
        self.memory_vectors = {}
        self.memory_index = {}

        # Load existing memory
        self._load_all_memories()

        # Initialize embedding model (placeholder for actual embedding)
        self._init_embedding_model()

    def _init_embedding_model(self):
        """Initialize text embedding model for semantic memory"""
        # Placeholder for actual embedding model (e.g., sentence-transformers)
        logger.info("📊 Initializing memory embedding model...")

    def _load_all_memories(self):
        """Load all memory types from persistent storage"""
        # Load episodic memories
        if self.episodic_file.exists():
            try:
                with open(self.episodic_file) as f:
                    self.episodic_memories = json.load(f)
                logger.info(f"✓ Loaded {len(self.episodic_memories)} episodic memories")
            except Exception as e:
                logger.warning(f"Failed to load episodic memories: {e}")

        # Load semantic memories
        if self.semantic_file.exists():
            try:
                with open(self.semantic_file) as f:
                    self.semantic_memories = json.load(f)
                logger.info(f"✓ Loaded {len(self.semantic_memories)} semantic memories")
            except Exception as e:
                logger.warning(f"Failed to load semantic memories: {e}")

        # Load procedural memories
        if self.procedural_file.exists():
            try:
                with open(self.procedural_file) as f:
                    self.procedural_memories = json.load(f)
                logger.info(f"✓ Loaded {len(self.procedural_memories)} procedural memories")
            except Exception as e:
                logger.warning(f"Failed to load procedural memories: {e}")

        # Load memory vectors
        if self.vector_file.exists():
            try:
                with open(self.vector_file, "rb") as f:
                    self.memory_vectors = pickle.load(f)
                logger.info(f"✓ Loaded {len(self.memory_vectors)} memory vectors")
            except Exception as e:
                logger.warning(f"Failed to load memory vectors: {e}")

        # Load memory index
        if self.index_file.exists():
            try:
                with open(self.index_file) as f:
                    self.memory_index = json.load(f)
                logger.info(f"✓ Loaded memory index with {len(self.memory_index)} entries")
            except Exception as e:
                logger.warning(f"Failed to load memory index: {e}")

    def store_episodic_memory(self, event: str, context: Dict[str, Any], importance: float = 0.5):
        """Store episodic memory (what happened when)"""
        memory_id = self._generate_memory_id(event, context)

        episodic_memory = {
            "id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "context": context,
            "importance": importance,
            "recall_count": 0,
            "last_recalled": None,
        }

        self.episodic_memories.append(episodic_memory)

        # Generate and store vector embedding
        embedding = self._generate_embedding(f"{event} {json.dumps(context)}")
        self.memory_vectors[memory_id] = embedding

        # Update index
        self._update_memory_index(memory_id, "episodic", event, importance)

        logger.info(f"💾 Stored episodic memory: {event[:50]}...")

    def store_semantic_memory(
        self, concept: str, knowledge: Dict[str, Any], importance: float = 0.7
    ):
        """Store semantic memory (facts and knowledge)"""
        memory_id = self._generate_memory_id(concept, knowledge)

        semantic_memory = {
            "id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "concept": concept,
            "knowledge": knowledge,
            "importance": importance,
            "confidence": knowledge.get("confidence", 0.8),
            "source": knowledge.get("source", "user_interaction"),
            "last_updated": datetime.now().isoformat(),
        }

        self.semantic_memories[concept] = semantic_memory

        # Generate and store vector embedding
        embedding = self._generate_embedding(f"{concept} {json.dumps(knowledge)}")
        self.memory_vectors[memory_id] = embedding

        # Update index
        self._update_memory_index(memory_id, "semantic", concept, importance)

        logger.info(f"🧠 Stored semantic memory: {concept}")

    def store_procedural_memory(self, procedure: str, steps: List[str], success_rate: float = 1.0):
        """Store procedural memory (how to do things)"""
        memory_id = self._generate_memory_id(procedure, {"steps": steps})

        procedural_memory = {
            "id": memory_id,
            "timestamp": datetime.now().isoformat(),
            "procedure": procedure,
            "steps": steps,
            "success_rate": success_rate,
            "usage_count": 0,
            "last_used": None,
            "optimization_history": [],
        }

        self.procedural_memories[procedure] = procedural_memory

        # Generate and store vector embedding
        embedding = self._generate_embedding(f"{procedure} {' '.join(steps)}")
        self.memory_vectors[memory_id] = embedding

        # Update index
        self._update_memory_index(memory_id, "procedural", procedure, success_rate)

        logger.info(f"⚙️ Stored procedural memory: {procedure}")

    def semantic_search(self, query: str, limit: int = 10, memory_type: str = "all") -> List[Dict]:
        """Perform semantic search across memories"""
        if not self.memory_vectors:
            return []

        query_embedding = self._generate_embedding(query)
        similarities = []

        for memory_id, memory_vector in self.memory_vectors.items():
            # Filter by memory type if specified
            if memory_type != "all":
                index_entry = self.memory_index.get(memory_id, {})
                if index_entry.get("type") != memory_type:
                    continue

            similarity = self._cosine_similarity(query_embedding, memory_vector)
            similarities.append((memory_id, similarity))

        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x[1], reverse=True)

        results = []
        for memory_id, similarity in similarities[:limit]:
            memory = self._get_memory_by_id(memory_id)
            if memory:
                memory["similarity_score"] = similarity
                results.append(memory)

        logger.info(f"🔍 Semantic search for '{query}': {len(results)} results")
        return results

    def recall_by_importance(self, threshold: float = 0.7, limit: int = 20) -> List[Dict]:
        """Recall memories by importance threshold"""
        important_memories = []

        # Check episodic memories
        for memory in self.episodic_memories:
            if memory["importance"] >= threshold:
                important_memories.append(memory)

        # Check semantic memories
        for memory in self.semantic_memories.values():
            if memory["importance"] >= threshold:
                important_memories.append(memory)

        # Check procedural memories
        for memory in self.procedural_memories.values():
            if memory.get("success_rate", 0) >= threshold:
                important_memories.append(memory)

        # Sort by importance and timestamp
        important_memories.sort(
            key=lambda x: (x.get("importance", 0), x["timestamp"]), reverse=True
        )

        return important_memories[:limit]

    def get_recent_memories(self, hours: int = 24, memory_type: str = "all") -> List[Dict]:
        """Get recent memories within specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_memories = []

        if memory_type in ["all", "episodic"]:
            for memory in self.episodic_memories:
                memory_time = datetime.fromisoformat(memory["timestamp"])
                if memory_time > cutoff_time:
                    recent_memories.append(memory)

        if memory_type in ["all", "semantic"]:
            for memory in self.semantic_memories.values():
                memory_time = datetime.fromisoformat(memory["timestamp"])
                if memory_time > cutoff_time:
                    recent_memories.append(memory)

        if memory_type in ["all", "procedural"]:
            for memory in self.procedural_memories.values():
                memory_time = datetime.fromisoformat(memory["timestamp"])
                if memory_time > cutoff_time:
                    recent_memories.append(memory)

        # Sort by timestamp
        recent_memories.sort(key=lambda x: x["timestamp"], reverse=True)

        return recent_memories

    def consolidate_memories(self, threshold: float = 0.3):
        """Consolidate similar memories to prevent duplication"""
        logger.info("🔄 Starting memory consolidation...")

        consolidated_count = 0
        memory_groups = self._group_similar_memories(threshold)

        for group in memory_groups:
            if len(group) > 1:
                primary_memory = max(group, key=lambda x: x.get("importance", 0))
                for memory in group:
                    if memory["id"] != primary_memory["id"]:
                        self._merge_memory_into_primary(memory, primary_memory)
                        consolidated_count += 1

        logger.info(f"✓ Consolidated {consolidated_count} memories")

    def forget_low_importance_memories(self, threshold: float = 0.2, max_age_days: int = 30):
        """Forget memories with low importance after certain age"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        forgotten_count = 0

        # Process episodic memories
        self.episodic_memories = [
            memory
            for memory in self.episodic_memories
            if not (
                memory["importance"] < threshold
                and datetime.fromisoformat(memory["timestamp"]) < cutoff_date
            )
        ]

        # Process semantic memories (keep most semantic knowledge)
        forgotten_semantic = []
        for concept, memory in list(self.semantic_memories.items()):
            if (
                memory["importance"] < threshold
                and datetime.fromisoformat(memory["timestamp"]) < cutoff_date
                and memory.get("confidence", 1.0) < 0.5
            ):
                forgotten_semantic.append(concept)
                forgotten_count += 1

        for concept in forgotten_semantic:
            del self.semantic_memories[concept]

        logger.info(f"🗑️ Forgot {forgotten_count} low-importance memories")

    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        total_memories = (
            len(self.episodic_memories)
            + len(self.semantic_memories)
            + len(self.procedural_memories)
        )

        # Calculate average importance
        all_importances = []
        for memory in self.episodic_memories:
            all_importances.append(memory["importance"])
        for memory in self.semantic_memories.values():
            all_importances.append(memory["importance"])
        for memory in self.procedural_memories.values():
            all_importances.append(memory.get("success_rate", 0.5))

        avg_importance = np.mean(all_importances) if all_importances else 0

        # Calculate memory age distribution
        now = datetime.now()
        age_distribution = {"recent": 0, "medium": 0, "old": 0}

        for memory in (
            self.episodic_memories
            + list(self.semantic_memories.values())
            + list(self.procedural_memories.values())
        ):
            memory_age = now - datetime.fromisoformat(memory["timestamp"])
            if memory_age.days < 7:
                age_distribution["recent"] += 1
            elif memory_age.days < 30:
                age_distribution["medium"] += 1
            else:
                age_distribution["old"] += 1

        return {
            "total_memories": total_memories,
            "episodic_count": len(self.episodic_memories),
            "semantic_count": len(self.semantic_memories),
            "procedural_count": len(self.procedural_memories),
            "vector_count": len(self.memory_vectors),
            "average_importance": avg_importance,
            "age_distribution": age_distribution,
            "memory_size_mb": self._calculate_memory_size(),
        }

    def save_all_memories(self):
        """Save all memories to persistent storage"""
        # Save episodic memories
        with open(self.episodic_file, "w") as f:
            json.dump(self.episodic_memories, f, indent=2)

        # Save semantic memories
        with open(self.semantic_file, "w") as f:
            json.dump(self.semantic_memories, f, indent=2)

        # Save procedural memories
        with open(self.procedural_file, "w") as f:
            json.dump(self.procedural_memories, f, indent=2)

        # Save memory vectors
        with open(self.vector_file, "wb") as f:
            pickle.dump(self.memory_vectors, f)

        # Save memory index
        with open(self.index_file, "w") as f:
            json.dump(self.memory_index, f, indent=2)

        logger.info("💾 All memories saved to persistent storage")

    def _generate_memory_id(self, content: str, context: Dict) -> str:
        """Generate unique ID for memory"""
        content_str = f"{content}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content_str.encode()).hexdigest()

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate vector embedding for text (placeholder implementation)"""
        # This is a simple placeholder - in production, use sentence-transformers or similar
        # For now, create a simple hash-based embedding
        text_hash = hashlib.sha256(text.encode()).hexdigest()

        # Convert hash to numerical vector
        embedding = np.array(
            [
                int(text_hash[i : i + 8], 16) % 1000 / 1000.0
                for i in range(0, min(len(text_hash), self.embedding_dim * 8), 8)
            ]
        )

        # Pad or truncate to desired dimension
        if len(embedding) < self.embedding_dim:
            embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
        else:
            embedding = embedding[: self.embedding_dim]

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        if norm_product == 0:
            return 0.0
        return dot_product / norm_product

    def _update_memory_index(
        self, memory_id: str, memory_type: str, content: str, importance: float
    ):
        """Update the memory index for fast lookup"""
        self.memory_index[memory_id] = {
            "type": memory_type,
            "content_preview": content[:100],
            "importance": importance,
            "timestamp": datetime.now().isoformat(),
        }

    def _get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get memory by ID from any memory store"""
        # Check episodic memories
        for memory in self.episodic_memories:
            if memory["id"] == memory_id:
                return memory

        # Check semantic memories
        for memory in self.semantic_memories.values():
            if memory["id"] == memory_id:
                return memory

        # Check procedural memories
        for memory in self.procedural_memories.values():
            if memory["id"] == memory_id:
                return memory

        return None

    def _group_similar_memories(self, threshold: float) -> List[List[Dict]]:
        """Group similar memories for consolidation"""
        # Placeholder implementation
        return []

    def _merge_memory_into_primary(self, secondary_memory: Dict, primary_memory: Dict):
        """Merge secondary memory into primary memory"""
        # Placeholder implementation
        pass

    def _calculate_memory_size(self) -> float:
        """Calculate total memory size in MB"""
        total_size = 0

        # Approximate JSON sizes
        total_size += len(json.dumps(self.episodic_memories).encode())
        total_size += len(json.dumps(self.semantic_memories).encode())
        total_size += len(json.dumps(self.procedural_memories).encode())

        # Vector size
        if self.memory_vectors:
            vector_size = sum(v.nbytes for v in self.memory_vectors.values())
            total_size += vector_size

        return total_size / (1024 * 1024)  # Convert to MB


class GoalTrackingSystem:
    """Advanced goal tracking and achievement system"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.goals_file = data_dir / "goal_tracking.json"

        self.active_goals = []
        self.completed_goals = []
        self.paused_goals = []

        self._load_goals()

    def create_goal(
        self, description: str, priority: str = "medium", deadline: Optional[str] = None
    ) -> str:
        """Create a new goal"""
        goal_id = self._generate_goal_id(description)

        goal = {
            "id": goal_id,
            "description": description,
            "priority": priority,  # low, medium, high, critical
            "status": "active",
            "created": datetime.now().isoformat(),
            "deadline": deadline,
            "progress": 0.0,
            "milestones": [],
            "actions_taken": [],
            "obstacles": [],
            "insights": [],
        }

        self.active_goals.append(goal)
        logger.info(f"🎯 Created goal: {description}")

        return goal_id

    def update_goal_progress(self, goal_id: str, progress: float, note: str = ""):
        """Update progress on a goal"""
        goal = self._find_goal_by_id(goal_id)
        if goal:
            old_progress = goal["progress"]
            goal["progress"] = max(0.0, min(1.0, progress))
            goal["last_updated"] = datetime.now().isoformat()

            if note:
                goal["actions_taken"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "note": note,
                        "progress_change": progress - old_progress,
                    }
                )

            logger.info(f"📈 Updated goal progress: {goal['description'][:50]}... ({progress:.1%})")

            # Check if goal is completed
            if progress >= 1.0:
                self._complete_goal(goal_id)

    def add_goal_milestone(self, goal_id: str, milestone: str, target_date: Optional[str] = None):
        """Add a milestone to a goal"""
        goal = self._find_goal_by_id(goal_id)
        if goal:
            milestone_entry = {
                "description": milestone,
                "target_date": target_date,
                "completed": False,
                "created": datetime.now().isoformat(),
            }
            goal["milestones"].append(milestone_entry)
            logger.info(f"🏁 Added milestone to goal: {milestone}")

    def record_goal_obstacle(self, goal_id: str, obstacle: str, severity: str = "medium"):
        """Record an obstacle encountered while pursuing a goal"""
        goal = self._find_goal_by_id(goal_id)
        if goal:
            obstacle_entry = {
                "description": obstacle,
                "severity": severity,
                "timestamp": datetime.now().isoformat(),
                "resolved": False,
            }
            goal["obstacles"].append(obstacle_entry)
            logger.info(f"⚠️ Recorded obstacle: {obstacle}")

    def get_goal_recommendations(self) -> List[Dict]:
        """Get AI recommendations for goal achievement"""
        recommendations = []

        for goal in self.active_goals:
            # Analyze goal progress and suggest actions
            if goal["progress"] < 0.3 and len(goal["actions_taken"]) == 0:
                recommendations.append(
                    {
                        "goal_id": goal["id"],
                        "type": "start_action",
                        "message": f"Consider breaking down '{goal['description']}' into smaller actionable steps",
                    }
                )

            elif goal["progress"] > 0.5 and not goal["milestones"]:
                recommendations.append(
                    {
                        "goal_id": goal["id"],
                        "type": "add_milestones",
                        "message": f"Add milestones to track progress on '{goal['description']}'",
                    }
                )

            # Check for stalled goals
            if goal.get("last_updated"):
                last_update = datetime.fromisoformat(goal["last_updated"])
                if datetime.now() - last_update > timedelta(days=7):
                    recommendations.append(
                        {
                            "goal_id": goal["id"],
                            "type": "stalled_goal",
                            "message": f"Goal '{goal['description']}' hasn't been updated in a week",
                        }
                    )

        return recommendations

    def _complete_goal(self, goal_id: str):
        """Mark a goal as completed"""
        goal = self._find_goal_by_id(goal_id)
        if goal:
            goal["status"] = "completed"
            goal["completed_date"] = datetime.now().isoformat()

            # Move to completed goals
            self.active_goals.remove(goal)
            self.completed_goals.append(goal)

            logger.info(f"🎉 Goal completed: {goal['description']}")

    def _find_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Find goal by ID in all goal lists"""
        for goal in self.active_goals + self.completed_goals + self.paused_goals:
            if goal["id"] == goal_id:
                return goal
        return None

    def _generate_goal_id(self, description: str) -> str:
        """Generate unique goal ID"""
        return hashlib.md5(f"{description}_{datetime.now()}".encode()).hexdigest()[:8]

    def _load_goals(self):
        """Load goals from persistent storage"""
        if self.goals_file.exists():
            try:
                with open(self.goals_file) as f:
                    goal_data = json.load(f)
                    self.active_goals = goal_data.get("active", [])
                    self.completed_goals = goal_data.get("completed", [])
                    self.paused_goals = goal_data.get("paused", [])
                logger.info(f"✓ Loaded {len(self.active_goals)} active goals")
            except Exception as e:
                logger.warning(f"Failed to load goals: {e}")

    def save_goals(self):
        """Save goals to persistent storage"""
        goal_data = {
            "active": self.active_goals,
            "completed": self.completed_goals,
            "paused": self.paused_goals,
            "last_save": datetime.now().isoformat(),
        }

        with open(self.goals_file, "w") as f:
            json.dump(goal_data, f, indent=2)

        logger.info("💾 Goals saved to persistent storage")

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Get all active goals"""
        return self.active_goals

    def add_goal_context(self, goal_id: str, context: Dict[str, Any]):
        """Add context to a goal"""
        goal = self._find_goal_by_id(goal_id)
        if goal:
            if "context" not in goal:
                goal["context"] = []
            goal["context"].append({"data": context, "timestamp": datetime.now().isoformat()})

    def get_completed_goals(self) -> List[Dict[str, Any]]:
        """Get all completed goals"""
        return self.completed_goals

    def get_goal_by_id(self, goal_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific goal by ID"""
        return self._find_goal_by_id(goal_id)


# Example usage
if __name__ == "__main__":
    print("🧠 AetherraCode Enhanced Memory System - Demonstration")

    # Initialize memory system
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    memory_system = VectorMemorySystem(data_dir)
    goal_system = GoalTrackingSystem(data_dir)

    # Store some example memories
    memory_system.store_episodic_memory(
        "User completed Python tutorial",
        {"duration": "2 hours", "success": True, "topics": ["variables", "functions"]},
        importance=0.8,
    )

    memory_system.store_semantic_memory(
        "Python best practices",
        {"use_type_hints": True, "follow_pep8": True, "write_docstrings": True},
        importance=0.9,
    )

    memory_system.store_procedural_memory(
        "Debug Python code",
        ["Read error message", "Check syntax", "Add print statements", "Use debugger"],
        success_rate=0.85,
    )

    # Create a goal
    goal_id = goal_system.create_goal("Learn advanced Python concepts", "high", "2025-07-30")
    goal_system.update_goal_progress(goal_id, 0.3, "Completed decorators tutorial")

    # Perform semantic search
    results = memory_system.semantic_search("Python programming help")
    print(f"\n🔍 Found {len(results)} relevant memories for 'Python programming help'")

    # Get memory statistics
    stats = memory_system.get_memory_statistics()
    print("\n📊 Memory Statistics:")
    print(f"Total memories: {stats['total_memories']}")
    print(f"Average importance: {stats['average_importance']:.2f}")
    print(f"Memory size: {stats['memory_size_mb']:.2f} MB")

    # Save everything
    memory_system.save_all_memories()
    goal_system.save_goals()

    print("\n✅ Enhanced memory system demonstration complete!")
