#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🔄 Lyrixa Interactive Loop
==========================

Lightweight async loop that samples system health and publishes emotion events.
Maps real-time system state to Lyrixa's emotional/reactive state.

Monitors:
- Homeostasis metrics (quarantined actuators, DLQ count, degraded state)
- Memory health (coherence, drift, contradictions)
- Kernel health (queue backpressure, circuit breaker state)
- User activity (idle detection, return events)
- Error patterns (burst detection)

Publishes:
- lyrixa.emotion events with mood, intensity, and reasons
"""

import asyncio
import contextlib
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional

from .state_mapper import get_state_mapper

logger = logging.getLogger(__name__)


@dataclass
class EmotionState:
    """Represents Lyrixa's current emotional state."""

    mood: str  # calm, focused, concerned, pensive, confident
    intensity: float  # 0.0-1.0
    reasons: List[str]
    timestamp: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for KEB publishing."""
        return {
            "mood": self.mood,
            "intensity": self.intensity,
            "reasons": self.reasons,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class InteractiveLoop:
    """
    Lightweight loop for sampling system health and publishing emotions.

    Acts as the "nervous system" connecting Lyrixa's intelligence to her
    expressive interface.
    """

    def __init__(
        self, event_bus=None, service_registry=None, sample_interval: float = 5.0, state_mapper=None
    ):
        """
        Initialize the interactive loop.

        Args:
            event_bus: Kernel Event Bus for publishing emotions
            service_registry: Service registry for component discovery
            sample_interval: Seconds between health samples
            state_mapper: StateMapper instance for signal → emotion mapping
        """
        self.event_bus = event_bus
        self.service_registry = service_registry
        self.sample_interval = sample_interval
        self.state_mapper = state_mapper or get_state_mapper()

        # State tracking
        self.current_emotion = EmotionState(
            mood="calm",
            intensity=0.3,
            reasons=["initial_state"],
            timestamp=time.time(),
            metadata={},
        )
        self.emotion_history: Deque[EmotionState] = deque(maxlen=100)

        # User activity tracking
        self.last_user_activity = time.time()
        self.user_idle_threshold = 600.0  # 10 minutes
        self.is_user_idle = False

        # Error tracking for burst detection
        self.recent_errors: Deque[float] = deque(maxlen=50)
        self.error_burst_threshold = 5  # errors per minute

        # Running state
        self.running = False
        self.loop_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            "emotions_published": 0,
            "health_samples": 0,
            "mood_changes": 0,
            "idle_detections": 0,
            "error_bursts_detected": 0,
        }

        # Component references (set dynamically)
        self.homeostasis = None
        self.memory_system = None
        self.kernel = None

        logger.info(f"🔄 Interactive Loop initialized (sample_interval={sample_interval}s)")

    async def start(self):
        """Start the interactive loop."""
        if self.running:
            logger.warning("Interactive Loop already running")
            return

        self.running = True
        logger.info("🚀 Starting Interactive Loop")

        # Discover system components
        await self._discover_components()

        # Start main loop
        self.loop_task = asyncio.create_task(self._main_loop())

        logger.info("✅ Interactive Loop started")

    async def stop(self):
        """Stop the interactive loop."""
        if not self.running:
            return

        logger.info("🛑 Stopping Interactive Loop")
        self.running = False

        if self.loop_task and not self.loop_task.done():
            self.loop_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.loop_task

        logger.info("✅ Interactive Loop stopped")

    async def _discover_components(self):
        """Discover system components from service registry."""
        if not self.service_registry:
            logger.warning("No service registry available for component discovery")
            return

        try:
            # Get homeostasis instance
            homeostasis_info = self.service_registry.get_service_info("aetherra_homeostasis")
            if homeostasis_info:
                self.homeostasis = homeostasis_info.instance
                logger.debug("📡 Connected to Homeostasis system")

            # Get memory system
            memory_info = self.service_registry.get_service_info("memory_system")
            if memory_info:
                self.memory_system = memory_info.instance
                logger.debug("📡 Connected to Memory system")

            # Get kernel
            kernel_info = self.service_registry.get_service_info("kernel_loop")
            if kernel_info:
                self.kernel = kernel_info.instance
                logger.debug("📡 Connected to Kernel Loop")

        except Exception as e:
            logger.warning(f"Component discovery partial failure: {e}")

    async def _main_loop(self):
        """Main interactive loop."""
        while self.running:
            try:
                # Sample system health
                health_snapshot = await self._sample_system_health()
                self.stats["health_samples"] += 1

                # Compute emotion from health signals using StateMapper
                new_emotion = self._compute_emotion(health_snapshot)

                # Check if emotion changed significantly
                if self._is_significant_change(new_emotion):
                    await self._publish_emotion(new_emotion)
                    self.emotion_history.append(new_emotion)
                    self.current_emotion = new_emotion
                    self.stats["mood_changes"] += 1

                # Check for user idle state
                await self._check_user_activity()

                # Check for error bursts
                await self._check_error_bursts()

                # Sleep until next sample
                await asyncio.sleep(self.sample_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}", exc_info=True)
                await asyncio.sleep(self.sample_interval)

    async def _sample_system_health(self) -> Dict[str, Any]:
        """
        Sample health from all available systems.

        Returns:
            Dictionary with health metrics from all systems
        """
        health = {
            "timestamp": time.time(),
            "homeostasis": {},
            "memory": {},
            "kernel": {},
        }

        # Sample Homeostasis
        if self.homeostasis:
            try:
                status = await self.homeostasis.get_system_health_status()

                # Extract key metrics
                dlq_health = status.get("dlq_health", {})
                supervisor = status.get("supervisor", {})

                health["homeostasis"] = {
                    "dlq_count": dlq_health.get("dlq_count", 0),
                    "quarantined_count": dlq_health.get("quarantined_count", 0),
                    "quarantined_actuators": dlq_health.get("quarantined_actuators", []),
                    "running": status.get("homeostasis", {}).get("running", False),
                    "supervisor_state": supervisor.get("current_state", "unknown"),
                }
            except Exception as e:
                logger.debug(f"Failed to sample homeostasis: {e}")

        # Sample Memory
        if self.memory_system:
            try:
                # Try to get memory pulse/health
                if hasattr(self.memory_system, "get_health_metrics"):
                    metrics = await self.memory_system.get_health_metrics()
                    health["memory"] = {
                        "coherence_score": metrics.get("coherence_score", 0.8),
                        "contradictions": metrics.get("contradictions", 0),
                        "drift_score": metrics.get("drift_score", 0.0),
                    }
                elif hasattr(self.memory_system, "get_pulse"):
                    pulse = self.memory_system.get_pulse()
                    health["memory"] = {
                        "coherence_score": pulse.get("coherence", 0.8),
                        "contradictions": pulse.get("contradictions", 0),
                        "drift_score": pulse.get("drift", 0.0),
                    }
            except Exception as e:
                logger.debug(f"Failed to sample memory: {e}")

        # Sample Kernel
        if self.kernel:
            try:
                if hasattr(self.kernel, "get_metrics"):
                    metrics = self.kernel.get_metrics()
                    health["kernel"] = {
                        "queue_size": metrics.get("queue_size", 0),
                        "queue_limit": metrics.get("queue_limit", 1000),
                        "drops_total": metrics.get("drops_total", 0),
                        "circuit_breaker_state": metrics.get("circuit_breaker_state", "closed"),
                    }
            except Exception as e:
                logger.debug(f"Failed to sample kernel: {e}")

        return health

    def _compute_emotion(self, health: Dict[str, Any]) -> EmotionState:
        """
        Compute emotional state from health snapshot using StateMapper.

        Maps health signals to mood and intensity using the state mapping rules.
        """
        # Extract metrics
        homeostasis = health.get("homeostasis", {})
        memory = health.get("memory", {})
        kernel = health.get("kernel", {})

        dlq_count = homeostasis.get("dlq_count", 0)
        quarantined_count = homeostasis.get("quarantined_count", 0)
        coherence = memory.get("coherence_score", 0.8)
        queue_size = kernel.get("queue_size", 0)
        queue_limit = kernel.get("queue_limit", 1000)
        cb_state = kernel.get("circuit_breaker_state", "closed")
        drops_total = kernel.get("drops_total", 0)

        # Use StateMapper to map signals to emotions
        signals = {}

        # Map homeostasis signal
        mood_home, intensity_home = self.state_mapper.map_homeostasis_signal(
            dlq_count=dlq_count, quarantined_count=quarantined_count, drops_total=drops_total
        )
        signals["homeostasis"] = (mood_home, intensity_home)

        # Map memory signal
        mood_mem, intensity_mem = self.state_mapper.map_memory_pulse(coherence)
        signals["memory"] = (mood_mem, intensity_mem)

        # Map kernel signal
        mood_kern, intensity_kern = self.state_mapper.map_kernel_health(
            queue_size=queue_size,
            queue_limit=queue_limit,
            circuit_breaker_state=cb_state,
            drops_burst=drops_total,
        )
        signals["kernel"] = (mood_kern, intensity_kern)

        # Combine signals using StateMapper
        combined_mood, combined_intensity, reasons = self.state_mapper.combine_signals(signals)

        # Apply context adjustments
        final_mood, final_intensity = self.state_mapper.adjust_for_context(
            mood=combined_mood,
            intensity=combined_intensity,
            is_user_idle=self.is_user_idle,
            error_burst=len(self.recent_errors) >= self.error_burst_threshold,
        )

        return EmotionState(
            mood=final_mood,
            intensity=final_intensity,
            reasons=reasons,
            timestamp=time.time(),
            metadata=health,
        )

    def _is_significant_change(self, new_emotion: EmotionState) -> bool:
        """Check if emotion change is significant enough to publish."""
        # Always publish if mood changed
        if new_emotion.mood != self.current_emotion.mood:
            return True

        # Publish if intensity changed by more than 0.2
        intensity_delta = abs(new_emotion.intensity - self.current_emotion.intensity)
        if intensity_delta > 0.2:
            return True

        # Throttle: publish at most once per 3 samples for same mood
        if len(self.emotion_history) > 0:
            last_same_mood = None
            for hist_emotion in reversed(self.emotion_history):
                if hist_emotion.mood == new_emotion.mood:
                    last_same_mood = hist_emotion
                    break

            if last_same_mood:
                time_since = new_emotion.timestamp - last_same_mood.timestamp
                if time_since < self.sample_interval * 3:
                    return False

        return False

    async def _publish_emotion(self, emotion: EmotionState):
        """Publish emotion event to KEB."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.publish("lyrixa.emotion", emotion.to_dict())
            self.stats["emotions_published"] += 1

            logger.debug(
                f"💚 Emotion published: {emotion.mood} "
                f"(intensity={emotion.intensity:.2f}, reasons={', '.join(emotion.reasons)})"
            )
        except Exception as e:
            logger.error(f"Failed to publish emotion: {e}")

    async def _check_user_activity(self):
        """Check for user idle/return events."""
        current_time = time.time()
        time_since_activity = current_time - self.last_user_activity

        was_idle = self.is_user_idle
        self.is_user_idle = time_since_activity > self.user_idle_threshold

        # Detect idle → active transition
        if was_idle and not self.is_user_idle:
            # User returned
            self.stats["idle_detections"] += 1

            # Publish a "welcome back" emotion spike
            welcome_emotion = EmotionState(
                mood="delighted",
                intensity=0.7,
                reasons=["user_returned"],
                timestamp=current_time,
                metadata={"idle_duration": time_since_activity},
            )
            await self._publish_emotion(welcome_emotion)

    async def _check_error_bursts(self):
        """Check for error burst patterns."""
        current_time = time.time()

        # Remove errors older than 1 minute
        cutoff = current_time - 60.0
        while self.recent_errors and self.recent_errors[0] < cutoff:
            self.recent_errors.popleft()

        # Check if we're in an error burst
        if len(self.recent_errors) >= self.error_burst_threshold:
            self.stats["error_bursts_detected"] += 1

            # Publish concerned emotion
            burst_emotion = EmotionState(
                mood="concerned",
                intensity=0.85,
                reasons=[f"error_burst={len(self.recent_errors)}_errors_per_min"],
                timestamp=current_time,
                metadata={"error_count": len(self.recent_errors)},
            )
            await self._publish_emotion(burst_emotion)

    # External API for activity tracking

    def record_user_activity(self):
        """Record user activity (called externally, e.g., from GUI or chat)."""
        self.last_user_activity = time.time()
        if self.is_user_idle:
            self.is_user_idle = False
            logger.debug("👤 User activity detected, exiting idle state")

    def record_error(self):
        """Record an error occurrence for burst detection."""
        self.recent_errors.append(time.time())

    # Status and introspection

    def get_current_emotion(self) -> Dict[str, Any]:
        """Get current emotion state."""
        return self.current_emotion.to_dict()

    def get_emotion_history(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent emotion history."""
        return [e.to_dict() for e in list(self.emotion_history)[-count:]]

    def get_stats(self) -> Dict[str, Any]:
        """Get interactive loop statistics."""
        return {
            **self.stats,
            "current_mood": self.current_emotion.mood,
            "current_intensity": self.current_emotion.intensity,
            "is_user_idle": self.is_user_idle,
            "recent_error_count": len(self.recent_errors),
        }


# Global singleton for easy access
_interactive_loop: Optional[InteractiveLoop] = None


async def get_interactive_loop(
    event_bus=None, service_registry=None, sample_interval: float = 5.0, state_mapper=None
) -> InteractiveLoop:
    """Get or create the global interactive loop instance."""
    global _interactive_loop

    if _interactive_loop is None:
        _interactive_loop = InteractiveLoop(
            event_bus=event_bus,
            service_registry=service_registry,
            sample_interval=sample_interval,
            state_mapper=state_mapper,
        )

    return _interactive_loop
