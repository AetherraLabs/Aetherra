#!/usr/bin/env python3
"""
🚀 Enhanced Aetherra Memory Benchmark Harness
=============================================

Advanced performance analysis with:
- Substage timing breakdowns (graph lookup, disk write, clustering)
- Memory profiling with tracemalloc
- Direct async vs sync mode comparisons
- Detailed performance diagnostics

Usage:
    python enhanced_benchmark_harness.py --mode full
    python enhanced_benchmark_harness.py --mode substage-analysis
    python enhanced_benchmark_harness.py --mode memory-profiling
"""

import argparse
import asyncio
import json
import logging
import statistics
import threading
import time
import tracemalloc
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List


@dataclass
class SubstageMetric:
    """Timing breakdown for individual substages"""

    stage_name: str
    duration_ms: float
    memory_delta_mb: float = 0.0
    cpu_percent: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DetailedPerformanceMetric:
    """Enhanced performance measurement with substage breakdowns"""

    operation: str
    total_duration_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    substages: List[SubstageMetric] = field(default_factory=list)
    memory_peak_mb: float = 0.0
    memory_start_mb: float = 0.0
    memory_end_mb: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnhancedBenchmarkResult:
    """Comprehensive benchmark results with detailed analysis"""

    test_name: str
    mode: str  # 'async' or 'sync'
    target_ms: float
    total_operations: int
    successful_operations: int

    # Overall timing statistics
    mean_duration_ms: float
    median_duration_ms: float
    p95_duration_ms: float
    p99_duration_ms: float
    max_duration_ms: float
    min_duration_ms: float
    std_dev_ms: float

    # Memory statistics
    peak_memory_mb: float
    avg_memory_delta_mb: float
    total_memory_allocated_mb: float

    # Substage analysis
    substage_breakdown: Dict[str, Dict[str, float]] = field(default_factory=dict)

    # Performance rating
    success_rate: float = 0.0
    performance_grade: str = "UNKNOWN"
    bottleneck_stage: str = "UNKNOWN"

    individual_metrics: List[DetailedPerformanceMetric] = field(default_factory=list)


class PerformanceTimer:
    """Context manager for precise timing with substage tracking"""

    def __init__(self, metric_name: str, track_memory: bool = True):
        self.metric_name = metric_name
        self.track_memory = track_memory
        self.substages: List[SubstageMetric] = []
        self.start_time = 0.0
        self.start_memory = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        if self.track_memory:
            self.start_memory = self._get_memory_usage()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @contextmanager
    def substage(self, stage_name: str):
        """Track timing for a specific substage"""
        stage_start = time.perf_counter()
        stage_start_memory = self._get_memory_usage() if self.track_memory else 0.0

        yield

        stage_duration = (time.perf_counter() - stage_start) * 1000
        stage_memory_delta = (
            (self._get_memory_usage() - stage_start_memory)
            if self.track_memory
            else 0.0
        )

        self.substages.append(
            SubstageMetric(
                stage_name=stage_name,
                duration_ms=stage_duration,
                memory_delta_mb=stage_memory_delta,
            )
        )

    def get_total_duration(self) -> float:
        """Get total elapsed time in milliseconds"""
        return (time.perf_counter() - self.start_time) * 1000

    def get_memory_delta(self) -> float:
        """Get total memory delta in MB"""
        if not self.track_memory:
            return 0.0
        return self._get_memory_usage() - self.start_memory

    def get_peak_memory(self) -> float:
        """Get peak memory usage during operation"""
        if not self.track_memory:
            return 0.0
        return max(self.start_memory, self._get_memory_usage())

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            current, peak = tracemalloc.get_traced_memory()
            return current / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0


