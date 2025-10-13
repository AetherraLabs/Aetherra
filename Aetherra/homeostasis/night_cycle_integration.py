# ... (rest of the implementation as in previous message, omitted for brevity)
#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""
🌙 Night-Cycle Intelligence Integration for Homeostasis
======================================================

Strategic Enhancement #5: Integrate with Night-Cycle Intelligence for optimized
resource allocation during low-activity periods.

This module provides:
- Activity pattern recognition and prediction
- Intelligent resource redistribution during low-activity periods
- Background optimization and predictive maintenance
- Sleep-mode coordination with wake-up triggers
- Circadian rhythm alignment for optimal resource utilization
- Energy-efficient operation scheduling

The Night-Cycle Intelligence system operates on the principle that computational
systems, like biological ones, benefit from periods of reduced activity where
resources can be redirected toward maintenance, optimization, and preparation
for future high-activity periods.

Author: Aetherra Labs
"""

import asyncio
import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class ActivityPeriod(Enum):
    """System activity periods."""

    PEAK = "peak"  # High activity, minimal optimization
    MODERATE = "moderate"  # Medium activity, selective optimization
    LOW = "low"  # Low activity, aggressive optimization
    NIGHT = "night"  # Deep optimization period
    DORMANT = "dormant"  # Minimal activity, maximum optimization


class OptimizationStrategy(Enum):
    """Optimization strategies for different activity periods."""

    CONSERVATIVE = "conservative"  # Minimal impact on active systems
    BALANCED = "balanced"  # Balance between optimization and availability
    AGGRESSIVE = "aggressive"  # Maximum optimization, some service degradation acceptable
    DEEP = "deep"  # Deep optimization, significant service reduction


class SleepMode(Enum):
    """System sleep modes."""

    AWAKE = "awake"  # Full operation
    LIGHT_SLEEP = "light_sleep"  # Reduce non-essential services
    DEEP_SLEEP = "deep_sleep"  # Minimal essential services only
    HIBERNATION = "hibernation"  # Maximum power savings


@dataclass
class ActivityPattern:
    """Pattern definition for system activity."""

    pattern_id: str
    time_range: Tuple[int, int]  # Hours as (start, end)
    expected_activity: float  # 0.0 to 1.0
    confidence: float  # Confidence in pattern prediction
    sample_count: int  # Number of observations
    last_updated: str
    seasonal_factors: Dict[str, float]  # Day of week, month variations


@dataclass
class OptimizationTask:
    """Background optimization task definition."""

    task_id: str
    task_type: str
    priority: int  # 1-5, higher is more important
    estimated_duration: float  # Minutes
    resource_requirements: Dict[str, float]  # CPU, memory, disk, network
    prerequisites: List[str]  # Other tasks that must complete first
    max_activity_threshold: float  # Don't run if activity > this
    created_at: str
    scheduled_for: Optional[str]
    completed_at: Optional[str]
    result: Optional[Dict[str, Any]]


@dataclass
class ResourceProfile:
    """Resource usage profile for optimization planning."""

    cpu_utilization: float
    memory_utilization: float
    disk_io_rate: float
    network_io_rate: float
    active_connections: int
    task_queue_length: int
    response_latency: float
    timestamp: str


@dataclass
class SleepSchedule:
    """Sleep schedule configuration."""

    schedule_id: str
    sleep_mode: SleepMode
    start_time: str  # HH:MM format
    end_time: str  # HH:MM format
    days_of_week: List[int]  # 0-6, Monday-Sunday
    wake_triggers: List[str]  # Events that can wake the system
    max_sleep_duration: float  # Maximum sleep time in hours
    enabled: bool


class NightCycleIntelligence:
    """
    Night-Cycle Intelligence system for optimized resource allocation.

    Manages activity pattern recognition, background optimization scheduling,
    and intelligent sleep-mode coordination.
    """

    def __init__(self, db_path: str = "night_cycle_intelligence.db"):
        self.db_path = db_path

        # State
        self.intelligence_active = False
        self.current_activity_period = ActivityPeriod.MODERATE
        self.current_sleep_mode = SleepMode.AWAKE

        # Activity pattern recognition
        self.activity_patterns: Dict[str, ActivityPattern] = {}
        self.activity_history: List[ResourceProfile] = []
        self.pattern_learning_window = 7 * 24  # 7 days in hours

        # Optimization management
        self.optimization_queue: List[OptimizationTask] = []
        self.active_optimizations: Dict[str, OptimizationTask] = {}
        self.completed_optimizations: List[OptimizationTask] = []

        # Sleep scheduling
        self.sleep_schedules: List[SleepSchedule] = []
        self.wake_triggers: Dict[str, bool] = {}

        # Configuration
        self.activity_sampling_interval = 300.0  # 5 minutes
        self.optimization_check_interval = 600.0  # 10 minutes
        self.min_optimization_window = 30.0  # 30 minutes
        self.max_concurrent_optimizations = 3

        # Background tasks
        self.monitoring_task: Optional[asyncio.Task] = None
        self.optimization_task: Optional[asyncio.Task] = None
        self.pattern_learning_task: Optional[asyncio.Task] = None

        # Statistics
        self.stats = {
            "patterns_learned": 0,
            "optimizations_completed": 0,
            "sleep_cycles": 0,
            "energy_saved": 0.0,
            "performance_improved": 0.0,
            "prediction_accuracy": 0.0,
        }

        self._init_database()
        self._setup_default_schedules()
        logger.info("🌙 Night-Cycle Intelligence initialized")

    def _init_database(self):
        """Initialize the night-cycle database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA journal_mode=WAL")

                # Activity patterns table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS activity_patterns (
                        pattern_id TEXT PRIMARY KEY,
                        time_start INTEGER NOT NULL,
                        time_end INTEGER NOT NULL,
                        expected_activity REAL NOT NULL,
                        confidence REAL NOT NULL,
                        sample_count INTEGER NOT NULL,
                        last_updated TEXT NOT NULL,
                        seasonal_factors TEXT NOT NULL
                    )
                """)

                # Activity history table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS activity_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpu_utilization REAL NOT NULL,
                        memory_utilization REAL NOT NULL,
                        disk_io_rate REAL NOT NULL,
                        network_io_rate REAL NOT NULL,
                        active_connections INTEGER NOT NULL,
                        task_queue_length INTEGER NOT NULL,
                        response_latency REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)

                # Optimization tasks table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS optimization_tasks (
                        task_id TEXT PRIMARY KEY,
                        task_type TEXT NOT NULL,
                        priority INTEGER NOT NULL,
                        estimated_duration REAL NOT NULL,
                        resource_requirements TEXT NOT NULL,
                        prerequisites TEXT NOT NULL,
                        max_activity_threshold REAL NOT NULL,
                        created_at TEXT NOT NULL,
                        scheduled_for TEXT,
                        completed_at TEXT,
                        result TEXT
                    )
                """)

                # Sleep schedules table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sleep_schedules (
                        schedule_id TEXT PRIMARY KEY,
                        sleep_mode TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        days_of_week TEXT NOT NULL,
                        wake_triggers TEXT NOT NULL,
                        max_sleep_duration REAL NOT NULL,
                        enabled BOOLEAN NOT NULL
                    )
                """)

                # Statistics table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS night_cycle_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stat_name TEXT NOT NULL,
                        stat_value REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.error(f"❌ Failed to initialize night-cycle database: {e}")
            raise

    def _setup_default_schedules(self):
        """Setup default sleep schedules."""
        # Default night-time deep sleep schedule
        night_schedule = SleepSchedule(
            schedule_id="default_night",
            sleep_mode=SleepMode.DEEP_SLEEP,
            start_time="02:00",
            end_time="06:00",
            days_of_week=[0, 1, 2, 3, 4, 5, 6],  # Every day
            wake_triggers=["emergency_alert", "user_activity", "scheduled_task"],
            max_sleep_duration=4.0,  # 4 hours max
            enabled=True,
        )

        # Weekend extended optimization
        weekend_schedule = SleepSchedule(
            schedule_id="weekend_extended",
            sleep_mode=SleepMode.LIGHT_SLEEP,
            start_time="00:00",
            end_time="08:00",
            days_of_week=[5, 6],  # Saturday, Sunday
            wake_triggers=["user_activity", "scheduled_task"],
            max_sleep_duration=8.0,
            enabled=True,
        )

        self.sleep_schedules = [night_schedule, weekend_schedule]

        # Default wake triggers
        self.wake_triggers = {
            "emergency_alert": False,
            "user_activity": False,
            "scheduled_task": False,
            "resource_threshold": False,
            "external_request": False,
        }

    async def start_intelligence(self):
        """Start the night-cycle intelligence system."""
        if self.intelligence_active:
            logger.warning("Night-cycle intelligence already active")
            return

        try:
            # Load existing patterns and tasks
            await self._load_patterns()
            await self._load_optimization_tasks()

            # Start background tasks
            self.intelligence_active = True
            self.monitoring_task = asyncio.create_task(self._activity_monitoring_loop())
            self.optimization_task = asyncio.create_task(self._optimization_scheduler_loop())
            self.pattern_learning_task = asyncio.create_task(self._pattern_learning_loop())

            logger.info("🌙 Night-cycle intelligence started")

        except Exception as e:
            logger.error(f"❌ Failed to start night-cycle intelligence: {e}")
            raise

    async def stop_intelligence(self):
        """Stop the night-cycle intelligence system."""
        if not self.intelligence_active:
            return

        self.intelligence_active = False

        # Stop background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.optimization_task:
            self.optimization_task.cancel()
        if self.pattern_learning_task:
            self.pattern_learning_task.cancel()

        # Wake system if in sleep mode
        if self.current_sleep_mode != SleepMode.AWAKE:
            await self.wake_system("shutdown")

        logger.info("🌙 Night-cycle intelligence stopped")

    async def record_activity_sample(self, resource_profile: ResourceProfile):
        """Record a new activity sample for pattern learning."""
        try:
            # Add to history
            self.activity_history.append(resource_profile)

            # Limit history size
            if len(self.activity_history) > self.pattern_learning_window * 12:  # 5-min samples
                self.activity_history = self.activity_history[-self.pattern_learning_window * 12 :]

            # Store in database
            await self._store_activity_sample(resource_profile)

            # Update current activity period
            await self._update_activity_period(resource_profile)

        except Exception as e:
            logger.error(f"❌ Error recording activity sample: {e}")

    async def schedule_optimization_task(self, task: OptimizationTask):
        """Schedule a new optimization task."""
        try:
            # Add to queue
            self.optimization_queue.append(task)

            # Sort by priority
            self.optimization_queue.sort(key=lambda t: t.priority, reverse=True)

            # Store in database
            await self._store_optimization_task(task)

            logger.info(
                f"📋 Optimization task scheduled: {task.task_type} (priority: {task.priority})"
            )

        except Exception as e:
            logger.error(f"❌ Error scheduling optimization task: {e}")

    async def predict_next_low_activity_window(self) -> Optional[Tuple[datetime, datetime]]:
        """Predict the next suitable window for optimization tasks."""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour

            # Look for patterns in the next 24 hours
            for hour_offset in range(1, 25):
                check_hour = (current_hour + hour_offset) % 24
                pattern_id = f"hour_{check_hour:02d}"

                pattern = self.activity_patterns.get(pattern_id)
                if pattern and pattern.expected_activity < 0.3:  # Low activity threshold
                    # Found a low-activity period
                    start_time = current_time + timedelta(hours=hour_offset)
                    start_time = start_time.replace(minute=0, second=0, microsecond=0)

                    # Find the end of the low-activity period
                    end_hour = check_hour
                    for next_hour_offset in range(1, 12):  # Look up to 12 hours ahead
                        next_hour = (check_hour + next_hour_offset) % 24
                        next_pattern_id = f"hour_{next_hour:02d}"
                        next_pattern = self.activity_patterns.get(next_pattern_id)

                        if not next_pattern or next_pattern.expected_activity >= 0.3:
                            break
                        end_hour = next_hour

                    end_time = start_time + timedelta(hours=(end_hour - check_hour) % 24 + 1)

                    # Ensure minimum window duration
                    if (end_time - start_time).total_seconds() >= self.min_optimization_window * 60:
                        return start_time, end_time

            return None

        except Exception as e:
            logger.error(f"❌ Error predicting low-activity window: {e}")
            return None

    async def enter_sleep_mode(self, sleep_mode: SleepMode, reason: str = "scheduled"):
        """Enter specified sleep mode."""
        try:
            if self.current_sleep_mode == sleep_mode:
                return

            old_mode = self.current_sleep_mode
            self.current_sleep_mode = sleep_mode

            # Execute sleep mode actions
            await self._execute_sleep_mode_actions(sleep_mode, reason)

            self.stats["sleep_cycles"] += 1

            logger.info(f"😴 Entered sleep mode: {old_mode.value} → {sleep_mode.value} ({reason})")

        except Exception as e:
            logger.error(f"❌ Error entering sleep mode: {e}")

    async def wake_system(self, trigger: str):
        """Wake the system from sleep mode."""
        try:
            if self.current_sleep_mode == SleepMode.AWAKE:
                return

            old_mode = self.current_sleep_mode
            self.current_sleep_mode = SleepMode.AWAKE

            # Execute wake actions
            await self._execute_wake_actions(old_mode, trigger)

            # Reset wake triggers
            self.wake_triggers = {k: False for k in self.wake_triggers}

            logger.info(f"⏰ System awakened: {old_mode.value} → awake (trigger: {trigger})")

        except Exception as e:
            logger.error(f"❌ Error waking system: {e}")

    async def trigger_wake_event(self, trigger: str, metadata: Optional[Dict[str, Any]] = None):
        """Trigger a wake event."""
        if trigger in self.wake_triggers:
            self.wake_triggers[trigger] = True

            if self.current_sleep_mode != SleepMode.AWAKE:
                await self.wake_system(trigger)

            logger.info(f"🔔 Wake trigger activated: {trigger}")

    def get_intelligence_status(self) -> Dict[str, Any]:
        """Get current night-cycle intelligence status."""
        return {
            "intelligence_active": self.intelligence_active,
            "current_activity_period": self.current_activity_period.value,
            "current_sleep_mode": self.current_sleep_mode.value,
            "patterns_learned": len(self.activity_patterns),
            "optimization_queue_length": len(self.optimization_queue),
            "active_optimizations": len(self.active_optimizations),
            "completed_optimizations": len(self.completed_optimizations),
            "sleep_schedules": len(self.sleep_schedules),
            "wake_triggers": self.wake_triggers.copy(),
            "stats": self.stats.copy(),
        }

    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get recommendations for optimization tasks."""
        try:
            recommendations = []

            # Predict next optimization window
            window = await self.predict_next_low_activity_window()

            if window:
                start_time, end_time = window
                duration_hours = (end_time - start_time).total_seconds() / 3600

                recommendations.append(
                    {
                        "type": "optimization_window",
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat(),
                        "duration_hours": duration_hours,
                        "confidence": 0.8,  # Could be calculated from pattern confidence
                        "suggested_tasks": [task.task_type for task in self.optimization_queue[:5]],
                    }
                )

            # Resource optimization recommendations
            if self.activity_history:
                recent_profile = self.activity_history[-1]

                if recent_profile.cpu_utilization < 0.3:
                    recommendations.append(
                        {
                            "type": "cpu_optimization",
                            "description": "Low CPU usage detected - good time for CPU-intensive optimizations",
                            "confidence": 0.9,
                            "suggested_actions": [
                                "index_rebuild",
                                "cache_warming",
                                "data_compression",
                            ],
                        }
                    )

                if recent_profile.memory_utilization < 0.5:
                    recommendations.append(
                        {
                            "type": "memory_optimization",
                            "description": "Memory available for optimization tasks",
                            "confidence": 0.8,
                            "suggested_actions": ["memory_defragmentation", "cache_optimization"],
                        }
                    )

            return recommendations

        except Exception as e:
            logger.error(f"❌ Error getting optimization recommendations: {e}")
            return []

    # Private methods

    async def _activity_monitoring_loop(self):
        """Background loop for activity monitoring."""
        try:
            while self.intelligence_active:
                await self._collect_activity_sample()
                await self._check_sleep_schedules()
                await asyncio.sleep(self.activity_sampling_interval)

        except asyncio.CancelledError:
            logger.info("Activity monitoring loop cancelled")
        except Exception as e:
            logger.error(f"❌ Activity monitoring loop error: {e}")

    async def _optimization_scheduler_loop(self):
        """Background loop for optimization scheduling."""
        try:
            while self.intelligence_active:
                await self._process_optimization_queue()
                await self._check_optimization_completion()
                await asyncio.sleep(self.optimization_check_interval)

        except asyncio.CancelledError:
            logger.info("Optimization scheduler loop cancelled")
        except Exception as e:
            logger.error(f"❌ Optimization scheduler loop error: {e}")

    async def _pattern_learning_loop(self):
        """Background loop for pattern learning."""
        try:
            while self.intelligence_active:
                await self._update_activity_patterns()
                await self._evaluate_prediction_accuracy()
                await asyncio.sleep(3600.0)  # Update patterns every hour

        except asyncio.CancelledError:
            logger.info("Pattern learning loop cancelled")
        except Exception as e:
            logger.error(f"❌ Pattern learning loop error: {e}")

    async def _collect_activity_sample(self):
        """Collect current activity sample."""
        try:
            # Simulate collecting resource metrics
            # In real implementation, this would gather actual system metrics
            current_time = datetime.now()

            # Generate realistic activity patterns with circadian rhythm
            hour = current_time.hour

            # Base activity follows circadian pattern
            base_activity = 0.5 + 0.3 * np.sin(2 * np.pi * (hour - 6) / 24)
            base_activity = max(0.1, min(0.9, base_activity))

            # Add some randomness
            noise = np.random.normal(0, 0.1)
            activity_level = max(0.0, min(1.0, base_activity + noise))

            # Create resource profile
            profile = ResourceProfile(
                cpu_utilization=activity_level * 0.8 + np.random.normal(0, 0.05),
                memory_utilization=0.4 + activity_level * 0.3 + np.random.normal(0, 0.02),
                disk_io_rate=activity_level * 100 + np.random.normal(0, 10),
                network_io_rate=activity_level * 50 + np.random.normal(0, 5),
                active_connections=int(activity_level * 20 + np.random.normal(0, 2)),
                task_queue_length=int(activity_level * 10 + np.random.normal(0, 1)),
                response_latency=50 + activity_level * 100 + np.random.normal(0, 10),
                timestamp=current_time.isoformat(),
            )

            await self.record_activity_sample(profile)

        except Exception as e:
            logger.error(f"❌ Error collecting activity sample: {e}")

    async def _update_activity_period(self, profile: ResourceProfile):
        """Update current activity period based on resource profile."""
        try:
            # Calculate overall activity level
            activity_score = (
                profile.cpu_utilization * 0.3
                + profile.memory_utilization * 0.2
                + min(profile.disk_io_rate / 100, 1.0) * 0.2
                + min(profile.network_io_rate / 50, 1.0) * 0.2
                + min(profile.active_connections / 20, 1.0) * 0.1
            )

            # Determine activity period
            if activity_score >= 0.8:
                new_period = ActivityPeriod.PEAK
            elif activity_score >= 0.6:
                new_period = ActivityPeriod.MODERATE
            elif activity_score >= 0.3:
                new_period = ActivityPeriod.LOW
            elif activity_score >= 0.1:
                new_period = ActivityPeriod.NIGHT
            else:
                new_period = ActivityPeriod.DORMANT

            if new_period != self.current_activity_period:
                old_period = self.current_activity_period
                self.current_activity_period = new_period
                logger.debug(f"🌅 Activity period changed: {old_period.value} → {new_period.value}")

        except Exception as e:
            logger.error(f"❌ Error updating activity period: {e}")

    async def _check_sleep_schedules(self):
        """Check if any sleep schedules should be activated."""
        try:
            current_time = datetime.now()
            current_weekday = current_time.weekday()
            current_time_str = current_time.strftime("%H:%M")

            for schedule in self.sleep_schedules:
                if not schedule.enabled:
                    continue

                if current_weekday not in schedule.days_of_week:
                    continue

                # Check if current time is within sleep window
                if schedule.start_time <= current_time_str <= schedule.end_time:
                    if self.current_sleep_mode == SleepMode.AWAKE:
                        await self.enter_sleep_mode(schedule.sleep_mode, "scheduled")

                    # Check wake time
                    elif (
                        current_time_str == schedule.end_time
                        and self.current_sleep_mode != SleepMode.AWAKE
                    ):
                        await self.wake_system("scheduled_wake")

        except Exception as e:
            logger.error(f"❌ Error checking sleep schedules: {e}")

    async def _process_optimization_queue(self):
        """Process pending optimization tasks."""
        try:
            if len(self.active_optimizations) >= self.max_concurrent_optimizations:
                return

            # Check if current activity allows optimization
            if self.current_activity_period in [ActivityPeriod.PEAK, ActivityPeriod.MODERATE]:
                return

            # Process queue
            while (
                self.optimization_queue
                and len(self.active_optimizations) < self.max_concurrent_optimizations
            ):
                task = self.optimization_queue.pop(0)

                # Check if prerequisites are met
                if not await self._check_task_prerequisites(task):
                    # Re-queue for later
                    self.optimization_queue.append(task)
                    break

                # Start the optimization task
                await self._start_optimization_task(task)

        except Exception as e:
            logger.error(f"❌ Error processing optimization queue: {e}")

    async def _start_optimization_task(self, task: OptimizationTask):
        """Start an optimization task."""
        try:
            # Move to active optimizations
            self.active_optimizations[task.task_id] = task

            # Simulate task execution (in real implementation, this would execute actual optimization)
            logger.info(f"🔧 Starting optimization: {task.task_type}")

            # Update database
            await self._update_optimization_task(task, scheduled_for=datetime.now().isoformat())

        except Exception as e:
            logger.error(f"❌ Error starting optimization task {task.task_id}: {e}")

    async def _check_optimization_completion(self):
        """Check for completed optimization tasks."""
        try:
            completed_tasks = []

            for task_id, _task in self.active_optimizations.items():
                # Simulate task completion (random for demo)
                if np.random.random() < 0.1:  # 10% chance per check
                    completed_tasks.append(task_id)

            # Process completed tasks
            for task_id in completed_tasks:
                task = self.active_optimizations.pop(task_id)

                # Mark as completed
                task.completed_at = datetime.now().isoformat()
                task.result = {
                    "status": "completed",
                    "performance_improvement": np.random.uniform(0.05, 0.25),
                    "resources_saved": np.random.uniform(0.02, 0.15),
                }

                self.completed_optimizations.append(task)
                self.stats["optimizations_completed"] += 1

                # Update database
                await self._update_optimization_task(
                    task, completed_at=task.completed_at, result=json.dumps(task.result)
                )

                logger.info(f"✅ Optimization completed: {task.task_type}")

        except Exception as e:
            logger.error(f"❌ Error checking optimization completion: {e}")

    async def _check_task_prerequisites(self, task: OptimizationTask) -> bool:
        """Check if task prerequisites are met."""
        for prereq_id in task.prerequisites:
            # Check if prerequisite task is completed
            prereq_completed = any(t.task_id == prereq_id for t in self.completed_optimizations)
            if not prereq_completed:
                return False

        return True

    async def _execute_sleep_mode_actions(self, sleep_mode: SleepMode, reason: str):
        """Execute actions for entering sleep mode."""
        try:
            if sleep_mode == SleepMode.LIGHT_SLEEP:
                # Reduce non-essential services
                logger.info("😴 Light sleep: Reducing non-essential services")
                # In real implementation: stop background tasks, reduce polling frequencies

            elif sleep_mode == SleepMode.DEEP_SLEEP:
                # Minimal essential services only
                logger.info("😴 Deep sleep: Minimal essential services")
                # In real implementation: stop most services, keep only critical monitoring

            elif sleep_mode == SleepMode.HIBERNATION:
                # Maximum power savings
                logger.info("😴 Hibernation: Maximum power savings")
                # In real implementation: persist state, stop almost everything

        except Exception as e:
            logger.error(f"❌ Error executing sleep mode actions: {e}")

    async def _execute_wake_actions(self, old_mode: SleepMode, trigger: str):
        """Execute actions for waking from sleep mode."""
        try:
            if old_mode == SleepMode.LIGHT_SLEEP:
                logger.info("⏰ Waking from light sleep: Restoring services")
                # In real implementation: restart background services

            elif old_mode == SleepMode.DEEP_SLEEP:
                logger.info("⏰ Waking from deep sleep: Full service restoration")
                # In real implementation: restart all services, restore full operation

            elif old_mode == SleepMode.HIBERNATION:
                logger.info("⏰ Waking from hibernation: Full system restoration")
                # In real implementation: restore persisted state, full restart

        except Exception as e:
            logger.error(f"❌ Error executing wake actions: {e}")

    async def _update_activity_patterns(self):
        """Update activity patterns based on historical data."""
        try:
            if len(self.activity_history) < 24:  # Need at least 24 samples
                return

            # Group samples by hour of day
            hourly_data: Dict[int, List[float]] = {}

            for profile in self.activity_history[-7 * 24 * 12 :]:  # Last 7 days
                timestamp = datetime.fromisoformat(profile.timestamp)
                hour = timestamp.hour

                # Calculate activity score
                activity_score = (
                    profile.cpu_utilization * 0.3
                    + profile.memory_utilization * 0.2
                    + min(profile.disk_io_rate / 100, 1.0) * 0.2
                    + min(profile.network_io_rate / 50, 1.0) * 0.2
                    + min(profile.active_connections / 20, 1.0) * 0.1
                )

                if hour not in hourly_data:
                    hourly_data[hour] = []
                hourly_data[hour].append(activity_score)

            # Update patterns for each hour
            for hour, scores in hourly_data.items():
                if len(scores) < 3:  # Need minimum samples
                    continue

                pattern_id = f"hour_{hour:02d}"

                mean_activity = np.mean(scores)
                confidence = min(1.0, len(scores) / 21)  # 3 samples per day for 7 days

                pattern = ActivityPattern(
                    pattern_id=pattern_id,
                    time_range=(hour, (hour + 1) % 24),
                    expected_activity=float(mean_activity),
                    confidence=confidence,
                    sample_count=len(scores),
                    last_updated=datetime.now().isoformat(),
                    seasonal_factors={},  # Could add day-of-week factors
                )

                self.activity_patterns[pattern_id] = pattern
                await self._store_activity_pattern(pattern)

            self.stats["patterns_learned"] = len(self.activity_patterns)

        except Exception as e:
            logger.error(f"❌ Error updating activity patterns: {e}")

    async def _evaluate_prediction_accuracy(self):
        """Evaluate the accuracy of activity predictions."""
        try:
            if not self.activity_patterns or len(self.activity_history) < 12:
                return

            # Check recent predictions vs actual activity
            recent_samples = self.activity_history[-12:]  # Last hour
            correct_predictions = 0
            total_predictions = 0

            for profile in recent_samples:
                timestamp = datetime.fromisoformat(profile.timestamp)
                hour = timestamp.hour
                pattern_id = f"hour_{hour:02d}"

                pattern = self.activity_patterns.get(pattern_id)
                if not pattern:
                    continue

                # Calculate actual activity
                actual_activity = (
                    profile.cpu_utilization * 0.3
                    + profile.memory_utilization * 0.2
                    + min(profile.disk_io_rate / 100, 1.0) * 0.2
                    + min(profile.network_io_rate / 50, 1.0) * 0.2
                    + min(profile.active_connections / 20, 1.0) * 0.1
                )

                # Check if prediction was reasonably accurate (within 0.2)
                if abs(actual_activity - pattern.expected_activity) < 0.2:
                    correct_predictions += 1

                total_predictions += 1

            if total_predictions > 0:
                accuracy = correct_predictions / total_predictions
                self.stats["prediction_accuracy"] = accuracy

        except Exception as e:
            logger.error(f"❌ Error evaluating prediction accuracy: {e}")

    # Database operations

    async def _store_activity_sample(self, profile: ResourceProfile):
        """Store activity sample in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO activity_history
                    (cpu_utilization, memory_utilization, disk_io_rate, network_io_rate,
                     active_connections, task_queue_length, response_latency, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.cpu_utilization,
                        profile.memory_utilization,
                        profile.disk_io_rate,
                        profile.network_io_rate,
                        profile.active_connections,
                        profile.task_queue_length,
                        profile.response_latency,
                        profile.timestamp,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error storing activity sample: {e}")

    async def _store_activity_pattern(self, pattern: ActivityPattern):
        """Store activity pattern in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO activity_patterns
                    (pattern_id, time_start, time_end, expected_activity, confidence,
                     sample_count, last_updated, seasonal_factors)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        pattern.pattern_id,
                        pattern.time_range[0],
                        pattern.time_range[1],
                        pattern.expected_activity,
                        pattern.confidence,
                        pattern.sample_count,
                        pattern.last_updated,
                        json.dumps(pattern.seasonal_factors),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error storing activity pattern: {e}")

    async def _store_optimization_task(self, task: OptimizationTask):
        """Store optimization task in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO optimization_tasks
                    (task_id, task_type, priority, estimated_duration, resource_requirements,
                     prerequisites, max_activity_threshold, created_at, scheduled_for,
                     completed_at, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        task.task_id,
                        task.task_type,
                        task.priority,
                        task.estimated_duration,
                        json.dumps(task.resource_requirements),
                        json.dumps(task.prerequisites),
                        task.max_activity_threshold,
                        task.created_at,
                        task.scheduled_for,
                        task.completed_at,
                        json.dumps(task.result) if task.result else None,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error storing optimization task: {e}")

    async def _update_optimization_task(self, task: OptimizationTask, **kwargs):
        """Update optimization task in database."""
        try:
            update_fields = []
            values = []

            for field, value in kwargs.items():
                update_fields.append(f"{field} = ?")
                values.append(value)

            if not update_fields:
                return

            values.append(task.task_id)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"""
                    UPDATE optimization_tasks
                    SET {", ".join(update_fields)}
                    WHERE task_id = ?
                """,
                    values,
                )
                conn.commit()

        except Exception as e:
            logger.error(f"❌ Error updating optimization task: {e}")

    async def _load_patterns(self):
        """Load activity patterns from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM activity_patterns")
                rows = cursor.fetchall()

                for row in rows:
                    pattern = ActivityPattern(
                        pattern_id=row[0],
                        time_range=(row[1], row[2]),
                        expected_activity=row[3],
                        confidence=row[4],
                        sample_count=row[5],
                        last_updated=row[6],
                        seasonal_factors=json.loads(row[7]),
                    )

                    self.activity_patterns[pattern.pattern_id] = pattern

                logger.info(f"🌙 Loaded {len(self.activity_patterns)} activity patterns")

        except Exception as e:
            logger.error(f"❌ Error loading patterns: {e}")

    async def _load_optimization_tasks(self):
        """Load optimization tasks from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM optimization_tasks
                    WHERE completed_at IS NULL
                    ORDER BY priority DESC
                """)
                rows = cursor.fetchall()

                for row in rows:
                    task = OptimizationTask(
                        task_id=row[0],
                        task_type=row[1],
                        priority=row[2],
                        estimated_duration=row[3],
                        resource_requirements=json.loads(row[4]),
                        prerequisites=json.loads(row[5]),
                        max_activity_threshold=row[6],
                        created_at=row[7],
                        scheduled_for=row[8],
                        completed_at=row[9],
                        result=json.loads(row[10]) if row[10] else None,
                    )

                    if task.scheduled_for:
                        self.active_optimizations[task.task_id] = task
                    else:
                        self.optimization_queue.append(task)

                logger.info(f"🌙 Loaded {len(self.optimization_queue)} pending optimization tasks")

        except Exception as e:
            logger.error(f"❌ Error loading optimization tasks: {e}")


# Global instance for easy access
_night_cycle_intelligence: Optional[NightCycleIntelligence] = None
_intelligence_lock = threading.Lock()


def get_night_cycle_intelligence() -> NightCycleIntelligence:
    """Get the global night-cycle intelligence instance."""
    global _night_cycle_intelligence

    if _night_cycle_intelligence is None:
        with _intelligence_lock:
            if _night_cycle_intelligence is None:
                _night_cycle_intelligence = NightCycleIntelligence()

    return _night_cycle_intelligence
