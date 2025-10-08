"""QFAC core models and helper utilities.

This module defines the MemoryRecord contract and related structures for the
compression-aware memory pipeline. It keeps imports light and gracefully
handles optional dependencies.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple

try:  # Optional dependency for faster hashing
    import blake3  # type: ignore
except Exception:  # pragma: no cover - optional
    blake3 = None


Vector = Sequence[float]


@dataclass
class Edge:
    to: str
    type: Literal["causes", "supports", "refutes", "temporal_next", "related"] = "related"
    weight: float = 1.0
    confidence: float = 1.0


@dataclass
class FractalSignature:
    scales: List[int]
    coeffs: List[List[Tuple[int, float]]]  # per-scale top-k: (index, value)
    motifs: List[str]  # hashed motifs


@dataclass
class ObserverState:
    agent_id: str
    perspective: str = "default"
    priors: Dict[str, float] = field(default_factory=dict)
    priors_hash: str = ""

    def materialize(self) -> ObserverState:
        if self.priors_hash:
            return self
        # Stable hash of priors dict
        items = sorted(self.priors.items())
        raw = (
            json.dumps(items, separators=",") if False else json.dumps(items, separators=(",", ":"))
        )
        if blake3:
            self.priors_hash = blake3.blake3(raw.encode("utf-8")).hexdigest()
        else:
            self.priors_hash = hashlib.blake2b(raw.encode("utf-8")).hexdigest()
        return self


ContentType = str | bytes | Dict[str, Any]


@dataclass
class MemoryRecord:
    id: str
    timestamp: int
    content: ContentType
    embedding: Optional[Vector] = None  # or product-quantized codes later
    pq_code: Optional[List[int]] = None
    causal_links: List[Edge] = field(default_factory=list)
    observer_state: Optional[Dict[str, Any]] = None
    fractal_sig: Optional[FractalSignature] = None
    fidelity: Dict[str, float] = field(
        default_factory=lambda: {
            "recon_psnr": 1.0,
            "semantic_sim": 1.0,
            "causal_consistency": 1.0,
        }
    )
    qfac_meta: Dict[str, Any] = field(
        default_factory=lambda: {
            "tier": "T0",
            "codec": "none",
            "version": "2.5.0",
            "error_bound": {
                "semantic_sim": 0.97,
                "recon_psnr": 0.90,
            },
            "last_rewrite": 0,
        }
    )
    hash: str = ""
    merkle_path: List[str] = field(default_factory=list)

    def ensure_ids(self):
        if not self.timestamp:
            self.timestamp = int(time.time())
        if not self.hash:
            self.hash = compute_content_hash(self.content)

    def to_dict(self) -> Dict[str, Any]:  # pragma: no cover - thin wrapper
        d = asdict(self)
        if self.fractal_sig:
            d["fractal_sig"] = asdict(self.fractal_sig)
        return d

    @classmethod
    def new(
        cls,
        content: ContentType,
        *,
        embedding: Optional[Sequence[float]] = None,
    ) -> MemoryRecord:
        """Factory used by the lightweight qfac_api tests.

        Generates an id from a content+timestamp hash and sets current timestamp.
        """
        now = int(time.time())
        # derive a short id from content+timestamp hash for uniqueness
        base_hash = compute_content_hash({"content": content, "ts": now})
        rid = base_hash[:16]
        return cls(
            id=rid,
            timestamp=now,
            content=content,
            embedding=(list(embedding) if embedding is not None else None),
        )


def compute_content_hash(content: ContentType) -> str:
    try:
        if isinstance(content, (bytes | bytearray)):
            raw = bytes(content)
        elif isinstance(content, str):
            raw = content.encode("utf-8")
        else:
            raw = json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if blake3:  # Prefer fast blake3 when available
            return str(blake3.blake3(raw).hexdigest())
        return hashlib.blake2b(raw).hexdigest()
    except Exception:  # Fallback in worst case
        return hashlib.sha256(str(content).encode("utf-8")).hexdigest()
