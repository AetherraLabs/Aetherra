# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Standard library imports
import os
import time

# Third party imports
import pytest
import requests

# Aetherra imports
from aetherra_hub.compat import start_hub_server

HAS_FLASK = True
try:
    # Third party imports
    import flask  # noqa: F401
except Exception:
    HAS_FLASK = False


def _wait_until(cond_fn, timeout=6.0, interval=0.1):
    start = time.time()
    while time.time() - start < timeout:
        if cond_fn():
            return True
        time.sleep(interval)
    return cond_fn()


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_trainer_jobs_and_evals_endpoints_smoke():
    # Enable trainer features for this test
    os.environ["AETHERRA_TRAINER_ENABLED"] = "1"

    port = 3023
    server = start_hub_server(port=port)
    assert server.is_running()

    # Status endpoint
    r = requests.get(f"http://localhost:{port}/api/trainer/status", timeout=5)
    assert r.status_code == 200
    st = r.json()
    assert isinstance(st, dict)
    assert "enabled" in st

    # Submit a training job
    job_payload = {
        "task": "sft",
        "base_model": "dummy-model",
        "dataset_id": "small-ds",
    }
    r = requests.post(
        f"http://localhost:{port}/api/trainer/jobs", json=job_payload, timeout=5
    )
    assert r.status_code == 200
    jres = r.json()
    assert "job_id" in jres
    job_id = jres["job_id"]

    # Wait until job completes or fails (simulated ~0.75s)
    def _job_done():
        rr = requests.get(
            f"http://localhost:{port}/api/trainer/jobs/{job_id}", timeout=5
        )
        if rr.status_code != 200:
            return False
        jd = rr.json()
        job = jd.get("job") if isinstance(jd, dict) else None
        if not isinstance(job, dict):
            return False
        return job.get("state") in {"completed", "failed"}

    assert _wait_until(_job_done, timeout=8.0)

    # List jobs should include at least 1
    r = requests.get(f"http://localhost:{port}/api/trainer/jobs", timeout=5)
    assert r.status_code == 200
    jobs_payload = r.json()
    jobs = jobs_payload.get("jobs") if isinstance(jobs_payload, dict) else None
    assert isinstance(jobs, list) and len(jobs) >= 1

    # Submit an evaluation
    eval_payload = {
        "task": "eval",
        "model": "dummy-model",
        "dataset_id": "tiny-eval",
    }
    r = requests.post(
        f"http://localhost:{port}/api/trainer/evals", json=eval_payload, timeout=5
    )
    assert r.status_code == 200
    eres = r.json()
    assert "eval_id" in eres
    eval_id = eres["eval_id"]

    # Wait until eval completes
    def _eval_done():
        rr = requests.get(
            f"http://localhost:{port}/api/trainer/evals/{eval_id}", timeout=5
        )
        if rr.status_code != 200:
            return False
        ed = rr.json()
        ev = ed.get("eval") if isinstance(ed, dict) else None
        if not isinstance(ev, dict):
            return False
        return ev.get("state") in {"completed", "failed"}

    assert _wait_until(_eval_done, timeout=8.0)

    # List evals should include at least 1
    r = requests.get(f"http://localhost:{port}/api/trainer/evals", timeout=5)
    assert r.status_code == 200
    evals_payload = r.json()
    evals = evals_payload.get("evals") if isinstance(evals_payload, dict) else None
    assert isinstance(evals, list) and len(evals) >= 1

    # Metrics should expose trainer series
    r = requests.get(f"http://localhost:{port}/metrics", timeout=5)
    assert r.status_code == 200
    txt = r.text
    assert "aetherra_trainer_enabled" in txt
    assert "aetherra_trainer_jobs_total" in txt
    assert "aetherra_trainer_evals_total" in txt
    assert "aetherra_trainer_eval_runs_total" in txt
    assert "aetherra_trainer_eval_last_score" in txt
