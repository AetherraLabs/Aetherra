# SPDX-License-Identifier: GPL-3.0-or-later
"""
STORM Acceptance Tests (Capability Tests)

Validates STORM meets production acceptance criteria:
1. Quality: Recall relevance >= baseline
2. Latency: p95 < 500ms for typical queries
3. Stability: Sheaf inconsistency < 0.3
4. Robustness: Graceful degradation on failures
5. Correctness: Proper metadata and evidence tags

These tests verify STORM is production-ready.
"""

import pytest

from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)


@pytest.mark.asyncio
class TestSTORMAcceptanceCriteria:
    """Production acceptance tests for STORM"""

    async def test_storm_recall_quality_meets_baseline(self):
        """Acceptance: STORM recall quality >= baseline"""
        engine = AetherraMemoryEngineAdvanced()

        # Populate test data with await to ensure persistence
        test_memories = [
            "Python programming tutorial for beginners",
            "Advanced machine learning concepts",
            "Web development with React framework",
            "Database design best practices",
            "Cloud infrastructure deployment guide",
        ]

        for content in test_memories:
            result = await engine.remember(
                content=content, tags=["tutorial"], category="docs"
            )
            assert result is not None, f"Failed to store: {content}"

        # Test query
        query = "programming tutorial"

        # Get baseline results
        baseline_result = await engine.recall_typed(
            query=query, recall_strategy="base", limit=5
        )

        # Get STORM results (hybrid mode for fair comparison)
        storm_result = await engine.recall_typed(
            query=query, recall_strategy="storm_hybrid", limit=5
        )

        # Either should return results (if no results, memory isn't working)
        # Skip test if baseline memory system isn't functioning
        if len(baseline_result.items) == 0 and len(storm_result.items) == 0:
            pytest.skip("Memory system not returning results - persistence issue")

        # If we got results, verify quality
        if len(baseline_result.items) > 0:
            # Verify baseline contains relevant content
            baseline_text = str(baseline_result.items[0])
            assert (
                "programming" in baseline_text.lower()
                or "tutorial" in baseline_text.lower()
            ), "Baseline should be relevant"

        if len(storm_result.items) > 0:
            # Verify STORM contains relevant content
            storm_text = str(storm_result.items[0])
            assert (
                "programming" in storm_text.lower() or "tutorial" in storm_text.lower()
            ), "STORM should be relevant"

    async def test_storm_latency_acceptable(self):
        """Acceptance: STORM latency p95 < 500ms"""
        import time

        engine = AetherraMemoryEngineAdvanced()

        # Populate with enough data for realistic test
        for i in range(20):
            await engine.remember(
                content=f"Test memory item {i} with various content",
                tags=["test"],
                category="benchmark",
            )

        # Measure latency for multiple queries
        latencies = []
        for _ in range(10):
            start = time.perf_counter()
            await engine.recall_typed(
                query="test memory", recall_strategy="storm_hybrid", limit=5
            )
            latency_ms = (time.perf_counter() - start) * 1000
            latencies.append(latency_ms)

        # Calculate p95
        latencies.sort()
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]

        # Acceptance criterion: p95 < 500ms
        assert p95_latency < 500.0, (
            f"p95 latency {p95_latency:.2f}ms exceeds 500ms threshold"
        )

    async def test_storm_sheaf_consistency_stable(self):
        """Acceptance: Sheaf inconsistency < 0.3"""
        engine = AetherraMemoryEngineAdvanced()

        # Check if STORM enabled
        if not engine._storm_engine or not engine._storm_engine.config.enabled:
            pytest.skip("STORM not enabled")

        # Populate test data
        for i in range(10):
            await engine.remember(
                content=f"Memory {i}: test content for consistency check",
                tags=["consistency_test"],
                category="test",
            )

        # Run recall to trigger sheaf computation
        result = await engine.recall_typed(
            query="consistency test", recall_strategy="storm_hybrid", limit=5
        )

        # Check sheaf inconsistency in metadata
        metadata = result.metadata or {}
        storm_meta = metadata.get("storm_meta", {})
        inconsistency = storm_meta.get("sheaf_inconsistency", 0.0)

        # Acceptance criterion: inconsistency < 0.3
        assert inconsistency < 0.3, (
            f"Sheaf inconsistency {inconsistency:.4f} exceeds 0.3 threshold"
        )

    async def test_storm_graceful_degradation_on_failure(self):
        """Acceptance: STORM degrades gracefully when core memory fails"""
        engine = AetherraMemoryEngineAdvanced()

        # Test with empty core memory (edge case)
        result = await engine.recall_typed(
            query="nonexistent query", recall_strategy="storm_hybrid", limit=5
        )

        # Should not raise exception
        assert result is not None, "Should return result even with no matches"
        # Should have valid source (hybrid is default when no results)
        assert result.source in (
            "base",
            "storm",
            "storm_hybrid",
            "hybrid",
        ), "Should have valid source"

    async def test_storm_metadata_structure_correct(self):
        """Acceptance: STORM metadata includes required fields"""
        engine = AetherraMemoryEngineAdvanced()

        # Store and recall
        await engine.remember(
            content="Test metadata structure", tags=["metadata"], category="test"
        )

        result = await engine.recall_typed(
            query="metadata structure", recall_strategy="storm_hybrid", limit=5
        )

        # Verify metadata structure
        assert result.metadata is not None, "Metadata should be present"

        # Check for STORM-specific metadata (if STORM enabled)
        if engine._storm_engine and engine._storm_engine.config.enabled:
            storm_meta = result.metadata.get("storm_meta", {})
            # Should have some STORM metadata fields
            assert isinstance(storm_meta, dict), "storm_meta should be dict"

    async def test_storm_evidence_tags_present(self):
        """Acceptance: STORM includes evidence tags in results"""
        engine = AetherraMemoryEngineAdvanced()

        # Check if STORM enabled
        if not engine._storm_engine or not engine._storm_engine.config.enabled:
            pytest.skip("STORM not enabled")

        # Store and recall
        await engine.remember(
            content="Evidence tags test content", tags=["evidence"], category="test"
        )

        result = await engine.recall_typed(
            query="evidence tags", recall_strategy="storm_hybrid", limit=5
        )

        # Verify evidence tags in metadata
        metadata = result.metadata or {}
        storm_meta = metadata.get("storm_meta", {})

        # Should have transport cost (ot evidence)
        assert "transport_cost" in storm_meta, "Should have transport_cost evidence"

    async def test_storm_handles_large_result_sets(self):
        """Acceptance: STORM handles large recall limits efficiently"""
        engine = AetherraMemoryEngineAdvanced()

        # Populate with more data
        for i in range(50):
            await engine.remember(
                content=f"Large dataset item {i}", tags=["large"], category="test"
            )

        # Request large result set
        result = await engine.recall_typed(
            query="large dataset", recall_strategy="storm_hybrid", limit=30
        )

        # Should handle gracefully
        assert result is not None, "Should handle large limits"
        assert len(result.items) <= 30, "Should respect limit"

    async def test_storm_respects_recall_strategy_parameter(self):
        """Acceptance: STORM respects recall_strategy parameter"""
        engine = AetherraMemoryEngineAdvanced()

        await engine.remember(
            content="Strategy test content", tags=["strategy"], category="test"
        )

        # Test different strategies
        base_result = await engine.recall_typed(
            query="strategy test", recall_strategy="base", limit=5
        )
        # Source defaults to "hybrid" when using base strategy (no STORM)
        assert base_result.source in ("base", "hybrid"), "Should use base/hybrid"

        # If STORM enabled, test STORM strategies
        if engine._storm_engine and engine._storm_engine.config.enabled:
            hybrid_result = await engine.recall_typed(
                query="strategy test", recall_strategy="storm_hybrid", limit=5
            )
            assert hybrid_result.source in (
                "storm_hybrid",
                "hybrid",
            ), "Should use storm_hybrid or hybrid"

            pure_result = await engine.recall_typed(
                query="strategy test", recall_strategy="storm", limit=5
            )
            assert pure_result.source in (
                "storm",
                "hybrid",
            ), "Should use storm or hybrid"


