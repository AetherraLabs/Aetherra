#!/usr/bin/env python3
"""
🚀 AETHERRA QFAC Phase 3: Observer-Aware Compression (Cognitive Collapsing)
============================================================================

Observer Effect Simulator - Memory fidelity changes when accessed.
Implements cognitive collapsing mechanisms with observer-dependent rendering.

Core Features:
• Observer-dependent memory mutation
• Layered access model (Surface/Core/Deep)
• Observer profiles with different impact levels
• Memory decay and sharpening based on access patterns
• Meta-memory tracking (memory of how memory was remembered)
"""

import json
import sqlite3
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .fractal_encoder import FractalEncoder, FractalNode


class ObserverType(Enum):
    """Different types of observers with varying impact levels"""

    LYRIXA = "lyrixa"  # Highest impact - sharp, detailed access
    USER = "user"  # Medium impact - focused access
    PLUGIN = "plugin"  # Low impact - limited access
    SYSTEM = "system"  # Minimal impact - maintenance access


class AccessLayer(Enum):
    """Different layers of memory access depth"""

    SURFACE = "surface"  # Summary + emotional tag
    CORE = "core"  # Compressed raw data
    DEEP = "deep"  # Full high-fidelity reconstruction


@dataclass
class ObserverProfile:
    """Defines how an observer affects memory during access"""

    observer_id: str
    observer_type: ObserverType
    impact_strength: float  # 0.0 - 1.0, how much access changes memory
    sharpening_factor: float  # How much accessed memories improve
    decay_factor: float  # How much unaccessed memories degrade
    access_permissions: Set[AccessLayer]
    collapse_threshold: float  # When to trigger cognitive collapse


@dataclass
class MemoryAccess:
    """Records a single memory access event"""

    access_id: str
    memory_node_id: str
    observer_profile: ObserverProfile
    access_layer: AccessLayer
    timestamp: float
    collapse_strength: float  # Impact of this access on memory
    fidelity_before: float
    fidelity_after: float
    meta_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LayeredMemoryView:
    """Represents memory at different access layers"""

    node_id: str
    surface_layer: Dict[str, Any]  # Summary + emotional tags
    core_layer: Dict[str, Any]  # Compressed raw data
    deep_layer: Dict[str, Any]  # Full reconstruction
    current_fidelity: float
    access_count: int
    last_accessed: float


@dataclass
class MetaMemory:
    """Memory of how a memory was remembered"""

    meta_id: str
    original_memory_id: str
    access_pattern: List[MemoryAccess]
    reconstruction_history: List[Dict[str, Any]]
    observer_influence_map: Dict[str, float]
    cognitive_drift: float  # How much memory has changed over time
    emergence_patterns: List[str]  # New patterns that emerged from access


