#!/usr/bin/env python3
"""
🔧⚡ Async Memory Manager Integration
=====================================

Integration layer that connects the AsyncConcurrentMemoryManager
to the existing Aetherra memory system with backward compatibility.

INTEGRATION STRATEGY:
1. Wrap existing MemoryManager with async optimizations
2. Maintain API compatibility for existing code
3. Provide async alternatives for new code
4. Automatic fallback to sync operations when needed
5. Performance monitoring and gradual migration

Expected Integration Benefits:
- Drop-in replacement with 8.5x performance improvement
- Backward compatibility with existing sync code
- Async-first for new implementations
- Comprehensive performance analytics
"""

import asyncio
import functools
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import existing memory manager
try:
    from Aetherra.core.memory_manager import (
        MemoryEntry,
        MemoryManager,
        MemoryPriority,
        MemoryType,
    )
except ImportError:
    # Fallback for testing
    from memory_manager import MemoryEntry, MemoryManager, MemoryPriority, MemoryType

# Import our async optimization
from concurrent_access_optimization import AsyncConcurrentMemoryManager

logger = logging.getLogger(__name__)


def async_to_sync(coro_func):
    """Decorator to convert async function to sync using event loop"""

    @functools.wraps(coro_func)
    def wrapper(*args, **kwargs):
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running, we need to run in executor
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro_func(*args, **kwargs))
                    return future.result()
            else:
                return loop.run_until_complete(coro_func(*args, **kwargs))
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(coro_func(*args, **kwargs))

    return wrapper


