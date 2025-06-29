#!/usr/bin/env python3
"""
Real-Time Performance Optimization for NeuroCode
Monitors execution patterns and provides AI-powered optimization suggestions
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

import psutil


@dataclass
class ExecutionMetric:
    """Single execution measurement"""
    command: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    timestamp: float
    context: Dict[str, Any]


@dataclass
class OptimizationSuggestion:
    """AI-generated optimization suggestion"""
    command: str
    current_performance: Dict[str, float]
    suggested_optimization: str
    expected_improvement: str
    confidence: float
    implementation_complexity: str


class PerformanceOptimizer:
    """
    Real-time performance monitoring and optimization for NeuroCode
    """

    def __init__(self, metrics_file: str = "performance_metrics.json"):
        self.metrics_file = metrics_file
        self.execution_metrics: Dict[str, List[ExecutionMetric]] = {}
        self.optimization_cache: Dict[str, OptimizationSuggestion] = {}
        self.optimization_threshold = 1.0  # Commands taking >1 second
        self.min_samples = 5  # Minimum samples before optimization

        # Performance targets
        self.performance_targets = {
            "memory_efficiency": 100,  # MB
            "response_time": 0.5,      # seconds
            "cpu_efficiency": 80       # percentage
        }

        # Load existing metrics
        self.load_metrics()

    def profile_execution(self, command: str, execution_time: float,
                         memory_usage: Optional[float] = None,
                         context: Optional[Dict[str, Any]] = None) -> Optional[OptimizationSuggestion]:
        """Profile command execution for optimization opportunities"""

        # Get system metrics if not provided
        if memory_usage is None:
            process = psutil.Process()
            memory_usage = process.memory_info().rss / 1024 / 1024  # MB

        cpu_usage = psutil.cpu_percent(interval=0.1)

        # Ensure memory_usage is not None
        final_memory_usage = memory_usage if memory_usage is not None else process.memory_info().rss / 1024 / 1024

        metric = ExecutionMetric(
            command=command,
            execution_time=execution_time,
            memory_usage=final_memory_usage,
            cpu_usage=cpu_usage,
            timestamp=time.time(),
            context=context or {}
        )

        # Store metric
        if command not in self.execution_metrics:
            self.execution_metrics[command] = []

        self.execution_metrics[command].append(metric)

        # Keep only recent metrics (last 100 executions)
        self.execution_metrics[command] = self.execution_metrics[command][-100:]

        # Auto-optimize if pattern detected
        if len(self.execution_metrics[command]) >= self.min_samples:
            if self.should_optimize(command):
                suggestion = self.suggest_optimization(command)
                if suggestion:
                    print(f"🚀 Performance optimization available for '{command}'")
                    print(f"   Expected improvement: {suggestion.expected_improvement}")
                    return suggestion

        return None

    def should_optimize(self, command: str) -> bool:
        """Determine if command should be optimized"""
        metrics = self.execution_metrics[command]
        if len(metrics) < self.min_samples:
            return False

        # Calculate average performance
        avg_time = sum(m.execution_time for m in metrics[-10:]) / min(10, len(metrics))
        avg_memory = sum(m.memory_usage for m in metrics[-10:]) / min(10, len(metrics))

        # Check if performance is below threshold
        return (avg_time > self.optimization_threshold or
                avg_memory > self.performance_targets["memory_efficiency"])

    def suggest_optimization(self, command: str) -> Optional[OptimizationSuggestion]:
        """AI-powered optimization suggestions"""
        if command in self.optimization_cache:
            return self.optimization_cache[command]

        metrics = self.execution_metrics[command]
        if len(metrics) < self.min_samples:
            return None

        # Calculate performance stats
        recent_metrics = metrics[-10:]
        avg_time = sum(m.execution_time for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)

        current_performance = {
            "avg_execution_time": avg_time,
            "avg_memory_usage": avg_memory,
            "avg_cpu_usage": avg_cpu
        }

        # Generate optimization suggestion based on patterns
        suggestion = self._generate_optimization_suggestion(command, current_performance, recent_metrics)

        if suggestion:
            self.optimization_cache[command] = suggestion

        return suggestion

    def _generate_optimization_suggestion(self, command: str,
                                        current_performance: Dict[str, float],
                                        metrics: List[ExecutionMetric]) -> Optional[OptimizationSuggestion]:
        """Generate specific optimization suggestions"""

        avg_time = current_performance["avg_execution_time"]
        avg_memory = current_performance["avg_memory_usage"]

        suggestions = []
        confidence = 0.7

        # Time-based optimizations
        if avg_time > 2.0:
            suggestions.append("Consider caching frequently accessed data")
            suggestions.append("Implement parallel processing for data-intensive operations")
            confidence += 0.1

        if avg_time > 5.0:
            suggestions.append("Break down complex operations into smaller, async tasks")
            confidence += 0.1

        # Memory-based optimizations
        if avg_memory > 200:
            suggestions.append("Implement lazy loading for large datasets")
            suggestions.append("Use generators instead of loading all data into memory")
            confidence += 0.1

        if avg_memory > 500:
            suggestions.append("Consider using memory-mapped files for large data")
            suggestions.append("Implement data streaming instead of batch processing")
            confidence += 0.1

        # Pattern-based optimizations
        if len(metrics) > 20:
            time_trend = self._calculate_time_trend(metrics)
            if time_trend > 0.1:  # Performance degrading
                suggestions.append("Performance is degrading over time - check for memory leaks")
                suggestions.append("Consider resetting cached data periodically")
                confidence += 0.1

        if not suggestions:
            return None

        # Calculate expected improvement
        if avg_time > 2.0:
            expected_improvement = "30-50% faster execution"
        elif avg_time > 1.0:
            expected_improvement = "15-30% faster execution"
        else:
            expected_improvement = "10-20% faster execution"

        # Determine implementation complexity
        if len(suggestions) > 3:
            complexity = "High - Multiple optimizations needed"
        elif len(suggestions) > 1:
            complexity = "Medium - Several improvements possible"
        else:
            complexity = "Low - Single optimization needed"

        return OptimizationSuggestion(
            command=command,
            current_performance=current_performance,
            suggested_optimization=" | ".join(suggestions),
            expected_improvement=expected_improvement,
            confidence=min(confidence, 0.95),
            implementation_complexity=complexity
        )

    def _calculate_time_trend(self, metrics: List[ExecutionMetric]) -> float:
        """Calculate if execution time is trending up or down"""
        if len(metrics) < 10:
            return 0.0

        recent_times = [m.execution_time for m in metrics[-10:]]
        older_times = [m.execution_time for m in metrics[-20:-10]]

        if not older_times:
            return 0.0

        recent_avg = sum(recent_times) / len(recent_times)
        older_avg = sum(older_times) / len(older_times)

        return (recent_avg - older_avg) / older_avg

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "summary": {
                "total_commands_tracked": len(self.execution_metrics),
                "total_executions": sum(len(metrics) for metrics in self.execution_metrics.values()),
                "optimization_suggestions": len(self.optimization_cache)
            },
            "command_performance": {},
            "system_health": self._get_system_health(),
            "optimization_opportunities": []
        }

        # Analyze each command
        for command, metrics in self.execution_metrics.items():
            if not metrics:
                continue

            recent_metrics = metrics[-10:]
            report["command_performance"][command] = {
                "executions": len(metrics),
                "avg_time": sum(m.execution_time for m in recent_metrics) / len(recent_metrics),
                "avg_memory": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                "trend": self._calculate_time_trend(metrics),
                "needs_optimization": self.should_optimize(command)
            }

            if self.should_optimize(command):
                suggestion = self.suggest_optimization(command)
                if suggestion:
                    report["optimization_opportunities"].append(asdict(suggestion))

        return report

    def _get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "timestamp": time.time()
        }

    def apply_optimization(self, command: str, optimization_type: str) -> bool:
        """Apply specific optimization to command"""
        # This would integrate with the NeuroCode interpreter to apply optimizations
        print(f"🔧 Applying {optimization_type} optimization to '{command}'")

        # For now, just mark as optimized
        if command in self.optimization_cache:
            del self.optimization_cache[command]

        return True

    def save_metrics(self) -> None:
        """Save metrics to file"""
        try:
            data = {
                "metrics": {
                    cmd: [asdict(metric) for metric in metrics]
                    for cmd, metrics in self.execution_metrics.items()
                },
                "optimizations": {
                    cmd: asdict(opt) for cmd, opt in self.optimization_cache.items()
                },
                "saved_at": time.time()
            }

            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"⚠️ Failed to save performance metrics: {e}")

    def load_metrics(self) -> None:
        """Load metrics from file"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file) as f:
                    data = json.load(f)

                # Load execution metrics
                for cmd, metric_data in data.get("metrics", {}).items():
                    self.execution_metrics[cmd] = [
                        ExecutionMetric(**metric) for metric in metric_data
                    ]

                # Load optimization cache
                for cmd, opt_data in data.get("optimizations", {}).items():
                    self.optimization_cache[cmd] = OptimizationSuggestion(**opt_data)

        except Exception as e:
            print(f"⚠️ Failed to load performance metrics: {e}")

    def clear_metrics(self) -> None:
        """Clear all stored metrics"""
        self.execution_metrics.clear()
        self.optimization_cache.clear()
        if os.path.exists(self.metrics_file):
            os.remove(self.metrics_file)


