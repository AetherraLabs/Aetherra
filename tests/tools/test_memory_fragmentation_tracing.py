"""Memory measurement must not change the caller's global tracing session."""

# Standard library imports
import json
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

PROBE = """
import json
import sys
import tracemalloc
from contextlib import nullcontext
from unittest.mock import patch

sys.path.insert(0, sys.argv[1])
from tools.memory_fragmentation_metrics import measure_fragmentation

caller_owned = sys.argv[2] == "1"
snapshot_fails = sys.argv[3] == "1"
if caller_owned:
    tracemalloc.start(7)
sentinel = bytearray(256)
original_trace = tracemalloc.get_object_traceback(sentinel)
failure = patch.object(
    tracemalloc, "take_snapshot", side_effect=RuntimeError("snapshot unavailable")
) if snapshot_fails else nullcontext()
error = None
stats = None
try:
    with failure:
        stats = measure_fragmentation(workload_iterations=20)
except RuntimeError as exc:
    error = str(exc)
print(json.dumps({
    "tracing": tracemalloc.is_tracing(),
    "traceback_limit": tracemalloc.get_traceback_limit(),
    "caller_trace_preserved": original_trace is not None
        and tracemalloc.get_object_traceback(sentinel) == original_trace,
    "error": error,
    "stats": stats.to_dict() if stats else None,
}))
"""


@pytest.mark.parametrize("caller_owned", [False, True], ids=["owned", "borrowed"])
@pytest.mark.parametrize("snapshot_fails", [False, True], ids=["success", "failure"])
def test_measurement_restores_tracing_ownership(tmp_path, caller_owned, snapshot_fails):
    # Isolate tracing so this test cannot clear another test runner's snapshots.
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            "-c",
            PROBE,
            str(Path(__file__).resolve().parents[2]),
            str(int(caller_owned)),
            str(int(snapshot_fails)),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["tracing"] is caller_owned
    assert report["caller_trace_preserved"] is caller_owned
    if caller_owned:
        assert report["traceback_limit"] == 7
    if snapshot_fails:
        assert report["error"] == "snapshot unavailable"
    else:
        assert report["error"] is None
        assert report["stats"]["before_traces"] > 0
        assert report["stats"]["after_traces"] > 0
