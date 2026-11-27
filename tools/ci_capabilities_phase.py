"""Lifecycle evidence enabled only by the capability CI supervisor."""

# Standard library imports
import importlib.metadata
import os
import platform
import time
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from tools.ci_capabilities_diagnostics import emit

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
    record("unconfigure")
