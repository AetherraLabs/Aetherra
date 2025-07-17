"""
🧠 Aetherra Memory Management System
===================================

A comprehensive memory management system designed to prevent memory leaks,
optimize performance, and ensure stable operation of the Aetherra AI system.

Author: Aetherra Performance Team
Date: July 16, 2025
"""

import gc
import psutil
import threading
import time
import weakref
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import json
import tracemalloc
import sys
import os
from contextlib import contextmanager

@dataclass
class MemoryMetrics:
    """Memory usage metrics"""
    total_memory: float = 0.0
    used_memory: float = 0.0
    free_memory: float = 0.0
    memory_percent: float = 0.0
    peak_memory: float = 0.0
    gc_collections: int = 0

class MemoryManager:
    """
    🧠 Advanced Memory Management System

    Features:
    - Memory leak detection
    - Automatic garbage collection
    - Resource monitoring
    - Memory usage optimization
    - Object lifecycle tracking
    - Emergency memory cleanup
    """

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = Path(workspace_path or ".")
        self.metrics_dir = self.workspace_path / ".aetherra" / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Memory tracking
        self.tracked_objects = weakref.WeakSet()
        self.memory_snapshots = []
        self.peak_memory = 0.0
        self.gc_threshold = 100 * 1024 * 1024  # 100MB

        # Monitoring settings
        self.monitoring_interval = 60  # seconds
        self.max_memory_usage = 80  # percent
        self.leak_detection_enabled = True

        # Initialize logging
        self._setup_logging()

        # Start memory tracing
        if self.leak_detection_enabled:
            tracemalloc.start()

        # Start monitoring
        self._start_monitoring()

        # Register cleanup handlers
        self._register_cleanup_handlers()

    def _setup_logging(self):
        """Setup memory management logging"""
        log_file = self.metrics_dir / "memory_management.log"

        self.logger = logging.getLogger("aetherra_memory")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def track_object(self, obj: Any, name: Optional[str] = None):
        """
        🔍 Track an object for memory management

        Args:
            obj: Object to track
            name: Optional name for the object
        """
        if hasattr(obj, '__dict__'):
            obj._memory_tracker_name = name or obj.__class__.__name__
            self.tracked_objects.add(obj)

            # Add cleanup method if it exists
            if hasattr(obj, 'cleanup'):
                weakref.finalize(obj, obj.cleanup)

    def get_memory_usage(self) -> MemoryMetrics:
        """
        📊 Get current memory usage metrics

        Returns:
            MemoryMetrics object with current usage
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        virtual_memory = psutil.virtual_memory()

        metrics = MemoryMetrics(
            total_memory=virtual_memory.total,
            used_memory=memory_info.rss,
            free_memory=virtual_memory.available,
            memory_percent=virtual_memory.percent,
            peak_memory=max(self.peak_memory, memory_info.rss),
            gc_collections=len(gc.get_stats())
        )

        # Update peak memory
        self.peak_memory = metrics.peak_memory

        return metrics

    def force_garbage_collection(self):
        """
        🗑️ Force garbage collection
        """
        before = self.get_memory_usage()

        # Clear weak references
        self.tracked_objects.clear()

        # Force collection of all generations
        collected = 0
        for generation in range(3):
            collected += gc.collect(generation)

        after = self.get_memory_usage()
        freed = before.used_memory - after.used_memory

        self.logger.info(f"Garbage collection freed {freed/1024/1024:.1f}MB, collected {collected} objects")

        return freed

    def check_memory_leaks(self) -> List[Dict[str, Any]]:
        """
        🔍 Check for potential memory leaks

        Returns:
            List of potential leak reports
        """
        if not self.leak_detection_enabled:
            return []

        try:
            # Take memory snapshot
            snapshot = tracemalloc.take_snapshot()

            # Compare with previous snapshots
            leaks = []

            if self.memory_snapshots:
                # Get top differences
                top_stats = snapshot.compare_to(self.memory_snapshots[-1], 'lineno')

                for stat in top_stats[:10]:  # Top 10 differences
                    if stat.size_diff > 1024 * 1024:  # > 1MB difference
                        leaks.append({
                            'file': stat.traceback.format()[0] if stat.traceback else 'Unknown',
                            'size_diff': stat.size_diff,
                            'size_diff_mb': stat.size_diff / 1024 / 1024,
                            'count_diff': stat.count_diff
                        })

            # Store snapshot
            self.memory_snapshots.append(snapshot)

            # Keep only last 5 snapshots
            if len(self.memory_snapshots) > 5:
                self.memory_snapshots.pop(0)

            return leaks

        except Exception as e:
            self.logger.error(f"Error checking memory leaks: {e}")
            return []

    def cleanup_resources(self):
        """
        🧹 Clean up resources and free memory
        """
        # Clear tracked objects
        cleanup_count = 0

        for obj in list(self.tracked_objects):
            try:
                if hasattr(obj, 'cleanup'):
                    obj.cleanup()
                    cleanup_count += 1
                elif hasattr(obj, 'close'):
                    obj.close()
                    cleanup_count += 1
                elif hasattr(obj, 'clear'):
                    obj.clear()
                    cleanup_count += 1
            except Exception as e:
                self.logger.warning(f"Error cleaning up object: {e}")

        # Force garbage collection
        freed = self.force_garbage_collection()

        self.logger.info(f"Cleaned up {cleanup_count} objects, freed {freed/1024/1024:.1f}MB")

        return cleanup_count, freed

    def _start_monitoring(self):
        """Start memory monitoring thread"""
        def monitor():
            while True:
                try:
                    metrics = self.get_memory_usage()

                    # Log metrics
                    self.logger.info(f"Memory usage: {metrics.memory_percent:.1f}% "
                                   f"({metrics.used_memory/1024/1024:.1f}MB)")

                    # Check for high memory usage
                    if metrics.memory_percent > self.max_memory_usage:
                        self.logger.warning(f"High memory usage detected: {metrics.memory_percent:.1f}%")
                        self._handle_high_memory_usage()

                    # Check for leaks
                    leaks = self.check_memory_leaks()
                    if leaks:
                        self.logger.warning(f"Potential memory leaks detected: {len(leaks)} locations")

                    # Save metrics
                    self._save_metrics(metrics)

                except Exception as e:
                    self.logger.error(f"Error in memory monitoring: {e}")

                time.sleep(self.monitoring_interval)

        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def _handle_high_memory_usage(self):
        """Handle high memory usage situation"""
        self.logger.warning("Attempting to reduce memory usage...")

        # Force garbage collection
        freed = self.force_garbage_collection()

        # Clean up tracked objects
        cleanup_count, additional_freed = self.cleanup_resources()

        total_freed = freed + additional_freed

        if total_freed > 0:
            self.logger.info(f"Successfully freed {total_freed/1024/1024:.1f}MB of memory")
        else:
            self.logger.warning("Unable to free significant memory - consider restarting")

    def _save_metrics(self, metrics: MemoryMetrics):
        """Save memory metrics to file"""
        metrics_file = self.metrics_dir / "memory_metrics.json"

        metrics_data = {
            'timestamp': time.time(),
            'total_memory': metrics.total_memory,
            'used_memory': metrics.used_memory,
            'free_memory': metrics.free_memory,
            'memory_percent': metrics.memory_percent,
            'peak_memory': metrics.peak_memory,
            'gc_collections': metrics.gc_collections
        }

        # Load existing metrics
        all_metrics = []
        if metrics_file.exists():
            with open(metrics_file, 'r') as f:
                all_metrics = json.load(f)

        # Add new metrics
        all_metrics.append(metrics_data)

        # Keep only last 1000 entries
        if len(all_metrics) > 1000:
            all_metrics = all_metrics[-1000:]

        # Save back
        with open(metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)

    def _register_cleanup_handlers(self):
        """Register cleanup handlers for graceful shutdown"""
        import atexit
        import signal

        def cleanup_handler():
            self.logger.info("Performing final cleanup...")
            self.cleanup_resources()

        # Register for normal exit
        atexit.register(cleanup_handler)

        # Register for signals
        for sig in [signal.SIGINT, signal.SIGTERM]:
            signal.signal(sig, lambda s, f: cleanup_handler())

    @contextmanager
    def memory_context(self, name: str = "operation"):
        """
        🔍 Context manager for monitoring memory usage of operations

        Args:
            name: Name of the operation
        """
        before = self.get_memory_usage()
        start_time = time.time()

        try:
            yield
        finally:
            after = self.get_memory_usage()
            duration = time.time() - start_time

            memory_diff = after.used_memory - before.used_memory

            self.logger.info(f"Operation '{name}' completed in {duration:.2f}s, "
                           f"memory change: {memory_diff/1024/1024:+.1f}MB")

            if memory_diff > 10 * 1024 * 1024:  # > 10MB increase
                self.logger.warning(f"Large memory increase detected in '{name}': "
                                  f"{memory_diff/1024/1024:.1f}MB")

    def get_memory_report(self) -> Dict[str, Any]:
        """
        📊 Get comprehensive memory report

        Returns:
            Dictionary with detailed memory information
        """
        metrics = self.get_memory_usage()

        return {
            'current_usage': {
                'used_mb': metrics.used_memory / 1024 / 1024,
                'free_mb': metrics.free_memory / 1024 / 1024,
                'percent': metrics.memory_percent,
                'peak_mb': metrics.peak_memory / 1024 / 1024
            },
            'tracking': {
                'tracked_objects': len(self.tracked_objects),
                'memory_snapshots': len(self.memory_snapshots),
                'gc_collections': metrics.gc_collections
            },
            'settings': {
                'monitoring_enabled': True,
                'leak_detection_enabled': self.leak_detection_enabled,
                'max_memory_usage': self.max_memory_usage,
                'monitoring_interval': self.monitoring_interval
            }
        }

# Global instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager

def track_object(obj: Any, name: Optional[str] = None):
    """Track an object for memory management"""
    manager = get_memory_manager()
    manager.track_object(obj, name)

def force_cleanup():
    """Force cleanup of all tracked objects"""
    manager = get_memory_manager()
    return manager.cleanup_resources()

def memory_context(name: str = "operation"):
    """Context manager for memory monitoring"""
    manager = get_memory_manager()
    return manager.memory_context(name)

if __name__ == "__main__":
    # Example usage
    manager = MemoryManager()

    print("🧠 Aetherra Memory Management System")
    print("=" * 40)

    # Get memory report
    report = manager.get_memory_report()
    print(f"Current memory usage: {report['current_usage']['used_mb']:.1f}MB "
          f"({report['current_usage']['percent']:.1f}%)")

    # Test memory context
    with manager.memory_context("test_operation"):
        # Simulate some work
        data = [i for i in range(100000)]
        del data

    # Force cleanup
    cleaned, freed = manager.cleanup_resources()
    print(f"Cleaned up {cleaned} objects, freed {freed/1024/1024:.1f}MB")
