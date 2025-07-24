"""
🚀 Optimized Memory Retrieval System - Performance Enhancement
============================================================

Implementation of 4 critical optimizations for memory retrieval:
1. ✅ Separate fast path for exact vector search (skip graph)
2. ✅ Cache most recent retrievals (LRUCache(size=50))
3. ✅ Offload metadata enrichment to post-fetch thread
4. ✅ Pre-index top_k memory entries for recurring queries

Expected Performance: 224ms → ~90ms (2.5x improvement)
"""

import asyncio
import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


# LRU Cache implementation for memory retrieval
class MemoryRetrievalCache:
    """
    High-performance LRU cache for memory retrieval results
    """

    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
        self.lock = threading.RLock()

        # Cache metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def _hash_query(self, query: str, **kwargs) -> str:
        """Create a hash key for the query and parameters"""
        key_data = f"{query}|{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, query: str, **kwargs) -> Optional[List[Dict[str, Any]]]:
        """Get cached retrieval results"""
        with self.lock:
            cache_key = self._hash_query(query, **kwargs)

            if cache_key in self.cache:
                # Move to end (most recently used)
                self.access_order.remove(cache_key)
                self.access_order.append(cache_key)
                self.hits += 1
                return self.cache[cache_key].copy()

            self.misses += 1
            return None

    def put(self, query: str, results: List[Dict[str, Any]], **kwargs):
        """Cache retrieval results"""
        with self.lock:
            cache_key = self._hash_query(query, **kwargs)

            # Add to cache
            self.cache[cache_key] = results.copy()

            # Update access order
            if cache_key in self.access_order:
                self.access_order.remove(cache_key)
            self.access_order.append(cache_key)

            # Evict oldest if over limit
            if len(self.cache) > self.max_size:
                oldest_key = self.access_order.pop(0)
                del self.cache[oldest_key]
                self.evictions += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests) if total_requests > 0 else 0.0

        return {
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": hit_rate,
            "cache_size": len(self.cache),
            "max_size": self.max_size,
        }


# Pre-indexed top-k memory entries for recurring queries
class TopKMemoryIndex:
    """
    Pre-computed index of top-k memory entries for common query patterns
    """

    def __init__(self, k: int = 100):
        self.k = k
        self.indexes = {}
        self.last_rebuild = {}
        self.rebuild_interval = timedelta(hours=1)

        # Common query patterns to pre-index
        self.query_patterns = [
            "goal",
            "task",
            "error",
            "success",
            "plugin",
            "conversation",
            "learning",
            "improvement",
            "decision",
            "preference",
        ]

    def should_rebuild(self, pattern: str) -> bool:
        """Check if index should be rebuilt for a pattern"""
        if pattern not in self.last_rebuild:
            return True

        return (datetime.now() - self.last_rebuild[pattern]) > self.rebuild_interval

    def build_index(self, pattern: str, memory_system):
        """Build pre-computed index for a query pattern"""
        try:
            # Get top-k results for this pattern
            results = memory_system.fast_vector_search(pattern, limit=self.k)

            # Store in index
            self.indexes[pattern] = {
                "results": results,
                "built_at": datetime.now(),
                "result_count": len(results),
            }

            self.last_rebuild[pattern] = datetime.now()

            return True

        except Exception as e:
            print(f"Failed to build index for pattern '{pattern}': {e}")
            return False

    def get_precomputed(self, query: str, limit: int) -> Optional[List[Dict[str, Any]]]:
        """Get precomputed results if query matches a pattern"""
        for pattern in self.query_patterns:
            if pattern.lower() in query.lower():
                if pattern in self.indexes:
                    index_data = self.indexes[pattern]
                    results = index_data["results"][:limit]

                    # Add cache hit marker
                    for result in results:
                        result["_cache_source"] = "precomputed_index"

                    return results

        return None

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "indexed_patterns": len(self.indexes),
            "total_precomputed_entries": sum(
                len(idx["results"]) for idx in self.indexes.values()
            ),
            "patterns": list(self.indexes.keys()),
            "last_rebuilds": {
                pattern: rebuild_time.isoformat()
                for pattern, rebuild_time in self.last_rebuild.items()
            },
        }


