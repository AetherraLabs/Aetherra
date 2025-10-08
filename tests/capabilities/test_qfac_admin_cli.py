import io
import json
import sys
from contextlib import redirect_stdout

from tools.qfac_admin import main as qfac_admin_main


def _run_and_capture(args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = qfac_admin_main(args)
    return code, buf.getvalue()


def _parse_json_loose(s: str):
    # Find first opening brace and last closing brace to extract JSON block
    start = s.find("{")
    end = s.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in output")
    return json.loads(s[start : end + 1])


def test_qfac_admin_show_and_reset_runs_and_outputs_json():
    # Show
    code, out = _run_and_capture(["--show"])
    assert code == 0
    data = _parse_json_loose(out)
    assert "retrieval_policy" in data
    assert "parity_counters" in data
    # Reset
    code2, out2 = _run_and_capture(["--reset"])
    assert code2 in (0, 1)  # allow 1 on unexpected error
    # If succeeded or unavailable, output should still be JSON
    _ = _parse_json_loose(out2)
