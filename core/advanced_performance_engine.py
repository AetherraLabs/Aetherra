#!/usr/bin/env python3
"""
🚀 AetherraCode Advanced Performance Engine
=======================================

Ultra-fast performance optimization system designed to make AetherraCode & Neuroplex
fluid, fast, and responsive across all operations.

Key Features:
- Intelligent caching with automatic invalidation
- Parallel processing for data-heavy operations
- Startup optimization and lazy loading
- Memory pooling and efficient garbage collection
- Adaptive performance tuning based on usage patterns
- Real-time performance monitoring and auto-optimization
"""

import asyncio
import functools
import gc
import hashlib
import multiprocessing
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

try:
    import psutil
except ImportError:
    psutil = None


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics"""

    operation_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float("inf")
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    success_rate: float = 100.0
    recent_times: deque = field(default_factory=lambda: deque(maxlen=100))


@dataclass
class OptimizationSettings:
    """Performance optimization configuration"""

    enable_caching: bool = True
    enable_parallel: bool = True
    enable_memory_pooling: bool = True
    enable_lazy_loading: bool = True
    cache_size_limit: int = 1000
    thread_pool_size: int = min(8, multiprocessing.cpu_count())
    process_pool_size: int = min(4, multiprocessing.cpu_count())
    memory_threshold: float = 80.0  # Percentage
    cpu_threshold: float = 90.0  # Percentage
    auto_gc_threshold: int = 1000  # Operations before automatic GC


class IntelligentCache:
    """High-performance intelligent caching system"""

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_times: Dict[str, float] = {}
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.cache_lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with LRU tracking"""
        with self.cache_lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                self.access_counts[key] += 1
                return self.cache[key]
            return None

    def set(self, key: str, value: Any) -> None:
        """Set item in cache with automatic eviction"""
        with self.cache_lock:
            # Evict if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self._evict_lru()

            self.cache[key] = value
            self.access_times[key] = time.time()
            self.access_counts[key] = 1

    def _evict_lru(self) -> None:
        """Evict least recently used item"""
        if not self.cache:
            return

        # Find LRU item based on access time and frequency
        lru_key = min(self.access_times.items(), key=lambda x: (x[1], self.access_counts[x[0]]))[0]

        del self.cache[lru_key]
        del self.access_times[lru_key]
        del self.access_counts[lru_key]

    def clear(self) -> None:
        """Clear all cached items"""
        with self.cache_lock:
            self.cache.clear()
            self.access_times.clear()
            self.access_counts.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.cache_lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "utilization": len(self.cache) / self.max_size * 100,
                "total_accesses": sum(self.access_counts.values()),
                "unique_keys": len(self.access_counts),
            }


class MemoryPool:
    """Efficient memory pooling system"""

    def __init__(self):
        self.pools: Dict[type, List[Any]] = defaultdict(list)
        self.pool_lock = threading.RLock()
        self.max_pool_size = 100

    def get(self, obj_type: type, *args, **kwargs) -> Any:
        """Get object from pool or create new one"""
        with self.pool_lock:
            pool = self.pools[obj_type]
            if pool:
                return pool.pop()
            else:
                # Create new object
                try:
                    return obj_type(*args, **kwargs)
                except Exception:
                    # Fallback for complex objects
                    return obj_type()

    def return_obj(self, obj: Any) -> None:
        """Return object to pool"""
        obj_type = type(obj)
        with self.pool_lock:
            pool = self.pools[obj_type]
            if len(pool) < self.max_pool_size:
                # Reset object if possible
                if hasattr(obj, "reset"):
                    obj.reset()
                elif hasattr(obj, "clear"):
                    obj.clear()

                pool.append(obj)

    def clear_pools(self) -> None:
        """Clear all object pools"""
        with self.pool_lock:
            for pool in self.pools.values():
                pool.clear()


