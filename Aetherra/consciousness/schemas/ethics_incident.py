#!/usr/bin/env python3
"""Ethics Incident Schema

Records an ethics evaluation result, including any veto actions or counter-proposals.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

ETHICS_SCHEMA_VERSION = 1


class EthicsIncident(BaseModel):
    schema_version: int = Field(ETHICS_SCHEMA_VERSION, description="Schema version")
    id: str = Field(..., description="Unique incident id")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Timestamp UTC")
    action_description: str = Field(
        ..., description="Natural language description of proposed action"
    )
    risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="Estimated ethical risk (1=highest)"
    )
    policy_flags: list[str] = Field(
        default_factory=list, description="Policy flag identifiers triggered"
    )
    decision: str = Field(..., description="allow|veto|revise")
    counter_proposal: Optional[str] = Field(
        None, description="Suggested safer alternative if veto or revise"
    )
    rationale: str = Field(..., description="Brief justification for decision")

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": ETHICS_SCHEMA_VERSION,
                "id": "incident-001",
                "ts": "2025-09-01T12:00:10Z",
                "action_description": "Access external URL http://example.com/data",
                "risk_score": 0.65,
                "policy_flags": ["external_network", "data_exfiltration_uncertain"],
                "decision": "revise",
                "counter_proposal": "Request user confirmation before network access",
                "rationale": "Network egress policy requires explicit allowlist confirmation",
            }
        }
