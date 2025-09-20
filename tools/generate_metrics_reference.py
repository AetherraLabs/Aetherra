"""Generate docs/METRICS_REFERENCE.md from live metrics_accum definitions.

This script is a best-effort extractor to reduce drift:
- Imports metrics_accum and inspects ChatMetrics dataclass fields.
- Emits a markdown table skeleton (operator augments manual descriptions).
- Appends existing custom sections if present (alert suggestions block retained by markers).

Usage:
  python tools/generate_metrics_reference.py --out docs/METRICS_REFERENCE.md

Idempotent: existing file lines between markers are replaced; other content preserved.
"""

from __future__ import annotations

# Standard library imports
import argparse
import pathlib
import re
from dataclasses import fields
from typing import List

# Aetherra imports
from aetherra_hub.services import metrics_accum

MARKER_BEGIN = "<!-- GENERATED_METRICS_TABLE_BEGIN -->"
MARKER_END = "<!-- GENERATED_METRICS_TABLE_END -->"

STATIC_HEADERS = [
    "# Aetherra Metrics Reference",
    "> Sections below between markers are regenerated; manual edits go outside markers.",
]

# Simple map for known fields → human description (extend as needed)
FIELD_DESCRIPTIONS = {
    "requests_total": "Total chat requests processed",
    "streams_current": "Active SSE streaming connections",
    "fallback_mock_total": "Mock fallback path activations (aggregate)",
    "chars_in_total": "Cumulative input characters (approx)",
    "chars_out_total": "Cumulative output characters (approx)",
    "tokens_in_total": "Approximate input tokens (heuristic)",
    "tokens_out_total": "Approximate output tokens (heuristic)",
    "chunks_total": "SSE chunk events emitted",
    "resume_gaps_total": "SSE resume gap detections (missed events)",
    "soft_timeouts_total": "Soft timeout terminations before engine response",
    "breaker_open_total": "Circuit breaker / timeout triggered count",
    "auth_missing_token_total": "Missing required token rejections",
    "auth_invalid_token_total": "Invalid token rejections",
    "hmr_denied_total": "HMR enable attempts denied",
}

# Derived metrics (histograms etc.) appended manually for awareness
DERIVED_ROWS = [
    (
        "aetherra_chat_latency_ms_*",
        "histogram",
        "Latency histogram & counters",
        "Buckets 50..5000ms",
    ),
    (
        "aetherra_chat_ttft_ms_*",
        "histogram",
        "TTFT histogram & counters",
        "Buckets 50..2000ms",
    ),
]


def build_table() -> List[str]:
    rows: List[str] = []
    rows.append("| Metric (field) | Type | Description | Notes |")
    rows.append("| -------------- | ---- | ----------- | ----- |")
    for f in fields(metrics_accum.ChatMetrics):  # dataclass field introspection
        name = f.name
        prom = None
        # Convert dataclass fields into canonical metric names where 1:1 mapping exists
        if (
            name.endswith("_total")
            or name.endswith("_current")
            or name.endswith("_count")
        ):
            # prefix with aetherra_chat_ except resume_gaps (still chat domain)
            prom = f"aetherra_chat_{name}"
        elif name in ("latency_ms_sum", "latency_count", "ttft_ms_sum", "ttft_count"):
            prom = f"aetherra_chat_{name}"
        if not prom:
            continue  # skip internal helpers / histograms (buckets handled separately)
        desc = FIELD_DESCRIPTIONS.get(name, "TBD")
        mtype = (
            "counter" if prom.endswith("_total") or prom.endswith("_count") else "gauge"
        )
        rows.append(f"| {prom} | {mtype} | {desc} | |")
    for prom, mtype, desc, notes in DERIVED_ROWS:
        rows.append(f"| {prom} | {mtype} | {desc} | {notes} |")
    return rows


def regenerate(original: str) -> str:
    table_lines = build_table()
    new_block = "\n".join([MARKER_BEGIN, *table_lines, MARKER_END])
    if MARKER_BEGIN in original and MARKER_END in original:
        pattern = re.compile(rf"{MARKER_BEGIN}.*?{MARKER_END}", re.DOTALL)
        return pattern.sub(new_block, original)
    # Prepend if markers absent
    return "\n".join([*STATIC_HEADERS, new_block, original])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/METRICS_REFERENCE.md")
    args = ap.parse_args()
    out_path = pathlib.Path(args.out)
    existing = ""
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
    updated = regenerate(existing or "")
    out_path.write_text(updated, encoding="utf-8")
    print(f"Wrote metrics reference: {out_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