class AdaptivePerformanceEngine:
    """Core performance engine with adaptive optimization"""

    def __init__(self, settings: Optional[OptimizationSettings] = None):
        self.settings = settings or OptimizationSettings()
        self.cache = IntelligentCache(self.settings.cache_size_limit)
        self.memory_pool = MemoryPool()
        self.metrics: Dict[str, PerformanceMetrics] = defaultdict(PerformanceMetrics)

        # Thread pools for async operations
        self.thread_pool = ThreadPoolExecutor(max_workers=self.settings.thread_pool_size)
        self.process_pool = ProcessPoolExecutor(max_workers=self.settings.process_pool_size)

        # Performance monitoring
        self.operation_count = 0
        self.last_gc_count = 0
        self.startup_time = time.time()

        # Auto-optimization tracking
        self.optimization_suggestions: Dict[str, List[str]] = defaultdict(list)
        self.performance_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))

        # System monitoring
        self.monitor_lock = threading.Lock()
        self.is_monitoring = False
        self._start_monitoring()

    def _start_monitoring(self) -> None:
        """Start background performance monitoring"""
        if not self.is_monitoring and psutil:
            self.is_monitoring = True
            thread = threading.Thread(target=self._monitor_system, daemon=True)
            thread.start()

    def _monitor_system(self) -> None:
        """Background system monitoring"""
        while self.is_monitoring:
            try:
                if psutil:
                    cpu_percent = psutil.cpu_percent(interval=1)
                    memory_percent = psutil.virtual_memory().percent

                    # Auto-optimize if thresholds exceeded
                    if cpu_percent > self.settings.cpu_threshold:
                        self._trigger_cpu_optimization()

                    if memory_percent > self.settings.memory_threshold:
                        self._trigger_memory_optimization()

                time.sleep(5)  # Monitor every 5 seconds
            except Exception:
                break

    def _trigger_cpu_optimization(self) -> None:
        """Trigger CPU optimization when under high load"""
        # Reduce thread pool size temporarily
        if self.thread_pool._max_workers > 2:
            self.thread_pool._max_workers = max(2, self.thread_pool._max_workers - 1)

        # Clear old cache entries
        if len(self.cache.cache) > self.settings.cache_size_limit // 2:
            self.cache.clear()

    def _trigger_memory_optimization(self) -> None:
        """Trigger memory optimization when memory is high"""
        # Force garbage collection
        gc.collect()

        # Clear memory pools
        self.memory_pool.clear_pools()

        # Reduce cache size
        self.cache.max_size = max(100, self.cache.max_size // 2)
        self.cache.clear()

    def optimize_operation(self, operation_name: str, func: Callable, *args, **kwargs) -> Any:
        """Optimize any operation with intelligent caching and monitoring"""
        start_time = time.time()
        operation_hash = None
        result = None
        from_cache = False

        try:
            # Generate cache key if caching enabled
            if self.settings.enable_caching:
                try:
                    # Create safe hash for caching
                    arg_str = str(args) + str(sorted(kwargs.items()))
                    operation_hash = hashlib.md5(f"{operation_name}:{arg_str}".encode()).hexdigest()

                    # Check cache first
                    cached_result = self.cache.get(operation_hash)
                    if cached_result is not None:
                        from_cache = True
                        result = cached_result
                except Exception:
                    pass  # Continue without caching if hash fails

            # Execute operation if not cached
            if not from_cache:
                result = func(*args, **kwargs)

                # Cache result if possible
                if operation_hash and self.settings.enable_caching:
                    try:
                        self.cache.set(operation_hash, result)
                    except Exception:
                        pass  # Continue if caching fails

            return result

        finally:
            # Record performance metrics
            execution_time = time.time() - start_time
            self._record_performance(operation_name, execution_time, from_cache)

            # Auto-GC if needed
            self.operation_count += 1
            if self.operation_count % self.settings.auto_gc_threshold == 0:
                gc.collect()

    def optimize_parallel(
        self,
        operation_name: str,
        func: Callable,
        data_list: List[Any],
        max_workers: Optional[int] = None,
    ) -> List[Any]:
        """Optimize operations with parallel processing"""
        if not self.settings.enable_parallel or len(data_list) < 4:
            # Not worth parallelizing
            return [func(item) for item in data_list]

        start_time = time.time()
        workers = max_workers or min(len(data_list), self.settings.thread_pool_size)

        try:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                results = list(executor.map(func, data_list))
            return results

        finally:
            execution_time = time.time() - start_time
            self._record_performance(f"{operation_name}_parallel", execution_time, False)

    async def optimize_async(self, operation_name: str, func: Callable, *args, **kwargs) -> Any:
        """Optimize operations with async execution"""
        start_time = time.time()

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)

            return result

        finally:
            execution_time = time.time() - start_time
            self._record_performance(f"{operation_name}_async", execution_time, False)

    def _record_performance(
        self, operation_name: str, execution_time: float, from_cache: bool
    ) -> None:
        """Record performance metrics for analysis"""
        metrics = self.metrics[operation_name]

        metrics.operation_count += 1
        metrics.total_time += execution_time
        metrics.avg_time = metrics.total_time / metrics.operation_count
        metrics.max_time = max(metrics.max_time, execution_time)
        metrics.min_time = min(metrics.min_time, execution_time)
        metrics.recent_times.append(execution_time)

        if from_cache:
            metrics.cache_hits += 1
        else:
            metrics.cache_misses += 1

        # Update performance trends
        self.performance_trends[operation_name].append(execution_time)

        # Generate optimization suggestions
        self._analyze_performance_trends(operation_name, metrics)

    def _analyze_performance_trends(self, operation_name: str, metrics: PerformanceMetrics) -> None:
        """Analyze performance trends and generate suggestions"""
        if metrics.operation_count < 10:
            return  # Need more data

        suggestions = []
        recent_avg = sum(metrics.recent_times) / len(metrics.recent_times)

        # Check if performance is degrading
        if len(metrics.recent_times) >= 20:
            first_half = list(metrics.recent_times)[:10]
            second_half = list(metrics.recent_times)[-10:]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            if second_avg > first_avg * 1.2:  # 20% slower
                suggestions.append("Performance degrading - consider caching or optimization")

        # Check cache effectiveness
        if metrics.cache_misses > metrics.cache_hits * 2:
            suggestions.append("Low cache hit rate - consider larger cache or better keys")

        # Check if operation is slow
        if recent_avg > 1.0:  # Operations taking more than 1 second
            suggestions.append("Slow operation - consider parallel processing or chunking")

        if suggestions:
            self.optimization_suggestions[operation_name] = suggestions

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        total_operations = sum(m.operation_count for m in self.metrics.values())
        total_time = sum(m.total_time for m in self.metrics.values())
        total_cache_hits = sum(m.cache_hits for m in self.metrics.values())
        total_cache_accesses = sum(m.cache_hits + m.cache_misses for m in self.metrics.values())

        uptime = time.time() - self.startup_time

        return {
            "uptime_seconds": uptime,
            "total_operations": total_operations,
            "operations_per_second": total_operations / uptime if uptime > 0 else 0,
            "total_execution_time": total_time,
            "cache_hit_rate": (total_cache_hits / total_cache_accesses * 100)
            if total_cache_accesses > 0
            else 0,
            "cache_stats": self.cache.stats(),
            "operation_metrics": {
                name: {
                    "count": m.operation_count,
                    "avg_time": m.avg_time,
                    "total_time": m.total_time,
                    "cache_hit_rate": (m.cache_hits / (m.cache_hits + m.cache_misses) * 100)
                    if (m.cache_hits + m.cache_misses) > 0
                    else 0,
                }
                for name, m in self.metrics.items()
            },
            "optimization_suggestions": dict(self.optimization_suggestions),
            "system_info": self._get_system_info(),
        }

    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        info = {
            "thread_pool_size": self.settings.thread_pool_size,
            "process_pool_size": self.settings.process_pool_size,
            "cache_enabled": self.settings.enable_caching,
            "parallel_enabled": self.settings.enable_parallel,
        }

        if psutil:
            info.update(
                {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "available_memory_gb": psutil.virtual_memory().available / (1024**3),
                    "cpu_count": psutil.cpu_count(),
                }
            )

        return info

    def optimize_startup(self) -> None:
        """Optimize application startup time"""
        # Pre-warm thread pools
        self.thread_pool.submit(lambda: None).result()

        # Pre-allocate common objects in memory pool
        common_types = [list, dict, set, str]
        for obj_type in common_types:
            try:
                for _ in range(10):
                    obj = self.memory_pool.get(obj_type)
                    self.memory_pool.return_obj(obj)
            except Exception:
                continue

        # Pre-compile common patterns
        try:
            import re

            common_patterns = [r"\d+", r"[a-zA-Z]+", r"\w+", r"\s+"]
            for pattern in common_patterns:
                re.compile(pattern)
        except Exception:
            pass

    def shutdown(self) -> None:
        """Clean shutdown of performance engine"""
        self.is_monitoring = False
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        self.cache.clear()
        self.memory_pool.clear_pools()


