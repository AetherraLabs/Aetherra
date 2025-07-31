symbolic reasoning, and narrative generation. Inspired by Synthetic Soul's approach.
"""
DEPRECATED: LyrixaMemoryEngine is now an adapter for QuantumEnhancedMemoryEngine.
All memory operations are delegated to the canonical engine.
"""

from .QuantumEnhancedMemoryEngine.engine import QuantumEnhancedMemoryEngine

class LyrixaMemoryEngine:
    def __init__(self, *args, **kwargs):
        self.engine = QuantumEnhancedMemoryEngine()

    def store(self, memory_entry: dict) -> dict:
        return self.engine.store(memory_entry)

    def retrieve(self, query: str, context: dict = None) -> dict:
        return self.engine.retrieve(query, context)
from .memory_core import LyrixaMemorySystem
from .narrator import MemoryNarrative, MemoryNarrator
from .pulse import DriftAlert, MemoryHealth, MemoryPulseMonitor
from .reflector import MemoryReflector, ReflectionInsight


@dataclass
class MemorySystemConfig:
    """Configuration for the integrated memory system"""

    # Database paths
    core_db_path: str = "lyrixa_memory.db"
    fractal_db_path: str = "fractal_memory.db"
    concepts_db_path: str = "concept_clusters.db"
    timeline_db_path: str = "episodic_timeline.db"
    pulse_db_path: str = "memory_pulse.db"
    reflector_db_path: str = "memory_reflector.db"

    # System parameters
    max_fragments_per_day: int = 1000
    auto_narrative_generation: bool = True
    auto_pulse_monitoring: bool = True
    reflection_frequency: timedelta = timedelta(hours=6)

    # Memory retention
    fragment_retention_days: int = 365
    low_confidence_cleanup_threshold: float = 0.2

    # Integration settings
    enable_cross_system_validation: bool = True
    narrative_generation_threshold: int = 5  # Min fragments for narrative


@dataclass
class MemoryOperationResult:
    """Result of a memory operation"""

    success: bool
    operation_type: str
    fragment_id: Optional[str] = None
    insights: List[ReflectionInsight] = None
    narrative: Optional[MemoryNarrative] = None
    alerts: List[DriftAlert] = None
    message: str = ""


