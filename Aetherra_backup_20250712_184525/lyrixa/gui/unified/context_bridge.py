"""
Context Bridge Module
====================

Manages cross-subsystem updates and communication between all Lyrixa phases.
Provides a centralized event bus and signal management for real-time data flow.

Cross-Phase Communication Matrix:
- Phase 1 Memory → Phase 4 Intelligence: semantic_events, context_clusters
- Phase 2 Anticipation → Phase 3 Notifications: pending_suggestions, confidence_score
- Phase 3 Performance Monitor → Phase 4 Analytics: resource_trends, agent_cpu_costs
- Phase 4 Feedback → Phase 2+1 Systems: user_preference_delta, suggestion_ratings
"""

import logging
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Set

# Setup logging
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of cross-phase events."""

    MEMORY_UPDATE = "memory_update"
    SEMANTIC_EVENT = "semantic_event"
    CONTEXT_CLUSTER = "context_cluster"
    PENDING_SUGGESTION = "pending_suggestion"
    CONFIDENCE_SCORE = "confidence_score"
    RESOURCE_TREND = "resource_trend"
    AGENT_CPU_COST = "agent_cpu_cost"
    USER_PREFERENCE = "user_preference"
    SUGGESTION_RATING = "suggestion_rating"
    SYSTEM_STATE = "system_state"


@dataclass
class CrossPhaseEvent:
    """Event data structure for cross-phase communication."""

    event_type: EventType
    source_phase: str
    target_phase: str
    data: Dict[str, Any]
    timestamp: float
    event_id: str


class ContextBridge:
    """
    Central communication hub for all Lyrixa phases.

    Manages event routing, state synchronization, and real-time updates
    between Memory, Anticipation, GUI, Analytics, and Intelligence systems.
    """

    def __init__(self):
        """Initialize the context bridge."""
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[CrossPhaseEvent] = []
        self.subscribers: Dict[str, Set[Callable]] = {}
        self.active_connections = 0
        self.last_sync_time = time.time()

        # Phase component references
        self.memory_system = None
        self.anticipation_engine = None
        self.analytics_dashboard = None
        self.notification_system = None
        self.performance_monitor = None
        self.intelligence_layer = None

        logger.info("🔗 ContextBridge initialized")

    def register_component(self, phase_name: str, component):
        """Register a phase component with the bridge."""
        try:
            setattr(self, f"{phase_name}_system", component)
            self.active_connections += 1
            logger.info(f"✅ Registered {phase_name} component")

            # Setup automatic bindings based on component type
            self._setup_component_bindings(phase_name, component)

        except Exception as e:
            logger.error(f"❌ Failed to register {phase_name}: {e}")

    def _setup_component_bindings(self, phase_name: str, component):
        """Setup automatic event bindings for registered components."""
        try:
            if phase_name == "memory":
                # Memory → Intelligence: semantic events, context clusters
                self.subscribe(
                    EventType.MEMORY_UPDATE, self._handle_memory_to_intelligence
                )

            elif phase_name == "anticipation":
                # Anticipation → Notifications: pending suggestions, confidence
                self.subscribe(
                    EventType.PENDING_SUGGESTION,
                    self._handle_anticipation_to_notifications,
                )
                self.subscribe(
                    EventType.CONFIDENCE_SCORE,
                    self._handle_anticipation_to_notifications,
                )

            elif phase_name == "performance_monitor":
                # Performance → Analytics: resource trends, CPU costs
                self.subscribe(
                    EventType.RESOURCE_TREND, self._handle_performance_to_analytics
                )
                self.subscribe(
                    EventType.AGENT_CPU_COST, self._handle_performance_to_analytics
                )

            elif phase_name == "intelligence_layer":
                # Intelligence → Memory+Anticipation: user preferences, ratings
                self.subscribe(
                    EventType.USER_PREFERENCE, self._handle_feedback_to_systems
                )
                self.subscribe(
                    EventType.SUGGESTION_RATING, self._handle_feedback_to_systems
                )

        except Exception as e:
            logger.warning(f"⚠️ Binding setup failed for {phase_name}: {e}")

    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
        logger.info(f"🔔 Subscribed to {event_type.value}")

    def emit_event(
        self,
        event_type: EventType,
        source_phase: str,
        target_phase: str,
        data: Dict[str, Any],
    ) -> str:
        """Emit a cross-phase event."""
        event = CrossPhaseEvent(
            event_type=event_type,
            source_phase=source_phase,
            target_phase=target_phase,
            data=data,
            timestamp=time.time(),
            event_id=str(uuid.uuid4())[:8],
        )

        # Store in history
        self.event_history.append(event)

        # Keep history manageable
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-500:]

        # Notify handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"❌ Event handler error: {e}")

        logger.debug(f"📡 Emitted {event_type.value}: {source_phase} → {target_phase}")
        return event.event_id

    # Specific Cross-Phase Communication Handlers

    def _handle_memory_to_intelligence(self, event: CrossPhaseEvent):
        """Handle Memory → Intelligence communication."""
        try:
            if self.intelligence_layer:
                data = event.data
                if event.event_type == EventType.SEMANTIC_EVENT:
                    # Pass semantic events to intelligence layer
                    self.intelligence_layer.update_semantic_context(data)
                elif event.event_type == EventType.CONTEXT_CLUSTER:
                    # Pass context clusters for visualization
                    self.intelligence_layer.update_context_clusters(data)

            logger.debug("🧠 Memory → Intelligence data routed")
        except Exception as e:
            logger.error(f"❌ Memory→Intelligence routing failed: {e}")

    def _handle_anticipation_to_notifications(self, event: CrossPhaseEvent):
        """Handle Anticipation → Notifications communication."""
        try:
            if self.notification_system:
                data = event.data
                if event.event_type == EventType.PENDING_SUGGESTION:
                    # Show pending suggestions in notification system
                    self.notification_system.add_suggestion(data)
                elif event.event_type == EventType.CONFIDENCE_SCORE:
                    # Update confidence indicators
                    self.notification_system.update_confidence(data)

            logger.debug("🔮 Anticipation → Notifications data routed")
        except Exception as e:
            logger.error(f"❌ Anticipation→Notifications routing failed: {e}")

    def _handle_performance_to_analytics(self, event: CrossPhaseEvent):
        """Handle Performance Monitor → Analytics communication."""
        try:
            if self.analytics_dashboard:
                data = event.data
                if event.event_type == EventType.RESOURCE_TREND:
                    # Update resource trend charts
                    self.analytics_dashboard.update_resource_trends(data)
                elif event.event_type == EventType.AGENT_CPU_COST:
                    # Update CPU cost metrics
                    self.analytics_dashboard.update_cpu_costs(data)

            logger.debug("⚡ Performance → Analytics data routed")
        except Exception as e:
            logger.error(f"❌ Performance→Analytics routing failed: {e}")

    def _handle_feedback_to_systems(self, event: CrossPhaseEvent):
        """Handle Feedback → Memory+Anticipation communication."""
        try:
            data = event.data

            # Route to memory system
            if self.memory_system and event.event_type == EventType.USER_PREFERENCE:
                # Store user preferences in memory
                self._update_memory_preferences(data)

            # Route to anticipation engine
            if (
                self.anticipation_engine
                and event.event_type == EventType.SUGGESTION_RATING
            ):
                # Update anticipation models with suggestion ratings
                if hasattr(self.anticipation_engine, "update_suggestion_feedback"):
                    self.anticipation_engine.update_suggestion_feedback(data)

            logger.debug("💭 Feedback → Systems data routed")
        except Exception as e:
            logger.error(f"❌ Feedback→Systems routing failed: {e}")

    def _update_memory_preferences(self, data: Dict[str, Any]):
        """Update memory system with user preferences."""
        try:
            if self.memory_system and hasattr(self.memory_system, "store_memory"):
                # Try sync version first, fallback to async if needed
                try:
                    self.memory_system.store_memory(
                        content=f"User preference: {data}",
                        memory_type="preference",
                        tags=["user", "preference", "feedback"],
                        confidence=1.0,
                    )
                except TypeError:
                    # If store_memory is async, we'll need to handle it differently
                    logger.warning(
                        "Memory system store_memory is async - preferences not directly stored"
                    )
        except Exception as e:
            logger.error(f"❌ Memory preference update failed: {e}")

    # Real-time Synchronization

    def sync_all_phases(self):
        """Synchronize state across all connected phases."""
        try:
            current_time = time.time()

            # Get current system state
            system_state = self._collect_system_state()

            # Emit system state update
            self.emit_event(
                EventType.SYSTEM_STATE, "context_bridge", "all_phases", system_state
            )

            self.last_sync_time = current_time
            logger.debug("🔄 Phase synchronization completed")

        except Exception as e:
            logger.error(f"❌ Phase sync failed: {e}")

    def _collect_system_state(self) -> Dict[str, Any]:
        """Collect current state from all registered components."""
        state = {
            "timestamp": time.time(),
            "active_connections": self.active_connections,
            "event_count": len(self.event_history),
            "last_sync": self.last_sync_time,
        }

        # Collect component-specific states
        if self.memory_system:
            state["memory_status"] = "active"
        if self.anticipation_engine:
            state["anticipation_status"] = "active"
        if self.analytics_dashboard:
            state["analytics_status"] = "active"
        if self.notification_system:
            state["notifications_status"] = "active"
        if self.performance_monitor:
            state["performance_status"] = "active"
        if self.intelligence_layer:
            state["intelligence_status"] = "active"

        return state

    # Utility Methods

    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about cross-phase communication."""
        if not self.event_history:
            return {"total_events": 0}

        # Count events by type
        event_counts = {}
        for event in self.event_history:
            event_type = event.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Recent activity (last 60 seconds)
        recent_time = time.time() - 60
        recent_events = [e for e in self.event_history if e.timestamp > recent_time]

        return {
            "total_events": len(self.event_history),
            "recent_events": len(recent_events),
            "event_types": event_counts,
            "active_connections": self.active_connections,
            "last_sync": self.last_sync_time,
        }

    def clear_event_history(self, keep_recent_minutes: int = 10):
        """Clear old events from history, keeping recent ones."""
        cutoff_time = time.time() - (keep_recent_minutes * 60)
        self.event_history = [
            e for e in self.event_history if e.timestamp > cutoff_time
        ]
        logger.info(
            f"🧹 Event history cleaned, kept {len(self.event_history)} recent events"
        )


# Global instance for easy access
context_bridge = ContextBridge()


# Convenience functions for common operations
def emit_memory_event(data: Dict[str, Any]) -> str:
    """Emit a memory-related event."""
    return context_bridge.emit_event(
        EventType.SEMANTIC_EVENT, "memory", "intelligence", data
    )


def emit_anticipation_event(suggestion_data: Dict[str, Any]) -> str:
    """Emit an anticipation/suggestion event."""
    return context_bridge.emit_event(
        EventType.PENDING_SUGGESTION, "anticipation", "notifications", suggestion_data
    )


def emit_performance_event(metrics_data: Dict[str, Any]) -> str:
    """Emit a performance metrics event."""
    return context_bridge.emit_event(
        EventType.RESOURCE_TREND, "performance", "analytics", metrics_data
    )


def emit_feedback_event(feedback_data: Dict[str, Any]) -> str:
    """Emit user feedback event."""
    return context_bridge.emit_event(
        EventType.USER_PREFERENCE, "intelligence", "memory", feedback_data
    )