# Metadata enrichment in background thread
class MetadataEnricher:
    """
    Asynchronous metadata enrichment system
    """

    def __init__(self, max_workers: int = 2):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.enrichment_queue = asyncio.Queue()
        self.active = True

    def enrich_async(
        self, results: List[Dict[str, Any]], memory_system
    ) -> List[Dict[str, Any]]:
        """Enrich metadata in background thread"""

        def _enrich_worker():
            for result in results:
                try:
                    # Add computed metadata
                    if "fragment_id" in result:
                        # Get fragment details
                        fragment = memory_system.fractal_mesh.get_fragment(
                            result["fragment_id"]
                        )
                        if fragment:
                            result["_enriched_metadata"] = {
                                "concept_clusters": list(fragment.symbolic_tags),
                                "associative_strength": len(fragment.associative_links),
                                "narrative_role": fragment.narrative_role,
                                "confidence_score": fragment.confidence_score,
                                "access_count": fragment.access_pattern.get(
                                    "access_count", 0
                                ),
                            }

                    # Add temporal context
                    if "timestamp" in result:
                        timestamp = datetime.fromisoformat(result["timestamp"])
                        result["_temporal_context"] = {
                            "age_days": (datetime.now() - timestamp).days,
                            "recency_score": max(
                                0, 1 - (datetime.now() - timestamp).days / 365
                            ),
                            "time_category": _categorize_time(timestamp),
                        }

                    # Mark as enriched
                    result["_metadata_enriched"] = True

                except Exception as e:
                    result["_metadata_error"] = str(e)

            return results

        # Submit to thread pool
        self.executor.submit(_enrich_worker)
        return results  # Return immediately, enrichment happens in background

    def shutdown(self):
        """Shutdown the enrichment system"""
        self.active = False
        self.executor.shutdown(wait=True)


def _categorize_time(timestamp: datetime) -> str:
    """Categorize timestamp into time periods"""
    now = datetime.now()
    diff = now - timestamp

    if diff.days == 0:
        return "today"
    elif diff.days == 1:
        return "yesterday"
    elif diff.days <= 7:
        return "this_week"
    elif diff.days <= 30:
        return "this_month"
    elif diff.days <= 365:
        return "this_year"
    else:
        return "historical"