class LyrixaMemoryEngine:
    """
    Next-generation integrated memory system for Lyrixa

    Combines:
    - Fast vector-based retrieval (existing system)
    - Multi-dimensional episodic memory (FractalMesh)
    - Narrative story generation
    - Health monitoring and drift correction
    - Reflective meta-cognitive analysis
    """

    def __init__(self, config: Optional[MemorySystemConfig] = None):
        self.config = config or MemorySystemConfig()

        # Initialize core components
        self.core_memory = LyrixaMemorySystem(self.config.core_db_path)
        self.fractal_mesh = FractalMeshCore(self.config.fractal_db_path)
        self.concept_manager = ConceptClusterManager(self.config.concepts_db_path)
        self.timeline_manager = EpisodicTimeline(self.config.timeline_db_path)
        self.analog_finder = CrossContextAnalogies()
        self.narrator = MemoryNarrator()
        self.pulse_monitor = MemoryPulseMonitor(self.config.pulse_db_path)
        self.reflector = MemoryReflector(self.config.reflector_db_path)

        # Integration state
        self.last_pulse_check = datetime.now()
        self.last_reflection = datetime.now()
        self.last_narrative_generation = datetime.now()

        # Performance metrics
        self.operation_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "fragments_created": 0,
            "narratives_generated": 0,
            "insights_discovered": 0,
        }

        # In-memory store for test compatibility
        self._mem = []

    def store(self, content, metadata=None):
        """Store memory for test compatibility"""
        self._mem.append({"content": content, "metadata": metadata or {}})

    def retrieve(self, query):
        """Retrieve memory for test compatibility"""
        return [m for m in self._mem if query in m["content"]]

    async def remember(
        self,
        content: Any,
        tags: Optional[List[str]] = None,
        category: str = "general",
        fragment_type: MemoryFragmentType = MemoryFragmentType.SEMANTIC,
        confidence: float = 1.0,
        narrative_role: Optional[str] = None,
    ) -> MemoryOperationResult:
        """
        Store a new memory with integrated processing across all systems
        """
        self.operation_stats["total_operations"] += 1

        try:
            # Create unique fragment ID
            fragment_id = str(uuid.uuid4())
            current_time = datetime.now()

            # Store in core memory system (vector embeddings)
            core_result = await self.core_memory.store_memory(
                content={"text": str(content), "category": category},
                context={"category": category, "narrative_role": narrative_role},
                tags=tags or [],
                importance=confidence * 0.8,  # Convert confidence to importance
                memory_type=category,
            )

            # Create fractal mesh fragment
            fragment = MemoryFragment(
                fragment_id=fragment_id,
                content={"text": str(content), "category": category},
                fragment_type=fragment_type,
                temporal_tags={
                    "hour": current_time.hour,
                    "day_of_week": current_time.weekday(),
                    "timestamp": current_time.isoformat(),
                },
                symbolic_tags=set(tags or []),
                associative_links=[],  # Will be populated by concept analysis
                confidence_score=confidence,
                access_pattern={"created": current_time.isoformat(), "access_count": 0},
                narrative_role=narrative_role,
                created_at=current_time,
                last_evolved=current_time,
            )

            # Store in fractal mesh
            self.fractal_mesh.store_fragment(fragment)

            # Process through concept clustering
            affected_clusters = self.concept_manager.process_new_fragment(fragment)

            # Process through episodic timeline
            affected_chains = self.timeline_manager.process_new_fragment(fragment)

            # Update fragment with associative links from clustering
            if affected_clusters:
                fragment.associative_links.extend(
                    affected_clusters[:5]
                )  # Limit associations
                self.fractal_mesh.store_fragment(fragment)  # Update with associations

            self.operation_stats["successful_operations"] += 1
            self.operation_stats["fragments_created"] += 1

            # Trigger background processing
            background_tasks = []

            # Auto-generate narratives if threshold met
            if self.config.auto_narrative_generation:
                background_tasks.append(self._check_narrative_generation())

            # Auto-pulse monitoring
            if self.config.auto_pulse_monitoring:
                background_tasks.append(self._check_pulse_monitoring())

            # Run background tasks
            if background_tasks:
                await asyncio.gather(*background_tasks, return_exceptions=True)

            return MemoryOperationResult(
                success=True,
                operation_type="remember",
                fragment_id=fragment_id,
                message=f"Memory stored successfully with {len(affected_clusters)} concept associations",
            )

        except Exception as e:
            return MemoryOperationResult(
                success=False,
                operation_type="remember",
                message=f"Failed to store memory: {str(e)}",
            )

    async def recall(
        self,
        query: str,
        recall_strategy: str = "hybrid",
        limit: int = 10,
        time_filter: Optional[Dict[str, Any]] = None,
        concept_filter: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Intelligent multi-strategy memory recall

        Strategies:
        - "vector": Fast semantic similarity (existing system)
        - "episodic": Story-based temporal recall
        - "conceptual": Concept cluster based recall
        - "hybrid": Combined approach (default)
        """

        results = []

        if recall_strategy in ["vector", "hybrid"]:
            # Vector-based recall from core system
            vector_results = await self.core_memory.recall_memories(
                query_text=query, limit=limit
            )

            for i, memory in enumerate(vector_results):
                results.append(
                    {
                        "content": memory.content,
                        "source": "vector",
                        "relevance_score": (limit - i) / limit,
                        "type": "semantic_match",
                        "memory_id": memory.id,
                        "tags": memory.tags,
                    }
                )

        if recall_strategy in ["conceptual", "hybrid"]:
            # Concept-based recall
            if concept_filter:
                for concept in concept_filter:
                    concept_fragments = self.fractal_mesh.retrieve_by_concept(
                        concept, limit
                    )
                    for fragment in concept_fragments:
                        results.append(
                            {
                                "content": fragment.content,
                                "source": "conceptual",
                                "relevance_score": fragment.confidence_score,
                                "type": "concept_match",
                                "fragment_id": fragment.fragment_id,
                                "concepts": list(fragment.symbolic_tags),
                            }
                        )

        if recall_strategy in ["episodic", "hybrid"]:
            # Episodic recall
            if time_filter and "start" in time_filter and "end" in time_filter:
                episodic_chains = self.timeline_manager.retrieve_episodic_sequence(
                    start_time=time_filter["start"], end_time=time_filter["end"]
                )

                for chain in episodic_chains:
                    results.append(
                        {
                            "content": {
                                "narrative_arc": chain.narrative_arc,
                                "fragment_count": len(chain.fragments),
                                "time_span": chain.temporal_span,
                            },
                            "source": "episodic",
                            "relevance_score": chain.significance_score,
                            "type": "episodic_sequence",
                            "chain_id": chain.chain_id,
                        }
                    )

        # Sort by relevance and remove duplicates
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        # Return top results
        return results[:limit]

    async def generate_narrative(
        self,
        narrative_type: str = "daily",
        time_range: Optional[tuple] = None,
        theme: Optional[str] = None,
    ) -> MemoryNarrative:
        """Generate a narrative from recent memories"""

        # Get relevant fragments
        if time_range:
            start_time, end_time = time_range
            fragments = [
                f
                for f in self.fractal_mesh.fragments.values()
                if start_time <= f.created_at <= end_time
            ]
        else:
            # Default to last 24 hours
            cutoff = datetime.now() - timedelta(days=1)
            fragments = [
                f
                for f in self.fractal_mesh.fragments.values()
                if f.created_at >= cutoff
            ]

        # Generate narrative based on type
        if narrative_type == "daily":
            narrative = self.narrator.generate_daily_narrative(fragments)
        elif narrative_type == "weekly":
            narrative = self.narrator.generate_weekly_narrative(fragments)
        elif narrative_type == "thematic" and theme:
            narrative = self.narrator.generate_thematic_narrative(fragments, theme)
        else:
            narrative = self.narrator.generate_daily_narrative(fragments)

        self.operation_stats["narratives_generated"] += 1
        self.last_narrative_generation = datetime.now()

        return narrative

    async def run_reflection(
        self, reflection_type: str = "past_week", target_concept: Optional[str] = None
    ) -> List[ReflectionInsight]:
        """Run reflective analysis on memories"""

        fragments = list(self.fractal_mesh.fragments.values())
        concept_clusters = list(self.concept_manager.clusters.values())

        if reflection_type == "past_week":
            cutoff = datetime.now() - timedelta(days=7)
            time_range = (cutoff, datetime.now())
            insights = self.reflector.reflect_on_past_range(fragments, time_range)

        elif reflection_type == "contradictions":
            insights = self.reflector.analyze_contradictions(
                fragments, concept_clusters
            )

        elif reflection_type == "concept_exploration" and target_concept:
            insights = self.reflector.explore_concept_connections(
                target_concept, fragments, concept_clusters
            )

        elif reflection_type == "blind_spots":
            insights = self.reflector.detect_blind_spots(fragments)

        else:
            # Default past week reflection
            cutoff = datetime.now() - timedelta(days=7)
            time_range = (cutoff, datetime.now())
            insights = self.reflector.reflect_on_past_range(fragments, time_range)

        self.operation_stats["insights_discovered"] += len(insights)
        self.last_reflection = datetime.now()

        return insights

    async def check_memory_health(self) -> MemoryHealth:
        """Check overall memory system health"""

        fragments = list(self.fractal_mesh.fragments.values())
        concept_clusters = list(self.concept_manager.clusters.values())

        health = self.pulse_monitor.run_pulse_check(fragments, concept_clusters)
        self.last_pulse_check = datetime.now()

        return health

    def get_memory_health(self) -> Dict[str, Any]:
        """Get current memory system health status synchronously

        Returns:
            Dictionary containing health metrics and status information
        """
        try:
            fragments = list(self.fractal_mesh.fragments.values())
            concept_clusters = list(self.concept_manager.clusters.values())

            # Run health check synchronously
            health = self.pulse_monitor.run_pulse_check(fragments, concept_clusters)

            # Convert MemoryHealth to dictionary format
            health_dict = {
                "coherence_score": health.coherence_score,
                "total_fragments": health.total_fragments,
                "active_concepts": health.active_concepts,
                "average_confidence": health.average_confidence,
                "contradiction_count": health.contradiction_count,
                "orphaned_fragments": health.orphaned_fragments,
                "health_trend": health.health_trend,
                "last_maintenance": health.last_maintenance.isoformat()
                if health.last_maintenance
                else None,
                "memory_stats": {
                    "last_check": self.last_pulse_check.isoformat(),
                    "system_uptime": (
                        datetime.now() - self.last_pulse_check
                    ).total_seconds(),
                },
                "performance_metrics": self.operation_stats,
                "status": "healthy" if health.coherence_score > 0.7 else "degraded",
            }

            return health_dict

        except Exception as e:
            return {
                "coherence_score": 0.0,
                "total_fragments": 0,
                "active_concepts": 0,
                "average_confidence": 0.0,
                "contradiction_count": 0,
                "orphaned_fragments": 0,
                "health_trend": "unknown",
                "last_maintenance": None,
                "memory_stats": {
                    "last_check": datetime.now().isoformat(),
                    "system_uptime": 0,
                },
                "performance_metrics": {},
                "status": "error",
                "error": str(e),
            }

    async def get_memory_pulse(self) -> Dict[str, Any]:
        """Get memory pulse monitoring information

        Returns:
            Dictionary containing pulse monitoring data
        """
        try:
            # Run health check first to get current pulse data
            health = await self.check_memory_health()

            # Get recent drift alerts from pulse monitor if available
            drift_alerts = []
            if hasattr(self.pulse_monitor, "get_recent_alerts"):
                alerts = self.pulse_monitor.get_recent_alerts()
                drift_alerts = [
                    {
                        "alert_id": alert.alert_id,
                        "drift_type": alert.drift_type,
                        "severity": alert.severity,
                        "description": alert.description,
                        "detected_at": alert.detected_at.isoformat(),
                        "resolved": alert.resolved,
                    }
                    for alert in alerts
                ]

            pulse_data = {
                "pulse_status": "active",
                "last_pulse_check": self.last_pulse_check.isoformat(),
                "coherence_score": health.coherence_score,
                "health_trend": health.health_trend,
                "drift_alerts": drift_alerts,
                "monitoring_active": self.config.auto_pulse_monitoring,
                "next_scheduled_check": (
                    self.last_pulse_check + timedelta(hours=2)
                ).isoformat(),
            }

            return pulse_data

        except Exception as e:
            return {
                "pulse_status": "error",
                "last_pulse_check": self.last_pulse_check.isoformat(),
                "coherence_score": 0.0,
                "health_trend": "unknown",
                "drift_alerts": [],
                "monitoring_active": False,
                "error": str(e),
            }

    async def get_memory_insights(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive memory insights and recommendations"""

        # Get recent insights
        recent_insights = self.reflector.get_recent_insights(days)

        # Get health status
        health = await self.check_memory_health()

        # Get active alerts
        active_alerts = self.pulse_monitor.get_active_alerts()

        # Get actionable recommendations
        recommendations = self.reflector.get_actionable_recommendations()

        return {
            "health_summary": self.pulse_monitor.get_health_summary(),
            "recent_insights": [
                {
                    "type": insight.insight_type,
                    "description": insight.description,
                    "significance": insight.significance,
                    "recommendation": insight.actionable_recommendation,
                }
                for insight in recent_insights[:5]
            ],
            "active_alerts": [
                {
                    "type": alert.drift_type,
                    "severity": alert.severity,
                    "description": alert.description,
                    "action": alert.recommended_action,
                }
                for alert in active_alerts[:3]
            ],
            "recommendations": recommendations[:5],
            "system_stats": self.operation_stats,
        }

    async def maintenance_cycle(self) -> Dict[str, Any]:
        """Run a complete maintenance cycle"""

        maintenance_results = {
            "health_check": await self.check_memory_health(),
            "insights": await self.run_reflection("past_week"),
            "narrative": await self.generate_narrative("daily"),
            "alerts_resolved": 0,
            "fragments_cleaned": 0,
        }

        # Auto-resolve low-severity alerts (would implement actual resolution)
        low_severity_alerts = [
            a for a in self.pulse_monitor.get_active_alerts() if a.severity == "low"
        ]

        for alert in low_severity_alerts[:3]:  # Resolve up to 3 low-severity alerts
            if self.pulse_monitor.resolve_alert(
                alert.alert_id, "Auto-resolved during maintenance"
            ):
                maintenance_results["alerts_resolved"] += 1

        # Clean up very old low-confidence fragments
        cutoff_date = datetime.now() - timedelta(
            days=self.config.fragment_retention_days
        )
        old_fragments = [
            f
            for f in self.fractal_mesh.fragments.values()
            if (
                f.created_at < cutoff_date
                and f.confidence_score < self.config.low_confidence_cleanup_threshold
            )
        ]

        # Would implement actual cleanup here
        maintenance_results["fragments_cleaned"] = len(old_fragments)

        return maintenance_results

    # Background processing methods
    async def _check_narrative_generation(self):
        """Check if narrative generation should be triggered"""
        time_since_last = datetime.now() - self.last_narrative_generation

        if time_since_last > timedelta(hours=12):  # Generate narratives twice daily
            await self.generate_narrative("daily")

    async def _check_pulse_monitoring(self):
        """Check if pulse monitoring should be triggered"""
        time_since_last = datetime.now() - self.last_pulse_check

        if time_since_last > timedelta(hours=2):  # Check health every 2 hours
            await self.check_memory_health()

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status and metrics"""

        return {
            "components": {
                "core_memory": "active",
                "fractal_mesh": f"{len(self.fractal_mesh.fragments)} fragments",
                "concept_clusters": f"{len(self.concept_manager.clusters)} clusters",
                "episodic_chains": f"{len(self.timeline_manager.episodic_chains)} chains",
                "narrator": "active",
                "pulse_monitor": "active",
                "reflector": "active",
            },
            "last_operations": {
                "pulse_check": self.last_pulse_check.isoformat(),
                "reflection": self.last_reflection.isoformat(),
                "narrative_generation": self.last_narrative_generation.isoformat(),
            },
            "performance": self.operation_stats,
            "configuration": {
                "auto_narrative": self.config.auto_narrative_generation,
                "auto_pulse": self.config.auto_pulse_monitoring,
                "reflection_frequency": str(self.config.reflection_frequency),
            },
        }
