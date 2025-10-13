#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors
"""
🧪 Night-Cycle Intelligence Integration Tests
============================================

Unit and integration tests for the NightCycleIntelligence module.
Simulates activity patterns, resource optimization, and sleep-mode transitions.

Author: Aetherra Labs
"""

import asyncio
import os
import tempfile
from datetime import datetime

import pytest

from Aetherra.homeostasis.night_cycle_integration import (
    ActivityPattern,
    NightCycleIntelligence,
    OptimizationTask,
    ResourceProfile,
    SleepMode,
)


@pytest.mark.asyncio
async def test_activity_pattern_learning_and_sleep_mode():
    # Use a temporary directory for SQLite DB compatibility
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_night_cycle.db")
        nci = NightCycleIntelligence(db_path=db_path)
        try:
            await nci.start_intelligence()

            # Simulate 48 hours of low activity (night)
            for _ in range(48):
                profile = ResourceProfile(
                    cpu_utilization=0.1,
                    memory_utilization=0.2,
                    disk_io_rate=10.0,
                    network_io_rate=5.0,
                    active_connections=1,
                    task_queue_length=0,
                    response_latency=50.0,
                    timestamp=(datetime.now()).isoformat(),
                )
                await nci.record_activity_sample(profile)

            # Force pattern update
            await nci._update_activity_patterns()
            status = nci.get_intelligence_status()
            assert status["patterns_learned"] > 0

            # Simulate entering sleep mode
            await nci.enter_sleep_mode(SleepMode.DEEP_SLEEP, reason="test")
            assert nci.current_sleep_mode == SleepMode.DEEP_SLEEP
            await nci.wake_system("test_wake")
            assert nci.current_sleep_mode == SleepMode.AWAKE

        finally:
            await nci.stop_intelligence()
            import sqlite3
            import time
            from contextlib import suppress

            # Force close any remaining SQLite connections
            with suppress(Exception):
                conn = sqlite3.connect(db_path)
                conn.close()

            # Try to remove SQLite auxiliary files
            with suppress(FileNotFoundError):
                os.remove(db_path + "-shm")
            with suppress(FileNotFoundError):
                os.remove(db_path + "-wal")

            time.sleep(0.2)  # Allow Windows to release SQLite file handles
            del nci


@pytest.mark.asyncio
async def test_optimization_task_scheduling():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_night_cycle.db")
        nci = NightCycleIntelligence(db_path=db_path)
        try:
            await nci.start_intelligence()

            # Add a low-activity pattern to allow optimization
            nci.activity_patterns["hour_02"] = ActivityPattern(
                pattern_id="hour_02",
                time_range=(2, 3),
                expected_activity=0.1,
                confidence=1.0,
                sample_count=10,
                last_updated=datetime.now().isoformat(),
                seasonal_factors={},
            )

            # Schedule an optimization task
            task = OptimizationTask(
                task_id="test_task",
                task_type="test_optimization",
                priority=5,
                estimated_duration=10.0,
                resource_requirements={"cpu": 0.1},
                prerequisites=[],
                max_activity_threshold=0.2,
                created_at=datetime.now().isoformat(),
                scheduled_for=None,
                completed_at=None,
                result=None,
            )
            await nci.schedule_optimization_task(task)
            assert len(nci.optimization_queue) == 1

            # Simulate low activity period
            nci.current_activity_period = nci.current_activity_period.NIGHT
            await nci._process_optimization_queue()
            assert len(nci.active_optimizations) == 1

        finally:
            await nci.stop_intelligence()
            import sqlite3
            import time
            from contextlib import suppress

            # Force close any remaining SQLite connections
            with suppress(Exception):
                conn = sqlite3.connect(db_path)
                conn.close()

            # Try to remove SQLite auxiliary files
            with suppress(FileNotFoundError):
                os.remove(db_path + "-shm")
            with suppress(FileNotFoundError):
                os.remove(db_path + "-wal")

            time.sleep(0.2)  # Allow Windows to release SQLite file handles
            del nci
