#!/usr/bin/env python3
# Lightweight learning KPI evaluator for Lyrixa/Aetherra

import argparse
import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def _norm_text(x: Any) -> str:
    if isinstance(x, str):
        return x
    try:
        return json.dumps(x, ensure_ascii=False)
    except Exception:
        return str(x)


def _extract_tags(item: dict[str, Any]) -> list[str]:
    t = item.get("tags")
    if isinstance(t, list):
        return [str(s).lower() for s in t]
    return []


def _hit_text(item: dict[str, Any]) -> str:
    title = item.get("title") or ""
    body = item.get("body") or item.get("content") or item.get("text") or ""
    return f"{title}\n{body}"


async def _get_memory_handle():
    """Best-effort handle to a memory search function across available systems."""
    # Try persistent memory first
    try:
        import sys

        sys.path.insert(0, str(WORKSPACE_ROOT))
        from aetherra_persistent_memory import (
            get_persistent_memory_system,  # type: ignore
        )

        return await get_persistent_memory_system()
    except Exception as exc:
        logging.debug("persistent_memory lookup failed: %s", exc)

    # Try service registry -> memory_system
    try:
        import sys

        sys.path.insert(0, str(WORKSPACE_ROOT))
        from aetherra_service_registry import get_service_registry  # type: ignore

        reg = await get_service_registry()
        mem = reg.get_service("memory_system") if reg else None
        if mem:
            return mem
    except Exception as exc:
        logging.debug("service_registry lookup failed: %s", exc)

    return None


async def _search(
    mem, query: str, top_k: int = 8
) -> tuple[list[dict[str, Any]], float]:
    """Search wrapper that tolerates different backends; returns (hits, latency_ms)."""
    start = time.perf_counter()
    hits: list[dict[str, Any]] = []
    try:
        # Lyrixa-style async API
        if hasattr(mem, "recall_memories"):
            res = await mem.recall_memories(query_text=query, limit=top_k)  # type: ignore
            hits = list(res) if isinstance(res, list) else []
        # Aetherra core engine API
        elif hasattr(mem, "retrieve"):
            import inspect

            fn = mem.retrieve
            if inspect.iscoroutinefunction(fn):
                try:
                    res = await fn(query, {"limit": top_k})  # type: ignore
                except TypeError:
                    res = await fn(query)  # type: ignore
            else:
                try:
                    res = fn(query, {"limit": top_k})  # type: ignore
                except TypeError:
                    res = fn(query)  # type: ignore
            hits = list(res) if isinstance(res, list) else []
        # Kernel compatibility API
        elif hasattr(mem, "process_query"):
            res = await mem.process_query({"query": query, "limit": top_k})  # type: ignore
            hits = list(res) if isinstance(res, list) else []
    except Exception:
        hits = []
    latency_ms = (time.perf_counter() - start) * 1000.0
    return hits, latency_ms


def _overlap(a: list[str], b: list[str]) -> int:
    sa, sb = {x.lower() for x in a}, {x.lower() for x in b}
    return len(sa & sb)


def _dup_ratio(docs: list[str], threshold: float = 0.92) -> float:
    # Simple Jaccard over token sets as a fast proxy
    toks = [set(t.lower().split()) for t in docs]
    n = len(toks)
    if n < 2:
        return 0.0
    dup = 0
    total = 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1
            a, b = toks[i], toks[j]
            inter = len(a & b)
            union = len(a | b) or 1
            jacc = inter / union
            if jacc >= threshold:
                dup += 1
    return dup / total if total else 0.0


async def compute_kpis(testset_path: Path) -> dict[str, Any]:
    with testset_path.open("r", encoding="utf-8") as f:
        cases = json.load(f)
    mem = await _get_memory_handle()
    if mem is None:
        return {
            "ok": False,
            "error": "memory_system_unavailable",
        }

    passes = 0
    latency_samples: list[float] = []
    doc_samples: list[str] = []

    for case in cases:
        q = case.get("query", "")
        expected_tags: list[str] = case.get("expected_tags", [])
        must_contain: list[str] = case.get("must_contain", [])
        hits, lat = await _search(mem, q, 8)
        latency_samples.append(lat)

        # Aggregate text and tags
        tag_union: list[str] = []
        text_blob_parts: list[str] = []
        for h in hits:
            tag_union.extend(_extract_tags(h))
            text_blob_parts.append(_hit_text(h))
            doc_samples.append(_hit_text(h))
        # Tag overlap check
        if _overlap(tag_union, expected_tags) > 0:
            passes += 1
        # Must contain all substrings
        text_blob = "\n".join(text_blob_parts).lower()
        if all(substr.lower() in text_blob for substr in must_contain):
            passes += 1

    recall = passes / (2 * max(1, len(cases)))

    # Coherence score: ask memory if available
    coherence = 0.0
    try:
        if hasattr(mem, "get_status"):
            st = await mem.get_status()  # type: ignore
            if isinstance(st, dict):
                coherence = float(st.get("coherence", 0.0) or 0.0)
    except Exception:
        coherence = 0.0

    # Drift: best-effort placeholder (0 unless memory exposes API in future)
    drift = 0.0

    # Redundancy: approximate by near-duplicate ratio among returned docs
    redundancy = _dup_ratio(doc_samples, threshold=0.92)

    latency_avg_ms = sum(latency_samples) / max(1, len(latency_samples))

    return {
        "ok": True,
        "recall": round(recall, 4),
        "coherence": round(coherence, 4),
        "drift": round(drift, 4),
        "redundancy": round(redundancy, 4),
        "latency_avg_ms": round(latency_avg_ms, 2),
        "cases": len(cases),
    }


def _write_report(report: dict[str, Any], out_path: Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Append to metrics JSONL for trend tracking
    metrics_dir = WORKSPACE_ROOT / "metrics"
    metrics_dir.mkdir(exist_ok=True)
    jl = metrics_dir / "learning_metrics.jsonl"
    row = {"ts": time.time(), **report}
    with jl.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


async def _amain(args):
    testset = Path(args.testset)
    out = Path(args.output)
    result = await compute_kpis(testset)
    _write_report(result, out)
    print(json.dumps(result, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser("Lyrixa Learning Evaluator")
    p.add_argument("testset", help="Path to golden testset JSON")
    p.add_argument(
        "--output", default=str(WORKSPACE_ROOT / "reports" / "learning_eval.json")
    )
    args = p.parse_args()
    asyncio.run(_amain(args))


if __name__ == "__main__":
    main()
