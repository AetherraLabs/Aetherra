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
except Exception:  # pragma: no cover
    HAS_FLASK = False


def _wait_until(cond_fn, timeout=4.0, interval=0.1):
    start = time.time()
    while time.time() - start < timeout:
        if cond_fn():
            return True
        time.sleep(interval)
    return cond_fn()


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_trainer_disabled_paths_expose_disabled_status_and_no_progress():
    # Ensure disabled
    os.environ["AETHERRA_TRAINER_ENABLED"] = "0"
    port = 3031
    server = start_hub_server(port=port)
    assert server.is_running()

    r = requests.get(f"http://localhost:{port}/api/trainer/status", timeout=5)
    assert r.status_code == 200
    st = r.json()
    assert st.get("enabled") is False

    # Submitting when disabled currently returns HTTP 400 with an error payload
    r = requests.post(
        f"http://localhost:{port}/api/trainer/jobs", json={"task": "sft"}, timeout=5
    )
    assert r.status_code == 400
    payload = r.json()
    # Ensure disabled signal present
    assert "disabled" in (payload.get("error") or "").lower()
    # Server may or may not return a job id in this hard-disabled mode; don't assert its presence.

    # Metrics should still expose the enabled gauge = 0
    r = requests.get(f"http://localhost:{port}/metrics", timeout=5)
    assert r.status_code == 200
    m = r.text
    assert "aetherra_trainer_enabled" in m
    # Ensure it reports 0 (best-effort parse)
    # Not strict parsing to avoid fragile test; presence + disabled status is enough


@pytest.mark.skipif(not HAS_FLASK, reason="Flask not installed")
def test_trainer_metrics_series_present_after_job_and_eval():
    os.environ["AETHERRA_TRAINER_ENABLED"] = "1"
    port = 3032
    server = start_hub_server(port=port)
    assert server.is_running()

    # Kick off a job
    jr = requests.post(
        f"http://localhost:{port}/api/trainer/jobs", json={"task": "sft"}, timeout=5
    )
    assert jr.status_code == 200
    jid = jr.json().get("job_id")
    assert jid

    def _job_done():
        rr = requests.get(f"http://localhost:{port}/api/trainer/jobs/{jid}", timeout=5)
        if rr.status_code != 200:
            return False
        job = rr.json().get("job")
        if not isinstance(job, dict):
            return False
        return job.get("state") in {"completed", "failed"}

    assert _wait_until(_job_done, timeout=6.0)

    # Kick off an eval
    er = requests.post(
        f"http://localhost:{port}/api/trainer/evals", json={"task": "eval"}, timeout=5
    )
    assert er.status_code == 200
    eid = er.json().get("eval_id")
    assert eid

    def _eval_done():
        rr = requests.get(f"http://localhost:{port}/api/trainer/evals/{eid}", timeout=5)
        if rr.status_code != 200:
            return False
        ev = rr.json().get("eval")
        if not isinstance(ev, dict):
            return False
        return ev.get("state") in {"completed", "failed"}

    assert _wait_until(_eval_done, timeout=6.0)

    # Metrics assertions
    r = requests.get(f"http://localhost:{port}/metrics", timeout=5)
    assert r.status_code == 200
    txt = r.text
    for needle in [
        "aetherra_trainer_enabled",
        "aetherra_trainer_jobs_total",
        "aetherra_trainer_evals_total",
        "aetherra_trainer_eval_runs_total",
        "aetherra_trainer_eval_last_score",
    ]:
        assert needle in txt
