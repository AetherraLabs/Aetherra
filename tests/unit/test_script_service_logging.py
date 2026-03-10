"""
Unit tests for ScriptServiceLogging module.

Tests cover:
  - Log event creation and formatting
  - Timeline tracking
  - Metrics aggregation
  - Prometheus metrics export
  - JSON log export
  - File writing and export
"""

import unittest
import tempfile
import os
import json
from pathlib import Path


class TestLogEvent(unittest.TestCase):
    """Test LogEvent dataclass."""

    def test_create_log_event(self):
        """Test creating log event."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            LogEvent,
            EventLevel,
            ExecutionPhase,
        )

        event = LogEvent(
            timestamp="2024-01-01T10:00:00",
            phase=ExecutionPhase.EXECUTING,
            level=EventLevel.INFO,
            message="Test event",
        )

        self.assertEqual(event.message, "Test event")
        self.assertEqual(event.phase, ExecutionPhase.EXECUTING)

    def test_log_event_to_json(self):
        """Test converting log event to JSON."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            LogEvent,
            EventLevel,
            ExecutionPhase,
        )

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

        self.assertEqual(data["message"], "Test event")
        self.assertEqual(data["phase"], "executing")
        self.assertEqual(data["step_name"], "step1")


class TestTimelineEntry(unittest.TestCase):
    """Test TimelineEntry dataclass."""

    def test_create_timeline_entry(self):
        """Test creating timeline entry."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            TimelineEntry,
        )
        import time

        entry = TimelineEntry(
            timestamp=time.time(),
            event="test_event",
            duration=0.5,
        )

        self.assertEqual(entry.event, "test_event")
        self.assertEqual(entry.duration, 0.5)


class TestExecutionTimeline(unittest.TestCase):
    """Test ExecutionTimeline class."""

    def test_create_timeline(self):
        """Test creating execution timeline."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()

        self.assertEqual(len(timeline.entries), 0)

    def test_record_event(self):
        """Test recording event in timeline."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()
        timeline.record("test_event", duration=0.5)

        self.assertEqual(len(timeline.entries), 1)
        self.assertEqual(timeline.entries[0].event, "test_event")

    def test_timeline_elapsed(self):
        """Test timeline elapsed time."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )
        import time

        timeline = ExecutionTimeline()
        time.sleep(0.1)
        elapsed = timeline.get_elapsed()

        self.assertGreater(elapsed, 0.05)

    def test_timeline_export(self):
        """Test exporting timeline."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()
        timeline.record("event1", duration=0.5)
        timeline.record("event2", duration=0.3)

        export = timeline.export()

        self.assertIn("total_elapsed", export)
        self.assertIn("events", export)
        self.assertEqual(len(export["events"]), 2)


class TestServiceMetrics(unittest.TestCase):
    """Test ServiceMetrics class."""

    def test_create_metrics(self):
        """Test creating service metrics."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()

        self.assertEqual(len(metrics.step_durations), 0)
        self.assertEqual(len(metrics.errors), 0)

    def test_record_step(self):
        """Test recording step duration."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_step(0.3)

        self.assertEqual(len(metrics.step_durations), 2)

    def test_average_step_duration(self):
        """Test average step duration."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_step(0.3)

        avg = metrics.get_average_step_duration()
        self.assertAlmostEqual(avg, 0.4)

    def test_record_error(self):
        """Test recording error."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_error("Error 1")
        metrics.record_error("Error 2")

        self.assertEqual(len(metrics.errors), 2)

    def test_record_warning(self):
        """Test recording warning."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_warning("Warning 1")

        self.assertEqual(len(metrics.warnings), 1)

    def test_custom_metrics(self):
        """Test custom metrics."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.set_custom("cache_hits", 150)
        metrics.set_custom("cache_misses", 45)

        self.assertEqual(metrics.custom_metrics["cache_hits"], 150)

    def test_success_rate(self):
        """Test success rate calculation."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_error("Error 1")
        metrics.record_error("Error 2")

        # 8 successful out of 10 total = 80%
        success_rate = metrics.get_success_rate(10)
        self.assertEqual(success_rate, 80.0)

    def test_metrics_to_dict(self):
        """Test metrics dictionary export."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_error("Error 1")

        data = metrics.to_dict()

        self.assertIn("step_durations", data)
        self.assertIn("error_count", data)
        self.assertEqual(data["error_count"], 1)


class TestMetricsSnapshot(unittest.TestCase):
    """Test MetricsSnapshot dataclass."""

    def test_create_snapshot(self):
        """Test creating metrics snapshot."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            MetricsSnapshot,
            ExecutionPhase,
        )

        snapshot = MetricsSnapshot(
            timestamp="2024-01-01T10:00:00",
            phase=ExecutionPhase.COMPLETED,
            total_steps=10,
            completed_steps=10,
            elapsed_time=5.0,
        )

        self.assertEqual(snapshot.total_steps, 10)
        self.assertEqual(snapshot.phase, ExecutionPhase.COMPLETED)


