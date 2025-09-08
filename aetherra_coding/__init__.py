"""Aetherra Coding System (Lyrixa Code Studio)

Phase 0 scaffolding: public API surface.

Exports:
    CodeOrchestrator: plan/generate/apply_patch/verify/commit minimal API.

Environment flags honored (initial subset):
    AETHERRA_AUDIT (default=1) enable run audit logging.
    AETHERRA_AUDIT_PATH custom ledger path (default audit/aetherra_runs.jsonl).
    AETHERRA_MODE assist|co-drive|autopilot (default assist).

Future:
    - Agent routing
    - Refactor graph and semantic search
    - Plugin scaffolding logic
"""

from .orchestrator import (  # noqa: F401
    CodeOrchestrator,
    CommitResult,
    PatchResult,
    PlanResult,
    VerifyResult,
)
