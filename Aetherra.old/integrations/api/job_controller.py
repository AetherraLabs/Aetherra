#!/usr/bin/env python3
"""
Job Controller for Aetherra .aether Script Execution API
========================================================

Orchestrates the execution of .aether scripts, manages job lifecycle,
and provides interfaces for monitoring and control.
"""

import threading
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .job_store import JobStatus, job_store


class AetherScriptRunner:
    """
    Handles the actual execution of .aether scripts

    This is a simplified implementation that can be enhanced to integrate
    with the actual Aetherra runtime system.
    """

    def __init__(self):
        self.script_base_path = Path("Aetherra/system")

    def find_script(self, script_name: str) -> Optional[Path]:
        """Find a .aether script by name"""
        script_path = self.script_base_path / script_name

        # If no extension provided, add .aether
        if not script_path.suffix:
            script_path = script_path.with_suffix(".aether")

        if script_path.exists():
            return script_path

        # Also check scripts directory
        alt_path = Path("Aetherra/scripts/system") / script_name
        if not alt_path.suffix:
            alt_path = alt_path.with_suffix(".aether")
        if alt_path.exists():
            return alt_path

        return None

    def execute_script(
        self,
        script_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a .aether script

        This is a placeholder implementation that simulates script execution.
        In the real implementation, this would integrate with the Aetherra
        enhanced language interpreter.
        """
        script_path = self.find_script(script_name)
        if not script_path:
            raise FileNotFoundError(f"Script '{script_name}' not found")

        # Read script content
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # Simulate script execution
        # TODO: Integrate with enhanced Aetherra interpreter
        result = {
            "script_name": script_name,
            "script_path": str(script_path),
            "parameters": parameters or {},
            "context": context or {},
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "simulated": True,
            "content_length": len(script_content),
            "lines": len(script_content.split("\n")),
        }

        # Add some simulated results based on script type
        if "goal_autopilot" in script_name:
            result.update({"processed": 5, "resumed": 2, "escalated": 1, "failed": 0})
        elif "test_" in script_name:
            result.update({"tests_run": 10, "passed": 9, "failed": 1, "success": True})
        else:
            result.update(
                {"status": "completed", "message": "Script executed successfully"}
            )

        return result


class JobController:
    """
    Main controller for managing .aether script execution jobs
    """

    def __init__(self):
        self.script_runner = AetherScriptRunner()
        self.running_jobs: Dict[str, threading.Thread] = {}

    def run_script(
        self,
        script_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start execution of a .aether script asynchronously

        Returns:
            job_id: Unique identifier for tracking the job
        """
        job_id = str(uuid.uuid4())

        # Create job in store
        job_store.create_job(job_id, script_name, parameters, context)

        # Start execution in background thread
        thread = threading.Thread(
            target=self._execute_job,
            args=(job_id,),
            daemon=True,
            name=f"AetherJob-{job_id[:8]}",
        )

        self.running_jobs[job_id] = thread
        thread.start()

        return job_id

    def _execute_job(self, job_id: str):
        """Execute a job in background thread"""
        job = job_store.get_job(job_id)
        if not job:
            return

        try:
            # Update job to running status
            job_store.update_job_status(job_id, JobStatus.RUNNING)

            # Execute the script
            result = self.script_runner.execute_script(
                job.script_name, job.parameters, job.context
            )

            # Update job with successful result
            job_store.update_job_status(job_id, JobStatus.COMPLETED, output=result)

        except Exception as e:
            # Update job with error
            error_msg = f"{type(e).__name__}: {str(e)}"
            job_store.update_job_status(job_id, JobStatus.FAILED, error=error_msg)

            # Log full traceback for debugging
            print(f"Job {job_id} failed with error: {error_msg}")
            print(traceback.format_exc())

        finally:
            # Clean up running job reference
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a job"""
        job = job_store.get_job(job_id)
        if not job:
            return None
        return job.to_dict()

    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a running job

        Note: This is a simplified implementation. For proper cancellation,
        we would need to implement cooperative cancellation in the script runner.
        """
        job = job_store.get_job(job_id)
        if not job:
            return False

        # If job is already finished, cannot cancel
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False

        # Mark job as cancelled in store
        success = job_store.cancel_job(job_id)

        # TODO: Implement actual thread interruption for running jobs
        # For now, we just mark it as cancelled in the store

        return success

    def list_jobs(
        self, status_filter: Optional[str] = None, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List jobs with optional filtering"""
        status_enum = None
        if status_filter:
            try:
                status_enum = JobStatus(status_filter)
            except ValueError:
                pass  # Invalid status filter, ignore

        jobs = job_store.list_jobs(status_enum, limit)
        return [job.to_dict() for job in jobs]

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        stats = job_store.get_stats()
        stats.update(
            {
                "running_threads": len(self.running_jobs),
                "available_scripts": self._get_available_scripts(),
            }
        )
        return stats

    def _get_available_scripts(self) -> List[str]:
        """Get list of available .aether scripts"""
        scripts = []

        # Check system directory
        system_path = Path("Aetherra/system")
        if system_path.exists():
            for script_file in system_path.glob("*.aether"):
                scripts.append(script_file.name)

        # Check scripts/system directory
        scripts_path = Path("Aetherra/scripts/system")
        if scripts_path.exists():
            for script_file in scripts_path.glob("*.aether"):
                scripts.append(script_file.name)

        return sorted(list(set(scripts)))  # Remove duplicates and sort

    def cleanup_old_jobs(self) -> int:
        """Clean up old completed jobs"""
        return job_store.cleanup_old_jobs()


# Global job controller instance
job_controller = JobController()
