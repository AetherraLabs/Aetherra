#!/usr/bin/env python3
"""Narrative Chapter Schema

Aggregated episodic summary compiled periodically to track coherent arcs.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

NARRATIVE_SCHEMA_VERSION = 1


class NarrativeChapter(BaseModel):
    schema_version: int = Field(NARRATIVE_SCHEMA_VERSION, description="Schema version")
    id: str = Field(..., description="Unique chapter id")
    start_ts: datetime = Field(..., description="Start timestamp of covered period")
    end_ts: datetime = Field(..., description="End timestamp of covered period")
    summary: str = Field(..., description="High-level consolidated narrative summary")
    key_events: List[str] = Field(
        default_factory=list, description="Referenced episodic event ids"
    )
    coherence_index: float = Field(
        1.0, ge=0.0, le=1.0, description="Narrative coherence metric (1=coherent)"
    )
    anomalies: List[str] = Field(
        default_factory=list, description="Narrative anomaly codes detected"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": NARRATIVE_SCHEMA_VERSION,
                "id": "chapter-2025-09-01T12:00Z",
                "start_ts": "2025-09-01T12:00:00Z",
                "end_ts": "2025-09-01T12:15:00Z",
                "summary": "System performed health checks and adjusted plans due to elevated uncertainty.",
                "key_events": ["01JABCDEF1234567890"],
                "coherence_index": 0.94,
                "anomalies": [],
            }
        }
