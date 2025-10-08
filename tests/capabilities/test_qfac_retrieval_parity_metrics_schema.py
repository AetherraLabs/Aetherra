import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines

REQUIRED = [
    r"^aetherra_qfac_retrieval_parity_total ",
    r"^aetherra_qfac_retrieval_parity_top1_match_total ",
    r"^aetherra_qfac_retrieval_parity_any_rank_mismatch_total ",
    r"^aetherra_qfac_retrieval_threshold_dropped_results_total ",
]


def test_qfac_retrieval_parity_metrics_schema_contains_required_series():
    lines = build_all_metrics_lines()
    text = "\n".join(lines)

    missing = []
    for pattern in REQUIRED:
        if not re.search(pattern, text, flags=re.MULTILINE):
            missing.append(pattern)

    assert not missing, (
        f"Missing required QFAC retrieval parity metrics: {missing}\nGot:\n{text}"
    )
