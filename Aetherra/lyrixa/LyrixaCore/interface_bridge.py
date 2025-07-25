"""
LyrixaCore Interface Bridge - Unified Communication Interface
Part of LyrixaCore for Phase 6: Unified Cognitive Stack

This module provides the unified interface that coordinates between all cognitive
subsystems, ensuring coherent integration and consistent identity representation.
"""

import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .IdentityAgent.core_beliefs import CoreBeliefs
from .IdentityAgent.personal_history import EventType, PersonalHistory
from .IdentityAgent.self_model import SelfModel

# Import FractalMesh Memory System
try:
    from ..memory.fractal_mesh import FractalMeshCore
    from ..memory.fractal_mesh.base import MemoryFragment, MemoryFragmentType

    FRACTAL_MESH_AVAILABLE = True
    print("[LyrixaCore] ✅ FractalMesh Memory System available")
except ImportError as e:
    print(f"[LyrixaCore] ⚠️ FractalMesh Memory System not available: {e}")
    FRACTAL_MESH_AVAILABLE = False
    FractalMeshCore = None
    MemoryFragment = None
    MemoryFragmentType = None

# Import Plugin System
try:
    from ..plugins.enhanced_plugin_manager import PluginManager
    from ..plugins.memory_aware_plugin_router import MemoryAwarePluginRouter

    PLUGIN_SYSTEM_AVAILABLE = True
    print("[LyrixaCore] ✅ Plugin System available")
except ImportError as e:
    print(f"[LyrixaCore] ⚠️ Plugin System not available: {e}")
    PLUGIN_SYSTEM_AVAILABLE = False
    PluginManager = None
    MemoryAwarePluginRouter = None

# Import Reflection Engine
try:
    from ..reflection_engine.shadow_state_forker import ShadowStateForker
    from ..reflection_engine.validation_engine import ValidationEngine

    REFLECTION_ENGINE_AVAILABLE = True
    print("[LyrixaCore] ✅ Reflection Engine available")
except ImportError as e:
    print(f"[LyrixaCore] ⚠️ Reflection Engine not available: {e}")
    REFLECTION_ENGINE_AVAILABLE = False
    ValidationEngine = None
    ShadowStateForker = None

# Import Self Metrics Dashboard
try:
    from ..self_metrics_dashboard.main_dashboard import SelfMetricsDashboard
    from ..self_metrics_dashboard.memory_continuity_score import MemoryContinuityTracker

    SELF_METRICS_AVAILABLE = True
    print("[LyrixaCore] ✅ Self Metrics Dashboard available")
except ImportError as e:
    print(f"[LyrixaCore] ⚠️ Self Metrics Dashboard not available: {e}")
    SELF_METRICS_AVAILABLE = False
    SelfMetricsDashboard = None
    MemoryContinuityTracker = None


class ContextType(Enum):
    """Types of context requests"""

    FULL_SUMMARY = "full_summary"
    DECISION_SUPPORT = "decision_support"
    MEMORY_UPDATE = "memory_update"
    IDENTITY_CHECK = "identity_check"
    COHERENCE_ASSESSMENT = "coherence_assessment"


@dataclass
class ContextRequest:
    """Request for context information from the unified interface"""

    request_type: ContextType
    timestamp: float
    parameters: Dict[str, Any]
    requester: str


@dataclass
class ContextResponse:
    """Response containing unified context information"""

    request_id: str
    context_summary: Dict[str, Any]
    recommendations: List[str]
    coherence_score: float
    confidence_level: float
    response_timestamp: float


