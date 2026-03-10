#!/usr/bin/env python3
"""Affect Snapshot Schema

Represents a transient aggregate of affective state used to bias attention/prioritization.
Initial MVP: valence, arousal, uncertainty. Extensible with appraisal dimensions.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime

# Third party imports
from pydantic import BaseModel, Field

AFFECT_SCHEMA_VERSION = 1


class AffectSnapshot(BaseModel):
    schema_version: int = Field(AFFECT_SCHEMA_VERSION, description="Schema version")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Snapshot timestamp UTC")
    valence: float = Field(
        0.0, ge=-1.0, le=1.0, description="Pleasantness axis (-1 negative, 1 positive)"
    )
    arousal: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Activation/energy (0 calm, 1 highly activated)",
    )
    uncertainty: float = Field(0.0, ge=0.0, le=1.0, description="Epistemic uncertainty (0 certain)")
    rationale: str = Field("baseline", description="Brief explanation for current state")

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": AFFECT_SCHEMA_VERSION,
                "ts": "2025-09-01T12:00:05Z",
                "valence": 0.1,
                "arousal": 0.3,
                "uncertainty": 0.4,
                "rationale": "elevated uncertainty from failed tool invocation",
            }
        }
