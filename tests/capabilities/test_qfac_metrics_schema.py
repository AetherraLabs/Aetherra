import re

from aetherra_hub.services.metrics_accum import build_all_metrics_lines

REQUIRED = [
    # Policy
    r"^aetherra_qfac_policy_mode_current ",
    r"^aetherra_qfac_policy_allowed ",
    r"^aetherra_qfac_policy_info\{key=\"reason\",value=\".*\"\} 1$",
    r"^aetherra_qfac_policy_info\{key=\"policy\",value=\".*\"\} 1$",
    # Snapshot
    r"^aetherra_qfac_nodes_total ",
    r"^aetherra_qfac_nodes_compressed ",
    r"^aetherra_qfac_degraded_nodes_total ",
    r"^aetherra_qfac_compression_ratio ",
    r"^aetherra_qfac_compression_ratio_avg ",
]


def test_qfac_metrics_schema_contains_required_series():
    lines = build_all_metrics_lines()
    text = "\n".join(lines)

    missing = []
    for pattern in REQUIRED:
        if not re.search(pattern, text, flags=re.MULTILINE):
            missing.append(pattern)

    assert not missing, f"Missing required QFAC metrics: {missing}\nGot:\n{text}"
