#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🌟 Interactive Lyrixa Integration
==================================

Orchestration layer for Interactive Lyrixa system.
Wires together all components and provides unified lifecycle management.

Components:
- StateMapper: Signal → emotion mapping from JSON config
- InteractiveLoop: Health sampling and emotion publishing
- ExpressionManager: FSM for visual/audio expressions

Integration Points:
- Kernel Event Bus (KEB): Pub/sub for system signals
- Service Registry: Component discovery and restart-on-crash
- Maintenance System: Hooks for degraded-mode behavior
- Hub Metrics: Export lyrixa_interactivity_* metrics
"""

import logging
import os
import time
from typing import Any, Dict, Optional

from .expression_manager import ExpressionManager, get_expression_manager
from .interactive_loop import InteractiveLoop, get_interactive_loop
from .state_mapper import StateMapper, get_state_mapper

logger = logging.getLogger(__name__)


class InteractiveSystem:
    """
    Unified orchestrator for Interactive Lyrixa components.

    Handles:
    - Component initialization and lifecycle
    - Service Registry registration
    - Maintenance System integration
    - Metrics export
    - Safety guardrails (rate limits, HMR rollback)
    """

    def __init__(self, event_bus=None, service_registry=None, config=None):
        """
        Initialize the Interactive Lyrixa system.

        Args:
            event_bus: Kernel Event Bus instance
            service_registry: Service Registry instance
            config: Optional configuration overrides
        """
        self.event_bus = event_bus
        self.service_registry = service_registry
        self.config = config or {}

        # Feature flag check
        self.enabled = self._check_feature_flag()

        # Core components
        self.state_mapper: Optional[StateMapper] = None
        self.interactive_loop: Optional[InteractiveLoop] = None
        self.expression_manager: Optional[ExpressionManager] = None

        # State
        self.initialized = False
        self.running = False
        self.degraded_mode = False

        # Safety tracking
        self.transition_timestamps = []
        self.max_transitions_per_minute = 10

        # Statistics
        self.stats = {
            "start_time": None,
            "uptime_seconds": 0,
            "transitions_total": 0,
            "emotions_published": 0,
            "expressions_emitted": 0,
            "safety_throttles": 0,
            "maintenance_disables": 0,
        }

        logger.info(f"🌟 Interactive System initialized (enabled={self.enabled})")

    def _check_feature_flag(self) -> bool:
        """
        Check if Interactive Lyrixa is enabled.

        For development: Always enabled unless explicitly disabled.
        Feature flags only used for production rollback if needed.
        """
        flag = os.getenv("AETHERRA_INTERACTIVE", "1")  # Default: ENABLED
        return flag == "1"

    async def initialize(self):
        """Initialize all components."""
        if self.initialized:
            logger.warning("Interactive System already initialized")
            return

        logger.info("🔧 Initializing Interactive System components")

        try:
            # Initialize StateMapper (loads state_map.json)
            self.state_mapper = get_state_mapper()

            # Initialize InteractiveLoop
            sample_interval = self.config.get("sample_interval", 5.0)
            self.interactive_loop = await get_interactive_loop(
                event_bus=self.event_bus,
                service_registry=self.service_registry,
                sample_interval=sample_interval,
                state_mapper=self.state_mapper,
            )

            # Initialize ExpressionManager
            self.expression_manager = await get_expression_manager(
                event_bus=self.event_bus,
                service_registry=self.service_registry,
                state_mapper=self.state_mapper,
            )

            # Register with Service Registry (if available)
            await self._register_with_service_registry()

            # Subscribe to Maintenance System events
            await self._subscribe_to_maintenance_events()

            self.initialized = True
            logger.info("✅ Interactive System initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Interactive System: {e}", exc_info=True)
            raise

    async def start(self):
        """Start all components."""
        if not self.initialized:
            logger.warning("Interactive System not initialized, initializing now")
            await self.initialize()

        if self.running:
            logger.warning("Interactive System already running")
            return

        logger.info("🚀 Starting Interactive System")

        try:
            # Start InteractiveLoop
            if self.interactive_loop:
                await self.interactive_loop.start()

            # Start ExpressionManager
            if self.expression_manager:
                await self.expression_manager.start()

            self.running = True
            self.stats["start_time"] = time.time()

            logger.info("✅ Interactive System started")

        except Exception as e:
            logger.error(f"❌ Failed to start Interactive System: {e}", exc_info=True)
            raise

    async def stop(self):
        """Stop all components."""
        if not self.running:
            return

        logger.info("🛑 Stopping Interactive System")

        try:
            # Stop ExpressionManager
            if self.expression_manager:
                await self.expression_manager.stop()

            # Stop InteractiveLoop
            if self.interactive_loop:
                await self.interactive_loop.stop()

            # Unregister from Service Registry
            await self._unregister_from_service_registry()

            self.running = False

            # Update uptime
            if self.stats["start_time"]:
                self.stats["uptime_seconds"] = time.time() - self.stats["start_time"]

            logger.info("✅ Interactive System stopped")

        except Exception as e:
            logger.error(f"Error stopping Interactive System: {e}", exc_info=True)

    async def _register_with_service_registry(self):
        """Register Interactive System with Service Registry for restart-on-crash."""
        if not self.service_registry:
            logger.debug("No Service Registry available")
            return

        try:
            # Register InteractiveLoop as a background service
            await self.service_registry.register_service(
                name="lyrixa_interactive_loop",
                instance=self.interactive_loop,
                service_type="background",
                restart_on_crash=True,
                health_check=lambda: self.interactive_loop.running
                if self.interactive_loop
                else False,
            )

            logger.info("📡 Registered with Service Registry (restart-on-crash enabled)")

        except Exception as e:
            logger.warning(f"Failed to register with Service Registry: {e}")

    async def _unregister_from_service_registry(self):
        """Unregister from Service Registry."""
        if not self.service_registry:
            return

        try:
            await self.service_registry.unregister_service("lyrixa_interactive_loop")
            logger.debug("📡 Unregistered from Service Registry")
        except Exception as e:
            logger.warning(f"Failed to unregister from Service Registry: {e}")

    async def _subscribe_to_maintenance_events(self):
        """Subscribe to Maintenance System mode changes for auto-disable."""
        if not self.event_bus:
            return

        try:
            await self.event_bus.subscribe("maintenance.mode_changed", "lyrixa_interactive_system")

            # Register handler
            self.event_bus.add_handler(
                topic="maintenance.mode_changed",
                handler=self._handle_maintenance_mode_change,
                handler_id="lyrixa_interactive_maintenance_hook",
            )

            logger.debug("📡 Subscribed to Maintenance System events")

        except Exception as e:
            logger.warning(f"Failed to subscribe to maintenance events: {e}")

    async def _handle_maintenance_mode_change(self, event: Dict[str, Any]):
        """Handle maintenance mode changes (auto-disable during degraded/recovery)."""
        mode = event.get("mode", "")

        if mode in ["degraded", "recovery"]:
            # Auto-disable interactivity
            if self.running and not self.degraded_mode:
                logger.warning(f"⚠️ Auto-disabling Interactive System (maintenance mode: {mode})")
                self.degraded_mode = True
                self.stats["maintenance_disables"] += 1

                # Pause components without full stop
                if self.interactive_loop:
                    self.interactive_loop.running = False
                if self.expression_manager:
                    self.expression_manager.running = False

        elif mode == "normal" and self.degraded_mode:
            # Re-enable if we were in degraded mode
            logger.info(f"✅ Re-enabling Interactive System (maintenance mode: {mode})")
            self.degraded_mode = False

            # Resume components
            if self.interactive_loop:
                self.interactive_loop.running = True
            if self.expression_manager:
                self.expression_manager.running = True

    def check_safety_throttle(self) -> bool:
        """
        Check if we should throttle transitions based on frequency caps.

        Returns:
            True if throttling should be applied, False otherwise
        """
        current_time = time.time()

        # Remove timestamps older than 1 minute
        cutoff = current_time - 60.0
        self.transition_timestamps = [t for t in self.transition_timestamps if t > cutoff]

        # Check if we exceed the limit
        if len(self.transition_timestamps) >= self.max_transitions_per_minute:
            self.stats["safety_throttles"] += 1
            logger.warning(
                f"⚠️ Safety throttle applied: {len(self.transition_timestamps)} "
                f"transitions in last minute (max={self.max_transitions_per_minute})"
            )
            return True

        # Record this transition
        self.transition_timestamps.append(current_time)
        return False

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics for export to Hub /metrics endpoint.

        Returns metrics in Prometheus format:
        - lyrixa_interactivity_emotion_intensity_avg
        - lyrixa_interactivity_state_transitions_total
        - lyrixa_interactivity_expressions_emitted_total
        - lyrixa_interactivity_safety_throttles_total
        """
        metrics = {
            "lyrixa_interactivity_enabled": 1 if self.enabled else 0,
            "lyrixa_interactivity_running": 1 if self.running else 0,
            "lyrixa_interactivity_degraded_mode": 1 if self.degraded_mode else 0,
            "lyrixa_interactivity_uptime_seconds": self.stats["uptime_seconds"],
            "lyrixa_interactivity_state_transitions_total": self.stats["transitions_total"],
            "lyrixa_interactivity_emotions_published_total": self.stats["emotions_published"],
            "lyrixa_interactivity_expressions_emitted_total": self.stats["expressions_emitted"],
            "lyrixa_interactivity_safety_throttles_total": self.stats["safety_throttles"],
            "lyrixa_interactivity_maintenance_disables_total": self.stats["maintenance_disables"],
        }

        # Add current emotion intensity if available
        if self.interactive_loop:
            current_emotion = self.interactive_loop.get_current_emotion()
            metrics["lyrixa_interactivity_emotion_intensity_avg"] = current_emotion.get(
                "intensity", 0.0
            )

        # Add expression manager stats if available
        if self.expression_manager:
            expr_stats = self.expression_manager.get_stats()
            metrics.update(
                {
                    "lyrixa_interactivity_state_transitions_total": expr_stats.get(
                        "state_transitions", 0
                    ),
                    "lyrixa_interactivity_expressions_emitted_total": expr_stats.get(
                        "expressions_emitted", 0
                    ),
                    "lyrixa_interactivity_interruptions_total": expr_stats.get("interruptions", 0),
                }
            )

        return metrics

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of Interactive System."""
        status = {
            "enabled": self.enabled,
            "initialized": self.initialized,
            "running": self.running,
            "degraded_mode": self.degraded_mode,
            "stats": self.stats,
        }

        if self.interactive_loop:
            status["interactive_loop"] = {
                "running": self.interactive_loop.running,
                "current_emotion": self.interactive_loop.get_current_emotion(),
                "stats": self.interactive_loop.get_stats(),
            }

        if self.expression_manager:
            status["expression_manager"] = {
                "running": self.expression_manager.running,
                "current_expression": self.expression_manager.get_current_expression(),
                "stats": self.expression_manager.get_stats(),
            }

        return status


# Global singleton
_interactive_system: Optional[InteractiveSystem] = None


async def get_interactive_system(
    event_bus=None, service_registry=None, config=None
) -> InteractiveSystem:
    """Get or create the global Interactive System instance."""
    global _interactive_system

    if _interactive_system is None:
        _interactive_system = InteractiveSystem(
            event_bus=event_bus, service_registry=service_registry, config=config
        )

    return _interactive_system
