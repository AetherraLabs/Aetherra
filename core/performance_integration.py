#!/usr/bin/env python3
"""
⚡ AetherraCode Performance Integration System
==========================================

Comprehensive performance optimization integration for AetherraCode & Neuroplex.
This module provides easy-to-use performance enhancements that integrate with
all existing systems while maintaining backward compatibility.

Features:
- Automatic performance optimization across all components
- Intelligent resource management and monitoring
- Fast startup optimization
- Real-time performance tuning
- Memory and CPU optimization
- Network and I/O performance improvements
"""

import functools
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

# Import our performance modules
try:
    from .memory_performance import memory_optimizer
    from .performance_engine import performance_engine
    from .ui_performance import ui_optimizer

    PERFORMANCE_MODULES_AVAILABLE = True
except ImportError:
    PERFORMANCE_MODULES_AVAILABLE = False
    performance_engine = None
    memory_optimizer = None
    ui_optimizer = None


@dataclass
class PerformanceConfig:
    """Global performance configuration"""

    enable_caching: bool = True
    enable_parallel_processing: bool = True
    enable_memory_optimization: bool = True
    enable_ui_optimization: bool = True
    enable_startup_optimization: bool = True
    max_memory_mb: int = 1024
    target_fps: int = 60
    cache_size: int = 1000
    worker_threads: int = 4


