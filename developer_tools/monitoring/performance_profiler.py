"""
Performance Profiler - Resource usage analysis and optimization insights.

This module provides comprehensive performance monitoring and profiling capabilities
for the Aetherra & Lyrixa project, helping identify bottlenecks and optimization opportunities.
"""

import sys
import time
import psutil
import threading
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import cProfile
import pstats
from io import StringIO
import tracemalloc


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    timestamp: str
    cpu_percent: float
    memory_usage: float
    memory_percent: float
    disk_io_read: int
    disk_io_write: int
    network_io_sent: int
    network_io_recv: int
    thread_count: int
    open_files: int
    process_time: float


@dataclass
class ProfileSession:
    """Container for profiling session data."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    duration: Optional[float]
    metrics: List[PerformanceMetrics]
    function_stats: Optional[Dict[str, Any]]
    memory_stats: Optional[Dict[str, Any]]
    bottlenecks: List[str]
    recommendations: List[str]


class PerformanceProfiler:
    """Comprehensive performance profiler for system monitoring and analysis."""

    def __init__(self, data_dir: str = "data/profiler"):
        """Initialize the performance profiler.

        Args:
            data_dir: Directory to store profiling data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_file = self.data_dir / "sessions.json"
        self.current_session: Optional[ProfileSession] = None
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.process = psutil.Process()

        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_io_high': 100 * 1024 * 1024,  # 100MB/s
            'response_time': 1.0  # 1 second
        }

        # Initialize sessions storage
        if not self.sessions_file.exists():
            self._save_sessions([])

    def start_profiling(self, session_name: Optional[str] = None) -> str:
        """Start a new profiling session.

        Args:
            session_name: Optional name for the session

        Returns:
            Session ID
        """
        if self.current_session:
            self.stop_profiling()

        session_id = session_name or f"session_{int(time.time())}"

        self.current_session = ProfileSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            duration=None,
            metrics=[],
            function_stats=None,
            memory_stats=None,
            bottlenecks=[],
            recommendations=[]
        )

        # Start memory tracing
        tracemalloc.start()

        # Start monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_performance)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()

        print(f"📊 Started profiling session: {session_id}")
        return session_id

    def stop_profiling(self) -> Optional[ProfileSession]:
        """Stop the current profiling session and generate analysis.

        Returns:
            Completed session data
        """
        if not self.current_session:
            print("❌ No active profiling session")
            return None

        # Stop monitoring
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)

        # Complete session
        self.current_session.end_time = datetime.now().isoformat()
        start_dt = datetime.fromisoformat(self.current_session.start_time)
        end_dt = datetime.fromisoformat(self.current_session.end_time)
        self.current_session.duration = (end_dt - start_dt).total_seconds()

        # Stop memory tracing and get stats
        if tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')

            memory_stats = {
                'total_traces': len(top_stats),
                'top_memory_consumers': []
            }

            for stat in top_stats[:10]:
                memory_stats['top_memory_consumers'].append({
                    'file': stat.traceback.format()[0] if stat.traceback.format() else 'unknown',
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                })

            self.current_session.memory_stats = memory_stats
            tracemalloc.stop()

        # Analyze performance and generate recommendations
        self._analyze_performance()

        # Save session
        self._save_session(self.current_session)

        session = self.current_session
        self.current_session = None

        print(f"✅ Profiling session completed: {session.session_id}")
        print(f"   Duration: {session.duration:.2f}s")
        print(f"   Metrics collected: {len(session.metrics)}")
        print(f"   Bottlenecks found: {len(session.bottlenecks)}")

        return session

    def profile_function(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile a specific function's performance.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Profiling results
        """
        # Setup profiler
        profiler = cProfile.Profile()

        # Start timing and memory tracking
        start_time = time.time()
        tracemalloc.start()
        start_memory = self.process.memory_info().rss

        try:
            # Profile function execution
            profiler.enable()
            result = func(*args, **kwargs)
            profiler.disable()

            # Collect metrics
            end_time = time.time()
            end_memory = self.process.memory_info().rss
            duration = end_time - start_time
            memory_delta = end_memory - start_memory

            # Get memory snapshot
            snapshot = tracemalloc.take_snapshot()
            top_stats = snapshot.statistics('lineno')
            tracemalloc.stop()

            # Process function stats
            stats_stream = StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats('cumulative')
            stats.print_stats(20)
            function_stats = stats_stream.getvalue()

            return {
                'function_name': func.__name__,
                'duration': duration,
                'memory_delta_mb': memory_delta / 1024 / 1024,
                'function_stats': function_stats,
                'top_memory_usage': [
                    {
                        'file': stat.traceback.format()[0] if stat.traceback.format() else 'unknown',
                        'size_mb': stat.size / 1024 / 1024
                    }
                    for stat in top_stats[:5]
                ],
                'result': result
            }

        except Exception as e:
            if tracemalloc.is_tracing():
                tracemalloc.stop()
            return {
                'function_name': func.__name__,
                'error': str(e),
                'duration': time.time() - start_time
            }

    def get_system_metrics(self) -> PerformanceMetrics:
        """Get current system performance metrics.

        Returns:
            Current performance metrics
        """
        try:
            # Get process info
            memory_info = self.process.memory_info()
            io_info = self.process.io_counters()

            # Get system info
            cpu_percent = self.process.cpu_percent()
            memory_percent = self.process.memory_percent()

            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_usage=memory_info.rss / 1024 / 1024,  # MB
                memory_percent=memory_percent,
                disk_io_read=io_info.read_bytes,
                disk_io_write=io_info.write_bytes,
                network_io_sent=getattr(io_info, 'read_chars', 0),
                network_io_recv=getattr(io_info, 'write_chars', 0),
                thread_count=self.process.num_threads(),
                open_files=len(self.process.open_files()),
                process_time=time.time()
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Fallback metrics
            return PerformanceMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_usage=0.0,
                memory_percent=0.0,
                disk_io_read=0,
                disk_io_write=0,
                network_io_sent=0,
                network_io_recv=0,
                thread_count=0,
                open_files=0,
                process_time=time.time()
            )

    def generate_report(self, session_id: Optional[str] = None) -> str:
        """Generate a performance report.

        Args:
            session_id: Specific session to report on (default: latest)

        Returns:
            Report content
        """
        sessions = self._load_sessions()

        if session_id:
            session = next((s for s in sessions if s['session_id'] == session_id), None)
            if not session:
                return f"❌ Session '{session_id}' not found"
        else:
            if not sessions:
                return "❌ No profiling sessions found"
            session = sessions[-1]  # Latest session

        report = [
            "# 📊 Performance Analysis Report",
            f"**Session:** {session['session_id']}",
            f"**Duration:** {session.get('duration', 0):.2f}s",
            f"**Period:** {session['start_time']} - {session.get('end_time', 'N/A')}",
            "",
            "## 📈 Performance Summary",
        ]

        if session.get('metrics'):
            metrics = session['metrics']
            avg_cpu = sum(m['cpu_percent'] for m in metrics) / len(metrics)
            avg_memory = sum(m['memory_usage'] for m in metrics) / len(metrics)
            max_memory = max(m['memory_usage'] for m in metrics)

            report.extend([
                f"- **Average CPU Usage:** {avg_cpu:.1f}%",
                f"- **Average Memory Usage:** {avg_memory:.1f} MB",
                f"- **Peak Memory Usage:** {max_memory:.1f} MB",
                f"- **Metrics Collected:** {len(metrics)}",
                ""
            ])

        if session.get('bottlenecks'):
            report.extend([
                "## ⚠️ Performance Bottlenecks",
                ""
            ])
            for bottleneck in session['bottlenecks']:
                report.append(f"- {bottleneck}")
            report.append("")

        if session.get('recommendations'):
            report.extend([
                "## 💡 Optimization Recommendations",
                ""
            ])
            for rec in session['recommendations']:
                report.append(f"- {rec}")
            report.append("")

        if session.get('memory_stats'):
            mem_stats = session['memory_stats']
            report.extend([
                "## 🧠 Memory Analysis",
                f"- **Total Memory Traces:** {mem_stats.get('total_traces', 0)}",
                ""
            ])

            if mem_stats.get('top_memory_consumers'):
                report.append("### Top Memory Consumers:")
                for consumer in mem_stats['top_memory_consumers'][:5]:
                    report.append(f"- {consumer['file']}: {consumer['size_mb']:.2f} MB")
                report.append("")

        return "\n".join(report)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all profiling sessions.

        Returns:
            List of session summaries
        """
        sessions = self._load_sessions()
        return [
            {
                'session_id': s['session_id'],
                'start_time': s['start_time'],
                'duration': s.get('duration', 0),
                'metrics_count': len(s.get('metrics', [])),
                'bottlenecks_count': len(s.get('bottlenecks', []))
            }
            for s in sessions
        ]

    def _monitor_performance(self):
        """Background thread for continuous performance monitoring."""
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()
                if self.current_session:
                    self.current_session.metrics.append(metrics)

                time.sleep(1.0)  # Collect metrics every second

            except Exception as e:
                print(f"⚠️ Performance monitoring error: {e}")
                time.sleep(5.0)  # Wait before retrying

    def _analyze_performance(self):
        """Analyze collected metrics and generate insights."""
        if not self.current_session or not self.current_session.metrics:
            return

        metrics = self.current_session.metrics
        bottlenecks = []
        recommendations = []

        # Analyze CPU usage
        cpu_values = [m.cpu_percent for m in metrics]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)

        if max_cpu > self.thresholds['cpu_percent']:
            bottlenecks.append(f"High CPU usage detected: {max_cpu:.1f}% (avg: {avg_cpu:.1f}%)")
            recommendations.append("Consider optimizing CPU-intensive operations or using multiprocessing")

        # Analyze memory usage
        memory_values = [m.memory_percent for m in metrics]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)

        if max_memory > self.thresholds['memory_percent']:
            bottlenecks.append(f"High memory usage detected: {max_memory:.1f}% (avg: {avg_memory:.1f}%)")
            recommendations.append("Consider implementing memory optimization or garbage collection")

        # Analyze memory growth
        if len(metrics) > 10:
            early_memory = sum(m.memory_usage for m in metrics[:5]) / 5
            late_memory = sum(m.memory_usage for m in metrics[-5:]) / 5
            memory_growth = late_memory - early_memory

            if memory_growth > 50:  # 50MB growth
                bottlenecks.append(f"Memory growth detected: {memory_growth:.1f} MB increase")
                recommendations.append("Check for memory leaks or large object accumulation")

        # Analyze thread count
        thread_values = [m.thread_count for m in metrics]
        max_threads = max(thread_values)

        if max_threads > 50:
            bottlenecks.append(f"High thread count detected: {max_threads} threads")
            recommendations.append("Consider using thread pools or async operations")

        # Analyze file handles
        file_values = [m.open_files for m in metrics]
        max_files = max(file_values)

        if max_files > 100:
            bottlenecks.append(f"High file handle count: {max_files} open files")
            recommendations.append("Ensure proper file handle cleanup and use context managers")

        self.current_session.bottlenecks = bottlenecks
        self.current_session.recommendations = recommendations

    def _save_session(self, session: ProfileSession):
        """Save a profiling session to storage."""
        sessions = self._load_sessions()
        sessions.append(asdict(session))

        # Keep only last 50 sessions
        if len(sessions) > 50:
            sessions = sessions[-50:]

        self._save_sessions(sessions)

    def _load_sessions(self) -> List[Dict[str, Any]]:
        """Load profiling sessions from storage."""
        try:
            if self.sessions_file.exists():
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading sessions: {e}")
        return []

    def _save_sessions(self, sessions: List[Dict[str, Any]]):
        """Save profiling sessions to storage."""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving sessions: {e}")


