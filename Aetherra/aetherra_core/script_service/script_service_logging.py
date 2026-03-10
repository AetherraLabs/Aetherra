"""
Script Service Logging & Telemetry - Structured logging and metrics export.

Provides comprehensive observability for script execution:
  1. Structured JSON logging for all events
  2. Execution timeline tracking
  3. Prometheus-compatible metrics export
  4. Performance monitoring and analysis
  5. Audit trail generation

Features:
  - JSON-formatted log records with context
  - Execution phase tracking (parsed, validated, executing, completed)
  - Metrics aggregation and export
  - Histogram tracking for durations
  - Error tracking and categorization
  - Performance thresholds and alerts

Example:
    >>> logger = ScriptServiceLogger("script.aether")
    >>> metrics = ExecutionMetrics()
    >>> logger.log_execution_start("script.aether")
    >>> logger.log_step_completed("step1", 0.5)
    >>> logger.export_prometheus()
"""

import json
import logging
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


class ExecutionPhase(Enum):
    """Script execution phases."""

    INIT = "init"
    """Script initialization"""
    PARSED = "parsed"
    """Script parsed successfully"""
    VALIDATED = "validated"
    """Script validation complete"""
    EXECUTING = "executing"
    """Steps executing"""
    COMPLETED = "completed"
    """Execution complete"""
    FAILED = "failed"
    """Execution failed"""