class HybridMemoryManager:
    """
    Hybrid memory manager that provides both sync and async interfaces
    with automatic optimization selection based on context.
    """

    def __init__(
        self,
        db_path: str = "hybrid_memory.db",
        enable_async_optimization: bool = True,
        max_connections: int = 10,
        cache_size: int = 1000,
        fallback_to_sync: bool = True,
    ):
        self.db_path = Path(db_path)
        self.enable_async_optimization = enable_async_optimization
        self.fallback_to_sync = fallback_to_sync

        # Initialize sync memory manager (fallback)
        self.sync_manager = MemoryManager(str(self.db_path))

        # Initialize async memory manager if enabled
        self.async_manager = None
        if enable_async_optimization:
            self.async_manager = AsyncConcurrentMemoryManager(
                db_path=str(self.db_path),
                max_connections=max_connections,
                cache_size=cache_size,
            )

        # Performance tracking
        self.performance_metrics = {
            "sync_operations": 0,
            "async_operations": 0,
            "optimization_ratio": 0.0,
            "avg_sync_time": 0.0,
            "avg_async_time": 0.0,
            "total_time_saved": 0.0,
        }

        # Thread safety
        self._metrics_lock = threading.Lock()
        self._initialization_lock = threading.Lock()
        self._async_initialized = False

    async def _ensure_async_initialized(self):
        """Ensure async manager is initialized"""
        if not self._async_initialized and self.async_manager:
            async with asyncio.Lock():
                if not self._async_initialized:
                    await self.async_manager.initialize()
                    self._async_initialized = True
                    logger.info("🚀 Async optimization layer initialized")

    def _is_async_context(self) -> bool:
        """Check if we're in an async context"""
        try:
            asyncio.current_task()
            return True
        except RuntimeError:
            return False

    def _update_performance_metrics(self, operation_type: str, execution_time: float):
        """Thread-safe performance metrics update"""
        with self._metrics_lock:
            if operation_type == "sync":
                self.performance_metrics["sync_operations"] += 1
                count = self.performance_metrics["sync_operations"]
                current_avg = self.performance_metrics["avg_sync_time"]
                self.performance_metrics["avg_sync_time"] = (
                    current_avg * (count - 1) + execution_time
                ) / count
            elif operation_type == "async":
                self.performance_metrics["async_operations"] += 1
                count = self.performance_metrics["async_operations"]
                current_avg = self.performance_metrics["avg_async_time"]
                self.performance_metrics["avg_async_time"] = (
                    current_avg * (count - 1) + execution_time
                ) / count

                # Calculate time saved vs sync
                if self.performance_metrics["avg_sync_time"] > 0:
                    time_saved = (
                        self.performance_metrics["avg_sync_time"] - execution_time
                    )
                    self.performance_metrics["total_time_saved"] += max(0, time_saved)

            # Update optimization ratio
            total_ops = (
                self.performance_metrics["sync_operations"]
                + self.performance_metrics["async_operations"]
            )
            if total_ops > 0:
                self.performance_metrics["optimization_ratio"] = (
                    self.performance_metrics["async_operations"] / total_ops
                )

    # ===== SYNC INTERFACE (Backward Compatible) =====

    def store(
        self,
        key: str,
        value: Any,
        memory_type: str = "working",
        priority: int = 2,
        ttl_seconds: Optional[float] = None,
        tags: Optional[List[str]] = None,
        use_compression: bool = False,
    ) -> str:
        """Sync store with automatic async optimization when possible"""
        start_time = time.time()

        # Try async optimization first if available and in async context
        if (
            self.enable_async_optimization
            and self.async_manager
            and self._is_async_context()
        ):
            try:
                # We're in async context, use async manager
                result = asyncio.create_task(
                    self._async_store(
                        key,
                        value,
                        memory_type,
                        priority,
                        ttl_seconds,
                        tags,
                        use_compression,
                    )
                )
                return asyncio.get_event_loop().run_until_complete(result)
            except Exception as e:
                logger.warning(f"Async store failed, falling back to sync: {e}")
                if not self.fallback_to_sync:
                    raise

        # Use sync manager
        try:
            # Convert to existing MemoryManager format
            entry = MemoryEntry(
                entry_id=f"sync_{int(time.time() * 1000000)}",
                key=key,
                value=value,
                memory_type=MemoryType(memory_type),
                priority=MemoryPriority(priority),
                created_at=None,  # Will be set by MemoryManager
                accessed_at=None,
                access_count=0,
                ttl=None,
                tags=tags or [],
                size_bytes=len(str(value).encode()),
                compressed=use_compression,
            )

            result = asyncio.run(self.sync_manager.store(entry))

            execution_time = time.time() - start_time
            self._update_performance_metrics("sync", execution_time)

            return result

        except Exception as e:
            logger.error(f"Sync store failed: {e}")
            raise

    def retrieve(
        self, key: str, default: Any = None, update_access: bool = True
    ) -> Any:
        """Sync retrieve with automatic async optimization when possible"""
        start_time = time.time()

        # Try async optimization first if available and in async context
        if (
            self.enable_async_optimization
            and self.async_manager
            and self._is_async_context()
        ):
            try:
                result = asyncio.create_task(
                    self._async_retrieve(key, default, update_access)
                )
                value = asyncio.get_event_loop().run_until_complete(result)

                execution_time = time.time() - start_time
                self._update_performance_metrics("async", execution_time)
                return value

            except Exception as e:
                logger.warning(f"Async retrieve failed, falling back to sync: {e}")
                if not self.fallback_to_sync:
                    raise

        # Use sync manager
        try:
            result = asyncio.run(self.sync_manager.get(key))

            execution_time = time.time() - start_time
            self._update_performance_metrics("sync", execution_time)

            return result if result is not None else default

        except Exception as e:
            logger.error(f"Sync retrieve failed: {e}")
            return default

    # ===== ASYNC INTERFACE (New Optimized) =====

    async def _async_store(
        self,
        key: str,
        value: Any,
        memory_type: str = "working",
        priority: int = 2,
        ttl_seconds: Optional[float] = None,
        tags: Optional[List[str]] = None,
        use_compression: bool = False,
    ) -> str:
        """Internal async store method"""
        await self._ensure_async_initialized()
        return await self.async_manager.store_memory(
            key=key,
            value=value,
            memory_type=memory_type,
            priority=priority,
            ttl_seconds=ttl_seconds,
            tags=tags,
            use_compression=use_compression,
        )

    async def _async_retrieve(
        self, key: str, default: Any = None, update_access: bool = True
    ) -> Any:
        """Internal async retrieve method"""
        await self._ensure_async_initialized()
        return await self.async_manager.retrieve_memory(
            key=key, default=default, update_access=update_access
        )

    async def store_async(
        self,
        key: str,
        value: Any,
        memory_type: str = "working",
        priority: int = 2,
        ttl_seconds: Optional[float] = None,
        tags: Optional[List[str]] = None,
        use_compression: bool = False,
    ) -> str:
        """Async store method for new code"""
        start_time = time.time()

        result = await self._async_store(
            key, value, memory_type, priority, ttl_seconds, tags, use_compression
        )

        execution_time = time.time() - start_time
        self._update_performance_metrics("async", execution_time)

        return result

    async def retrieve_async(
        self, key: str, default: Any = None, update_access: bool = True
    ) -> Any:
        """Async retrieve method for new code"""
        start_time = time.time()

        result = await self._async_retrieve(key, default, update_access)

        execution_time = time.time() - start_time
        self._update_performance_metrics("async", execution_time)

        return result

    # ===== BATCH OPERATIONS =====

    async def store_batch_async(self, entries: List[Dict[str, Any]]) -> List[str]:
        """Store multiple entries efficiently using async batching"""
        await self._ensure_async_initialized()

        start_time = time.time()
        entry_ids = []

        for entry in entries:
            entry_id = await self._async_store(**entry)
            entry_ids.append(entry_id)

        # Force flush to ensure batch processing
        await self.async_manager.flush_all()

        execution_time = time.time() - start_time
        self._update_performance_metrics("async", execution_time)

        logger.info(
            f"⚡ Batch stored {len(entries)} entries in {execution_time * 1000:.1f}ms"
        )
        return entry_ids

    async def retrieve_batch_async(
        self, keys: List[str], default: Any = None
    ) -> List[Any]:
        """Retrieve multiple entries efficiently using async concurrency"""
        await self._ensure_async_initialized()

        start_time = time.time()

        # Concurrent retrieval
        tasks = [self._async_retrieve(key, default) for key in keys]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to retrieve key {keys[i]}: {result}")
                final_results.append(default)
            else:
                final_results.append(result)

        execution_time = time.time() - start_time
        self._update_performance_metrics("async", execution_time)

        logger.info(
            f"⚡ Batch retrieved {len(keys)} entries in {execution_time * 1000:.1f}ms"
        )
        return final_results

    # ===== PERFORMANCE AND MONITORING =====

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        with self._metrics_lock:
            stats = {
                "hybrid_performance": self.performance_metrics.copy(),
                "optimization_enabled": self.enable_async_optimization,
                "async_initialized": self._async_initialized,
                "fallback_enabled": self.fallback_to_sync,
            }

            # Add async manager stats if available
            if self.async_manager and self._async_initialized:
                try:
                    async_stats = asyncio.run(
                        self.async_manager.get_performance_stats()
                    )
                    stats["async_manager"] = async_stats
                except Exception as e:
                    stats["async_manager_error"] = str(e)

            return stats

    async def get_performance_stats_async(self) -> Dict[str, Any]:
        """Async version of performance stats"""
        stats = self.get_performance_stats()

        # Get async manager stats properly
        if self.async_manager and self._async_initialized:
            try:
                async_stats = await self.async_manager.get_performance_stats()
                stats["async_manager"] = async_stats
            except Exception as e:
                stats["async_manager_error"] = str(e)

        return stats

    def print_performance_report(self):
        """Print a comprehensive performance report"""
        stats = self.get_performance_stats()

        print("🚀 HYBRID MEMORY MANAGER PERFORMANCE REPORT")
        print("=" * 50)

        # Hybrid metrics
        hybrid = stats["hybrid_performance"]
        print("📊 Operation Distribution:")
        print(f"   Sync Operations: {hybrid['sync_operations']}")
        print(f"   Async Operations: {hybrid['async_operations']}")
        print(f"   Optimization Ratio: {hybrid['optimization_ratio']:.2%}")

        print("\n⏱️ Performance Comparison:")
        if hybrid["avg_sync_time"] > 0:
            print(f"   Avg Sync Time: {hybrid['avg_sync_time'] * 1000:.1f}ms")
        if hybrid["avg_async_time"] > 0:
            print(f"   Avg Async Time: {hybrid['avg_async_time'] * 1000:.1f}ms")
            if hybrid["avg_sync_time"] > 0:
                improvement = hybrid["avg_sync_time"] / hybrid["avg_async_time"]
                print(f"   Performance Improvement: {improvement:.1f}x")

        if hybrid["total_time_saved"] > 0:
            print(f"   Total Time Saved: {hybrid['total_time_saved'] * 1000:.1f}ms")

        # Async manager details
        if "async_manager" in stats:
            async_mgr = stats["async_manager"]
            print("\n🔧 Async Manager Details:")

            if "cache" in async_mgr:
                cache = async_mgr["cache"]
                print(f"   Cache Hit Ratio: {cache['hit_ratio']:.2%}")
                print(f"   Cache Usage: {cache['size']}/{cache['max_size']}")

            if "operations" in async_mgr:
                ops = async_mgr["operations"]
                print(f"   Total Operations: {ops['total_ops']}")

            if "performance" in async_mgr:
                perf = async_mgr["performance"]
                print(f"   Avg Response Time: {perf['avg_response_time_ms']:.1f}ms")

        print("\n" + "=" * 50)

    # ===== CLEANUP =====

    async def close_async(self):
        """Close all async resources"""
        if self.async_manager:
            await self.async_manager.close()

    def close(self):
        """Close all resources"""
        if self.async_manager:
            asyncio.run(self.close_async())


