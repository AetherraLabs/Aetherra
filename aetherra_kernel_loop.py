#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
[CORE] Aetherra OS Kernel Loop
==========================
The core heartbeat and orchestration engine for the AI-native Operating System.

This is the living brain of Aetherra - continuously processing, learning, and evolving.
"""

import asyncio
import json
import logging
import os
import random
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Coroutine, Dict, List, Optional, cast

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AetherraKernelLoop:
    """
    [BRAIN] The Core AI OS Kernel Loop

    Orchestrates all system operations:
    - Memory processing and optimization
    - Plugin execution and coordination
    - Scheduled maintenance tasks
    - Real-time event handling
    - System health monitoring
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.running = False
        self.start_time = None
        self.cycle_count = 0
        self.last_night_cycle = None
        # Track a per-day key to ensure once-per-day behavior in selected TZ
        self._night_last_date_key = None
        self._night_cycle_scheduled = False

        # Core systems (will be injected by startup)
        self.memory_system = None
        self.plugin_manager = None
        self.aetherra_engine = None
        self.scheduler = None
        self.service_registry = None

        # Performance metrics
        self.metrics = {
            "total_cycles": 0,
            "avg_cycle_time": 0.0,
            "last_cycle_time": 0.0,
            "errors_count": 0,
            "night_cycles_count": 0,
            # Backpressure metrics (optional bounded queues)
            "drops_high": 0,
            "drops_normal": 0,
            "drops_background": 0,
        }

        # Task queues
        self.high_priority_queue = asyncio.Queue()
        self.normal_priority_queue = asyncio.Queue()
        self.background_queue = asyncio.Queue()

        # Optional bounded queue sizes (0 = unbounded)
        self.queue_limits = {
            "high_priority": int(os.getenv("AETHERRA_KERNEL_QSIZE_HIGH", "0") or 0),
            "normal_priority": int(os.getenv("AETHERRA_KERNEL_QSIZE_NORMAL", "0") or 0),
            "background": int(os.getenv("AETHERRA_KERNEL_QSIZE_BACKGROUND", "0") or 0),
        }

        # Optional task persistence (best-effort snapshotting)
        self.persist_tasks = os.getenv("AETHERRA_KERNEL_PERSIST_TASKS", "0") == "1"
        default_tasks_path = os.path.join(
            os.getenv("AETHERRA_STATE_DIR", ".aetherra"), "kernel_tasks.json"
        )
        self.tasks_path = Path(
            os.getenv("AETHERRA_KERNEL_TASKS_PATH", default_tasks_path)
        )
        self._pending_tasks: Dict[str, List[Dict[str, Any]]] = {
            "high_priority": [],
            "normal_priority": [],
            "background": [],
        }

        # Night cycle window (configurable via env)
        try:
            self.night_start_hour = int(os.getenv("AETHERRA_NIGHT_START_HOUR", "2"))
            self.night_end_hour = int(os.getenv("AETHERRA_NIGHT_END_HOUR", "4"))
        except Exception:
            self.night_start_hour, self.night_end_hour = 2, 4

        # Night cycle timezone control
        # - AETHERRA_NIGHT_TZ: IANA name (e.g., "UTC", "America/Los_Angeles")
        # - AETHERRA_NIGHT_UTC=1 pins scheduling to UTC (equivalent to AETHERRA_NIGHT_TZ=UTC)
        # - AETHERRA_NIGHT_STAGGER_MAX_SEC: int seconds of max jitter to stagger start within window
        self.night_tz_name = (os.getenv("AETHERRA_NIGHT_TZ", "") or "").strip()
        self.night_utc = os.getenv("AETHERRA_NIGHT_UTC", "0") == "1"
        try:
            self.night_stagger_max_sec = int(
                os.getenv("AETHERRA_NIGHT_STAGGER_MAX_SEC", "0") or 0
            )
        except Exception:
            self.night_stagger_max_sec = 0
        # Fixed jitter per process to preserve staggering consistency
        self._night_stagger_sec = (
            random.randint(0, max(0, int(self.night_stagger_max_sec)))
            if self.night_stagger_max_sec > 0
            else 0
        )

        # Task TTL (deadline) and plugin timeouts
        try:
            self.default_task_ttl_sec = int(
                os.getenv("AETHERRA_KERNEL_TASK_DEFAULT_TTL_SEC", "0") or 0
            )
        except Exception:
            self.default_task_ttl_sec = 0

        try:
            self.plugin_invoke_timeout_sec = float(
                os.getenv("AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC", "30") or 30
            )
        except Exception:
            self.plugin_invoke_timeout_sec = 30.0

        # Simple circuit breaker for plugin invocations
        try:
            self.plugin_cb_threshold = int(
                os.getenv("AETHERRA_PLUGIN_CB_THRESHOLD", "5") or 5
            )
        except Exception:
            self.plugin_cb_threshold = 5
        try:
            self.plugin_cb_cooldown_sec = int(
                os.getenv("AETHERRA_PLUGIN_CB_COOLDOWN_SEC", "60") or 60
            )
        except Exception:
            self.plugin_cb_cooldown_sec = 60
        self._plugin_cb_failures = 0
        self._plugin_cb_open_until = 0.0

        # Optional metrics flush interval (seconds) for live observability
        try:
            self.metrics_flush_sec = int(
                os.getenv("AETHERRA_KERNEL_METRICS_FLUSH_SEC", "0") or 0
            )
        except Exception:
            self.metrics_flush_sec = 0
        self._last_metrics_flush = 0.0

        # Dead Letter Queue (DLQ) for dropped/expired tasks
        try:
            self.dlq_enabled = os.getenv("AETHERRA_KERNEL_DLQ", "1") == "1"
            default_dlq_path = os.path.join(
                os.getenv("AETHERRA_STATE_DIR", ".aetherra"), "kernel_dlq.jsonl"
            )
            self.dlq_path = Path(
                os.getenv("AETHERRA_KERNEL_DLQ_PATH", default_dlq_path)
            )
            self.dlq_max = int(os.getenv("AETHERRA_KERNEL_DLQ_MAX", "10000") or 10000)
        except Exception:
            self.dlq_enabled = True
            self.dlq_path = Path(".aetherra/kernel_dlq.jsonl")
            self.dlq_max = 10000
        self._dlq_count = 0

        # Per-plugin concurrency cap (0 = unlimited)
        try:
            self.plugin_max_concurrency = int(
                os.getenv("AETHERRA_PLUGIN_MAX_CONCURRENCY", "0") or 0
            )
        except Exception:
            self.plugin_max_concurrency = 0
        self._plugin_running_counts: Dict[str, int] = {}

        # Retry policy for transient failures (timeouts/errors)
        try:
            self.retry_max = int(os.getenv("AETHERRA_KERNEL_RETRY_MAX", "0") or 0)
        except Exception:
            self.retry_max = 0
        try:
            self.retry_base_delay_ms = int(
                os.getenv("AETHERRA_KERNEL_RETRY_BASE_DELAY_MS", "200") or 200
            )
        except Exception:
            self.retry_base_delay_ms = 200
        # Control-plane: pause flag
        self.paused = False

        # Priority aging settings (seconds). 0 = disabled
        try:
            self.priority_aging_sec = int(
                os.getenv("AETHERRA_KERNEL_AGING_SEC", "0") or 0
            )
        except Exception:
            self.priority_aging_sec = 0

        # HMR integration (metrics and control)
        self._hmr_metrics = {
            "attempts": 0,
            "success": 0,
            "rollback": 0,
            "last_swap_ms": 0,
            "per_target": {},
        }
        self._quiesced_targets: set[str] = set()
        self.hmr_controller = None  # set by launcher when HMR is enabled
        # In-flight counters per target to support safer quiesce/drain
        self._inflight_by_target: Dict[str, int] = {}

        # Optional visible heartbeat logging (for idle visibility)
        try:
            self.visible_heartbeat_sec = int(
                os.getenv("AETHERRA_KERNEL_HEARTBEAT_SEC", "0") or 0
            )
        except Exception:
            self.visible_heartbeat_sec = 0
        self.visible_heartbeat_level = os.getenv(
            "AETHERRA_KERNEL_HEARTBEAT_LEVEL", "INFO"
        ).upper()

        # --- Production defaults & safety rails ---
        # Apply conservative defaults in production profile when not explicitly configured.
        # Goals:
        # - Bounded queues (avoid unbounded backpressure)
        # - DLQ enabled
        # - Plugin invoke timeout <= 20s
        # - Circuit breaker threshold low by default
        try:
            profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
            is_prod = profile in ("prod", "production", "staging")
            # Queue size defaults (only if not explicitly set)
            if is_prod:
                # Detect whether operator explicitly set each limit
                env_set_high = "AETHERRA_KERNEL_QSIZE_HIGH" in os.environ
                env_set_norm = "AETHERRA_KERNEL_QSIZE_NORMAL" in os.environ
                env_set_bg = "AETHERRA_KERNEL_QSIZE_BACKGROUND" in os.environ
                # If not set or set to 0/unbounded, apply safe defaults
                if (not env_set_high) or int(
                    self.queue_limits.get("high_priority", 0) or 0
                ) <= 0:
                    self.queue_limits["high_priority"] = 100
                if (not env_set_norm) or int(
                    self.queue_limits.get("normal_priority", 0) or 0
                ) <= 0:
                    self.queue_limits["normal_priority"] = 500
                if (not env_set_bg) or int(
                    self.queue_limits.get("background", 0) or 0
                ) <= 0:
                    self.queue_limits["background"] = 1000

                # Ensure DLQ is enabled in production unless explicitly disabled
                if "AETHERRA_KERNEL_DLQ" not in os.environ:
                    self.dlq_enabled = True

                # Plugin timeout: cap default at 20s in production if not explicitly configured
                if "AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC" not in os.environ:
                    try:
                        self.plugin_invoke_timeout_sec = min(
                            20.0, float(self.plugin_invoke_timeout_sec or 20.0)
                        )
                    except Exception:
                        self.plugin_invoke_timeout_sec = 20.0

                # Circuit breaker threshold: prefer slightly lower default in production if not set
                if "AETHERRA_PLUGIN_CB_THRESHOLD" not in os.environ:
                    try:
                        self.plugin_cb_threshold = max(
                            1, int(min(3, self.plugin_cb_threshold or 3))
                        )
                    except Exception:
                        self.plugin_cb_threshold = 3

                logger.info(
                    f"[PROFILE] Production defaults applied: qlimits={{high:{self.queue_limits['high_priority']}, normal:{self.queue_limits['normal_priority']}, background:{self.queue_limits['background']}}}, "
                    f"dlq_enabled={self.dlq_enabled}, plugin_timeout={self.plugin_invoke_timeout_sec}s, cb_threshold={self.plugin_cb_threshold}"
                )
        except Exception as _e:
            logger.debug(f"[PROFILE] Failed to apply production defaults: {_e}")

    # ---- Night cycle helpers (TZ-aware) ----
    def _now_in_night_tz(self) -> datetime:
        """Return current time in configured night timezone (or local if unset)."""
        try:
            if self.night_tz_name:
                # Prefer Python 3.9+ zoneinfo if available, else fallback to pytz or UTC
                try:
                    from zoneinfo import ZoneInfo  # type: ignore

                    return datetime.now(ZoneInfo(self.night_tz_name))
                except Exception:
                    try:
                        import pytz  # type: ignore

                        tz = pytz.timezone(self.night_tz_name)
                        return datetime.now(tz)
                    except Exception:
                        return datetime.now(timezone.utc)
            if self.night_utc:
                return datetime.now(timezone.utc)
        except Exception:
            pass
        # Fallback: local naive datetime
        return datetime.now()

    def _night_date_key(self, now_dt: datetime) -> str:
        tz_key = self.night_tz_name or ("UTC" if self.night_utc else "local")
        try:
            return f"{now_dt.date().isoformat()}|{tz_key}"
        except Exception:
            return f"unknown|{tz_key}"

    def inject_systems(
        self,
        memory_system,
        plugin_manager,
        aetherra_engine,
        scheduler,
        service_registry,
    ):
        """[PLUGIN] Inject core system references for orchestration."""
        self.memory_system = memory_system
        self.plugin_manager = plugin_manager
        self.aetherra_engine = aetherra_engine
        self.scheduler = scheduler
        self.service_registry = service_registry
        logger.info("[LINK] Core systems injected into kernel loop")

    async def start_kernel_loop(self):
        """[LAUNCH] Start the main OS kernel loop."""
        logger.info("[CORE] Starting Aetherra OS Kernel Loop...")
        self.running = True
        self.start_time = datetime.now()

        # Refuse to start in production if backpressure is unbounded (safety gate)
        try:
            profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
            allow_unbounded = os.getenv("AETHERRA_ALLOW_UNBOUNDED", "0") == "1"
            if profile in ("prod", "production", "staging") and not allow_unbounded:
                ql = self.queue_limits or {}
                if any(
                    int(ql.get(k, 0) or 0) <= 0
                    for k in ("high_priority", "normal_priority", "background")
                ):
                    logger.error(
                        "[SAFETY] Refusing to start: unbounded kernel queues in production. "
                        "Set AETHERRA_KERNEL_QSIZE_* > 0 or use AETHERRA_ALLOW_UNBOUNDED=1 to override."
                    )
                    raise RuntimeError("kernel_backpressure_unbounded")
                # Enforce DLQ in production
                if not self.dlq_enabled:
                    logger.error(
                        "[SAFETY] Refusing to start: DLQ is disabled in production. "
                        "Set AETHERRA_KERNEL_DLQ=1 or AETHERRA_ALLOW_UNBOUNDED=1 to override."
                    )
                    raise RuntimeError("kernel_dlq_disabled_in_production")
        except Exception as _e:
            # If the exception is our intentional safety exception, propagate after logging
            if isinstance(_e, RuntimeError) and str(_e) in (
                "kernel_backpressure_unbounded",
                "kernel_dlq_disabled_in_production",
            ):
                self.running = False
                logger.critical(
                    f"[ABORT] Kernel did not start due to safety gate: {_e}"
                )
                raise
            logger.debug(f"[SAFETY] Safety gate check error: {_e}")

        # Load any persisted tasks (best-effort)
        if self.persist_tasks:
            await self._load_persisted_tasks()

        # Start concurrent tasks
        tasks = [
            asyncio.create_task(self._main_processing_loop()),
            asyncio.create_task(self._background_maintenance_loop()),
            asyncio.create_task(self._health_monitoring_loop()),
            asyncio.create_task(self._memory_optimization_loop()),
            asyncio.create_task(self._plugin_orchestration_loop()),
            asyncio.create_task(self._heartbeat_loop()),
        ]

        # Optional visible heartbeat to keep terminal active during idle
        if getattr(self, "visible_heartbeat_sec", 0) and self.visible_heartbeat_sec > 0:
            tasks.append(asyncio.create_task(self._visible_heartbeat_loop()))

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"[ERROR] Kernel loop error: {e}")
            await self.shutdown()

    async def _heartbeat_loop(self):
        """💓 Send regular heartbeat to service registry."""
        while self.running:
            try:
                if self.service_registry:
                    await self.service_registry.update_heartbeat("kernel_loop")
                await asyncio.sleep(60)  # Heartbeat every minute
            except Exception as e:
                logger.error(f"[ERROR] Kernel heartbeat error: {e}")
                await asyncio.sleep(60)

    async def _visible_heartbeat_loop(self):
        """Emit a lightweight heartbeat log at a configurable interval for operator visibility.

        Controlled via env:
        - AETHERRA_KERNEL_HEARTBEAT_SEC (int > 0 to enable)
        - AETHERRA_KERNEL_HEARTBEAT_LEVEL (INFO|DEBUG; default INFO)
        """
        interval = max(1, int(getattr(self, "visible_heartbeat_sec", 0) or 0))
        # Map level string to logging level
        level_name = (
            getattr(self, "visible_heartbeat_level", "INFO") or "INFO"
        ).upper()
        level = logging.INFO if level_name == "INFO" else logging.DEBUG

        while self.running and interval > 0:
            try:
                upt = 0
                try:
                    if self.start_time:
                        upt = int((datetime.now() - self.start_time).total_seconds())
                except Exception:
                    pass
                qh = self.high_priority_queue.qsize()
                qn = self.normal_priority_queue.qsize()
                qb = self.background_queue.qsize()
                avg_ms = int(
                    float(self.metrics.get("avg_cycle_time", 0.0) or 0.0) * 1000
                )
                last_ms = int(
                    float(self.metrics.get("last_cycle_time", 0.0) or 0.0) * 1000
                )
                inflight = {}
                try:
                    inflight = self._inflight_by_target.copy()
                except Exception:
                    pass
                logger.log(
                    level,
                    f"[BEAT] upt={upt}s cycles={self.cycle_count} q(H/N/B)={qh}/{qn}/{qb} avg={avg_ms}ms last={last_ms}ms paused={self.paused} inflight={inflight}",
                )
                await asyncio.sleep(interval)
            except Exception as e:
                logger.debug(f"[HB] Visible heartbeat error: {e}")
                # Backoff minimally to avoid tight loop on repeated errors
                await asyncio.sleep(max(5, interval))

    async def _main_processing_loop(self):
        """[LOOP] Main processing cycle - handles events and orchestration."""
        while self.running:
            cycle_start = time.time()

            try:
                # Honor global pause toggle
                if self.paused:
                    await asyncio.sleep(0.5)
                    continue

                # Apply priority aging (promote long-waiting tasks upward)
                try:
                    await self._apply_priority_aging()
                except Exception:
                    pass
                # Process high priority tasks first
                await self._process_task_queue(
                    self.high_priority_queue, "high_priority", max_tasks=5
                )

                # Process normal priority tasks
                await self._process_task_queue(
                    self.normal_priority_queue, "normal_priority", max_tasks=3
                )

                # Process background tasks
                await self._process_task_queue(
                    self.background_queue, "background", max_tasks=1
                )

                # Check for night cycle
                await self._check_night_cycle()

                # Update metrics
                cycle_time = time.time() - cycle_start
                self._update_metrics(cycle_time)

                # Adaptive sleep based on load
                sleep_time = max(0.1, 1.0 - cycle_time)
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"[ERROR] Main processing loop error: {e}")
                self.metrics["errors_count"] += 1
                await asyncio.sleep(1.0)

    async def _background_maintenance_loop(self):
        """🛠️ Background system maintenance and optimization."""
        while self.running:
            try:
                # Every 5 minutes: System health check
                if self.cycle_count % 300 == 0:
                    await self._perform_health_check()

                # Every 30 minutes: Memory optimization
                if self.cycle_count % 1800 == 0 and self.memory_system:
                    await self._optimize_memory()

                # Every hour: Plugin health check
                if self.cycle_count % 3600 == 0 and self.plugin_manager:
                    await self._check_plugin_health()

                # Periodic task snapshot (if enabled)
                if getattr(self, "persist_tasks", False):
                    await self._snapshot_tasks()

                # Optional periodic metrics flush for live dashboards
                if self.metrics_flush_sec:
                    now = time.time()
                    if now - self._last_metrics_flush >= self.metrics_flush_sec:
                        await self._save_metrics()
                        self._last_metrics_flush = now

                await asyncio.sleep(60)  # Run every minute

            except Exception as e:
                logger.error(f"[ERROR] Background maintenance error: {e}")
                await asyncio.sleep(60)

    async def _health_monitoring_loop(self):
        """💓 Continuous system health monitoring."""
        while self.running:
            try:
                # Monitor system vitals
                health_status = await self._gather_health_metrics()
                # Enrich payload with kernel operational telemetry
                try:
                    health_status.update(
                        {
                            "queue_sizes": {
                                "high_priority": self.high_priority_queue.qsize(),
                                "normal_priority": self.normal_priority_queue.qsize(),
                                "background": self.background_queue.qsize(),
                            },
                            "queue_limits": getattr(self, "queue_limits", {}).copy(),
                            "plugin_cb_open": self._plugin_cb_is_open(),
                            "dlq_count": getattr(self, "_dlq_count", 0),
                            "last_metrics_flush": self._last_metrics_flush,
                        }
                    )
                except Exception:
                    pass

                # Log health status
                logger.debug(f"[HEALTH] System Health: {health_status}")

                # Alert on critical issues
                if health_status.get("critical_issues"):
                    logger.warning(
                        f"[WARN] Critical issues detected: {health_status['critical_issues']}"
                    )

                # Broadcast structured health to services (best-effort)
                try:
                    if self.service_registry and hasattr(
                        self.service_registry, "broadcast_message"
                    ):
                        await self.service_registry.broadcast_message(
                            "kernel.health", health_status
                        )
                except Exception:
                    pass

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"[ERROR] Health monitoring error: {e}")
                await asyncio.sleep(30)

    async def _memory_optimization_loop(self):
        """[BRAIN] Continuous memory system optimization."""
        while self.running:
            try:
                if self.memory_system:
                    # Light memory optimization every 10 minutes
                    await self.memory_system.light_optimization()

                await asyncio.sleep(600)  # Every 10 minutes

            except Exception as e:
                logger.error(f"[ERROR] Memory optimization error: {e}")
                await asyncio.sleep(600)

    async def _plugin_orchestration_loop(self):
        """[PLUGIN] Plugin coordination and execution."""
        while self.running:
            try:
                if self.plugin_manager:
                    # Execute scheduled plugin tasks
                    await self.plugin_manager.execute_scheduled_tasks()

                await asyncio.sleep(120)  # Every 2 minutes

            except Exception as e:
                logger.error(f"[ERROR] Plugin orchestration error: {e}")
                await asyncio.sleep(120)

    async def _check_night_cycle(self):
        """🌙 Check if we should perform night cycle processing (TZ-aware, once/day)."""
        # Safety: in production refuse to run if TZ not explicitly set
        profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
        is_prod = profile in ("prod", "production", "staging")
        tz_explicit = bool(self.night_tz_name) or self.night_utc

        # In prod/staging, block unconditionally if TZ not explicit to avoid surprises
        if is_prod and not tz_explicit:
            self.metrics["night_cycles_blocked_no_tz"] = (
                self.metrics.get("night_cycles_blocked_no_tz", 0) + 1
            )
            logger.warning(
                "[NIGHT] Blocking night cycle in production: timezone not explicitly set. "
                "Set AETHERRA_NIGHT_TZ (e.g., 'UTC' or an IANA TZ) or AETHERRA_NIGHT_UTC=1."
            )
            return

        # Determine current time in configured TZ (or local if not set)
        now_tz = self._now_in_night_tz()

        # Night cycle within configured window, once per day
        start_h, end_h = (
            getattr(self, "night_start_hour", 2),
            getattr(self, "night_end_hour", 4),
        )
        if end_h < start_h:
            end_h = start_h

        in_window = start_h <= int(now_tz.hour) <= end_h

        if in_window:
            date_key = self._night_date_key(now_tz)
            if self._night_last_date_key == date_key:
                return  # already handled today

            # Schedule with optional staggering, capped within window length
            window_len_sec = max(0, int((end_h - start_h) * 3600))
            delay_sec = min(max(0, self._night_stagger_sec), max(0, window_len_sec - 60))

            async def _run_after_delay(delay: float, date_key_val: str):
                try:
                    if delay > 0:
                        await asyncio.sleep(delay)
                    logger.info(
                        f"🌙 Initiating Night Cycle (tz={self.night_tz_name or ('UTC' if self.night_utc else 'local')}, delay={int(delay)}s)..."
                    )
                    await self._perform_night_cycle()
                    self.metrics["night_cycles_count"] += 1
                except Exception as _e:
                    logger.error(f"[ERROR] Night cycle error (scheduled): {_e}")
                finally:
                    # mark completion for the day
                    self._night_cycle_scheduled = False
                    self._night_last_date_key = date_key_val
                    self.last_night_cycle = datetime.now()

            # Prevent multiple schedules in the same window
            if not self._night_cycle_scheduled:
                self._night_cycle_scheduled = True
                asyncio.create_task(_run_after_delay(delay_sec, date_key))

    async def _perform_night_cycle(self):
        """🌙 Deep system optimization and reflection during night cycle."""
        try:
            logger.info("🌙 Night Cycle: Deep Memory Consolidation...")
            if self.memory_system:
                await self.memory_system.deep_consolidation()

            logger.info("🌙 Night Cycle: Plugin Optimization...")
            if self.plugin_manager:
                await self.plugin_manager.optimize_plugins()

            logger.info("🌙 Night Cycle: System Reflection...")
            if self.aetherra_engine:
                await self.aetherra_engine.reflect_on_day()

            logger.info("🌙 Night Cycle: Cleanup and Maintenance...")
            await self._cleanup_temporary_files()

            logger.info("[OK] Night Cycle completed successfully")

        except Exception as e:
            logger.error(f"[ERROR] Night cycle error: {e}")

    async def _process_task_queue(
        self, queue: asyncio.Queue, pending_key: str, max_tasks: int = 5
    ):
        """📋 Process tasks from a priority queue."""
        processed = 0
        while not queue.empty() and processed < max_tasks:
            try:
                task = await asyncio.wait_for(queue.get(), timeout=0.1)
                # Drop if expired by deadline
                try:
                    deadline_ts = task.get("deadline_ts")
                    trace_id = task.get("trace_id")
                    # HMR tasks have no deadline by default
                    if deadline_ts and time.time() > float(deadline_ts):
                        self.metrics["expired_tasks"] = (
                            self.metrics.get("expired_tasks", 0) + 1
                        )
                        logger.warning(
                            f"[EXPIRE] Dropping expired task trace={trace_id} type={task.get('type')}"
                        )
                        self._dlq_write(task, reason="expired")
                        # remove from pending snapshot below
                    else:
                        await self._execute_task(task)
                except Exception:
                    await self._execute_task(task)
                processed += 1
                # Remove one matching entry from pending snapshot (best-effort)
                try:
                    lst = self._pending_tasks.get(pending_key, [])
                    if lst:
                        for i, t in enumerate(lst):
                            if t == task:
                                del lst[i]
                                break
                except Exception:
                    pass
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"[ERROR] Task processing error: {e}")

    async def _apply_priority_aging(self):
        """Promote long-waiting tasks from lower queues to higher priority.

        - If AETHERRA_KERNEL_AGING_SEC > 0, tasks in normal older than this are promoted to high.
        - Tasks in background older than this are promoted to normal.

        Uses asyncio.Queue._queue (deque) for efficient filtering. Best-effort only.
        """
        if not getattr(self, "priority_aging_sec", 0):
            return
        now = time.time()

        def _promote(
            src_q: asyncio.Queue, dst_q: asyncio.Queue, src_key: str, dst_key: str
        ):
            try:
                # Access underlying deque; filter and move eligible tasks
                dq = getattr(src_q, "_queue", None)
                if dq is None or len(dq) == 0:
                    return 0
                moved = 0
                keep = []
                while dq:
                    item = dq.popleft()
                    enq = float(item.get("enqueued_ts", 0) or 0)
                    if enq and (now - enq) >= self.priority_aging_sec:
                        # Promote
                        dst_q.put_nowait(item)
                        moved += 1
                        # Update pending snapshot bookkeeping (best-effort)
                        try:
                            lst = self._pending_tasks.get(src_key, [])
                            for i, t in enumerate(lst):
                                if t == item:
                                    del lst[i]
                                    break
                            self._pending_tasks.get(dst_key, []).append(item)
                        except Exception:
                            pass
                    else:
                        keep.append(item)
                # Restore remaining
                for k in keep:
                    dq.append(k)
                return moved
            except Exception:
                return 0

        # Background -> Normal
        moved_bg = _promote(
            self.background_queue,
            self.normal_priority_queue,
            "background",
            "normal_priority",
        )
        # Normal -> High
        moved_nm = _promote(
            self.normal_priority_queue,
            self.high_priority_queue,
            "normal_priority",
            "high_priority",
        )
        if moved_bg or moved_nm:
            self.metrics["priority_aging_promotions"] = (
                self.metrics.get("priority_aging_promotions", 0)
                + int(moved_bg)
                + int(moved_nm)
            )

    async def _execute_task(self, task: Dict[str, Any]):
        """[SYS] Execute a single task."""
        try:
            task_type = task.get("type")
            task_data = task.get("data", {})
            requester = task.get("requester") or task_data.get("requester")
            trace_id = task.get("trace_id") or "-"
            target_for_inflight: Optional[str] = None

            # Honor HMR quiesce signals (best-effort Phase 1)
            if (
                task_type == "plugin_invoke"
                and "adapter:plugin" in self._quiesced_targets
            ):
                logger.debug("[HMR] Dropping plugin_invoke during quiesce")
                return
            if (
                task_type == "memory_query"
                and "adapter:memory" in self._quiesced_targets
            ):
                logger.debug("[HMR] Dropping memory_query during quiesce")
                return
            if task_type == "aetherra_thought" and "engine" in self._quiesced_targets:
                logger.debug("[HMR] Dropping aetherra_thought during quiesce")
                return

            # HMR control-plane tasks
            if task_type in ("hmr_reload", "hmr_status"):
                if not self.hmr_controller:
                    logger.warning("[HMR] HMR task received but controller not enabled")
                    return {"ok": False, "error": "hmr_disabled"}
                try:
                    coro_or_result = self.hmr_controller.handle_kernel_task(task)
                    if asyncio.iscoroutine(coro_or_result):
                        return await cast(Coroutine[Any, Any, Any], coro_or_result)
                    return coro_or_result
                except Exception as e:
                    logger.error(f"[HMR] HMR task handling error: {e}")
                    return {"ok": False, "error": "hmr_exception"}

            if task_type == "memory_query":
                if self.memory_system:
                    timeout = float(task.get("timeout_sec") or 0) or 0
                    target_for_inflight = "adapter:memory"
                    self._inflight_inc(target_for_inflight)
                    if timeout > 0:
                        try:
                            await asyncio.wait_for(
                                self.memory_system.process_query(task_data),
                                timeout=timeout,
                            )
                        finally:
                            self._inflight_dec(target_for_inflight)
                    else:
                        try:
                            await self.memory_system.process_query(task_data)
                        finally:
                            self._inflight_dec(target_for_inflight)
            elif task_type == "plugin_invoke":
                # Circuit breaker short-circuit
                if self._plugin_cb_is_open():
                    self.metrics["plugin_cb_dropped"] = (
                        self.metrics.get("plugin_cb_dropped", 0) + 1
                    )
                    logger.warning(
                        f"[CB] Plugin invoke dropped (open) trace={trace_id} requester={requester}"
                    )
                    return
                # Optional security capability check to prevent bypass
                try:
                    from Aetherra.security.capabilities import (
                        has_capability,
                    )  # type: ignore
                except Exception:
                    has_capability = None  # type: ignore

                # Enforce capability gate by default in production profile
                profile = (os.getenv("AETHERRA_PROFILE", "") or "").strip().lower()
                require_caps = os.getenv(
                    "AETHERRA_REQUIRE_CAPABILITIES", "0"
                ) == "1" or profile in ("prod", "production")
                if require_caps and has_capability is not None and requester:
                    if not has_capability(str(requester), "kernel:invoke_plugin"):
                        logger.warning(
                            f"[SEC] Denied plugin_invoke from '{requester}' (missing kernel:invoke_plugin)"
                        )
                        return

                # Simple per-requester rate limiting (tokens per minute)
                try:
                    limit = int(
                        os.getenv("AETHERRA_KERNEL_RATE_LIMIT_PER_MIN", "0") or 0
                    )
                except Exception:
                    limit = 0
                if limit > 0 and requester:
                    now = int(time.time() // 60)  # minute window
                    if not hasattr(self, "_rl_window"):
                        self._rl_window = now
                        self._rl_counts = {}
                    if getattr(self, "_rl_window", now) != now:
                        self._rl_window = now
                        self._rl_counts = {}
                    cnt = getattr(self, "_rl_counts", {}).get(requester, 0)
                    if cnt >= limit:
                        logger.warning(
                            f"[RATE] Rate-limited plugin_invoke for '{requester}' (limit={limit}/min)"
                        )
                        self.metrics["plugin_invoke_rate_limited"] = (
                            self.metrics.get("plugin_invoke_rate_limited", 0) + 1
                        )
                        return
                    # consume
                    self._rl_counts[requester] = cnt + 1

                if self.plugin_manager:
                    # Timeout support with circuit breaker accounting
                    timeout = (
                        float(task.get("timeout_sec") or 0)
                        or self.plugin_invoke_timeout_sec
                    )
                    target_for_inflight = "adapter:plugin"
                    # Enforce simple per-plugin concurrency cap if configured
                    plugin_id = str(
                        task_data.get("plugin_id")
                        or task_data.get("name")
                        or task_data.get("id")
                        or ""
                    )
                    if self.plugin_max_concurrency > 0 and plugin_id:
                        running = self._plugin_running_counts.get(plugin_id, 0)
                        if running >= self.plugin_max_concurrency:
                            # Defer with small jitter to avoid thundering herd
                            self.metrics["plugin_invoke_deferred_concurrency"] = (
                                self.metrics.get(
                                    "plugin_invoke_deferred_concurrency", 0
                                )
                                + 1
                            )
                            delay = 0.3 + random.uniform(0.0, 0.7)
                            logger.debug(
                                f"[CONC] Deferring plugin '{plugin_id}' invoke by {delay:.2f}s (running={running}, cap={self.plugin_max_concurrency})"
                            )
                            asyncio.create_task(
                                self._requeue_after_delay(
                                    task, delay_sec=delay, priority="normal"
                                )
                            )
                            return

                    # Proceed with invoke and manage running count
                    if plugin_id and self.plugin_max_concurrency > 0:
                        self._plugin_running_counts[plugin_id] = (
                            self._plugin_running_counts.get(plugin_id, 0) + 1
                        )
                    try:
                        self._inflight_inc(target_for_inflight)
                        await asyncio.wait_for(
                            self.plugin_manager.invoke_plugin(task_data),
                            timeout=timeout,
                        )
                        self._record_plugin_success()
                    except asyncio.TimeoutError:
                        self.metrics["plugin_invoke_timeouts"] = (
                            self.metrics.get("plugin_invoke_timeouts", 0) + 1
                        )
                        self._record_plugin_failure()
                        logger.warning(
                            f"[TIMEOUT] plugin_invoke timed out after {timeout}s trace={trace_id} requester={requester}"
                        )
                        await self._maybe_retry(task, reason="timeout")
                    except Exception as ex:
                        self.metrics["plugin_invoke_errors"] = (
                            self.metrics.get("plugin_invoke_errors", 0) + 1
                        )
                        self._record_plugin_failure()
                        logger.error(
                            f"[ERROR] plugin_invoke error trace={trace_id} requester={requester} err={ex}"
                        )
                        await self._maybe_retry(task, reason="error")
                    finally:
                        if target_for_inflight:
                            self._inflight_dec(target_for_inflight)
                        if plugin_id and self.plugin_max_concurrency > 0:
                            try:
                                self._plugin_running_counts[plugin_id] = max(
                                    0, self._plugin_running_counts.get(plugin_id, 1) - 1
                                )
                            except Exception:
                                pass
            elif task_type == "aetherra_thought":
                if self.aetherra_engine:
                    # Process thought as a message to the Aetherra engine
                    thought_content = task_data.get(
                        "content", task_data.get("message", str(task_data))
                    )
                    target_for_inflight = "engine"
                    self._inflight_inc(target_for_inflight)
                    try:
                        await self.aetherra_engine.process_message(thought_content)
                    finally:
                        self._inflight_dec(target_for_inflight)
            else:
                logger.warning(f"[WARN] Unknown task type: {task_type}")

        except Exception as e:
            logger.error(f"[ERROR] Task execution error: {e}")

    def _plugin_cb_is_open(self) -> bool:
        return time.time() < float(self._plugin_cb_open_until or 0)

    def _record_plugin_failure(self):
        self._plugin_cb_failures += 1
        if self._plugin_cb_failures >= max(1, self.plugin_cb_threshold):
            self._plugin_cb_open_until = time.time() + max(
                1, self.plugin_cb_cooldown_sec
            )
            self._plugin_cb_failures = 0
            self.metrics["plugin_cb_open_count"] = (
                self.metrics.get("plugin_cb_open_count", 0) + 1
            )
            logger.warning(
                f"[CB] Opened circuit for plugin_invoke cooldown={self.plugin_cb_cooldown_sec}s"
            )

    def _record_plugin_success(self):
        # On success, gradually heal failures
        if self._plugin_cb_failures > 0:
            self._plugin_cb_failures = 0

    async def _gather_health_metrics(self) -> Dict[str, Any]:
        """[HEALTH] Gather comprehensive system health metrics."""
        health = {
            "timestamp": datetime.now().isoformat(),
            "kernel_uptime": (datetime.now() - self.start_time).total_seconds()
            if self.start_time
            else 0,
            "cycle_count": self.cycle_count,
            "memory_status": "unknown",
            "plugin_status": "unknown",
            "lyrixa_status": "unknown",
            "critical_issues": [],
        }

        try:
            # Check memory system health
            if self.memory_system and hasattr(self.memory_system, "get_health_status"):
                health["memory_status"] = await self.memory_system.get_health_status()

            # Check plugin system health
            if self.plugin_manager and hasattr(
                self.plugin_manager, "get_health_status"
            ):
                health["plugin_status"] = await self.plugin_manager.get_health_status()

            # Check Lyrixa health
            if self.aetherra_engine and hasattr(
                self.aetherra_engine, "get_health_status"
            ):
                health[
                    "aetherra_status"
                ] = await self.aetherra_engine.get_health_status()

        except Exception as e:
            logger.error(f"[ERROR] Health metrics gathering error: {e}")
            health["critical_issues"].append(f"Health check error: {str(e)}")

        return health

    async def _perform_health_check(self):
        """[HEALTH] Perform comprehensive system health check."""
        logger.info("[HEALTH] Performing system health check...")
        health = await self._gather_health_metrics()

        # Log health summary
        try:
            logger.info(
                f"[STATS] Health Summary: Memory={health.get('memory_status', 'unknown')}, "
                f"Plugins={health.get('plugin_status', 'unknown')}, Lyrixa={health.get('aetherra_status', 'unknown')}"
            )
        except Exception:
            # Never allow health logging to raise due to missing keys
            logger.info(f"[STATS] Health Summary: {health}")

    async def _optimize_memory(self):
        """[BRAIN] Perform memory optimization."""
        if self.memory_system:
            logger.info("[BRAIN] Performing memory optimization...")
            await self.memory_system.optimize()

    async def _check_plugin_health(self):
        """[PLUGIN] Check plugin system health."""
        if self.plugin_manager:
            logger.info("[PLUGIN] Checking plugin health...")
            await self.plugin_manager.health_check()

    async def _cleanup_temporary_files(self):
        """🧹 Clean up temporary files and logs."""
        try:
            # Clean up old log files (older than 7 days)
            log_dir = Path("logs")
            if log_dir.exists():
                cutoff = datetime.now() - timedelta(days=7)
                for log_file in log_dir.glob("*.log"):
                    if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff:
                        log_file.unlink()
                        logger.debug(f"🗑️ Cleaned up old log: {log_file}")
        except Exception as e:
            logger.error(f"[ERROR] Cleanup error: {e}")

    def _update_metrics(self, cycle_time: float):
        """[STATS] Update kernel performance metrics."""
        self.cycle_count += 1
        self.metrics["total_cycles"] = self.cycle_count
        self.metrics["last_cycle_time"] = cycle_time

        # Calculate rolling average
        if self.metrics["avg_cycle_time"] == 0:
            self.metrics["avg_cycle_time"] = cycle_time
        else:
            alpha = 0.1  # Smoothing factor
            self.metrics["avg_cycle_time"] = (
                alpha * cycle_time + (1 - alpha) * self.metrics["avg_cycle_time"]
            )

    async def add_task(self, task: Dict[str, Any], priority: str = "normal"):
        """📝 Add a task to the appropriate priority queue with optional backpressure and snapshotting."""
        # Ensure task envelope fields
        task = self._ensure_task_envelope(task)
        if priority == "high":
            q = self.high_priority_queue
            key = "high_priority"
        elif priority == "background":
            q = self.background_queue
            key = "background"
        else:
            q = self.normal_priority_queue
            key = "normal_priority"

        limit = self.queue_limits.get(key, 0)
        if limit and q.qsize() >= limit:
            metric_key = (
                "drops_high"
                if key == "high_priority"
                else ("drops_background" if key == "background" else "drops_normal")
            )
            self.metrics[metric_key] = self.metrics.get(metric_key, 0) + 1
            logger.warning(
                f"[BACKPRESSURE] Dropping task for {key}: queue full (limit={limit})"
            )
            self._dlq_write(task, reason=f"queue_full:{key}")
            return

        await q.put(task)
        # Track pending for snapshotting
        try:
            self._pending_tasks[key].append(task)
        except Exception:
            pass

    def _ensure_task_envelope(self, task: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not isinstance(task, dict):
                task = {"type": "unknown", "data": {"raw": str(task)}}
            if "trace_id" not in task:
                task["trace_id"] = uuid.uuid4().hex
            if "enqueued_ts" not in task:
                task["enqueued_ts"] = time.time()
            # Apply default TTL if provided and no deadline present
            if task.get("deadline_ts") is None and self.default_task_ttl_sec > 0:
                task["deadline_ts"] = float(task["enqueued_ts"]) + float(
                    self.default_task_ttl_sec
                )
        except Exception:
            pass
        return task

    def _dlq_write(self, task: Dict[str, Any], reason: str = "unknown"):
        try:
            if not self.dlq_enabled:
                return
            if self._dlq_count >= max(1, self.dlq_max):
                self.metrics["dlq_overflow"] = self.metrics.get("dlq_overflow", 0) + 1
                return
            self.dlq_path.parent.mkdir(parents=True, exist_ok=True)
            record = {
                "ts": datetime.now().isoformat(),
                "reason": reason,
                "trace_id": task.get("trace_id"),
                "type": task.get("type"),
                "data": task.get("data"),
            }
            with open(self.dlq_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            self._dlq_count += 1
            self.metrics["dlq_count"] = self._dlq_count
        except Exception as e:
            logger.debug(f"[DLQ] Failed to write DLQ record: {e}")

    async def _requeue_after_delay(
        self, task: Dict[str, Any], delay_sec: float, priority: str = "normal"
    ):
        """Helper: re-enqueue a task after a delay (best-effort)."""
        try:
            await asyncio.sleep(max(0.0, float(delay_sec)))
            await self.add_task(task, priority=priority)
        except Exception as e:
            logger.debug(f"[REQUEUE] Failed to requeue task: {e}")

    async def _maybe_retry(self, task: Dict[str, Any], reason: str = "error"):
        """Schedule a retry with jittered exponential backoff if policy allows."""
        try:
            if self.retry_max <= 0:
                return
            meta = task.setdefault("_retry", {})
            attempt = int(meta.get("attempt", 0))
            if attempt >= self.retry_max:
                self.metrics["plugin_invoke_retries_exhausted"] = (
                    self.metrics.get("plugin_invoke_retries_exhausted", 0) + 1
                )
                logger.warning(
                    f"[RETRY] Exhausted retries for trace={task.get('trace_id')} reason={reason}"
                )
                return
            meta["attempt"] = attempt + 1
            # Base delay in seconds with exponential backoff and jitter (0.5x..1.5x)
            base = max(1.0, float(self.retry_base_delay_ms) / 1000.0)
            backoff = base * (2 ** (attempt))
            delay = backoff * random.uniform(0.5, 1.5)
            self.metrics["plugin_invoke_retries_scheduled"] = (
                self.metrics.get("plugin_invoke_retries_scheduled", 0) + 1
            )
            logger.info(
                f"[RETRY] Scheduling retry {meta['attempt']}/{self.retry_max} in {delay:.2f}s for trace={task.get('trace_id')}"
            )
            asyncio.create_task(
                self._requeue_after_delay(task, delay_sec=delay, priority="normal")
            )
        except Exception as e:
            logger.debug(f"[RETRY] Failed to schedule retry: {e}")

    async def shutdown(self):
        """🛑 Gracefully shutdown the kernel loop."""
        logger.info("🛑 Shutting down Aetherra OS Kernel Loop...")
        self.running = False

        # Save final metrics
        await self._save_metrics()

        # Snapshot pending tasks if enabled
        if getattr(self, "persist_tasks", False):
            await self._snapshot_tasks()

        logger.info("[OK] Kernel loop shutdown complete")

    async def _save_metrics(self):
        """[MEM] Save kernel metrics to file."""
        try:
            metrics_file = Path("aetherra_kernel_metrics.json")
            self.metrics["shutdown_time"] = datetime.now().isoformat()
            self.metrics["live_time"] = datetime.now().isoformat()

            with open(metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2)

            logger.info(f"[STATS] Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save metrics: {e}")

    def get_status(self) -> Dict[str, Any]:
        """📋 Get current kernel status."""
        return {
            "running": self.running,
            "paused": self.paused,
            "uptime": (datetime.now() - self.start_time).total_seconds()
            if self.start_time
            else 0,
            "cycle_count": self.cycle_count,
            "metrics": self.metrics.copy(),
            "queue_sizes": {
                "high_priority": self.high_priority_queue.qsize(),
                "normal_priority": self.normal_priority_queue.qsize(),
                "background": self.background_queue.qsize(),
            },
            "queue_limits": getattr(self, "queue_limits", {}).copy(),
            "plugin_cb_open": self._plugin_cb_is_open(),
            "dlq_count": getattr(self, "_dlq_count", 0),
            "hmr": self._hmr_metrics,
            "inflight": self._inflight_by_target.copy(),
        }

    # -------------------- HMR helpers --------------------
    def record_hmr_attempt(self, target: str):
        try:
            self._hmr_metrics["attempts"] += 1
            per = self._hmr_metrics.setdefault("per_target", {})
            entry = per.setdefault(target, {"attempts": 0, "success": 0, "rollback": 0})
            entry["attempts"] += 1
        except Exception:
            pass

    def record_hmr_success(self, target: str, swap_ms: int):
        try:
            self._hmr_metrics["success"] += 1
            self._hmr_metrics["last_swap_ms"] = int(swap_ms)
            per = self._hmr_metrics.setdefault("per_target", {})
            entry = per.setdefault(target, {"attempts": 0, "success": 0, "rollback": 0})
            entry["success"] += 1
        except Exception:
            pass

    def record_hmr_rollback(self, target: str):
        try:
            self._hmr_metrics["rollback"] += 1
            per = self._hmr_metrics.setdefault("per_target", {})
            entry = per.setdefault(target, {"attempts": 0, "success": 0, "rollback": 0})
            entry["rollback"] += 1
        except Exception:
            pass

    async def quiesce_for_target(self, target: str, timeout_sec: int = 30) -> bool:
        """Pause a target and drain related work until empty or timeout.

        Targets: "adapter:plugin", "adapter:memory", "engine", "adapter:lyrixa_chat" (future).
        """
        try:
            t = str(target)
            self._quiesced_targets.add(t)
            # Wait for in-flight to hit zero, with small sleeps
            deadline = time.time() + max(0, int(timeout_sec))
            while self._inflight_by_target.get(t, 0) > 0 and time.time() < deadline:
                await asyncio.sleep(0.05)
            return self._inflight_by_target.get(t, 0) == 0
        except Exception:
            return False

    def resume_target(self, target: str) -> None:
        try:
            self._quiesced_targets.discard(str(target))
        except Exception:
            pass

    async def swap_system(self, target: str, new_instance) -> bool:
        """Replace kernel-held reference for a target."""
        try:
            t = str(target)
            if t in ("engine", "aetherra_engine"):
                self.aetherra_engine = new_instance
            elif t in ("adapter:memory", "memory"):
                self.memory_system = new_instance
            elif t in ("adapter:plugin", "plugin_manager"):
                self.plugin_manager = new_instance
            elif t in ("adapter:lyrixa_chat", "lyrixa_chat"):
                self.lyrixa_chat = new_instance
            else:
                return False
            return True
        except Exception:
            return False

    # -------------------- In-flight helpers --------------------
    def _inflight_inc(self, target: Optional[str]):
        try:
            if not target:
                return
            t = str(target)
            self._inflight_by_target[t] = self._inflight_by_target.get(t, 0) + 1
        except Exception:
            pass

    def _inflight_dec(self, target: Optional[str]):
        try:
            if not target:
                return
            t = str(target)
            self._inflight_by_target[t] = max(0, self._inflight_by_target.get(t, 0) - 1)
        except Exception:
            pass

    async def rollback_swap(self, target: str, old_instance) -> None:
        try:
            await self.swap_system(target, old_instance)
        except Exception:
            pass

    # -------------------- Control-plane helpers --------------------
    def pause(self):
        """Pause processing of queues (idempotent)."""
        self.paused = True

    def resume(self):
        """Resume processing of queues (idempotent)."""
        self.paused = False

    async def drain_queue(self, name: str, mode: str = "dlq"):
        """Drain a queue by name: 'high_priority'|'normal_priority'|'background'.

        mode='dlq' writes items to DLQ; mode='drop' discards silently.
        """
        q = None
        if name == "high_priority":
            q = self.high_priority_queue
        elif name == "normal_priority":
            q = self.normal_priority_queue
        elif name == "background":
            q = self.background_queue
        if q is None:
            return
        drained = 0
        while not q.empty():
            try:
                t = q.get_nowait()
                if mode == "dlq":
                    self._dlq_write(t, reason=f"drain:{name}")
                drained += 1
            except Exception:
                break
        if drained:
            self.metrics["queue_drained_total"] = (
                self.metrics.get("queue_drained_total", 0) + drained
            )

    def set_queue_limits(self, limits: Dict[str, int]):
        """Dynamically update queue limits at runtime (best-effort)."""
        try:
            for k in ("high_priority", "normal_priority", "background"):
                if k in limits:
                    v = int(limits[k])
                    self.queue_limits[k] = max(0, v)
        except Exception:
            pass

    async def _snapshot_tasks(self):
        """Persist a best-effort snapshot of pending tasks to disk."""
        try:
            self.tasks_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "high_priority": self._pending_tasks.get("high_priority", []),
                "normal_priority": self._pending_tasks.get("normal_priority", []),
                "background": self._pending_tasks.get("background", []),
                "ts": datetime.now().isoformat(),
            }
            with open(self.tasks_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"[SNAPSHOT] Pending tasks saved to {self.tasks_path}")
        except Exception as e:
            logger.debug(f"[SNAPSHOT] Failed to save pending tasks: {e}")

    async def _load_persisted_tasks(self):
        """Load previously persisted tasks (if any) into queues (best-effort)."""
        try:
            if not self.tasks_path.exists():
                return
            with open(self.tasks_path, encoding="utf-8") as f:
                data = json.load(f)
            for key, q in (
                ("high_priority", self.high_priority_queue),
                ("normal_priority", self.normal_priority_queue),
                ("background", self.background_queue),
            ):
                tasks = data.get(key, []) or []
                for t in tasks:
                    await q.put(t)
                self._pending_tasks[key] = list(tasks)
            # Remove file after load to avoid duplicate replays next boot
            try:
                self.tasks_path.unlink(missing_ok=True)
            except Exception:
                pass
            logger.info(
                f"[SNAPSHOT] Restored tasks from {self.tasks_path} (high={len(self._pending_tasks['high_priority'])}, "
                f"normal={len(self._pending_tasks['normal_priority'])}, background={len(self._pending_tasks['background'])})"
            )
        except Exception as e:
            logger.debug(f"[SNAPSHOT] Failed to restore tasks: {e}")


# Global kernel instance
kernel_loop = AetherraKernelLoop()


async def start_kernel(config: Optional[Dict] = None):
    """[LAUNCH] Start the Aetherra OS kernel loop."""
    global kernel_loop
    if config:
        kernel_loop.config.update(config)
    await kernel_loop.start_kernel_loop()


async def shutdown_kernel():
    """🛑 Shutdown the kernel loop."""
    global kernel_loop
    await kernel_loop.shutdown()


def get_kernel() -> AetherraKernelLoop:
    """[LINK] Get the global kernel instance."""
    return kernel_loop


if __name__ == "__main__":
    # Test the kernel loop
    async def test_kernel():
        kernel = AetherraKernelLoop()

        # Mock system injection
        class MockSystem:
            async def light_optimization(self):
                pass

            async def deep_consolidation(self):
                pass

            async def optimize(self):
                pass

            async def get_health_status(self):
                return "healthy"

            async def process_query(self, data):
                pass

            async def execute_scheduled_tasks(self):
                pass

            async def invoke_plugin(self, data):
                pass

            async def optimize_plugins(self):
                pass

            async def health_check(self):
                pass

            async def process_thought(self, data):
                pass

            async def reflect_on_day(self):
                pass

        mock_system = MockSystem()
        kernel.inject_systems(
            mock_system, mock_system, mock_system, mock_system, mock_system
        )

        # Run for a short test
        try:
            await asyncio.wait_for(kernel.start_kernel_loop(), timeout=5.0)
        except asyncio.TimeoutError:
            await kernel.shutdown()
            print("[OK] Kernel loop test completed successfully")

    asyncio.run(test_kernel())
