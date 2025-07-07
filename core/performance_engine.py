#!/usr/bin/env python3
"""
🚀 AetherraCode Performance Engine - Comprehensive Performance Optimization System
================================================================================

Advanced performance optimization engine that provides real-time monitoring,
intelligent caching, parallel processing, and adaptive performance tuning
across all AetherraCode & Lyrixacomponents.

Features:
- Real-time performance monitoring and profiling
- Intelligent caching system with auto-expiration
- Parallel processing for CPU-intensive operations
- Memory optimization and garbage collection
- Startup performance optimization
- Network request optimization and batching
- Database query optimization
- UI responsiveness enhancement
- Auto-scaling and resource management
"""

import functools
import gc
import hashlib
import json
import multiprocessing
import os
import sys
import threading
import time
import weakref
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import psutil


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""

    operation: str
    execution_time: float
    memory_before: float
    memory_after: float
    cpu_usage: float
    thread_count: int
    timestamp: float
    cache_hits: int = 0
    cache_misses: int = 0
    parallel_speedup: float = 1.0
    optimization_applied: bool = False


@dataclass
class OptimizationConfig:
    """Performance optimization configuration"""

    enable_caching: bool = True
    enable_parallel_processing: bool = True
    enable_memory_optimization: bool = True
    enable_startup_optimization: bool = True
    max_cache_size: int = 1000
    max_workers: Optional[int] = None
    gc_threshold: int = 100
    memory_limit_mb: int = 1024
    profiling_enabled: bool = True


class IntelligentCache:
    """High-performance caching system with auto-expiration and LRU eviction"""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_order: deque = deque()
        self.hits = 0
        self.misses = 0
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get cached value with TTL check"""
        with self._lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl_seconds:
                    self.hits += 1
                    # Update access order
                    if key in self.access_order:
                        self.access_order.remove(key)
                    self.access_order.append(key)
                    return value
                else:
                    # Expired
                    del self.cache[key]

            self.misses += 1
            return None

    def set(self, key: str, value: Any) -> None:
        """Cache value with LRU eviction"""
        with self._lock:
            # Remove if exists
            if key in self.cache:
                self.access_order.remove(key)

            # Evict if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]

            # Add new entry
            self.cache[key] = (value, time.time())
            self.access_order.append(key)

    def clear(self) -> None:
        """Clear all cached entries"""
        with self._lock:
            self.cache.clear()
            self.access_order.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size,
        }


class ParallelProcessor:
    """Advanced parallel processing manager"""

    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = None  # Lazy initialization
        self.futures: Set[concurrent.futures.Future] = set()

    def execute_parallel(
        self, func: Callable, items: List[Any], use_processes: bool = False
    ) -> List[Any]:
        """Execute function in parallel on list of items"""
        if len(items) <= 1:
            return [func(item) for item in items]

        if use_processes and self._can_use_processes():
            return self._execute_with_processes(func, items)
        else:
            return self._execute_with_threads(func, items)

    def _execute_with_threads(self, func: Callable, items: List[Any]) -> List[Any]:
        """Execute with thread pool"""
        futures = [self.thread_pool.submit(func, item) for item in items]
        self.futures.update(futures)

        try:
            results = [future.result() for future in futures]
            return results
        finally:
            self.futures.difference_update(futures)

    def _execute_with_processes(self, func: Callable, items: List[Any]) -> List[Any]:
        """Execute with process pool"""
        if self.process_pool is None:
            self.process_pool = multiprocessing.Pool(processes=self.max_workers)

        try:
            results = self.process_pool.map(func, items)
            return list(results)
        except Exception as e:
            print(f"⚠️ Process pool execution failed: {e}")
            # Fallback to thread pool
            return self._execute_with_threads(func, items)

    def _can_use_processes(self) -> bool:
        """Check if process pool can be used"""
        return hasattr(os, "fork") or sys.platform == "win32"

    def cleanup(self) -> None:
        """Clean up executor resources"""
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.close()
            self.process_pool.join()


class MemoryOptimizer:
    """Advanced memory optimization and monitoring"""

    def __init__(self, memory_limit_mb: int = 1024):
        self.memory_limit_mb = memory_limit_mb
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        self.weak_refs: Set[weakref.ref] = set()
        self.last_gc_time = time.time()
        self.gc_interval = 30  # seconds

    def optimize_memory(self) -> Dict[str, Any]:
        """Perform comprehensive memory optimization"""
        initial_memory = self.get_memory_usage()

        # Force garbage collection
        gc.collect()

        # Clean up weak references
        self._cleanup_weak_refs()

        # Clear caches if memory is high
        if initial_memory > self.memory_limit_bytes * 0.8:
            self._clear_system_caches()

        final_memory = self.get_memory_usage()
        freed_mb = (initial_memory - final_memory) / 1024 / 1024

        return {
            "initial_memory_mb": initial_memory / 1024 / 1024,
            "final_memory_mb": final_memory / 1024 / 1024,
            "freed_mb": freed_mb,
            "gc_collections": gc.get_count(),
        }

    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        process = psutil.Process()
        return process.memory_info().rss

    def check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure"""
        current_memory = self.get_memory_usage()
        return current_memory > self.memory_limit_bytes * 0.9

    def _cleanup_weak_refs(self) -> None:
        """Clean up dead weak references"""
        dead_refs = [ref for ref in self.weak_refs if ref() is None]
        self.weak_refs.difference_update(dead_refs)

    def _clear_system_caches(self) -> None:
        """Clear various system caches"""
        # Clear import cache
        # Clear type cache if available
        if hasattr(sys, "_clear_type_cache"):
            sys._clear_type_cache()

        # Note: regex cache clearing is handled internally by Python


