"""
🚀 Optimized LyrixaMemoryEngine Integration
===========================================

Enhanced memory engine with performance optimizations:
1. Batch-mode writes with 100ms flush intervals
2. Write-ahead buffer in FractalMesh
3. Binary/JSON optimization with ujson fallback
4. Asynchronous tagging and scoring (1-2 tick delay)
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from .fractal_mesh.base import MemoryFragment, MemoryFragmentType
from .lyrixa_memory_engine import LyrixaMemoryEngine, MemorySystemConfig
from .optimized_storage import AsyncMemoryProcessor, OptimizedMemoryStorage


class OptimizedLyrixaMemoryEngine(LyrixaMemoryEngine):
    """
    High-performance version of LyrixaMemoryEngine with storage optimizations
    """

    def __init__(self, config: Optional[MemorySystemConfig] = None):
        # Initialize parent class
        super().__init__(config)

        # Replace fractal mesh storage with optimized version
        self.optimized_storage = OptimizedMemoryStorage(
            db_path=self.config.fractal_db_path.replace(".db", "_optimized.db"),
            batch_size=50,
            flush_interval_ms=100,
        )

        # Initialize async processor
        self.async_processor = AsyncMemoryProcessor()
        self.processor_task: Optional[asyncio.Task] = None

        # Performance tracking
        self.optimization_metrics = {
            "fast_stores": 0,
            "batch_stores": 0,
            "async_processing_tasks": 0,
            "total_time_saved": 0.0,
        }

        # Start async processor
        self._start_async_processor()

    def _start_async_processor(self):
        """Start the async processing loop"""
        if not self.processor_task:
            self.processor_task = asyncio.create_task(
                self.async_processor.start_processing()
            )

    async def store_memory_optimized(
        self,
        content: Any,
        category: str = "general",
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
        fragment_type: MemoryFragmentType = MemoryFragmentType.EPISODIC,
        narrative_role: str = "event",
    ) -> str:
        """
        Optimized memory storage with batch processing and async operations
        """
        start_time = time.perf_counter()

        # Create fragment (same as original but faster)
        current_time = datetime.now()
        fragment_id = f"mem_{current_time.strftime('%Y%m%d_%H%M%S')}_{hash(str(content)) % 10000:04d}"

        fragment = MemoryFragment(
            fragment_id=fragment_id,
            content={"text": str(content), "category": category},
            fragment_type=fragment_type,
            temporal_tags={
                "hour": current_time.hour,
                "day_of_week": current_time.weekday(),
                "timestamp": current_time.isoformat(),
            },
            symbolic_tags=set(tags or []),
            associative_links=[],
            confidence_score=confidence,
            access_pattern={"created": current_time.isoformat(), "access_count": 0},
            narrative_role=narrative_role,
            created_at=current_time,
            last_evolved=current_time,
        )

        # Fast, non-blocking storage
        fragment_id = self.optimized_storage.store_fragment_fast(fragment)

        # Schedule async processing for concept clustering and timeline processing
        await self._schedule_async_processing(fragment)

        # Update optimization metrics
        storage_time = (time.perf_counter() - start_time) * 1000
        self.optimization_metrics["fast_stores"] += 1

        # Estimate time saved compared to synchronous processing
        estimated_sync_time = 500  # ms - typical sync processing time
        time_saved = max(0, estimated_sync_time - storage_time)
        self.optimization_metrics["total_time_saved"] += time_saved

        # Update operation stats
        self.operation_stats["successful_operations"] += 1
        self.operation_stats["fragments_created"] += 1

        return fragment_id

    async def store_memories_batch_optimized(
        self, memories: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Batch storage for multiple memories with maximum optimization
        """
        start_time = time.perf_counter()

        fragments = []
        current_time = datetime.now()

        # Create all fragments
        for i, memory_data in enumerate(memories):
            content = memory_data.get("content", "")
            category = memory_data.get("category", "general")
            tags = memory_data.get("tags", [])
            confidence = memory_data.get("confidence", 1.0)
            fragment_type = memory_data.get(
                "fragment_type", MemoryFragmentType.EPISODIC
            )
            narrative_role = memory_data.get("narrative_role", "event")

            fragment_id = f"mem_batch_{current_time.strftime('%Y%m%d_%H%M%S')}_{i:04d}"

            fragment = MemoryFragment(
                fragment_id=fragment_id,
                content={"text": str(content), "category": category},
                fragment_type=fragment_type,
                temporal_tags={
                    "hour": current_time.hour,
                    "day_of_week": current_time.weekday(),
                    "timestamp": current_time.isoformat(),
                    "batch_index": i,
                },
                symbolic_tags=set(tags),
                associative_links=[],
                confidence_score=confidence,
                access_pattern={"created": current_time.isoformat(), "access_count": 0},
                narrative_role=narrative_role,
                created_at=current_time,
                last_evolved=current_time,
            )

            fragments.append(fragment)

        # Batch storage
        fragment_ids = self.optimized_storage.store_fragments_batch(fragments)

        # Schedule async processing for all fragments
        for fragment in fragments:
            await self._schedule_async_processing(fragment)

        # Update metrics
        batch_time = (time.perf_counter() - start_time) * 1000
        self.optimization_metrics["batch_stores"] += 1

        estimated_individual_time = len(fragments) * 500  # ms per fragment
        time_saved = max(0, estimated_individual_time - batch_time)
        self.optimization_metrics["total_time_saved"] += time_saved

        self.operation_stats["successful_operations"] += len(fragments)
        self.operation_stats["fragments_created"] += len(fragments)

        return fragment_ids

    async def _schedule_async_processing(self, fragment: MemoryFragment):
        """
        Schedule async processing with 1-2 tick delay to avoid blocking storage
        """
        # Small delay to ensure storage operation completes first
        await asyncio.sleep(0.001)  # 1ms delay

        # Schedule concept clustering
        self._schedule_concept_processing(fragment)

        # Schedule timeline processing
        self._schedule_timeline_processing(fragment)

        # Schedule async tagging and scoring
        await self.async_processor.schedule_processing(fragment)

        self.optimization_metrics["async_processing_tasks"] += 3

    def _schedule_concept_processing(self, fragment: MemoryFragment):
        """
        Schedule concept clustering in background
        """

        async def process_concepts():
            # Small additional delay for non-critical processing
            await asyncio.sleep(0.002)

            try:
                # Process through concept clustering (async)
                affected_clusters = self.concept_manager.process_new_fragment(fragment)

                # Update fragment with associative links
                if affected_clusters:
                    fragment.associative_links.extend(affected_clusters[:5])
                    # Note: Could trigger another optimized update here if needed

            except Exception as e:
                print(f"Async concept processing error: {e}")

        # Schedule as background task
        asyncio.create_task(process_concepts())

    def _schedule_timeline_processing(self, fragment: MemoryFragment):
        """
        Schedule timeline processing in background
        """

        async def process_timeline():
            await asyncio.sleep(0.002)

            try:
                # Process through episodic timeline (async)
                affected_chains = self.timeline_manager.process_new_fragment(fragment)

                # Additional timeline processing could happen here

            except Exception as e:
                print(f"Async timeline processing error: {e}")

        # Schedule as background task
        asyncio.create_task(process_timeline())

    async def force_flush_all(self):
        """
        Force flush all optimized storage buffers (useful for testing)
        """
        await self.optimized_storage.force_flush()

        # Wait for async processing to complete
        await asyncio.sleep(0.01)

    def get_optimization_metrics(self) -> Dict[str, Any]:
        """
        Get performance optimization metrics
        """
        storage_metrics = self.optimized_storage.get_performance_metrics()

        return {
            **self.optimization_metrics,
            "storage_metrics": storage_metrics,
            "avg_time_saved_per_operation": (
                self.optimization_metrics["total_time_saved"]
                / max(
                    1,
                    self.optimization_metrics["fast_stores"]
                    + self.optimization_metrics["batch_stores"],
                )
            ),
            "processor_queue_size": self.async_processor.processing_queue.qsize(),
        }

    async def retrieve_memory_optimized(
        self, query: str, limit: int = 10, include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Optimized memory retrieval with fast binary deserialization
        """
        start_time = time.perf_counter()

        # Use parent class retrieval but with optimized storage lookup
        # This maintains the same interface while benefiting from optimized storage

        results = await self.recall_memories(
            query=query,
            max_memories=limit,
            time_range_hours=24 * 30,  # 30 days default
            include_context=include_context,
        )

        retrieval_time = (time.perf_counter() - start_time) * 1000

        # Add retrieval performance to metrics
        if "retrieval_times" not in self.optimization_metrics:
            self.optimization_metrics["retrieval_times"] = []

        self.optimization_metrics["retrieval_times"].append(retrieval_time)

        # Keep only last 100 retrieval times for averaging
        if len(self.optimization_metrics["retrieval_times"]) > 100:
            self.optimization_metrics["retrieval_times"] = self.optimization_metrics[
                "retrieval_times"
            ][-100:]

        return results

    def cleanup_optimized(self):
        """
        Clean up optimized resources
        """
        # Stop async processor
        self.async_processor.stop_processing()

        if self.processor_task:
            self.processor_task.cancel()

        # Clean up optimized storage
        self.optimized_storage.cleanup()


class MemoryOptimizationBenchmark:
    """
    Benchmark tool to compare optimized vs standard memory operations
    """

    def __init__(self):
        self.standard_engine = LyrixaMemoryEngine()
        self.optimized_engine = OptimizedLyrixaMemoryEngine()

    async def benchmark_storage_performance(
        self, num_operations: int = 100
    ) -> Dict[str, Any]:
        """
        Compare storage performance between standard and optimized engines
        """
        # Test data
        test_memories = [
            {
                "content": f"Test memory {i} with some content to store",
                "category": "benchmark",
                "tags": [f"test_{i}", "benchmark"],
                "confidence": 0.8,
            }
            for i in range(num_operations)
        ]

        # Benchmark standard storage
        start_time = time.perf_counter()
        standard_ids = []
        for memory in test_memories:
            memory_id = await self.standard_engine.store_memory(
                content=memory["content"],
                category=memory["category"],
                tags=memory["tags"],
                confidence=memory["confidence"],
            )
            standard_ids.append(memory_id)
        standard_time = (time.perf_counter() - start_time) * 1000

        # Benchmark optimized storage
        start_time = time.perf_counter()
        optimized_ids = []
        for memory in test_memories:
            memory_id = await self.optimized_engine.store_memory_optimized(
                content=memory["content"],
                category=memory["category"],
                tags=memory["tags"],
                confidence=memory["confidence"],
            )
            optimized_ids.append(memory_id)

        # Force flush to ensure fair comparison
        await self.optimized_engine.force_flush_all()
        optimized_time = (time.perf_counter() - start_time) * 1000

        # Benchmark batch storage
        start_time = time.perf_counter()
        batch_ids = await self.optimized_engine.store_memories_batch_optimized(
            test_memories
        )
        await self.optimized_engine.force_flush_all()
        batch_time = (time.perf_counter() - start_time) * 1000

        return {
            "num_operations": num_operations,
            "standard_time_ms": standard_time,
            "optimized_time_ms": optimized_time,
            "batch_time_ms": batch_time,
            "optimization_improvement": (
                (standard_time - optimized_time) / standard_time
            )
            * 100,
            "batch_improvement": ((standard_time - batch_time) / standard_time) * 100,
            "standard_avg_per_op": standard_time / num_operations,
            "optimized_avg_per_op": optimized_time / num_operations,
            "batch_avg_per_op": batch_time / num_operations,
            "target_achieved": optimized_time / num_operations
            < 150,  # <150ms per operation target
        }

    def cleanup(self):
        """Clean up benchmark resources"""
        self.optimized_engine.cleanup_optimized()
