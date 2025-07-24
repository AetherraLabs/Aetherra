#!/usr/bin/env python3
"""
Aetherra .aether Script Execution API Server
============================================

FastAPI-based REST API for executing and managing .aether scripts.
Provides endpoints for running scripts, monitoring job status, and system health.
"""

import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .job_controller import job_controller
from .models import (
    CancelResponse,
    ErrorResponse,
    HealthResponse,
    JobListResponse,
    RunRequest,
    RunResponse,
    StatusResponse,
)

# Create FastAPI application
app = FastAPI(
    title="Aetherra Script Execution API",
    description="REST API for executing and managing .aether scripts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store server start time for uptime calculation
server_start_time = time.time()


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Aetherra Script Execution API",
        "version": "1.0.0",
        "description": "REST API for executing and managing .aether scripts",
        "endpoints": {
            "health": "/health",
            "run_script": "/run",
            "job_status": "/status/{job_id}",
            "cancel_job": "/cancel/{job_id}",
            "list_jobs": "/jobs",
            "documentation": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    uptime_seconds = time.time() - server_start_time
    uptime_hours = int(uptime_seconds // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    uptime = f"{uptime_hours}h {uptime_minutes}m"

    stats = job_controller.get_system_stats()

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        uptime=uptime,
        active_jobs=stats.get("active_jobs", 0),
    )


@app.post("/run", response_model=RunResponse)
async def run_script(request: RunRequest):
    """
    Execute a .aether script asynchronously

    - **script_name**: Name of the .aether script to execute (e.g., "goal_autopilot.aether")
    - **parameters**: Optional parameters to pass to the script
    - **context**: Optional execution context
    """
    try:
        job_id = job_controller.run_script(
            request.script_name, request.parameters, request.context
        )

        return RunResponse(
            job_id=job_id,
            status="started",
            script_name=request.script_name,
            started_at=datetime.now(timezone.utc),
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Script not found: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start script execution: {str(e)}"
        )


@app.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """
    Get the status and results of a job

    - **job_id**: Unique identifier of the job to query
    """
    job_data = job_controller.get_job_status(job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    return StatusResponse(**job_data)


@app.post("/cancel/{job_id}", response_model=CancelResponse)
async def cancel_job(job_id: str):
    """
    Cancel a running or pending job

    - **job_id**: Unique identifier of the job to cancel
    """
    job_data = job_controller.get_job_status(job_id)

    if not job_data:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    success = job_controller.cancel_job(job_id)

    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job {job_id} - job may already be completed",
        )

    return CancelResponse(
        job_id=job_id,
        status="cancelled",
        message="Job cancelled successfully",
        cancelled_at=datetime.now(timezone.utc),
    )


@app.get("/jobs", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = Query(
        None,
        description="Filter by status (pending, running, completed, failed, cancelled)",
    ),
    limit: Optional[int] = Query(
        50, description="Maximum number of jobs to return", le=1000
    ),
):
    """
    List jobs with optional filtering

    - **status**: Optional status filter
    - **limit**: Maximum number of jobs to return (default: 50, max: 1000)
    """
    try:
        jobs_data = job_controller.list_jobs(status, limit)
        jobs = [StatusResponse(**job) for job in jobs_data]

        return JobListResponse(jobs=jobs, total=len(jobs))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@app.get("/scripts", response_model=dict)
async def list_available_scripts():
    """List available .aether scripts"""
    try:
        stats = job_controller.get_system_stats()
        return {
            "scripts": stats.get("available_scripts", []),
            "count": len(stats.get("available_scripts", [])),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scripts: {str(e)}")


@app.get("/stats", response_model=dict)
async def get_system_statistics():
    """Get detailed system statistics"""
    try:
        stats = job_controller.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get statistics: {str(e)}"
        )


@app.delete("/jobs/cleanup", response_model=dict)
async def cleanup_old_jobs():
    """Clean up old completed jobs to free memory"""
    try:
        cleaned_count = job_controller.cleanup_old_jobs()
        return {
            "message": f"Cleaned up {cleaned_count} old jobs",
            "cleaned_count": cleaned_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup jobs: {str(e)}")


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="NotFound",
            message="The requested resource was not found",
            details={"path": str(request.url.path)},
        ).dict(),
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An internal server error occurred",
            details={"error": str(exc)},
        ).dict(),
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    print("🚀 Aetherra Script Execution API starting up...")
    print(
        f"📊 Available scripts: {len(job_controller.get_system_stats().get('available_scripts', []))}"
    )
    print("✅ API ready to receive requests")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print("🛑 Aetherra Script Execution API shutting down...")
    # Perform any necessary cleanup here
    print("✅ Shutdown complete")


if __name__ == "__main__":
    import uvicorn

    # Run the server
    uvicorn.run(
        "aether_server:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
