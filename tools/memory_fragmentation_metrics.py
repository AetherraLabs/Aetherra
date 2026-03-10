"""Memory Fragmentation / Compaction Metrics (Lightweight)

Goal:
  Provide a coarse heuristic for Python memory fragmentation using available
  introspection tools without requiring CPython internal APIs or external
  native extensions (to keep CI portable).

Strategy:
  - Use `tracemalloc` to capture two snapshots separated by an allocation +
    deallocation workload.
  - Compute: total allocated size delta, number of traces delta, and a simple
    fragmentation ratio: (distinct_filename_blocks / total_blocks).
  - Optionally perform a "pseudo-compaction" hint by forcing GC + allocating
    and freeing large throwaway buffers to encourage arena reuse.

This is heuristic only; results feed into capability tests that assert the
fragmentation ratio remains below a generous threshold to detect pathological
leaks or runaway small-object churn.

License: GPL-3.0-or-later
"""

from __future__ import annotations

# Standard library imports
import gc
import tracemalloc
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class FragmentationStats:
    before_size: int
    after_size: int
    before_traces: int
    after_traces: int
    distinct_files_before: int
    distinct_files_after: int
    fragmentation_ratio_before: float
    fragmentation_ratio_after: float

    def to_dict(self) -> dict[str, Any]:  # pragma: no cover - trivial
        return asdict(self)


def _fragmentation_ratio(snapshot: tracemalloc.Snapshot) -> float:
    stats = snapshot.statistics("filename")
    total_traces = sum(s.count for s in stats) or 1
    distinct = len(stats)
    return distinct / total_traces


def measure_fragmentation(workload_iterations: int = 5000) -> FragmentationStats:
    """Measure a coarse memory fragmentation signal.

    Heuristic steps:
      1. Ensure tracemalloc tracing is active.
      2. Warm up allocations to guarantee a non-zero baseline snapshot, retrying
       up to 3 attempts (some CI runs on Windows showed an occasional empty
       first snapshot when taken too early after start()).
      3. Run a mixed allocation workload (lists + dicts) to create churn.
      4. Perform a pseudo-compaction hint by allocating and freeing a large list.
      5. Capture an after snapshot and compute simple statistics.

    Returns a FragmentationStats dataclass with before/after sizes, trace counts,
    distinct file counts, and a filename-based fragmentation ratio.
    """

    if not tracemalloc.is_tracing():  # Activate tracing if not already on
        tracemalloc.start()

    # 1-2. Obtain baseline snapshot with retries to avoid rare zero-trace case
    max_attempts = 3
    before = None
    b_stats = []
    for attempt in range(1, max_attempts + 1):
        # Warmup: create moderate allocations (lists + dict) to ensure frames
        _warmup_list = [i for i in range(2000)]
        _warmup_dict = {str(i): i for i in range(600)}
        before = tracemalloc.take_snapshot()
        b_stats = before.statistics("filename")
        # Cleanup warmups to not bias workload deltas too much
        del _warmup_list, _warmup_dict
        gc.collect()
        if b_stats:  # Non-empty baseline obtained
            break
    # If still empty, proceed but ratios will gracefully handle via denominator guard

    # 3. Allocation churn workload
    for i in range(workload_iterations):
        if i % 2 == 0:
            _ = [str(j) for j in range(12)]  # slightly varied list size
        else:
            _ = {f"k{j}": j for j in range(6)}
    gc.collect()

    # 4. Pseudo-compaction: large transient allocation
    _temp = [0] * 20000
    del _temp
    gc.collect()

    # 5. After snapshot & stats
    after = tracemalloc.take_snapshot()
    a_stats = after.statistics("filename")

    before_size = sum(s.size for s in b_stats)
    after_size = sum(s.size for s in a_stats)
    before_traces = sum(s.count for s in b_stats)
    after_traces = sum(s.count for s in a_stats)

    # Guard: if baseline snapshot somehow None (extremely unlikely), reuse after
    baseline_snapshot = before if before is not None else after

    return FragmentationStats(
        before_size=before_size,
        after_size=after_size,
        before_traces=before_traces,
        after_traces=after_traces,
        distinct_files_before=len(b_stats),
        distinct_files_after=len(a_stats),
        fragmentation_ratio_before=_fragmentation_ratio(baseline_snapshot),
        fragmentation_ratio_after=_fragmentation_ratio(after),
    )


if __name__ == "__main__":  # pragma: no cover - manual
    stats = measure_fragmentation()
    print(stats.to_dict())