# Singleton instance for global use
performance_optimizer = PerformanceOptimizer()


# Utility functions for easy integration
def profile_command(command: str, execution_time: float, context: Optional[Dict[str, Any]] = None):
    """Profile a command execution"""
    return performance_optimizer.profile_execution(command, execution_time, context=context)


def get_optimization_suggestions(command: str) -> Optional[OptimizationSuggestion]:
    """Get optimization suggestions for a command"""
    return performance_optimizer.suggest_optimization(command)


def generate_performance_report() -> Dict[str, Any]:
    """Generate comprehensive performance report"""
    return performance_optimizer.get_performance_report()


if __name__ == "__main__":
    # Example usage
    print("🚀 NeuroCode Performance Optimizer")

    # Simulate some command executions
    optimizer = PerformanceOptimizer()

    # Profile some commands
    optimizer.profile_execution("data_processing", 2.5, 150.0)
    optimizer.profile_execution("data_processing", 2.8, 160.0)
    optimizer.profile_execution("data_processing", 3.1, 180.0)
    optimizer.profile_execution("data_processing", 2.9, 170.0)
    optimizer.profile_execution("data_processing", 3.2, 190.0)

    # Get optimization suggestions
    suggestion = optimizer.suggest_optimization("data_processing")
    if suggestion:
        print("\n📊 Optimization Suggestion:")
        print(f"   Command: {suggestion.command}")
        print(f"   Current avg time: {suggestion.current_performance['avg_execution_time']:.2f}s")
        print(f"   Suggestion: {suggestion.suggested_optimization}")
        print(f"   Expected improvement: {suggestion.expected_improvement}")
        print(f"   Confidence: {suggestion.confidence:.0%}")

    # Generate report
    report = optimizer.get_performance_report()
    print("\n📈 Performance Report:")
    print(f"   Commands tracked: {report['summary']['total_commands_tracked']}")
    print(f"   Total executions: {report['summary']['total_executions']}")
    print(f"   Optimization opportunities: {len(report['optimization_opportunities'])}")

    # Save metrics
    optimizer.save_metrics()
    print("\n✅ Performance metrics saved!")