class EventLevel(Enum):
    """Event severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class LogEvent:
    """A single log event."""

    timestamp: str
    """ISO format timestamp"""
    phase: ExecutionPhase
    """Execution phase"""
    level: EventLevel
    """Event severity"""
    message: str
    """Event message"""
    step_name: Optional[str] = None
    """Associated step"""
    duration: float = 0.0
    """Event duration in seconds"""
    metrics: Dict[str, Any] = field(default_factory=dict)
    """Associated metrics"""

    def to_json(self) -> str:
        """Convert to JSON string."""
        data = asdict(self)
        data["phase"] = self.phase.value
        data["level"] = self.level.value
        return json.dumps(data)


@dataclass
class TimelineEntry:
    """Timeline entry for an event."""

    timestamp: float
    """Unix timestamp"""
    event: str
    """Event description"""
    duration: float = 0.0
    """Duration of event"""
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""


@dataclass
class MetricsSnapshot:
    """Point-in-time metrics snapshot."""

    timestamp: str
    """When snapshot was taken"""
    phase: ExecutionPhase
    """Current phase"""
    total_steps: int = 0
    """Total steps in script"""
    completed_steps: int = 0
    """Completed steps"""
    failed_steps: int = 0
    """Failed steps"""
    elapsed_time: float = 0.0
    """Elapsed time in seconds"""
    avg_step_duration: float = 0.0
    """Average step duration"""
    success_rate: float = 100.0
    """Percentage of steps successful"""
    memory_usage_mb: float = 0.0
    """Memory usage in MB"""


class ExecutionTimeline:
    """Tracks execution timeline and event sequence."""

    def __init__(self):
        """Initialize timeline."""
        self.entries: List[TimelineEntry] = []
        self.start_time = time.time()

    def record(
        self,
        event: str,
        duration: float = 0.0,
        metadata: Optional[Dict] = None,
    ):
        """
        Record event in timeline.

        Args:
            event: Event description
            duration: Event duration in seconds
            metadata: Additional metadata
        """
        entry = TimelineEntry(
            timestamp=time.time(),
            event=event,
            duration=duration,
            metadata=metadata or {},
        )
        self.entries.append(entry)

    def get_elapsed(self) -> float:
        """Get total elapsed time."""
        return time.time() - self.start_time

    def export(self) -> Dict[str, Any]:
        """Export timeline data."""
        return {
            "total_elapsed": self.get_elapsed(),
            "events": [
                {
                    "timestamp": e.timestamp,
                    "event": e.event,
                    "duration": e.duration,
                    "metadata": e.metadata,
                }
                for e in self.entries
            ],
        }


class ServiceMetrics:
    """Aggregates service-level metrics."""

    def __init__(self):
        """Initialize metrics."""
        self.step_durations: List[float] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.custom_metrics: Dict[str, Any] = {}

    def record_step(self, duration: float):
        """Record step execution duration."""
        self.step_durations.append(duration)

    def record_error(self, error: str):
        """Record error."""
        self.errors.append(error)

    def record_warning(self, warning: str):
        """Record warning."""
        self.warnings.append(warning)

    def set_custom(self, key: str, value: Any):
        """Set custom metric."""
        self.custom_metrics[key] = value

    def get_average_step_duration(self) -> float:
        """Get average step duration."""
        if not self.step_durations:
            return 0.0
        return sum(self.step_durations) / len(self.step_durations)

    def get_success_rate(self, total_steps: int) -> float:
        """Get success rate as percentage."""
        if total_steps == 0:
            return 100.0
        successful = total_steps - len(self.errors)
        return (successful / total_steps) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "step_durations": self.step_durations,
            "avg_step_duration": self.get_average_step_duration(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "custom_metrics": self.custom_metrics,
        }


class ScriptServiceLogger:
    """Structured logging for script service."""

    def __init__(
        self,
        script_path: str,
        log_dir: Optional[str] = None,
    ):
        """
        Initialize logger.

        Args:
            script_path: Path to script being logged
            log_dir: Directory for log files (optional)
        """
        self.script_path = script_path
        self.log_dir = Path(log_dir) if log_dir else None
        self.events: List[LogEvent] = []
        self.timeline = ExecutionTimeline()
        self.metrics = ServiceMetrics()
        self.current_phase = ExecutionPhase.INIT
        self.start_time = datetime.now()

        # Create Python logger
        self._setup_logger()

    def _setup_logger(self):
        """Setup Python logging."""
        self.logger = logging.getLogger(f"script_service.{self.script_path}")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(
        self,
        level: EventLevel,
        message: str,
        step_name: Optional[str] = None,
        duration: float = 0.0,
        metrics: Optional[Dict] = None,
    ):
        """
        Log event.

        Args:
            level: Event level
            message: Event message
            step_name: Associated step name
            duration: Event duration
            metrics: Associated metrics
        """
        event = LogEvent(
            timestamp=datetime.now().isoformat(),
            phase=self.current_phase,
            level=level,
            message=message,
            step_name=step_name,
            duration=duration,
            metrics=metrics or {},
        )
        self.events.append(event)

        # Also log to Python logger
        log_func = getattr(self.logger, level.value.lower())
        log_func(f"{message} (phase={self.current_phase.value})")

    def log_execution_start(self):
        """Log execution start."""
        self.current_phase = ExecutionPhase.INIT
        self.log(EventLevel.INFO, f"Execution started: {self.script_path}")
        self.timeline.record("execution_start")

    def log_parsing_complete(self, step_count: int):
        """Log parsing completion."""
        self.current_phase = ExecutionPhase.PARSED
        self.log(
            EventLevel.INFO,
            f"Parsing complete: {step_count} steps",
            metrics={"step_count": step_count},
        )
        self.timeline.record("parsing_complete", metadata={"steps": step_count})

    def log_validation_complete(self, is_valid: bool, error_count: int = 0):
        """Log validation completion."""
        self.current_phase = ExecutionPhase.VALIDATED
        status = "valid" if is_valid else "invalid"
        self.log(
            EventLevel.WARNING if not is_valid else EventLevel.INFO,
            f"Validation complete: {status} ({error_count} errors)",
            metrics={"valid": is_valid, "error_count": error_count},
        )
        self.timeline.record(
            "validation_complete",
            metadata={"valid": is_valid, "errors": error_count},
        )

    def log_step_start(self, step_name: str):
        """Log step start."""
        self.log(EventLevel.INFO, f"Step starting", step_name=step_name)
        self.timeline.record(f"step_start_{step_name}")

    def log_step_completed(self, step_name: str, duration: float):
        """Log step completion."""
        self.log(
            EventLevel.INFO,
            f"Step completed",
            step_name=step_name,
            duration=duration,
            metrics={"duration": duration},
        )
        self.timeline.record(
            f"step_completed_{step_name}",
            duration=duration,
        )
        self.metrics.record_step(duration)

    def log_step_failed(self, step_name: str, error: str, duration: float):
        """Log step failure."""
        self.log(
            EventLevel.ERROR,
            f"Step failed: {error}",
            step_name=step_name,
            duration=duration,
            metrics={"error": error},
        )
        self.timeline.record(
            f"step_failed_{step_name}",
            duration=duration,
            metadata={"error": error},
        )
        self.metrics.record_error(error)

    def log_execution_complete(self, success: bool, duration: float):
        """Log execution completion."""
        self.current_phase = (
            ExecutionPhase.COMPLETED if success else ExecutionPhase.FAILED
        )
        level = EventLevel.INFO if success else EventLevel.ERROR
        status = "succeeded" if success else "failed"
        self.log(
            level,
            f"Execution {status}",
            duration=duration,
            metrics={"success": success, "total_duration": duration},
        )
        self.timeline.record(
            "execution_complete",
            duration=duration,
            metadata={"success": success},
        )

    def log_warning(self, message: str, step_name: Optional[str] = None):
        """Log warning."""
        self.log(EventLevel.WARNING, message, step_name=step_name)
        self.metrics.record_warning(message)

    def log_error(self, message: str, step_name: Optional[str] = None):
        """Log error."""
        self.log(EventLevel.ERROR, message, step_name=step_name)
        self.metrics.record_error(message)

    def get_metrics_snapshot(
        self, total_steps: int = 0, completed_steps: int = 0
    ) -> MetricsSnapshot:
        """Get current metrics snapshot."""
        elapsed = self.timeline.get_elapsed()
        avg_duration = self.metrics.get_average_step_duration()
        success_rate = self.metrics.get_success_rate(total_steps)

        return MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            phase=self.current_phase,
            total_steps=total_steps,
            completed_steps=completed_steps,
            failed_steps=len(self.metrics.errors),
            elapsed_time=elapsed,
            avg_step_duration=avg_duration,
            success_rate=success_rate,
        )

    def export_json(self) -> str:
        """Export logs as JSON."""
        data = {
            "script_path": self.script_path,
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "phase": self.current_phase.value,
            "events": [json.loads(e.to_json()) for e in self.events],
            "metrics": self.metrics.to_dict(),
            "timeline": self.timeline.export(),
        }
        return json.dumps(data, indent=2)

    def export_prometheus(self) -> str:
        """
        Export metrics in Prometheus format.

        Prometheus text exposition format: HELP, TYPE, then metrics.
        """
        lines = []

        # Script execution metrics
        lines.append("# HELP script_steps_total Total steps in script")
        lines.append("# TYPE script_steps_total counter")
        lines.append('script_steps_total{script="' + self.script_path + '"} 0')

        lines.append("# HELP script_steps_completed Completed steps")
        lines.append("# TYPE script_steps_completed gauge")
        lines.append('script_steps_completed{script="' + self.script_path + '"} 0')

        lines.append("# HELP script_step_duration_seconds Step execution duration")
        lines.append("# TYPE script_step_duration_seconds histogram")
        if self.metrics.step_durations:
            avg = self.metrics.get_average_step_duration()
            lines.append(
                f'script_step_duration_seconds_avg{{script="{self.script_path}"}} {avg}'
            )

        lines.append("# HELP script_errors_total Total errors")
        lines.append("# TYPE script_errors_total counter")
        lines.append(
            f'script_errors_total{{script="{self.script_path}"}} '
            f"{len(self.metrics.errors)}"
        )

        lines.append("# HELP script_warnings_total Total warnings")
        lines.append("# TYPE script_warnings_total counter")
        lines.append(
            f'script_warnings_total{{script="{self.script_path}"}} '
            f"{len(self.metrics.warnings)}"
        )

        return "\n".join(lines)

    def export_timeline(self) -> Dict[str, Any]:
        """Export execution timeline."""
        return self.timeline.export()

    def write_logs(self):
        """Write logs to file (if log_dir configured)."""
        if not self.log_dir:
            return

        self.log_dir.mkdir(parents=True, exist_ok=True)

        log_file = self.log_dir / f"{Path(self.script_path).stem}_log.json"
        with open(log_file, "w") as f:
            f.write(self.export_json())

        metrics_file = self.log_dir / f"{Path(self.script_path).stem}_metrics.txt"
        with open(metrics_file, "w") as f:
            f.write(self.export_prometheus())