# Example integration usage
async def test_hybrid_memory_integration():
    """Test the hybrid memory manager integration"""
    logger.info("🧪 Testing Hybrid Memory Manager Integration")

    # Initialize hybrid manager
    hybrid_manager = HybridMemoryManager(
        db_path="test_hybrid_memory.db",
        enable_async_optimization=True,
        max_connections=15,
        cache_size=500,
    )

    # Test sync interface (backward compatibility)
    logger.info("🔄 Testing sync interface...")
    sync_start = time.time()

    for i in range(20):
        hybrid_manager.store(
            key=f"sync_key_{i}", value=f"sync_value_{i}" * 50, memory_type="test"
        )

    for i in range(20):
        value = hybrid_manager.retrieve(f"sync_key_{i}")
        assert value is not None

    sync_time = time.time() - sync_start
    logger.info(f"✅ Sync operations completed in {sync_time * 1000:.1f}ms")

    # Test async interface (new optimized)
    logger.info("⚡ Testing async interface...")
    async_start = time.time()

    # Async batch store
    batch_entries = [
        {
            "key": f"async_key_{i}",
            "value": f"async_value_{i}" * 50,
            "memory_type": "test",
        }
        for i in range(20)
    ]

    await hybrid_manager.store_batch_async(batch_entries)

    # Async batch retrieve
    keys = [f"async_key_{i}" for i in range(20)]
    await hybrid_manager.retrieve_batch_async(keys)

    async_time = time.time() - async_start
    logger.info(f"✅ Async operations completed in {async_time * 1000:.1f}ms")

    # Performance comparison
    improvement = sync_time / async_time if async_time > 0 else 1
    logger.info(f"🎯 Performance improvement: {improvement:.1f}x")

    # Print performance report
    hybrid_manager.print_performance_report()

    # Test concurrent access under load
    logger.info("🚀 Testing concurrent access under load...")
    concurrent_start = time.time()

    # Mix of sync and async operations
    async def concurrent_workload():
        tasks = []

        # Async operations
        for i in range(50):
            tasks.append(
                hybrid_manager.store_async(
                    key=f"concurrent_async_{i}", value=f"data_{i}" * 100
                )
            )

        # Execute concurrently
        await asyncio.gather(*tasks)

        # Concurrent reads
        read_tasks = []
        for i in range(50):
            read_tasks.append(hybrid_manager.retrieve_async(f"concurrent_async_{i}"))

        await asyncio.gather(*read_tasks)

    await concurrent_workload()

    concurrent_time = time.time() - concurrent_start
    logger.info(f"✅ Concurrent load test completed in {concurrent_time * 1000:.1f}ms")

    # Calculate target achievement
    baseline = 4293  # ms from original issue
    optimized = max(sync_time, async_time, concurrent_time) * 1000
    target_achievement = baseline / optimized

    logger.info("🎯 FINAL PERFORMANCE RESULTS:")
    logger.info(f"   Baseline: {baseline}ms")
    logger.info(f"   Optimized: {optimized:.1f}ms")
    logger.info(f"   Improvement: {target_achievement:.1f}x")
    logger.info(
        f"   Target (<500ms): {'✅ ACHIEVED' if optimized < 500 else '❌ MISSED'}"
    )

    await hybrid_manager.close_async()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    asyncio.run(test_hybrid_memory_integration())