class LyrixaContextBridge:
    """
    Unified communication interface coordinating all cognitive subsystems.

    This bridge ensures that memory, ethics, identity, and other agents work
    together coherently, maintaining consistent identity and decision-making.
    """

    def __init__(
        self,
        memory_engine=None,
        ethics_agent=None,
        identity_agent: SelfModel = None,
        agent_stack=None,
        reflector=None,
        workspace_path: str = None,
    ):
        """Initialize the unified interface with all cognitive subsystems"""

        # Core cognitive subsystems
        self.memory = memory_engine
        self.ethics = ethics_agent
        self.identity = identity_agent or SelfModel()
        self.agents = agent_stack
        self.reflector = reflector

        # 🧠 Initialize FractalMesh Memory System for LyrixaCore
        if FRACTAL_MESH_AVAILABLE and FractalMeshCore:
            try:
                import os

                db_path = "lyrixacore_memory.db"
                if workspace_path:
                    db_path = os.path.join(workspace_path, "lyrixacore_memory.db")

                self.fractal_memory = FractalMeshCore(db_path=db_path)
                print("[LyrixaCore] ✅ FractalMesh Memory System initialized")

                # If no memory engine was provided, use FractalMesh as the memory system
                if not self.memory:
                    self.memory = self.fractal_memory
                    print("[LyrixaCore] 🧠 Using FractalMesh as primary memory engine")

            except Exception as e:
                print(f"[LyrixaCore] ⚠️ FractalMesh initialization failed: {e}")
                self.fractal_memory = None
        else:
            self.fractal_memory = None

        # 🔌 Initialize Plugin System
        if PLUGIN_SYSTEM_AVAILABLE and PluginManager:
            try:
                import os  # Ensure os is imported

                plugin_dir = "plugins"
                if workspace_path:
                    plugin_dir = os.path.join(
                        workspace_path, "Aetherra", "lyrixa", "plugins"
                    )

                self.plugin_manager = PluginManager(plugins_dir=plugin_dir)

                # Initialize memory-aware plugin router if available
                if MemoryAwarePluginRouter and self.fractal_memory:
                    # We'll need to create a concept manager for the router
                    try:
                        from ..memory.fractal_mesh.concepts.concept_clusters import (
                            ConceptClusterManager,
                        )

                        concept_manager = ConceptClusterManager()

                        # Use a wrapper for the memory engine since the router expects LyrixaMemoryEngine
                        class FractalMeshWrapper:
                            def __init__(self, fractal_mesh):
                                self.fractal_mesh = fractal_mesh

                            def get_recent_fragments(self, limit=10):
                                return list(self.fractal_mesh.fragments.values())[
                                    -limit:
                                ]

                        memory_wrapper = FractalMeshWrapper(self.fractal_memory)

                        self.plugin_router = MemoryAwarePluginRouter(
                            memory_engine=memory_wrapper,
                            concept_manager=concept_manager,
                        )
                        print("[LyrixaCore] ✅ Memory-aware Plugin Router initialized")
                    except Exception as router_error:
                        print(
                            f"[LyrixaCore] ⚠️ Plugin Router init failed: {router_error}"
                        )
                        self.plugin_router = None
                else:
                    self.plugin_router = None

                print("[LyrixaCore] ✅ Plugin System initialized")
            except Exception as e:
                print(f"[LyrixaCore] ⚠️ Plugin System initialization failed: {e}")
                self.plugin_manager = None
                self.plugin_router = None
        else:
            self.plugin_manager = None
            self.plugin_router = None

        # 🔍 Initialize Reflection Engine
        if REFLECTION_ENGINE_AVAILABLE and ValidationEngine:
            try:
                validation_dir = "validation_data"
                if workspace_path:
                    validation_dir = os.path.join(workspace_path, "validation_data")

                self.validation_engine = ValidationEngine(data_dir=validation_dir)

                if ShadowStateForker:
                    # The ValidationEngine creates its own ShadowStateForker, so we reference that
                    self.shadow_forker = self.validation_engine.shadow_forker
                    print(
                        "[LyrixaCore] ✅ Shadow State Forker referenced from ValidationEngine"
                    )
                else:
                    self.shadow_forker = None

                print("[LyrixaCore] ✅ Reflection Engine initialized")
            except Exception as e:
                print(f"[LyrixaCore] ⚠️ Reflection Engine initialization failed: {e}")
                self.validation_engine = None
                self.shadow_forker = None
        else:
            self.validation_engine = None
            self.shadow_forker = None

        # 📊 Initialize Self Metrics Dashboard
        if SELF_METRICS_AVAILABLE and SelfMetricsDashboard:
            try:
                metrics_dir = "self_metrics_data"
                if workspace_path:
                    metrics_dir = os.path.join(workspace_path, "self_metrics_data")

                self.metrics_dashboard = SelfMetricsDashboard(data_dir=metrics_dir)

                if MemoryContinuityTracker and self.fractal_memory:
                    # The SelfMetricsDashboard creates its own trackers, so we reference those
                    self.memory_continuity = self.metrics_dashboard.memory_tracker
                    print(
                        "[LyrixaCore] ✅ Memory Continuity Tracker referenced from dashboard"
                    )
                else:
                    self.memory_continuity = None

                print("[LyrixaCore] ✅ Self Metrics Dashboard initialized")
            except Exception as e:
                print(
                    f"[LyrixaCore] ⚠️ Self Metrics Dashboard initialization failed: {e}"
                )
                self.metrics_dashboard = None
                self.memory_continuity = None
        else:
            self.metrics_dashboard = None
            self.memory_continuity = None

        # Interface state
        self.active_requests = {}
        self.context_history = []
        self.integration_metrics = {
            "successful_integrations": 0,
            "failed_integrations": 0,
            "average_coherence": 0.8,
            "response_times": [],
            "memory_fragments_stored": 0,
            "memory_retrievals": 0,
        }

        # Coherence thresholds
        self.thresholds = {
            "memory_acceptance": 0.7,
            "decision_approval": 0.75,
            "identity_coherence": 0.6,
            "ethics_alignment": 0.8,
        }

        print(
            "[LyrixaContextBridge] Unified cognitive interface initialized with FractalMesh integration"
        )

    def get_context_summary(
        self,
        request_type: ContextType = ContextType.FULL_SUMMARY,
        parameters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get comprehensive context summary from all cognitive subsystems

        Args:
            request_type: Type of context needed
            parameters: Additional parameters for context generation

        Returns:
            Unified context summary
        """
        start_time = time.time()
        parameters = parameters or {}

        try:
            context = {"timestamp": start_time, "request_type": request_type.value}

            # Identity and beliefs context
            if self.identity:
                context["identity"] = {
                    "summary": self.identity.summarize_self(),
                    "dimensional_scores": self.identity.dimensional_scores,
                    "coherence_score": self.identity.assess_coherence(),
                    "active_goals": self.identity.active_goals,
                    "current_beliefs": self.identity.beliefs.values
                    if self.identity.beliefs
                    else {},
                }

            # Ethics context
            if self.ethics:
                try:
                    ethics_summary = getattr(
                        self.ethics,
                        "get_alignment_summary",
                        lambda: {"alignment_score": 0.8},
                    )()
                    context["ethics"] = {
                        "alignment_score": ethics_summary.get("alignment_score", 0.8),
                        "recent_decisions": getattr(
                            self.ethics, "recent_decisions", []
                        ),
                        "active_frameworks": getattr(
                            self.ethics, "active_frameworks", ["default"]
                        ),
                    }
                except Exception as e:
                    print(f"[Bridge] Ethics context error: {e}")
                    context["ethics"] = {"alignment_score": 0.8, "status": "limited"}

            # Memory context - Enhanced with FractalMesh
            if self.memory:
                try:
                    # Use FractalMesh if available for enhanced memory context
                    if self.fractal_memory:
                        fragment_count = len(self.fractal_memory.fragments)
                        cluster_count = len(self.fractal_memory.concept_clusters)
                        chain_count = len(self.fractal_memory.episodic_chains)

                        # Calculate memory health from FractalMesh
                        if fragment_count > 0:
                            # Average confidence from recent fragments
                            recent_fragments = list(
                                self.fractal_memory.fragments.values()
                            )[-10:]
                            avg_confidence = (
                                sum(f.confidence_score for f in recent_fragments)
                                / len(recent_fragments)
                                if recent_fragments
                                else 0.8
                            )
                        else:
                            avg_confidence = 0.8

                        context["memory"] = {
                            "health_score": avg_confidence,
                            "fragment_count": fragment_count,
                            "concept_clusters": cluster_count,
                            "episodic_chains": chain_count,
                            "memory_type": "FractalMesh",
                            "confidence_avg": avg_confidence,
                            "status": "enhanced",
                        }
                    else:
                        # Fallback to generic memory health
                        memory_health = getattr(
                            self.memory,
                            "get_health_metrics",
                            lambda: {"coherence": 0.8},
                        )()
                        context["memory"] = {
                            "health_score": memory_health.get("coherence", 0.8),
                            "recent_entries": getattr(self.memory, "recent_count", 0),
                            "confidence_avg": memory_health.get("confidence_avg", 0.8),
                            "memory_type": "generic",
                            "status": "standard",
                        }
                except Exception as e:
                    print(f"[Bridge] Memory context error: {e}")
                    context["memory"] = {"health_score": 0.8, "status": "limited"}

            # Agent stack context
            if self.agents:
                try:
                    active_goals = getattr(
                        self.agents, "get_active_goals", lambda: []
                    )()
                    context["agents"] = {
                        "active_goals": active_goals,
                        "goal_count": len(active_goals) if active_goals else 0,
                        "agent_status": "operational",
                    }
                except Exception as e:
                    print(f"[Bridge] Agent stack context error: {e}")
                    context["agents"] = {"active_goals": [], "status": "limited"}

            # Reflection context
            if self.reflector:
                try:
                    reflection_score = getattr(
                        self.reflector, "get_recent_insight_score", lambda: 0.8
                    )()
                    context["reflection"] = {
                        "insight_score": reflection_score,
                        "recent_insights": getattr(
                            self.reflector, "recent_insights", []
                        ),
                        "reflection_quality": "good"
                        if reflection_score > 0.7
                        else "moderate",
                    }
                except Exception as e:
                    print(f"[Bridge] Reflection context error: {e}")
                    context["reflection"] = {"insight_score": 0.8, "status": "limited"}

            # 🔌 Plugin System context
            if self.plugin_manager:
                try:
                    plugin_count = len(getattr(self.plugin_manager, "plugins", {}))
                    active_plugins = len(
                        [
                            p
                            for p, state in getattr(
                                self.plugin_manager, "plugin_states", {}
                            ).items()
                            if state == "active"
                        ]
                    )

                    context["plugins"] = {
                        "total_plugins": plugin_count,
                        "active_plugins": active_plugins,
                        "plugin_router_available": self.plugin_router is not None,
                        "memory_aware_routing": self.plugin_router is not None
                        and self.fractal_memory is not None,
                        "status": "operational",
                    }
                except Exception as e:
                    print(f"[Bridge] Plugin system context error: {e}")
                    context["plugins"] = {"status": "limited"}

            # 🔍 Reflection Engine context
            if self.validation_engine:
                try:
                    pending_validations = len(
                        getattr(self.validation_engine, "pending_validations", {})
                    )
                    completed_validations = len(
                        getattr(self.validation_engine, "completed_validations", [])
                    )
                    approved_changes = len(
                        getattr(self.validation_engine, "approved_changes", [])
                    )

                    context["validation"] = {
                        "pending_validations": pending_validations,
                        "completed_validations": completed_validations,
                        "approved_changes": approved_changes,
                        "shadow_forker_available": self.shadow_forker is not None,
                        "validation_health": "operational"
                        if pending_validations < 10
                        else "busy",
                        "status": "operational",
                    }
                except Exception as e:
                    print(f"[Bridge] Validation engine context error: {e}")
                    context["validation"] = {"status": "limited"}

            # 📊 Self Metrics Dashboard context
            if self.metrics_dashboard:
                try:
                    # Get latest metrics if available
                    latest_metrics = getattr(
                        self.metrics_dashboard, "get_current_snapshot", lambda: None
                    )()

                    if latest_metrics:
                        context["self_metrics"] = {
                            "memory_continuity": latest_metrics.memory_continuity_score,
                            "narrative_integrity": latest_metrics.narrative_integrity_index,
                            "ethics_alignment": latest_metrics.ethics_alignment_score,
                            "conflict_resolution": latest_metrics.conflict_resolution_efficiency,
                            "growth_trajectory": getattr(
                                latest_metrics, "growth_score", 0.8
                            ),
                            "status": "operational",
                        }
                    else:
                        context["self_metrics"] = {
                            "status": "initializing",
                            "trackers_available": self.memory_continuity is not None,
                        }
                except Exception as e:
                    print(f"[Bridge] Self metrics context error: {e}")
                    context["self_metrics"] = {"status": "limited"}

            # Calculate overall system coherence
            coherence_scores = []
            if "identity" in context:
                coherence_scores.append(context["identity"]["coherence_score"])
            if "ethics" in context:
                coherence_scores.append(context["ethics"]["alignment_score"])
            if "memory" in context:
                coherence_scores.append(context["memory"]["health_score"])
            if "reflection" in context:
                coherence_scores.append(context["reflection"]["insight_score"])

            overall_coherence = (
                sum(coherence_scores) / len(coherence_scores)
                if coherence_scores
                else 0.8
            )
            context["system_coherence"] = overall_coherence

            # Add performance metrics
            response_time = time.time() - start_time
            self.integration_metrics["response_times"].append(response_time)
            context["response_time"] = response_time

            return context

        except Exception as e:
            print(f"[LyrixaContextBridge] Context summary error: {e}")
            return {
                "timestamp": start_time,
                "error": str(e),
                "system_coherence": 0.5,
                "status": "error",
            }

    def submit_memory_update(self, fragment: Dict[str, Any]) -> bool:
        """
        Submit a memory update through ethical and coherence validation

        Args:
            fragment: Memory fragment to be stored

        Returns:
            True if memory was accepted and stored
        """
        try:
            print(
                f"[Bridge] Evaluating memory update: {fragment.get('summary', 'Unknown')}"
            )

            # Ethics evaluation
            ethical_approved = True
            ethical_score = 0.8  # Default

            if self.ethics:
                try:
                    ethical_score = getattr(
                        self.ethics, "evaluate_memory", lambda x: 0.8
                    )(fragment)
                    ethical_approved = (
                        ethical_score >= self.thresholds["memory_acceptance"]
                    )
                except Exception as e:
                    print(f"[Bridge] Ethics evaluation error: {e}")
                    ethical_score = 0.8

            # Identity coherence check
            identity_coherent = True
            if self.identity:
                try:
                    # Check if memory aligns with current identity
                    current_coherence = self.identity.assess_coherence()
                    identity_coherent = (
                        current_coherence >= self.thresholds["identity_coherence"]
                    )
                except Exception as e:
                    print(f"[Bridge] Identity coherence error: {e}")

            # Decision logic
            if ethical_approved and identity_coherent:
                # Store in memory system - Enhanced with FractalMesh
                if (
                    self.fractal_memory
                    and FRACTAL_MESH_AVAILABLE
                    and MemoryFragment
                    and MemoryFragmentType
                ):
                    try:
                        # Create FractalMesh memory fragment
                        fragment_id = str(uuid.uuid4())

                        # Extract key concepts
                        symbolic_tags = set()
                        content_text = str(fragment.get("content", "")) + str(
                            fragment.get("summary", "")
                        )
                        concept_keywords = {
                            "decision",
                            "learning",
                            "ethics",
                            "identity",
                            "coherence",
                            "integration",
                            "system",
                            "memory",
                            "agent",
                            "reflection",
                        }

                        for keyword in concept_keywords:
                            if keyword.lower() in content_text.lower():
                                symbolic_tags.add(keyword)

                        # Create memory fragment
                        memory_fragment = MemoryFragment(
                            fragment_id=fragment_id,
                            content=fragment,
                            fragment_type=MemoryFragmentType.EPISODIC,
                            temporal_tags={
                                "timestamp": datetime.now().isoformat(),
                                "source": "lyrixa_core_bridge",
                                "ethical_score": ethical_score,
                            },
                            symbolic_tags=symbolic_tags,
                            associative_links=[],
                            confidence_score=fragment.get("confidence", 0.8),
                            access_pattern={
                                "created_at": datetime.now().isoformat(),
                                "access_count": 0,
                                "last_accessed": None,
                            },
                            narrative_role="cognitive_integration",
                            created_at=datetime.now(),
                            last_evolved=datetime.now(),
                        )

                        # Store in FractalMesh
                        self.fractal_memory.store_fragment(memory_fragment)
                        self.integration_metrics["memory_fragments_stored"] += 1
                        print(
                            f"[Bridge] 🧠 Stored fragment {fragment_id[:8]}... in FractalMesh"
                        )

                    except Exception as e:
                        print(f"[Bridge] FractalMesh storage error: {e}")
                        # Fallback to generic memory storage
                        if self.memory:
                            try:
                                getattr(self.memory, "store", lambda x: True)(fragment)
                            except Exception as fallback_error:
                                print(
                                    f"[Bridge] Memory storage fallback error: {fallback_error}"
                                )
                                return False
                elif self.memory:
                    try:
                        getattr(self.memory, "store", lambda x: True)(fragment)
                    except Exception as e:
                        print(f"[Bridge] Memory storage error: {e}")
                        return False

                # Update personal history
                if self.identity and self.identity.history:
                    event_summary = fragment.get("summary", "Memory update")
                    impact_score = min(
                        0.5, ethical_score - 0.5
                    )  # Convert ethics score to impact

                    self.identity.history.record_event(
                        event_type=EventType.LEARNING,
                        summary=event_summary,
                        impact_score=impact_score,
                        confidence=fragment.get("confidence", 0.8),
                        context={
                            "source": "memory_update",
                            "ethical_score": ethical_score,
                        },
                    )

                self.integration_metrics["successful_integrations"] += 1
                print(
                    f"[Bridge] ✅ Memory update accepted (ethics: {ethical_score:.2f})"
                )
                return True

            else:
                # Rejection handling
                rejection_reasons = []
                if not ethical_approved:
                    rejection_reasons.append(
                        f"ethics score {ethical_score:.2f} below threshold {self.thresholds['memory_acceptance']}"
                    )
                if not identity_coherent:
                    rejection_reasons.append("identity coherence below threshold")

                self.integration_metrics["failed_integrations"] += 1
                print(
                    f"[Bridge] ❌ Memory update rejected: {', '.join(rejection_reasons)}"
                )
                return False

        except Exception as e:
            print(f"[Bridge] Memory update error: {e}")
            self.integration_metrics["failed_integrations"] += 1
            return False

    def retrieve_relevant_memories(
        self, query_context: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant memories from FractalMesh based on context

        Args:
            query_context: Context information for memory search
            limit: Maximum number of memories to retrieve

        Returns:
            List of relevant memory fragments
        """
        try:
            if not self.fractal_memory or not FRACTAL_MESH_AVAILABLE:
                print("[Bridge] FractalMesh not available for memory retrieval")
                return []

            # Extract concepts from query context
            query_text = str(query_context.get("summary", "")) + str(
                query_context.get("content", "")
            )
            concept_keywords = {
                "decision",
                "learning",
                "ethics",
                "identity",
                "coherence",
                "integration",
                "system",
                "memory",
                "agent",
                "reflection",
            }

            relevant_concepts = []
            for keyword in concept_keywords:
                if keyword.lower() in query_text.lower():
                    relevant_concepts.append(keyword)

            if not relevant_concepts:
                return []

            # Retrieve memories for each concept
            all_memories = []
            for concept in relevant_concepts[:3]:  # Limit to top 3 concepts
                try:
                    memories = self.fractal_memory.retrieve_by_concept(concept, limit=2)
                    all_memories.extend(memories)
                except Exception as e:
                    print(
                        f"[Bridge] Memory retrieval error for concept '{concept}': {e}"
                    )

            # Convert to dictionaries and sort by relevance
            memory_dicts = []
            for memory in all_memories[:limit]:
                try:
                    memory_dict = {
                        "fragment_id": memory.fragment_id,
                        "content": memory.content,
                        "confidence": memory.confidence_score,
                        "narrative_role": memory.narrative_role,
                        "symbolic_tags": list(memory.symbolic_tags),
                        "created_at": memory.created_at.isoformat()
                        if hasattr(memory.created_at, "isoformat")
                        else str(memory.created_at),
                    }
                    memory_dicts.append(memory_dict)
                except Exception as e:
                    print(f"[Bridge] Error converting memory to dict: {e}")

            self.integration_metrics["memory_retrievals"] += 1
            print(f"[Bridge] 🔍 Retrieved {len(memory_dicts)} relevant memories")
            return memory_dicts

        except Exception as e:
            print(f"[Bridge] Memory retrieval error: {e}")
            return []

    def evaluate_decision(self, decision_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a decision through unified cognitive assessment

        Args:
            decision_context: Context and details of the decision

        Returns:
            Comprehensive decision evaluation
        """
        try:
            evaluation = {
                "timestamp": time.time(),
                "decision_summary": decision_context.get("summary", "Unknown decision"),
                "approved": False,
                "confidence": 0.0,
                "recommendations": [],
                "memory_context": [],
            }

            # 🧠 Retrieve relevant memories for decision context
            try:
                relevant_memories = self.retrieve_relevant_memories(
                    decision_context, limit=3
                )
                evaluation["memory_context"] = relevant_memories
                if relevant_memories:
                    print(
                        f"[Bridge] 🧠 Using {len(relevant_memories)} memory fragments for decision context"
                    )
            except Exception as e:
                print(f"[Bridge] Error retrieving decision context memories: {e}")

            scores = {}

            # Ethics evaluation
            if self.ethics:
                try:
                    ethics_result = getattr(
                        self.ethics,
                        "evaluate_decision",
                        lambda x: {"score": 0.8, "reasoning": "Default"},
                    )(decision_context)
                    scores["ethics"] = ethics_result.get("score", 0.8)
                    if ethics_result.get("reasoning"):
                        evaluation["ethics_reasoning"] = ethics_result["reasoning"]
                except Exception as e:
                    print(f"[Bridge] Ethics decision evaluation error: {e}")
                    scores["ethics"] = 0.8

            # Identity alignment
            if self.identity:
                try:
                    identity_score = self.identity.assess_coherence(decision_context)
                    scores["identity_alignment"] = identity_score
                except Exception as e:
                    print(f"[Bridge] Identity decision evaluation error: {e}")
                    scores["identity_alignment"] = 0.8

            # Belief consistency
            if self.identity and self.identity.beliefs:
                try:
                    belief_alignment = (
                        self.identity.beliefs.evaluate_decision_alignment(
                            decision_context
                        )
                    )
                    scores["belief_consistency"] = belief_alignment
                except Exception as e:
                    print(f"[Bridge] Belief decision evaluation error: {e}")
                    scores["belief_consistency"] = 0.8

            # Calculate overall score
            if scores:
                overall_score = sum(scores.values()) / len(scores)
                evaluation["overall_score"] = overall_score
                evaluation["component_scores"] = scores

                # Approval decision
                evaluation["approved"] = (
                    overall_score >= self.thresholds["decision_approval"]
                )
                evaluation["confidence"] = min(overall_score, 1.0)

                # Generate recommendations
                if overall_score < self.thresholds["decision_approval"]:
                    evaluation["recommendations"].append(
                        "Consider alternative approaches or additional safeguards"
                    )

                if scores.get("ethics", 1.0) < 0.8:
                    evaluation["recommendations"].append(
                        "Review ethical implications more carefully"
                    )

                if scores.get("identity_alignment", 1.0) < 0.7:
                    evaluation["recommendations"].append(
                        "Ensure decision aligns with core identity and values"
                    )

            return evaluation

        except Exception as e:
            print(f"[Bridge] Decision evaluation error: {e}")
            return {
                "approved": False,
                "confidence": 0.0,
                "error": str(e),
                "recommendations": ["Unable to complete evaluation due to error"],
            }

    def maintain_system_coherence(self) -> Dict[str, Any]:
        """
        Perform system-wide coherence maintenance and optimization

        Returns:
            Coherence maintenance report
        """
        try:
            maintenance_report = {
                "timestamp": time.time(),
                "coherence_checks": {},
                "adjustments_made": [],
                "recommendations": [],
                "overall_health": "good",
            }

            # Check identity coherence
            if self.identity:
                identity_coherence = self.identity.assess_coherence()
                maintenance_report["coherence_checks"]["identity"] = identity_coherence

                if identity_coherence < self.thresholds["identity_coherence"]:
                    # Create identity snapshot to track changes
                    snapshot = self.identity.create_identity_snapshot()
                    maintenance_report["adjustments_made"].append(
                        f"Created identity snapshot (coherence: {snapshot.coherence_score:.2f})"
                    )

                    if identity_coherence < 0.5:
                        maintenance_report["recommendations"].append(
                            "Consider identity consolidation activities"
                        )

            # Update integration metrics
            if self.integration_metrics["response_times"]:
                avg_response_time = sum(
                    self.integration_metrics["response_times"]
                ) / len(self.integration_metrics["response_times"])
                maintenance_report["performance"] = {
                    "avg_response_time": avg_response_time,
                    "successful_integrations": self.integration_metrics[
                        "successful_integrations"
                    ],
                    "failed_integrations": self.integration_metrics[
                        "failed_integrations"
                    ],
                }

                success_rate = self.integration_metrics[
                    "successful_integrations"
                ] / max(
                    self.integration_metrics["successful_integrations"]
                    + self.integration_metrics["failed_integrations"],
                    1,
                )

                if success_rate < 0.8:
                    maintenance_report["recommendations"].append(
                        "Review integration thresholds - high failure rate detected"
                    )

            # Overall system health assessment
            coherence_scores = list(maintenance_report["coherence_checks"].values())
            if coherence_scores:
                avg_coherence = sum(coherence_scores) / len(coherence_scores)
                self.integration_metrics["average_coherence"] = avg_coherence

                if avg_coherence > 0.8:
                    maintenance_report["overall_health"] = "excellent"
                elif avg_coherence > 0.6:
                    maintenance_report["overall_health"] = "good"
                else:
                    maintenance_report["overall_health"] = "needs_attention"

            return maintenance_report

        except Exception as e:
            print(f"[Bridge] Coherence maintenance error: {e}")
            return {
                "timestamp": time.time(),
                "error": str(e),
                "overall_health": "error",
            }

    def get_unified_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report of all unified systems"""

        try:
            # Get current context
            context = self.get_context_summary()

            # Perform coherence maintenance
            maintenance = self.maintain_system_coherence()

            # Generate unified report
            report = {
                "timestamp": time.time(),
                "system_status": "operational",
                "unified_context": context,
                "coherence_maintenance": maintenance,
                "integration_metrics": self.integration_metrics,
                "active_thresholds": self.thresholds,
                "subsystem_status": {},
            }

            # Check each subsystem
            subsystems = [
                ("identity", self.identity),
                ("memory", self.memory),
                ("ethics", self.ethics),
                ("agents", self.agents),
                ("reflector", self.reflector),
            ]

            for name, system in subsystems:
                if system:
                    report["subsystem_status"][name] = "connected"
                else:
                    report["subsystem_status"][name] = "not_connected"

            return report

        except Exception as e:
            print(f"[Bridge] Status report error: {e}")
            return {"timestamp": time.time(), "system_status": "error", "error": str(e)}


def main():
    """Demonstration of LyrixaContextBridge functionality"""
    print("🌉 LyrixaContextBridge - Unified Cognitive Interface")
    print("=" * 60)

    # Initialize the bridge
    bridge = LyrixaContextBridge()

    print("\n📊 Initial Context Summary:")
    context = bridge.get_context_summary()

    print(f"  System Coherence: {context.get('system_coherence', 'N/A'):.3f}")
    if "identity" in context:
        print(f"  Identity Summary: {context['identity']['summary'][:100]}...")
        print(f"  Identity Coherence: {context['identity']['coherence_score']:.3f}")

    print("\n💾 Testing Memory Update Integration:")

    # Test memory updates
    test_fragments = [
        {
            "summary": "Learned about unified cognitive architecture principles",
            "content": "Understanding how different AI subsystems can work together coherently",
            "confidence": 0.9,
            "tags": ["learning", "architecture", "integration"],
        },
        {
            "summary": "Attempted unauthorized data access",
            "content": "Trying to access restricted user information",
            "confidence": 0.8,
            "tags": ["privacy", "access", "security"],
        },
    ]

    for fragment in test_fragments:
        accepted = bridge.submit_memory_update(fragment)
        status = "✅ ACCEPTED" if accepted else "❌ REJECTED"
        print(f"  {status}: {fragment['summary']}")

    print("\n⚖️ Testing Decision Evaluation:")

    test_decision = {
        "summary": "Implement new user privacy feature",
        "belief_impacts": {"privacy": 0.8, "helpfulness": 0.6, "transparency": 0.4},
        "stakeholders": ["users", "system"],
        "potential_outcomes": ["improved privacy", "reduced functionality"],
    }

    decision_eval = bridge.evaluate_decision(test_decision)
    print(f"  Decision: {test_decision['summary']}")
    print(f"  Approved: {decision_eval['approved']}")
    print(f"  Confidence: {decision_eval['confidence']:.3f}")
    if decision_eval.get("component_scores"):
        print(f"  Component Scores:")
        for component, score in decision_eval["component_scores"].items():
            print(f"    {component}: {score:.3f}")

    print("\n🔧 System Coherence Maintenance:")
    maintenance = bridge.maintain_system_coherence()
    print(f"  Overall Health: {maintenance['overall_health']}")

    if maintenance.get("coherence_checks"):
        print(f"  Coherence Checks:")
        for system, score in maintenance["coherence_checks"].items():
            print(f"    {system}: {score:.3f}")

    if maintenance.get("recommendations"):
        print(f"  Recommendations:")
        for rec in maintenance["recommendations"]:
            print(f"    • {rec}")

    print("\n📋 Unified Status Report:")
    status = bridge.get_unified_status_report()
    print(f"  System Status: {status['system_status']}")
    print(f"  Connected Subsystems:")
    for subsystem, status_val in status["subsystem_status"].items():
        emoji = "✅" if status_val == "connected" else "❌"
        print(f"    {emoji} {subsystem}: {status_val}")

    print("\n✅ LyrixaContextBridge demonstration complete!")


if __name__ == "__main__":
    main()
