"""Local semantic ranking for conversation recall, not a memory store.

The public model must be provisioned beforehand. Never download models or send
personal text to an embedding service during recall. Missing model/dependency
fails explicitly so the caller can report degraded retrieval.
"""
from __future__ import annotations

from functools import lru_cache
from threading import RLock

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
MIN_SIMILARITY = 0.35
_lock = RLock()


@lru_cache(maxsize=1)
def _encoder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(
        MODEL,
        revision=REVISION,
        device="cpu",
        local_files_only=True,
        trust_remote_code=False,
    )


def rank(
    query: str, records: list[tuple[str, str]], limit: int
) -> list[tuple[str, float]]:
    """Return a bounded ranking of relevant IDs; no recency/importance boost.

    Linear scan is intentional for this local milestone. The store stays in
    SQLite; only selected evidence is supplied to generation. Hash-seeded
    prototype embeddings elsewhere in Memory are not used here.
    """
    if not records or limit <= 0:
        return []
    with _lock:
        vectors = _encoder().encode(
            [query, *(text for _, text in records)],
            normalize_embeddings=True,
            show_progress_bar=False,
        )
    ranked = [
        (record_id, float(vectors[0] @ vector))
        for (record_id, _), vector in zip(records, vectors[1:], strict=True)
    ]
    ranked = [
        (record_id, score) for record_id, score in ranked if score >= MIN_SIMILARITY
    ]
    return sorted(ranked, key=lambda item: (-item[1], item[0]))[:limit]
