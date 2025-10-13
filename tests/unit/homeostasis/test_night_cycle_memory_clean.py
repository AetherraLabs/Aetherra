"""Tests for Night-Cycle Intelligence Integration with in-memory database."""

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
    """Test activity pattern learning and sleep mode functionality."""
    # Use in-memory database to avoid Windows file locking issues
    nci = NightCycleIntelligence(db_path=":memory:")

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


@pytest.mark.asyncio
async def test_optimization_task_scheduling():
    """Test optimization task scheduling during low-activity periods."""
    # Use in-memory database to avoid Windows file locking issues
    nci = NightCycleIntelligence(db_path=":memory:")

    try:
        await nci.start_intelligence()

        # Add a low-activity pattern to allow optimization
        nci.activity_patterns["hour_02"] = ActivityPattern(
            pattern_id="hour_02",
            time_range=(2, 3),
            expected_activity=0.1,
            confidence=0.9,
            sample_count=10,
            last_updated=datetime.now().isoformat(),
            seasonal_factors={"monday": 1.0},
        )

        # Create and schedule an optimization task
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

        # Verify task was scheduled
        scheduled_tasks = nci.optimization_queue
        assert len(scheduled_tasks) == 1
        assert scheduled_tasks[0].task_id == "test_task"

        # Simulate optimization execution
        await nci._process_optimization_queue()

        # Verify task processing
        status = nci.get_intelligence_status()
        assert "optimization_queue_length" in status

    finally:
        await nci.stop_intelligence()