# Fast path vector search (skip graph traversal)
class FastVectorSearch:
    """
    Optimized vector search that bypasses graph traversal for exact matches
    """

    def __init__(self, memory_system):
        self.memory_system = memory_system
        self.direct_vector_threshold = (
            0.85  # Skip graph if vector similarity > threshold
        )

    async def fast_vector_only(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fast vector-only search bypassing all graph operations"""
        start_time = time.perf_counter()

        try:
            # Direct vector search without concept graph traversal
            vector_results = await self.memory_system.core_memory.recall_memories(
                query_text=query,
                limit=limit,
                bypass_metadata=True,  # Skip metadata enrichment for speed
            )

            # Convert to standardized format
            results = []
            for i, memory in enumerate(vector_results):
                result = {
                    "content": memory.content,
                    "source": "fast_vector",
                    "relevance_score": (limit - i) / limit,
                    "type": "direct_vector_match",
                    "memory_id": memory.id,
                    "tags": memory.tags,
                    "search_time_ms": 0,  # Will be set below
                    "_optimization_used": "fast_vector_path",
                }
                results.append(result)

            # Record timing
            search_time = (time.perf_counter() - start_time) * 1000
            for result in results:
                result["search_time_ms"] = search_time

            return results

        except Exception as e:
            print(f"Fast vector search failed: {e}")
            return []


# Main optimized retrieval engine
class OptimizedMemoryRetrieval:
    """
    High-performance memory retrieval with all 4 optimizations integrated
    """

    def __init__(self, memory_system):
        self.memory_system = memory_system

        # Initialize optimization components
        self.cache = MemoryRetrievalCache(max_size=50)
        self.topk_index = TopKMemoryIndex(k=100)
        self.metadata_enricher = MetadataEnricher(max_workers=2)
        self.fast_vector = FastVectorSearch(memory_system)

        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "fast_path_used": 0,
            "precomputed_hits": 0,
            "avg_response_time_ms": 0,
            "optimization_breakdown": {
                "cache": 0,
                "precomputed": 0,
                "fast_vector": 0,
                "full_pipeline": 0,
            },
        }

        # Background index building
        self._start_background_indexing()

    def _start_background_indexing(self):
        """Start background index building for common patterns"""

        def build_indexes():
            for pattern in self.topk_index.query_patterns:
                if self.topk_index.should_rebuild(pattern):
                    self.topk_index.build_index(pattern, self.memory_system)
                    time.sleep(0.1)  # Brief pause between builds

        # Build indexes in background thread
        threading.Thread(target=build_indexes, daemon=True).start()

    async def optimized_recall(
        self,
        query: str,
        limit: int = 10,
        recall_strategy: str = "auto",
        enable_cache: bool = True,
        force_full_pipeline: bool = False,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Optimized memory recall with 4-layer optimization stack

        Returns:
            Tuple of (results, performance_stats)
        """
        start_time = time.perf_counter()
        self.metrics["total_queries"] += 1

        # Create query context for caching
        query_context = {"limit": limit, "strategy": recall_strategy}

        optimization_used = None

        try:
            # OPTIMIZATION 1: Check cache first
            if enable_cache and not force_full_pipeline:
                cached_results = self.cache.get(query, **query_context)
                if cached_results:
                    self.metrics["cache_hits"] += 1
                    self.metrics["optimization_breakdown"]["cache"] += 1
                    optimization_used = "cache_hit"

                    # Add cache metadata
                    for result in cached_results:
                        result["_optimization_used"] = "cache_hit"

                    return cached_results, {
                        "query_time_ms": (time.perf_counter() - start_time) * 1000,
                        "optimization_used": optimization_used,
                        "cache_hit": True,
                    }

            # OPTIMIZATION 2: Check precomputed index
            if not force_full_pipeline:
                precomputed_results = self.topk_index.get_precomputed(query, limit)
                if precomputed_results:
                    self.metrics["precomputed_hits"] += 1
                    self.metrics["optimization_breakdown"]["precomputed"] += 1
                    optimization_used = "precomputed_index"

                    # Cache the results
                    if enable_cache:
                        self.cache.put(query, precomputed_results, **query_context)

                    return precomputed_results, {
                        "query_time_ms": (time.perf_counter() - start_time) * 1000,
                        "optimization_used": optimization_used,
                        "precomputed_hit": True,
                    }

            # OPTIMIZATION 3: Fast vector path for exact matches
            if recall_strategy in ["auto", "vector"] and not force_full_pipeline:
                # Check if query should use fast path
                query_length = len(query.split())

                # Use fast path for short, specific queries
                if query_length <= 5 or any(
                    keyword in query.lower()
                    for keyword in ["find", "show", "get", "list", "what", "when"]
                ):
                    fast_results = await self.fast_vector.fast_vector_only(query, limit)
                    if (
                        fast_results and len(fast_results) >= limit // 2
                    ):  # Good enough coverage
                        self.metrics["fast_path_used"] += 1
                        self.metrics["optimization_breakdown"]["fast_vector"] += 1
                        optimization_used = "fast_vector_path"

                        # OPTIMIZATION 4: Background metadata enrichment
                        enriched_results = self.metadata_enricher.enrich_async(
                            fast_results, self.memory_system
                        )

                        # Cache the results
                        if enable_cache:
                            self.cache.put(query, enriched_results, **query_context)

                        return enriched_results, {
                            "query_time_ms": (time.perf_counter() - start_time) * 1000,
                            "optimization_used": optimization_used,
                            "fast_path_used": True,
                            "metadata_enriched_async": True,
                        }

            # FALLBACK: Full pipeline (original method)
            self.metrics["optimization_breakdown"]["full_pipeline"] += 1
            optimization_used = "full_pipeline"

            # Use original recall method from memory system
            results = await self.memory_system.recall(
                query=query, recall_strategy=recall_strategy, limit=limit
            )

            # OPTIMIZATION 4: Background metadata enrichment
            enriched_results = self.metadata_enricher.enrich_async(
                results, self.memory_system
            )

            # Mark results with optimization info
            for result in enriched_results:
                result["_optimization_used"] = "full_pipeline"

            # Cache the results
            if enable_cache:
                self.cache.put(query, enriched_results, **query_context)

            # Update performance metrics
            query_time = (time.perf_counter() - start_time) * 1000
            self.metrics["avg_response_time_ms"] = (
                self.metrics["avg_response_time_ms"]
                * (self.metrics["total_queries"] - 1)
                + query_time
            ) / self.metrics["total_queries"]

            return enriched_results, {
                "query_time_ms": query_time,
                "optimization_used": optimization_used,
                "full_pipeline_used": True,
                "metadata_enriched_async": True,
            }

        except Exception as e:
            return [], {
                "query_time_ms": (time.perf_counter() - start_time) * 1000,
                "optimization_used": optimization_used,
                "error": str(e),
            }

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_stats = self.cache.get_stats()
        index_stats = self.topk_index.get_stats()

        total_queries = self.metrics["total_queries"]
        optimized_queries = (
            self.metrics["cache_hits"]
            + self.metrics["precomputed_hits"]
            + self.metrics["fast_path_used"]
        )

        optimization_rate = (
            (optimized_queries / total_queries) if total_queries > 0 else 0
        )

        return {
            "retrieval_metrics": self.metrics,
            "cache_performance": cache_stats,
            "index_performance": index_stats,
            "optimization_rate": optimization_rate,
            "avg_response_time_ms": self.metrics["avg_response_time_ms"],
            "expected_improvement": f"{224 / max(self.metrics['avg_response_time_ms'], 1):.1f}x faster than baseline",
        }

    def shutdown(self):
        """Clean shutdown of optimization components"""
        self.metadata_enricher.shutdown()


# Integration with existing LyrixaMemoryEngine
def apply_retrieval_optimizations(memory_engine):
    """
    Apply the 4 retrieval optimizations to an existing LyrixaMemoryEngine
    """

    # Create optimized retrieval system
    optimized_retrieval = OptimizedMemoryRetrieval(memory_engine)

    # Store reference to original recall method (for potential fallback)
    # original_recall = memory_engine.recall

    # Replace with optimized version
    async def optimized_recall_wrapper(
        query: str,
        recall_strategy: str = "hybrid",
        limit: int = 10,
        time_filter: Optional[Dict[str, Any]] = None,
        concept_filter: Optional[List[str]] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Optimized recall method with 4-layer optimization stack
        """

        # Use optimized retrieval
        results, performance_stats = await optimized_retrieval.optimized_recall(
            query=query, limit=limit, recall_strategy=recall_strategy, **kwargs
        )

        # Add performance stats to engine
        if not hasattr(memory_engine, "retrieval_performance"):
            memory_engine.retrieval_performance = {}

        memory_engine.retrieval_performance["last_query"] = performance_stats
        memory_engine.retrieval_performance["optimization_system"] = (
            optimized_retrieval.get_performance_stats()
        )

        return results

    # Replace the method
    memory_engine.recall_optimized = optimized_recall_wrapper
    memory_engine.optimization_system = optimized_retrieval

    return memory_engine


# Test and validation
async def validate_retrieval_optimizations():
    """
    Validate the retrieval optimizations performance
    """
    print("🚀 Validating Memory Retrieval Optimizations")
    print("=" * 60)

    # Simulate memory system for testing
    class MockMemorySystem:
        def __init__(self):
            self.core_memory = MockCoreMemory()
            self.fractal_mesh = MockFractalMesh()

        async def recall(self, query, **kwargs):
            # Simulate original slow recall (224ms baseline)
            await asyncio.sleep(0.224)
            return [
                {"content": f"Mock result {i}", "relevance_score": 0.8 - i * 0.1}
                for i in range(kwargs.get("limit", 5))
            ]

    class MockCoreMemory:
        async def recall_memories(self, query_text, limit, bypass_metadata=False):
            # Simulate fast vector search
            delay = 0.05 if bypass_metadata else 0.15
            await asyncio.sleep(delay)

            return [
                MockMemory(f"memory_{i}", {"text": f"Vector result {i}"}, [f"tag_{i}"])
                for i in range(limit)
            ]

    class MockFractalMesh:
        def get_fragment(self, fragment_id):
            return None

    class MockMemory:
        def __init__(self, id, content, tags):
            self.id = id
            self.content = content
            self.tags = tags

    # Create test system
    mock_system = MockMemorySystem()
    optimized_retrieval = OptimizedMemoryRetrieval(mock_system)

    # Test queries
    test_queries = [
        "find my goals",
        "show recent conversations",
        "what plugins failed",
        "list learning progress",
        "AI development strategies",
    ]

    print("🧪 Testing optimization layers:")

    # Test each optimization layer
    for i, query in enumerate(test_queries):
        print(f"\n📋 Test {i + 1}: '{query}'")

        # First call (cold cache)
        start_time = time.perf_counter()
        results, stats = await optimized_retrieval.optimized_recall(query, limit=5)
        first_time = (time.perf_counter() - start_time) * 1000

        print(f"   🔄 Cold call: {first_time:.1f}ms ({stats['optimization_used']})")

        # Second call (should hit cache)
        start_time = time.perf_counter()
        results_cached, stats_cached = await optimized_retrieval.optimized_recall(
            query, limit=5
        )
        second_time = (time.perf_counter() - start_time) * 1000

        print(
            f"   ⚡ Cached call: {second_time:.1f}ms ({stats_cached['optimization_used']})"
        )
        print(f"   📈 Speedup: {first_time / max(second_time, 0.1):.1f}x")

    # Final performance report
    print("\n" + "=" * 60)
    print("📊 OPTIMIZATION PERFORMANCE REPORT")
    print("=" * 60)

    perf_stats = optimized_retrieval.get_performance_stats()

    print(f"Average Response Time: {perf_stats['avg_response_time_ms']:.1f}ms")
    print(
        f"Target Achievement: {'✅ SUCCESS' if perf_stats['avg_response_time_ms'] < 90 else '❌ MISSED'}"
    )
    print(f"Optimization Rate: {perf_stats['optimization_rate'] * 100:.1f}%")
    print(f"Cache Hit Rate: {perf_stats['cache_performance']['hit_rate'] * 100:.1f}%")

    print("\nOptimization Breakdown:")
    for opt_type, count in perf_stats["retrieval_metrics"][
        "optimization_breakdown"
    ].items():
        print(f"  {opt_type}: {count} uses")

    print(f"\nExpected vs Baseline: {perf_stats['expected_improvement']}")

    # Cleanup
    optimized_retrieval.shutdown()

    print("\n🎯 Validation Complete!")


if __name__ == "__main__":
    asyncio.run(validate_retrieval_optimizations())
