# SPDX-License-Identifier: GPL-3.0-or-later
"""
STORM A/B Testing Framework

Compares STORM recall performance against baseline recall to validate
quality improvements before production rollout.

Metrics Collected:
- Recall quality (relevance, precision)
- Latency (p50, p95, p99)
- Cost (OT computation overhead)
- Coherence (sheaf consistency)

Acceptance Criteria:
- Quality: STORM >= baseline on relevance scores
- Latency: p95 < 500ms for production queries
- Stability: No sheaf inconsistency > 0.3
- Robustness: Graceful degradation on failures
"""

import asyncio
import statistics
import time
from dataclasses import dataclass, field

from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)


@dataclass
class RecallMetrics:
    """Metrics for a single recall operation"""

    strategy: str  # "baseline" or "storm"
    query: str
    latency_ms: float
    num_results: int
    relevance_scores: list[float] = field(default_factory=list)
    ot_cost: float | None = None
    sheaf_inconsistency: float | None = None
    approximate: bool = False
    error: str | None = None


@dataclass
class ABTestResults:
    """Aggregated A/B test results"""

    baseline_metrics: list[RecallMetrics] = field(default_factory=list)
    storm_metrics: list[RecallMetrics] = field(default_factory=list)

    def baseline_latency_p95(self) -> float:
        """95th percentile latency for baseline"""
        latencies = [m.latency_ms for m in self.baseline_metrics if m.error is None]
        return statistics.quantiles(latencies, n=20)[18] if latencies else 0.0

    def storm_latency_p95(self) -> float:
        """95th percentile latency for STORM"""
        latencies = [m.latency_ms for m in self.storm_metrics if m.error is None]
        return statistics.quantiles(latencies, n=20)[18] if latencies else 0.0

    def baseline_avg_relevance(self) -> float:
        """Average relevance score for baseline"""
        all_scores = []
        for m in self.baseline_metrics:
            if m.error is None:
                all_scores.extend(m.relevance_scores)
        return statistics.mean(all_scores) if all_scores else 0.0

    def storm_avg_relevance(self) -> float:
        """Average relevance score for STORM"""
        all_scores = []
        for m in self.storm_metrics:
            if m.error is None:
                all_scores.extend(m.relevance_scores)
        return statistics.mean(all_scores) if all_scores else 0.0

    def storm_max_inconsistency(self) -> float:
        """Max sheaf inconsistency observed"""
        inconsistencies = [
            m.sheaf_inconsistency
            for m in self.storm_metrics
            if m.sheaf_inconsistency is not None
        ]
        return max(inconsistencies) if inconsistencies else 0.0

    def passes_quality_gate(self) -> bool:
        """Quality gate: STORM relevance >= baseline"""
        return self.storm_avg_relevance() >= self.baseline_avg_relevance()

    def passes_latency_gate(self) -> bool:
        """Latency gate: STORM p95 < 500ms"""
        return self.storm_latency_p95() < 500.0

    def passes_stability_gate(self) -> bool:
        """Stability gate: sheaf inconsistency < 0.3"""
        return self.storm_max_inconsistency() < 0.3

    def passes_all_gates(self) -> bool:
        """All acceptance gates pass"""
        return (
            self.passes_quality_gate()
            and self.passes_latency_gate()
            and self.passes_stability_gate()
        )