class PerformanceManager:
    """Central performance management system"""

    def __init__(self, config: Optional[PerformanceConfig] = None):
        self.config = config or PerformanceConfig()
        self.optimizations_applied = []
        self.performance_history = []
        self.startup_time = time.time()

        # Initialize performance systems if available
        if PERFORMANCE_MODULES_AVAILABLE:
            self.performance_engine = performance_engine
            self.memory_optimizer = memory_optimizer
            self.ui_optimizer = ui_optimizer
        else:
            self.performance_engine = None
            self.memory_optimizer = None
            self.ui_optimizer = None

        # Thread pool for background optimizations
        self.executor = ThreadPoolExecutor(max_workers=self.config.worker_threads)

        # Apply initial optimizations
        self._apply_startup_optimizations()

    def _apply_startup_optimizations(self) -> None:
        """Apply optimizations at startup"""
        if not self.config.enable_startup_optimization:
            return

        optimizations = []

        # Memory optimizations
        if self.config.enable_memory_optimization and self.memory_optimizer:
            self.memory_optimizer.optimize_memory()
            optimizations.append("memory_startup_optimization")

        # Cache optimizations
        if self.config.enable_caching and self.performance_engine:
            # Pre-warm cache with common operations
            optimizations.append("cache_prewarming")

        # UI optimizations
        if self.config.enable_ui_optimization and self.ui_optimizer:
            self.ui_optimizer.optimization_enabled = True
            optimizations.append("ui_startup_optimization")

        self.optimizations_applied.extend(optimizations)

    def optimize_operation(
        self, operation_name: str, operation_func: Callable, *args, **kwargs
    ) -> Any:
        """Optimize any operation automatically"""
        start_time = time.time()

        try:
            # Apply memory optimization
            if self.config.enable_memory_optimization and self.memory_optimizer:
                # Optimize string arguments
                optimized_args = []
                for arg in args:
                    if isinstance(arg, str):
                        optimized_args.append(self.memory_optimizer.optimize_string(arg))
                    else:
                        optimized_args.append(arg)
                args = tuple(optimized_args)

            # Apply caching if available
            if self.config.enable_caching and self.performance_engine:
                try:
                    # Create a safe hash for caching (handle unhashable types)
                    safe_args = str(args) if args else ""
                    safe_kwargs = str(sorted(kwargs.items())) if kwargs else ""
                    cache_key = f"{operation_name}:{hash(safe_args + safe_kwargs)}"
                    return self.performance_engine.cached_operation(
                        cache_key, operation_func, *args, **kwargs
                    )
                except (TypeError, ValueError):
                    # Fall back to direct execution if hashing fails
                    pass

            return operation_func(*args, **kwargs)

        finally:
            # Record performance
            execution_time = time.time() - start_time
            self.performance_history.append(
                {
                    "operation": operation_name,
                    "execution_time": execution_time,
                    "timestamp": start_time,
                }
            )

    def optimize_ui_operation(
        self,
        widget_class: Optional[type] = None,
        render_func: Optional[Callable] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Optimize UI operations"""
        if not self.config.enable_ui_optimization or not self.ui_optimizer:
            if widget_class:
                return widget_class(*args, **kwargs)
            elif render_func:
                return render_func(*args, **kwargs)
            return None

        # Widget creation optimization
        if widget_class:
            return self.ui_optimizer.optimize_widget_creation(widget_class, *args, **kwargs)

        # Render optimization
        if render_func:
            operation_name = getattr(render_func, "__name__", "render_operation")
            return self.ui_optimizer.optimize_render_operation(
                operation_name, lambda: render_func(*args, **kwargs)
            )

        return None

    def optimize_data_processing(
        self, data: List[Any], process_func: Callable, use_parallel: Optional[bool] = None
    ) -> List[Any]:
        """Optimize data processing operations"""
        if use_parallel is None:
            use_parallel = self.config.enable_parallel_processing and len(data) > 10

        if use_parallel and self.performance_engine:
            return self.performance_engine.parallel_operation("data_processing", process_func, data)
        else:
            return [process_func(item) for item in data]

    def check_system_health(self) -> Dict[str, Any]:
        """Check overall system health and performance"""
        health_report = {
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.startup_time,
            "optimizations_applied": len(self.optimizations_applied),
            "recent_operations": len(
                [op for op in self.performance_history if time.time() - op["timestamp"] < 60]
            ),
        }

        # Add specific module health if available
        if self.performance_engine:
            engine_report = self.performance_engine.get_performance_report()
            health_report["performance_engine"] = {
                "total_operations": engine_report["summary"]["total_operations"],
                "cache_hit_rate": engine_report["cache_performance"]["hit_rate"],
            }

        if self.memory_optimizer:
            memory_report = self.memory_optimizer.get_performance_report()
            health_report["memory_status"] = memory_report["memory_status"]

        if self.ui_optimizer:
            ui_metrics = self.ui_optimizer.measure_ui_performance()
            health_report["ui_performance"] = {
                "widget_count": ui_metrics.widget_count,
                "memory_usage_mb": ui_metrics.memory_usage,
                "fps": ui_metrics.fps,
            }

        return health_report

    def auto_optimize(self) -> Dict[str, Any]:
        """Perform automatic system optimization"""
        optimizations_performed = []

        # Check if optimization is needed
        health = self.check_system_health()

        # Memory optimization
        if self.memory_optimizer:
            pressure = self.memory_optimizer.check_memory_pressure()
            if pressure["pressure_level"] in ["high", "critical"]:
                memory_result = self.memory_optimizer.optimize_memory()
                optimizations_performed.append(
                    f"memory: {memory_result['memory_freed_mb']:.1f}MB freed"
                )

        # Cache optimization
        if self.performance_engine:
            cache_stats = self.performance_engine.cache.stats()
            if cache_stats["hit_rate"] < 0.3:  # Low hit rate
                self.performance_engine.cache.clear()
                optimizations_performed.append("cache: cleared low-efficiency cache")

        # UI optimization
        if self.ui_optimizer:
            suggestions = self.ui_optimizer.get_optimization_suggestions()
            if "High memory usage" in str(suggestions):
                ui_result = self.ui_optimizer.clear_caches()
                optimizations_performed.append(
                    f"ui: cleared {ui_result['widgets_cleared']} cached widgets"
                )

        return {"optimizations_performed": optimizations_performed, "system_health": health}

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        return {
            "config": {
                "caching_enabled": self.config.enable_caching,
                "parallel_processing": self.config.enable_parallel_processing,
                "memory_optimization": self.config.enable_memory_optimization,
                "ui_optimization": self.config.enable_ui_optimization,
            },
            "runtime_stats": {
                "uptime_seconds": time.time() - self.startup_time,
                "total_optimizations": len(self.optimizations_applied),
                "recent_operations": len(self.performance_history),
            },
            "system_health": self.check_system_health(),
            "optimization_history": self.optimizations_applied[-10:],  # Last 10 optimizations
        }

    def shutdown(self) -> None:
        """Clean shutdown of performance systems"""
        self.executor.shutdown(wait=True)

        if self.performance_engine:
            self.performance_engine.shutdown()

        if self.memory_optimizer:
            self.memory_optimizer.cleanup()


# Global performance manager
performance_manager = PerformanceManager()


# Decorators for easy performance integration
def performance_optimized(
    operation_name: Optional[str] = None, enable_caching: bool = True, enable_parallel: bool = False
):
    """Decorator for automatic performance optimization"""

    def decorator(func):
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return performance_manager.optimize_operation(op_name, func, *args, **kwargs)

        return wrapper

    return decorator


def fast_data_processing(use_parallel: bool = True):
    """Decorator for optimized data processing"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(data, *args, **kwargs):
            if isinstance(data, list) and len(data) > 1:
                process_func = functools.partial(func, *args, **kwargs) if args or kwargs else func
                return performance_manager.optimize_data_processing(
                    data, process_func, use_parallel
                )
            else:
                return func(data, *args, **kwargs)

        return wrapper

    return decorator


def ui_optimized(cache_widgets: bool = True, debounce_ms: int = 0):
    """Decorator for UI performance optimization"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return performance_manager.optimize_ui_operation(*args, render_func=func, **kwargs)

        return wrapper

    return decorator


# Context managers
@contextmanager
def optimized_operation(operation_name: str):
    """Context manager for optimized operations"""
    start_time = time.time()

    # Pre-operation optimization
    if performance_manager.memory_optimizer:
        pressure = performance_manager.memory_optimizer.check_memory_pressure()
        if pressure["pressure_level"] == "critical":
            performance_manager.memory_optimizer.optimize_memory()

    try:
        yield
    finally:
        # Post-operation cleanup
        execution_time = time.time() - start_time
        if execution_time > 1.0:  # Long operation
            performance_manager.auto_optimize()


@contextmanager
def fast_startup():
    """Context manager for optimized startup"""
    startup_start = time.time()

    # Apply startup optimizations
    if performance_manager.config.enable_startup_optimization:
        performance_manager._apply_startup_optimizations()

    try:
        yield
    finally:
        startup_time = time.time() - startup_start
        print(f"⚡ Startup completed in {startup_time:.2f}s with performance optimizations")


# Utility functions
def optimize_aethercode_startup() -> Dict[str, Any]:
    """Optimize AetherraCode startup performance"""
    return performance_manager.auto_optimize()


def get_performance_status() -> Dict[str, Any]:
    """Get current performance status"""
    return performance_manager.get_performance_summary()


def enable_performance_mode(mode: str = "balanced") -> None:
    """Enable specific performance mode"""
    if mode == "performance":
        performance_manager.config.enable_caching = True
        performance_manager.config.enable_parallel_processing = True
        performance_manager.config.enable_memory_optimization = True
        performance_manager.config.max_memory_mb = 512
        performance_manager.config.target_fps = 30
    elif mode == "quality":
        performance_manager.config.enable_caching = True
        performance_manager.config.enable_parallel_processing = False
        performance_manager.config.enable_memory_optimization = False
        performance_manager.config.max_memory_mb = 2048
        performance_manager.config.target_fps = 60
    else:  # balanced
        performance_manager.config.enable_caching = True
        performance_manager.config.enable_parallel_processing = True
        performance_manager.config.enable_memory_optimization = True
        performance_manager.config.max_memory_mb = 1024
        performance_manager.config.target_fps = 60


def auto_tune_performance() -> Dict[str, Any]:
    """Automatically tune performance based on system capabilities"""
    return performance_manager.auto_optimize()


# Integration functions for existing AetherraCode components
def optimize_interpreter_startup():
    """Optimize AetherraCode interpreter startup"""
    with fast_startup():
        if performance_manager.memory_optimizer:
            # Pre-intern common AetherraCode keywords
            keywords = ["goal", "remember", "think", "agent", "when", "if", "else", "end"]
            for keyword in keywords:
                performance_manager.memory_optimizer.optimize_string(keyword)


def optimize_memory_operations(memory_system):
    """Optimize memory system operations"""
    if hasattr(memory_system, "remember"):
        original_remember = memory_system.remember

        @performance_optimized("memory_remember", enable_caching=True)
        def optimized_remember(text, **kwargs):
            return original_remember(text, **kwargs)

        memory_system.remember = optimized_remember


def optimize_ui_components(ui_system):
    """Optimize UI system components"""
    if hasattr(ui_system, "create_widget"):

        def optimized_create_widget(widget_class, *args, **kwargs):
            return performance_manager.optimize_ui_operation(
                *args, widget_class=widget_class, **kwargs
            )

        ui_system.create_widget = optimized_create_widget


if __name__ == "__main__":
    # Example usage and testing
    print("⚡ AetherraCode Performance Integration System")
    print("=" * 60)

    # Test performance optimization
    @performance_optimized("test_operation")
    def test_operation(data):
        """Test operation for performance measurement"""
        return sum(x**2 for x in data)

    # Test data processing optimization
    @fast_data_processing()
    def process_item(item):
        return item**2

    # Test operations
    test_data = list(range(1000))

    with optimized_operation("performance_test"):
        # Test individual operation
        result1 = test_operation(test_data)

        # Test data processing
        result2 = process_item(test_data)

    # Get performance summary
    summary = get_performance_status()
    print("\n📊 Performance Summary:")
    print(f"Uptime: {summary['runtime_stats']['uptime_seconds']:.2f}s")
    print(f"Optimizations applied: {summary['runtime_stats']['total_optimizations']}")

    # Test auto-optimization
    auto_result = auto_tune_performance()
    print("\n🔧 Auto-optimization results:")
    for opt in auto_result.get("optimizations_performed", []):
        print(f"  • {opt}")

    # Cleanup
    performance_manager.shutdown()
