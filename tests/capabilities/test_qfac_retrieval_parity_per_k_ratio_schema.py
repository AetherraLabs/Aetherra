import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines


def test_qfac_retrieval_parity_per_k_ratio_metrics_schema_contains_preferred_series():
    lines = build_all_metrics_lines()
    text = "\n".join(lines)

    for k in (3, 5, 10):
        # Help/Type lines are emitted in exporter; we assert the sample line presence for compactness.
        pattern = rf"^aetherra_qfac_retrieval_parity_top{k}_ratio "
        assert re.search(pattern, text, flags=re.MULTILINE), (
            f"Missing per-k parity ratio gauge for k={k}. Got:\n{text}"
        )