def main():
    """Main function for CLI usage."""
    profiler = PerformanceProfiler()

    if len(sys.argv) < 2:
        print("Usage: python performance_profiler.py <command> [args]")
        print("Commands:")
        print("  start [name]    - Start profiling session")
        print("  stop            - Stop current session")
        print("  report [id]     - Generate report")
        print("  list            - List sessions")
        print("  metrics         - Show current metrics")
        return

    command = sys.argv[1]

    if command == "start":
        name = sys.argv[2] if len(sys.argv) > 2 else None
        session_id = profiler.start_profiling(name)
        print(f"Started session: {session_id}")

    elif command == "stop":
        session = profiler.stop_profiling()
        if session:
            print(f"Session completed: {session.session_id}")

    elif command == "report":
        session_id = sys.argv[2] if len(sys.argv) > 2 else None
        report = profiler.generate_report(session_id)
        print(report)

    elif command == "list":
        sessions = profiler.list_sessions()
        print("📊 Profiling Sessions:")
        for session in sessions:
            print(f"  {session['session_id']}: {session['duration']:.2f}s ({session['metrics_count']} metrics)")

    elif command == "metrics":
        metrics = profiler.get_system_metrics()
        print("📈 Current System Metrics:")
        print(f"  CPU: {metrics.cpu_percent:.1f}%")
        print(f"  Memory: {metrics.memory_usage:.1f} MB ({metrics.memory_percent:.1f}%)")
        print(f"  Threads: {metrics.thread_count}")
        print(f"  Open Files: {metrics.open_files}")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
