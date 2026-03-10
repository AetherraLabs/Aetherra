# Standard library imports
import pathlib
import re

# Aetherra imports
from aetherra_hub.services import metrics_accum

# Minimal drift guard: ensure every ChatMetrics exported counter/gauge appears at least once
# in docs/METRICS_REFERENCE.md either literally or via wildcard group.

DOC_PATH = pathlib.Path("docs/METRICS_REFERENCE.md")

WILDCARD_PATTERNS = [
    r"aetherra_chat_latency_ms_.*",  # histogram family
    r"aetherra_chat_ttft_ms_.*",
]


def _matches_any(metric: str, content: str) -> bool:
    if metric in content:
        return True
    for pat in WILDCARD_PATTERNS:
        if re.search(pat, metric):  # metrics themselves will match wildcard directly
            return True
    return False


def test_metrics_reference_lists_core_chat_metrics():
    assert DOC_PATH.exists(), "docs/METRICS_REFERENCE.md missing"
    doc = DOC_PATH.read_text(encoding="utf-8")
    missing = []
    # Only check straightforward 1:1 mapped counters/gauges
    for field in metrics_accum.ChatMetrics.__dataclass_fields__.values():
        name = field.name
        prom = None
        if (
            name.endswith("_total")
            or name.endswith("_current")
            or name.endswith("_count")
        ) or name in ("latency_ms_sum", "latency_count", "ttft_ms_sum", "ttft_count"):
            prom = f"aetherra_chat_{name}"
        if not prom:
            continue
        if not _matches_any(prom, doc):
            missing.append(prom)
    assert not missing, f"Missing metrics in METRICS_REFERENCE.md: {missing}"
