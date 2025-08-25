from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional


# Exceptions (explicit error model)
class MemoryNotFound(Exception):
    pass


class QuantumBridgeUnavailable(Exception):
    pass


class CompressionFailure(Exception):
    pass


class PolicyViolation(Exception):
    def __init__(self, reason: str, code: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.code = code


RecallSource = Literal["core", "conceptual", "episodic", "hybrid", "qfac"]


@dataclass
class MemoryRecallResult:
    """Canonical typed recall contract.

    items: list of typed records or dict payloads. Each item should include a
    'kind' discriminator when available. For gradual adoption we allow dicts.
    """

    items: List[Any]
    source: RecallSource = "hybrid"
    scores: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NarrativeRecord:
    id: str
    title: str
    body: str
    summary: Optional[str]
    time_range: Optional[tuple]
    narrative_type: Literal["daily", "weekly", "thematic", "reflection"]
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    derived_from: List[str] = field(default_factory=list)


@dataclass
class QuantumShadowRecord:
    operation: Literal[
        "encode",
        "retrieve",
        "interference",
        "error_correction",
    ]
    inputs: Dict[str, Any]
    backend: str
    circuit_fingerprint: str
    measurement_results: Dict[str, Any]
    fidelity_estimates: Dict[str, Any] | None = None
    timestamp_utc: Optional[str] = None
