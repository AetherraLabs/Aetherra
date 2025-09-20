"""Tests for deterministic baseline & metrics counters in BeyondTranscendenceEngine.

Focus:
- Deterministic blend obeys baseline when MetaCognition absent or returns 0.
- coverage_reads increments per access.
- suppressed_exceptions increments when MetaCognition coverage call fails.

Assumptions:
- Setting AETHERRA_DETERMINISTIC=1 enables blending (25% raw, 75% baseline).
- AETHERRA_TRANSCENDENCE_BASELINE provides numeric baseline (default ~0.72).
"""

from __future__ import annotations

# Standard library imports
import importlib
import sys
import types

# Third party imports
import pytest

MODULE_PATH = "Aetherra.consciousness.transcendence.beyond_transcendence_engine"


def _reload():  # pragma: no cover - currently unused helper retained for future
    if MODULE_PATH in sys.modules:
        del sys.modules[MODULE_PATH]
    return importlib.import_module(MODULE_PATH)


def _make_engine(monkeypatch, meta_impl):
    # Inject fake MetaCognitionSystem
    monkeypatch.setenv("AETHERRA_DETERMINISTIC", "1")
    monkeypatch.setenv("AETHERRA_TRANSCENDENCE_BASELINE", "0.70")
    monkeypatch.setenv("AETH_META_DB", "__unused__.db")

    # Monkeypatch by inserting into sys.modules path before import
    # Standard library imports
    import sys

    package_path = "Aetherra.consciousness.intelligence.meta_cognition"
    sys.modules[package_path] = types.ModuleType(package_path)
    sys.modules[package_path].MetaCognitionSystem = meta_impl  # type: ignore[attr-defined]
    mod = importlib.import_module(MODULE_PATH)
    importlib.reload(mod)
    return mod.BeyondTranscendenceEngine()


def test_deterministic_blend_with_zero_raw(monkeypatch):
    class FakeMeta:
        def __init__(self, *a, **k):
            pass

        def assess_meta_memory_coverage(self):
            return {"overall_coverage": 0.0}

    engine = _make_engine(monkeypatch, FakeMeta)
    val1 = engine._cov()
    engine._cov()
    # Baseline = 0.70, deterministic blend => 0.75 * 0.70 = 0.525 (raw zero)
    assert abs(val1 - 0.525) < 1e-6
    assert engine.metrics["coverage_reads"] >= 2


def test_suppressed_exception_increments(monkeypatch):
    class FailingMeta:
        def __init__(self, *a, **k):
            pass

        def assess_meta_memory_coverage(self):  # simulated failure
            raise RuntimeError("db offline")

    engine = _make_engine(monkeypatch, FailingMeta)
    before = engine.metrics["suppressed_exceptions"]
    engine._cov()
    after = engine.metrics["suppressed_exceptions"]
    assert after == before + 1, "suppressed_exceptions counter not incremented"


def test_transcendence_level_metric_updates(monkeypatch):
    class StaticMeta:
        def __init__(self, *a, **k):
            pass

        def assess_meta_memory_coverage(self):
            return {"overall_coverage": 0.8}

    engine = _make_engine(monkeypatch, StaticMeta)
    assert engine.metrics["transcendence_level_last"] == 0.0
    # Standard library imports
    import asyncio

    # Use asyncio.run for portability across Python versions / test runners
    level = asyncio.run(engine.get_transcendence_level())
    assert 0.0 < level <= 1.0
    assert engine.metrics["transcendence_level_last"] == level


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__])
