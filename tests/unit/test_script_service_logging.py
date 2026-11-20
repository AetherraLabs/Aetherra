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

# Standard library imports
import json
import tempfile
import unittest
from pathlib import Path


class TestLogEvent(unittest.TestCase):
    """Test LogEvent dataclass."""

    def test_create_log_event(self):
        """Test creating log event."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            EventLevel,
            ExecutionPhase,
            LogEvent,
        )

        event = LogEvent(
            timestamp="2024-01-01T10:00:00",
            phase=ExecutionPhase.EXECUTING,
            level=EventLevel.INFO,
            message="Test event",
        )

        assert event.message == "Test event"
        assert event.phase == ExecutionPhase.EXECUTING

    def test_log_event_to_json(self):
        """Test converting log event to JSON."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            EventLevel,
            ExecutionPhase,
            LogEvent,
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

        assert data["message"] == "Test event"
        assert data["phase"] == "executing"
        assert data["step_name"] == "step1"


class TestTimelineEntry(unittest.TestCase):
    """Test TimelineEntry dataclass."""

    def test_create_timeline_entry(self):
        """Test creating timeline entry."""
        # Standard library imports
        import time

        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            TimelineEntry,
        )

        entry = TimelineEntry(
            timestamp=time.time(),
            event="test_event",
            duration=0.5,
        )

        assert entry.event == "test_event"
        assert entry.duration == 0.5


class TestExecutionTimeline(unittest.TestCase):
    """Test ExecutionTimeline class."""

    def test_create_timeline(self):
        """Test creating execution timeline."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()

        assert len(timeline.entries) == 0

    def test_record_event(self):
        """Test recording event in timeline."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()
        timeline.record("test_event", duration=0.5)

        assert len(timeline.entries) == 1
        assert timeline.entries[0].event == "test_event"

    def test_timeline_elapsed(self):
        """Test timeline elapsed time."""
        # Standard library imports
        import time

        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()
        time.sleep(0.1)
        elapsed = timeline.get_elapsed()

        assert elapsed > 0.05

    def test_timeline_export(self):
        """Test exporting timeline."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionTimeline,
        )

        timeline = ExecutionTimeline()
        timeline.record("event1", duration=0.5)
        timeline.record("event2", duration=0.3)

        export = timeline.export()

        assert "total_elapsed" in export
        assert "events" in export
        assert len(export["events"]) == 2


class TestServiceMetrics(unittest.TestCase):
    """Test ServiceMetrics class."""

    def test_create_metrics(self):
        """Test creating service metrics."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()

        assert len(metrics.step_durations) == 0
        assert len(metrics.errors) == 0

    def test_record_step(self):
        """Test recording step duration."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_step(0.3)

        assert len(metrics.step_durations) == 2

    def test_average_step_duration(self):
        """Test average step duration."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_step(0.3)

        avg = metrics.get_average_step_duration()
        assert round(abs(avg - 0.4), 7) == 0

    def test_record_error(self):
        """Test recording error."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_error("Error 1")
        metrics.record_error("Error 2")

        assert len(metrics.errors) == 2

    def test_record_warning(self):
        """Test recording warning."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_warning("Warning 1")

        assert len(metrics.warnings) == 1

    def test_custom_metrics(self):
        """Test custom metrics."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.set_custom("cache_hits", 150)
        metrics.set_custom("cache_misses", 45)

        assert metrics.custom_metrics["cache_hits"] == 150

    def test_success_rate(self):
        """Test success rate calculation."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_error("Error 1")
        metrics.record_error("Error 2")

        # 8 successful out of 10 total = 80%
        success_rate = metrics.get_success_rate(10)
        assert success_rate == 80.0

    def test_metrics_to_dict(self):
        """Test metrics dictionary export."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ServiceMetrics,
        )

        metrics = ServiceMetrics()
        metrics.record_step(0.5)
        metrics.record_error("Error 1")

        data = metrics.to_dict()

        assert "step_durations" in data
        assert "error_count" in data
        assert data["error_count"] == 1


class TestMetricsSnapshot(unittest.TestCase):
    """Test MetricsSnapshot dataclass."""

    def test_create_snapshot(self):
        """Test creating metrics snapshot."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ExecutionPhase,
            MetricsSnapshot,
        )

        snapshot = MetricsSnapshot(
            timestamp="2024-01-01T10:00:00",
            phase=ExecutionPhase.COMPLETED,
            total_steps=10,
            completed_steps=10,
            elapsed_time=5.0,
        )

        assert snapshot.total_steps == 10
        assert snapshot.phase == ExecutionPhase.COMPLETED


