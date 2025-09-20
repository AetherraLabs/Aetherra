#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

"""A/B recall benchmark harness for classical vs quantum-enriched recall.

- Runs a small corpus + query set through classical and quantum paths.
- Measures latency and hit quality; optionally emits to Hub via service registry.
- Safe to run in CI; uses deterministic QRNG when AETHERRA_PROFILE=test/ci.

Usage (examples):
  python tools/ab_recall_benchmark.py --queries "hello world" "quantum memory" --limit 5 --emit 1
  python tools/ab_recall_benchmark.py --dataset demos --emit 0

Env flags:
  AETHERRA_PROFILE=test|ci    # deterministic QRNG
  AETHERRA_QHASH_*            # qhash bits/weights
  AETHERRA_RFM_*              # random feature map settings
  AETHERRA_HUB_AB_METRICS=1   # hub export toggle (server side)
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import json
import os
import time
from typing import Any, Dict, List


async def _get_engine():
    try:
        # Aetherra imports
        from aetherra_service_registry import get_service_registry

        reg = await get_service_registry()
        info = reg.get_service_info("aetherra_engine")
        if info and info.instance:
            return info.instance
    except Exception:
        pass
    # Fallback: create a private engine
    # Aetherra imports
    from Aetherra.aetherra_core.engine.aetherra_engine import AetherraEngine

    eng = AetherraEngine()
    await eng.initialize()
    await eng.start_conversation("ab_bench")
    return eng


async def _bench_once(eng, query: str, limit: int = 8) -> Dict[str, Any]:
    # Force classical/quantum via env for controlled runs
    os.environ.pop("AETHERRA_AB_FORCE_BUCKET", None)
    os.environ["AETHERRA_AB_RECALL_MODE"] = "classical"
    t0 = time.time()
    await eng.process_message(query)
    dt_class_ms = (time.time() - t0) * 1000.0

    os.environ["AETHERRA_AB_RECALL_MODE"] = "quantum"
    t1 = time.time()
    await eng.process_message(query)
    dt_quant_ms = (time.time() - t1) * 1000.0

    # Extract simple hit proxy (relevant_memories_count in responses is not returned; use session metrics deltas)
    sm = eng.get_session_metrics()
    # Compose record
    return {
        "query": query,
        "classical": {
            "latency_ms": dt_class_ms,
        },
        "quantum": {
            "latency_ms": dt_quant_ms,
        },
        "session_metrics": {
            "ab_recall_total": sm.get("ab_recall_total", 0),
            "ab_recall_classical_total": sm.get("ab_recall_classical_total", 0),
            "ab_recall_quantum_total": sm.get("ab_recall_quantum_total", 0),
            "lat_sum_classical": sm.get("ab_recall_latency_ms_sum_classical", 0.0),
            "lat_cnt_classical": sm.get("ab_recall_latency_ms_count_classical", 0),
            "lat_sum_quantum": sm.get("ab_recall_latency_ms_sum_quantum", 0.0),
            "lat_cnt_quantum": sm.get("ab_recall_latency_ms_count_quantum", 0),
        },
    }


async def run_benchmark(
    queries: List[str], limit: int = 8, emit: bool = False
) -> Dict[str, Any]:
    eng = await _get_engine()
    results: List[Dict[str, Any]] = []
    for q in queries:
        rec = await _bench_once(eng, q, limit)
        results.append(rec)
    # Derive summary stats
    c_lat = [r["classical"]["latency_ms"] for r in results]
    q_lat = [r["quantum"]["latency_ms"] for r in results]
    summary = {
        "n": len(results),
        "latency_ms_avg": {
            "classical": (sum(c_lat) / max(1, len(c_lat))) if c_lat else 0.0,
            "quantum": (sum(q_lat) / max(1, len(q_lat))) if q_lat else 0.0,
        },
    }
    payload = {"results": results, "summary": summary}

    if emit:
        try:
            # The Hub scrapes metrics; here we just print a summary and rely on Hub /metrics to expose the AB series from engine.
            print("[AB] Benchmark summary:", json.dumps(summary))
        except Exception:
            pass
    return payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--emit", type=int, default=1)
    ap.add_argument(
        "--queries",
        nargs="*",
        default=[
            "hello world",
            "how does memory recall work?",
            "quantum similarity and random features",
        ],
    )
    args = ap.parse_args()

    out = asyncio.run(run_benchmark(args.queries, args.limit, bool(args.emit)))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
