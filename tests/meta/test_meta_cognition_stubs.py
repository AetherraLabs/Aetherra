"""Smoke tests ensuring MetaCognitionSystem public APIs are callable.

Goals:
- No AttributeError from missing private helper methods
- Basic type/shape sanity for key public methods
- Uses a temp file-backed SQLite DB to avoid ':memory:' per-connection schema resets
"""

from __future__ import annotations

# Standard library imports
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.consciousness.intelligence.meta_cognition import (
    MetaCognitionSystem,
    SelfKnowledgeDomain,
)


@pytest.fixture()
def meta_cog(tmp_path: Path) -> MetaCognitionSystem:
    db_file = tmp_path / "meta_cognition_test.db"
    return MetaCognitionSystem(db_path=str(db_file))


def test_enhance_self_knowledge_and_reflection(meta_cog: MetaCognitionSystem):
    node_id = meta_cog.enhance_self_knowledge(
        SelfKnowledgeDomain.COGNITIVE_PATTERNS,
        {"sample": True},
        confidence=0.5,
        source="unit_test",
    )
    assert isinstance(node_id, str) and node_id

    # Should not raise and should return an entry-like object
    reflection = meta_cog.conduct_self_reflection(trigger_event="unit")
    assert hasattr(reflection, "reflection_id")


def test_domain_specific_enhancements(meta_cog: MetaCognitionSystem):
    nid1 = meta_cog.enhance_cognitive_patterns_knowledge()
    nid2 = meta_cog.enhance_system_capabilities_knowledge()
    assert isinstance(nid1, str) and isinstance(nid2, str)


def test_coverage_and_summary_shapes(meta_cog: MetaCognitionSystem):
    coverage = meta_cog.assess_meta_memory_coverage()
    assert "overall_coverage" in coverage and "domain_coverages" in coverage

    summary = meta_cog.get_self_knowledge_summary()
    assert "meta_memory_status" in summary
    assert "improvement_roadmap" in summary


def test_identify_knowledge_gaps_safely(meta_cog: MetaCognitionSystem):
    gaps = meta_cog.identify_knowledge_gaps()
    # Just ensure it's a list and entries have expected shape if present
    assert isinstance(gaps, list)
    if gaps:
        assert isinstance(gaps[0], dict)
        assert "domain" in gaps[0]