class TestScriptServiceLogger(unittest.TestCase):
    """Test ScriptServiceLogger class."""

    def test_logger_initialization(self):
        """Test logger initialization."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")

        assert logger.script_path == "/path/to/script.aether"
        assert logger.timeline is not None
        assert logger.metrics is not None

    def test_log_execution_start(self):
        """Test logging execution start."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_start()

        assert len(logger.events) == 1
        assert "Execution started" in logger.events[0].message

    def test_log_parsing_complete(self):
        """Test logging parsing completion."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_parsing_complete(5)

        assert len(logger.events) == 1
        assert "Parsing complete" in logger.events[0].message

    def test_log_validation_complete(self):
        """Test logging validation completion."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_validation_complete(True, 0)

        assert len(logger.events) == 1
        assert "valid" in logger.events[0].message

    def test_log_step_start(self):
        """Test logging step start."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_start("step1")

        assert len(logger.events) == 1
        assert logger.events[0].step_name == "step1"

    def test_log_step_completed(self):
        """Test logging step completion."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)

        assert len(logger.events) == 1
        assert logger.metrics.step_durations[0] == 0.5

    def test_log_step_failed(self):
        """Test logging step failure."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_failed("step1", "Connection timeout", 2.0)

        assert len(logger.events) == 1
        assert len(logger.metrics.errors) == 1

    def test_log_execution_complete(self):
        """Test logging execution completion."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_complete(True, 3.5)

        assert len(logger.events) == 1
        assert "succeeded" in logger.events[0].message

    def test_log_warning(self):
        """Test logging warning."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_warning("Test warning")

        assert len(logger.metrics.warnings) == 1

    def test_log_error(self):
        """Test logging error."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_error("Test error")

        assert len(logger.metrics.errors) == 1

    def test_get_metrics_snapshot(self):
        """Test getting metrics snapshot."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)
        snapshot = logger.get_metrics_snapshot(total_steps=10, completed_steps=1)

        assert snapshot.total_steps == 10
        assert snapshot.completed_steps == 1

    def test_export_json(self):
        """Test exporting logs as JSON."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_execution_start()
        logger.log_step_start("step1")

        json_export = logger.export_json()
        data = json.loads(json_export)

        assert "script_path" in data
        assert "events" in data
        assert "metrics" in data
        assert "timeline" in data

    def test_export_prometheus(self):
        """Test exporting metrics in Prometheus format."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.log_step_completed("step1", 0.5)

        prometheus_export = logger.export_prometheus()

        assert "# HELP" in prometheus_export
        assert "# TYPE" in prometheus_export
        assert "script_steps_total" in prometheus_export
        assert "script_errors_total" in prometheus_export

    def test_export_timeline(self):
        """Test exporting execution timeline."""
        # Aetherra imports
        from Aetherra.aetherra_core.script_service.script_service_logging import (
            ScriptServiceLogger,
        )

        logger = ScriptServiceLogger("/path/to/script.aether")
        logger.timeline.record("test_event", duration=0.5)

        timeline_export = logger.export_timeline()

        assert "total_elapsed" in timeline_export
        assert "events" in timeline_export

    def test_write_logs(self):
        """Test writing logs to file."""
        # Aetherra imports
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

            assert len(log_files) == 1
            assert len(metrics_files) == 1


if __name__ == "__main__":
    unittest.main()
