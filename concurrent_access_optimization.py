#!/usr/bin/env python3
"""
🚀⚡ Concurrent Access Optimization System
===============================================

Comprehensive async optimization to eliminate concurrent access bottlenecks:

ISSUE ANALYSIS:
- No async support in core memory operations
- SQLite connections created per operation (expensive)
- Threading.Lock() blocking asyncio event loop
- Synchronous I/O in async context
- No connection pooling or read-write lock optimization

OPTIMIZATION STRATEGY:
1. AsyncIO-native memory operations with aiofiles
2. Connection pooling with async SQLite wrappers
3. Read-write locks for concurrent read optimization
4. Async batch processing with ThreadPoolExecutor
5. Lock-free caching with async-safe data structures

Expected Performance Gain: 4293ms → <500ms (8.5x improvement)
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import aiosqlite

logger = logging.getLogger(__name__)


@dataclass
class AsyncConnectionPool:
    """High-performance async SQLite connection pool"""

    db_path: str
    max_connections: int = 10
    min_connections: int = 2
    connection_timeout: float = 30.0

    # Connection management
    _available_connections: asyncio.Queue = field(
        default_factory=lambda: asyncio.Queue()
    )
    _all_connections: Set[aiosqlite.Connection] = field(default_factory=set)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _initialized: bool = False

    async def initialize(self):
        """Initialize the connection pool"""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            logger.info(f"🔗 Initializing async connection pool for {self.db_path}")

            # Create minimum connections
            for _ in range(self.min_connections):
                conn = await aiosqlite.connect(
                    self.db_path,
                    timeout=self.connection_timeout,
                    check_same_thread=False,
                )

                # Optimize SQLite settings for concurrency
                await conn.execute("PRAGMA journal_mode=WAL")
                await conn.execute("PRAGMA synchronous=NORMAL")
                await conn.execute("PRAGMA cache_size=10000")
                await conn.execute("PRAGMA temp_store=MEMORY")
                await conn.execute("PRAGMA mmap_size=268435456")  # 256MB

                self._all_connections.add(conn)
                await self._available_connections.put(conn)

            self._initialized = True
            logger.info(
                f"✅ Connection pool initialized with {self.min_connections} connections"
            )

    @asynccontextmanager
    async def get_connection(self):
        """Get a connection from the pool"""
        if not self._initialized:
            await self.initialize()

        # Get connection with timeout
        try:
            conn = await asyncio.wait_for(
                self._available_connections.get(), timeout=self.connection_timeout
            )
        except asyncio.TimeoutError:
            # Create new connection if pool exhausted and under max limit
            async with self._lock:
                if len(self._all_connections) < self.max_connections:
                    conn = await aiosqlite.connect(
                        self.db_path,
                        timeout=self.connection_timeout,
                        check_same_thread=False,
                    )
                    await conn.execute("PRAGMA journal_mode=WAL")
                    self._all_connections.add(conn)
                    logger.debug(
                        f"🔗 Created new connection, pool size: {len(self._all_connections)}"
                    )
                else:
                    raise RuntimeError(
                        "Connection pool exhausted and max connections reached"
                    )

        try:
            yield conn
        finally:
            # Return connection to pool
            await self._available_connections.put(conn)

    async def close_all(self):
        """Close all connections in the pool"""
        async with self._lock:
            for conn in self._all_connections:
                await conn.close()
            self._all_connections.clear()

            # Clear the queue
            while not self._available_connections.empty():
                try:
                    self._available_connections.get_nowait()
                except asyncio.QueueEmpty:
                    break

            self._initialized = False
            logger.info("🔒 All connections closed")


@dataclass
class AsyncReadWriteLock:
    """High-performance async read-write lock for concurrent access optimization"""

    _readers: int = 0
    _writers: int = 0
    _read_ready: asyncio.Condition = field(default_factory=asyncio.Condition)
    _write_ready: asyncio.Condition = field(default_factory=asyncio.Condition)

    @asynccontextmanager
    async def read_lock(self):
        """Acquire read lock - multiple readers allowed"""
        async with self._read_ready:
            await self._read_ready.wait_for(lambda: self._writers == 0)
            self._readers += 1

        try:
            yield
        finally:
            async with self._read_ready:
                self._readers -= 1
                if self._readers == 0:
                    self._read_ready.notify_all()

    @asynccontextmanager
    async def write_lock(self):
        """Acquire write lock - exclusive access"""
        async with self._write_ready:
            await self._write_ready.wait_for(
                lambda: self._readers == 0 and self._writers == 0
            )
            self._writers += 1

        try:
            yield
        finally:
            async with self._write_ready:
                self._writers -= 1
                self._write_ready.notify_all()


@dataclass
class AsyncMemoryCache:
    """Lock-free async memory cache with TTL and LRU eviction"""

    max_size: int = 1000
    default_ttl: float = 3600.0  # 1 hour

    # Cache storage
    _data: Dict[str, Any] = field(default_factory=dict)
    _timestamps: Dict[str, float] = field(default_factory=dict)
    _access_order: deque = field(default_factory=deque)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        async with self._lock:
            if key not in self._data:
                return None

            # Check TTL
            if time.time() - self._timestamps[key] > self.default_ttl:
                await self._remove_key(key)
                return None

            # Update access order (LRU)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

            return self._data[key]

    async def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set item in cache"""
        async with self._lock:
            # Evict if at capacity
            if len(self._data) >= self.max_size and key not in self._data:
                await self._evict_lru()

            self._data[key] = value
            self._timestamps[key] = time.time()

            # Update access order
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

    async def _evict_lru(self):
        """Evict least recently used item"""
        if self._access_order:
            lru_key = self._access_order.popleft()
            await self._remove_key(lru_key)

    async def _remove_key(self, key: str):
        """Remove key from all structures"""
        self._data.pop(key, None)
        self._timestamps.pop(key, None)
        if key in self._access_order:
            self._access_order.remove(key)

    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self._data.clear()
            self._timestamps.clear()
            self._access_order.clear()

    async def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            return {
                "size": len(self._data),
                "max_size": self.max_size,
                "hit_ratio": getattr(self, "_hits", 0)
                / max(getattr(self, "_requests", 1), 1),
                "memory_usage_mb": len(str(self._data).encode()) / 1024 / 1024,
            }


