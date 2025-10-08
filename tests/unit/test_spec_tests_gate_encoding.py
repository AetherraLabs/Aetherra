import os
import subprocess
import sys


def test_spec_tests_gate_handles_utf8_output():
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    # Run the script; we don't care about exit code here, only that it doesn't crash due to encoding
    p = subprocess.run(
        [sys.executable, "tools/spec_tests_gate.py"],
        capture_output=True,
        text=True,
        env=env,
    )
    # Must have produced some stdout or a clean stderr without Unicode errors
    stderr = p.stderr or ""
    assert "UnicodeEncodeError" not in stderr
    assert "UnicodeDecodeError" not in stderr
