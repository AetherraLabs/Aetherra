#!/usr/bin/env python3
"""
Standalone test runner for ScriptServiceLogging module.

Runs comprehensive logging and telemetry tests without Aetherra engine init.

Test Categories:
  - Log event creation and JSON export (2 tests)
  - Timeline tracking and export (3 tests)
  - Service metrics aggregation (8 tests)
  - Metrics snapshot (1 test)
  - Logger initialization and logging (10 tests)
  - Export formats (3 tests)

Total: 27 comprehensive tests
"""

import sys
import os
import tempfile
import json
import time
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

# Import modules directly (no engine init)
from Aetherra.aetherra_core.script_service.script_service_logging import (
    LogEvent,
    TimelineEntry,
    ExecutionTimeline,
    ServiceMetrics,
    MetricsSnapshot,
    ScriptServiceLogger,
    EventLevel,
    ExecutionPhase,
)


class TestRunner:
    """Simple test runner with colored output."""

    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []

    def run_test(self, name, test_func):
        """Run a single test."""
        self.total += 1
        try:
            test_func()
            self.passed += 1
            print(f"  ✓ test_{self.total:02d}: {name}")
            return True
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"  ✗ test_{self.total:02d}: {name}")
            print(f"      AssertionError: {e}")
            return False
        except Exception as e:
            self.failed += 1
            self.errors.append((name, f"{type(e).__name__}: {e}"))
            print(f"  ✗ test_{self.total:02d}: {name}")
            print(f"      {type(e).__name__}: {e}")
            return False

    def summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print(f"Tests run: {self.total}")
        print(f"Passed:    {self.passed}")
        print(f"Failed:    {self.failed}")
        if self.failed > 0:
            print(f"\nFailures:")
            for name, error in self.errors:
                print(f"  - {name}: {error[:100]}")
        print(f"{'='*60}\n")
        return self.failed == 0


def test_create_log_event():
    """Test creating log event."""
    event = LogEvent(
        timestamp="2024-01-01T10:00:00",
        phase=ExecutionPhase.EXECUTING,
        level=EventLevel.INFO,
        message="Test event",
    )
    assert event.message == "Test event"
    assert event.phase == ExecutionPhase.EXECUTING


def test_log_event_to_json():
    """Test converting log event to JSON."""
    event = LogEvent(
        timestamp="2024-01-01T10:00:00",
        phase=ExecutionPhase.EXECUTING,
        level=EventLevel.INFO,
        message="Test event",
        step_name="step1",
        duration=0.5,
    )
    json_str = event.to_json()
    data = json.loads(json_str)
    assert data["message"] == "Test event"
    assert data["phase"] == "executing"


def test_create_timeline():
    """Test creating execution timeline."""
    timeline = ExecutionTimeline()
    assert len(timeline.entries) == 0


def test_record_event():
    """Test recording event in timeline."""
    timeline = ExecutionTimeline()
    timeline.record("test_event", duration=0.5)
    assert len(timeline.entries) == 1
    assert timeline.entries[0].event == "test_event"


def test_timeline_elapsed():
    """Test timeline elapsed time."""
    timeline = ExecutionTimeline()
    time.sleep(0.05)
    elapsed = timeline.get_elapsed()
    assert elapsed > 0.03


def test_timeline_export():
    """Test exporting timeline."""
    timeline = ExecutionTimeline()
    timeline.record("event1", duration=0.5)
    timeline.record("event2", duration=0.3)
    export = timeline.export()
    assert "total_elapsed" in export
    assert "events" in export
    assert len(export["events"]) == 2


def test_create_metrics():
    """Test creating service metrics."""
    metrics = ServiceMetrics()
    assert len(metrics.step_durations) == 0
    assert len(metrics.errors) == 0


def test_record_step():
    """Test recording step duration."""
    metrics = ServiceMetrics()
    metrics.record_step(0.5)
    metrics.record_step(0.3)
    assert len(metrics.step_durations) == 2


def test_average_step_duration():
    """Test average step duration."""
    metrics = ServiceMetrics()
    metrics.record_step(0.5)
    metrics.record_step(0.3)
    avg = metrics.get_average_step_duration()
    assert abs(avg - 0.4) < 0.01


def test_record_error():
    """Test recording error."""
    metrics = ServiceMetrics()
    metrics.record_error("Error 1")
    metrics.record_error("Error 2")
    assert len(metrics.errors) == 2


def test_record_warning():
    """Test recording warning."""
    metrics = ServiceMetrics()
    metrics.record_warning("Warning 1")
    assert len(metrics.warnings) == 1


def test_custom_metrics():
    """Test custom metrics."""
    metrics = ServiceMetrics()
    metrics.set_custom("cache_hits", 150)
    metrics.set_custom("cache_misses", 45)
    assert metrics.custom_metrics["cache_hits"] == 150


def test_success_rate():
    """Test success rate calculation."""
    metrics = ServiceMetrics()
    metrics.record_error("Error 1")
    metrics.record_error("Error 2")
    success_rate = metrics.get_success_rate(10)
    assert success_rate == 80.0


def test_metrics_to_dict():
    """Test metrics dictionary export."""
    metrics = ServiceMetrics()
    metrics.record_step(0.5)
    metrics.record_error("Error 1")
    data = metrics.to_dict()
    assert "step_durations" in data
    assert "error_count" in data
    assert data["error_count"] == 1


def test_create_snapshot():
    """Test creating metrics snapshot."""
    snapshot = MetricsSnapshot(
        timestamp="2024-01-01T10:00:00",
        phase=ExecutionPhase.COMPLETED,
        total_steps=10,
        completed_steps=10,
        elapsed_time=5.0,
    )
    assert snapshot.total_steps == 10
    assert snapshot.phase == ExecutionPhase.COMPLETED


