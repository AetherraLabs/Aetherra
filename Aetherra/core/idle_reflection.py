#!/usr/bin/env python3
"""
🧠 Idle Reflection System for Lyrixa
====================================

This module implements the "Idle Reflection" feature, which processes and organizes
recent memories, generates insights, and prepares suggestions when the system is idle.
Integrated with Aetherra's autonomous capabilities.
"""

import asyncio
import threading
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

# Try to import Aetherra components with fallback
try:
    from Aetherra.core.engine.reasoning_engine import ReasoningEngine, ReasoningContext
    from Aetherra.core.engine.introspection_controller import IntrospectionController
    HAS_AETHERRA_ENGINES = True
except ImportError:
    HAS_AETHERRA_ENGINES = False
    logger.warning("Aetherra engines not available, using mock implementations")

    # Create mock classes
    class MockResult:
        def __init__(self):
            self.conclusion = 'Basic pattern analysis completed'
            self.alternatives = ['General insight available']
            self.confidence = 0.5

    class ReasoningEngine:
        async def reason(self, context):
            return MockResult()

    class ReasoningContext:
        def __init__(self, query, domain, context_data, constraints, objectives):
            self.query = query
            self.domain = domain
            self.context_data = context_data
            self.constraints = constraints
            self.objectives = objectives

    class IntrospectionController:
        def get_current_health(self):
            return {"status": "unknown", "timestamp": datetime.now().isoformat()}

# Try to import memory system
try:
    from Aetherra.lyrixa.enhanced_memory_system import LyrixaEnhancedMemorySystem
    HAS_MEMORY_SYSTEM = True
except ImportError:
    HAS_MEMORY_SYSTEM = False
    # Create a mock class for type hints
    class LyrixaEnhancedMemorySystem:
        async def get_recent_memories(self, limit=100):
            return []

        async def store_enhanced_memory(self, content, context, tags, importance):
            pass


