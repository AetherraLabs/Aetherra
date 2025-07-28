#!/usr/bin/env python3
"""
Job Store for Aetherra .aether Script Execution API
===================================================

In-memory storage for tracking job states, results, and metadata.
In production, this could be replaced with a database or Redis.
"""

import time
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional


class JobStatus(Enum):
    """Job status enumeration"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Job data model"""

    def __init__(
        self,
        job_id: str,
        script_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        self.job_id = job_id
        self.script_name = script_name
        self.parameters = parameters or {}
        self.context = context or {}
        self.status = JobStatus.PENDING
        self.output: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.progress: Optional[Dict[str, Any]] = None
        self.created_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for API responses"""
        return {
            "job_id": self.job_id,
            "script_name": self.script_name,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "created_at": self.created_at,
            "parameters": self.parameters,
            "context": self.context,
        }


class JobStore:
    """
    In-memory job storage with thread safety

    Provides methods to create, update, query, and manage job lifecycle.
    """

    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self.lock = Lock()
        self.start_time = time.time()

    def create_job(
        self,
        job_id: str,
        script_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Job:
        """Create a new job"""
        with self.lock:
            job = Job(job_id, script_name, parameters, context)
            self.jobs[job_id] = job
            return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        with self.lock:
            return self.jobs.get(job_id)

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> bool:
        """Update job status and related fields"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False

            job.status = status

            if status == JobStatus.RUNNING and not job.started_at:
                job.started_at = datetime.now(timezone.utc)
            elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                job.completed_at = datetime.now(timezone.utc)

            if output is not None:
                job.output = output
            if error is not None:
                job.error = error

            return True

    def update_job_progress(self, job_id: str, progress: Dict[str, Any]) -> bool:
        """Update job progress information"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            job.progress = progress
            return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False

            if job.status in [
                JobStatus.COMPLETED,
                JobStatus.FAILED,
                JobStatus.CANCELLED,
            ]:
                return False  # Cannot cancel already finished jobs

            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(timezone.utc)
            return True

    def list_jobs(
        self, status_filter: Optional[JobStatus] = None, limit: Optional[int] = None
    ) -> List[Job]:
        """List jobs with optional filtering"""
        with self.lock:
            jobs = list(self.jobs.values())

            if status_filter:
                jobs = [job for job in jobs if job.status == status_filter]

            # Sort by creation time (newest first)
            jobs.sort(key=lambda x: x.created_at, reverse=True)

            if limit:
                jobs = jobs[:limit]

            return jobs

    def get_active_jobs_count(self) -> int:
        """Get count of active (pending or running) jobs"""
        with self.lock:
            return sum(
                1
                for job in self.jobs.values()
                if job.status in [JobStatus.PENDING, JobStatus.RUNNING]
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get job store statistics"""
        with self.lock:
            stats = {
                "total_jobs": len(self.jobs),
                "active_jobs": self.get_active_jobs_count(),
                "uptime_seconds": time.time() - self.start_time,
                "status_breakdown": {},
            }

            # Count jobs by status
            for status in JobStatus:
                count = sum(1 for job in self.jobs.values() if job.status == status)
                stats["status_breakdown"][status.value] = count

            return stats

    def cleanup_old_jobs(self, max_age_hours: int = 24, max_jobs: int = 1000) -> int:
        """
        Clean up old completed/failed jobs to prevent memory bloat
        Returns number of jobs cleaned up
        """
        with self.lock:
            if len(self.jobs) <= max_jobs:
                return 0

            cutoff_time = datetime.now(timezone.utc).timestamp() - (
                max_age_hours * 3600
            )

            jobs_to_remove = []
            for job_id, job in self.jobs.items():
                if (
                    job.status
                    in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
                    and job.created_at.timestamp() < cutoff_time
                ):
                    jobs_to_remove.append(job_id)

            # Remove oldest jobs first if we're still over the limit
            if len(self.jobs) - len(jobs_to_remove) > max_jobs:
                finished_jobs = [
                    (job_id, job.created_at)
                    for job_id, job in self.jobs.items()
                    if job.status
                    in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
                    and job_id not in jobs_to_remove
                ]
                finished_jobs.sort(key=lambda x: x[1])  # Sort by creation time

                additional_to_remove = len(self.jobs) - len(jobs_to_remove) - max_jobs
                for job_id, _ in finished_jobs[:additional_to_remove]:
                    jobs_to_remove.append(job_id)

            # Remove the jobs
            for job_id in jobs_to_remove:
                del self.jobs[job_id]

            return len(jobs_to_remove)


# Global job store instance
job_store = JobStore()
