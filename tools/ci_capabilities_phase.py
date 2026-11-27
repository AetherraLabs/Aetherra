"""Lifecycle evidence enabled only by the capability CI supervisor."""

# Standard library imports
import asyncio
import contextlib
import importlib.metadata
import json
import os
import platform
import signal
import sys
import time
import types
from itertools import islice
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from tools.ci_capabilities_diagnostics import clean_stacks, emit, read_process

FLAGS = (
    "AETHERRA_PROFILE",
    "AETHERRA_QUIET",
    "TESTING",
    "TEST_MODE",
    "AETHERRA_QFAC_IN_OS",
    "AETHERRA_QFAC_MODE",
    "HF_HUB_OFFLINE",
    "TRANSFORMERS_OFFLINE",
    "AETHERRA_STORM_ENABLED",
)
VALUES = {
    "0",
    "1",
    "true",
    "false",
    "yes",
    "no",
    "on",
    "off",
    "test",
    "prod",
    "production",
    "development",
    "ci",
    "offline",
    "online",
    "hybrid",
    "classical",
    "quantum",
}


_async_capture = None


def _await_chain(coroutine, max_frames=32):
    frames = []
    seen = set()
    for _ in range(max_frames):
        if id(coroutine) in seen:
            break
        seen.add(id(coroutine))
        if isinstance(coroutine, types.CoroutineType):
            frame, following = coroutine.cr_frame, coroutine.cr_await
        elif isinstance(coroutine, types.GeneratorType):
            frame, following = coroutine.gi_frame, coroutine.gi_yieldfrom
        elif isinstance(coroutine, types.AsyncGeneratorType):
            frame, following = coroutine.ag_frame, coroutine.ag_await
        else:
            break
        if frame is not None:
            frames.append(
                {
                    "name": frame.f_code.co_qualname,
                    "filename": frame.f_code.co_filename,
                    "line": frame.f_lineno,
                }
            )
        coroutine = following
    return clean_stacks([{"frames": frames}])[0]["frames"]


def _capture_async_stacks(state, loop):
    try:
        if not state["enabled"]:
            return
        deadline = time.monotonic() + 0.05
        tasks = []
        remaining = 256
        for task in islice(asyncio.all_tasks(loop), 32):
            if remaining <= 0 or time.monotonic() >= deadline:
                break
            frames = _await_chain(task.get_coro(), min(32, remaining))
            remaining -= len(frames)
            tasks.append({"frames": frames})
        emit(
            state["output"],
            "async-stacks.jsonl",
            {
                "pid": state["pid"],
                "time": time.monotonic(),
                "tasks": tasks,
            },
        )
    except Exception:
        return  # Diagnostics cannot fail a test or expose exception payloads.
    finally:
        state["pending"] = False


def _request_async_capture(state):
    if not state["enabled"] or state["pending"]:
        return
    try:
        loop = asyncio.get_running_loop()
        state["pending"] = True
        loop.call_soon_threadsafe(_capture_async_stacks, state, loop)
    except Exception:
        state["pending"] = False


def _disable_async_capture():
    global _async_capture
    state, _async_capture = _async_capture, None
    if state is None:
        return
    state["enabled"] = False
    # A supervisor may already have read the marker. Late signals stay harmless.
    with contextlib.suppress(OSError, ValueError):
        if signal.getsignal(signal.SIGUSR1) is state["handler"]:
            signal.signal(signal.SIGUSR1, signal.SIG_IGN)
    with contextlib.suppress(OSError):
        state["marker"].unlink(missing_ok=True)


def _install_async_capture(output):
    global _async_capture
    if sys.platform != "linux" or _async_capture is not None:
        return
    if signal.getsignal(signal.SIGUSR1) not in (signal.SIG_DFL, signal.SIG_IGN):
        return
    identity = read_process(os.getpid())
    if identity is None:
        return
    marker = output / f"async-ready-{os.getpid()}.json"
    state = {
        "enabled": True,
        "pending": False,
        "output": output,
        "pid": os.getpid(),
        "marker": marker,
    }

    def handler(signum, frame):
        _request_async_capture(state)

    state["handler"] = handler
    temporary = marker.with_suffix(".tmp")
    try:
        signal.signal(signal.SIGUSR1, handler)
        _async_capture = state
        output.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(identity) + "\n", encoding="utf-8")
        temporary.replace(marker)
    except (OSError, ValueError):
        _disable_async_capture()
    finally:
        with contextlib.suppress(OSError):
            temporary.unlink(missing_ok=True)


def environment_flags():
    return {
        name: (value if value.lower() in VALUES else "set")
        for name in FLAGS
        if (value := os.environ.get(name)) is not None
    }


def record(phase, nodeid=None, state="start"):
    folder = os.environ.get("AETHERRA_CI_DIAGNOSTICS")
    if folder:
        emit(
            Path(folder),
            "phases.jsonl",
            {
                "pid": os.getpid(),
                "time": time.monotonic(),
                "phase": phase,
                "nodeid": nodeid,
                "state": state,
                "flags": environment_flags() if state == "start" else {},
            },
        )


def pytest_configure(config):
    folder = os.environ.get("AETHERRA_CI_DIAGNOSTICS")
    if not folder:
        return
    _install_async_capture(Path(folder))
    versions = {}
    for name in (
        "pytest",
        "pytest-asyncio",
        "requests",
        "httpx",
        "flask",
        "torch",
        "transformers",
        "sentence-transformers",
        "psutil",
    ):
        try:
            versions[name] = importlib.metadata.version(name)
        except Exception as exc:
            versions[name] = type(exc).__name__
    flags = {
        name: (value if value.lower() in VALUES else "set")
        for name in FLAGS
        if (value := os.environ.get(name)) is not None
    }
    emit(
        Path(folder),
        "environment.jsonl",
        {"python": platform.python_version(), "packages": versions, "flags": flags},
    )
    record("collection")


def pytest_collection_finish(session):
    record("collection", state="complete")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_setup(item):
    record("setup", item.nodeid)
    yield
    record("setup", item.nodeid, "complete")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    record("call", item.nodeid)
    yield
    record("call", item.nodeid, "complete")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_teardown(item):
    record("teardown", item.nodeid)
    yield
    record("teardown", item.nodeid, "complete")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    record("sessionfinish")
    yield
    record("sessionfinish", state="complete")


def pytest_unconfigure(config):
    _disable_async_capture()
    record("unconfigure")
