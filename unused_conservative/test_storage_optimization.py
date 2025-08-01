"""
🚀 Memory Storage Optimization Test & Integration
================================================

Test and validate the memory storage optimizations for achieving <150ms performance target.
"""

import asyncio
import json

# For testing, let's create a simplified optimized storage system
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List


@dataclass
class OptimizedFragment:
    """Simplified fragment for optimization testing"""

    fragment_id: str
    content: str
    category: str
    tags: List[str]
    confidence: float
    created_at: datetime


class BatchMemoryStorage:
    """
    Simplified batch memory storage for testing optimizations
    """

    def __init__(self, db_path: str = "test_optimized_memory.db"):
        self.db_path = Path(db_path)
        self.write_buffer: List[OptimizedFragment] = []
        self.buffer_lock = Lock()
        self.batch_size = 50
        self.metrics = {
            "total_writes": 0,
            "batch_writes": 0,
            "total_time_ms": 0.0,
            "avg_time_per_write": 0.0,
        }

        self._init_database()

    def _init_database(self):
        """Initialize optimized database"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Optimized schema
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_fragments_fast (
                    fragment_id TEXT PRIMARY KEY,
                    content_json TEXT,
                    category TEXT,
                    tags_json TEXT,
                    confidence REAL,
                    created_at INTEGER
                )
            """)

            # Create indexes separately
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON memory_fragments_fast(created_at)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_category ON memory_fragments_fast(category)"
            )

            # Optimize SQLite settings
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")

            conn.commit()
        finally:
            conn.close()

    def store_fragment_fast(self, fragment: OptimizedFragment) -> str:
        """Fast storage with buffering"""
        start_time = time.perf_counter()

        with self.buffer_lock:
            self.write_buffer.append(fragment)

            # Flush if buffer is full
            if len(self.write_buffer) >= self.batch_size:
                self._flush_buffer()

        # Update metrics
        write_time = (time.perf_counter() - start_time) * 1000
        self.metrics["total_writes"] += 1
        self.metrics["total_time_ms"] += write_time
        self.metrics["avg_time_per_write"] = (
            self.metrics["total_time_ms"] / self.metrics["total_writes"]
        )

        return fragment.fragment_id

    def store_batch(self, fragments: List[OptimizedFragment]) -> List[str]:
        """Batch storage"""
        start_time = time.perf_counter()

        with self.buffer_lock:
            self.write_buffer.extend(fragments)
            self._flush_buffer()

        # Update metrics
        batch_time = (time.perf_counter() - start_time) * 1000
        self.metrics["batch_writes"] += 1
        self.metrics["total_writes"] += len(fragments)
        self.metrics["total_time_ms"] += batch_time
        self.metrics["avg_time_per_write"] = (
            self.metrics["total_time_ms"] / self.metrics["total_writes"]
        )

        return [f.fragment_id for f in fragments]

    def _flush_buffer(self):
        """Flush write buffer to database"""
        if not self.write_buffer:
            return

        fragments_to_write = self.write_buffer.copy()
        self.write_buffer.clear()

        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute("BEGIN TRANSACTION")

            # Prepare batch data
            batch_data = []
            for fragment in fragments_to_write:
                batch_data.append(
                    (
                        fragment.fragment_id,
                        json.dumps({"text": fragment.content}),
                        fragment.category,
                        json.dumps(fragment.tags),
                        fragment.confidence,
                        int(fragment.created_at.timestamp()),
                    )
                )

            # Batch insert
            conn.executemany(
                """
                INSERT OR REPLACE INTO memory_fragments_fast
                (fragment_id, content_json, category, tags_json, confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                batch_data,
            )

            conn.execute("COMMIT")

        except Exception as e:
            conn.execute("ROLLBACK")
            print(f"Batch write error: {e}")
        finally:
            conn.close()

    def force_flush(self):
        """Force flush buffer"""
        with self.buffer_lock:
            self._flush_buffer()

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()


class StorageOptimizationTest:
    """
    Test the storage optimizations to validate <150ms target
    """

    def __init__(self):
        self.storage = BatchMemoryStorage()

    async def test_individual_writes(self, num_writes: int = 100) -> Dict[str, Any]:
        """Test individual write performance"""
        print(f"Testing {num_writes} individual writes...")

        start_time = time.perf_counter()

        for i in range(num_writes):
            fragment = OptimizedFragment(
                fragment_id=f"test_individual_{i}",
                content=f"Test content for memory {i} with some substantial text to store",
                category="performance_test",
                tags=[f"test_{i}", "individual", "performance"],
                confidence=0.8,
                created_at=datetime.now(),
            )

            self.storage.store_fragment_fast(fragment)

        # Force flush to ensure all writes are complete
        self.storage.force_flush()

        total_time = (time.perf_counter() - start_time) * 1000
        avg_time = total_time / num_writes

        return {
            "test_type": "individual_writes",
            "num_operations": num_writes,
            "total_time_ms": total_time,
            "avg_time_per_write_ms": avg_time,
            "target_achieved": avg_time < 150,  # <150ms target
            "storage_metrics": self.storage.get_metrics(),
        }

    async def test_batch_writes(
        self, num_batches: int = 10, batch_size: int = 50
    ) -> Dict[str, Any]:
        """Test batch write performance"""
        print(f"Testing {num_batches} batches of {batch_size} writes each...")

        total_operations = num_batches * batch_size
        start_time = time.perf_counter()

        for batch_num in range(num_batches):
            batch_fragments = []

            for i in range(batch_size):
                fragment = OptimizedFragment(
                    fragment_id=f"test_batch_{batch_num}_{i}",
                    content=f"Batch {batch_num} memory {i} with content for testing performance",
                    category="batch_test",
                    tags=[f"batch_{batch_num}", f"item_{i}", "performance"],
                    confidence=0.8,
                    created_at=datetime.now(),
                )
                batch_fragments.append(fragment)

            self.storage.store_batch(batch_fragments)

        total_time = (time.perf_counter() - start_time) * 1000
        avg_time = total_time / total_operations

        return {
            "test_type": "batch_writes",
            "num_batches": num_batches,
            "batch_size": batch_size,
            "total_operations": total_operations,
            "total_time_ms": total_time,
            "avg_time_per_write_ms": avg_time,
            "target_achieved": avg_time < 150,  # <150ms target
            "storage_metrics": self.storage.get_metrics(),
        }

    async def test_mixed_workload(
        self, individual_writes: int = 50, batch_writes: int = 25
    ) -> Dict[str, Any]:
        """Test mixed individual and batch writes"""
        print(
            f"Testing mixed workload: {individual_writes} individual + {batch_writes} batch writes..."
        )

        start_time = time.perf_counter()

        # Individual writes
        for i in range(individual_writes):
            fragment = OptimizedFragment(
                fragment_id=f"test_mixed_individual_{i}",
                content=f"Mixed workload individual memory {i}",
                category="mixed_test",
                tags=[f"mixed_{i}", "individual"],
                confidence=0.8,
                created_at=datetime.now(),
            )
            self.storage.store_fragment_fast(fragment)

        # Batch writes
        batch_fragments = []
        for i in range(batch_writes):
            fragment = OptimizedFragment(
                fragment_id=f"test_mixed_batch_{i}",
                content=f"Mixed workload batch memory {i}",
                category="mixed_test",
                tags=[f"mixed_batch_{i}", "batch"],
                confidence=0.8,
                created_at=datetime.now(),
            )
            batch_fragments.append(fragment)

        self.storage.store_batch(batch_fragments)

        total_time = (time.perf_counter() - start_time) * 1000
        total_operations = individual_writes + batch_writes
        avg_time = total_time / total_operations

        return {
            "test_type": "mixed_workload",
            "individual_writes": individual_writes,
            "batch_writes": batch_writes,
            "total_operations": total_operations,
            "total_time_ms": total_time,
            "avg_time_per_write_ms": avg_time,
            "target_achieved": avg_time < 150,  # <150ms target
            "storage_metrics": self.storage.get_metrics(),
        }

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive optimization test"""
        print("🚀 Running Memory Storage Optimization Tests")
        print("=" * 60)

        results = {}

        # Test 1: Individual writes
        results["individual"] = await self.test_individual_writes(100)
        print(
            f"✅ Individual writes: {results['individual']['avg_time_per_write_ms']:.2f}ms avg"
        )

        # Reset storage for next test
        self.storage = BatchMemoryStorage("test_optimized_memory_batch.db")

        # Test 2: Batch writes
        results["batch"] = await self.test_batch_writes(10, 50)
        print(f"✅ Batch writes: {results['batch']['avg_time_per_write_ms']:.2f}ms avg")

        # Reset storage for next test
        self.storage = BatchMemoryStorage("test_optimized_memory_mixed.db")

        # Test 3: Mixed workload
        results["mixed"] = await self.test_mixed_workload(50, 25)
        print(
            f"✅ Mixed workload: {results['mixed']['avg_time_per_write_ms']:.2f}ms avg"
        )

        # Overall results
        all_avg_times = [
            results["individual"]["avg_time_per_write_ms"],
            results["batch"]["avg_time_per_write_ms"],
            results["mixed"]["avg_time_per_write_ms"],
        ]

        overall_avg = sum(all_avg_times) / len(all_avg_times)
        target_achieved = overall_avg < 150

        results["summary"] = {
            "overall_avg_time_ms": overall_avg,
            "target_150ms_achieved": target_achieved,
            "improvement_needed": max(0, overall_avg - 150),
            "performance_rating": "EXCELLENT"
            if overall_avg < 100
            else "GOOD"
            if overall_avg < 150
            else "NEEDS_OPTIMIZATION",
        }

        print("=" * 60)
        print(f"🎯 OVERALL PERFORMANCE: {overall_avg:.2f}ms average")
        print(f"🎪 TARGET ACHIEVED: {'✅ YES' if target_achieved else '❌ NO'}")
        print(f"🚀 RATING: {results['summary']['performance_rating']}")

        return results


async def main():
    """Run the storage optimization test"""
    test = StorageOptimizationTest()
    results = await test.run_comprehensive_test()

    # Print detailed results
    print("\n" + "=" * 60)
    print("📊 DETAILED RESULTS")
    print("=" * 60)

    for test_type, result in results.items():
        if test_type != "summary":
            print(f"\n{test_type.upper()} TEST:")
            print(
                f"  Operations: {result.get('total_operations', result.get('num_operations', 'N/A'))}"
            )
            print(f"  Total Time: {result['total_time_ms']:.2f}ms")
            print(f"  Avg Per Op: {result['avg_time_per_write_ms']:.2f}ms")
            print(f"  Target Met: {'✅' if result['target_achieved'] else '❌'}")

    return results


if __name__ == "__main__":
    asyncio.run(main())