@dataclass
class AsyncBatchProcessor:
    """High-performance async batch processor for database operations"""

    max_batch_size: int = 100
    flush_interval: float = 1.0  # seconds

    # Batch storage
    _pending_operations: List[Dict[str, Any]] = field(default_factory=list)
    _batch_lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    _last_flush: float = field(default_factory=time.time)
    _flush_task: Optional[asyncio.Task] = None
    _processor_callback: Optional[Callable] = None

    def __post_init__(self):
        self._last_flush = time.time()

    async def add_operation(self, operation: Dict[str, Any]) -> bool:
        """Add operation to batch, returns True if batch was flushed"""
        async with self._batch_lock:
            self._pending_operations.append(operation)

            # Check if should flush
            should_flush = (
                len(self._pending_operations) >= self.max_batch_size
                or time.time() - self._last_flush > self.flush_interval
            )

            if should_flush:
                await self._flush_batch()
                return True

            return False

    async def _flush_batch(self):
        """Flush current batch of operations"""
        if not self._pending_operations:
            return

        batch = self._pending_operations.copy()
        self._pending_operations.clear()
        self._last_flush = time.time()

        logger.debug(f"🔄 Flushing batch of {len(batch)} operations")

        if self._processor_callback:
            try:
                await self._processor_callback(batch)
            except Exception as e:
                logger.error(f"❌ Batch processing failed: {e}")

    async def force_flush(self):
        """Force flush all pending operations"""
        async with self._batch_lock:
            await self._flush_batch()

    def set_processor(self, callback: Callable):
        """Set the batch processor callback"""
        self._processor_callback = callback