def test_logger_initialization():
    """Test logger initialization."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    assert logger.script_path == "/path/to/script.aether"
    assert logger.timeline is not None
    assert logger.metrics is not None


def test_log_execution_start():
    """Test logging execution start."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_execution_start()
    assert len(logger.events) == 1
    assert "Execution started" in logger.events[0].message


def test_log_parsing_complete():
    """Test logging parsing completion."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_parsing_complete(5)
    assert len(logger.events) == 1
    assert "Parsing complete" in logger.events[0].message


def test_log_validation_complete():
    """Test logging validation completion."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_validation_complete(True, 0)
    assert len(logger.events) == 1


def test_log_step_start():
    """Test logging step start."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_step_start("step1")
    assert len(logger.events) == 1
    assert logger.events[0].step_name == "step1"


def test_log_step_completed():
    """Test logging step completion."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_step_completed("step1", 0.5)
    assert len(logger.events) == 1
    assert logger.metrics.step_durations[0] == 0.5


def test_log_step_failed():
    """Test logging step failure."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_step_failed("step1", "Connection timeout", 2.0)
    assert len(logger.events) == 1
    assert len(logger.metrics.errors) == 1


def test_log_execution_complete():
    """Test logging execution completion."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_execution_complete(True, 3.5)
    assert len(logger.events) == 1
    assert "succeeded" in logger.events[0].message


def test_log_warning():
    """Test logging warning."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_warning("Test warning")
    assert len(logger.metrics.warnings) == 1


def test_log_error():
    """Test logging error."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_error("Test error")
    assert len(logger.metrics.errors) == 1


def test_get_metrics_snapshot():
    """Test getting metrics snapshot."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_step_completed("step1", 0.5)
    snapshot = logger.get_metrics_snapshot(total_steps=10, completed_steps=1)
    assert snapshot.total_steps == 10


def test_export_json():
    """Test exporting logs as JSON."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_execution_start()
    logger.log_step_start("step1")
    json_export = logger.export_json()
    data = json.loads(json_export)
    assert "script_path" in data
    assert "events" in data


def test_export_prometheus():
    """Test exporting metrics in Prometheus format."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.log_step_completed("step1", 0.5)
    prometheus_export = logger.export_prometheus()
    assert "# HELP" in prometheus_export
    assert "# TYPE" in prometheus_export
    assert "script_steps_total" in prometheus_export


def test_export_timeline():
    """Test exporting execution timeline."""
    logger = ScriptServiceLogger("/path/to/script.aether")
    logger.timeline.record("test_event", duration=0.5)
    timeline_export = logger.export_timeline()
    assert "total_elapsed" in timeline_export
    assert "events" in timeline_export


def test_write_logs():
    """Test writing logs to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ScriptServiceLogger("/path/to/script.aether", log_dir=tmpdir)
        logger.log_execution_start()
        logger.write_logs()

        log_files = list(Path(tmpdir).glob("*.json"))
        metrics_files = list(Path(tmpdir).glob("*.txt"))

        assert len(log_files) == 1
        assert len(metrics_files) == 1


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("ScriptServiceLogging - Standalone Test Suite")
    print("=" * 60 + "\n")

    runner = TestRunner()

    # Log event tests
    print("LogEvent Tests (2/27):")
    runner.run_test("Create log event", test_create_log_event)
    runner.run_test("Log event to JSON", test_log_event_to_json)

    # Timeline tests
    print("\nExecutionTimeline Tests (4/27):")
    runner.run_test("Create timeline", test_create_timeline)
    runner.run_test("Record event", test_record_event)
    runner.run_test("Timeline elapsed", test_timeline_elapsed)
    runner.run_test("Timeline export", test_timeline_export)

    # Metrics tests
    print("\nServiceMetrics Tests (8/27):")
    runner.run_test("Create metrics", test_create_metrics)
    runner.run_test("Record step", test_record_step)
    runner.run_test("Average step duration", test_average_step_duration)
    runner.run_test("Record error", test_record_error)
    runner.run_test("Record warning", test_record_warning)
    runner.run_test("Custom metrics", test_custom_metrics)
    runner.run_test("Success rate", test_success_rate)
    runner.run_test("Metrics to dict", test_metrics_to_dict)

    # Snapshot test
    print("\nMetricsSnapshot Tests (1/27):")
    runner.run_test("Create snapshot", test_create_snapshot)

    # Logger tests
    print("\nScriptServiceLogger Tests (12/27):")
    runner.run_test("Logger initialization", test_logger_initialization)
    runner.run_test("Log execution start", test_log_execution_start)
    runner.run_test("Log parsing complete", test_log_parsing_complete)
    runner.run_test("Log validation complete", test_log_validation_complete)
    runner.run_test("Log step start", test_log_step_start)
    runner.run_test("Log step completed", test_log_step_completed)
    runner.run_test("Log step failed", test_log_step_failed)
    runner.run_test("Log execution complete", test_log_execution_complete)
    runner.run_test("Log warning", test_log_warning)
    runner.run_test("Log error", test_log_error)
    runner.run_test("Get metrics snapshot", test_get_metrics_snapshot)
    runner.run_test("Write logs to file", test_write_logs)

    # Export tests
    print("\nExport Format Tests (3/27):")
    runner.run_test("Export JSON", test_export_json)
    runner.run_test("Export Prometheus", test_export_prometheus)
    runner.run_test("Export timeline", test_export_timeline)

    # Print summary
    success = runner.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
