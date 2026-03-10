#!/usr/bin/env python3
"""Episodic Event Schema

Atomic recorded event representing an observed or internally generated cognitive occurrence.
Optimized for append-only storage with optional summarization later.
"""

from __future__ import annotations

# Standard library imports
from datetime import datetime
from typing import List, Optional

# Third party imports
from pydantic import BaseModel, Field

EVENT_SCHEMA_VERSION = 1


class EventAttribution(BaseModel):
    source: str = Field(..., description="Origin component or module name")
    agent: Optional[str] = Field(None, description="If multi-agent, the agent identity")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence in attribution")


class EpisodicEvent(BaseModel):
    schema_version: int = Field(EVENT_SCHEMA_VERSION, description="Schema version")
    id: str = Field(..., description="Stable unique event id (UUID)")
    ts: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp UTC")
    type: str = Field(
        ...,
        description="Event category (thought, action, perception, affect, ethics, narrative)",
    )
    sub_type: Optional[str] = Field(None, description="Optional refined type classification")
    content: str = Field(..., description="Primary textual/structured content summary")
    raw: Optional[dict] = Field(None, description="Raw payload or data fragment")
    importance: float = Field(
        0.5, ge=0.0, le=1.0, description="Relative significance for retention policies"
    )
    attribution: EventAttribution
    tags: List[str] = Field(default_factory=list, description="Search/filter tags")
    workspace_priority: Optional[int] = Field(
        None, description="Priority if event generated a workspace candidate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "schema_version": EVENT_SCHEMA_VERSION,
                "id": "01JABCDEF1234567890",
                "ts": "2025-09-01T12:00:02Z",
                "type": "thought",
                "sub_type": "planning",
                "content": "Generated plan step: verify system health",
                "importance": 0.7,
                "attribution": {"source": "planner", "confidence": 0.93},
                "tags": ["plan", "health"],
                "workspace_priority": 5,
            }
        }