# Global performance engine instance
_performance_engine: Optional[AdaptivePerformanceEngine] = None


def get_performance_engine() -> AdaptivePerformanceEngine:
    """Get global performance engine instance"""
    global _performance_engine
    if _performance_engine is None:
        _performance_engine = AdaptivePerformanceEngine()
        _performance_engine.optimize_startup()
    return _performance_engine


# Convenient decorators for optimization
def performance_optimized(operation_name: Optional[str] = None):
    """Decorator to automatically optimize function performance"""

    def decorator(func: Callable) -> Callable:
        name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            engine = get_performance_engine()
            return engine.optimize_operation(name, func, *args, **kwargs)

        return wrapper

    return decorator


def parallel_optimized(operation_name: Optional[str] = None, max_workers: Optional[int] = None):
    """Decorator to automatically parallelize function over lists"""

    def decorator(func: Callable) -> Callable:
        name = operation_name or f"{func.__module__}.{func.__name__}_parallel"

        @functools.wraps(func)
        def wrapper(data_list: List[Any], *args, **kwargs):
            engine = get_performance_engine()
            if args or kwargs:
                # Create partial function for additional arguments
                partial_func = functools.partial(func, *args, **kwargs)
                return engine.optimize_parallel(name, partial_func, data_list, max_workers)
            else:
                return engine.optimize_parallel(name, func, data_list, max_workers)

        return wrapper

    return decorator


