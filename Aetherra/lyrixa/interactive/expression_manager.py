#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🎭 Lyrixa Expression Manager
============================

Finite state machine for Lyrixa's expressions and emotional states.
Maps system health signals to visual/audio expressions with enter/exit/tick hooks.

Subscribes to:
- kernel.health (load/CB state)
- homeostasis.signal (degraded/quarantine)
- memory.pulse (coherence/drift)
- storm.shadow (agreement/divergence)
- chat.stream.event (stream lifecycle)

Emits:
- lyrixa.expression events for UI rendering and plugin reactions
"""

import asyncio
import contextlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExpressionState(Enum):
    """Available expression states for Lyrixa."""

    CALM = "calm"
    FOCUSED = "focused"
    CONCERNED = "concerned"
    DELIGHTED = "delighted"
    RESTING = "resting"
    THOUGHTFUL = "thoughtful"
    CONFIDENT = "confident"
    PENSIVE = "pensive"
    ON_EDGE = "on_edge"


@dataclass
class ExpressionConfig:
    """Configuration for a specific expression state."""

    state: ExpressionState
    duration_ms: int = 2500
    priority: int = 1  # Higher priority states can interrupt lower ones
    allow_interrupt: bool = True
    animation_speed: float = 1.0
    intensity: float = 0.5  # 0.0-1.0
    visual_cues: Dict[str, Any] = field(default_factory=dict)
    audio_cues: Optional[str] = None


@dataclass
class ExpressionEvent:
    """Event emitted when expression changes."""

    state: ExpressionState
    timestamp: float
    intensity: float
    reason: str
    duration_ms: int
    trace_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for KEB publishing."""
        return {
            "state": self.state.value,
            "timestamp": self.timestamp,
            "intensity": self.intensity,
            "reason": self.reason,
            "ttl_ms": self.duration_ms,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
        }