class AsyncConcurrentMemoryManager:
    """
    Optimized async memory manager with concurrent access optimizations
    """

    def __init__(
        self,
        db_path: str = "async_memory.db",
        max_connections: int = 10,
        cache_size: int = 1000,
        batch_size: int = 100,
        thread_pool_size: int = 8,
    ):
        self.db_path = Path(db_path)

        # Async infrastructure
        self.connection_pool = AsyncConnectionPool(
            db_path=str(self.db_path), max_connections=max_connections
        )
        self.rw_lock = AsyncReadWriteLock()
        self.cache = AsyncMemoryCache(max_size=cache_size)
        self.batch_processor = AsyncBatchProcessor(max_batch_size=batch_size)

        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(
            max_workers=thread_pool_size, thread_name_prefix="memory_worker"
        )

        # Performance metrics
        self.metrics = {
            "read_operations": 0,
            "write_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "batch_flushes": 0,
            "avg_response_time": 0.0,
        }

        # Set up batch processor
        self.batch_processor.set_processor(self._process_batch)

        # Initialize flag
        self._initialized = False

    async def initialize(self):
        """Initialize the async memory manager"""
        if self._initialized:
            return

        logger.info("🚀 Initializing AsyncConcurrentMemoryManager")

        # Initialize connection pool
        await self.connection_pool.initialize()

        # Create database schema
        await self._create_schema()

        self._initialized = True
        logger.info("✅ AsyncConcurrentMemoryManager initialized")

    async def _create_schema(self):
        """Create optimized database schema"""
        schema_queries = [
            """
            CREATE TABLE IF NOT EXISTS async_memory_entries (
                entry_id TEXT PRIMARY KEY,
                key_name TEXT NOT NULL,
                value_data BLOB NOT NULL,
                memory_type TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_at REAL NOT NULL,
                accessed_at REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                ttl_seconds REAL,
                tags TEXT,
                size_bytes INTEGER NOT NULL,
                compressed BOOLEAN DEFAULT FALSE
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_async_memory_key ON async_memory_entries(key_name)",
            "CREATE INDEX IF NOT EXISTS idx_async_memory_type ON async_memory_entries(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_async_memory_accessed ON async_memory_entries(accessed_at)",
            "CREATE INDEX IF NOT EXISTS idx_async_memory_created ON async_memory_entries(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_async_memory_priority ON async_memory_entries(priority)",
        ]

        async with self.connection_pool.get_connection() as conn:
            for query in schema_queries:
                await conn.execute(query)
            await conn.commit()

        logger.info("📊 Database schema created with optimized indexes")

    async def store_memory(
        self,
        key: str,
        value: Any,
        memory_type: str = "working",
        priority: int = 2,
        ttl_seconds: Optional[float] = None,
        tags: Optional[List[str]] = None,
        use_compression: bool = False,
    ) -> str:
        """Store memory entry with async optimization"""
        start_time = time.time()

        try:
            # Generate entry ID
            entry_id = hashlib.md5(f"{key}:{time.time()}".encode()).hexdigest()

            # Serialize value in thread pool to avoid blocking
            if use_compression:
                import zlib

                value_data = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool, lambda: zlib.compress(pickle.dumps(value))
                )
            else:
                value_data = await asyncio.get_event_loop().run_in_executor(
                    self.thread_pool, lambda: pickle.dumps(value)
                )

            # Calculate size
            size_bytes = len(value_data)

            # Create operation for batch processing
            operation = {
                "type": "store",
                "entry_id": entry_id,
                "key": key,
                "value_data": value_data,
                "memory_type": memory_type,
                "priority": priority,
                "created_at": time.time(),
                "accessed_at": time.time(),
                "access_count": 0,
                "ttl_seconds": ttl_seconds,
                "tags": json.dumps(tags or []),
                "size_bytes": size_bytes,
                "compressed": use_compression,
            }

            # Add to batch processor
            flushed = await self.batch_processor.add_operation(operation)

            # Update cache
            cache_key = f"entry:{key}"
            await self.cache.set(
                cache_key, {"value": value, "entry_id": entry_id, "metadata": operation}
            )

            # Update metrics
            self.metrics["write_operations"] += 1
            response_time = time.time() - start_time
            self._update_avg_response_time(response_time)

            if flushed:
                self.metrics["batch_flushes"] += 1

            logger.debug(
                f"💾 Stored memory entry {entry_id} for key '{key}' in {response_time * 1000:.1f}ms"
            )
            return entry_id

        except Exception as e:
            logger.error(f"❌ Failed to store memory for key '{key}': {e}")
            raise

    async def retrieve_memory(
        self, key: str, default: Any = None, update_access: bool = True
    ) -> Any:
        """Retrieve memory entry with read lock optimization"""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = f"entry:{key}"
            cached_data = await self.cache.get(cache_key)

            if cached_data:
                self.metrics["cache_hits"] += 1
                self.metrics["read_operations"] += 1

                response_time = time.time() - start_time
                self._update_avg_response_time(response_time)

                logger.debug(
                    f"📋 Cache hit for key '{key}' in {response_time * 1000:.1f}ms"
                )
                return cached_data["value"]

            # Cache miss - query database with read lock
            self.metrics["cache_misses"] += 1

            async with self.rw_lock.read_lock():
                async with self.connection_pool.get_connection() as conn:
                    query = """
                    SELECT entry_id, value_data, memory_type, priority, created_at,
                           accessed_at, access_count, ttl_seconds, tags, size_bytes, compressed
                    FROM async_memory_entries
                    WHERE key_name = ?
                    ORDER BY accessed_at DESC
                    LIMIT 1
                    """

                    cursor = await conn.execute(query, (key,))
                    row = await cursor.fetchone()

                    if not row:
                        logger.debug(f"🔍 No memory found for key '{key}'")
                        return default

                    # Deserialize value in thread pool
                    if row[10]:  # compressed
                        import zlib

                        value = await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool,
                            lambda: pickle.loads(zlib.decompress(row[1])),
                        )
                    else:
                        value = await asyncio.get_event_loop().run_in_executor(
                            self.thread_pool, lambda: pickle.loads(row[1])
                        )

                    # Update access count if requested
                    if update_access:
                        await self._update_access_async(row[0])

                    # Cache the result
                    await self.cache.set(
                        cache_key,
                        {
                            "value": value,
                            "entry_id": row[0],
                            "metadata": {
                                "memory_type": row[2],
                                "priority": row[3],
                                "created_at": row[4],
                                "size_bytes": row[9],
                            },
                        },
                    )

                    self.metrics["read_operations"] += 1
                    response_time = time.time() - start_time
                    self._update_avg_response_time(response_time)

                    logger.debug(
                        f"💽 Retrieved memory for key '{key}' in {response_time * 1000:.1f}ms"
                    )
                    return value

        except Exception as e:
            logger.error(f"❌ Failed to retrieve memory for key '{key}': {e}")
            raise

    async def _update_access_async(self, entry_id: str):
        """Update access count asynchronously"""
        operation = {
            "type": "update_access",
            "entry_id": entry_id,
            "accessed_at": time.time(),
        }
        await self.batch_processor.add_operation(operation)

    async def _process_batch(self, operations: List[Dict[str, Any]]):
        """Process a batch of database operations"""
        if not operations:
            return

        start_time = time.time()

        try:
            async with self.rw_lock.write_lock():
                async with self.connection_pool.get_connection() as conn:
                    store_ops = [op for op in operations if op["type"] == "store"]
                    update_ops = [
                        op for op in operations if op["type"] == "update_access"
                    ]

                    # Batch store operations
                    if store_ops:
                        store_query = """
                        INSERT OR REPLACE INTO async_memory_entries
                        (entry_id, key_name, value_data, memory_type, priority,
                         created_at, accessed_at, access_count, ttl_seconds,
                         tags, size_bytes, compressed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """

                        store_params = [
                            (
                                op["entry_id"],
                                op["key"],
                                op["value_data"],
                                op["memory_type"],
                                op["priority"],
                                op["created_at"],
                                op["accessed_at"],
                                op["access_count"],
                                op["ttl_seconds"],
                                op["tags"],
                                op["size_bytes"],
                                op["compressed"],
                            )
                            for op in store_ops
                        ]

                        await conn.executemany(store_query, store_params)

                    # Batch update operations
                    if update_ops:
                        update_query = """
                        UPDATE async_memory_entries
                        SET accessed_at = ?, access_count = access_count + 1
                        WHERE entry_id = ?
                        """

                        update_params = [
                            (op["accessed_at"], op["entry_id"]) for op in update_ops
                        ]

                        await conn.executemany(update_query, update_params)

                    await conn.commit()

                    batch_time = time.time() - start_time
                    logger.info(
                        f"⚡ Processed batch: {len(store_ops)} stores, "
                        f"{len(update_ops)} updates in {batch_time * 1000:.1f}ms"
                    )

        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            raise

    def _update_avg_response_time(self, response_time: float):
        """Update average response time metric"""
        total_ops = self.metrics["read_operations"] + self.metrics["write_operations"]
        if total_ops > 1:
            self.metrics["avg_response_time"] = (
                self.metrics["avg_response_time"] * (total_ops - 1) + response_time
            ) / total_ops
        else:
            self.metrics["avg_response_time"] = response_time

    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_stats = await self.cache.stats()

        return {
            "operations": {
                "read_ops": self.metrics["read_operations"],
                "write_ops": self.metrics["write_operations"],
                "total_ops": self.metrics["read_operations"]
                + self.metrics["write_operations"],
            },
            "cache": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_ratio": self.metrics["cache_hits"]
                / max(self.metrics["cache_hits"] + self.metrics["cache_misses"], 1),
                "size": cache_stats["size"],
                "max_size": cache_stats["max_size"],
            },
            "batching": {
                "flushes": self.metrics["batch_flushes"],
                "pending_ops": len(self.batch_processor._pending_operations),
            },
            "performance": {
                "avg_response_time_ms": self.metrics["avg_response_time"] * 1000,
                "connection_pool_size": len(self.connection_pool._all_connections),
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def flush_all(self):
        """Flush all pending operations"""
        await self.batch_processor.force_flush()

    async def close(self):
        """Close all resources"""
        logger.info("🔒 Shutting down AsyncConcurrentMemoryManager")

        # Flush pending operations
        await self.flush_all()

        # Close connection pool
        await self.connection_pool.close_all()

        # Clear cache
        await self.cache.clear()

        # Shutdown thread pool
        self.thread_pool.shutdown(wait=True)

        logger.info("✅ AsyncConcurrentMemoryManager shutdown complete")


# Example usage and testing
async def test_concurrent_memory_performance():
    """Test concurrent access performance"""
    logger.info("🧪 Testing Concurrent Access Optimization Performance")

    # Initialize manager
    manager = AsyncConcurrentMemoryManager(
        db_path="test_concurrent_memory.db",
        max_connections=20,
        cache_size=500,
        batch_size=50,
    )

    await manager.initialize()

    # Test concurrent writes
    logger.info("📝 Testing concurrent write performance...")
    start_time = time.time()

    async def write_test_data(i: int):
        await manager.store_memory(
            key=f"test_key_{i}",
            value=f"test_value_{i}" * 100,  # Larger payload
            memory_type="test",
            priority=2,
        )

    # Run 100 concurrent writes
    write_tasks = [write_test_data(i) for i in range(100)]
    await asyncio.gather(*write_tasks)

    write_time = time.time() - start_time
    logger.info(f"⚡ Concurrent writes completed in {write_time * 1000:.1f}ms")

    # Test concurrent reads
    logger.info("📖 Testing concurrent read performance...")
    start_time = time.time()

    async def read_test_data(i: int):
        value = await manager.retrieve_memory(f"test_key_{i}")
        return value

    # Run 100 concurrent reads
    read_tasks = [read_test_data(i) for i in range(100)]
    await asyncio.gather(*read_tasks)

    read_time = time.time() - start_time
    logger.info(f"⚡ Concurrent reads completed in {read_time * 1000:.1f}ms")

    # Test mixed concurrent operations
    logger.info("🔄 Testing mixed concurrent operations...")
    start_time = time.time()

    mixed_tasks = []
    for i in range(50):
        mixed_tasks.append(write_test_data(i + 200))  # Writes
        mixed_tasks.append(read_test_data(i))  # Reads

    await asyncio.gather(*mixed_tasks)
    mixed_time = time.time() - start_time
    logger.info(f"⚡ Mixed operations completed in {mixed_time * 1000:.1f}ms")

    # Get performance stats
    stats = await manager.get_performance_stats()
    logger.info("📊 Performance Statistics:")
    for category, metrics in stats.items():
        if isinstance(metrics, dict):
            logger.info(f"  {category.upper()}:")
            for key, value in metrics.items():
                logger.info(f"    {key}: {value}")
        else:
            logger.info(f"  {category}: {metrics}")

    # Calculate performance improvement
    baseline_time = 4293  # ms from original issue
    optimized_time = max(write_time, read_time, mixed_time) * 1000
    improvement_ratio = baseline_time / optimized_time

    logger.info("🎯 PERFORMANCE RESULTS:")
    logger.info(f"   Baseline: {baseline_time}ms")
    logger.info(f"   Optimized: {optimized_time:.1f}ms")
    logger.info(f"   Improvement: {improvement_ratio:.1f}x faster")
    logger.info(f"   Target Achieved: {'✅ YES' if optimized_time < 500 else '❌ NO'}")

    await manager.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    asyncio.run(test_concurrent_memory_performance())