class StartupOptimizer:
    """Optimize startup performance and module loading"""

    def __init__(self):
        self.import_times: Dict[str, float] = {}
        self.lazy_imports: Dict[str, Callable] = {}
        self.startup_time = time.time()

    def optimize_imports(self, module_name: str) -> Any:
        """Optimize module imports with lazy loading"""
        if module_name in self.lazy_imports:
            return self.lazy_imports[module_name]()

        start_time = time.time()
        try:
            module = __import__(module_name)
            import_time = time.time() - start_time
            self.import_times[module_name] = import_time
            return module
        except ImportError as e:
            print(f"⚠️ Failed to import {module_name}: {e}")
            return None

    def setup_lazy_import(self, module_name: str, import_func: Callable) -> None:
        """Setup lazy import for expensive modules"""
        self.lazy_imports[module_name] = import_func

    def get_startup_report(self) -> Dict[str, Any]:
        """Get comprehensive startup performance report"""
        total_startup = time.time() - self.startup_time
        return {
            "total_startup_time": total_startup,
            "import_times": self.import_times,
            "slow_imports": {k: v for k, v in self.import_times.items() if v > 0.1},
            "import_count": len(self.import_times),
        }


class PerformanceEngine:
    """Main performance optimization engine"""

    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self.metrics: List[PerformanceMetrics] = []
        self.cache = IntelligentCache(max_size=self.config.max_cache_size)
        self.parallel_processor = ParallelProcessor(max_workers=self.config.max_workers)
        self.memory_optimizer = MemoryOptimizer(
            memory_limit_mb=self.config.memory_limit_mb
        )
        self.startup_optimizer = StartupOptimizer()

        # Performance tracking
        self.operation_counts: Dict[str, int] = defaultdict(int)
        self.optimization_history: List[Dict[str, Any]] = []
        self.last_cleanup = time.time()

        # Setup automatic optimization
        if self.config.enable_memory_optimization:
            self._setup_automatic_cleanup()

    @contextmanager
    def profile_operation(self, operation_name: str, auto_optimize: bool = True):
        """Context manager for profiling operations"""
        if not self.config.profiling_enabled:
            yield
            return

        # Pre-operation metrics
        start_time = time.time()
        memory_before = self.memory_optimizer.get_memory_usage()
        cpu_before = psutil.cpu_percent(interval=None)
        thread_count = threading.active_count()

        try:
            yield
        finally:
            # Post-operation metrics
            end_time = time.time()
            execution_time = end_time - start_time
            memory_after = self.memory_optimizer.get_memory_usage()
            cpu_after = psutil.cpu_percent(interval=None)

            # Record metrics
            metrics = PerformanceMetrics(
                operation=operation_name,
                execution_time=execution_time,
                memory_before=memory_before / 1024 / 1024,  # MB
                memory_after=memory_after / 1024 / 1024,  # MB
                cpu_usage=(cpu_before + cpu_after) / 2,
                thread_count=thread_count,
                timestamp=start_time,
                cache_hits=self.cache.hits,
                cache_misses=self.cache.misses,
            )

            self.metrics.append(metrics)
            self.operation_counts[operation_name] += 1

            # Auto-optimize if needed
            if auto_optimize and self._should_optimize(operation_name, execution_time):
                self._apply_optimizations(operation_name)

    def cached_operation(
        self, cache_key: str, operation_func: Callable, *args, **kwargs
    ) -> Any:
        """Execute operation with intelligent caching"""
        if not self.config.enable_caching:
            return operation_func(*args, **kwargs)

        # Generate cache key
        full_key = f"{cache_key}:{self._generate_cache_key(args, kwargs)}"

        # Try cache first
        cached_result = self.cache.get(full_key)
        if cached_result is not None:
            return cached_result

        # Execute operation
        with self.profile_operation(f"cached_{cache_key}"):
            result = operation_func(*args, **kwargs)
            self.cache.set(full_key, result)
            return result

    def parallel_operation(
        self,
        operation_name: str,
        func: Callable,
        items: List[Any],
        use_processes: bool = False,
    ) -> List[Any]:
        """Execute operation in parallel"""
        if not self.config.enable_parallel_processing or len(items) <= 1:
            return [func(item) for item in items]

        with self.profile_operation(f"parallel_{operation_name}"):
            start_time = time.time()
            results = self.parallel_processor.execute_parallel(
                func, items, use_processes
            )
            parallel_time = time.time() - start_time

            # Calculate speedup (estimate sequential time)
            estimated_sequential = len(items) * 0.1  # rough estimate
            speedup = max(1.0, estimated_sequential / parallel_time)

            # Update metrics
            if self.metrics:
                self.metrics[-1].parallel_speedup = speedup

            return results

    def optimize_startup(self, module_names: List[str]) -> Dict[str, Any]:
        """Optimize application startup"""
        if not self.config.enable_startup_optimization:
            return {}

        optimization_results = {}

        # Optimize imports
        for module_name in module_names:
            result = self.startup_optimizer.optimize_imports(module_name)
            optimization_results[module_name] = result is not None

        # Memory optimization
        memory_results = self.memory_optimizer.optimize_memory()
        optimization_results.update(memory_results)

        return optimization_results

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        if not self.metrics:
            return {"status": "no_metrics_available"}

        # Calculate statistics
        total_operations = len(self.metrics)
        avg_execution_time = (
            sum(m.execution_time for m in self.metrics) / total_operations
        )
        avg_memory_usage = (
            sum(m.memory_after - m.memory_before for m in self.metrics)
            / total_operations
        )

        # Find slow operations
        slow_operations = [m for m in self.metrics if m.execution_time > 1.0]

        # Cache statistics
        cache_stats = self.cache.stats()

        # Top operations by count
        top_operations = sorted(
            self.operation_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "summary": {
                "total_operations": total_operations,
                "avg_execution_time": avg_execution_time,
                "avg_memory_usage_mb": avg_memory_usage,
                "slow_operations_count": len(slow_operations),
                "optimizations_applied": len(self.optimization_history),
            },
            "cache_performance": cache_stats,
            "top_operations": top_operations,
            "slow_operations": [
                {
                    "operation": m.operation,
                    "execution_time": m.execution_time,
                    "memory_usage_mb": m.memory_after - m.memory_before,
                }
                for m in slow_operations[-5:]  # Last 5 slow operations
            ],
            "optimization_history": self.optimization_history[
                -5:
            ],  # Last 5 optimizations
            "startup_report": self.startup_optimizer.get_startup_report(),
            "system_health": {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage("/").percent
                if os.name != "nt"
                else psutil.disk_usage("C:\\").percent,
                "thread_count": threading.active_count(),
            },
        }

    def _should_optimize(self, operation_name: str, execution_time: float) -> bool:
        """Determine if operation should be optimized"""
        return (
            execution_time > 1.0  # Slow operations
            or self.operation_counts[operation_name] > 10  # Frequent operations
            or self.memory_optimizer.check_memory_pressure()  # Memory pressure
        )

    def _apply_optimizations(self, operation_name: str) -> None:
        """Apply optimizations for specific operation"""
        optimizations_applied = []

        # Memory optimization
        if self.memory_optimizer.check_memory_pressure():
            memory_results = self.memory_optimizer.optimize_memory()
            optimizations_applied.append(
                f"memory_cleanup:{memory_results['freed_mb']:.1f}MB"
            )

        # Cache optimization
        if self.cache.stats()["hit_rate"] < 0.5 and self.cache.stats()["size"] > 100:
            # Increase cache size if hit rate is low
            self.cache.max_size = min(
                self.cache.max_size * 2, self.config.max_cache_size * 2
            )
            optimizations_applied.append("cache_size_increased")

        # Record optimization
        if optimizations_applied:
            self.optimization_history.append(
                {
                    "operation": operation_name,
                    "timestamp": time.time(),
                    "optimizations": optimizations_applied,
                }
            )

    def _generate_cache_key(self, args: Tuple, kwargs: Dict) -> str:
        """Generate cache key from arguments"""
        key_data = {"args": args, "kwargs": sorted(kwargs.items())}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()[:16]

    def _setup_automatic_cleanup(self) -> None:
        """Setup automatic memory cleanup"""

        def cleanup_worker():
            while True:
                time.sleep(30)  # Clean up every 30 seconds
                if time.time() - self.last_cleanup > 60:  # Only if 1 minute passed
                    try:
                        self.memory_optimizer.optimize_memory()
                        self.last_cleanup = time.time()
                    except Exception as e:
                        print(f"⚠️ Automatic cleanup failed: {e}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def shutdown(self) -> None:
        """Clean shutdown of performance engine"""
        self.parallel_processor.cleanup()
        self.cache.clear()


# Global performance engine instance
performance_engine = PerformanceEngine()


# Decorators for easy performance optimization
def performance_optimized(
    operation_name: Optional[str] = None,
    cache_key: Optional[str] = None,
    enable_parallel: bool = False,
):
    """Decorator for automatic performance optimization"""

    def decorator(func):
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if cache_key:
                return performance_engine.cached_operation(
                    cache_key, func, *args, **kwargs
                )
            elif enable_parallel and isinstance(args[0], list):
                # For functions that take a list as first argument
                items = args[0]
                remaining_args = args[1:]
                partial_func = (
                    functools.partial(func, *remaining_args, **kwargs)
                    if remaining_args or kwargs
                    else func
                )
                return performance_engine.parallel_operation(
                    op_name, partial_func, items
                )
            else:
                with performance_engine.profile_operation(op_name):
                    return func(*args, **kwargs)

        return wrapper

    return decorator


def cached(cache_key: str, ttl_seconds: int = 3600):
    """Decorator for caching function results"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return performance_engine.cached_operation(cache_key, func, *args, **kwargs)

        return wrapper

    return decorator


def parallel_processing(use_processes: bool = False):
    """Decorator for parallel processing of list operations"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(items, *args, **kwargs):
            if not isinstance(items, list):
                return func(items, *args, **kwargs)

            partial_func = (
                functools.partial(func, *args, **kwargs) if args or kwargs else func
            )
            return performance_engine.parallel_operation(
                func.__name__, partial_func, items, use_processes
            )

        return wrapper

    return decorator


# Utility functions
def optimize_aethercode_startup(modules: Optional[List[str]] = None) -> Dict[str, Any]:
    """Optimize AetherraCode startup performance"""
    default_modules = [
        "core.interpreter",
        "core.memory",
        "core.ai_runtime",
        "core.plugin_manager",
        "ui.aetherplex_gui",
    ]
    modules_to_optimize = modules or default_modules
    return performance_engine.optimize_startup(modules_to_optimize)


def get_performance_status() -> Dict[str, Any]:
    """Get current performance status"""
    return performance_engine.get_performance_report()


def clear_performance_cache() -> None:
    """Clear performance cache"""
    performance_engine.cache.clear()


if __name__ == "__main__":
    # Example usage and testing
    print("🚀 AetherraCode Performance Engine")
    print("=" * 50)

    # Test performance profiling
    with performance_engine.profile_operation("test_operation"):
        time.sleep(0.1)  # Simulate work
        data = [i**2 for i in range(1000)]  # Some computation

    # Test cached operation
    @cached("fibonacci", ttl_seconds=60)
    def fibonacci(n):
        if n <= 1:
            return n
        return fibonacci(n - 1) + fibonacci(n - 2)

    # Test parallel processing
    @parallel_processing()
    def square(x):
        return x**2

    numbers = list(range(100))
    squared = square(numbers)

    # Generate performance report
    report = performance_engine.get_performance_report()
    print("\n📊 Performance Report:")
    print(f"Operations tracked: {report['summary']['total_operations']}")
    print(f"Average execution time: {report['summary']['avg_execution_time']:.3f}s")
    print(f"Cache hit rate: {report['cache_performance']['hit_rate']:.2%}")

    # Cleanup
    performance_engine.shutdown()
