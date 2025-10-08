import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines


def test_qfac_retrieval_parity_ratio_metric_is_emitted_with_schema():
    lines = build_all_metrics_lines()
    text = "\n".join(lines)

    assert re.search(
        r"^# HELP aetherra_qfac_retrieval_parity_ratio ", text, flags=re.MULTILINE
    ), f"Missing HELP for parity_ratio. Got:\n{text}"
    assert re.search(
        r"^# TYPE aetherra_qfac_retrieval_parity_ratio gauge$", text, flags=re.MULTILINE
    ), f"Missing TYPE for parity_ratio. Got:\n{text}"
    assert re.search(
        r"^aetherra_qfac_retrieval_parity_ratio ", text, flags=re.MULTILINE
    ), f"Missing parity_ratio sample line. Got:\n{text}"
