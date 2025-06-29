#!/usr/bin/env python3
"""
📊 NeuroCode Performance Monitor & Logger
=========================================

Comprehensive monitoring and logging system for NeuroCode operations:
- Performance metrics collection
- Error logging and analysis
- Memory usage tracking
- Execution time profiling
- System health monitoring

This provides production-ready observability for NeuroCode systems.
"""

import json
import logging
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    operation: str
    start_time: float
    end_time: float
    duration: float
    memory_before: float
    memory_after: float
    memory_delta: float
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NeuroLogger:
    """Advanced logging system for NeuroCode operations"""

    def __init__(self, log_dir: str = "logs", enable_performance: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_performance = enable_performance
        self.metrics: List[PerformanceMetrics] = []
        self.operation_stack: List[Dict[str, Any]] = []

        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

        simple_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        # File handlers
        self.logger = logging.getLogger("neurocode")
        self.logger.setLevel(logging.DEBUG)

        # Main log file
        main_handler = logging.FileHandler(self.log_dir / "neurocode.log")
        main_handler.setLevel(logging.INFO)
        main_handler.setFormatter(detailed_formatter)

        # Error log file
        error_handler = logging.FileHandler(self.log_dir / "errors.log")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)

        # Performance log file
        perf_handler = logging.FileHandler(self.log_dir / "performance.log")
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(simple_formatter)

        # Console handler (optional)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(simple_formatter)

        # Add handlers
        self.logger.addHandler(main_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(perf_handler)
        # self.logger.addHandler(console_handler)  # Uncomment for console output

        # Separate performance logger
        self.perf_logger = logging.getLogger("neurocode.performance")
        self.perf_logger.addHandler(perf_handler)
        self.perf_logger.setLevel(logging.INFO)

    def start_operation(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Start monitoring an operation"""
        if not self.enable_performance:
            return operation

        operation_id = f"{operation}_{int(time.time() * 1000)}"

        operation_data = {
            "id": operation_id,
            "operation": operation,
            "start_time": time.time(),
            "memory_before": self._get_memory_usage(),
            "metadata": metadata or {},
        }

        self.operation_stack.append(operation_data)
        self.logger.info(f"Started operation: {operation}")

        return operation_id

    def end_operation(
        self, operation_id: str, success: bool = True, error_message: Optional[str] = None
    ) -> Optional[PerformanceMetrics]:
        """End monitoring an operation"""
        if not self.enable_performance:
            return None

        # Find the operation in the stack
        operation_data = None
        for i, op in enumerate(self.operation_stack):
            if op["id"] == operation_id:
                operation_data = self.operation_stack.pop(i)
                break

        if not operation_data:
            self.logger.warning(f"Operation not found in stack: {operation_id}")
            return None

        end_time = time.time()
        memory_after = self._get_memory_usage()

        metrics = PerformanceMetrics(
            operation=operation_data["operation"],
            start_time=operation_data["start_time"],
            end_time=end_time,
            duration=end_time - operation_data["start_time"],
            memory_before=operation_data["memory_before"],
            memory_after=memory_after,
            memory_delta=memory_after - operation_data["memory_before"],
            success=success,
            error_message=error_message,
            metadata=operation_data["metadata"],
        )

        self.metrics.append(metrics)

        # Log performance data
        self.perf_logger.info(
            f"Operation: {metrics.operation} | "
            f"Duration: {metrics.duration:.3f}s | "
            f"Memory: {metrics.memory_delta:+.2f}MB | "
            f"Status: {'SUCCESS' if success else 'FAILED'}"
        )

        if not success and error_message:
            self.logger.error(f"Operation failed: {operation_data['operation']} - {error_message}")
        else:
            self.logger.info(f"Completed operation: {operation_data['operation']}")

        return metrics

    def log_error(self, error: Exception, context: str = "", operation: Optional[str] = None):
        """Log an error with full context"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "operation": operation,
            "traceback": traceback.format_exc(),
        }

        self.logger.error(f"Error in {context}: {type(error).__name__}: {error}")

        # Save detailed error to file
        error_file = self.log_dir / f"error_{int(time.time())}.json"
        with open(error_file, "w") as f:
            json.dump(error_data, f, indent=2)

    def log_info(
        self,
        message: str,
        operation: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Log informational message"""
        if metadata:
            message += f" | Metadata: {json.dumps(metadata)}"

        self.logger.info(message)

    def log_warning(self, message: str, operation: Optional[str] = None):
        """Log warning message"""
        self.logger.warning(message)

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary statistics"""
        if not self.metrics:
            return {"message": "No performance data available"}

        successful_ops = [m for m in self.metrics if m.success]
        failed_ops = [m for m in self.metrics if not m.success]

        durations = [m.duration for m in successful_ops]
        memory_deltas = [m.memory_delta for m in self.metrics]

        summary = {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(self.metrics) * 100,
            "average_duration": sum(durations) / len(durations) if durations else 0,
            "max_duration": max(durations) if durations else 0,
            "min_duration": min(durations) if durations else 0,
            "average_memory_delta": sum(memory_deltas) / len(memory_deltas) if memory_deltas else 0,
            "max_memory_delta": max(memory_deltas) if memory_deltas else 0,
            "operations_by_type": {},
        }

        # Count operations by type
        for metric in self.metrics:
            op_type = metric.operation
            if op_type not in summary["operations_by_type"]:
                summary["operations_by_type"][op_type] = {
                    "count": 0,
                    "success_count": 0,
                    "average_duration": 0,
                }

            summary["operations_by_type"][op_type]["count"] += 1
            if metric.success:
                summary["operations_by_type"][op_type]["success_count"] += 1

        # Calculate average durations by type
        for op_type in summary["operations_by_type"]:
            type_metrics = [m for m in self.metrics if m.operation == op_type and m.success]
            if type_metrics:
                avg_duration = sum(m.duration for m in type_metrics) / len(type_metrics)
                summary["operations_by_type"][op_type]["average_duration"] = avg_duration

        return summary

    def export_metrics(self, filename: Optional[str] = None) -> str:
        """Export metrics to JSON file"""
        if not filename:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.log_dir / filename

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_performance_summary(),
            "metrics": [asdict(m) for m in self.metrics],
        }

        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Metrics exported to: {filepath}")
        return str(filepath)

    def monitor_system_health(self) -> Dict[str, Any]:
        """Monitor overall system health"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            health_data = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "active_operations": len(self.operation_stack),
            }

            # Log warnings for resource usage
            if cpu_percent > 80:
                self.log_warning(f"High CPU usage: {cpu_percent}%")

            if memory.percent > 80:
                self.log_warning(f"High memory usage: {memory.percent}%")

            if disk.percent > 90:
                self.log_warning(f"Low disk space: {disk.percent}% used")

            return health_data

        except Exception as e:
            self.log_error(e, "system_health_monitoring")
            return {"error": str(e)}


class PerformanceMonitor:
    """Context manager for easy performance monitoring"""

    def __init__(
        self, logger: NeuroLogger, operation: str, metadata: Optional[Dict[str, Any]] = None
    ):
        self.logger = logger
        self.operation = operation
        self.metadata = metadata
        self.operation_id = None

    def __enter__(self):
        self.operation_id = self.logger.start_operation(self.operation, self.metadata)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        success = exc_type is None
        error_message = str(exc_val) if exc_val else None

        if self.operation_id:
            self.logger.end_operation(self.operation_id, success, error_message)

        if exc_val:
            self.logger.log_error(exc_val, self.operation)


# Global logger instance
_global_logger: Optional[NeuroLogger] = None


def get_logger() -> NeuroLogger:
    """Get the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = NeuroLogger()
    return _global_logger


def monitor_operation(operation: str, metadata: Optional[Dict[str, Any]] = None):
    """Decorator for monitoring function performance"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger()
            with PerformanceMonitor(logger, operation, metadata):
                return func(*args, **kwargs)

        return wrapper

    return decorator


if __name__ == "__main__":
    # Demo usage
    logger = NeuroLogger()

    print("🔍 NeuroCode Performance Monitor Demo")
    print("-" * 40)

    # Simulate some operations
    with PerformanceMonitor(logger, "memory_operation"):
        time.sleep(0.1)  # Simulate work

    with PerformanceMonitor(logger, "file_execution"):
        time.sleep(0.05)  # Simulate work

    # Get summary
    summary = logger.get_performance_summary()
    print("📊 Performance Summary:")
    print(f"   Operations: {summary['total_operations']}")
    print(f"   Success Rate: {summary['success_rate']:.1f}%")
    print(f"   Avg Duration: {summary['average_duration']:.3f}s")

    # Export metrics
    export_file = logger.export_metrics()
    print(f"📁 Metrics exported to: {export_file}")

    # System health
    health = logger.monitor_system_health()
    print("🏥 System Health:")
    print(f"   CPU: {health['cpu_percent']:.1f}%")
    print(f"   Memory: {health['memory_percent']:.1f}%")
    print(f"   Available Memory: {health['memory_available_gb']:.1f}GB")
