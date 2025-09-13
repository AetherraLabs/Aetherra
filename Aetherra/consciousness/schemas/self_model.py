#!/usr/bin/env python3
"""Self-Model Schema

Represents the system's structured self-description used for coherence checks
and adaptive reasoning. Designed to be compact, versioned, and forward-extensible.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

SELF_MODEL_VERSION = 1


class CapabilityDescriptor(BaseModel):
    name: str = Field(..., description="Stable capability identifier")
    enabled: bool = Field(..., description="Whether capability is currently active")
    confidence: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="System confidence in this capability functioning correctly",
    )
    last_verified: Optional[datetime] = Field(
        None, description="Last successful self-test timestamp"
    )


class ResourceProfile(BaseModel):
    cpu_load: Optional[float] = Field(
        None, ge=0.0, le=100.0, description="Approximate CPU load %"
    )
    memory_used_mb: Optional[float] = Field(
        None, ge=0.0, description="Resident memory in MB"
    )
    open_file_descriptors: Optional[int] = Field(
        None, ge=0, description="Current open file descriptors if available"
    )
    processes: Optional[int] = Field(
        None, ge=0, description="Number of relevant processes/agents"
    )


class IdentityProfile(BaseModel):
    system_id: str = Field(..., description="Stable unique system identifier")
    version: str = Field(
        ..., description="System software version or git describe output"
    )
    deployment_tier: str = Field(..., description="Deployment tier: dev/test/beta/prod")


class SelfModel(BaseModel):
    model_version: int = Field(
        SELF_MODEL_VERSION, description="Schema version for migrations"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last updated timestamp (UTC)"
    )
    identity: IdentityProfile
    capabilities: List[CapabilityDescriptor]
    resources: ResourceProfile
    coherence_score: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Recent self-coherence estimate (1=fully consistent)",
    )
    anomalies: List[str] = Field(
        default_factory=list, description="Recent anomaly codes detected in self-tests"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_version": SELF_MODEL_VERSION,
                "updated_at": "2025-09-01T12:00:00Z",
                "identity": {
                    "system_id": "aetherra-node-001",
                    "version": "v1.2.3",
                    "deployment_tier": "dev",
                },
                "capabilities": [
                    {
                        "name": "planning",
                        "enabled": True,
                        "confidence": 0.97,
                        "last_verified": "2025-09-01T11:58:00Z",
                    }
                ],
                "resources": {
                    "cpu_load": 34.5,
                    "memory_used_mb": 512.2,
                    "processes": 5,
                },
                "coherence_score": 0.99,
                "anomalies": [],
            }
        }