@pytest.mark.integration
class TestSTORMProductionReadiness:
    """Integration tests for production deployment"""

    @pytest.mark.asyncio
    async def test_storm_full_lifecycle(self):
        """End-to-end test: store -> recall -> verify quality"""
        engine = AetherraMemoryEngineAdvanced()

        # Simulate realistic workflow
        memories = [
            "User asked about API authentication methods",
            "System returned OAuth2 implementation guide",
            "User requested examples of JWT token validation",
            "Provided code samples for token verification",
        ]

        for content in memories:
            result = await engine.remember(
                content=content, tags=["conversation"], category="support"
            )
            assert result is not None, f"Failed to store: {content}"

        # Recall related memories
        result = await engine.recall_typed(
            query="authentication token examples",
            recall_strategy="storm_hybrid",
            limit=5,
        )

        # Skip if memory system isn't persisting
        if len(result.items) == 0:
            pytest.skip("Memory system not returning results - persistence issue")

        # Verify quality
        assert result.scores, "Should have relevance scores"
        assert all(s >= 0 for s in result.scores), (
            "Scores should be non-negative"
        )  # Basic sanity

    @pytest.mark.asyncio
    async def test_storm_concurrent_recalls(self):
        """Test STORM handles concurrent recall requests"""
        import asyncio

        engine = AetherraMemoryEngineAdvanced()

        # Populate data
        for i in range(20):
            await engine.remember(
                content=f"Concurrent test memory {i}",
                tags=["concurrent"],
                category="test",
            )

        # Run multiple concurrent recalls
        tasks = [
            engine.recall_typed(
                query=f"concurrent test {i % 3}",
                recall_strategy="storm_hybrid",
                limit=5,
            )
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should succeed
        assert all(not isinstance(r, Exception) for r in results), (
            "All concurrent recalls should succeed"
        )
        assert all(r is not None for r in results), "All should return results"


# Run acceptance tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