class TestScriptServiceLogger(unittest.TestCase):
    """Test ScriptServiceLogger class."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")

        self.assertEqual(logger.script_path, "/path/to/script.aether")
        self.assertIsNotNone(logger.timeline)
        self.assertIsNotNone(logger.metrics)

    def test_log_execution_start(self):
        """Test logging execution start."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_start()

        self.assertEqual(len(logger.events), 1)
        self.assertIn("Execution started", logger.events[0].message)

    def test_log_parsing_complete(self):
        """Test logging parsing completion."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_parsing_complete(5)

        self.assertEqual(len(logger.events), 1)
        self.assertIn("Parsing complete", logger.events[0].message)

    def test_log_validation_complete(self):
        """Test logging validation completion."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_validation_complete(True, 0)

        self.assertEqual(len(logger.events), 1)
        self.assertIn("valid", logger.events[0].message)

    def test_log_step_start(self):
        """Test logging step start."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_start("step1")

        self.assertEqual(len(logger.events), 1)
        self.assertEqual(logger.events[0].step_name, "step1")

    def test_log_step_completed(self):
        """Test logging step completion."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)

        self.assertEqual(len(logger.events), 1)
        self.assertEqual(logger.metrics.step_durations[0], 0.5)

    def test_log_step_failed(self):
        """Test logging step failure."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_failed("step1", "Connection timeout", 2.0)

        self.assertEqual(len(logger.events), 1)
        self.assertEqual(len(logger.metrics.errors), 1)

    def test_log_execution_complete(self):
        """Test logging execution completion."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_complete(True, 3.5)

        self.assertEqual(len(logger.events), 1)
        self.assertIn("succeeded", logger.events[0].message)

    def test_log_warning(self):
        """Test logging warning."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_warning("Test warning")

        self.assertEqual(len(logger.metrics.warnings), 1)

    def test_log_error(self):
        """Test logging error."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_error("Test error")

        self.assertEqual(len(logger.metrics.errors), 1)

    def test_get_metrics_snapshot(self):
        """Test getting metrics snapshot."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)
        snapshot = logger.get_metrics_snapshot(total_steps=10, completed_steps=1)

        self.assertEqual(snapshot.total_steps, 10)
        self.assertEqual(snapshot.completed_steps, 1)

    def test_export_json(self):
        """Test exporting logs as JSON."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_start()
        logger.log_step_start("step1")

        json_export = logger.export_json()
        data = json.loads(json_export)

        self.assertIn("script_path", data)
        self.assertIn("events", data)
        self.assertIn("metrics", data)
        self.assertIn("timeline", data)

    def test_export_prometheus(self):
        """Test exporting metrics in Prometheus format."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)

        prometheus_export = logger.export_prometheus()

        self.assertIn("# HELP", prometheus_export)
        self.assertIn("# TYPE", prometheus_export)
        self.assertIn("script_steps_total", prometheus_export)
        self.assertIn("script_errors_total", prometheus_export)

    def test_export_timeline(self):
        """Test exporting execution timeline."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.timeline.record("test_event", duration=0.5)

        timeline_export = logger.export_timeline()

        self.assertIn("total_elapsed", timeline_export)
        self.assertIn("events", timeline_export)

    def test_write_logs(self):
        """Test writing logs to file."""
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            logger = ScriptServiceLogger("/path/to/script.aether", log_dir=tmpdir)
            logger.log_execution_start()
            logger.write_logs()

            # Check files were created
            log_files = list(Path(tmpdir).glob("*.json"))
            metrics_files = list(Path(tmpdir).glob("*.txt"))

            self.assertEqual(len(log_files), 1)
            self.assertEqual(len(metrics_files), 1)


if __name__ == "__main__":
    unittest.main()