class ExpressionManager:
    """
    Finite state machine managing Lyrixa's expressions and emotional states.

    Subscribes to system events from KEB and chat streams, maps them to
    appropriate expressions, and publishes lyrixa.expression events.
    """

    def __init__(self, event_bus=None, service_registry=None, state_mapper=None):
        """
        Initialize the expression manager.

        Args:
            event_bus: Kernel Event Bus instance for pub/sub
            service_registry: Service registry for component discovery
            state_mapper: StateMapper instance for signal → emotion mapping
        """
        self.event_bus = event_bus
        self.service_registry = service_registry
        self.state_mapper = state_mapper

        # State tracking
        self.current_state = ExpressionState.CALM
        self.previous_state = ExpressionState.CALM
        self.state_entered_at = time.time()
        self.state_duration = 0.0

        # Configuration (will be loaded from state_map.json via state_mapper)
        self.configs = self._initialize_configs()
        self.default_duration_ms = 2500

        # Hooks for plugins to register callbacks
        self.enter_hooks: Dict[ExpressionState, List[Callable]] = {
            state: [] for state in ExpressionState
        }
        self.exit_hooks: Dict[ExpressionState, List[Callable]] = {
            state: [] for state in ExpressionState
        }
        self.tick_hooks: Dict[ExpressionState, List[Callable]] = {
            state: [] for state in ExpressionState
        }

        # Expression queue for priority handling
        self.expression_queue: List[ExpressionEvent] = []

        # Running state
        self.running = False
        self.subscription_tasks: List[asyncio.Task] = []

        # Statistics
        self.stats = {
            "state_transitions": 0,
            "expressions_emitted": 0,
            "interruptions": 0,
            "by_state": {state: 0 for state in ExpressionState},
        }

        logger.info("🎭 Expression Manager initialized")

    def _initialize_configs(self) -> Dict[ExpressionState, ExpressionConfig]:
        """
        Initialize default configurations for each expression state.

        If state_mapper is available, loads from state_map.json.
        Otherwise uses hardcoded defaults.
        """
        if self.state_mapper:
            # Load from JSON via state_mapper
            json_configs = {}
            for state in ExpressionState:
                state_config = self.state_mapper.get_expression_config(state.value)
                if state_config:
                    json_configs[state] = ExpressionConfig(
                        state=state,
                        duration_ms=state_config.get("duration_ms", 2500),
                        priority=state_config.get("priority", 1),
                        intensity=state_config.get("intensity", 0.5),
                        visual_cues=state_config.get("visual_cues", {}),
                        audio_cues=state_config.get("audio_cues"),
                    )
            if json_configs:
                logger.debug("✅ Loaded expression configs from state_map.json")
                return json_configs

        # Fallback to hardcoded defaults
        return {
            ExpressionState.CALM: ExpressionConfig(
                state=ExpressionState.CALM,
                duration_ms=5000,
                priority=1,
                intensity=0.3,
                visual_cues={"glow": "soft_blue", "animation": "breathe"},
                audio_cues=None,
            ),
            ExpressionState.FOCUSED: ExpressionConfig(
                state=ExpressionState.FOCUSED,
                duration_ms=3000,
                priority=2,
                intensity=0.7,
                visual_cues={"glow": "bright_blue", "animation": "pulse"},
                audio_cues=None,
            ),
            ExpressionState.CONCERNED: ExpressionConfig(
                state=ExpressionState.CONCERNED,
                duration_ms=4000,
                priority=3,
                intensity=0.8,
                visual_cues={"glow": "orange", "animation": "flicker"},
                audio_cues="concern_chime",
            ),
            ExpressionState.DELIGHTED: ExpressionConfig(
                state=ExpressionState.DELIGHTED,
                duration_ms=2000,
                priority=2,
                intensity=0.9,
                visual_cues={"glow": "golden", "animation": "sparkle"},
                audio_cues="delight_chime",
            ),
            ExpressionState.RESTING: ExpressionConfig(
                state=ExpressionState.RESTING,
                duration_ms=10000,
                priority=1,
                intensity=0.2,
                visual_cues={"glow": "dim_blue", "animation": "slow_breathe"},
                audio_cues=None,
            ),
            ExpressionState.THOUGHTFUL: ExpressionConfig(
                state=ExpressionState.THOUGHTFUL,
                duration_ms=3500,
                priority=2,
                intensity=0.6,
                visual_cues={"glow": "purple", "animation": "shimmer"},
                audio_cues=None,
            ),
            ExpressionState.CONFIDENT: ExpressionConfig(
                state=ExpressionState.CONFIDENT,
                duration_ms=2500,
                priority=2,
                intensity=0.85,
                visual_cues={"glow": "bright_white", "animation": "steady"},
                audio_cues=None,
            ),
            ExpressionState.PENSIVE: ExpressionConfig(
                state=ExpressionState.PENSIVE,
                duration_ms=4000,
                priority=2,
                intensity=0.5,
                visual_cues={"glow": "soft_purple", "animation": "wave"},
                audio_cues=None,
            ),
            ExpressionState.ON_EDGE: ExpressionConfig(
                state=ExpressionState.ON_EDGE,
                duration_ms=3000,
                priority=4,
                intensity=0.9,
                visual_cues={"glow": "red", "animation": "rapid_pulse"},
                audio_cues="alert_tone",
            ),
        }

    async def start(self):
        """Start the expression manager and subscribe to event streams."""
        if self.running:
            logger.warning("Expression Manager already running")
            return

        self.running = True
        logger.info("🚀 Starting Expression Manager")

        # Subscribe to KEB topics if event bus available
        if self.event_bus:
            await self._subscribe_to_keb_topics()

        # Start expression processing loop
        self.subscription_tasks.append(asyncio.create_task(self._expression_processing_loop()))

        # Start tick loop for current state
        self.subscription_tasks.append(asyncio.create_task(self._state_tick_loop()))

        logger.info("✅ Expression Manager started")

    async def stop(self):
        """Stop the expression manager and clean up subscriptions."""
        if not self.running:
            return

        logger.info("🛑 Stopping Expression Manager")
        self.running = False

        # Cancel all subscription tasks
        for task in self.subscription_tasks:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        self.subscription_tasks.clear()
        logger.info("✅ Expression Manager stopped")

    async def _subscribe_to_keb_topics(self):
        """Subscribe to relevant KEB topics for expression triggers."""
        topics = [
            "kernel.health",
            "homeostasis.signal",
            "memory.pulse",
            "storm.shadow",
            "chat.stream.event",
            "lyrixa.emotion",  # Listen to our own emotion events
        ]

        for topic in topics:
            try:
                await self.event_bus.subscribe(topic, "lyrixa_expression_manager")
                logger.debug(f"📡 Subscribed to KEB topic: {topic}")
            except Exception as e:
                logger.warning(f"Failed to subscribe to {topic}: {e}")

    async def _expression_processing_loop(self):
        """Main loop for processing queued expressions."""
        while self.running:
            try:
                # Process queued expressions by priority
                if self.expression_queue:
                    self.expression_queue.sort(
                        key=lambda e: self.configs.get(
                            e.state, self.configs[ExpressionState.CALM]
                        ).priority,
                        reverse=True,
                    )

                    next_expression = self.expression_queue.pop(0)
                    await self._transition_to(next_expression)

                # Check for automatic state decay/return to calm
                current_time = time.time()
                self.state_duration = current_time - self.state_entered_at

                config = self.configs[self.current_state]
                duration_sec = config.duration_ms / 1000.0

                if (
                    self.state_duration > duration_sec
                    and self.current_state != ExpressionState.CALM
                ):
                    # Auto-transition back to calm
                    await self.set_expression(
                        ExpressionState.CALM, reason="state_timeout", intensity=0.3
                    )

                await asyncio.sleep(0.1)  # 100ms processing cycle

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in expression processing loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    async def _state_tick_loop(self):
        """Loop that calls tick hooks for the current state."""
        while self.running:
            try:
                # Call tick hooks for current state
                for hook in self.tick_hooks[self.current_state]:
                    try:
                        if asyncio.iscoroutinefunction(hook):
                            await hook(self.current_state, self.state_duration)
                        else:
                            hook(self.current_state, self.state_duration)
                    except Exception as e:
                        logger.error(f"Error in tick hook: {e}")

                await asyncio.sleep(0.5)  # Tick every 500ms

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in state tick loop: {e}", exc_info=True)
                await asyncio.sleep(1.0)

    async def handle_keb_event(self, topic: str, event: Dict[str, Any]):
        """
        Handle incoming KEB events and map them to expressions.

        Args:
            topic: KEB topic name
            event: Event data
        """
        try:
            if topic == "kernel.health":
                await self._handle_kernel_health(event)
            elif topic == "homeostasis.signal":
                await self._handle_homeostasis_signal(event)
            elif topic == "memory.pulse":
                await self._handle_memory_pulse(event)
            elif topic == "storm.shadow":
                await self._handle_storm_shadow(event)
            elif topic == "chat.stream.event":
                await self._handle_chat_stream_event(event)
            elif topic == "lyrixa.emotion":
                await self._handle_emotion_event(event)

        except Exception as e:
            logger.error(f"Error handling KEB event from {topic}: {e}", exc_info=True)

    async def _handle_kernel_health(self, event: Dict[str, Any]):
        """Handle kernel health events."""
        cb_state = event.get("circuit_breaker_state")
        queue_backlog = event.get("queue_backlog", 0)

        if cb_state == "open" or queue_backlog > 100:
            await self.set_expression(
                ExpressionState.ON_EDGE,
                reason=f"kernel_stress_cb={cb_state}_backlog={queue_backlog}",
                intensity=min(0.9, 0.5 + queue_backlog / 200.0),
            )

    async def _handle_homeostasis_signal(self, event: Dict[str, Any]):
        """Handle homeostasis system signals."""
        signal_type = event.get("type", "")
        quarantined = event.get("quarantined_actuators", [])
        dlq_count = event.get("dlq_count", 0)

        if signal_type == "degraded" or len(quarantined) > 0 or dlq_count > 10:
            await self.set_expression(
                ExpressionState.CONCERNED,
                reason=f"homeostasis_degraded_quarantine={len(quarantined)}_dlq={dlq_count}",
                intensity=0.7,
            )

    async def _handle_memory_pulse(self, event: Dict[str, Any]):
        """Handle memory pulse/health events."""
        coherence = event.get("coherence_score", 0.0)

        if coherence < 0.7:
            await self.set_expression(
                ExpressionState.CONCERNED,
                reason=f"memory_coherence_low={coherence:.2f}",
                intensity=0.6,
            )
        elif 0.7 <= coherence < 0.9:
            await self.set_expression(
                ExpressionState.FOCUSED,
                reason=f"memory_coherence_moderate={coherence:.2f}",
                intensity=0.7,
            )
        else:
            await self.set_expression(
                ExpressionState.CALM,
                reason=f"memory_coherence_excellent={coherence:.2f}",
                intensity=0.3,
            )

    async def _handle_storm_shadow(self, event: Dict[str, Any]):
        """Handle STORM shadow mode events."""
        inconsistency = event.get("sheaf_inconsistency", 0.0)
        coherence = event.get("coherence_score", 1.0)

        if inconsistency > 0.5:
            await self.set_expression(
                ExpressionState.PENSIVE,
                reason=f"storm_inconsistency_high={inconsistency:.2f}",
                intensity=0.6,
            )
        elif coherence > 0.95:
            await self.set_expression(
                ExpressionState.CONFIDENT,
                reason=f"storm_coherence_perfect={coherence:.2f}",
                intensity=0.85,
            )

    async def _handle_chat_stream_event(self, event: Dict[str, Any]):
        """Handle chat stream lifecycle events."""
        event_type = event.get("type", "")
        confidence = event.get("confidence", 0.8)

        if event_type == "stream_start":
            await self.set_expression(
                ExpressionState.FOCUSED, reason="chat_stream_started", intensity=0.7
            )
        elif event_type == "stream_complete":
            if confidence < 0.6:
                await self.set_expression(
                    ExpressionState.THOUGHTFUL,
                    reason=f"chat_low_confidence={confidence:.2f}",
                    intensity=0.5,
                )
            else:
                await self.set_expression(
                    ExpressionState.CALM, reason="chat_stream_complete", intensity=0.4
                )
        elif event_type == "stream_resume":
            # Quick blink/acknowledgment
            await self.set_expression(
                ExpressionState.FOCUSED,
                reason="chat_stream_resumed",
                intensity=0.6,
                duration_ms=500,
            )

    async def _handle_emotion_event(self, event: Dict[str, Any]):
        """Handle emotion events from the interactive loop."""
        mood = event.get("mood", "")
        intensity = event.get("intensity", 0.5)

        # Map emotion moods to expressions
        mood_to_expression = {
            "calm": ExpressionState.CALM,
            "focused": ExpressionState.FOCUSED,
            "concerned": ExpressionState.CONCERNED,
            "pensive": ExpressionState.PENSIVE,
            "confident": ExpressionState.CONFIDENT,
        }

        if mood in mood_to_expression:
            await self.set_expression(
                mood_to_expression[mood], reason=f"emotion_event_mood={mood}", intensity=intensity
            )

    async def set_expression(
        self,
        state: ExpressionState,
        reason: str = "",
        intensity: Optional[float] = None,
        duration_ms: Optional[int] = None,
        force: bool = False,
    ):
        """
        Set or queue a new expression state.

        Args:
            state: Target expression state
            reason: Reason for the expression change
            intensity: Expression intensity (0.0-1.0), uses config default if None
            duration_ms: Duration in milliseconds, uses config default if None
            force: Force immediate transition, bypassing priority queue
        """
        config = self.configs.get(state, self.configs[ExpressionState.CALM])

        if intensity is None:
            intensity = config.intensity

        if duration_ms is None:
            duration_ms = config.duration_ms

        # Create expression event
        event = ExpressionEvent(
            state=state,
            timestamp=time.time(),
            intensity=intensity,
            reason=reason,
            duration_ms=duration_ms,
            trace_id=f"expr_{int(time.time() * 1000)}",
        )

        if force:
            # Immediate transition
            await self._transition_to(event)
        else:
            # Check if we should queue or transition immediately
            current_config = self.configs[self.current_state]

            if config.priority > current_config.priority and current_config.allow_interrupt:
                # Higher priority, interrupt current
                await self._transition_to(event)
                self.stats["interruptions"] += 1
            else:
                # Queue for later
                self.expression_queue.append(event)

    async def _transition_to(self, event: ExpressionEvent):
        """Perform state transition with enter/exit hooks."""
        old_state = self.current_state
        new_state = event.state

        if old_state == new_state:
            # Refresh the current state and re-fire enter hooks to acknowledge explicit request
            self.state_entered_at = time.time()
            for hook in self.enter_hooks[new_state]:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(new_state)
                    else:
                        hook(new_state)
                except Exception as e:
                    logger.error(f"Error in enter hook for {new_state}: {e}")
            # Also publish an event to keep downstream in sync
            await self._publish_expression_event(event)
            return

        # Call exit hooks for old state
        for hook in self.exit_hooks[old_state]:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(old_state)
                else:
                    hook(old_state)
            except Exception as e:
                logger.error(f"Error in exit hook for {old_state}: {e}")

        # Update state
        self.previous_state = old_state
        self.current_state = new_state
        self.state_entered_at = time.time()
        self.state_duration = 0.0

        # Update statistics
        self.stats["state_transitions"] += 1
        self.stats["by_state"][new_state] = self.stats["by_state"].get(new_state, 0) + 1

        # Call enter hooks for new state
        for hook in self.enter_hooks[new_state]:
            try:
                if asyncio.iscoroutinefunction(hook):
                    await hook(new_state)
                else:
                    hook(new_state)
            except Exception as e:
                logger.error(f"Error in enter hook for {new_state}: {e}")

        # Publish expression event to KEB
        await self._publish_expression_event(event)

        logger.debug(
            f"🎭 Expression transition: {old_state.value} → {new_state.value} "
            f"(intensity={event.intensity:.2f}, reason={event.reason})"
        )

    async def _publish_expression_event(self, event: ExpressionEvent):
        """Publish expression event to KEB for UI and plugins."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.publish("lyrixa.expression", event.to_dict())
            self.stats["expressions_emitted"] += 1
        except Exception as e:
            logger.error(f"Failed to publish expression event: {e}")

    # Hook registration methods

    def register_enter_hook(self, state: ExpressionState, hook: Callable):
        """Register a callback to be called when entering a state."""
        self.enter_hooks[state].append(hook)

    def register_exit_hook(self, state: ExpressionState, hook: Callable):
        """Register a callback to be called when exiting a state."""
        self.exit_hooks[state].append(hook)

    def register_tick_hook(self, state: ExpressionState, hook: Callable):
        """Register a callback to be called periodically while in a state."""
        self.tick_hooks[state].append(hook)

    # Status and introspection

    def get_current_expression(self) -> Dict[str, Any]:
        """Get current expression state and metadata."""
        return {
            "state": self.current_state.value,
            "previous_state": self.previous_state.value,
            "duration": self.state_duration,
            "entered_at": self.state_entered_at,
            "config": self.configs[self.current_state].__dict__,
            "queue_depth": len(self.expression_queue),
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get expression manager statistics."""
        return {
            **self.stats,
            "current_state": self.current_state.value,
            "uptime": time.time() - self.state_entered_at if self.running else 0,
        }


# Global singleton for easy access
_expression_manager: Optional[ExpressionManager] = None


async def get_expression_manager(
    event_bus=None, service_registry=None, state_mapper=None
) -> ExpressionManager:
    """Get or create the global expression manager instance."""
    global _expression_manager

    if _expression_manager is None:
        _expression_manager = ExpressionManager(
            event_bus=event_bus, service_registry=service_registry, state_mapper=state_mapper
        )

    return _expression_manager
