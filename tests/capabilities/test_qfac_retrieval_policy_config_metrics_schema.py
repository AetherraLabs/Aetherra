import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines

REQUIRED = [
    r"^aetherra_qfac_retrieval_threshold ",
    r"^aetherra_qfac_retrieval_parity_enabled ",
]


def test_qfac_retrieval_policy_config_metrics_schema_contains_required_series():
    text = "\n".join(build_all_metrics_lines())
    missing = [p for p in REQUIRED if not re.search(p, text, flags=re.MULTILINE)]
    assert not missing, (
        f"Missing QFAC retrieval policy config metrics: {missing}\nGot:\n{text}"
    )