class ObserverEffectSimulator:
    """
    🧠 Core simulator for observer-aware memory compression

    Implements the quantum-inspired observer effect where memory
    fidelity and content changes based on who accesses it and how.
    """

    def __init__(self, fractal_encoder: FractalEncoder, data_dir: str):
        self.fractal_encoder = fractal_encoder
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Database setup
        self.db_path = self.data_dir / "observer_effects.db"
        self.meta_db_path = self.data_dir / "meta_memory.db"

        # Observer profiles registry
        self.observer_profiles: Dict[str, ObserverProfile] = {}

        # Memory state tracking
        self.memory_states: Dict[str, LayeredMemoryView] = {}
        self.access_history: List[MemoryAccess] = []

        # Default observer profiles
        self._create_default_profiles()

        print("🧠 ObserverEffectSimulator initialized")
        print(f"   📁 Data directory: {self.data_dir}")
        print(f"   🗃️ Database: {self.db_path}")
        print(f"   🧠 Meta-memory DB: {self.meta_db_path}")
        print(f"   👁️ Observer profiles: {len(self.observer_profiles)}")

    async def initialize_databases(self):
        """Initialize observer effect and meta-memory databases"""
        await self._init_observer_db()
        await self._init_meta_memory_db()
        print("   📋 Observer effect databases initialized")

    async def _init_observer_db(self):
        """Initialize observer effects database"""
        conn = sqlite3.connect(self.db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_accesses (
                access_id TEXT PRIMARY KEY,
                memory_node_id TEXT NOT NULL,
                observer_id TEXT NOT NULL,
                observer_type TEXT NOT NULL,
                access_layer TEXT NOT NULL,
                timestamp REAL NOT NULL,
                collapse_strength REAL NOT NULL,
                fidelity_before REAL NOT NULL,
                fidelity_after REAL NOT NULL,
                meta_context TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS layered_memory_views (
                node_id TEXT PRIMARY KEY,
                surface_layer TEXT NOT NULL,
                core_layer TEXT NOT NULL,
                deep_layer TEXT NOT NULL,
                current_fidelity REAL NOT NULL,
                access_count INTEGER NOT NULL,
                last_accessed REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS observer_profiles (
                observer_id TEXT PRIMARY KEY,
                observer_type TEXT NOT NULL,
                impact_strength REAL NOT NULL,
                sharpening_factor REAL NOT NULL,
                decay_factor REAL NOT NULL,
                access_permissions TEXT NOT NULL,
                collapse_threshold REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    async def _init_meta_memory_db(self):
        """Initialize meta-memory database"""
        conn = sqlite3.connect(self.meta_db_path)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS meta_memories (
                meta_id TEXT PRIMARY KEY,
                original_memory_id TEXT NOT NULL,
                access_pattern TEXT NOT NULL,
                reconstruction_history TEXT NOT NULL,
                observer_influence_map TEXT NOT NULL,
                cognitive_drift REAL NOT NULL,
                emergence_patterns TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def _create_default_profiles(self):
        """Create default observer profiles"""
        self.observer_profiles = {
            "lyrixa_core": ObserverProfile(
                observer_id="lyrixa_core",
                observer_type=ObserverType.LYRIXA,
                impact_strength=0.9,
                sharpening_factor=0.8,
                decay_factor=0.1,
                access_permissions={
                    AccessLayer.SURFACE,
                    AccessLayer.CORE,
                    AccessLayer.DEEP,
                },
                collapse_threshold=0.7,
            ),
            "user_interactive": ObserverProfile(
                observer_id="user_interactive",
                observer_type=ObserverType.USER,
                impact_strength=0.6,
                sharpening_factor=0.5,
                decay_factor=0.2,
                access_permissions={AccessLayer.SURFACE, AccessLayer.CORE},
                collapse_threshold=0.5,
            ),
            "plugin_system": ObserverProfile(
                observer_id="plugin_system",
                observer_type=ObserverType.PLUGIN,
                impact_strength=0.3,
                sharpening_factor=0.2,
                decay_factor=0.05,
                access_permissions={AccessLayer.SURFACE},
                collapse_threshold=0.3,
            ),
            "system_maintenance": ObserverProfile(
                observer_id="system_maintenance",
                observer_type=ObserverType.SYSTEM,
                impact_strength=0.1,
                sharpening_factor=0.05,
                decay_factor=0.02,
                access_permissions={AccessLayer.SURFACE},
                collapse_threshold=0.8,
            ),
        }

    async def access_memory(
        self,
        memory_node_id: str,
        observer_id: str,
        access_layer: AccessLayer = AccessLayer.SURFACE,
        context: Optional[Dict[str, Any]] = None,
    ) -> LayeredMemoryView:
        """
        🎭 Access memory with observer effect simulation

        This is the core method where the observer effect occurs:
        1. Memory fidelity changes based on observer
        2. Layered access affects depth of change
        3. Meta-memory tracks how memory was accessed
        """
        if observer_id not in self.observer_profiles:
            raise ValueError(f"Unknown observer: {observer_id}")

        observer_profile = self.observer_profiles[observer_id]

        # Check access permissions
        if access_layer not in observer_profile.access_permissions:
            raise PermissionError(
                f"Observer {observer_id} cannot access {access_layer.value} layer"
            )

        # Get or create layered memory view
        memory_view = await self._get_or_create_memory_view(memory_node_id)

        # Calculate observer impact
        collapse_strength = await self._calculate_collapse_strength(
            memory_view, observer_profile, access_layer, context
        )

        # Apply observer effect
        fidelity_before = memory_view.current_fidelity
        memory_view = await self._apply_observer_effect(
            memory_view, observer_profile, collapse_strength, access_layer
        )
        fidelity_after = memory_view.current_fidelity

        # Record access
        access_record = MemoryAccess(
            access_id=f"access_{int(time.time() * 1000)}_{observer_id}",
            memory_node_id=memory_node_id,
            observer_profile=observer_profile,
            access_layer=access_layer,
            timestamp=time.time(),
            collapse_strength=collapse_strength,
            fidelity_before=fidelity_before,
            fidelity_after=fidelity_after,
            meta_context=context or {},
        )

        # Store access and update memory
        await self._store_access_record(access_record)
        await self._update_memory_view(memory_view)

        # Update meta-memory
        await self._update_meta_memory(memory_node_id, access_record)

        print(f"👁️ Memory accessed: {memory_node_id}")
        print(f"   🎭 Observer: {observer_id} ({observer_profile.observer_type.value})")
        print(f"   📊 Layer: {access_layer.value}")
        print(f"   💪 Collapse strength: {collapse_strength:.3f}")
        print(f"   📈 Fidelity: {fidelity_before:.3f} → {fidelity_after:.3f}")

        return memory_view

    async def _get_or_create_memory_view(
        self, memory_node_id: str
    ) -> LayeredMemoryView:
        """Get existing memory view or create new layered view"""
        if memory_node_id in self.memory_states:
            return self.memory_states[memory_node_id]

        # Try to load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM layered_memory_views WHERE node_id = ?", (memory_node_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            memory_view = LayeredMemoryView(
                node_id=row[0],
                surface_layer=json.loads(row[1]),
                core_layer=json.loads(row[2]),
                deep_layer=json.loads(row[3]),
                current_fidelity=row[4],
                access_count=row[5],
                last_accessed=row[6],
            )
            self.memory_states[memory_node_id] = memory_view
            return memory_view

        # Create new memory view from fractal encoder
        fractal_node = await self._load_fractal_node(memory_node_id)
        if not fractal_node:
            raise ValueError(f"Memory node not found: {memory_node_id}")

        # Create layered representation
        memory_view = await self._create_layered_view(fractal_node)
        self.memory_states[memory_node_id] = memory_view

        return memory_view

    async def _load_fractal_node(self, node_id: str) -> Optional[FractalNode]:
        """Load fractal node from encoder database"""
        # Access the fractal encoder's database directly
        conn = sqlite3.connect(self.fractal_encoder.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fractal_nodes WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Parse node data (same structure as in FractalEncoder.reconstruct_memory)
        return FractalNode(
            node_id=row[0],
            content=json.loads(row[1]),
            pattern_refs=json.loads(row[2]),
            fractal_depth=row[3],
            compression_seeds=json.loads(row[4]),
            reconstruction_rules=json.loads(row[5]),
            similarity_map=json.loads(row[6]),
            access_frequency=row[7],
            created_at=row[8],
            last_accessed=row[9],
        )

    async def _create_layered_view(
        self, fractal_node: FractalNode
    ) -> LayeredMemoryView:
        """Create layered memory view from fractal node"""
        # Reconstruct full memory
        full_memory = await self.fractal_encoder.reconstruct_memory(
            fractal_node.node_id
        )

        # Create surface layer (summary + emotional tags)
        surface_layer = await self._extract_surface_layer(full_memory, fractal_node)

        # Create core layer (compressed raw)
        core_layer = await self._extract_core_layer(full_memory, fractal_node)

        # Deep layer is full reconstruction
        deep_layer = {
            "full_content": full_memory,
            "fractal_patterns": fractal_node.pattern_refs,
            "reconstruction_rules": fractal_node.reconstruction_rules,
            "compression_seeds": fractal_node.compression_seeds,
        }

        return LayeredMemoryView(
            node_id=fractal_node.node_id,
            surface_layer=surface_layer,
            core_layer=core_layer,
            deep_layer=deep_layer,
            current_fidelity=1.0,  # Start with perfect fidelity
            access_count=0,
            last_accessed=time.time(),
        )

    async def _extract_surface_layer(
        self, memory: Any, fractal_node: FractalNode
    ) -> Dict[str, Any]:
        """Extract surface layer: summary + emotional tags"""
        summary = await self._generate_memory_summary(memory)
        emotional_tags = await self._extract_emotional_tags(memory)

        return {
            "summary": summary,
            "emotional_tags": emotional_tags,
            "node_id": fractal_node.node_id,
            "fractal_depth": fractal_node.fractal_depth,
            "pattern_count": len(fractal_node.pattern_refs),
        }

    async def _extract_core_layer(
        self, memory: Any, fractal_node: FractalNode
    ) -> Dict[str, Any]:
        """Extract core layer: compressed raw data"""
        return {
            "compressed_content": await self._compress_content(memory),
            "pattern_references": fractal_node.pattern_refs[:5],  # Top 5 patterns
            "key_metadata": {
                "type": type(memory).__name__,
                "size": len(str(memory)),
                "complexity": fractal_node.fractal_depth,
            },
            "reconstruction_hints": fractal_node.compression_seeds[:3],
        }

    async def _generate_memory_summary(self, memory: Any) -> str:
        """Generate brief summary of memory content"""
        content_str = str(memory)
        if len(content_str) <= 100:
            return content_str

        # Extract key phrases and concepts
        words = content_str.split()
        if len(words) <= 20:
            return content_str

        # Simple extractive summary (first part + key terms)
        summary_parts = words[:10] + ["..."] + words[-5:]
        return " ".join(summary_parts)

    async def _extract_emotional_tags(self, memory: Any) -> List[str]:
        """Extract emotional context from memory"""
        content_str = str(memory).lower()

        # Simple emotion detection based on keywords
        emotion_keywords = {
            "positive": ["good", "great", "happy", "success", "excellent", "amazing"],
            "negative": ["bad", "error", "fail", "problem", "issue", "wrong"],
            "neutral": ["information", "data", "process", "system", "function"],
            "curiosity": ["question", "wonder", "explore", "discover", "learn"],
            "confidence": ["certain", "sure", "confident", "know", "understand"],
        }

        tags = []
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in content_str for keyword in keywords):
                tags.append(emotion)

        return tags if tags else ["neutral"]

    async def _compress_content(self, memory: Any) -> str:
        """Create compressed representation of content"""
        content_str = str(memory)

        # Simple compression: key terms + structure markers
        if isinstance(memory, dict):
            keys = list(memory.keys())
            return f"dict[{', '.join(keys[:5])}{'...' if len(keys) > 5 else ''}]"
        elif isinstance(memory, list):
            return f"list[{len(memory)} items]"
        else:
            # Text compression: first/last words + length
            words = content_str.split()
            if len(words) <= 10:
                return content_str

            return (
                f"{' '.join(words[:3])}...{' '.join(words[-3:])} [{len(words)} words]"
            )

    async def _calculate_collapse_strength(
        self,
        memory_view: LayeredMemoryView,
        observer_profile: ObserverProfile,
        access_layer: AccessLayer,
        context: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate how strongly this access affects memory"""
        base_strength = observer_profile.impact_strength

        # Layer-based modifiers
        layer_multipliers = {
            AccessLayer.SURFACE: 0.3,
            AccessLayer.CORE: 0.7,
            AccessLayer.DEEP: 1.0,
        }

        layer_strength = base_strength * layer_multipliers[access_layer]

        # Access frequency modifier (more accesses = less impact)
        frequency_modifier = 1.0 / (1.0 + memory_view.access_count * 0.1)

        # Time decay modifier (recent accesses have more impact)
        time_since_access = time.time() - memory_view.last_accessed
        time_modifier = 1.0 / (1.0 + time_since_access / 3600)  # Decay over hours

        # Context-based modifiers
        context_modifier = 1.0
        if context:
            if context.get("intent") == "detailed_analysis":
                context_modifier = 1.5
            elif context.get("intent") == "quick_lookup":
                context_modifier = 0.5

        collapse_strength = (
            layer_strength * frequency_modifier * time_modifier * context_modifier
        )

        # Clamp to valid range
        return max(0.0, min(1.0, collapse_strength))

    async def _apply_observer_effect(
        self,
        memory_view: LayeredMemoryView,
        observer_profile: ObserverProfile,
        collapse_strength: float,
        access_layer: AccessLayer,
    ) -> LayeredMemoryView:
        """Apply observer effect to memory view"""
        # Update access statistics
        memory_view.access_count += 1
        memory_view.last_accessed = time.time()

        # Apply fidelity changes based on observer effect
        fidelity_change = 0.0

        if collapse_strength > observer_profile.collapse_threshold:
            # Strong access - memory becomes sharper
            fidelity_change = observer_profile.sharpening_factor * collapse_strength
            memory_view.current_fidelity = min(
                1.0, memory_view.current_fidelity + fidelity_change
            )
        else:
            # Weak access - slight degradation
            fidelity_change = -observer_profile.decay_factor * (1.0 - collapse_strength)
            memory_view.current_fidelity = max(
                0.1, memory_view.current_fidelity + fidelity_change
            )

        # Modify content based on access layer and fidelity
        if access_layer == AccessLayer.DEEP and memory_view.current_fidelity > 0.8:
            # High-fidelity deep access might enhance details
            await self._enhance_deep_layer(memory_view, observer_profile)

        return memory_view

    async def _enhance_deep_layer(
        self, memory_view: LayeredMemoryView, observer_profile: ObserverProfile
    ):
        """Enhance deep layer content based on high-fidelity access"""
        if observer_profile.observer_type == ObserverType.LYRIXA:
            # Lyrixa access enhances pattern recognition
            enhanced_patterns = memory_view.deep_layer.get("fractal_patterns", [])
            if len(enhanced_patterns) > 0:
                memory_view.deep_layer["enhanced_patterns"] = enhanced_patterns
                memory_view.deep_layer["lyrixa_insights"] = [
                    f"Pattern {i}: Enhanced recognition"
                    for i in range(min(3, len(enhanced_patterns)))
                ]

    async def _store_access_record(self, access_record: MemoryAccess):
        """Store memory access record in database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO memory_accesses
               (access_id, memory_node_id, observer_id, observer_type, access_layer,
                timestamp, collapse_strength, fidelity_before, fidelity_after, meta_context)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                access_record.access_id,
                access_record.memory_node_id,
                access_record.observer_profile.observer_id,
                access_record.observer_profile.observer_type.value,
                access_record.access_layer.value,
                access_record.timestamp,
                access_record.collapse_strength,
                access_record.fidelity_before,
                access_record.fidelity_after,
                json.dumps(access_record.meta_context),
            ),
        )
        conn.commit()
        conn.close()

    async def _update_memory_view(self, memory_view: LayeredMemoryView):
        """Update memory view in database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """INSERT OR REPLACE INTO layered_memory_views
               (node_id, surface_layer, core_layer, deep_layer, current_fidelity, access_count, last_accessed)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                memory_view.node_id,
                json.dumps(memory_view.surface_layer),
                json.dumps(memory_view.core_layer),
                json.dumps(memory_view.deep_layer),
                memory_view.current_fidelity,
                memory_view.access_count,
                memory_view.last_accessed,
            ),
        )
        conn.commit()
        conn.close()

    async def _update_meta_memory(
        self, memory_node_id: str, access_record: MemoryAccess
    ):
        """Update meta-memory tracking"""
        meta_memory = await self._get_or_create_meta_memory(memory_node_id)

        # Add access to pattern
        meta_memory.access_pattern.append(access_record)

        # Update observer influence
        observer_id = access_record.observer_profile.observer_id
        if observer_id not in meta_memory.observer_influence_map:
            meta_memory.observer_influence_map[observer_id] = 0.0

        meta_memory.observer_influence_map[observer_id] += (
            access_record.collapse_strength
        )

        # Calculate cognitive drift
        if len(meta_memory.access_pattern) > 1:
            recent_fidelity = meta_memory.access_pattern[-1].fidelity_after
            initial_fidelity = meta_memory.access_pattern[0].fidelity_before
            meta_memory.cognitive_drift = abs(recent_fidelity - initial_fidelity)

        # Store updated meta-memory
        await self._store_meta_memory(meta_memory)

    async def _get_or_create_meta_memory(self, memory_node_id: str) -> MetaMemory:
        """Get existing meta-memory or create new one"""
        # Try to load from database
        conn = sqlite3.connect(self.meta_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM meta_memories WHERE original_memory_id = ?",
            (memory_node_id,),
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            # Convert access pattern from JSON back to MemoryAccess objects
            access_pattern_data = json.loads(row[2])
            access_pattern = []
            for access_data in access_pattern_data:
                # Reconstruct observer profile
                observer_profile = ObserverProfile(
                    observer_id=access_data["observer_id"],
                    observer_type=ObserverType(access_data["observer_type"]),
                    impact_strength=0.0,  # Will be filled from profiles
                    sharpening_factor=0.0,
                    decay_factor=0.0,
                    access_permissions=set(),
                    collapse_threshold=0.0,
                )

                # Create MemoryAccess object
                memory_access = MemoryAccess(
                    access_id=access_data["access_id"],
                    memory_node_id=memory_node_id,
                    observer_profile=observer_profile,
                    access_layer=AccessLayer(access_data["access_layer"]),
                    timestamp=access_data["timestamp"],
                    collapse_strength=access_data["collapse_strength"],
                    fidelity_before=access_data["fidelity_before"],
                    fidelity_after=access_data["fidelity_after"],
                    meta_context={},
                )
                access_pattern.append(memory_access)

            return MetaMemory(
                meta_id=row[0],
                original_memory_id=row[1],
                access_pattern=access_pattern,
                reconstruction_history=json.loads(row[3]),
                observer_influence_map=json.loads(row[4]),
                cognitive_drift=row[5],
                emergence_patterns=json.loads(row[6]),
            )

        # Create new meta-memory
        return MetaMemory(
            meta_id=f"meta_{memory_node_id}_{int(time.time())}",
            original_memory_id=memory_node_id,
            access_pattern=[],
            reconstruction_history=[],
            observer_influence_map={},
            cognitive_drift=0.0,
            emergence_patterns=[],
        )

    async def _store_meta_memory(self, meta_memory: MetaMemory):
        """Store meta-memory in database"""
        # Convert access pattern to JSON-serializable format
        access_pattern_data = []
        for access in meta_memory.access_pattern:
            access_data = {
                "access_id": access.access_id,
                "timestamp": access.timestamp,
                "observer_id": access.observer_profile.observer_id,
                "observer_type": access.observer_profile.observer_type.value,
                "access_layer": access.access_layer.value,
                "collapse_strength": access.collapse_strength,
                "fidelity_before": access.fidelity_before,
                "fidelity_after": access.fidelity_after,
            }
            access_pattern_data.append(access_data)

        conn = sqlite3.connect(self.meta_db_path)
        conn.execute(
            """INSERT OR REPLACE INTO meta_memories
               (meta_id, original_memory_id, access_pattern, reconstruction_history,
                observer_influence_map, cognitive_drift, emergence_patterns, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                meta_memory.meta_id,
                meta_memory.original_memory_id,
                json.dumps(access_pattern_data),
                json.dumps(meta_memory.reconstruction_history),
                json.dumps(meta_memory.observer_influence_map),
                meta_memory.cognitive_drift,
                json.dumps(meta_memory.emergence_patterns),
                time.time(),
            ),
        )
        conn.commit()
        conn.close()

    async def get_observer_impact_statistics(self) -> Dict[str, Any]:
        """Get statistics about observer effects across all memories"""
        conn = sqlite3.connect(self.db_path)

        # Access frequency by observer type
        cursor = conn.cursor()
        cursor.execute(
            "SELECT observer_type, COUNT(*), AVG(collapse_strength) FROM memory_accesses GROUP BY observer_type"
        )
        observer_stats = cursor.fetchall()

        # Fidelity drift statistics
        cursor.execute(
            "SELECT AVG(fidelity_after - fidelity_before) as avg_drift FROM memory_accesses"
        )
        drift_result = cursor.fetchone()
        avg_fidelity_drift = (
            drift_result[0] if drift_result and drift_result[0] else 0.0
        )

        # Most accessed memories
        cursor.execute(
            "SELECT memory_node_id, COUNT(*) as access_count FROM memory_accesses GROUP BY memory_node_id ORDER BY access_count DESC LIMIT 5"
        )
        top_accessed = cursor.fetchall()

        conn.close()

        return {
            "observer_statistics": {
                observer_type: {
                    "access_count": count,
                    "avg_collapse_strength": avg_strength,
                }
                for observer_type, count, avg_strength in observer_stats
            },
            "average_fidelity_drift": avg_fidelity_drift,
            "most_accessed_memories": [
                {"memory_id": mem_id, "access_count": count}
                for mem_id, count in top_accessed
            ],
            "total_observer_profiles": len(self.observer_profiles),
            "total_memory_views": len(self.memory_states),
        }

    async def simulate_memory_decay(self, time_threshold_hours: float = 24.0):
        """Simulate natural memory decay for unaccessed memories"""
        current_time = time.time()
        threshold_seconds = time_threshold_hours * 3600

        decay_count = 0

        for memory_view in self.memory_states.values():
            time_since_access = current_time - memory_view.last_accessed

            if time_since_access > threshold_seconds:
                # Apply decay based on time elapsed
                decay_rate = 0.1 * (time_since_access / threshold_seconds)
                decay_amount = min(0.5, decay_rate)  # Max 50% decay

                memory_view.current_fidelity = max(
                    0.1, memory_view.current_fidelity - decay_amount
                )
                await self._update_memory_view(memory_view)
                decay_count += 1

        print(f"🕰️ Memory decay simulation: {decay_count} memories affected")
        return decay_count


# Async initialization function
async def create_observer_effect_simulator(
    fractal_encoder: FractalEncoder, data_dir: str
) -> ObserverEffectSimulator:
    """Create and initialize ObserverEffectSimulator"""
    simulator = ObserverEffectSimulator(fractal_encoder, data_dir)
    await simulator.initialize_databases()
    return simulator
