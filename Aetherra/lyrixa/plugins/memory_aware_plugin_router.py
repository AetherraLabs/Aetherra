"""
🧠🔌 Memory-Aware Plugin Router
==============================

Routes plugin behavior through concept clusters to enable memory-aware plugin execution.
Provides plugins with relevant memory context and tracks plugin usage patterns.

Core Features:
- Plugin behavior routing through memory concepts
- Memory context injection for enhanced plugin intelligence
- Plugin usage pattern tracking and analysis
- Concept-based plugin recommendation system
- Memory-driven plugin parameter optimization
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set

from ..memory.fractal_mesh.base import MemoryFragment, MemoryFragmentType
from ..memory.fractal_mesh.concepts.concept_clusters import (
    ConceptCluster,
    ConceptClusterManager,
)
from ..memory.lyrixa_memory_engine import LyrixaMemoryEngine

logger = logging.getLogger(__name__)


@dataclass
class PluginMemoryContext:
    """Memory context provided to plugins for enhanced behavior"""

    # Current relevant concepts
    active_concepts: List[str] = field(default_factory=list)
    concept_clusters: List[ConceptCluster] = field(default_factory=list)

    # Relevant memory fragments
    related_fragments: List[MemoryFragment] = field(default_factory=list)
    recent_fragments: List[MemoryFragment] = field(default_factory=list)

    # Usage patterns
    plugin_usage_history: List[Dict[str, Any]] = field(default_factory=list)
    successful_patterns: List[Dict[str, Any]] = field(default_factory=list)

    # Context metadata
    context_confidence: float = 0.0
    memory_depth: int = 0  # How deep in memory chain we're accessing
    temporal_context: str = "current"  # "current", "recent", "historical"


@dataclass
class PluginExecutionResult:
    """Enhanced plugin execution result with memory integration"""

    plugin_name: str
    execution_id: str
    success: bool
    result: Any
    error: Optional[str] = None

    # Memory integration metrics
    memory_context_used: bool = False
    concepts_triggered: List[str] = field(default_factory=list)
    new_memories_created: List[str] = field(default_factory=list)
    execution_confidence: float = 0.0

    # Performance metrics
    execution_time: float = 0.0
    memory_access_time: float = 0.0
    context_relevance_score: float = 0.0

    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    user_context: Optional[str] = None
    goal_context: Optional[str] = None


class MemoryAwarePluginRouter:
    """
    Routes plugin execution through memory concept clusters for enhanced intelligence
    """

    def __init__(
        self,
        memory_engine: LyrixaMemoryEngine,
        concept_manager: ConceptClusterManager,
        max_context_fragments: int = 10,
        context_decay_hours: int = 24,
    ):
        self.memory_engine = memory_engine
        self.concept_manager = concept_manager
        self.max_context_fragments = max_context_fragments
        self.context_decay_hours = context_decay_hours

        # Plugin execution tracking
        self.plugin_executions: List[PluginExecutionResult] = []
        self.concept_plugin_mappings: Dict[str, Set[str]] = {}
        self.plugin_success_patterns: Dict[str, List[Dict[str, Any]]] = {}

        logger.info("🧠🔌 Memory-Aware Plugin Router initialized")

    async def execute_plugin_with_memory_context(
        self,
        plugin_name: str,
        plugin_function: Any,  # callable function
        input_data: Dict[str, Any],
        user_context: Optional[str] = None,
        goal_context: Optional[str] = None,
        **kwargs,
    ) -> PluginExecutionResult:
        """
        Execute plugin with enriched memory context for enhanced behavior
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.now()

        logger.info(f"🔄 Executing plugin '{plugin_name}' with memory context")

        try:
            # Step 1: Generate memory context for the plugin
            memory_context = await self._generate_memory_context(
                plugin_name, input_data, user_context, goal_context
            )

            # Step 2: Enhance input data with memory context
            enhanced_input = await self._enhance_input_with_memory(
                input_data, memory_context
            )

            # Step 3: Execute plugin with enhanced context
            memory_start = datetime.now()
            result = await self._execute_with_context(
                plugin_function, enhanced_input, memory_context, **kwargs
            )
            memory_time = (datetime.now() - memory_start).total_seconds()

            # Step 4: Process results and update memory
            execution_result = PluginExecutionResult(
                plugin_name=plugin_name,
                execution_id=execution_id,
                success=True,
                result=result,
                memory_context_used=True,
                concepts_triggered=memory_context.active_concepts,
                execution_time=(datetime.now() - start_time).total_seconds(),
                memory_access_time=memory_time,
                context_relevance_score=memory_context.context_confidence,
                user_context=user_context,
                goal_context=goal_context,
            )

            # Step 5: Store execution in memory and update patterns
            await self._record_plugin_execution(execution_result, memory_context)

            logger.info(
                f"✅ Plugin '{plugin_name}' executed successfully with "
                f"{len(memory_context.active_concepts)} concept triggers"
            )

            return execution_result

        except Exception as e:
            logger.error(f"❌ Plugin '{plugin_name}' execution failed: {e}")

            execution_result = PluginExecutionResult(
                plugin_name=plugin_name,
                execution_id=execution_id,
                success=False,
                result=None,
                error=str(e),
                execution_time=(datetime.now() - start_time).total_seconds(),
                user_context=user_context,
                goal_context=goal_context,
            )

            await self._record_plugin_execution(execution_result, None)
            return execution_result

    async def _generate_memory_context(
        self,
        plugin_name: str,
        input_data: Dict[str, Any],
        user_context: Optional[str],
        goal_context: Optional[str],
    ) -> PluginMemoryContext:
        """Generate relevant memory context for plugin execution"""

        # Extract key concepts from input and context
        context_text = f"{plugin_name} {json.dumps(input_data)}"
        if user_context:
            context_text += f" {user_context}"
        if goal_context:
            context_text += f" {goal_context}"

        # Query memory for relevant fragments
        try:
            recall_result = await self.memory_engine.recall(
                query=context_text, limit=self.max_context_fragments
            )

            related_fragments = recall_result if isinstance(recall_result, list) else []
            concepts = set()

            # Extract concepts from fragments
            for fragment in related_fragments:
                if isinstance(fragment, dict) and "concepts" in fragment:
                    concepts.update(fragment.get("concepts", []))
                elif hasattr(fragment, "symbolic_tags"):
                    concepts.update(fragment.symbolic_tags)

            # Get concept clusters
            active_concepts = list(concepts)
            concept_clusters = []
            for concept in active_concepts:
                clusters = self.concept_manager.get_concept_clusters(min_strength=0.1)
                concept_clusters.extend(
                    [
                        c
                        for c in clusters
                        if concept in c.related_concepts or concept == c.central_concept
                    ]
                )

            # Get plugin usage history
            plugin_history = self._get_plugin_usage_history(plugin_name)

            # Calculate context confidence
            context_confidence = min(
                1.0, len(related_fragments) / self.max_context_fragments
            )

            return PluginMemoryContext(
                active_concepts=active_concepts,
                concept_clusters=concept_clusters,
                related_fragments=related_fragments,
                plugin_usage_history=plugin_history,
                context_confidence=context_confidence,
                memory_depth=len(related_fragments),
                temporal_context="current" if len(related_fragments) > 5 else "sparse",
            )

        except Exception as e:
            logger.warning(f"Failed to generate memory context: {e}")
            return PluginMemoryContext()

    async def _enhance_input_with_memory(
        self, input_data: Dict[str, Any], memory_context: PluginMemoryContext
    ) -> Dict[str, Any]:
        """Enhance plugin input with relevant memory context"""

        enhanced_input = input_data.copy()

        # Add memory context to input
        enhanced_input["_memory_context"] = {
            "active_concepts": memory_context.active_concepts,
            "related_memories": [
                {
                    "content": frag.content if hasattr(frag, "content") else str(frag),
                    "confidence": getattr(frag, "confidence_score", 0.5),
                    "concepts": list(getattr(frag, "symbolic_tags", set())),
                    "timestamp": getattr(frag, "created_at", datetime.now()).isoformat()
                    if hasattr(frag, "created_at")
                    else datetime.now().isoformat(),
                }
                for frag in memory_context.related_fragments[:5]  # Top 5 most relevant
            ],
            "usage_patterns": memory_context.plugin_usage_history[
                -3:
            ],  # Recent patterns
            "context_confidence": memory_context.context_confidence,
        }

        # Add concept-based recommendations
        if memory_context.active_concepts:
            enhanced_input["_concept_hints"] = await self._get_concept_hints(
                memory_context.active_concepts
            )

        return enhanced_input

    async def _execute_with_context(
        self,
        plugin_function: Any,  # callable function
        enhanced_input: Dict[str, Any],
        memory_context: PluginMemoryContext,
        **kwargs,
    ) -> Any:
        """Execute plugin function with memory context"""

        # Check if plugin supports memory context
        import inspect

        sig = inspect.signature(plugin_function)
        if "_memory_context" in sig.parameters:
            # Plugin is memory-aware
            return await plugin_function(
                enhanced_input, memory_context=memory_context, **kwargs
            )
        else:
            # Legacy plugin - just pass enhanced input
            return await plugin_function(enhanced_input, **kwargs)

    async def _record_plugin_execution(
        self,
        result: PluginExecutionResult,
        memory_context: Optional[PluginMemoryContext],
    ):
        """Record plugin execution in memory and update patterns"""

        # Store execution result
        self.plugin_executions.append(result)

        # Update concept-plugin mappings
        if memory_context and result.success:
            for concept in memory_context.active_concepts:
                if concept not in self.concept_plugin_mappings:
                    self.concept_plugin_mappings[concept] = set()
                self.concept_plugin_mappings[concept].add(result.plugin_name)

        # Create memory fragment for this execution
        execution_fragment = MemoryFragment(
            fragment_id=str(uuid.uuid4()),
            content={
                "plugin_execution": f"Plugin '{result.plugin_name}' executed with "
                f"{'success' if result.success else 'failure'}. "
                f"Concepts: {', '.join(result.concepts_triggered)}",
                "plugin_name": result.plugin_name,
                "execution_id": result.execution_id,
                "success": result.success,
                "execution_time": result.execution_time,
                "context_relevance": result.context_relevance_score,
            },
            fragment_type=MemoryFragmentType.PROCEDURAL,  # Plugin execution is procedural
            temporal_tags={"timestamp": result.timestamp.isoformat()},
            symbolic_tags=set(result.concepts_triggered),
            associative_links=[],
            confidence_score=0.8 if result.success else 0.3,
            access_pattern={"created": result.timestamp.isoformat()},
            narrative_role="plugin_execution",
            created_at=result.timestamp,
            last_evolved=result.timestamp,
        )

        # Store in memory
        try:
            await self.memory_engine.remember(
                content=execution_fragment.content,
                tags=list(execution_fragment.symbolic_tags),
                category="plugin_execution",
                fragment_type=execution_fragment.fragment_type,
                confidence=execution_fragment.confidence_score,
                narrative_role=execution_fragment.narrative_role,
            )
        except Exception as e:
            logger.warning(f"Failed to store plugin execution in memory: {e}")

    def _get_plugin_usage_history(
        self, plugin_name: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get recent usage history for a plugin"""

        cutoff_date = datetime.now() - timedelta(days=days)
        recent_executions = [
            {
                "execution_id": exec.execution_id,
                "success": exec.success,
                "concepts": exec.concepts_triggered,
                "timestamp": exec.timestamp.isoformat(),
                "context_relevance": exec.context_relevance_score,
            }
            for exec in self.plugin_executions
            if exec.plugin_name == plugin_name and exec.timestamp >= cutoff_date
        ]

        return recent_executions[-10:]  # Last 10 executions

    async def _get_concept_hints(self, concepts: List[str]) -> Dict[str, Any]:
        """Generate concept-based hints for plugin execution"""

        hints = {"suggestions": [], "warnings": [], "optimizations": []}

        for concept in concepts:
            # Get successful plugins for this concept
            if concept in self.concept_plugin_mappings:
                successful_plugins = list(self.concept_plugin_mappings[concept])
                hints["suggestions"].append(
                    f"Concept '{concept}' historically works well with: {', '.join(successful_plugins[:3])}"
                )

            # Check for concept contradictions
            contradictions = self.concept_manager.get_recent_contradictions(days=7)
            concept_contradictions = [c for c in contradictions if c.concept == concept]
            if concept_contradictions:
                hints["warnings"].append(
                    f"Recent contradictions detected in concept '{concept}'"
                )

        return hints

    # Public API Methods

    async def get_recommended_plugins_for_context(
        self, context: str, max_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get plugin recommendations based on memory context"""

        # Extract concepts from context
        recall_result = await self.memory_engine.recall(query=context, limit=10)

        fragments = recall_result if isinstance(recall_result, list) else []
        concepts = set()
        for fragment in fragments:
            if isinstance(fragment, dict):
                if "concepts" in fragment:
                    concepts.update(fragment.get("concepts", []))
                elif "symbolic_tags" in fragment:
                    concepts.update(fragment.get("symbolic_tags", []))
            elif hasattr(fragment, "symbolic_tags"):
                concepts.update(getattr(fragment, "symbolic_tags", set()))

        # Find plugins associated with these concepts
        plugin_scores = {}
        for concept in concepts:
            if concept in self.concept_plugin_mappings:
                for plugin in self.concept_plugin_mappings[concept]:
                    if plugin not in plugin_scores:
                        plugin_scores[plugin] = 0
                    plugin_scores[plugin] += 1

        # Sort by score and return top recommendations
        recommendations = [
            {
                "plugin": plugin,
                "relevance_score": score,
                "triggered_concepts": list(concepts),
            }
            for plugin, score in sorted(
                plugin_scores.items(), key=lambda x: x[1], reverse=True
            )[:max_recommendations]
        ]

        return recommendations

    async def analyze_plugin_performance_by_concept(
        self, plugin_name: str
    ) -> Dict[str, Any]:
        """Analyze how a plugin performs across different memory concepts"""

        plugin_executions = [
            exec for exec in self.plugin_executions if exec.plugin_name == plugin_name
        ]

        concept_performance = {}
        for exec in plugin_executions:
            for concept in exec.concepts_triggered:
                if concept not in concept_performance:
                    concept_performance[concept] = {
                        "total_executions": 0,
                        "successful_executions": 0,
                        "avg_execution_time": 0.0,
                        "avg_context_relevance": 0.0,
                    }

                stats = concept_performance[concept]
                stats["total_executions"] += 1
                if exec.success:
                    stats["successful_executions"] += 1
                stats["avg_execution_time"] += exec.execution_time
                stats["avg_context_relevance"] += exec.context_relevance_score

        # Calculate averages
        for concept, stats in concept_performance.items():
            if stats["total_executions"] > 0:
                stats["success_rate"] = (
                    stats["successful_executions"] / stats["total_executions"]
                )
                stats["avg_execution_time"] /= stats["total_executions"]
                stats["avg_context_relevance"] /= stats["total_executions"]

        return {
            "plugin_name": plugin_name,
            "total_executions": len(plugin_executions),
            "overall_success_rate": (
                sum(1 for exec in plugin_executions if exec.success)
                / len(plugin_executions)
                if plugin_executions
                else 0
            ),
            "concept_performance": concept_performance,
        }

    async def get_memory_driven_plugin_insights(self) -> Dict[str, Any]:
        """Get insights about plugin usage patterns based on memory analysis"""

        insights = {
            "most_active_concepts": {},
            "plugin_concept_affinities": {},
            "success_patterns": {},
            "optimization_suggestions": [],
        }

        # Analyze concept activity
        concept_activity = {}
        for exec in self.plugin_executions:
            for concept in exec.concepts_triggered:
                if concept not in concept_activity:
                    concept_activity[concept] = {"count": 0, "success_rate": 0}
                concept_activity[concept]["count"] += 1
                if exec.success:
                    concept_activity[concept]["success_rate"] += 1

        # Calculate success rates
        for concept, data in concept_activity.items():
            data["success_rate"] = data["success_rate"] / data["count"]

        insights["most_active_concepts"] = dict(
            sorted(concept_activity.items(), key=lambda x: x[1]["count"], reverse=True)[
                :10
            ]
        )

        # Generate optimization suggestions
        for concept, plugins in self.concept_plugin_mappings.items():
            if len(plugins) > 1:
                insights["optimization_suggestions"].append(
                    f"Concept '{concept}' triggers multiple plugins - consider consolidation"
                )

        return insights


# Integration with existing plugin manager
class MemoryEnhancedPluginManager:
    """
    Wrapper that enhances existing plugin manager with memory awareness
    """

    def __init__(self, existing_manager, memory_engine: LyrixaMemoryEngine):
        self.plugin_manager = existing_manager
        self.memory_router = MemoryAwarePluginRouter(
            memory_engine=memory_engine,
            concept_manager=memory_engine.concept_manager,
        )

    async def execute_plugin(self, plugin_name: str, *args, **kwargs):
        """Execute plugin with memory awareness"""

        # Get original plugin function
        original_function = getattr(self.plugin_manager, "execute_plugin", None)
        if not original_function:
            raise AttributeError(
                "Original plugin manager doesn't support execute_plugin"
            )

        # Convert args to input_data format
        input_data = {"args": args, "kwargs": kwargs}

        # Execute with memory context
        return await self.memory_router.execute_plugin_with_memory_context(
            plugin_name=plugin_name,
            plugin_function=lambda data, **kw: original_function(
                plugin_name, *data["args"], **data["kwargs"]
            ),
            input_data=input_data,
        )


# Example usage and testing
async def demo_memory_aware_plugin_execution():
    """Demonstrate memory-aware plugin execution"""
    print("🧠🔌 Memory-Aware Plugin Router Demo")
    print("=" * 50)

    # This would integrate with your actual memory engine
    # For demo purposes, we'll show the interface

    print("✅ Plugin router would enhance plugins with:")
    print("   • Relevant memory context from concept clusters")
    print("   • Historical usage patterns and success rates")
    print("   • Concept-based parameter optimization")
    print("   • Cross-plugin memory sharing")
    print("   • Automated performance insights")

    print("\n🎯 Integration complete - plugins are now memory-aware!")


if __name__ == "__main__":
    asyncio.run(demo_memory_aware_plugin_execution())