class IdleReflectionSystem:
    """🧠 Idle Reflection System for Lyrixa with Aetherra Integration"""

    def __init__(self,
                 memory_instance: Optional[LyrixaEnhancedMemorySystem] = None,
                 workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.memory = memory_instance
        self.is_running = False
        self.reflection_thread = None
        self.last_reflection = None
        self.reflection_insights = []

        # Configuration
        self.config = {
            "reflection_interval": 180,  # 3 minutes when idle
            "max_insights_per_cycle": 10,
            "memory_analysis_limit": 100,
            "insight_retention_days": 7,
            "min_idle_time": 30,  # seconds before starting reflection
        }

        # Initialize engines if available
        if HAS_AETHERRA_ENGINES:
            self.reasoning_engine = ReasoningEngine()
            self.introspection_controller = IntrospectionController()
            logger.info("✅ Idle Reflection initialized with Aetherra engines")
        else:
            self.reasoning_engine = None
            self.introspection_controller = None
            logger.info("⚠️ Idle Reflection initialized without Aetherra engines")

        # Reflection state
        self.reflection_state = {
            "cycles_completed": 0,
            "insights_generated": 0,
            "last_reflection_time": None,
            "current_focus": "general",
            "reflection_quality": 0.0,
            "active_themes": [],
            "pending_suggestions": []
        }

        logger.info("🧠 Idle Reflection System initialized")

    def start(self):
        """Start the idle reflection system."""
        if not self.is_running:
            self.is_running = True
            self.reflection_thread = threading.Thread(
                target=self._reflection_loop, daemon=True
            )
            self.reflection_thread.start()
            logger.info("🚀 Idle Reflection System started")

    def stop(self):
        """Stop the idle reflection system."""
        self.is_running = False
        if self.reflection_thread:
            self.reflection_thread.join()
        logger.info("⏹️ Idle Reflection System stopped")

    def _reflection_loop(self):
        """Periodic reflection loop."""
        while self.is_running:
            try:
                self._perform_reflection()
                self.reflection_state["cycles_completed"] += 1
                self.reflection_state["last_reflection_time"] = datetime.now()

                # Adaptive interval based on activity
                sleep_time = self._calculate_next_interval()
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in reflection loop: {e}")
                time.sleep(self.config["reflection_interval"])

    def _calculate_next_interval(self) -> float:
        """Calculate adaptive interval based on system activity"""
        base_interval = self.config["reflection_interval"]

        # Adjust based on recent activity
        if self.memory:
            try:
                # Check for recent activity
                recent_memories = asyncio.run(self.memory.get_recent_memories(limit=10))
                if recent_memories:
                    last_activity = recent_memories[0].get("timestamp", datetime.now())
                    if isinstance(last_activity, str):
                        last_activity = datetime.fromisoformat(last_activity)

                    idle_time = (datetime.now() - last_activity).total_seconds()

                    # Shorter interval if recently active
                    if idle_time < 300:  # 5 minutes
                        return base_interval * 0.5
                    elif idle_time > 1800:  # 30 minutes
                        return base_interval * 2

            except Exception as e:
                logger.error(f"Error calculating interval: {e}")

        return base_interval

    def _perform_reflection(self):
        """Synchronous wrapper for reflection"""
        try:
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._perform_reflection_async())
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error in sync reflection: {e}")

    async def _perform_reflection_async(self):
        """Perform a single reflection cycle."""
        try:
            logger.info("🧠 Starting reflection cycle...")

            # 1. Gather recent memories and experiences
            context_data = await self._gather_reflection_context()

            # 2. Analyze patterns and themes
            insights = await self._analyze_patterns(context_data)

            # 3. Generate actionable suggestions
            suggestions = await self._generate_suggestions(insights)

            # 4. Update reflection state
            self._update_reflection_state(insights, suggestions)

            # 5. Store insights for future reference
            await self._store_reflection_results(insights, suggestions)

            logger.info(f"✅ Reflection cycle completed - {len(insights)} insights generated")

        except Exception as e:
            logger.error(f"Error in reflection cycle: {e}")

    async def _gather_reflection_context(self) -> Dict[str, Any]:
        """Gather context data for reflection"""
        context = {
            "recent_memories": [],
            "interaction_patterns": {},
            "system_health": {},
            "user_preferences": {},
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Get recent memories
            if self.memory:
                recent_memories = await self.memory.get_recent_memories(
                    limit=self.config["memory_analysis_limit"]
                )
                context["recent_memories"] = recent_memories

                # Analyze interaction patterns
                context["interaction_patterns"] = await self._analyze_interaction_patterns(recent_memories)

            # Get system health if available
            if self.introspection_controller:
                try:
                    health_data = self.introspection_controller.get_current_health()
                    context["system_health"] = health_data
                except Exception as e:
                    logger.warning(f"Could not get system health: {e}")

        except Exception as e:
            logger.error(f"Error gathering reflection context: {e}")

        return context

    async def _analyze_interaction_patterns(self, memories: List[Dict]) -> Dict[str, Any]:
        """Analyze user interaction patterns"""
        patterns = {
            "frequent_topics": {},
            "interaction_frequency": 0,
            "preferred_communication_style": "unknown",
            "common_requests": [],
            "user_satisfaction_indicators": []
        }

        try:
            # Analyze topics
            for memory in memories:
                content = memory.get("content", {})
                if isinstance(content, dict):
                    topic = content.get("topic", "general")
                    patterns["frequent_topics"][topic] = patterns["frequent_topics"].get(topic, 0) + 1

            # Calculate interaction frequency
            if memories:
                time_span = (datetime.now() - datetime.fromisoformat(memories[-1].get("timestamp", datetime.now().isoformat()))).total_seconds()
                patterns["interaction_frequency"] = len(memories) / max(time_span / 3600, 1)  # interactions per hour

        except Exception as e:
            logger.error(f"Error analyzing interaction patterns: {e}")

        return patterns

    async def _analyze_patterns(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in the context data to generate insights"""
        insights = []

        try:
            if self.reasoning_engine:
                # Use Aetherra reasoning engine
                reasoning_context = ReasoningContext(
                    query="What patterns and insights can be derived from recent system activity and user interactions?",
                    domain="idle_reflection",
                    context_data=context_data,
                    constraints=["focus_on_actionable_insights", "consider_user_experience"],
                    objectives=["identify_improvement_opportunities", "detect_usage_patterns", "suggest_optimizations"]
                )

                reasoning_result = await self.reasoning_engine.reason(reasoning_context)

                # Extract insights from reasoning result
                if hasattr(reasoning_result, 'alternatives') and reasoning_result.alternatives:
                    for alternative in reasoning_result.alternatives:
                        insights.append({
                            "type": "pattern_analysis",
                            "insight": alternative,
                            "confidence": reasoning_result.confidence,
                            "source": "aetherra_reasoning",
                            "timestamp": datetime.now().isoformat()
                        })

                # Add main conclusion as insight
                insights.append({
                    "type": "primary_conclusion",
                    "insight": reasoning_result.conclusion,
                    "confidence": reasoning_result.confidence,
                    "source": "aetherra_reasoning",
                    "timestamp": datetime.now().isoformat()
                })

            else:
                # Fallback pattern analysis
                insights.extend(self._basic_pattern_analysis(context_data))

        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            # Fallback to basic analysis
            insights.extend(self._basic_pattern_analysis(context_data))

        return insights

    def _basic_pattern_analysis(self, context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Basic pattern analysis without reasoning engine"""
        insights = []

        try:
            # Analyze memory patterns
            memories = context_data.get("recent_memories", [])
            if memories:
                insights.append({
                    "type": "activity_level",
                    "insight": f"Processed {len(memories)} recent memories, indicating {'high' if len(memories) > 50 else 'moderate'} activity level",
                    "confidence": 0.7,
                    "source": "basic_analysis",
                    "timestamp": datetime.now().isoformat()
                })

            # Analyze interaction patterns
            patterns = context_data.get("interaction_patterns", {})
            if patterns.get("frequent_topics"):
                top_topic = max(patterns["frequent_topics"].items(), key=lambda x: x[1])
                insights.append({
                    "type": "topic_preference",
                    "insight": f"Most frequent topic: {top_topic[0]} with {top_topic[1]} occurrences",
                    "confidence": 0.8,
                    "source": "basic_analysis",
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Error in basic pattern analysis: {e}")

        return insights

    async def _generate_suggestions(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate actionable suggestions based on insights"""
        suggestions = []

        try:
            if self.reasoning_engine and insights:
                # Use Aetherra reasoning to generate suggestions
                insight_summary = "\n".join([insight["insight"] for insight in insights])

                reasoning_context = ReasoningContext(
                    query=f"Based on these insights, what actionable suggestions can improve user experience and system performance? Insights: {insight_summary}",
                    domain="suggestion_generation",
                    context_data={"insights": insights},
                    constraints=["actionable", "realistic", "user_focused"],
                    objectives=["improve_user_experience", "optimize_system_performance", "enhance_engagement"]
                )

                reasoning_result = await self.reasoning_engine.reason(reasoning_context)

                # Extract suggestions
                if hasattr(reasoning_result, 'alternatives') and reasoning_result.alternatives:
                    for i, alternative in enumerate(reasoning_result.alternatives):
                        suggestions.append({
                            "id": f"suggestion_{i+1}",
                            "suggestion": alternative,
                            "priority": "medium",
                            "confidence": reasoning_result.confidence,
                            "source": "aetherra_reasoning",
                            "timestamp": datetime.now().isoformat(),
                            "status": "pending"
                        })

            else:
                # Fallback suggestions
                suggestions.extend(self._basic_suggestions(insights))

        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            suggestions.extend(self._basic_suggestions(insights))

        return suggestions

    def _basic_suggestions(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate basic suggestions"""
        suggestions = []

        try:
            # General suggestions based on insights
            for insight in insights:
                if insight["type"] == "activity_level":
                    suggestions.append({
                        "id": f"activity_suggestion_{len(suggestions)+1}",
                        "suggestion": "Consider adjusting response patterns based on activity level",
                        "priority": "low",
                        "confidence": 0.6,
                        "source": "basic_analysis",
                        "timestamp": datetime.now().isoformat(),
                        "status": "pending"
                    })

        except Exception as e:
            logger.error(f"Error generating basic suggestions: {e}")

        return suggestions

    def _update_reflection_state(self, insights: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]):
        """Update internal reflection state"""
        self.reflection_state["insights_generated"] += len(insights)
        self.reflection_state["pending_suggestions"].extend(suggestions)

        # Extract themes
        themes = []
        for insight in insights:
            if insight.get("type"):
                themes.append(insight["type"])

        self.reflection_state["active_themes"] = list(set(themes))

        # Calculate reflection quality
        if insights:
            avg_confidence = sum(insight.get("confidence", 0) for insight in insights) / len(insights)
            self.reflection_state["reflection_quality"] = avg_confidence

    async def _store_reflection_results(self, insights: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]):
        """Store reflection results in memory"""
        try:
            if self.memory:
                # Store as enhanced memory
                reflection_data = {
                    "type": "idle_reflection",
                    "insights": insights,
                    "suggestions": suggestions,
                    "reflection_state": self.reflection_state.copy(),
                    "timestamp": datetime.now().isoformat()
                }

                await self.memory.store_enhanced_memory(
                    content=reflection_data,
                    context={"type": "system_reflection", "automated": True},
                    tags=["reflection", "insights", "automated"],
                    importance=0.6
                )

                logger.info(f"📝 Stored reflection results: {len(insights)} insights, {len(suggestions)} suggestions")

        except Exception as e:
            logger.error(f"Error storing reflection results: {e}")

    def get_reflection_status(self) -> Dict[str, Any]:
        """Get current reflection system status"""
        return {
            "is_running": self.is_running,
            "has_aetherra_engines": HAS_AETHERRA_ENGINES,
            "reflection_state": self.reflection_state.copy(),
            "config": self.config.copy(),
            "last_reflection": self.last_reflection.isoformat() if self.last_reflection else None
        }

    def get_recent_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent insights from reflection"""
        return self.reflection_insights[-limit:] if self.reflection_insights else []

    def get_pending_suggestions(self) -> List[Dict[str, Any]]:
        """Get pending suggestions"""
        return self.reflection_state.get("pending_suggestions", [])

    def mark_suggestion_completed(self, suggestion_id: str):
        """Mark a suggestion as completed"""
        suggestions = self.reflection_state.get("pending_suggestions", [])
        for suggestion in suggestions:
            if suggestion.get("id") == suggestion_id:
                suggestion["status"] = "completed"
                suggestion["completed_at"] = datetime.now().isoformat()
                break


# Factory function for easy integration
def create_idle_reflection_system(memory_instance=None, workspace_path=".") -> IdleReflectionSystem:
    """Create and return an idle reflection system instance"""
    return IdleReflectionSystem(memory_instance=memory_instance, workspace_path=workspace_path)


if __name__ == "__main__":
    # Example usage
    reflection_system = IdleReflectionSystem()
    reflection_system.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        reflection_system.stop()
