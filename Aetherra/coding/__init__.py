"""Coding System readiness foundation.

The Coding System foundation is intentionally non-mutating. It reports whether
the current repository has the governed prerequisites needed for AI-assisted
coding workflows, while leaving privileged change application to Guardian,
Security, and Self-Incorporation.
"""

from .readiness import (
    CODING_READINESS_CONTRACT_VERSION,
    assess_coding_readiness,
    build_coding_status_payload,
)

__all__ = [
    "CODING_READINESS_CONTRACT_VERSION",
    "assess_coding_readiness",
    "build_coding_status_payload",
]
