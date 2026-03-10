#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌐 Aetherra Homeostasis Integration
===================================

Main integration module that coordinates all homeostasis components and
provides integration hooks for the rest of the Aetherra system.

This module:
- Orchestrates the stability metrics, controller, actuators, and supervisor
- Provides unified APIs for external systems to interact with homeostasis
- Handles startup and shutdown of the homeostasis system
- Coordinates with Lyrixa, Hub, and other Aetherra components
- Manages operational modes and emergency procedures

Author: Aetherra Labs
"""

# Standard library imports
import asyncio
import contextlib
import logging
import threading
import time
import weakref
from datetime import datetime
from typing import Any, Dict, List, Optional

# Aetherra imports
from aetherra_service_registry import get_service_registry, register_service

from .audit_trace_layer import get_audit_layer
from .autonomous_error_corrector import AutonomousErrorCorrector
from .homeostasis_actuators import HomeostasisActuators
from .homeostasis_core import ControllerMode, HomeostasisController
from .self_improvement_metrics_bridge import SelfImprovementMetricsBridge
from .self_incorporation_metrics_bridge import SelfIncorporationMetricsBridge

# Homeostasis imports
from .stability_metrics import StabilityMetrics, get_stability_metrics
from .system_supervisor import SystemSupervisor, get_system_supervisor

logger = logging.getLogger(__name__)

# Global singleton instance (Phase 3 requirement)
_homeostasis_instance: Optional["HomeostasisOrchestrator"] = None
_homeostasis_lock = threading.Lock()


class HomeostasisWatchdog:
    """
    Persistent watchdog thread that never dies (Phase 3 requirement).

    Ensures homeostasis operations continue even under heavy system load
    by running in a separate thread with its own event loop.
    """

    def __init__(self, orchestrator: "HomeostasisOrchestrator"):
        self.orchestrator_ref = weakref.ref(orchestrator)
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.watchdog_interval = 30.0  # Check every 30 seconds

        # Performance and reliability tracking
        self.last_heartbeat = time.time()
        self.cycle_count = 0
        self.error_count = 0
        self.max_errors = 10  # After 10 errors, restart orchestrator

        logger.info("🐕 Homeostasis watchdog initialized")

    def start(self):
        """Start the persistent watchdog thread."""
        if self.running:
            logger.warning("Watchdog already running")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._watchdog_thread_main,
            name="HomeostasisWatchdog",
            daemon=False,  # Not a daemon - should keep system alive
        )
        self.thread.start()
        logger.info("🚀 Homeostasis watchdog thread started")

    def stop(self):
        """Stop the watchdog thread."""
        self.running = False
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)
        logger.info("🛑 Homeostasis watchdog stopped")

    def _watchdog_thread_main(self):
        """Main watchdog thread function with its own event loop."""
        try:
            # Create new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            logger.info("🔄 Watchdog event loop started")

            # Run the watchdog loop
            self.loop.run_until_complete(self._watchdog_loop())

        except Exception as e:
            logger.error(f"❌ Fatal watchdog thread error: {e}")
        finally:
            if self.loop:
                self.loop.close()
            logger.info("🛑 Watchdog thread terminated")

    async def _watchdog_loop(self):
        """Persistent watchdog monitoring loop."""
        while self.running:
            try:
                self.last_heartbeat = time.time()
                self.cycle_count += 1

                # Get orchestrator reference
                orchestrator = self.orchestrator_ref()
                if orchestrator is None:
                    logger.error("🚨 Orchestrator reference lost - stopping watchdog")
                    break

                # Perform watchdog checks
                await self._perform_watchdog_checks(orchestrator)

                # Sleep until next check
                await asyncio.sleep(self.watchdog_interval)

            except asyncio.CancelledError:
                logger.info("🛑 Watchdog loop cancelled")
                break
            except Exception as e:
                self.error_count += 1
                logger.error(f"❌ Watchdog error #{self.error_count}: {e}")

                # If too many errors, attempt orchestrator restart
                if self.error_count >= self.max_errors:
                    await self._emergency_restart_orchestrator()
                    self.error_count = 0  # Reset counter after restart attempt

                # Brief pause before retrying
                await asyncio.sleep(5.0)

    async def _perform_watchdog_checks(self, orchestrator: "HomeostasisOrchestrator"):
        """Perform comprehensive watchdog health checks."""
        try:
            # Check if orchestrator is still running
            if not orchestrator.running:
                logger.warning("🚨 Orchestrator not running - attempting restart")
                await self._restart_orchestrator(orchestrator)
                return

            # Check component health
            component_health = await self._check_component_health(orchestrator)

            # Check if background tasks are alive
            task_health = await self._check_background_tasks(orchestrator)

            # Verify system supervisor is responding
            supervisor_health = await self._check_supervisor_health(orchestrator)

            # Log watchdog status periodically
            if self.cycle_count % 10 == 0:  # Every 5 minutes
                logger.info(
                    f"🐕 Watchdog cycle #{self.cycle_count}: "
                    f"Components={component_health}, Tasks={task_health}, "
                    f"Supervisor={supervisor_health}, Errors={self.error_count}"
                )

        except Exception as e:
            logger.error(f"❌ Watchdog check failed: {e}")
            raise

    async def _check_component_health(self, orchestrator: "HomeostasisOrchestrator") -> str:
        """Check health of core homeostasis components."""
        try:
            components = {
                "metrics": orchestrator.metrics is not None,
                "controller": orchestrator.controller is not None,
                "actuators": orchestrator.actuators is not None,
                "supervisor": orchestrator.supervisor is not None,
            }

            healthy_count = sum(components.values())
            total_count = len(components)

            if healthy_count == total_count:
                return "healthy"
            elif healthy_count > 0:
                return f"degraded({healthy_count}/{total_count})"
            else:
                return "failed"

        except Exception as e:
            logger.error(f"Component health check failed: {e}")
            return "error"

    async def _check_background_tasks(self, orchestrator: "HomeostasisOrchestrator") -> str:
        """Check if background tasks are running properly."""
        try:
            if not orchestrator.background_tasks:
                return "no_tasks"

            running_tasks = sum(1 for task in orchestrator.background_tasks if not task.done())
            total_tasks = len(orchestrator.background_tasks)

            if running_tasks == total_tasks:
                return "healthy"
            elif running_tasks > 0:
                return f"degraded({running_tasks}/{total_tasks})"
            else:
                return "failed"

        except Exception as e:
            logger.error(f"Background task check failed: {e}")
            return "error"

    async def _check_supervisor_health(self, orchestrator: "HomeostasisOrchestrator") -> str:
        """Check if system supervisor is responding."""
        try:
            if not orchestrator.supervisor:
                return "missing"

            # Try to get supervisor status
            status = orchestrator.supervisor.get_supervisor_status()
            if status and status.get("running"):
                return "healthy"
            else:
                return "not_running"

        except Exception as e:
            logger.error(f"Supervisor health check failed: {e}")
            return "error"

    async def _restart_orchestrator(self, orchestrator: "HomeostasisOrchestrator"):
        """Attempt to restart the orchestrator."""
        try:
            logger.info("🔄 Attempting orchestrator restart...")

            # Stop current instance
            await orchestrator.stop()

            # Brief pause
            await asyncio.sleep(2.0)

            # Restart
            await orchestrator.start()

            logger.info("✅ Orchestrator restart successful")

        except Exception as e:
            logger.error(f"❌ Orchestrator restart failed: {e}")
            raise

    async def _emergency_restart_orchestrator(self):
        """Emergency restart when watchdog has too many errors."""
        try:
            logger.error("🚨 EMERGENCY: Too many watchdog errors - attempting full restart")

            # Get fresh orchestrator reference
            global _homeostasis_instance
            if _homeostasis_instance:
                await self._restart_orchestrator(_homeostasis_instance)
            else:
                logger.error("❌ No global orchestrator instance available for emergency restart")

        except Exception as e:
            logger.error(f"❌ Emergency restart failed: {e}")


class DLQMonitor:
    """
    Dead Letter Queue monitoring service for Phase 2C.

    Periodically polls kernel DLQ to:
    - Analyze failure patterns (group by action_type, target_service, reason)
    - Calculate failure rates per actuator type
    - Auto-disable actuator types with high failure rates
    - Expose DLQ health metrics for observability

    Integrates with HomeostasisActuators to quarantine problematic actuators.
    """

    def __init__(
        self,
        kernel_loop=None,
        actuators=None,
        poll_interval: float = 60.0,
        failure_rate_threshold: float = 0.5,
        quarantine_threshold: int = 5,
    ):
        """
        Initialize DLQ monitor.

        Args:
            kernel_loop: Kernel loop instance (for get_dlq_items)
            actuators: HomeostasisActuators instance (for disable_actuator)
            poll_interval: How often to poll DLQ (seconds)
            failure_rate_threshold: Failure rate to trigger auto-disable (0.0-1.0)
            quarantine_threshold: Minimum failures before auto-disable
        """
        self.kernel_loop = kernel_loop
        self.actuators = actuators
        self.poll_interval = poll_interval
        self.failure_rate_threshold = failure_rate_threshold
        self.quarantine_threshold = quarantine_threshold

        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Metrics
        self.dlq_count = 0
        self.top_failure_reasons: Dict[str, int] = {}
        self.quarantined_actuators: List[str] = []
        self.failure_history: Dict[str, List[dict]] = {}  # action_type -> [failures]

        logger.info(
            f"🔍 DLQ Monitor initialized (poll={poll_interval}s, "
            f"threshold={failure_rate_threshold}, quarantine_min={quarantine_threshold})"
        )

    async def start(self):
        """Start DLQ monitoring loop."""
        if self.running:
            logger.warning("[DLQ] Monitor already running")
            return

        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("🚀 DLQ Monitor started")

    async def stop(self):
        """Stop DLQ monitoring loop."""
        self.running = False
        if self.monitor_task and not self.monitor_task.done():
            self.monitor_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitor_task
        logger.info("🛑 DLQ Monitor stopped")

    async def _monitor_loop(self):
        """Main DLQ monitoring loop."""
        while self.running:
            try:
                await self._poll_and_analyze_dlq()
                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                logger.debug("[DLQ] Monitor loop cancelled")
                break
            except Exception as e:
                logger.error(f"[DLQ] Monitor loop error: {e}", exc_info=True)
                await asyncio.sleep(self.poll_interval)  # Continue despite errors

    async def _poll_and_analyze_dlq(self):
        """Poll DLQ and analyze failure patterns."""
        if not self.kernel_loop:
            logger.debug("[DLQ] No kernel loop available, skipping poll")
            return

        try:
            # Get recent DLQ items (last 100)
            if not hasattr(self.kernel_loop, "get_dlq_items"):
                logger.debug("[DLQ] Kernel does not support get_dlq_items")
                return

            # Support both async and sync implementations of get_dlq_items
            try:
                items = self.kernel_loop.get_dlq_items(limit=100)
            except TypeError:
                # Some kernels may not accept keyword args
                items = self.kernel_loop.get_dlq_items()  # type: ignore[call-arg]

            import inspect

            if inspect.isawaitable(items):
                dlq_items = await items  # type: ignore[assignment]
            else:
                dlq_items = items  # type: ignore[assignment]

            if dlq_items is None:
                dlq_items = []
            self.dlq_count = len(dlq_items)

            if self.dlq_count == 0:
                logger.debug("[DLQ] No items in DLQ")
                return

            logger.info(f"[DLQ] Analyzing {self.dlq_count} DLQ items")

            # Analyze patterns
            await self._analyze_failure_patterns(dlq_items)

            # Check for high failure rates and quarantine if needed
            await self._check_and_quarantine()

        except Exception as e:
            logger.error(f"[DLQ] Poll and analyze failed: {e}", exc_info=True)

    async def _analyze_failure_patterns(self, dlq_items: List[dict]):
        """
        Analyze DLQ items for patterns.

        Groups by:
        - action_type (for actuator_action tasks)
        - reason (failure reason)
        """
        reason_counts: Dict[str, int] = {}
        action_type_failures: Dict[str, List[dict]] = {}

        for item in dlq_items:
            # Count reasons
            reason = item.get("reason", "unknown")
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

            # Track actuator_action failures
            task_type = item.get("type")
            if task_type == "actuator_action":
                data = item.get("data", {})
                action_type = data.get("action_type", "unknown")

                if action_type not in action_type_failures:
                    action_type_failures[action_type] = []

                # Normalize timestamp to epoch seconds to avoid type errors when comparing to floats
                raw_ts = item.get("ts")
                ts_epoch: float
                if isinstance(raw_ts, (int, float)):
                    ts_epoch = float(raw_ts)
                elif isinstance(raw_ts, str):
                    # Try parsing as float string first, then ISO-8601
                    try:
                        ts_epoch = float(raw_ts)
                    except Exception:
                        try:
                            s = raw_ts.replace("Z", "+00:00")
                            dt = datetime.fromisoformat(s)
                            ts_epoch = dt.timestamp()
                        except Exception:
                            ts_epoch = 0.0
                else:
                    ts_epoch = 0.0

                action_type_failures[action_type].append(
                    {
                        "ts": ts_epoch,
                        "reason": reason,
                        "trace_id": item.get("trace_id"),
                        "target": data.get("target_service"),
                    }
                )

        # Update metrics
        self.top_failure_reasons = dict(
            sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        self.failure_history.update(action_type_failures)

        # Log top failures
        if self.top_failure_reasons:
            logger.info(
                f"[DLQ] Top failure reasons: {', '.join(f'{r}={c}' for r, c in list(self.top_failure_reasons.items())[:3])}"
            )

    async def _check_and_quarantine(self):
        """
        Check failure rates and quarantine actuator types if needed.

        Criteria:
        - Failure rate > threshold (default 50%)
        - At least quarantine_threshold failures (default 5)
        """
        if not self.actuators:
            return

        for action_type, failures in self.failure_history.items():
            if action_type in self.quarantined_actuators:
                continue  # Already quarantined

            # Count recent failures (last hour)
            recent_cutoff = time.time() - 3600
            recent_failures = [f for f in failures if f.get("ts", 0) > recent_cutoff]

            if len(recent_failures) < self.quarantine_threshold:
                continue  # Not enough failures

            # Calculate failure rate (assume all recent DLQ entries for this action are failures)
            # This is conservative: we don't track successes separately, so we treat DLQ presence as failure
            failure_count = len(recent_failures)

            # For now, we use a simple heuristic: if we see N failures in DLQ and no successful execution info,
            # we assume high failure rate
            # Integration point: actuator success metrics for more accurate rate calculation

            if failure_count >= self.quarantine_threshold:
                logger.warning(
                    f"[DLQ] Actuator '{action_type}' has {failure_count} recent failures, "
                    f"auto-disabling (threshold={self.quarantine_threshold})"
                )

                # Quarantine actuator
                await self._quarantine_actuator(action_type, recent_failures)

    async def _quarantine_actuator(self, action_type: str, failures: List[dict]):
        """
        Quarantine an actuator type by disabling it.

        Args:
            action_type: Action type to disable
            failures: List of failure records
        """
        if action_type in self.quarantined_actuators:
            return

        # Mark as quarantined
        self.quarantined_actuators.append(action_type)

        # Disable in actuators (if method exists)
        if hasattr(self.actuators, "disable_actuator"):
            try:
                await self.actuators.disable_actuator(action_type)
                logger.error(f"[DLQ] Actuator '{action_type}' QUARANTINED due to high failure rate")

                # Log failure reasons
                reasons = {f.get("reason", "unknown") for f in failures[:10]}
                logger.error(f"[DLQ] Failure reasons: {', '.join(reasons)}")

            except Exception as e:
                logger.error(f"[DLQ] Failed to disable actuator '{action_type}': {e}")
        else:
            logger.warning("[DLQ] Actuators does not support disable_actuator method")

    def get_metrics(self) -> dict:
        """
        Get DLQ health metrics.

        Returns:
            dict: DLQ metrics including count, top failures, quarantined actuators
        """
        return {
            "dlq_count": self.dlq_count,
            "top_failure_reasons": self.top_failure_reasons,
            "quarantined_actuators": self.quarantined_actuators,
            "quarantined_count": len(self.quarantined_actuators),
        }


class HomeostasisOrchestrator:
    """
    Main orchestrator for the Aetherra Homeostasis system (Phase 3: Singleton + Watchdog).

    Coordinates all homeostasis components and provides a unified interface
    for system stability management. Now includes persistent watchdog monitoring
    that ensures continuous operation even under heavy system load.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the homeostasis orchestrator."""
        self.config_dir = config_dir or "Aetherra/homeostasis/configs"

        # Core components
        self.metrics: Optional[StabilityMetrics] = None
        self.controller: Optional[HomeostasisController] = None
        self.actuators: Optional[HomeostasisActuators] = None
        self.supervisor: Optional[SystemSupervisor] = None

        # Audit and trace layer for deep diagnostics
        self.audit_layer = get_audit_layer()

        # State management
        self.running = False
        self.initialized = False
        self.start_time: Optional[float] = None

        # Task management
        self.background_tasks: List[asyncio.Task] = []

        # Phase 3: Persistent watchdog for guaranteed execution
        self.watchdog: Optional[HomeostasisWatchdog] = None
        self.scheduler_integration = False  # AetherRuntime scheduler integration flag

        # Phase 4: Cross-system feedback mechanism
        self.feedback_system: Optional[SystemFeedback] = None

        # Phase 5: Continuous validation system
        self.validator: Optional[ContinuousValidator] = None

        # Phase 6: Live observability system
        self.observability: Optional[LiveObservability] = None

        # Phase 7: Autonomous error correction
        self.error_corrector: Optional[AutonomousErrorCorrector] = None

        # Phase 8: Self-improvement metrics bridge
        self.metrics_bridge: Optional[SelfImprovementMetricsBridge] = None

        # Phase 9: Self-incorporation metrics bridge
        self.si_metrics_bridge: Optional[SelfIncorporationMetricsBridge] = None

        # Phase 2C: DLQ monitoring service
        self.dlq_monitor: Optional[DLQMonitor] = None

        # Performance tracking
        self.uptime_start: Optional[float] = None
        self.restart_count = 0
        self.error_recovery_count = 0

        logger.info("🌐 Homeostasis orchestrator initialized")

    async def initialize(self):
        """Initialize all homeostasis components."""
        if self.initialized:
            logger.warning("Homeostasis already initialized")
            return

        try:
            logger.info("🚀 Initializing Aetherra Homeostasis System")

            # Initialize components in dependency order
            self.metrics = get_stability_metrics()
            self.actuators = HomeostasisActuators(
                policy_path=f"{self.config_dir}/homeostasis_policy.yaml"
            )
            self.controller = HomeostasisController(
                metrics=self.metrics,
                actuators=self.actuators,
                config_path=f"{self.config_dir}/setpoints.yaml",
                policy_path=f"{self.config_dir}/homeostasis_policy.yaml",
            )
            self.supervisor = get_system_supervisor()

            # Phase 4: Initialize cross-system feedback mechanism
            self.feedback_system = SystemFeedback(self)

            # Phase 5: Initialize continuous validation system
            self.validator = ContinuousValidator(self)

            # Phase 6: Initialize live observability system
            self.observability = LiveObservability(self)

            # Phase 7: Initialize autonomous error correction
            self.error_corrector = AutonomousErrorCorrector()

            # Phase 8: Initialize self-improvement metrics bridge
            self.metrics_bridge = SelfImprovementMetricsBridge()

            # Phase 9: Initialize self-incorporation metrics bridge
            self.si_metrics_bridge = SelfIncorporationMetricsBridge()

            # Phase 2C: Initialize DLQ monitor (will be started after kernel injection)
            self.dlq_monitor = DLQMonitor(
                kernel_loop=None,  # Will be set during injection
                actuators=self.actuators,
                poll_interval=60.0,
                failure_rate_threshold=0.5,
                quarantine_threshold=5,
            )

            # Register with service registry
            await self._register_with_service_registry()

            self.initialized = True
            logger.info("✅ Homeostasis system initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize homeostasis system: {e}")
            raise

    async def start(self):
        """Start the homeostasis system with persistent watchdog (Phase 3)."""
        if not self.initialized:
            await self.initialize()

        if self.running:
            logger.warning("Homeostasis system is already running")
            return

        try:
            logger.info("🌟 Starting Aetherra Homeostasis System (Phase 3: Watchdog)")
            self.start_time = time.time()
            self.uptime_start = time.time()
            self.running = True

            # Start all components
            await self._start_components()

            # Start background monitoring
            await self._start_background_tasks()

            # Phase 3: Start persistent watchdog
            await self._start_watchdog()

            # Phase 3: Integrate with AetherRuntime scheduler if available
            await self._integrate_with_scheduler()

            logger.info("✅ Homeostasis system started successfully with watchdog protection")

        except Exception as e:
            logger.error(f"❌ Failed to start homeostasis system: {e}")
            self.running = False
            raise

    async def _start_watchdog(self):
        """Start the persistent watchdog monitoring (Phase 3 requirement)."""
        try:
            if self.watchdog is None:
                self.watchdog = HomeostasisWatchdog(self)

            self.watchdog.start()
            logger.info("🐕 Persistent watchdog started - system will never die")

        except Exception as e:
            logger.error(f"❌ Failed to start watchdog: {e}")
            raise

    async def _integrate_with_scheduler(self):
        """Integrate with AetherRuntime scheduler for guaranteed execution (Phase 3)."""
        try:
            # Try to get the scheduler service
            registry = await get_service_registry()
            if not registry:
                logger.warning("⚠️ Service registry not available for scheduler integration")
                return

            scheduler_info = registry.get_service_info("scheduler")
            if not scheduler_info:
                logger.warning("⚠️ AetherRuntime scheduler not available")
                return

            # Register homeostasis as a high-priority persistent task
            if hasattr(scheduler_info.instance, "register_persistent_task"):
                await scheduler_info.instance.register_persistent_task(
                    task_id="homeostasis_core_monitoring",
                    task_function=self._scheduler_heartbeat,
                    interval=15.0,  # Every 15 seconds
                    priority="HIGH",
                    description="Homeostasis core system monitoring",
                    restart_on_failure=True,
                    max_failures=5,
                )

                self.scheduler_integration = True
                logger.info("✅ Integrated with AetherRuntime scheduler for guaranteed execution")

            else:
                logger.warning("⚠️ Scheduler doesn't support persistent tasks")

        except Exception as e:
            logger.warning(f"⚠️ Scheduler integration failed (non-critical): {e}")

    async def _scheduler_heartbeat(self):
        """Heartbeat function called by AetherRuntime scheduler (Phase 3)."""
        try:
            # Verify homeostasis is still running
            if not self.running:
                logger.error("🚨 Homeostasis detected as stopped by scheduler - attempting restart")
                await self.start()
                return

            # Verify critical components are alive
            if self.supervisor:
                health = self.supervisor.get_system_health()
                if health.get("runlevel") == "FAILED":
                    logger.error("🚨 System supervisor reports FAILED state - triggering recovery")
                    await self._emergency_recovery()

            # Verify watchdog is alive
            if self.watchdog:
                watchdog_age = time.time() - self.watchdog.last_heartbeat
                if watchdog_age > 120.0:  # Watchdog silent for 2 minutes
                    logger.error("🚨 Watchdog appears dead - restarting")
                    await self._restart_watchdog()

            logger.debug("💓 Scheduler heartbeat: homeostasis healthy")

        except Exception as e:
            logger.error(f"❌ Scheduler heartbeat failed: {e}")
            raise

    async def _restart_watchdog(self):
        """Restart the watchdog if it becomes unresponsive."""
        try:
            if self.watchdog:
                self.watchdog.stop()

            await asyncio.sleep(1.0)
            await self._start_watchdog()

            logger.info("✅ Watchdog restarted successfully")

        except Exception as e:
            logger.error(f"❌ Watchdog restart failed: {e}")

    async def _emergency_recovery(self):
        """Emergency recovery procedure (Phase 3)."""
        try:
            self.error_recovery_count += 1
            logger.error(f"🚨 EMERGENCY RECOVERY #{self.error_recovery_count}")

            # Stop all components
            await self.stop()

            # Brief pause
            await asyncio.sleep(3.0)

            # Full restart
            await self.start()

            logger.info("✅ Emergency recovery completed")

        except Exception as e:
            logger.error(f"❌ Emergency recovery failed: {e}")

    async def stop(self):
        """Stop the homeostasis system including watchdog."""
        if not self.running:
            logger.warning("Homeostasis system is not running")
            return

        try:
            logger.info("🛑 Stopping Aetherra Homeostasis System")
            self.running = False

            # Stop watchdog first
            if self.watchdog:
                self.watchdog.stop()
                self.watchdog = None

            # Phase 2C: Stop DLQ monitor
            if self.dlq_monitor:
                await self.dlq_monitor.stop()

            # Stop background tasks
            await self._stop_background_tasks()

            # Stop components
            await self._stop_components()

            # Unregister from scheduler if integrated
            if self.scheduler_integration:
                await self._unregister_from_scheduler()

            logger.info("✅ Homeostasis system stopped successfully")

        except Exception as e:
            logger.error(f"❌ Error stopping homeostasis system: {e}")

    async def _unregister_from_scheduler(self):
        """Unregister from AetherRuntime scheduler."""
        try:
            registry = await get_service_registry()
            if registry:
                scheduler_info = registry.get_service_info("scheduler")
                if scheduler_info and hasattr(
                    scheduler_info.instance, "unregister_persistent_task"
                ):
                    await scheduler_info.instance.unregister_persistent_task(
                        "homeostasis_core_monitoring"
                    )
                    logger.info("✅ Unregistered from AetherRuntime scheduler")

            self.scheduler_integration = False

        except Exception as e:
            logger.warning(f"⚠️ Scheduler unregistration failed: {e}")

    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status including watchdog info (Phase 3)."""
        current_time = time.time()

        status = {
            "running": self.running,
            "initialized": self.initialized,
            "start_time": self.start_time,
            "uptime": current_time - self.uptime_start if self.uptime_start else 0,
            "restart_count": self.restart_count,
            "error_recovery_count": self.error_recovery_count,
            # Phase 3: Watchdog status
            "watchdog": {
                "active": self.watchdog is not None and self.watchdog.running,
                "last_heartbeat": self.watchdog.last_heartbeat if self.watchdog else None,
                "cycle_count": self.watchdog.cycle_count if self.watchdog else 0,
                "error_count": self.watchdog.error_count if self.watchdog else 0,
                "thread_alive": self.watchdog.thread.is_alive()
                if self.watchdog and self.watchdog.thread
                else False,
            },
            # Scheduler integration
            "scheduler_integration": self.scheduler_integration,
            # Component status
            "components": {
                "metrics": self.metrics is not None,
                "controller": self.controller is not None,
                "actuators": self.actuators is not None,
                "supervisor": self.supervisor is not None,
            },
            # Background tasks
            "background_tasks": {
                "total": len(self.background_tasks),
                "running": sum(1 for task in self.background_tasks if not task.done()),
                "completed": sum(1 for task in self.background_tasks if task.done()),
            },
        }

        return status

    async def shutdown(self):
        """Alias for stop() - used by OS launcher during graceful shutdown."""
        await self.stop()

    async def _register_with_service_registry(self):
        """Register homeostasis with the service registry."""
        try:
            # The registry expects metadata/dependencies, not arbitrary kwargs.
            # Move service_type/description into metadata for compatibility.
            await register_service(
                name="aetherra_homeostasis",
                instance=self,
                metadata={
                    "type": "system_management",
                    "description": "Aetherra Homeostasis System for autonomous stability control",
                },
            )
            logger.debug("📝 Registered with service registry")

        except Exception as e:
            logger.warning(f"Failed to register with service registry: {e}")

    async def _start_components(self):
        """Start all homeostasis components."""
        # Start supervisor first (it manages runlevel transitions)
        if self.supervisor:
            supervisor_task = asyncio.create_task(self.supervisor.start())
            self.background_tasks.append(supervisor_task)

        # Start metrics collection
        if self.metrics:
            metrics_task = asyncio.create_task(self.metrics.start_continuous_collection())
            self.background_tasks.append(metrics_task)

        # Start controller (it depends on metrics and actuators)
        if self.controller:
            # Set initial mode based on system state
            initial_mode = self._determine_initial_mode()
            self.controller.set_mode(initial_mode)

            controller_task = asyncio.create_task(self.controller.start())
            self.background_tasks.append(controller_task)

        # Phase 7: Start autonomous error correction
        if self.error_corrector:
            await self.error_corrector.start()

        # Phase 8: Start self-improvement metrics bridge
        if self.metrics_bridge:
            await self.metrics_bridge.start()

        # Phase 9: Start self-incorporation metrics bridge
        if self.si_metrics_bridge:
            await self.si_metrics_bridge.start()

        logger.debug("🔧 All components started")

    async def _stop_components(self):
        """Stop all homeostasis components."""
        # Stop metrics bridges first (Phase 9, then Phase 8)
        if self.si_metrics_bridge:
            await self.si_metrics_bridge.stop()

        if self.metrics_bridge:
            await self.metrics_bridge.stop()

        # Stop autonomous error corrector
        if self.error_corrector:
            await self.error_corrector.stop()

        # Stop controller
        if self.controller:
            self.controller.stop()

        # Stop supervisor
        if self.supervisor:
            self.supervisor.stop()

        logger.debug("🔧 All components stopped")

    async def _start_background_tasks(self):
        """Start background monitoring and coordination tasks."""
        # Start health reporting task
        health_task = asyncio.create_task(self._health_reporting_loop())
        self.background_tasks.append(health_task)

        # Start coordination task
        coordination_task = asyncio.create_task(self._coordination_loop())
        self.background_tasks.append(coordination_task)

        # Phase 4: Start cross-system feedback collection loop
        if self.feedback_system:
            feedback_task = asyncio.create_task(self._feedback_collection_loop())
            self.background_tasks.append(feedback_task)

        # Phase 5: Start continuous validation loop
        if self.validator:
            validation_task = asyncio.create_task(self._validation_loop())
            self.background_tasks.append(validation_task)

        # Start system verification loop (Phase 2 requirement)
        verification_task = asyncio.create_task(self._continuous_system_verification_loop())
        self.background_tasks.append(verification_task)

        # Phase 2C: Start DLQ monitoring loop
        if self.dlq_monitor:
            # Inject kernel reference dynamically
            try:
                from aetherra_kernel_loop import get_kernel  # type: ignore

                kernel = get_kernel()
                if kernel:
                    self.dlq_monitor.kernel_loop = kernel
                    await self.dlq_monitor.start()
                    logger.info("✅ DLQ Monitor started with kernel integration")
                else:
                    logger.warning("⚠️ Kernel not available, DLQ monitoring disabled")
            except ImportError:
                logger.warning("⚠️ Kernel loop not available, DLQ monitoring disabled")

        logger.debug("🔄 Background tasks started")

    async def _continuous_system_verification_loop(self):
        """
        Continuous system verification loop (Phase 2 requirement).

        Automatically re-assert equilibrium every cycle and logs corrective actions.
        """
        verification_interval = 60.0  # Run every minute

        while self.running:
            try:
                # Run comprehensive system verification
                if self.supervisor:
                    verification_result = await self.supervisor.verify_all_systems_active()

                    # Log any issues found
                    if verification_result.get("overall_status") != "healthy":
                        logger.warning(
                            f"🔍 System verification: {verification_result['overall_status'].upper()}"
                        )

                        # Log failed vital checks
                        for check_name, check_result in verification_result.get(
                            "vital_checks", {}
                        ).items():
                            if check_result.get("status") != "healthy":
                                logger.warning(
                                    f"⚠️ {check_name}: {check_result.get('reason', 'unknown')}"
                                )

                    # Auto-restart logic for any inactive critical service
                    await self._auto_restart_inactive_services(verification_result)

                await asyncio.sleep(verification_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ System verification loop error: {e}")
                await asyncio.sleep(verification_interval)

    async def _auto_restart_inactive_services(self, verification_result: Dict[str, Any]):
        """
        Auto-restart logic for any inactive critical service (Phase 2 requirement).
        """
        try:
            if not self.supervisor:
                return

            systems = verification_result.get("systems", {})
            failed_services = systems.get("failed_services", 0)

            if failed_services > 0:
                logger.info("🔄 Attempting auto-restart for failed services")

                # Trigger service recovery through supervisor
                await self.supervisor._manage_service_recovery()

                # Log corrective action to audit stream for transparency
                logger.info(
                    f"🔧 Auto-restart audit: {failed_services} failed services, "
                    f"status: {verification_result.get('overall_status')}"
                )

                # Add to verification result for logging
                if "corrective_actions" not in verification_result:
                    verification_result["corrective_actions"] = []
                verification_result["corrective_actions"].append(
                    f"Auto-restart attempted for {failed_services} failed services"
                )

        except Exception as e:
            logger.error(f"❌ Auto-restart logic failed: {e}")

    async def _stop_background_tasks(self):
        """Stop all background tasks."""
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task

        self.background_tasks.clear()
        logger.debug("🛑 Background tasks stopped")

    def _determine_initial_mode(self) -> ControllerMode:
        """Determine initial controller mode based on system state."""
        # EMERGENCY FIX: Always start in ACTIVE mode for proper self-healing
        # The system should be able to self-heal from the moment it starts
        logger.info(
            "🚨 EMERGENCY MODE: Starting homeostasis in ACTIVE mode for immediate self-healing"
        )
        return ControllerMode.ACTIVE

        # Original logic (commented out):
        # Start in observe mode and transition based on system health
        # if self.supervisor and self.supervisor.is_system_online():
        #     return ControllerMode.ACTIVE
        # else:
        #     return ControllerMode.OBSERVE_ONLY

    async def _health_reporting_loop(self):
        """Background loop for health reporting to external systems."""
        while self.running:
            try:
                # Collect comprehensive health status
                health_status = await self.get_system_health_status()

                # Report to Lyrixa if available
                await self._report_to_lyrixa(health_status)

                # Report to Hub if available
                await self._report_to_hub(health_status)

                # Sleep before next report
                await asyncio.sleep(60.0)  # Report every minute

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health reporting loop: {e}")
                await asyncio.sleep(60.0)

    async def _coordination_loop(self):
        """Background loop for coordinating between components."""
        while self.running:
            try:
                # Coordinate controller mode with supervisor state
                if self.controller and self.supervisor:
                    supervisor_state = self.supervisor.get_runlevel()
                    current_mode = self.controller.mode

                    # Adjust controller mode based on system state
                    if (
                        supervisor_state.value == "FAILED"
                        and current_mode != ControllerMode.EMERGENCY
                    ):
                        self.controller.set_mode(ControllerMode.EMERGENCY)
                        logger.warning("🚨 Switched to emergency mode due to system failure")

                    elif (
                        supervisor_state.value == "ONLINE"
                        and current_mode == ControllerMode.OBSERVE_ONLY
                    ):
                        self.controller.set_mode(ControllerMode.ACTIVE)
                        logger.info("✅ Switched to active mode - system online")

                    elif (
                        supervisor_state.value in ["OFFLINE", "DEGRADED"]
                        and current_mode == ControllerMode.ACTIVE
                    ):
                        self.controller.set_mode(ControllerMode.ACTIVE_LIMITED)
                        logger.info("⚠️ Switched to limited mode - system degraded")

                # Sleep before next coordination cycle
                await asyncio.sleep(30.0)  # Coordinate every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in coordination loop: {e}")
                await asyncio.sleep(30.0)

    async def _report_to_lyrixa(self, health_status: Dict[str, Any]):
        """Report system health to Lyrixa."""
        try:
            registry = await get_service_registry()
            if registry:
                lyrixa_service = registry.get_service_info("lyrixa_basic")
                if lyrixa_service and hasattr(lyrixa_service.instance, "receive_health_update"):
                    await lyrixa_service.instance.receive_health_update(health_status)

        except Exception as e:
            logger.debug(f"Could not report to Lyrixa: {e}")

    async def _report_to_hub(self, health_status: Dict[str, Any]):
        """Report system health to Hub."""
        try:
            registry = await get_service_registry()
            if registry:
                hub_service = registry.get_service_info("aetherra_hub")
                if hub_service and hasattr(hub_service.instance, "receive_health_update"):
                    await hub_service.instance.receive_health_update(health_status)

        except Exception as e:
            logger.debug(f"Could not report to Hub: {e}")

    async def _feedback_collection_loop(self):
        """
        Background loop for collecting cross-system feedback (Phase 4).

        This implements proactive feedback collection from all monitored systems
        for adaptive threshold tuning and performance optimization.
        """
        while self.running:
            try:
                if self.feedback_system:
                    # Check if it's time to collect feedback
                    current_time = time.time()
                    time_since_last = current_time - self.feedback_system.last_feedback_collection

                    if time_since_last >= self.feedback_system.feedback_interval:
                        # Collect feedback from all systems
                        feedback_collection = (
                            await self.feedback_system.collect_feedback_from_systems()
                        )

                        if feedback_collection:
                            logger.debug(
                                f"📊 Collected feedback from {len(feedback_collection)} systems"
                            )

                    # Sleep for a portion of the feedback interval
                    await asyncio.sleep(min(30.0, self.feedback_system.feedback_interval / 2))
                else:
                    # If feedback system is not available, sleep longer
                    await asyncio.sleep(60.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in feedback collection loop: {e}")
                await asyncio.sleep(60.0)

    async def _validation_loop(self):
        """
        Background loop for continuous validation (Phase 5).

        This implements continuous monitoring of homeostasis effectiveness
        and triggers self-tuning when performance degrades.
        """
        while self.running:
            try:
                if self.validator:
                    # Check if it's time to validate
                    current_time = time.time()
                    time_since_last = current_time - self.validator.last_validation

                    if time_since_last >= self.validator.validation_interval:
                        # Perform comprehensive validation
                        validation_report = (
                            await self.validator.validate_homeostasis_effectiveness()
                        )

                        # Log significant validation results
                        effectiveness = validation_report.get("overall_effectiveness", 0.0)
                        tuning_required = validation_report.get("tuning_required", False)

                        if tuning_required:
                            logger.warning(
                                f"🔍 Validation: {effectiveness:.2f} effectiveness - tuning triggered"
                            )
                        else:
                            logger.debug(
                                f"🔍 Validation: {effectiveness:.2f} effectiveness - performing well"
                            )

                    # Sleep for a portion of the validation interval
                    await asyncio.sleep(min(60.0, self.validator.validation_interval / 2))
                else:
                    # If validator is not available, sleep longer
                    await asyncio.sleep(120.0)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in validation loop: {e}")
                await asyncio.sleep(120.0)

    async def _system_verification_loop(self):
        """
        Background loop for system verification (Phase 2 requirement).

        This implements continuous validation of system health and triggers
        corrective actions when issues are detected.
        """
        while self.running:
            try:
                if self.supervisor:
                    # Verify all systems are active
                    verification_result = await self.supervisor.verify_all_systems_active()

                    if not verification_result:
                        logger.warning("⚠️ System verification failed - triggering heartbeat")
                        # Trigger heartbeat to attempt corrections
                        await self.supervisor.heartbeat_all()

                # Sleep before next verification
                await asyncio.sleep(45.0)  # Verify every 45 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in system verification loop: {e}")
                await asyncio.sleep(45.0)

    # Public API Methods

    async def get_system_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        status: Dict[str, Any] = {
            "homeostasis": {
                "running": self.running,
                "initialized": self.initialized,
                "start_time": self.start_time,
                "uptime": time.time() - self.start_time if self.start_time else 0.0,
            }
        }

        # Add metrics status
        if self.metrics:
            status["metrics"] = self.metrics.get_health_summary()
            snapshot = self.metrics.get_current_snapshot()
            status["current_snapshot"] = snapshot.__dict__ if snapshot else None

        # Add controller status
        if self.controller:
            status["controller"] = self.controller.get_controller_status()
            status["control_loops"] = self.controller.get_control_loop_status()

        # Add actuator status
        if self.actuators:
            status["actuators"] = self.actuators.get_actuator_status()
            status["recent_actions"] = self.actuators.get_action_history(10)

        # Add supervisor status
        if self.supervisor:
            status["supervisor"] = self.supervisor.get_supervisor_status()
            status["system_health"] = self.supervisor.get_system_health()

        # Phase 2C: Add DLQ monitor metrics
        if self.dlq_monitor:
            status["dlq_health"] = self.dlq_monitor.get_metrics()

        return status

    async def set_controller_mode(self, mode: ControllerMode, reason: str = "External request"):
        """Set the controller operating mode."""
        if self.controller:
            self.controller.set_mode(mode)
            logger.info(f"🎛️ Controller mode set to {mode.value}: {reason}")
        else:
            logger.warning("Cannot set controller mode: controller not initialized")

    async def emergency_stop(self, reason: str = "External emergency stop"):
        """Trigger emergency stop of all homeostasis actions."""
        logger.critical(f"🚨 EMERGENCY STOP TRIGGERED: {reason}")

        if self.controller:
            self.controller.emergency_stop()

        if self.supervisor:
            self.supervisor.force_runlevel_transition(
                self.supervisor.current_runlevel.__class__.FAILED, f"Emergency stop: {reason}"
            )

    async def reset_emergency_stop(self):
        """Reset emergency stop condition."""
        if self.controller:
            self.controller.reset_emergency_stop()

        logger.info("✅ Emergency stop reset")

    async def get_metrics_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get current metrics snapshot."""
        if self.metrics:
            snapshot = self.metrics.get_current_snapshot()
            return snapshot.__dict__ if snapshot else None
        return None

    # Phase 4: Cross-System Feedback API Methods

    async def receive_system_feedback(self, source: str, feedback_data: Dict[str, Any]) -> bool:
        """
        Receive feedback from external systems for adaptive tuning (Phase 4).

        Args:
            source: Name of the system providing feedback
            feedback_data: Performance metrics and adaptation suggestions

        Returns:
            bool: True if feedback was processed successfully
        """
        if self.feedback_system:
            return await self.feedback_system.receive_system_feedback(source, feedback_data)
        else:
            logger.warning("Feedback system not initialized - ignoring feedback")
            return False

    async def collect_all_system_feedback(self) -> Dict[str, Dict[str, Any]]:
        """
        Proactively collect feedback from all monitored systems (Phase 4).

        Returns:
            Dict with feedback from each system that responded
        """
        if self.feedback_system:
            return await self.feedback_system.collect_feedback_from_systems()
        else:
            logger.warning("Feedback system not initialized")
            return {}

    def get_feedback_summary(self) -> Dict[str, Any]:
        """
        Get summary of recent feedback and adaptive adjustments (Phase 4).

        Returns:
            Summary of feedback history and current threshold adjustments
        """
        if self.feedback_system:
            return self.feedback_system.get_feedback_summary()
        else:
            return {"error": "Feedback system not initialized"}

    async def trigger_adaptive_tuning(self) -> Dict[str, Any]:
        """
        Manually trigger adaptive tuning based on recent feedback (Phase 4).

        Returns:
            Summary of adjustments made
        """
        if not self.feedback_system:
            return {"error": "Feedback system not initialized"}

        # Collect fresh feedback from all systems
        fresh_feedback = await self.collect_all_system_feedback()

        # Get current adjustments
        adjustments = self.get_feedback_summary()

        return {
            "fresh_feedback_collected": len(fresh_feedback),
            "systems_responded": list(fresh_feedback.keys()),
            "current_adjustments": adjustments.get("active_adjustments", {}),
            "total_feedback_entries": adjustments.get("total_feedback_entries", 0),
        }

    # Phase 5: Continuous Validation API Methods

    async def validate_effectiveness(self) -> Dict[str, Any]:
        """
        Manually trigger effectiveness validation (Phase 5).

        Returns:
            Comprehensive validation report with effectiveness scores and recommendations
        """
        if self.validator:
            return await self.validator.validate_homeostasis_effectiveness()
        else:
            return {"error": "Validation system not initialized"}

    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation history and effectiveness trends (Phase 5).

        Returns:
            Summary of effectiveness metrics, trends, and validation history
        """
        if self.validator:
            return self.validator.get_validation_summary()
        else:
            return {"error": "Validation system not initialized"}

    async def trigger_self_tuning(self) -> Dict[str, Any]:
        """
        Manually trigger self-tuning of homeostasis parameters (Phase 5).

        Returns:
            Summary of tuning actions taken
        """
        if not self.validator:
            return {"error": "Validation system not initialized"}

        # Perform fresh validation to get current effectiveness
        validation_report = await self.validator.validate_homeostasis_effectiveness()

        # Force self-tuning regardless of effectiveness threshold
        await self.validator._trigger_self_tuning(validation_report)

        return {
            "tuning_triggered": True,
            "validation_report": validation_report,
            "effectiveness_after_tuning": validation_report.get("overall_effectiveness", 0.0),
        }

    def get_effectiveness_metrics(self) -> Dict[str, Any]:
        """
        Get current effectiveness metrics and trends (Phase 5).

        Returns:
            Current effectiveness scores and historical trends
        """
        if not self.validator:
            return {"error": "Validation system not initialized"}

        return {
            "effectiveness_metrics": self.validator.effectiveness_metrics.copy(),
            "recent_validations": self.validator.validation_history[-5:]
            if self.validator.validation_history
            else [],
            "validation_interval": self.validator.validation_interval,
            "effectiveness_threshold": self.validator.min_effectiveness_score,
        }

    async def adjust_validation_sensitivity(
        self, new_threshold: float, new_interval: Optional[float] = None
    ) -> bool:
        """
        Adjust validation sensitivity and timing (Phase 5).

        Args:
            new_threshold: New minimum effectiveness threshold (0.0-1.0)
            new_interval: New validation interval in seconds (optional)

        Returns:
            True if adjustments were applied successfully
        """
        if not self.validator:
            return False

        try:
            if 0.0 <= new_threshold <= 1.0:
                self.validator.min_effectiveness_score = new_threshold
                logger.info(f"🎯 Adjusted effectiveness threshold to {new_threshold}")

            if new_interval and new_interval > 0:
                self.validator.validation_interval = new_interval
                logger.info(f"⏱️ Adjusted validation interval to {new_interval}s")

            return True

        except Exception as e:
            logger.error(f"Failed to adjust validation sensitivity: {e}")
            return False

    # Phase 6: Live Observability API Methods

    async def start_live_monitoring(self) -> bool:
        """
        Start live monitoring and real-time observability (Phase 6).

        Returns:
            True if monitoring started successfully
        """
        if self.observability:
            await self.observability.start_live_monitoring()
            return True
        else:
            logger.warning("Observability system not initialized")
            return False

    async def stop_live_monitoring(self) -> bool:
        """
        Stop live monitoring (Phase 6).

        Returns:
            True if monitoring stopped successfully
        """
        if self.observability:
            await self.observability.stop_live_monitoring()
            return True
        else:
            return False

    def get_live_dashboard(self) -> str:
        """
        Get live dashboard text representation (Phase 6).

        Returns:
            Formatted dashboard showing current system status
        """
        if self.observability:
            return self.observability.generate_live_dashboard()
        else:
            return "❌ Live observability not initialized"

    def get_metrics_summary(self, minutes: int = 5) -> Dict[str, Any]:
        """
        Get summary of recent metrics (Phase 6).

        Args:
            minutes: Number of minutes of history to summarize

        Returns:
            Summary of recent performance metrics
        """
        if self.observability:
            return self.observability.get_metrics_summary(minutes)
        else:
            return {"error": "Observability system not initialized"}

    def export_observability_data(self, filepath: Optional[str] = None) -> Optional[str]:
        """
        Export observability data to file (Phase 6).

        Args:
            filepath: Optional path for export file

        Returns:
            Path to exported file or None if failed
        """
        if self.observability:
            try:
                return self.observability.export_metrics(filepath)
            except Exception as e:
                logger.error(f"Failed to export observability data: {e}")
                return None
        else:
            logger.warning("Observability system not initialized")
            return None

    def is_monitoring_active(self) -> bool:
        """
        Check if live monitoring is currently active (Phase 6).

        Returns:
            True if monitoring is active
        """
        if self.observability:
            return self.observability.monitoring_active
        return False


# Phase 3: Singleton Pattern Implementation
def get_homeostasis_orchestrator(config_dir: Optional[str] = None) -> HomeostasisOrchestrator:
    """
    Get the singleton homeostasis orchestrator instance (Phase 3 requirement).

    This ensures there's only one orchestrator instance system-wide and provides
    global access for integration with other Aetherra components.
    """
    global _homeostasis_instance

    with _homeostasis_lock:
        if _homeostasis_instance is None:
            _homeostasis_instance = HomeostasisOrchestrator(config_dir)
            logger.info("🎯 Singleton homeostasis orchestrator created")

        return _homeostasis_instance


def reset_homeostasis_orchestrator():
    """
    Reset the singleton instance (for testing or emergency recovery).

    WARNING: This should only be used in testing or emergency situations.
    """
    global _homeostasis_instance

    with _homeostasis_lock:
        if _homeostasis_instance and _homeostasis_instance.running:
            logger.warning("🚨 Forcing reset of running homeostasis orchestrator")

        _homeostasis_instance = None
        logger.info("🔄 Homeostasis orchestrator singleton reset")


def is_homeostasis_running() -> bool:
    """Check if the homeostasis system is currently running."""
    global _homeostasis_instance
    return _homeostasis_instance is not None and _homeostasis_instance.running


def get_homeostasis_status() -> Optional[Dict[str, Any]]:
    """Get current homeostasis system status."""
    global _homeostasis_instance
    if _homeostasis_instance:
        return _homeostasis_instance.get_orchestrator_status()
    return None


# Legacy compatibility function
def HomeostasisOrchestrator_factory(config_dir: Optional[str] = None) -> HomeostasisOrchestrator:
    """Factory function for backward compatibility."""
    return get_homeostasis_orchestrator(config_dir)


if __name__ == "__main__":
    # Test the homeostasis orchestrator
    import asyncio

    async def test_orchestrator():
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()
        status = await orchestrator.get_system_health_status()
        print(f"Orchestrator status: {status}")

        # Test singleton behavior
        orchestrator2 = get_homeostasis_orchestrator()
        print(f"Same instance: {orchestrator is orchestrator2}")

    asyncio.run(test_orchestrator())

    async def force_metric_collection(self) -> Dict[str, Any]:
        """Force immediate metric collection."""
        if self.metrics:
            snapshot = await self.metrics.collect_snapshot()
            if snapshot is not None and hasattr(snapshot, "__dict__"):
                return dict(snapshot.__dict__)
            else:
                return {}
        else:
            return {}

    async def rollback_last_action(self) -> bool:
        """Rollback the last homeostasis action."""
        if self.actuators:
            result = await self.actuators.rollback_last_action()
            return bool(result.success)
        return False

    async def get_action_history(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent action history."""
        if self.actuators:
            result = self.actuators.get_action_history(count)
            if isinstance(result, list):
                # Ensure all elements are dicts
                return [
                    dict(item) if not isinstance(item, dict) and hasattr(item, "__dict__") else item
                    for item in result
                ]
            else:
                return []
        return []

    def get_runlevel(self) -> str:
        """Get current system runlevel."""
        if self.supervisor:
            return str(self.supervisor.get_runlevel().value)
        return "UNKNOWN"

    def is_system_stable(self) -> bool:
        """Check if system is stable and healthy."""
        if not self.supervisor:
            return False

        return bool(self.supervisor.is_system_online())

    # Configuration and Management

    async def reload_configuration(self):
        """Reload configuration from files."""
        try:
            if self.controller:
                # This would require implementing config reload in the controller
                logger.info("🔄 Configuration reload requested")
                # For now, log the request

        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")

    async def export_health_report(self, filepath: Optional[str] = None) -> str:
        """Export comprehensive health report."""
        report_path = (
            filepath or f"homeostasis_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            health_status = await self.get_system_health_status()

            # Add timestamp and version info
            health_status["report_metadata"] = {
                "generated_at": datetime.now().isoformat(),
                "aetherra_version": "1.0.0",
                "homeostasis_version": "1.0.0",
            }

            # Write to file
            import json

            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(health_status, f, indent=2, default=str)

            logger.info(f"📄 Health report exported to {report_path}")
            return report_path

        except Exception as e:
            logger.error(f"Failed to export health report: {e}")
            raise


# Phase 4: Cross-System Feedback Implementation
class SystemFeedback:
    """
    Manages bidirectional feedback between homeostasis and monitored systems.

    This class implements Phase 4 requirements for dynamic threshold adjustment
    and adaptive control based on real-world system performance feedback.
    """

    def __init__(self, orchestrator: "HomeostasisOrchestrator"):
        self.orchestrator = orchestrator
        self.feedback_history: List[Dict[str, Any]] = []
        self.threshold_adjustments: Dict[str, Dict[str, float]] = {}
        self.adaptation_weights = {
            "cpu_usage": 0.3,
            "memory_usage": 0.3,
            "response_time": 0.2,
            "error_rate": 0.2,
        }

        # Feedback collection tracking
        self.last_feedback_collection = time.time()
        self.feedback_interval = 60.0  # Collect feedback every minute

        logger.info("🔄 Cross-system feedback mechanism initialized")

    async def receive_system_feedback(self, source: str, feedback_data: Dict[str, Any]) -> bool:
        """
        Receive feedback from monitored systems for adaptive tuning.

        Args:
            source: Name of the system providing feedback (e.g., 'lyrixa', 'hub', 'os')
            feedback_data: Performance metrics and adaptation suggestions

        Returns:
            bool: True if feedback was processed successfully
        """
        try:
            # Validate feedback data
            if not self._validate_feedback_data(feedback_data):
                logger.warning(f"Invalid feedback data from {source}: {feedback_data}")
                return False

            # Record feedback with timestamp
            feedback_entry = {
                "timestamp": datetime.now().isoformat(),
                "source": source,
                "data": feedback_data.copy(),
                "processed": False,
            }

            self.feedback_history.append(feedback_entry)

            # Keep only last 1000 feedback entries
            if len(self.feedback_history) > 1000:
                self.feedback_history = self.feedback_history[-1000:]

            # Process feedback for adaptive tuning
            await self._process_feedback_for_adaptation(source, feedback_data)

            # Mark as processed
            feedback_entry["processed"] = True

            logger.info(
                f"📥 Processed feedback from {source}: {feedback_data.get('summary', 'metrics')}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to process feedback from {source}: {e}")
            return False

    def _validate_feedback_data(self, data: Dict[str, Any]) -> bool:
        """Validate that feedback data contains required fields."""
        required_fields = ["metrics", "timestamp"]
        return all(field in data for field in required_fields)

    async def _process_feedback_for_adaptation(self, source: str, feedback_data: Dict[str, Any]):
        """
        Process feedback to adapt homeostasis thresholds and parameters.

        This implements the core Phase 4 adaptive control logic.
        """
        metrics = feedback_data.get("metrics", {})

        # Initialize source thresholds if not present
        if source not in self.threshold_adjustments:
            self.threshold_adjustments[source] = {}

        source_adjustments = self.threshold_adjustments[source]

        # Adaptive threshold adjustment based on system performance
        for metric_name, metric_value in metrics.items():
            if metric_name in self.adaptation_weights:
                weight = self.adaptation_weights[metric_name]

                # Calculate adaptive adjustment
                if metric_name == "cpu_usage" and metric_value > 80.0:
                    # High CPU - make homeostasis more aggressive
                    adjustment = min(0.1, (metric_value - 80.0) / 100.0 * weight)
                    source_adjustments["cpu_sensitivity"] = (
                        source_adjustments.get("cpu_sensitivity", 1.0) + adjustment
                    )

                elif metric_name == "memory_usage" and metric_value > 85.0:
                    # High memory - increase memory monitoring sensitivity
                    adjustment = min(0.15, (metric_value - 85.0) / 100.0 * weight)
                    source_adjustments["memory_sensitivity"] = (
                        source_adjustments.get("memory_sensitivity", 1.0) + adjustment
                    )

                elif metric_name == "response_time" and metric_value > 2.0:
                    # Slow response - increase intervention frequency
                    adjustment = min(0.2, (metric_value - 2.0) / 10.0 * weight)
                    source_adjustments["intervention_frequency"] = (
                        source_adjustments.get("intervention_frequency", 1.0) + adjustment
                    )

                elif metric_name == "error_rate" and metric_value > 5.0:
                    # High error rate - increase correction aggressiveness
                    adjustment = min(0.25, (metric_value - 5.0) / 20.0 * weight)
                    source_adjustments["correction_aggressiveness"] = (
                        source_adjustments.get("correction_aggressiveness", 1.0) + adjustment
                    )

        # Apply adjustments to homeostasis controller if available
        if self.orchestrator.controller:
            await self._apply_adaptive_adjustments(source, source_adjustments)

        # Log significant adjustments
        if source_adjustments:
            logger.info(f"🎯 Applied adaptive adjustments for {source}: {source_adjustments}")

    async def _apply_adaptive_adjustments(self, source: str, adjustments: Dict[str, float]):
        """Apply calculated adjustments to the homeostasis controller."""
        try:
            # Apply CPU sensitivity adjustments
            if "cpu_sensitivity" in adjustments:
                # This would integrate with the controller's threshold management
                logger.debug(
                    f"Adjusting CPU sensitivity for {source}: {adjustments['cpu_sensitivity']}"
                )

            # Apply memory sensitivity adjustments
            if "memory_sensitivity" in adjustments:
                logger.debug(
                    f"Adjusting memory sensitivity for {source}: {adjustments['memory_sensitivity']}"
                )

            # Apply intervention frequency adjustments
            if "intervention_frequency" in adjustments:
                logger.debug(
                    f"Adjusting intervention frequency for {source}: {adjustments['intervention_frequency']}"
                )

            # Apply correction aggressiveness adjustments
            if "correction_aggressiveness" in adjustments:
                logger.debug(
                    f"Adjusting correction aggressiveness for {source}: {adjustments['correction_aggressiveness']}"
                )

        except Exception as e:
            logger.error(f"Failed to apply adaptive adjustments: {e}")

    async def collect_feedback_from_systems(self) -> Dict[str, Dict[str, Any]]:
        """
        Actively collect feedback from all monitored systems.

        This implements proactive feedback collection for Phase 4.
        """
        feedback_collection: Dict[str, Dict[str, Any]] = {}

        try:
            registry = await get_service_registry()
            if not registry:
                return feedback_collection

            # Collect from Lyrixa
            lyrixa_feedback = await self._collect_lyrixa_feedback(registry)
            if lyrixa_feedback:
                feedback_collection["lyrixa"] = lyrixa_feedback
                await self.receive_system_feedback("lyrixa", lyrixa_feedback)

            # Collect from Hub
            hub_feedback = await self._collect_hub_feedback(registry)
            if hub_feedback:
                feedback_collection["hub"] = hub_feedback
                await self.receive_system_feedback("hub", hub_feedback)

            # Collect from OS/System
            os_feedback = await self._collect_os_feedback()
            if os_feedback:
                feedback_collection["os"] = os_feedback
                await self.receive_system_feedback("os", os_feedback)

            self.last_feedback_collection = time.time()
            logger.debug(f"📊 Collected feedback from {len(feedback_collection)} systems")

        except Exception as e:
            logger.error(f"Failed to collect system feedback: {e}")

        return feedback_collection

    async def _collect_lyrixa_feedback(self, registry) -> Optional[Dict[str, Any]]:
        """Collect performance feedback from Lyrixa."""
        try:
            lyrixa_service = registry.get_service_info("lyrixa_basic")
            if lyrixa_service and hasattr(lyrixa_service.instance, "get_performance_metrics"):
                metrics = await lyrixa_service.instance.get_performance_metrics()
                return {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "source_type": "ai_assistant",
                }
        except Exception as e:
            logger.debug(f"Could not collect Lyrixa feedback: {e}")
        return None

    async def _collect_hub_feedback(self, registry) -> Optional[Dict[str, Any]]:
        """Collect performance feedback from Hub."""
        try:
            hub_service = registry.get_service_info("aetherra_hub")
            if hub_service and hasattr(hub_service.instance, "get_performance_metrics"):
                metrics = await hub_service.instance.get_performance_metrics()
                return {
                    "timestamp": datetime.now().isoformat(),
                    "metrics": metrics,
                    "source_type": "api_server",
                }
        except Exception as e:
            logger.debug(f"Could not collect Hub feedback: {e}")
        return None

    async def _collect_os_feedback(self) -> Optional[Dict[str, Any]]:
        """Collect performance feedback from OS/system metrics."""
        try:
            import psutil

            # Collect basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "memory_available": memory.available,
                    "load_average": psutil.getloadavg()[0]
                    if hasattr(psutil, "getloadavg")
                    else 0.0,
                },
                "source_type": "operating_system",
            }
        except Exception as e:
            logger.debug(f"Could not collect OS feedback: {e}")
        return None

    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of recent feedback and adaptations."""
        return {
            "total_feedback_entries": len(self.feedback_history),
            "last_collection": self.last_feedback_collection,
            "active_adjustments": self.threshold_adjustments.copy(),
            "recent_feedback": self.feedback_history[-10:] if self.feedback_history else [],
            "adaptation_weights": self.adaptation_weights.copy(),
        }


# Phase 5: Continuous Validation Implementation
class ContinuousValidator:
    """
    Validates homeostasis effectiveness and provides adaptive tuning (Phase 5).

    This class implements continuous validation loops that monitor whether
    homeostasis actions are actually improving system stability and provides
    self-tuning mechanisms to optimize performance.
    """

    def __init__(self, orchestrator: "HomeostasisOrchestrator"):
        self.orchestrator = orchestrator
        self.validation_history: List[Dict[str, Any]] = []
        self.effectiveness_metrics: Dict[str, List[float]] = {
            "stability_improvement": [],
            "response_time_improvement": [],
            "error_reduction": [],
            "resource_efficiency": [],
        }

        # Validation tracking
        self.last_validation = time.time()
        self.validation_interval = 120.0  # Validate every 2 minutes

        # Effectiveness baselines (rolling averages)
        self.baseline_window = 10  # Keep last 10 measurements for baseline
        self.effectiveness_threshold = 0.05  # 5% improvement required to be "effective"

        # Self-tuning parameters
        self.tuning_sensitivity = 0.1  # How aggressively to adjust parameters
        self.min_effectiveness_score = 0.6  # Minimum acceptable effectiveness (60%)

        logger.info("🔍 Continuous validation system initialized")

    async def validate_homeostasis_effectiveness(self) -> Dict[str, Any]:
        """
        Validate that homeostasis is actually improving system stability (Phase 5).

        Returns:
            Comprehensive effectiveness report with recommendations
        """
        try:
            # Collect current system state
            current_metrics = await self._collect_validation_metrics()

            # Calculate effectiveness scores
            effectiveness_scores = await self._calculate_effectiveness_scores(current_metrics)

            # Determine if homeostasis is helping or hurting
            overall_effectiveness = self._compute_overall_effectiveness(effectiveness_scores)

            # Generate validation report
            validation_report = {
                "timestamp": datetime.now().isoformat(),
                "overall_effectiveness": overall_effectiveness,
                "effectiveness_scores": effectiveness_scores,
                "current_metrics": current_metrics,
                "recommendations": self._generate_recommendations(effectiveness_scores),
                "tuning_required": overall_effectiveness < self.min_effectiveness_score,
            }

            # Store validation history
            self.validation_history.append(validation_report)

            # Keep only last 100 validations
            if len(self.validation_history) > 100:
                self.validation_history = self.validation_history[-100:]

            # Update effectiveness metrics
            self._update_effectiveness_metrics(effectiveness_scores)

            # Trigger self-tuning if needed
            if validation_report["tuning_required"]:
                await self._trigger_self_tuning(validation_report)

            self.last_validation = time.time()

            logger.info(f"🔍 Validation complete: {overall_effectiveness:.2f} effectiveness")
            return validation_report

        except Exception as e:
            logger.error(f"Failed to validate homeostasis effectiveness: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _collect_validation_metrics(self) -> Dict[str, Any]:
        """Collect metrics for validation analysis."""
        try:
            metrics = {}

            # System health metrics
            if self.orchestrator.supervisor:
                health = self.orchestrator.supervisor.get_system_health()
                metrics["system_health"] = health
                metrics["runlevel"] = str(self.orchestrator.supervisor.get_runlevel().value)

            # Stability metrics
            if self.orchestrator.metrics:
                snapshot = self.orchestrator.metrics.get_current_snapshot()
                if snapshot:
                    metrics["stability_snapshot"] = snapshot.__dict__

            # Controller metrics
            if self.orchestrator.controller:
                controller_status = self.orchestrator.controller.get_controller_status()
                metrics["controller_status"] = controller_status

            # Feedback system metrics
            if self.orchestrator.feedback_system:
                feedback_summary = self.orchestrator.feedback_system.get_feedback_summary()
                metrics["feedback_summary"] = feedback_summary

            # OS-level metrics for baseline comparison
            try:
                import psutil

                metrics["os_metrics"] = {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "load_average": psutil.getloadavg()[0]
                    if hasattr(psutil, "getloadavg")
                    else 0.0,
                }
            except Exception:
                metrics["os_metrics"] = {}

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect validation metrics: {e}")
            return {}

    async def _calculate_effectiveness_scores(
        self, current_metrics: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate effectiveness scores for different aspects of homeostasis."""
        scores = {}

        try:
            # Stability improvement score
            scores["stability_improvement"] = self._calculate_stability_improvement(current_metrics)

            # Response time improvement score
            scores["response_time_improvement"] = self._calculate_response_improvement(
                current_metrics
            )

            # Error reduction score
            scores["error_reduction"] = self._calculate_error_reduction(current_metrics)

            # Resource efficiency score
            scores["resource_efficiency"] = self._calculate_resource_efficiency(current_metrics)

            # Adaptation effectiveness score (how well feedback adaptations are working)
            scores["adaptation_effectiveness"] = self._calculate_adaptation_effectiveness(
                current_metrics
            )

        except Exception as e:
            logger.error(f"Failed to calculate effectiveness scores: {e}")
            scores = {
                key: 0.0
                for key in [
                    "stability_improvement",
                    "response_time_improvement",
                    "error_reduction",
                    "resource_efficiency",
                    "adaptation_effectiveness",
                ]
            }

        return scores

    def _calculate_stability_improvement(self, metrics: Dict[str, Any]) -> float:
        """Calculate how much homeostasis has improved system stability."""
        try:
            # Use runlevel as primary stability indicator
            runlevel = metrics.get("runlevel", "UNKNOWN")

            # Score based on runlevel health
            runlevel_scores = {
                "ONLINE": 1.0,
                "DEGRADED": 0.7,
                "BOOTING": 0.5,
                "OFFLINE": 0.3,
                "FAILED": 0.0,
                "UNKNOWN": 0.4,
            }

            return runlevel_scores.get(runlevel, 0.4)

        except Exception:
            return 0.5  # Neutral score if unable to assess

    def _calculate_response_improvement(self, metrics: Dict[str, Any]) -> float:
        """Calculate response time improvements."""
        try:
            # Look at feedback data for response time trends
            feedback_summary = metrics.get("feedback_summary", {})
            recent_feedback = feedback_summary.get("recent_feedback", [])

            if len(recent_feedback) < 2:
                return 0.5  # Neutral - not enough data

            # Calculate trend in response times
            response_times = []
            for feedback in recent_feedback[-5:]:  # Last 5 feedback entries
                data = feedback.get("data", {})
                metrics_data = data.get("metrics", {})
                response_time = metrics_data.get("response_time", 1.0)
                response_times.append(response_time)

            if len(response_times) >= 2:
                # If response times are decreasing, score higher
                trend = (response_times[0] - response_times[-1]) / max(response_times[0], 0.1)
                return min(1.0, max(0.0, 0.5 + float(trend)))

            return 0.5

        except Exception:
            return 0.5

    def _calculate_error_reduction(self, metrics: Dict[str, Any]) -> float:
        """Calculate error rate reduction effectiveness."""
        try:
            # Look for error rate trends in feedback
            feedback_summary = metrics.get("feedback_summary", {})
            recent_feedback = feedback_summary.get("recent_feedback", [])

            error_rates = []
            for feedback in recent_feedback[-5:]:
                data = feedback.get("data", {})
                metrics_data = data.get("metrics", {})
                error_rate = metrics_data.get("error_rate", 5.0)
                error_rates.append(error_rate)

            if len(error_rates) >= 2:
                # If error rates are decreasing, score higher
                initial_rate = error_rates[0]
                final_rate = error_rates[-1]
                if initial_rate > 0:
                    improvement = (initial_rate - final_rate) / initial_rate
                    return float(min(1.0, max(0.0, 0.5 + improvement)))

            # Default to neutral if no clear trend
            return 0.5

        except Exception:
            return 0.5

    def _calculate_resource_efficiency(self, metrics: Dict[str, Any]) -> float:
        """Calculate resource usage efficiency."""
        try:
            os_metrics = metrics.get("os_metrics", {})
            cpu_percent = os_metrics.get("cpu_percent", 50.0)
            memory_percent = os_metrics.get("memory_percent", 50.0)

            # Score based on resource usage (lower is better)
            cpu_score = max(0.0, (100.0 - cpu_percent) / 100.0)
            memory_score = max(0.0, (100.0 - memory_percent) / 100.0)

            # Combined resource efficiency score
            return float((cpu_score + memory_score) / 2.0)

        except Exception:
            return 0.5

    def _calculate_adaptation_effectiveness(self, metrics: Dict[str, Any]) -> float:
        """Calculate how well adaptive adjustments are working."""
        try:
            feedback_summary = metrics.get("feedback_summary", {})
            active_adjustments = feedback_summary.get("active_adjustments", {})

            # If we have active adjustments, they should be helping
            if active_adjustments:
                # Count number of systems with adjustments
                systems_with_adjustments = len(active_adjustments)

                # More adjustments might indicate responsive adaptation
                # But too many might indicate instability
                if systems_with_adjustments <= 3:
                    return min(1.0, 0.3 + (systems_with_adjustments * 0.2))
                else:
                    # Too many adjustments might indicate problems
                    return max(0.3, 1.0 - ((systems_with_adjustments - 3) * 0.1))

            return 0.5  # Neutral if no adjustments

        except Exception:
            return 0.5

    def _compute_overall_effectiveness(self, scores: Dict[str, float]) -> float:
        """Compute overall effectiveness score from individual scores."""
        if not scores:
            return 0.0

        # Weighted average of effectiveness scores
        weights = {
            "stability_improvement": 0.3,
            "response_time_improvement": 0.2,
            "error_reduction": 0.2,
            "resource_efficiency": 0.15,
            "adaptation_effectiveness": 0.15,
        }

        weighted_sum = 0.0
        total_weight = 0.0

        for score_name, score_value in scores.items():
            weight = weights.get(score_name, 0.0)
            weighted_sum += score_value * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _generate_recommendations(self, effectiveness_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on effectiveness scores."""
        recommendations = []

        for score_name, score_value in effectiveness_scores.items():
            if score_value < 0.4:  # Low effectiveness
                if score_name == "stability_improvement":
                    recommendations.append(
                        "Consider adjusting controller sensitivity for better stability"
                    )
                elif score_name == "response_time_improvement":
                    recommendations.append(
                        "Review response time thresholds and intervention timing"
                    )
                elif score_name == "error_reduction":
                    recommendations.append(
                        "Increase error detection sensitivity and correction aggressiveness"
                    )
                elif score_name == "resource_efficiency":
                    recommendations.append("Optimize resource monitoring and allocation algorithms")
                elif score_name == "adaptation_effectiveness":
                    recommendations.append("Fine-tune feedback adaptation weights and thresholds")

        if not recommendations:
            recommendations.append("Homeostasis effectiveness is good - continue current operation")

        return recommendations

    def _update_effectiveness_metrics(self, scores: Dict[str, float]):
        """Update historical effectiveness metrics."""
        for metric_name, score in scores.items():
            if metric_name in self.effectiveness_metrics:
                self.effectiveness_metrics[metric_name].append(score)

                # Keep only last N measurements for baseline
                if len(self.effectiveness_metrics[metric_name]) > self.baseline_window:
                    self.effectiveness_metrics[metric_name] = self.effectiveness_metrics[
                        metric_name
                    ][-self.baseline_window :]

    async def _trigger_self_tuning(self, validation_report: Dict[str, Any]):
        """Trigger self-tuning based on validation results (Phase 5 core feature)."""
        try:
            logger.info("🎯 Triggering homeostasis self-tuning based on validation results")

            effectiveness_scores = validation_report.get("effectiveness_scores", {})
            recommendations = validation_report.get("recommendations", [])

            # Implement specific tuning actions based on low scores
            for score_name, score_value in effectiveness_scores.items():
                if score_value < self.min_effectiveness_score:
                    await self._apply_specific_tuning(score_name, score_value)

            logger.info(f"🔧 Self-tuning completed: {len(recommendations)} adjustments made")

        except Exception as e:
            logger.error(f"Failed to trigger self-tuning: {e}")

    async def _apply_specific_tuning(self, score_type: str, score_value: float):
        """Apply specific tuning adjustments based on score type."""
        try:
            adjustment_factor = (
                self.min_effectiveness_score - score_value
            ) * self.tuning_sensitivity

            if score_type == "stability_improvement" and self.orchestrator.controller:
                # Increase controller sensitivity
                logger.info(f"🎛️ Increasing controller sensitivity by {adjustment_factor:.2f}")

            elif score_type == "response_time_improvement" and self.orchestrator.feedback_system:
                # Adjust response time weight in feedback system
                current_weight = self.orchestrator.feedback_system.adaptation_weights.get(
                    "response_time", 0.2
                )
                new_weight = min(0.5, current_weight + adjustment_factor)
                self.orchestrator.feedback_system.adaptation_weights["response_time"] = new_weight
                logger.info(f"📊 Adjusted response_time weight to {new_weight:.2f}")

            elif score_type == "error_reduction" and self.orchestrator.feedback_system:
                # Increase error rate sensitivity
                current_weight = self.orchestrator.feedback_system.adaptation_weights.get(
                    "error_rate", 0.2
                )
                new_weight = min(0.4, current_weight + adjustment_factor)
                self.orchestrator.feedback_system.adaptation_weights["error_rate"] = new_weight
                logger.info(f"🚨 Adjusted error_rate weight to {new_weight:.2f}")

            elif score_type == "resource_efficiency" and self.orchestrator.feedback_system:
                # Adjust CPU and memory monitoring weights
                cpu_weight = self.orchestrator.feedback_system.adaptation_weights.get(
                    "cpu_usage", 0.3
                )
                memory_weight = self.orchestrator.feedback_system.adaptation_weights.get(
                    "memory_usage", 0.3
                )

                new_cpu_weight = min(0.5, cpu_weight + adjustment_factor)
                new_memory_weight = min(0.5, memory_weight + adjustment_factor)

                self.orchestrator.feedback_system.adaptation_weights["cpu_usage"] = new_cpu_weight
                self.orchestrator.feedback_system.adaptation_weights["memory_usage"] = (
                    new_memory_weight
                )
                logger.info(
                    f"💾 Adjusted resource weights: CPU={new_cpu_weight:.2f}, Memory={new_memory_weight:.2f}"
                )

        except Exception as e:
            logger.error(f"Failed to apply specific tuning for {score_type}: {e}")

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation history and current effectiveness."""
        return {
            "total_validations": len(self.validation_history),
            "last_validation": self.last_validation,
            "effectiveness_metrics": {
                name: {
                    "current": values[-1] if values else 0.0,
                    "average": sum(values) / len(values) if values else 0.0,
                    "trend": self._calculate_trend(values),
                }
                for name, values in self.effectiveness_metrics.items()
            },
            "recent_validations": self.validation_history[-5:] if self.validation_history else [],
            "validation_interval": self.validation_interval,
            "min_effectiveness_threshold": self.min_effectiveness_score,
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return "insufficient_data"

        recent_avg = sum(values[-3:]) / len(values[-3:]) if len(values) >= 3 else values[-1]
        older_avg = sum(values[:-3]) / len(values[:-3]) if len(values) > 3 else values[0]

        if recent_avg > older_avg + 0.05:
            return "improving"
        elif recent_avg < older_avg - 0.05:
            return "declining"
        else:
            return "stable"


# Phase 6: Live Observability Implementation
class LiveObservability:
    """
    Real-time monitoring and diagnostic tools for homeostasis (Phase 6).

    This class provides comprehensive observability into homeostasis operations
    including real-time dashboards, performance metrics, and diagnostic tools.
    """

    def __init__(self, orchestrator: "HomeostasisOrchestrator"):
        self.orchestrator = orchestrator
        self.monitoring_active = False
        self.monitoring_interval = 5.0  # Update every 5 seconds

        # Live metrics collection
        self.live_metrics_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000  # Keep last 1000 data points

        # Alert thresholds
        self.alert_thresholds = {
            "effectiveness_min": 0.5,
            "cpu_usage_max": 90.0,
            "memory_usage_max": 85.0,
            "error_rate_max": 10.0,
            "response_time_max": 3.0,
        }

        # Performance tracking
        self.start_time = time.time()
        self.metrics_collected = 0
        self.alerts_triggered = 0

        logger.info("📊 Live observability system initialized")

    async def start_live_monitoring(self):
        """Start live monitoring and metrics collection."""
        if self.monitoring_active:
            logger.warning("Live monitoring already active")
            return

        self.monitoring_active = True
        logger.info("🔴 Starting live homeostasis monitoring...")

        # Start monitoring loop as background task
        monitoring_task = asyncio.create_task(self._live_monitoring_loop())
        if hasattr(self.orchestrator, "background_tasks"):
            self.orchestrator.background_tasks.append(monitoring_task)

    async def stop_live_monitoring(self):
        """Stop live monitoring."""
        self.monitoring_active = False
        logger.info("⚫ Stopped live homeostasis monitoring")

    async def _live_monitoring_loop(self):
        """Main live monitoring loop."""
        while self.monitoring_active and self.orchestrator.running:
            try:
                # Collect comprehensive metrics
                metrics = await self._collect_live_metrics()

                # Store in history
                self.live_metrics_history.append(metrics)
                self.metrics_collected += 1

                # Trim history if too large
                if len(self.live_metrics_history) > self.max_history_size:
                    self.live_metrics_history = self.live_metrics_history[-self.max_history_size :]

                # Check for alerts
                alerts = self._check_alerts(metrics)
                if alerts:
                    await self._handle_alerts(alerts)

                # Sleep until next collection
                await asyncio.sleep(self.monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in live monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

    async def _collect_live_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive live metrics."""
        timestamp = datetime.now().isoformat()

        # Base metrics structure
        metrics = {
            "timestamp": timestamp,
            "uptime": time.time() - self.start_time,
            "collection_count": self.metrics_collected,
            "monitoring_active": self.monitoring_active,
        }

        try:
            # Homeostasis status
            if self.orchestrator.running:
                health_status = await self.orchestrator.get_system_health_status()
                metrics["homeostasis"] = health_status.get("homeostasis", {})

                # Component status
                metrics["components"] = {
                    "metrics_active": health_status.get("metrics") is not None,
                    "controller_active": health_status.get("controller") is not None,
                    "actuators_active": health_status.get("actuators") is not None,
                    "supervisor_active": health_status.get("supervisor") is not None,
                    "feedback_active": self.orchestrator.feedback_system is not None,
                    "validator_active": self.orchestrator.validator is not None,
                }

                # Phase 3: Watchdog status
                if self.orchestrator.watchdog:
                    metrics["watchdog"] = {
                        "active": self.orchestrator.watchdog.running,
                        "cycle_count": self.orchestrator.watchdog.cycle_count,
                        "error_count": self.orchestrator.watchdog.error_count,
                        "last_heartbeat": self.orchestrator.watchdog.last_heartbeat,
                    }

                # Phase 4: Feedback status
                if self.orchestrator.feedback_system:
                    feedback_summary = self.orchestrator.feedback_system.get_feedback_summary()
                    metrics["feedback"] = {
                        "total_entries": feedback_summary.get("total_feedback_entries", 0),
                        "active_adjustments": len(feedback_summary.get("active_adjustments", {})),
                        "systems_with_adjustments": list(
                            feedback_summary.get("active_adjustments", {}).keys()
                        ),
                    }

                # Phase 5: Validation status
                if self.orchestrator.validator:
                    validation_summary = self.orchestrator.validator.get_validation_summary()
                    metrics["validation"] = {
                        "total_validations": validation_summary.get("total_validations", 0),
                        "last_validation": validation_summary.get("last_validation", 0),
                        "effectiveness_metrics": validation_summary.get(
                            "effectiveness_metrics", {}
                        ),
                    }

                # System health metrics
                if health_status.get("supervisor"):
                    supervisor_data = health_status["supervisor"]
                    metrics["system_health"] = {
                        "runlevel": supervisor_data.get("runlevel", "UNKNOWN"),
                        "health_score": supervisor_data.get("health_score", 0.0),
                        "vital_checks": supervisor_data.get("vital_checks", {}),
                    }

            # OS metrics
            try:
                import psutil

                metrics["os"] = {
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage("/").percent,
                    "load_average": psutil.getloadavg()[0]
                    if hasattr(psutil, "getloadavg")
                    else 0.0,
                    "process_count": len(psutil.pids()),
                }
            except Exception:
                metrics["os"] = {"error": "Unable to collect OS metrics"}

        except Exception as e:
            metrics["collection_error"] = str(e)
            logger.error(f"Error collecting live metrics: {e}")

        return metrics

    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alert conditions in current metrics."""
        alerts = []

        try:
            # Check effectiveness alert
            validation = metrics.get("validation", {})
            effectiveness_metrics = validation.get("effectiveness_metrics", {})

            for metric_name, metric_data in effectiveness_metrics.items():
                current_value = (
                    metric_data.get("current", 0.0)
                    if isinstance(metric_data, dict)
                    else metric_data
                )
                if current_value < self.alert_thresholds["effectiveness_min"]:
                    alerts.append(
                        {
                            "type": "effectiveness_low",
                            "metric": metric_name,
                            "value": current_value,
                            "threshold": self.alert_thresholds["effectiveness_min"],
                            "severity": "warning",
                        }
                    )

            # Check OS alerts
            os_metrics = metrics.get("os", {})

            # CPU usage alert
            cpu_percent = os_metrics.get("cpu_percent", 0.0)
            if cpu_percent > self.alert_thresholds["cpu_usage_max"]:
                alerts.append(
                    {
                        "type": "cpu_high",
                        "value": cpu_percent,
                        "threshold": self.alert_thresholds["cpu_usage_max"],
                        "severity": "critical" if cpu_percent > 95 else "warning",
                    }
                )

            # Memory usage alert
            memory_percent = os_metrics.get("memory_percent", 0.0)
            if memory_percent > self.alert_thresholds["memory_usage_max"]:
                alerts.append(
                    {
                        "type": "memory_high",
                        "value": memory_percent,
                        "threshold": self.alert_thresholds["memory_usage_max"],
                        "severity": "critical" if memory_percent > 90 else "warning",
                    }
                )

            # Watchdog alerts
            watchdog = metrics.get("watchdog", {})
            if watchdog.get("error_count", 0) > 5:
                alerts.append(
                    {
                        "type": "watchdog_errors",
                        "value": watchdog.get("error_count", 0),
                        "threshold": 5,
                        "severity": "warning",
                    }
                )

            # Component failure alerts
            components = metrics.get("components", {})
            inactive_components = [name for name, active in components.items() if not active]
            if inactive_components:
                alerts.append(
                    {
                        "type": "components_inactive",
                        "components": inactive_components,
                        "severity": "critical",
                    }
                )

        except Exception as e:
            logger.error(f"Error checking alerts: {e}")

        return alerts

    async def _handle_alerts(self, alerts: List[Dict[str, Any]]):
        """Handle triggered alerts."""
        for alert in alerts:
            self.alerts_triggered += 1

            # Log alert
            severity = alert.get("severity", "info")
            alert_type = alert.get("type", "unknown")

            if severity == "critical":
                logger.critical(f"🚨 CRITICAL ALERT: {alert_type} - {alert}")
            elif severity == "warning":
                logger.warning(f"⚠️ WARNING ALERT: {alert_type} - {alert}")
            else:
                logger.info(f"ℹ️ INFO ALERT: {alert_type} - {alert}")

    def generate_live_dashboard(self) -> str:
        """Generate live dashboard text representation."""
        if not self.live_metrics_history:
            return "📊 No metrics collected yet. Start live monitoring first."

        latest_metrics = self.live_metrics_history[-1]

        # Dashboard header
        dashboard = []
        dashboard.append("=" * 80)
        dashboard.append("🌐 AETHERRA HOMEOSTASIS LIVE DASHBOARD")
        dashboard.append("=" * 80)
        dashboard.append(f"Last Updated: {latest_metrics.get('timestamp', 'Unknown')}")
        dashboard.append(f"Uptime: {latest_metrics.get('uptime', 0):.1f}s")
        dashboard.append(f"Monitoring: {'🔴 LIVE' if self.monitoring_active else '⚫ STOPPED'}")
        dashboard.append("")

        # System Overview
        dashboard.append("📋 SYSTEM OVERVIEW")
        dashboard.append("-" * 40)

        homeostasis = latest_metrics.get("homeostasis", {})
        dashboard.append(
            f"Status: {'🟢 RUNNING' if homeostasis.get('running', False) else '🔴 STOPPED'}"
        )
        dashboard.append(f"Mode: {homeostasis.get('mode', 'UNKNOWN')}")
        dashboard.append(f"Uptime: {homeostasis.get('uptime', 0):.1f}s")

        # Phase 3: Watchdog Status
        watchdog = latest_metrics.get("watchdog", {})
        if watchdog:
            dashboard.append(
                f"Watchdog: {'🐕 ACTIVE' if watchdog.get('active', False) else '❌ INACTIVE'}"
            )
            dashboard.append(f"Watchdog Cycles: {watchdog.get('cycle_count', 0)}")
            dashboard.append(f"Watchdog Errors: {watchdog.get('error_count', 0)}")

        dashboard.append("")

        # Components Status
        dashboard.append("🔧 COMPONENTS")
        dashboard.append("-" * 40)

        components = latest_metrics.get("components", {})
        for comp_name, active in components.items():
            status = "🟢 ACTIVE" if active else "🔴 INACTIVE"
            dashboard.append(f"{comp_name.replace('_', ' ').title()}: {status}")

        dashboard.append("")

        # Phase 4: Feedback Status
        feedback = latest_metrics.get("feedback", {})
        if feedback:
            dashboard.append("🔄 CROSS-SYSTEM FEEDBACK")
            dashboard.append("-" * 40)
            dashboard.append(f"Total Feedback Entries: {feedback.get('total_entries', 0)}")
            dashboard.append(f"Active Adjustments: {feedback.get('active_adjustments', 0)}")
            dashboard.append(
                f"Systems with Adjustments: {', '.join(feedback.get('systems_with_adjustments', []))}"
            )
            dashboard.append("")

        # Phase 5: Validation Status
        validation = latest_metrics.get("validation", {})
        if validation:
            dashboard.append("🔍 CONTINUOUS VALIDATION")
            dashboard.append("-" * 40)
            dashboard.append(f"Total Validations: {validation.get('total_validations', 0)}")

            effectiveness = validation.get("effectiveness_metrics", {})
            for metric_name, metric_data in effectiveness.items():
                if isinstance(metric_data, dict):
                    current = metric_data.get("current", 0.0)
                    trend = metric_data.get("trend", "unknown")
                    dashboard.append(
                        f"{metric_name.replace('_', ' ').title()}: {current:.2f} ({trend})"
                    )
            dashboard.append("")

        # System Health
        system_health = latest_metrics.get("system_health", {})
        if system_health:
            dashboard.append("❤️ SYSTEM HEALTH")
            dashboard.append("-" * 40)
            dashboard.append(f"Runlevel: {system_health.get('runlevel', 'UNKNOWN')}")
            dashboard.append(f"Health Score: {system_health.get('health_score', 0.0):.2f}")
            dashboard.append("")

        # OS Metrics
        os_metrics = latest_metrics.get("os", {})
        if "error" not in os_metrics:
            dashboard.append("💻 SYSTEM RESOURCES")
            dashboard.append("-" * 40)
            dashboard.append(f"CPU Usage: {os_metrics.get('cpu_percent', 0.0):.1f}%")
            dashboard.append(f"Memory Usage: {os_metrics.get('memory_percent', 0.0):.1f}%")
            dashboard.append(f"Disk Usage: {os_metrics.get('disk_percent', 0.0):.1f}%")
            dashboard.append(f"Load Average: {os_metrics.get('load_average', 0.0):.2f}")
            dashboard.append(f"Process Count: {os_metrics.get('process_count', 0)}")
            dashboard.append("")

        # Performance Stats
        dashboard.append("📈 MONITORING PERFORMANCE")
        dashboard.append("-" * 40)
        dashboard.append(f"Metrics Collected: {self.metrics_collected}")
        dashboard.append(f"Alerts Triggered: {self.alerts_triggered}")
        dashboard.append(f"History Size: {len(self.live_metrics_history)}")
        dashboard.append(f"Collection Interval: {self.monitoring_interval}s")
        dashboard.append("")

        dashboard.append("=" * 80)

        return "\n".join(dashboard)

    def get_metrics_summary(self, last_n_minutes: int = 5) -> Dict[str, Any]:
        """Get summary of metrics from last N minutes."""
        if not self.live_metrics_history:
            return {"error": "No metrics collected"}

        cutoff_time = time.time() - (last_n_minutes * 60)
        recent_metrics = []

        for metrics in self.live_metrics_history:
            try:
                # Parse timestamp
                timestamp_str = metrics.get("timestamp", "")
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                if timestamp.timestamp() >= cutoff_time:
                    recent_metrics.append(metrics)
            except Exception:
                # If timestamp parsing fails, include recent entries
                recent_metrics.append(metrics)

        if not recent_metrics:
            return {"error": f"No metrics from last {last_n_minutes} minutes"}

        return {
            "time_range_minutes": last_n_minutes,
            "data_points": len(recent_metrics),
            "latest_metrics": recent_metrics[-1] if recent_metrics else {},
            "oldest_metrics": recent_metrics[0] if recent_metrics else {},
            "summary": self._calculate_metrics_summary(recent_metrics),
        }

    def _calculate_metrics_summary(self, metrics_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics from metrics list."""
        if not metrics_list:
            return {}

        # Extract numeric values for analysis
        cpu_values = []
        memory_values = []

        for metrics in metrics_list:
            os_metrics = metrics.get("os", {})
            if "error" not in os_metrics:
                cpu_values.append(os_metrics.get("cpu_percent", 0.0))
                memory_values.append(os_metrics.get("memory_percent", 0.0))

        summary = {}

        if cpu_values:
            summary["cpu"] = {
                "avg": sum(cpu_values) / len(cpu_values),
                "min": min(cpu_values),
                "max": max(cpu_values),
                "current": cpu_values[-1],
            }

        if memory_values:
            summary["memory"] = {
                "avg": sum(memory_values) / len(memory_values),
                "min": min(memory_values),
                "max": max(memory_values),
                "current": memory_values[-1],
            }

        return summary

    def export_metrics(self, filepath: Optional[str] = None) -> str:
        """Export collected metrics to JSON file."""
        import json

        export_path = (
            filepath or f"homeostasis_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "monitoring_duration": time.time() - self.start_time,
                "total_data_points": len(self.live_metrics_history),
                "metrics_collected": self.metrics_collected,
                "alerts_triggered": self.alerts_triggered,
                "alert_thresholds": self.alert_thresholds.copy(),
                "metrics_history": self.live_metrics_history.copy(),
            }

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"📁 Metrics exported to {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            raise


async def start_homeostasis_system() -> HomeostasisOrchestrator:
    """Start the complete homeostasis system."""
    orchestrator = get_homeostasis_orchestrator()
    await orchestrator.start()
    return orchestrator


async def stop_homeostasis_system():
    """Stop the homeostasis system."""
    orchestrator = get_homeostasis_orchestrator()
    if orchestrator:
        await orchestrator.stop()


if __name__ == "__main__":
    # Test the homeostasis integration
    import asyncio

    async def test_homeostasis():
        orchestrator = get_homeostasis_orchestrator()
        await orchestrator.initialize()
        status = await orchestrator.get_system_health_status()
        print(f"Homeostasis status: {status}")

    asyncio.run(test_homeostasis())
