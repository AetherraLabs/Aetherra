"""Reflection / Memory Stability Test

Ensures the `PersonalityReflectionSystem` does not retain unbounded state
across many interactions.

Invariants validated:
1. reflection_history length is capped (<= 200 as per deque maxlen)
2. communication_patterns key count remains within a bounded taxonomy (<= 30)
3. communication_styles remains fixed size (7 styles)
4. Net retained memory attributed to reflection_system.py after a large batch
   of interactions stays below a small threshold (heuristic leak guard)

NOTE: This is a heuristic guard, not a precise leak detector. Thresholds can
be tuned if legitimate changes increase bounded retention.
"""

from __future__ import annotations

# Standard library imports
import os
import tracemalloc
from typing import List

# Third party imports
import pytest

try:
    # Aetherra imports
    from Aetherra.aetherra_core.system.reflection_system import (
        PersonalityReflectionSystem,
    )
except Exception as e:  # pragma: no cover - import guard
    pytest.skip(f"Reflection system unavailable: {e}", allow_module_level=True)


TOTAL_INTERACTIONS = 500
WARMUP = 50
MAX_PATTERN_KEYS = 30  # styles(7)+traits(7)+elements(9)+conversation types(5)+slack
MAX_MEMORY_GROWTH_BYTES = 150_000  # ~150 KB attributed lines growth heuristic


def _sample_inputs() -> list[str]:
    return [
        "Can you help me with some code?",
        "I feel a bit frustrated with this function design",
        "What's the algorithm complexity?",
        "Just saying hi, awesome progress!",
        "Need support to optimize performance",
        "Curious about architecture decisions",
        "Unique creative idea I'd love feedback on",
    ]


def _sample_responses() -> list[str]:
    return [
        "Certainly, let's analyze the function and optimize the algorithm further.",
        "I understand how you feel; it's challenging but we can improve it together.",
        "Great question! Therefore, we can consider complexity and compare approaches.",
        "Awesome! I love exploring innovative, creative solutions with you.",
        "Let me help: we can assess performance, evaluate bottlenecks, and iterate.",
        "Imagine a unique architecture; furthermore we can implement adaptive layers.",
        "I think we should support clarity, empathy, and thoughtful improvements.",
    ]


@pytest.mark.asyncio
async def test_reflection_memory_and_pattern_stability():
    # Force deterministic profile if not set (harmless outside of deterministic paths)
    os.environ.setdefault("AETHERRA_PROFILE", "test")

    system = PersonalityReflectionSystem()

    user_inputs = _sample_inputs()
    responses = _sample_responses()

    tracemalloc.start()

    # Run interactions
    for i in range(TOTAL_INTERACTIONS):
        ui = user_inputs[i % len(user_inputs)]
        resp = responses[i % len(responses)]
        await system.process_interaction(ui, resp, context={"idx": i})

        # Quick sanity mid-run: no unbounded explosion of pattern keys
        if (i + 1) % 100 == 0:
            assert len(system.communication_patterns) <= MAX_PATTERN_KEYS, (
                f"Pattern key count exceeded early ({len(system.communication_patterns)})"
            )

    # Post-run structural invariants
    assert len(system.reflection_history) <= 200, (
        "reflection_history exceeded maxlen bound"
    )
    assert len(system.communication_styles) == 7, "communication_styles mutated size"
    assert len(system.communication_patterns) <= MAX_PATTERN_KEYS, (
        f"communication_patterns exceeded bounded taxonomy: {len(system.communication_patterns)}"
    )

    # Memory growth heuristic: compare warm snapshot vs final snapshot
    warm_snapshot = tracemalloc.take_snapshot()

    # Execute a second batch (same volume) to observe additional retained growth
    for j in range(TOTAL_INTERACTIONS, TOTAL_INTERACTIONS * 2):
        ui = user_inputs[j % len(user_inputs)]
        resp = responses[j % len(responses)]
        await system.process_interaction(ui, resp, context={"idx": j})

    final_snapshot = tracemalloc.take_snapshot()
    diff = final_snapshot.compare_to(warm_snapshot, "filename")

    reflection_growth = 0
    for stat in diff:
        if stat.size_diff > 0 and stat.traceback[0].filename.endswith(
            "reflection_system.py"
        ):
            reflection_growth += stat.size_diff

    # Heuristic threshold assertion
    assert reflection_growth <= MAX_MEMORY_GROWTH_BYTES, (
        f"Reflection system retained {reflection_growth} bytes (> {MAX_MEMORY_GROWTH_BYTES}) after extended run"
    )

    # Clean up tracing
    tracemalloc.stop()
