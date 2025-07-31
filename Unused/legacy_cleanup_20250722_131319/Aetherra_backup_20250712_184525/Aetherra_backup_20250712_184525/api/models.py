#!/usr/bin/env python3
"""
FastAPI Models for Aetherra .aether Script Execution API
========================================================

Pydantic models defining request/response schemas for the API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    """Request model for running a .aether script"""

    script_name: str = Field(..., description="Name of the .aether script to execute")
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters to pass to the script"
    )
    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional execution context"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "script_name": "goal_autopilot.aether",
                "parameters": {"scan_interval": "30 minutes"},
                "context": {"priority": "high"},
            }
        }


class RunResponse(BaseModel):
    """Response model for script execution start"""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(..., description="Current status of the job")
    script_name: str = Field(..., description="Name of the script being executed")
    started_at: datetime = Field(..., description="When the job was started")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "started",
                "script_name": "goal_autopilot.aether",
                "started_at": "2025-07-07T12:00:00Z",
            }
        }


class StatusResponse(BaseModel):
    """Response model for job status queries"""

    job_id: str = Field(..., description="Unique identifier for the job")
    script_name: str = Field(..., description="Name of the script being executed")
    status: str = Field(
        ...,
        description="Current status: pending, running, completed, failed, cancelled",
    )
    output: Optional[Dict[str, Any]] = Field(
        None, description="Script execution output/results"
    )
    error: Optional[str] = Field(None, description="Error message if job failed")
    started_at: Optional[datetime] = Field(None, description="When the job was started")
    completed_at: Optional[datetime] = Field(None, description="When the job completed")
    progress: Optional[Dict[str, Any]] = Field(
        None, description="Progress information if available"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "script_name": "goal_autopilot.aether",
                "status": "completed",
                "output": {"processed": 5, "resumed": 2, "escalated": 1},
                "started_at": "2025-07-07T12:00:00Z",
                "completed_at": "2025-07-07T12:05:00Z",
            }
        }


class CancelResponse(BaseModel):
    """Response model for job cancellation"""

    job_id: str = Field(..., description="Unique identifier for the job")
    status: str = Field(..., description="Updated status after cancellation")
    message: str = Field(..., description="Cancellation result message")
    cancelled_at: datetime = Field(..., description="When the job was cancelled")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "cancelled",
                "message": "Job cancelled successfully",
                "cancelled_at": "2025-07-07T12:02:30Z",
            }
        }


class JobListResponse(BaseModel):
    """Response model for listing jobs"""

    jobs: list[StatusResponse] = Field(..., description="List of job statuses")
    total: int = Field(..., description="Total number of jobs")

    class Config:
        json_schema_extra = {
            "example": {
                "jobs": [
                    {
                        "job_id": "123e4567-e89b-12d3-a456-426614174000",
                        "script_name": "goal_autopilot.aether",
                        "status": "completed",
                        "started_at": "2025-07-07T12:00:00Z",
                    }
                ],
                "total": 1,
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check"""

    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    uptime: str = Field(..., description="Service uptime")
    active_jobs: int = Field(..., description="Number of currently active jobs")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "uptime": "2h 30m",
                "active_jobs": 3,
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error cases"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error description")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ScriptNotFound",
                "message": "The specified script was not found",
                "details": {"script_name": "nonexistent.aether"},
            }
        }
