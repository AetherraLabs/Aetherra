#!/usr/bin/env python3
"""
Aetherra .aether Script Execution API
====================================

FastAPI-based REST API for executing and managing .aether scripts.
"""

from .aether_server import app
from .job_controller import job_controller
from .job_store import JobStatus, job_store
from .models import CancelResponse, RunRequest, RunResponse, StatusResponse

__version__ = "1.0.0"
__all__ = [
    "app",
    "job_controller",
    "job_store",
    "JobStatus",
    "RunRequest",
    "RunResponse",
    "StatusResponse",
    "CancelResponse",
]