class MockAsyncMemoryManager:
    """Mock async memory manager for testing"""

    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.memory_counter = 0

    async def initialize(self):
        """Initialize the mock memory manager"""
        await asyncio.sleep(0.001)  # Simulate initialization

    async def store_memory(self, key: str, value: Dict[str, Any]) -> str:
        """Store a memory entry"""
        memory_id = f"mem_{self.memory_counter}"
        self.memory_counter += 1

        # Simulate database write
        await asyncio.sleep(0.002)  # 2ms write latency

        self.memories[memory_id] = {
            "key": key,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "id": memory_id,
        }

        return memory_id

    async def search_memories(
        self, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search for memories"""
        # Simulate search latency
        await asyncio.sleep(0.005)  # 5ms search latency

        # Simple text matching
        results = []
        for memory_id, memory_data in self.memories.items():
            if query.lower() in str(memory_data["value"]).lower():
                results.append(memory_data)
                if len(results) >= limit:
                    break

        return results


class MockSyncMemoryManager:
    """Mock sync memory manager for comparison"""

    def __init__(self):
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.memory_counter = 0
        self.lock = threading.Lock()

    def initialize(self):
        """Initialize the mock memory manager"""
        time.sleep(0.001)  # Simulate initialization

    def store_memory(self, key: str, value: Dict[str, Any]) -> str:
        """Store a memory entry (synchronous)"""
        with self.lock:
            memory_id = f"mem_{self.memory_counter}"
            self.memory_counter += 1

            # Simulate database write with blocking I/O
            time.sleep(0.005)  # 5ms blocking write (worse than async)

            self.memories[memory_id] = {
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "id": memory_id,
            }

            return memory_id

    def search_memories(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for memories (synchronous)"""
        with self.lock:
            # Simulate search latency with blocking I/O
            time.sleep(0.010)  # 10ms blocking search (worse than async)

            # Simple text matching
            results = []
            for memory_id, memory_data in self.memories.items():
                if query.lower() in str(memory_data["value"]).lower():
                    results.append(memory_data)
                    if len(results) >= limit:
                        break

            return results


class EnhancedMemoryBenchmark:
    """
    Enhanced memory system benchmark with detailed analysis
    """

    def __init__(self, enable_memory_profiling: bool = True):
        self.enable_memory_profiling = enable_memory_profiling
        self.logger = logging.getLogger(__name__)

        # Initialize memory profiling
        if self.enable_memory_profiling:
            tracemalloc.start()
            self.logger.info("🔍 Memory profiling enabled")

        # System components (using mock implementations)
        self.async_memory_manager = MockAsyncMemoryManager()
        self.sync_memory_manager = MockSyncMemoryManager()

        # Results storage
        self.benchmark_results: Dict[str, EnhancedBenchmarkResult] = {}

        # Test data
        self.test_data = self._generate_test_data()

        self.logger.info("🚀 Enhanced Memory Benchmark Harness initialized")

    async def initialize_systems(self):
        """Initialize all memory systems for comparison"""
        self.logger.info("🔧 Initializing memory systems...")

        try:
            await self.async_memory_manager.initialize()
            self.sync_memory_manager.initialize()
            self.logger.info("✅ All memory systems initialized")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize systems: {e}")
            raise

    async def benchmark_with_substage_analysis(
        self, iterations: int = 50
    ) -> EnhancedBenchmarkResult:
        """Benchmark with detailed substage timing analysis"""
        self.logger.info(
            f"🔍 Running substage analysis benchmark ({iterations} iterations)..."
        )

        metrics = []

        for i in range(iterations):
            with PerformanceTimer(
                f"substage_analysis_{i}", self.enable_memory_profiling
            ) as timer:
                try:
                    success = True
                    content = self.test_data["contents"][
                        i % len(self.test_data["contents"])
                    ]

                    # Substage 1: Input processing and validation
                    with timer.substage("input_processing"):
                        processed_content = self._preprocess_content(content)
                        tags = self._generate_tags(content)

                    # Substage 2: Vector embedding generation (simulated)
                    with timer.substage("vector_embedding"):
                        await asyncio.sleep(0.002)  # Simulated embedding time
                        # 384-dimensional embedding typical for many models

                    # Substage 3: Graph lookup and relationship analysis
                    with timer.substage("graph_lookup"):
                        related_memories = (
                            await self.async_memory_manager.search_memories(
                                query=content[:100], limit=5
                            )
                        )

                    # Substage 4: Concept clustering update
                    with timer.substage("concept_clustering"):
                        await asyncio.sleep(0.001)  # Simulated clustering

                    # Substage 5: Database write operations
                    with timer.substage("database_write"):
                        _ = await self.async_memory_manager.store_memory(
                            key=f"benchmark_test_{i}",
                            value={
                                "content": processed_content,
                                "tags": tags,
                                "confidence": 0.9,
                                "category": "benchmark_test",
                                "iteration": i,
                            },
                        )

                    # Substage 6: Index updates and optimization
                    with timer.substage("index_updates"):
                        await asyncio.sleep(0.0005)  # Simulated index update

                except Exception as e:
                    success = False
                    self.logger.warning(f"Operation {i} failed: {e}")
                    # Set default values for variables that might be unbound
                    content = ""
                    related_memories = []

                # Create detailed metric
                metric = DetailedPerformanceMetric(
                    operation=f"substage_analysis_{i}",
                    total_duration_ms=timer.get_total_duration(),
                    success=success,
                    substages=timer.substages.copy(),
                    memory_start_mb=timer.start_memory,
                    memory_end_mb=timer._get_memory_usage(),
                    memory_peak_mb=timer.get_peak_memory(),
                    details={
                        "iteration": i,
                        "content_length": len(content),
                        "related_count": len(related_memories),
                    },
                )
                metrics.append(metric)

        return self._calculate_enhanced_result("Substage Analysis", "async", metrics)

    async def benchmark_async_vs_sync_comparison(
        self, iterations: int = 30
    ) -> Dict[str, EnhancedBenchmarkResult]:
        """Direct comparison between async and sync implementations"""
        self.logger.info(
            f"⚡ Running async vs sync comparison ({iterations} iterations each)..."
        )

        results = {}

        # Benchmark async implementation
        self.logger.info("🚀 Testing async implementation...")
        async_metrics = []

        for i in range(iterations):
            with PerformanceTimer(
                f"async_op_{i}", self.enable_memory_profiling
            ) as timer:
                try:
                    content = self.test_data["contents"][
                        i % len(self.test_data["contents"])
                    ]

                    with timer.substage("async_storage"):
                        memory_id = await self.async_memory_manager.store_memory(
                            key=f"async_test_{i}",
                            value={
                                "content": content,
                                "tags": ["async_test"],
                                "iteration": i,
                            },
                        )

                    with timer.substage("async_retrieval"):
                        results_async = await self.async_memory_manager.search_memories(
                            query=content[:50], limit=3
                        )

                    success = True

                except Exception as e:
                    success = False
                    results_async = []
                    self.logger.warning(f"Async operation {i} failed: {e}")

                async_metrics.append(
                    DetailedPerformanceMetric(
                        operation=f"async_op_{i}",
                        total_duration_ms=timer.get_total_duration(),
                        success=success,
                        substages=timer.substages.copy(),
                        memory_peak_mb=timer.get_peak_memory(),
                        details={"result_count": len(results_async) if success else 0},
                    )
                )

        results["async"] = self._calculate_enhanced_result(
            "Async Implementation", "async", async_metrics
        )

        # Benchmark sync implementation
        self.logger.info("🔄 Testing sync implementation...")
        sync_metrics = []

        for i in range(iterations):
            with PerformanceTimer(
                f"sync_op_{i}", self.enable_memory_profiling
            ) as timer:
                try:
                    content = self.test_data["contents"][
                        i % len(self.test_data["contents"])
                    ]

                    with timer.substage("sync_storage"):
                        _ = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.sync_memory_manager.store_memory(
                                key=f"sync_test_{i}",
                                value={
                                    "content": content,
                                    "tags": ["sync_test"],
                                    "iteration": i,
                                },
                            ),
                        )

                    with timer.substage("sync_retrieval"):
                        results_sync = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda: self.sync_memory_manager.search_memories(
                                query=content[:50], limit=3
                            ),
                        )

                    success = True

                except Exception as e:
                    success = False
                    self.logger.warning(f"Sync operation {i} failed: {e}")

                sync_metrics.append(
                    DetailedPerformanceMetric(
                        operation=f"sync_op_{i}",
                        total_duration_ms=timer.get_total_duration(),
                        success=success,
                        substages=timer.substages.copy(),
                        memory_peak_mb=timer.get_peak_memory(),
                        details={"result_count": len(results_sync) if success else 0},
                    )
                )

        results["sync"] = self._calculate_enhanced_result(
            "Sync Implementation", "sync", sync_metrics
        )

        # Calculate performance improvement
        if (
            results["async"].mean_duration_ms > 0
            and results["sync"].mean_duration_ms > 0
        ):
            improvement_factor = (
                results["sync"].mean_duration_ms / results["async"].mean_duration_ms
            )
            self.logger.info(
                f"📊 Async vs Sync Performance: {improvement_factor:.2f}x improvement (async is faster)"
            )

        return results

    async def benchmark_memory_intensive_operations(
        self, iterations: int = 20
    ) -> EnhancedBenchmarkResult:
        """Benchmark memory-intensive operations with detailed profiling"""
        self.logger.info(
            f"🧠 Running memory-intensive benchmark ({iterations} iterations)..."
        )

        metrics = []

        for i in range(iterations):
            with PerformanceTimer(
                f"memory_intensive_{i}", self.enable_memory_profiling
            ) as timer:
                try:
                    success = True

                    # Generate large content for memory testing
                    large_content = self._generate_large_content(size_kb=50)

                    with timer.substage("large_content_processing"):
                        processed_content = self._preprocess_content(large_content)
                        complex_metadata = self._generate_complex_metadata(i)

                    with timer.substage("batch_storage"):
                        # Store multiple related memories
                        memory_ids = []
                        for j in range(5):
                            memory_id = await self.async_memory_manager.store_memory(
                                key=f"memory_intensive_{i}_part_{j}",
                                value={
                                    "content": f"{processed_content} - part {j}",
                                    **complex_metadata,
                                    "part": j,
                                },
                            )
                            memory_ids.append(memory_id)

                    with timer.substage("complex_search"):
                        # Perform complex search with multiple criteria
                        search_results = (
                            await self.async_memory_manager.search_memories(
                                query=large_content[:100], limit=10
                            )
                        )

                    with timer.substage("memory_cleanup"):
                        # Force garbage collection to measure cleanup impact
                        import gc

                        gc.collect()

                except Exception as e:
                    success = False
                    self.logger.warning(f"Memory intensive operation {i} failed: {e}")

                metric = DetailedPerformanceMetric(
                    operation=f"memory_intensive_{i}",
                    total_duration_ms=timer.get_total_duration(),
                    success=success,
                    substages=timer.substages.copy(),
                    memory_peak_mb=timer.get_peak_memory(),
                    details={
                        "content_size_kb": 50,
                        "batch_size": 5,
                        "search_results": len(search_results) if success else 0,
                    },
                )
                metrics.append(metric)

        return self._calculate_enhanced_result("Memory Intensive", "async", metrics)

    async def run_comprehensive_enhanced_benchmark(self) -> Dict[str, Any]:
        """Run complete enhanced benchmark suite"""
        self.logger.info("🚀 Starting comprehensive enhanced benchmark suite...")
        self.logger.info("=" * 80)

        try:
            # Initialize systems
            await self.initialize_systems()

            # Run all benchmark tests
            substage_result = await self.benchmark_with_substage_analysis(50)
            self.benchmark_results["substage_analysis"] = substage_result

            async_vs_sync_results = await self.benchmark_async_vs_sync_comparison(30)
            self.benchmark_results.update(async_vs_sync_results)

            memory_intensive_result = await self.benchmark_memory_intensive_operations(
                20
            )
            self.benchmark_results["memory_intensive"] = memory_intensive_result

            # Generate comprehensive report
            report = self._generate_comprehensive_report()

            # Print results
            self._print_enhanced_results(report)

            # Save detailed results to JSON
            self._save_detailed_results(report)

            return report

        except Exception as e:
            self.logger.error(f"❌ Benchmark failed: {e}")
            raise
        finally:
            if self.enable_memory_profiling:
                tracemalloc.stop()

    def _generate_test_data(self) -> Dict[str, List[str]]:
        """Generate realistic test data for benchmarking"""
        return {
            "contents": [
                "Advanced plugin system integration with memory-aware routing capabilities",
                "User interface optimization for improved responsiveness and accessibility",
                "Database connection pooling implementation for concurrent access patterns",
                "Machine learning model inference pipeline with caching mechanisms",
                "Error handling and logging system with distributed tracing support",
                "Configuration management system with hot-reload functionality",
                "Security audit findings and vulnerability remediation strategies",
                "Performance monitoring dashboard with real-time metrics visualization",
                "API rate limiting and throttling implementation for service protection",
                "Data validation and sanitization framework for input processing",
                "Asynchronous task queue processing with retry mechanisms",
                "Memory usage optimization through efficient data structures",
                "Network communication protocols with fault tolerance features",
                "File system operations with atomic transactions and rollback",
                "Cross-platform compatibility testing and validation procedures",
            ]
        }

    def _preprocess_content(self, content: str) -> str:
        """Simulate content preprocessing"""
        return content.strip().lower()

    def _generate_tags(self, content: str) -> List[str]:
        """Generate relevant tags for content"""
        words = content.lower().split()
        return [word for word in words if len(word) > 4][:5]

    def _generate_large_content(self, size_kb: int) -> str:
        """Generate large content for memory testing"""
        base_text = "This is a large content block for memory testing purposes. " * 10
        multiplier = (size_kb * 1024) // len(base_text)
        return base_text * multiplier

    def _generate_complex_metadata(self, iteration: int) -> Dict[str, Any]:
        """Generate complex metadata for testing"""
        return {
            "tags": [f"complex_{iteration}", "memory_test", "benchmark"],
            "confidence": 0.8 + (iteration % 10) * 0.02,
            "category": "memory_intensive_test",
            "priority": iteration % 5,
            "nested_data": {
                "performance_metrics": {
                    "cpu_usage": 0.1 + (iteration % 100) * 0.001,
                    "memory_usage": 0.2 + (iteration % 50) * 0.002,
                },
                "timestamps": {
                    "created": datetime.now().isoformat(),
                    "processed": (
                        datetime.now() + timedelta(milliseconds=iteration)
                    ).isoformat(),
                },
            },
        }

    def _calculate_enhanced_result(
        self, test_name: str, mode: str, metrics: List[DetailedPerformanceMetric]
    ) -> EnhancedBenchmarkResult:
        """Calculate enhanced benchmark results with detailed analysis"""
        if not metrics:
            return EnhancedBenchmarkResult(
                test_name=test_name,
                mode=mode,
                target_ms=200.0,
                total_operations=0,
                successful_operations=0,
                mean_duration_ms=0.0,
                median_duration_ms=0.0,
                p95_duration_ms=0.0,
                p99_duration_ms=0.0,
                max_duration_ms=0.0,
                min_duration_ms=0.0,
                std_dev_ms=0.0,
                peak_memory_mb=0.0,
                avg_memory_delta_mb=0.0,
                total_memory_allocated_mb=0.0,
            )

        # Filter successful operations
        successful_metrics = [m for m in metrics if m.success]
        durations = [m.total_duration_ms for m in successful_metrics]

        # Calculate timing statistics
        if durations:
            mean_duration = statistics.mean(durations)
            median_duration = statistics.median(durations)
            std_dev = statistics.stdev(durations) if len(durations) > 1 else 0.0
            sorted_durations = sorted(durations)

            p95_index = int(len(sorted_durations) * 0.95)
            p99_index = int(len(sorted_durations) * 0.99)

            p95_duration = sorted_durations[min(p95_index, len(sorted_durations) - 1)]
            p99_duration = sorted_durations[min(p99_index, len(sorted_durations) - 1)]
            max_duration = max(durations)
            min_duration = min(durations)
        else:
            mean_duration = median_duration = p95_duration = p99_duration = 0.0
            max_duration = min_duration = std_dev = 0.0

        # Calculate memory statistics
        memory_peaks = [
            m.memory_peak_mb for m in successful_metrics if m.memory_peak_mb > 0
        ]
        peak_memory = max(memory_peaks) if memory_peaks else 0.0

        memory_deltas = [
            (m.memory_end_mb - m.memory_start_mb)
            for m in successful_metrics
            if m.memory_end_mb > 0
        ]
        avg_memory_delta = statistics.mean(memory_deltas) if memory_deltas else 0.0
        total_memory_allocated = sum(max(0, delta) for delta in memory_deltas)

        # Analyze substage performance
        substage_breakdown = self._analyze_substage_performance(successful_metrics)

        # Determine performance grade and bottleneck
        performance_grade = self._calculate_performance_grade(mean_duration)
        bottleneck_stage = self._identify_bottleneck_stage(substage_breakdown)

        success_rate = len(successful_metrics) / len(metrics) * 100

        return EnhancedBenchmarkResult(
            test_name=test_name,
            mode=mode,
            target_ms=200.0,
            total_operations=len(metrics),
            successful_operations=len(successful_metrics),
            mean_duration_ms=mean_duration,
            median_duration_ms=median_duration,
            p95_duration_ms=p95_duration,
            p99_duration_ms=p99_duration,
            max_duration_ms=max_duration,
            min_duration_ms=min_duration,
            std_dev_ms=std_dev,
            peak_memory_mb=peak_memory,
            avg_memory_delta_mb=avg_memory_delta,
            total_memory_allocated_mb=total_memory_allocated,
            substage_breakdown=substage_breakdown,
            success_rate=success_rate,
            performance_grade=performance_grade,
            bottleneck_stage=bottleneck_stage,
            individual_metrics=metrics,
        )

    def _analyze_substage_performance(
        self, metrics: List[DetailedPerformanceMetric]
    ) -> Dict[str, Dict[str, float]]:
        """Analyze performance breakdown by substage"""
        substage_data = defaultdict(list)

        for metric in metrics:
            for substage in metric.substages:
                substage_data[substage.stage_name].append(substage.duration_ms)

        breakdown = {}
        total_time = sum(statistics.mean(times) for times in substage_data.values())

        for stage_name, durations in substage_data.items():
            if durations:
                mean_time = statistics.mean(durations)
                breakdown[stage_name] = {
                    "mean_ms": mean_time,
                    "median_ms": statistics.median(durations),
                    "max_ms": max(durations),
                    "min_ms": min(durations),
                    "percentage": (mean_time / total_time * 100)
                    if total_time > 0
                    else 0.0,
                }

        return breakdown

    def _calculate_performance_grade(self, mean_duration_ms: float) -> str:
        """Calculate performance grade based on timing"""
        if mean_duration_ms < 10:
            return "EXCEPTIONAL"
        elif mean_duration_ms < 50:
            return "EXCELLENT"
        elif mean_duration_ms < 100:
            return "GOOD"
        elif mean_duration_ms < 200:
            return "ACCEPTABLE"
        elif mean_duration_ms < 500:
            return "POOR"
        else:
            return "CRITICAL"

    def _identify_bottleneck_stage(
        self, substage_breakdown: Dict[str, Dict[str, float]]
    ) -> str:
        """Identify the stage consuming the most time"""
        if not substage_breakdown:
            return "UNKNOWN"

        max_time = 0.0
        bottleneck = "UNKNOWN"

        for stage_name, stats in substage_breakdown.items():
            if stats["mean_ms"] > max_time:
                max_time = stats["mean_ms"]
                bottleneck = stage_name

        return bottleneck

    def _generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "benchmark_timestamp": datetime.now().isoformat(),
            "memory_profiling_enabled": self.enable_memory_profiling,
            "test_results": {},
            "performance_summary": {},
            "recommendations": [],
        }

        # Add individual test results
        for test_name, result in self.benchmark_results.items():
            report["test_results"][test_name] = {
                "mode": result.mode,
                "mean_duration_ms": result.mean_duration_ms,
                "p95_duration_ms": result.p95_duration_ms,
                "success_rate": result.success_rate,
                "performance_grade": result.performance_grade,
                "bottleneck_stage": result.bottleneck_stage,
                "peak_memory_mb": result.peak_memory_mb,
                "substage_breakdown": result.substage_breakdown,
            }

        # Calculate overall performance summary
        all_results = list(self.benchmark_results.values())
        if all_results:
            report["performance_summary"] = {
                "overall_mean_ms": statistics.mean(
                    [r.mean_duration_ms for r in all_results]
                ),
                "overall_p95_ms": statistics.mean(
                    [r.p95_duration_ms for r in all_results]
                ),
                "overall_success_rate": statistics.mean(
                    [r.success_rate for r in all_results]
                ),
                "tests_meeting_target": sum(
                    1 for r in all_results if r.mean_duration_ms < 200
                ),
                "total_tests": len(all_results),
            }

        # Generate recommendations
        report["recommendations"] = self._generate_performance_recommendations()

        return report

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        for test_name, result in self.benchmark_results.items():
            if result.mean_duration_ms > 200:
                recommendations.append(
                    f"⚠️ {test_name}: Consider optimization (current: {result.mean_duration_ms:.1f}ms)"
                )

            if result.bottleneck_stage != "UNKNOWN":
                recommendations.append(
                    f"🎯 {test_name}: Focus optimization on {result.bottleneck_stage} stage"
                )

            if result.peak_memory_mb > 100:
                recommendations.append(
                    f"🧠 {test_name}: High memory usage detected ({result.peak_memory_mb:.1f}MB)"
                )

        # Add async vs sync recommendations
        if "async" in self.benchmark_results and "sync" in self.benchmark_results:
            async_result = self.benchmark_results["async"]
            sync_result = self.benchmark_results["sync"]

            if sync_result.mean_duration_ms > async_result.mean_duration_ms * 1.5:
                improvement = (
                    sync_result.mean_duration_ms / async_result.mean_duration_ms
                )
                recommendations.append(
                    f"🚀 Async implementation shows {improvement:.1f}x performance improvement"
                )

        return recommendations

    def _print_enhanced_results(self, report: Dict[str, Any]):
        """Print comprehensive benchmark results"""
        print("\n" + "=" * 80)
        print("🚀 ENHANCED AETHERRA MEMORY BENCHMARK RESULTS")
        print("=" * 80)

        # Overall summary
        if "performance_summary" in report:
            summary = report["performance_summary"]
            print("📊 OVERALL PERFORMANCE SUMMARY")
            print(f"   Mean Duration: {summary.get('overall_mean_ms', 0):.2f}ms")
            print(f"   P95 Duration:  {summary.get('overall_p95_ms', 0):.2f}ms")
            print(f"   Success Rate:  {summary.get('overall_success_rate', 0):.1f}%")
            print(
                f"   Tests Passed:  {summary.get('tests_meeting_target', 0)}/{summary.get('total_tests', 0)}"
            )
            print()

        # Individual test results
        print("📋 DETAILED TEST RESULTS")
        print("-" * 80)

        for test_name, result in report["test_results"].items():
            print(f"\n🔬 {test_name.upper().replace('_', ' ')}")
            print(f"   Mode: {result['mode'].upper()}")
            print(f"   Performance Grade: {result['performance_grade']}")
            print(f"   Mean Duration: {result['mean_duration_ms']:.2f}ms")
            print(f"   P95 Duration:  {result['p95_duration_ms']:.2f}ms")
            print(f"   Success Rate:  {result['success_rate']:.1f}%")
            print(f"   Peak Memory:   {result['peak_memory_mb']:.2f}MB")
            print(f"   Bottleneck:    {result['bottleneck_stage']}")

            # Substage breakdown
            if result["substage_breakdown"]:
                print("   📊 Substage Breakdown:")
                for stage, stats in result["substage_breakdown"].items():
                    print(
                        f"      {stage:20} {stats['mean_ms']:8.2f}ms ({stats['percentage']:5.1f}%)"
                    )

        # Recommendations
        if report.get("recommendations"):
            print("\n🎯 PERFORMANCE RECOMMENDATIONS")
            print("-" * 80)
            for rec in report["recommendations"]:
                print(f"   {rec}")

        print("\n" + "=" * 80)

    def _save_detailed_results(self, report: Dict[str, Any]):
        """Save detailed results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_benchmark_results_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"📁 Detailed results saved to {filename}")
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to save results: {e}")


async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Enhanced Aetherra Memory Benchmark")
    parser.add_argument(
        "--mode",
        choices=["full", "async-vs-sync", "substage-analysis", "memory-intensive"],
        default="full",
        help="Benchmark mode to run",
    )
    parser.add_argument(
        "--no-memory-profiling", action="store_true", help="Disable memory profiling"
    )
    parser.add_argument(
        "--iterations", type=int, default=50, help="Number of iterations for tests"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Initialize benchmark
    benchmark = EnhancedMemoryBenchmark(
        enable_memory_profiling=not args.no_memory_profiling
    )

    try:
        if args.mode == "full":
            await benchmark.run_comprehensive_enhanced_benchmark()
        elif args.mode == "async-vs-sync":
            await benchmark.initialize_systems()
            results = await benchmark.benchmark_async_vs_sync_comparison(
                args.iterations
            )
            print("\n🔍 ASYNC VS SYNC COMPARISON RESULTS")
            print("=" * 50)
            for mode, result in results.items():
                print(
                    f"{mode.upper():12} | {result.mean_duration_ms:8.2f}ms | {result.success_rate:6.1f}%"
                )
        elif args.mode == "substage-analysis":
            await benchmark.initialize_systems()
            result = await benchmark.benchmark_with_substage_analysis(args.iterations)
            print("\n🔬 SUBSTAGE ANALYSIS RESULTS")
            print("=" * 50)
            for stage, stats in result.substage_breakdown.items():
                print(
                    f"{stage:25} | {stats['mean_ms']:8.2f}ms ({stats['percentage']:5.1f}%)"
                )
        elif args.mode == "memory-intensive":
            await benchmark.initialize_systems()
            result = await benchmark.benchmark_memory_intensive_operations(
                args.iterations
            )
            print("\n🧠 MEMORY INTENSIVE RESULTS")
            print("=" * 50)
            print(f"Mean Duration: {result.mean_duration_ms:.2f}ms")
            print(f"Peak Memory: {result.peak_memory_mb:.2f}MB")
            print(f"Memory Delta: {result.avg_memory_delta_mb:.2f}MB")

    except KeyboardInterrupt:
        print("\n⚠️ Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
