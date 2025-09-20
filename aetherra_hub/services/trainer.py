"""Lightweight in-memory trainer service stub.

Supports capability tests expecting job/eval submission, status transitions,
listing, and metrics snapshot. Transitions are simulated with a short delay
using background threads. No real ML tasks are executed.
"""

from __future__ import annotations

# Standard library imports
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_ENABLED_ENV = "AETHERRA_TRAINER_ENABLED"

TRANSITION_DELAY = 0.75  # seconds to simulate running before completion


@dataclass
class _Job:
    job_id: str
    task: str = "sft"
    base_model: str | None = None
    dataset_id: str | None = None
    state: str = "queued"  # queued -> running -> completed|failed
    created_ts: float = field(default_factory=time.time)
    updated_ts: float = field(default_factory=time.time)


@dataclass
class _Eval:
    eval_id: str
    task: str = "eval"
    model: str | None = None
    dataset_id: str | None = None
    state: str = "queued"
    score: float | None = None
    created_ts: float = field(default_factory=time.time)
    updated_ts: float = field(default_factory=time.time)


_lock = threading.Lock()
_jobs: Dict[str, _Job] = {}
_evals: Dict[str, _Eval] = {}
_eval_last_score: float | None = None
_eval_runs_total: int = 0


def _enabled() -> bool:
    return os.environ.get(_ENABLED_ENV, "0") == "1"


def _bg_transition_job(job_id: str):
    time.sleep(0.25)
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.state = "running"
        job.updated_ts = time.time()
    time.sleep(TRANSITION_DELAY)
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.state = "completed"
        job.updated_ts = time.time()


def _bg_transition_eval(eval_id: str):
    time.sleep(0.25)
    with _lock:
        ev = _evals.get(eval_id)
        if not ev:
            return
        ev.state = "running"
        ev.updated_ts = time.time()
    time.sleep(TRANSITION_DELAY)
    with _lock:
        ev = _evals.get(eval_id)
        if not ev:
            return
        ev.state = "completed"
        ev.score = 0.75  # dummy score
        ev.updated_ts = time.time()
        global _eval_last_score, _eval_runs_total
        _eval_last_score = ev.score
        _eval_runs_total += 1


def submit_job(payload: dict) -> Optional[str]:
    if not _enabled():
        return None
    jid = str(uuid.uuid4())
    job = _Job(
        job_id=jid,
        task=payload.get("task", "sft"),
        base_model=payload.get("base_model"),
        dataset_id=payload.get("dataset_id"),
    )
    with _lock:
        _jobs[jid] = job
    t = threading.Thread(target=_bg_transition_job, args=(jid,), daemon=True)
    t.start()
    return jid


def submit_eval(payload: dict) -> Optional[str]:
    if not _enabled():
        return None
    eid = str(uuid.uuid4())
    ev = _Eval(
        eval_id=eid,
        task=payload.get("task", "eval"),
        model=payload.get("model"),
        dataset_id=payload.get("dataset_id"),
    )
    with _lock:
        _evals[eid] = ev
    t = threading.Thread(target=_bg_transition_eval, args=(eid,), daemon=True)
    t.start()
    return eid


def get_job(job_id: str) -> Optional[dict]:
    with _lock:
        j = _jobs.get(job_id)
        if not j:
            return None
        return j.__dict__.copy()


def get_eval(eval_id: str) -> Optional[dict]:
    with _lock:
        e = _evals.get(eval_id)
        if not e:
            return None
        return e.__dict__.copy()


def list_jobs() -> List[dict]:
    with _lock:
        return [j.__dict__.copy() for j in _jobs.values()]


def list_evals() -> List[dict]:
    with _lock:
        return [e.__dict__.copy() for e in _evals.values()]


def snapshot_metrics() -> dict:  # consumed by metrics_accum
    with _lock:
        jobs_state_counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
        for j in _jobs.values():
            jobs_state_counts[j.state] = jobs_state_counts.get(j.state, 0) + 1
        evals_state_counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
        for e in _evals.values():
            evals_state_counts[e.state] = evals_state_counts.get(e.state, 0) + 1
        running_jobs = jobs_state_counts.get("running", 0)
        return {
            "enabled": _enabled(),
            "jobs": jobs_state_counts,
            "jobs_running": running_jobs,
            "evals": evals_state_counts,
            "eval_runs_total": _eval_runs_total,
            "eval_last_score": _eval_last_score,
        }