def async_optimized(operation_name: Optional[str] = None):
    """Decorator to automatically optimize async functions"""

    def decorator(func: Callable) -> Callable:
        name = operation_name or f"{func.__module__}.{func.__name__}_async"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            engine = get_performance_engine()
            return await engine.optimize_async(name, func, *args, **kwargs)

        return wrapper

    return decorator


# Context managers for scoped optimization
class OptimizedExecution:
    """Context manager for optimized execution blocks"""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time: Optional[float] = None
        self.engine = get_performance_engine()

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            execution_time = time.time() - self.start_time
            self.engine._record_performance(self.operation_name, execution_time, False)


# Utility functions for common optimizations
def optimize_string_operations(text: str) -> str:
    """Optimize string operations with interning and pooling"""
    # Use string interning for small strings
    if len(text) < 100:
        return sys.intern(text)

    return text


def optimize_data_processing(
    data: List[Any], process_func: Callable, parallel_threshold: int = 100
) -> List[Any]:
    """Optimize data processing with automatic parallelization"""
    engine = get_performance_engine()

    if len(data) >= parallel_threshold and engine.settings.enable_parallel:
        return engine.optimize_parallel("data_processing", process_func, data)
    else:
        return [process_func(item) for item in data]


if __name__ == "__main__":
    # Demo and testing
    print("🚀 AetherraCode Advanced Performance Engine")
    print("=" * 50)

    engine = get_performance_engine()

    # Test basic optimization
    @performance_optimized("test_operation")
    def test_func(n: int) -> int:
        return sum(range(n))

    # Run test operations
    print("\n📈 Testing performance optimization...")
    for i in range(10):
        result = test_func(1000)
        print(f"  Operation {i + 1}: Result = {result}")

    # Test parallel optimization
    @parallel_optimized("parallel_test")
    def square(x: int) -> int:
        return x * x

    print("\n⚡ Testing parallel optimization...")
    data = list(range(100))
    results = square(data)
    print(f"  Processed {len(data)} items, first 10 results: {results[:10]}")

    # Show performance summary
    print("\n📊 Performance Summary:")
    summary = engine.get_performance_summary()
    print(f"  Total operations: {summary['total_operations']}")
    print(f"  Operations/second: {summary['operations_per_second']:.2f}")
    print(f"  Cache hit rate: {summary['cache_hit_rate']:.1f}%")
    print(f"  Uptime: {summary['uptime_seconds']:.2f}s")

    if summary["optimization_suggestions"]:
        print("\n🔧 Optimization Suggestions:")
        for op, suggestions in summary["optimization_suggestions"].items():
            print(f"  {op}:")
            for suggestion in suggestions:
                print(f"    - {suggestion}")

    # Cleanup
    engine.shutdown()
    print("\n✅ Performance engine demo completed!")
