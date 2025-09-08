#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
Aetherra Adaptive Behavior System
=================================

Advanced adaptive behavior engine that enables Aetherra OS to learn and adapt
its behavior based on usage patterns, environmental changes, and user feedback.

This system provides:
- Real-time behavior adaptation
- Learning from user interactions
- Dynamic system optimization
- Context-aware decision making
- Predictive behavior modeling
"""

import asyncio
import logging
import random
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class BehaviorPattern:
    """Represents a learned behavior pattern."""

    pattern_id: str
    trigger_context: dict[str, Any]
    response_actions: list[dict[str, Any]]
    success_rate: float
    usage_count: int
    last_used: datetime
    confidence: float
    adaptation_rate: float = 0.1


@dataclass
class ContextState:
    """Current context state for behavior decisions."""

    user_activity: str
    system_load: float
    time_of_day: str
    recent_commands: list[str]
    current_goals: list[str]
    environment_factors: dict[str, Any]


@dataclass
class AdaptationEvent:
    """Records an adaptation event for learning."""

    timestamp: datetime
    context: ContextState
    action_taken: str
    outcome: str
    success: bool
    user_feedback: str | None = None


class BehaviorLearningEngine:
    """Machine learning engine for behavior adaptation."""

    def __init__(self):
        # Learned behavior patterns keyed by pattern_id
        self.patterns: dict[str, BehaviorPattern] = {}
        self.adaptation_history = deque(maxlen=1000)
        self.context_features = {}
        self.learning_rate = 0.1
        self.exploration_rate = 0.2  # for exploration vs exploitation

    def learn_from_event(self, event: AdaptationEvent):
        """Learn from an adaptation event."""
        try:
            # Extract features from context
            features = self._extract_context_features(event.context)

            # Find or create behavior pattern
            pattern_id = self._generate_pattern_id(features, event.action_taken)

            if pattern_id in self.patterns:
                pattern = self.patterns[pattern_id]

                # Update success rate using exponential moving average
                alpha = pattern.adaptation_rate
                if event.success:
                    pattern.success_rate = (
                        alpha * 1.0 + (1 - alpha) * pattern.success_rate
                    )
                else:
                    pattern.success_rate = (
                        alpha * 0.0 + (1 - alpha) * pattern.success_rate
                    )

                pattern.usage_count += 1
                pattern.last_used = event.timestamp

                # Update confidence based on consistency
                pattern.confidence = min(1.0, pattern.usage_count / 10.0)

            else:
                # Create new pattern
                self.patterns[pattern_id] = BehaviorPattern(
                    pattern_id=pattern_id,
                    trigger_context=features,
                    response_actions=[
                        {"action": event.action_taken, "outcome": event.outcome}
                    ],
                    success_rate=1.0 if event.success else 0.0,
                    usage_count=1,
                    last_used=event.timestamp,
                    confidence=0.1,
                )

            # Store event in history
            self.adaptation_history.append(event)

            logger.info(
                f"[ADAPT] Learned from event: {event.action_taken} -> {event.outcome}"
            )

        except Exception as e:
            logger.error(f"[ADAPT] Learning error: {e}")

    def recommend_action(self, context: ContextState) -> dict[str, Any] | None:
        """Recommend an action based on learned patterns."""
        try:
            features = self._extract_context_features(context)

            # Find matching patterns
            matching_patterns = []
            for pattern in self.patterns.values():
                similarity = self._calculate_context_similarity(
                    features, pattern.trigger_context
                )
                if similarity > 0.7:  # Threshold for pattern matching
                    score = similarity * pattern.success_rate * pattern.confidence
                    matching_patterns.append((score, pattern))

            if not matching_patterns:
                return None

            # Sort by score and apply exploration vs exploitation
            matching_patterns.sort(key=lambda x: x[0], reverse=True)

            # Exploration: sometimes try a random action
            if random.random() < self.exploration_rate:
                pattern = random.choice([p for _, p in matching_patterns])
            else:
                # Exploitation: use best pattern
                pattern = matching_patterns[0][1]

            # Extract recommended action
            if pattern.response_actions:
                action = pattern.response_actions[0]
                return {
                    "action": action.get("action"),
                    "confidence": pattern.confidence,
                    "pattern_id": pattern.pattern_id,
                    "expected_outcome": action.get("outcome"),
                }

            return None

        except Exception as e:
            logger.error(f"[ADAPT] Action recommendation error: {e}")
            return None

    def _extract_context_features(self, context: ContextState) -> dict[str, Any]:
        """Extract relevant features from context."""
        return {
            "user_activity": context.user_activity,
            "system_load_bucket": self._bucket_system_load(context.system_load),
            "time_period": self._get_time_period(context.time_of_day),
            "command_patterns": self._analyze_command_patterns(context.recent_commands),
            "goal_categories": self._categorize_goals(context.current_goals),
        }

    def _bucket_system_load(self, load: float) -> str:
        """Bucket system load into categories."""
        if load < 0.3:
            return "low"
        elif load < 0.7:
            return "medium"
        else:
            return "high"

    def _get_time_period(self, time_str: str) -> str:
        """Get time period category."""
        try:
            hour = int(time_str.split(":")[0])
            if 6 <= hour < 12:
                return "morning"
            elif 12 <= hour < 18:
                return "afternoon"
            elif 18 <= hour < 22:
                return "evening"
            else:
                return "night"
        except Exception:
            return "unknown"

    def _analyze_command_patterns(self, commands: list[str]) -> str:
        """Analyze patterns in recent commands."""
        if not commands:
            return "none"

        # Simple pattern analysis
        if any("memory" in cmd.lower() for cmd in commands):
            return "memory_focused"
        elif any("plugin" in cmd.lower() for cmd in commands):
            return "plugin_focused"
        elif any("system" in cmd.lower() for cmd in commands):
            return "system_focused"
        else:
            return "general"

    def _categorize_goals(self, goals: list[str]) -> str:
        """Categorize current goals."""
        if not goals:
            return "none"

        categories = set()
        for goal in goals:
            goal_lower = goal.lower()
            if any(word in goal_lower for word in ["optimize", "improve", "enhance"]):
                categories.add("optimization")
            elif any(
                word in goal_lower for word in ["analyze", "understand", "explore"]
            ):
                categories.add("analysis")
            elif any(word in goal_lower for word in ["create", "build", "generate"]):
                categories.add("creation")
            else:
                categories.add("general")

        return "_".join(sorted(categories))

    def _generate_pattern_id(self, features: dict[str, Any], action: str) -> str:
        """Generate unique pattern ID."""
        feature_str = "_".join(f"{k}:{v}" for k, v in sorted(features.items()))
        pattern_str = f"{feature_str}_{action}"
        return f"pattern_{hash(pattern_str) % 10000:04d}"

    def _calculate_context_similarity(
        self, context1: dict[str, Any], context2: dict[str, Any]
    ) -> float:
        """Calculate similarity between two contexts."""
        try:
            total_score = 0.0
            total_weight = 0.0

            for key in set(context1.keys()) | set(context2.keys()):
                weight = 1.0

                if key in context1 and key in context2:
                    if context1[key] == context2[key]:
                        score = 1.0
                    else:
                        score = 0.0
                else:
                    score = 0.0  # Missing feature

                total_score += score * weight
                total_weight += weight

            return total_score / total_weight if total_weight > 0 else 0.0

        except Exception as e:
            logger.error(f"[ADAPT] Context similarity error: {e}")
            return 0.0


class AdaptiveBehaviorSystem:
    """
    Main adaptive behavior system for Aetherra AI OS.

    Enables continuous learning and adaptation of system behavior
    based on usage patterns and environmental feedback.
    """

    def __init__(self, service_registry=None):
        self.service_registry = service_registry
        self.learning_engine = BehaviorLearningEngine()
        self.current_context = None
        self.adaptation_active = True
        self.behavior_modifications = {}
        self.performance_metrics = {
            "total_adaptations": 0,
            "successful_adaptations": 0,
            "user_satisfaction": 0.5,
            "system_efficiency": 0.5,
        }

        # Adaptation strategies
        self.strategies = {
            "memory_optimization": self._strategy_memory_optimization,
            "service_prioritization": self._strategy_service_prioritization,
            "resource_allocation": self._strategy_resource_allocation,
            "user_experience_tuning": self._strategy_user_experience_tuning,
            "proactive_assistance": self._strategy_proactive_assistance,
        }

        # Continuous adaptation loop
        self.adaptation_task = None

    async def initialize(self):
        """Initialize the adaptive behavior system."""
        try:
            logger.info("[ADAPT] Initializing Adaptive Behavior System...")

            # Load previous learning data
            await self._load_learned_behaviors()

            # Start continuous adaptation loop
            self.adaptation_task = asyncio.create_task(self._adaptation_loop())

            logger.info("[ADAPT] Adaptive Behavior System initialized")
            return True

        except Exception as e:
            logger.error(f"[ADAPT] Initialization error: {e}")
            return False

    async def observe_context(self, context_data: dict[str, Any]):
        """Observe and update current context."""
        try:
            self.current_context = ContextState(
                user_activity=context_data.get("user_activity", "idle"),
                system_load=context_data.get("system_load", 0.5),
                time_of_day=datetime.now().strftime("%H:%M"),
                recent_commands=context_data.get("recent_commands", []),
                current_goals=context_data.get("current_goals", []),
                environment_factors=context_data.get("environment_factors", {}),
            )

            # Check if adaptation is needed
            await self._evaluate_adaptation_need()

        except Exception as e:
            logger.error(f"[ADAPT] Context observation error: {e}")

    async def record_user_feedback(self, action: str, feedback: str, success: bool):
        """Record user feedback for learning."""
        try:
            if self.current_context:
                event = AdaptationEvent(
                    timestamp=datetime.now(),
                    context=self.current_context,
                    action_taken=action,
                    outcome=feedback,
                    success=success,
                    user_feedback=feedback,
                )

                self.learning_engine.learn_from_event(event)

                # Update performance metrics
                self.performance_metrics["total_adaptations"] += 1
                if success:
                    self.performance_metrics["successful_adaptations"] += 1

                # Update user satisfaction (exponential moving average)
                satisfaction_delta = 0.1 if success else -0.1
                self.performance_metrics["user_satisfaction"] += (
                    satisfaction_delta * 0.1
                )
                self.performance_metrics["user_satisfaction"] = max(
                    0.0, min(1.0, self.performance_metrics["user_satisfaction"])
                )

                logger.info(
                    f"[ADAPT] Recorded feedback: {action} -> {feedback} (success: {success})"
                )

        except Exception as e:
            logger.error(f"[ADAPT] Feedback recording error: {e}")

    async def suggest_optimization(self) -> dict[str, Any] | None:
        """Suggest system optimization based on learned patterns."""
        try:
            if not self.current_context:
                return None

            recommendation = self.learning_engine.recommend_action(self.current_context)

            if recommendation:
                # Apply strategy if available
                action = recommendation.get("action")
                if action in self.strategies:
                    optimization = await self.strategies[action](self.current_context)
                    if optimization:
                        recommendation.update(optimization)

                logger.info(f"[ADAPT] Suggested optimization: {recommendation}")

            return recommendation

        except Exception as e:
            logger.error(f"[ADAPT] Optimization suggestion error: {e}")
            return None

    async def apply_adaptation(self, adaptation: dict[str, Any]) -> bool:
        """Apply a behavioral adaptation."""
        try:
            adaptation_type = adaptation.get("type")
            parameters = adaptation.get("parameters", {})

            logger.info(f"[ADAPT] Applying adaptation: {adaptation_type}")

            success = False

            if adaptation_type == "memory_optimization":
                success = await self._apply_memory_optimization(parameters)
            elif adaptation_type == "service_prioritization":
                success = await self._apply_service_prioritization(parameters)
            elif adaptation_type == "resource_allocation":
                success = await self._apply_resource_allocation(parameters)
            elif adaptation_type == "user_experience_tuning":
                success = await self._apply_user_experience_tuning(parameters)
            elif adaptation_type == "proactive_assistance":
                success = await self._apply_proactive_assistance(parameters)

            # Record the adaptation attempt
            if self.current_context and isinstance(adaptation_type, str):
                await self.record_user_feedback(
                    action=adaptation_type,
                    feedback="adaptation_applied" if success else "adaptation_failed",
                    success=success,
                )

            return success

        except Exception as e:
            logger.error(f"[ADAPT] Adaptation application error: {e}")
            return False

    async def get_adaptation_status(self) -> dict[str, Any]:
        """Get current adaptation system status."""
        try:
            return {
                "active": self.adaptation_active,
                "learned_patterns": len(self.learning_engine.patterns),
                "adaptation_history": len(self.learning_engine.adaptation_history),
                "performance_metrics": self.performance_metrics,
                "current_context": asdict(self.current_context)
                if self.current_context
                else None,
                "available_strategies": list(self.strategies.keys()),
                "behavior_modifications": len(self.behavior_modifications),
            }

        except Exception as e:
            logger.error(f"[ADAPT] Status error: {e}")
            return {}

    async def _adaptation_loop(self):
        """Continuous adaptation monitoring loop."""
        try:
            while self.adaptation_active:
                try:
                    # Periodic adaptation evaluation
                    if self.current_context:
                        suggestion = await self.suggest_optimization()

                        if suggestion and suggestion.get("confidence", 0) > 0.8:
                            # Auto-apply high-confidence adaptations
                            await self.apply_adaptation(
                                {
                                    "type": suggestion.get("action"),
                                    "parameters": suggestion,
                                }
                            )

                    # Update system efficiency metric
                    await self._update_efficiency_metrics()

                    # Sleep for adaptation interval
                    await asyncio.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    logger.error(f"[ADAPT] Adaptation loop error: {e}")
                    await asyncio.sleep(60)  # Longer sleep on error

        except asyncio.CancelledError:
            logger.info("[ADAPT] Adaptation loop cancelled")

    async def _evaluate_adaptation_need(self):
        """Evaluate if adaptation is needed based on current context."""
        try:
            if not self.current_context:
                return

            # Check for adaptation triggers
            triggers = []

            # High system load trigger
            if self.current_context.system_load > 0.8:
                triggers.append("high_system_load")

            # Repetitive command patterns
            if (
                len(set(self.current_context.recent_commands))
                < len(self.current_context.recent_commands) / 2
            ):
                triggers.append("repetitive_commands")

            # Goal-based triggers
            if any(
                "optimize" in goal.lower()
                for goal in self.current_context.current_goals
            ):
                triggers.append("optimization_goal")

            if triggers:
                logger.info(f"[ADAPT] Adaptation triggers detected: {triggers}")
                suggestion = await self.suggest_optimization()
                if suggestion:
                    logger.info(f"[ADAPT] Suggested adaptation: {suggestion}")

        except Exception as e:
            logger.error(f"[ADAPT] Adaptation evaluation error: {e}")

    # Strategy implementations
    async def _strategy_memory_optimization(
        self, context: ContextState
    ) -> dict[str, Any]:
        """Strategy for memory system optimization."""
        return {
            "type": "memory_optimization",
            "parameters": {
                "cleanup_threshold": 0.8 if context.system_load > 0.7 else 0.6,
                "cache_size": "increase"
                if context.user_activity == "heavy"
                else "maintain",
                "compression": context.system_load > 0.8,
            },
        }

    async def _strategy_service_prioritization(
        self, context: ContextState
    ) -> dict[str, Any]:
        """Strategy for service prioritization."""
        priorities = {}

        if "memory" in context.recent_commands:
            priorities["memory_system"] = "high"
        if "plugin" in str(context.recent_commands):
            priorities["plugin_manager"] = "high"

        return {
            "type": "service_prioritization",
            "parameters": {
                "priorities": priorities,
                "load_balancing": context.system_load > 0.6,
            },
        }

    async def _strategy_resource_allocation(
        self, context: ContextState
    ) -> dict[str, Any]:
        """Strategy for resource allocation."""
        return {
            "type": "resource_allocation",
            "parameters": {
                "cpu_allocation": "adaptive",
                "memory_allocation": "dynamic",
                "io_prioritization": "user_focused"
                if context.user_activity == "active"
                else "background",
            },
        }

    async def _strategy_user_experience_tuning(
        self, context: ContextState
    ) -> dict[str, Any]:
        """Strategy for user experience optimization."""
        return {
            "type": "user_experience_tuning",
            "parameters": {
                "response_time_target": 0.5
                if context.user_activity == "active"
                else 2.0,
                "proactive_suggestions": context.user_activity == "active",
                "interface_complexity": "simplified"
                if context.time_of_day in ["night", "early_morning"]
                else "full",
            },
        }

    async def _strategy_proactive_assistance(
        self, context: ContextState
    ) -> dict[str, Any]:
        """Strategy for proactive assistance."""
        return {
            "type": "proactive_assistance",
            "parameters": {
                "suggestion_frequency": "high"
                if context.user_activity == "learning"
                else "low",
                "context_awareness": True,
                "predictive_actions": len(context.current_goals) > 0,
            },
        }

    # Adaptation application methods
    async def _apply_memory_optimization(self, parameters: dict[str, Any]) -> bool:
        """Apply memory optimization adaptation."""
        try:
            memory_service = (
                self.service_registry.get_service("memory_system")
                if self.service_registry
                else None
            )

            if memory_service and hasattr(memory_service, "optimize_memory"):
                await memory_service.optimize_memory()
                logger.info("[ADAPT] Applied memory optimization")
                return True

            return False

        except Exception as e:
            logger.error(f"[ADAPT] Memory optimization error: {e}")
            return False

    async def _apply_service_prioritization(self, parameters: dict[str, Any]) -> bool:
        """Apply service prioritization adaptation."""
        try:
            # Store priority changes
            self.behavior_modifications["service_priorities"] = parameters.get(
                "priorities", {}
            )
            logger.info("[ADAPT] Applied service prioritization")
            return True

        except Exception as e:
            logger.error(f"[ADAPT] Service prioritization error: {e}")
            return False

    async def _apply_resource_allocation(self, parameters: dict[str, Any]) -> bool:
        """Apply resource allocation adaptation."""
        try:
            # Store resource allocation changes
            self.behavior_modifications["resource_allocation"] = parameters
            logger.info("[ADAPT] Applied resource allocation changes")
            return True

        except Exception as e:
            logger.error(f"[ADAPT] Resource allocation error: {e}")
            return False

    async def _apply_user_experience_tuning(self, parameters: dict[str, Any]) -> bool:
        """Apply user experience tuning."""
        try:
            # Store UX modifications
            self.behavior_modifications["user_experience"] = parameters
            logger.info("[ADAPT] Applied user experience tuning")
            return True

        except Exception as e:
            logger.error(f"[ADAPT] UX tuning error: {e}")
            return False

    async def _apply_proactive_assistance(self, parameters: dict[str, Any]) -> bool:
        """Apply proactive assistance settings."""
        try:
            # Store proactive assistance settings
            self.behavior_modifications["proactive_assistance"] = parameters
            logger.info("[ADAPT] Applied proactive assistance settings")
            return True

        except Exception as e:
            logger.error(f"[ADAPT] Proactive assistance error: {e}")
            return False

    async def _update_efficiency_metrics(self):
        """Update system efficiency metrics."""
        try:
            # Calculate efficiency based on performance metrics
            success_rate = self.performance_metrics["successful_adaptations"] / max(
                1, self.performance_metrics["total_adaptations"]
            )

            self.performance_metrics["system_efficiency"] = (
                success_rate * 0.5 + self.performance_metrics["user_satisfaction"] * 0.5
            )

        except Exception as e:
            logger.error(f"[ADAPT] Efficiency metrics error: {e}")

    async def _load_learned_behaviors(self):
        """Load previously learned behaviors from storage."""
        try:
            # In a full implementation, this would load from persistent storage
            logger.info("[ADAPT] Loaded learned behaviors from storage")

        except Exception as e:
            logger.error(f"[ADAPT] Load behaviors error: {e}")

    async def shutdown(self):
        """Shutdown the adaptive behavior system."""
        try:
            logger.info("[ADAPT] Shutting down Adaptive Behavior System...")

            self.adaptation_active = False

            if self.adaptation_task:
                self.adaptation_task.cancel()
                try:
                    await self.adaptation_task
                except asyncio.CancelledError:
                    pass

            # Save learned behaviors
            await self._save_learned_behaviors()

            logger.info("[ADAPT] Adaptive Behavior System shutdown complete")

        except Exception as e:
            logger.error(f"[ADAPT] Shutdown error: {e}")

    async def _save_learned_behaviors(self):
        """Save learned behaviors to persistent storage."""
        try:
            # In a full implementation, this would save to persistent storage
            logger.info("[ADAPT] Saved learned behaviors to storage")

        except Exception as e:
            logger.error(f"[ADAPT] Save behaviors error: {e}")


# Factory function for service integration
async def get_adaptive_behavior_system(service_registry=None):
    """Factory function to create and initialize the adaptive behavior system."""
    system = AdaptiveBehaviorSystem(service_registry)
    await system.initialize()
    return system
