import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines


def test_qfac_retrieval_parity_per_k_counters_schema_contains_help_type_and_lines():
    lines = build_all_metrics_lines()
    text = "\n".join(lines)

    for k in (1, 3, 5, 10):
        # Ensure HELP/TYPE are present
        assert re.search(
            rf"^# HELP aetherra_qfac_retrieval_parity_top{k}_match_total ", text, flags=re.MULTILINE
        )
        assert re.search(
            rf"^# TYPE aetherra_qfac_retrieval_parity_top{k}_match_total counter$", text, flags=re.MULTILINE
        )
        # Ensure metric line exists
        assert re.search(
            rf"^aetherra_qfac_retrieval_parity_top{k}_match_total ", text, flags=re.MULTILINE
        )
