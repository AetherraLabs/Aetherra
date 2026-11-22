"""Temporary bounded CI shutdown diagnosis; removed before the final patch."""

import faulthandler
import os
import subprocess
import sys
import threading

import psutil
import pytest


class ExitDiagnostics:
    def pytest_sessionfinish(self, session, exitstatus):
        print("EXIT_THREADS", [(t.name, t.daemon) for t in threading.enumerate()], flush=True)
        faulthandler.dump_traceback()


if os.environ.get("CAPABILITY_EXIT_CHILD"):
    faulthandler.dump_traceback_later(90, repeat=True)
    sys.exit(pytest.main(["-q", "-o", "addopts=", "tests/capabilities"], plugins=[ExitDiagnostics()]))

env = dict(os.environ, CAPABILITY_EXIT_CHILD="1")
process = subprocess.Popen([sys.executable, __file__], env=env, start_new_session=True)
try:
    code = process.wait(timeout=120)
    print("PYTEST_PROCESS_EXIT", code, flush=True)
except subprocess.TimeoutExpired:
    code = 124
    print("PYTEST_PROCESS_TIMEOUT", flush=True)
finally:
    # Orphans inherit this runner's environment but may have been reparented.
    for child in psutil.process_iter(["pid", "ppid", "name"]):
        try:
            if child.pid != os.getpid() and child.environ().get("CAPABILITY_EXIT_CHILD"):
                print("LEAKED_PROCESS", child.info, flush=True)
                child.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    process.wait(timeout=10)
sys.exit(code)