class STORMABTester:
    """A/B testing framework for STORM vs baseline recall"""

    def __init__(self, memory_engine: AetherraMemoryEngineAdvanced):
        self.engine = memory_engine
        self.results = ABTestResults()

    async def run_recall_test(
        self, query: str, strategy: str, limit: int = 10
    ) -> RecallMetrics:
        """Run single recall test and collect metrics"""
        start_time = time.perf_counter()
        error = None
        result = None

        try:
            result = await self.engine.recall_typed(
                query=query,
                recall_strategy=strategy,
                limit=limit,
            )
        except Exception as e:
            error = str(e)

        latency_ms = (time.perf_counter() - start_time) * 1000

        if error or result is None:
            return RecallMetrics(
                strategy=strategy,
                query=query,
                latency_ms=latency_ms,
                num_results=0,
                error=error or "No result returned",
            )

        # Extract metrics from result
        relevance_scores = result.scores if result.scores else []
        metadata = result.metadata or {}
        storm_meta = metadata.get("storm_meta", {})

        return RecallMetrics(
            strategy=strategy,
            query=query,
            latency_ms=latency_ms,
            num_results=len(result.items),
            relevance_scores=relevance_scores,
            ot_cost=storm_meta.get("transport_cost"),
            sheaf_inconsistency=storm_meta.get("sheaf_inconsistency"),
            approximate=metadata.get("approximate", False),
        )

    async def run_ab_test(self, queries: list[str], limit: int = 10) -> ABTestResults:
        """Run A/B test for list of queries"""
        for query in queries:
            # Run baseline
            baseline_metrics = await self.run_recall_test(query, "base", limit)
            self.results.baseline_metrics.append(baseline_metrics)

            # Run STORM (hybrid mode for fair comparison)
            storm_metrics = await self.run_recall_test(query, "storm_hybrid", limit)
            self.results.storm_metrics.append(storm_metrics)

        return self.results

    def print_summary(self) -> None:
        """Print A/B test summary"""
        print("\n" + "=" * 60)
        print("STORM A/B TEST RESULTS")
        print("=" * 60)

        print(f"\nQueries Tested: {len(self.results.baseline_metrics)}")

        print("\n--- LATENCY ---")
        print(f"Baseline p95: {self.results.baseline_latency_p95():.2f}ms")
        print(f"STORM p95:    {self.results.storm_latency_p95():.2f}ms")
        latency_gate = "✅ PASS" if self.results.passes_latency_gate() else "❌ FAIL"
        print(f"Latency Gate (<500ms): {latency_gate}")

        print("\n--- QUALITY ---")
        print(f"Baseline avg relevance: {self.results.baseline_avg_relevance():.4f}")
        print(f"STORM avg relevance:    {self.results.storm_avg_relevance():.4f}")
        quality_gate = "✅ PASS" if self.results.passes_quality_gate() else "❌ FAIL"
        print(f"Quality Gate (STORM >= baseline): {quality_gate}")

        print("\n--- STABILITY ---")
        print(f"STORM max inconsistency: {self.results.storm_max_inconsistency():.4f}")
        stability_gate = (
            "✅ PASS" if self.results.passes_stability_gate() else "❌ FAIL"
        )
        print(f"Stability Gate (<0.3): {stability_gate}")

        print("\n--- OVERALL ---")
        if self.results.passes_all_gates():
            print("✅ ALL GATES PASSED - APPROVED FOR ROLLOUT")
        else:
            print("❌ SOME GATES FAILED - REQUIRES INVESTIGATION")

        print("=" * 60 + "\n")


async def run_storm_ab_test():
    """Execute A/B test with sample queries"""
    print("🧪 Initializing STORM A/B Testing Framework...")

    # Initialize memory engine
    engine = AetherraMemoryEngineAdvanced()

    # Populate with test data
    test_data = [
        "User preferences for dark mode interface",
        "System configuration settings for memory limits",
        "Recent conversation about AI capabilities",
        "Technical documentation on API endpoints",
        "Meeting notes from project planning session",
    ]

    print(f"📝 Storing {len(test_data)} test memories...")
    for content in test_data:
        await engine.remember(
            content=content,
            tags=["test", "ab_testing"],
            category="test_data",
        )

    # Test queries
    test_queries = [
        "user interface preferences",
        "system settings configuration",
        "AI discussion topics",
        "API documentation",
        "project planning",
    ]

    print(f"🔍 Running A/B tests for {len(test_queries)} queries...\n")

    # Run A/B test
    tester = STORMABTester(engine)
    results = await tester.run_ab_test(test_queries, limit=5)

    # Print summary
    tester.print_summary()

    return results


if __name__ == "__main__":
    asyncio.run(run_storm_ab_test())
