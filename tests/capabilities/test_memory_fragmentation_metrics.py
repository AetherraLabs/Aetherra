from tools.memory_fragmentation_metrics import measure_fragmentation


def test_memory_fragmentation_metrics_heuristic():
    stats = measure_fragmentation(workload_iterations=1500)
    # Structural sanity
    assert stats.before_traces > 0 and stats.after_traces > 0
    # Ratio bounds (distinct files / total traces) should always be <= 1.0
    assert 0 < stats.fragmentation_ratio_before <= 1.0
    assert 0 < stats.fragmentation_ratio_after <= 1.0
    # Heuristic: fragmentation ratio should not increase by more than 0.25
    delta = stats.fragmentation_ratio_after - stats.fragmentation_ratio_before
    assert delta <= 0.25, f"Fragmentation ratio increased too much: {delta:.3f}"
    # Size non-negative
    assert stats.after_size >= 0
