"""Contracts for opt-in capability CI diagnostics."""

# Standard library imports
import importlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

# Third party imports
import pytest


@pytest.fixture
def diagnostics():
    return importlib.import_module("tools.ci_capabilities_diagnostics")


def records(output, name):
    return [json.loads(line) for line in (output / name).read_text().splitlines()]


def assert_process_stopped(diagnostics, pid):
    deadline = time.monotonic() + 1
    while time.monotonic() < deadline:
        process = diagnostics.read_process(pid)
        if process is None or process["state"] == "Z":
            return
        time.sleep(0.01)
    pytest.fail("Owned process survived bounded cleanup")


@pytest.mark.parametrize("status", [0, 1, 2, 5])
def test_forwards_child_exit_status(diagnostics, tmp_path, status):
    result = diagnostics.supervise(
        [sys.executable, "-c", f"raise SystemExit({status})"],
        tmp_path,
        timeout=5,
        checkpoints=(),
    )
    assert result == status


def test_normal_exit_records_state_before_cleanup(diagnostics, tmp_path):
    assert (
        diagnostics.supervise(
            [sys.executable, "-c", "raise SystemExit(7)"],
            tmp_path,
            timeout=5,
            checkpoints=(),
        )
        == 7
    )
    events = records(tmp_path, "supervisor.jsonl")
    cleanup = next(event for event in events if event["event"] == "before_cleanup")
    assert cleanup["child_returncode"] == 7
    assert cleanup["live_processes"] == []


@pytest.mark.skipif(sys.platform != "linux", reason="Linux survivor evidence contract")
@pytest.mark.parametrize("status", [0, 7])
def test_normal_exit_records_owned_survivor_before_reaping(
    diagnostics, tmp_path, status
):
    marker = tmp_path / "survivor.pid"
    code = (
        "import subprocess,sys,pathlib; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
        f"pathlib.Path({str(marker)!r}).write_text(str(p.pid)); raise SystemExit({status})"
    )
    assert (
        diagnostics.supervise(
            [sys.executable, "-c", code], tmp_path, timeout=5, checkpoints=()
        )
        == status
    )
    survivor = int(marker.read_text())
    cleanup = next(
        event
        for event in records(tmp_path, "supervisor.jsonl")
        if event["event"] == "before_cleanup"
    )
    assert cleanup["child_returncode"] == status
    assert {process["pid"] for process in cleanup["live_processes"]} == {survivor}
    assert_process_stopped(diagnostics, survivor)


def test_watchdog_is_bounded_and_reaps_child(diagnostics, tmp_path):
    started = time.monotonic()
    result = diagnostics.supervise(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        tmp_path,
        timeout=0.2,
        checkpoints=(),
    )
    assert result == 124
    assert time.monotonic() - started < 6
    events = records(tmp_path, "supervisor.jsonl")
    assert any(event["event"] == "watchdog" for event in events)
    assert events[-1]["event"] == "exit"
    assert events[-1]["reaped"] is True


def write_process(root, pid, parent, session, started, state="S"):
    folder = root / str(pid)
    folder.mkdir()
    fields = [state, str(parent), str(session), str(session)] + ["0"] * 18
    fields[17] = "3"
    fields[19] = str(started)
    (folder / "stat").write_text(f"{pid} (name with ) spaces) " + " ".join(fields))


def test_session_scope_excludes_siblings_and_reused_id(diagnostics, tmp_path):
    write_process(tmp_path, 10, 1, 10, 100)
    write_process(tmp_path, 11, 10, 10, 101)
    write_process(tmp_path, 12, 1, 10, 102)  # Reparented owned child.
    write_process(tmp_path, 13, 1, 13, 103)  # Unrelated sibling.
    write_process(tmp_path, 14, 1, 10, 99)  # Predates the owned session.
    found = diagnostics.owned_processes(10, 100, tmp_path)
    assert {process["pid"] for process in found} == {10, 11, 12}
    assert found[0]["threads"] == 3
    assert diagnostics.same_process({**found[0], "start": 999}, tmp_path) is False


def test_reused_session_leader_excludes_its_new_descendants(diagnostics, tmp_path):
    write_process(tmp_path, 10, 1, 10, 200)
    write_process(tmp_path, 11, 10, 10, 201)
    assert diagnostics.owned_processes(10, 100, tmp_path) == []


def test_absent_session_leader_preserves_owned_reparented_children(
    diagnostics, tmp_path
):
    write_process(tmp_path, 11, 1, 10, 101)
    assert [p["pid"] for p in diagnostics.owned_processes(10, 100, tmp_path)] == [11]


@pytest.mark.parametrize(
    "marker", [None, "malformed", "pid", "start", "session", "reused", "valid"]
)
def test_async_request_requires_matching_live_opt_in_marker(
    diagnostics, tmp_path, monkeypatch, marker
):
    process = {"pid": 10, "start": 100, "session": 10}
    sent = []
    monkeypatch.setattr(diagnostics, "sys", SimpleNamespace(platform="linux"))
    monkeypatch.setattr(diagnostics, "signal", SimpleNamespace(SIGUSR1=10))
    monkeypatch.setattr(diagnostics.os, "kill", lambda *args: sent.append(args))
    monkeypatch.setattr(diagnostics, "same_process", lambda _: marker != "reused")
    if marker is not None:
        contents = dict(process)
        if marker in process:
            contents[marker] += 1
        (tmp_path / "async-ready-10.json").write_text(
            "malformed" if marker == "malformed" else json.dumps(contents)
        )
    diagnostics.request_async_capture(process, tmp_path)
    assert sent == ([(10, 10)] if marker == "valid" else [])


@pytest.mark.parametrize("enabled", [False, True])
def test_snapshot_requests_async_only_when_enabled_before_sampling(
    diagnostics, tmp_path, monkeypatch, enabled
):
    process = {"pid": 10, "start": 100, "session": 10, "python": True}
    calls = []
    monkeypatch.setattr(diagnostics, "owned_processes", lambda *_: [process])
    monkeypatch.setattr(diagnostics, "same_process", lambda _: True)
    monkeypatch.setattr(
        diagnostics, "request_async_capture", lambda *_: calls.append("async")
    )
    monkeypatch.setattr(
        diagnostics, "sample_process", lambda *_: calls.append("sample")
    )
    diagnostics.snapshot(process, "sampler", tmp_path, request_async=enabled)
    assert calls == (["async", "sample"] if enabled else ["sample"])


def test_stack_output_whitelists_frames_without_private_data(diagnostics):
    private = "PRIVATE_SENTINEL"
    raw = [
        {
            "pid": 12,
            "thread_id": 23,
            "os_thread_id": 24,
            "active": False,
            "owns_gil": False,
            "thread_name": private,
            "process_info": {"command_line": private},
            "frames": [
                {
                    "name": "wait",
                    "filename": "/private/path/threading.py",
                    "line": 123,
                    "locals": [{"repr": private}],
                    "extra": private,
                }
            ],
            "environment": private,
        }
    ]
    result = diagnostics.clean_stacks(raw)
    assert result[0]["frames"] == [
        {"function": "wait", "file": "threading.py", "line": 123}
    ]
    assert result[0]["os_thread_id"] == 24
    assert private not in json.dumps(result)
    assert "/private/path" not in json.dumps(result)


@pytest.mark.parametrize("failure", ["exit", "timeout", "missing", "malformed"])
def test_sampler_failures_are_sanitized_and_nonfatal(
    diagnostics, tmp_path, monkeypatch, failure
):
    private = "PRIVATE_SENTINEL"

    def sample(*args, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(private, 1, output=private, stderr=private)
        if failure == "missing":
            raise FileNotFoundError(private)
        return (1 if failure == "exit" else 0), private

    # Attachment is an external OS boundary; exercise the real failure handling.
    monkeypatch.setattr(diagnostics, "capture_sample", sample)
    diagnostics.sample_process({"pid": 10}, "sampler", tmp_path, 0.2)
    text = (tmp_path / "stacks.jsonl").read_text()
    assert private not in text
    assert records(tmp_path, "stacks.jsonl")[0]["status"] != "ok"


def test_unwritable_artifacts_preserve_success(diagnostics, tmp_path):
    blocked = tmp_path / "file"
    blocked.write_text("occupied")
    assert (
        diagnostics.supervise(
            [sys.executable, "-c", "pass"], blocked, timeout=5, checkpoints=()
        )
        == 0
    )


def test_phase_plugin_records_lifecycle_without_payloads(tmp_path):
    suite = tmp_path / "test_sample.py"
    suite.write_text(
        "def test_sample():\n    private = 'PRIVATE_SENTINEL'\n    assert True\n"
    )
    output = tmp_path / "diagnostics"
    env = dict(os.environ, AETHERRA_CI_DIAGNOSTICS=str(output))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "tools.ci_capabilities_phase",
            "-q",
            "-o",
            "addopts=",
            str(suite),
        ],
        env=env,
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    events = records(output, "phases.jsonl")
    phases = {event["phase"] for event in events}
    assert {
        "collection",
        "setup",
        "call",
        "teardown",
        "sessionfinish",
        "unconfigure",
    } <= phases
    assert any(
        (event.get("nodeid") or "").endswith("test_sample.py::test_sample")
        for event in events
    )
    assert "PRIVATE_SENTINEL" not in (output / "phases.jsonl").read_text()


@pytest.mark.skipif(sys.platform != "linux", reason="Linux process ownership contract")
def test_linux_timeout_kills_owned_child_and_preserves_sibling(diagnostics, tmp_path):
    sibling = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    marker = tmp_path / "child.pid"
    code = (
        "import subprocess,sys,time,pathlib; "
        "p=subprocess.Popen([sys.executable,'-c',"
        "'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)']); "
        f"pathlib.Path({str(marker)!r}).write_text(str(p.pid)); time.sleep(30)"
    )
    try:
        assert (
            diagnostics.supervise(
                [sys.executable, "-c", code], tmp_path, timeout=0.5, checkpoints=()
            )
            == 124
        )
        assert sibling.poll() is None
        assert_process_stopped(diagnostics, int(marker.read_text()))
    finally:
        sibling.kill()
        sibling.wait(timeout=5)


@pytest.mark.skipif(sys.platform != "linux", reason="Linux signal exit contract")
def test_linux_signal_exit_is_forwarded(diagnostics, tmp_path):
    assert (
        diagnostics.supervise(
            [
                sys.executable,
                "-c",
                "import os,signal; os.kill(os.getpid(),signal.SIGTERM)",
            ],
            tmp_path,
            timeout=5,
            checkpoints=(),
        )
        == 128 + signal.SIGTERM
    )


@pytest.mark.skipif(sys.platform != "linux", reason="Linux sampler process cleanup")
def test_sampler_timeout_closes_inherited_pipes(diagnostics, tmp_path):
    marker = tmp_path / "sampler-child.pid"
    code = (
        "import subprocess,sys,time,pathlib; "
        "p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(30)']); "
        f"pathlib.Path({str(marker)!r}).write_text(str(p.pid)); time.sleep(30)"
    )
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        diagnostics.capture_sample([sys.executable, "-c", code], 0.5)
    assert time.monotonic() - started < 3
    assert_process_stopped(diagnostics, int(marker.read_text()))


@pytest.mark.skipif(
    sys.platform != "linux" or not os.environ.get("AETHERRA_CI_STACK_SAMPLER"),
    reason="Requires the isolated Linux CI stack sampler",
)
def test_real_sampler_captures_parent_and_child_threads(diagnostics, tmp_path):
    marker = tmp_path / "ready.pid"
    child_code = (
        "import os,pathlib,threading,time\n"
        "private='PRIVATE_SENTINEL'\n"
        "def wait_child():\n    time.sleep(30)\n"
        "threading.Thread(target=wait_child).start()\n"
        f"pathlib.Path({str(marker)!r}).write_text(str(os.getpid()))\n"
        "time.sleep(30)\n"
    )
    parent_code = (
        "import subprocess,sys,time\n"
        f"subprocess.Popen([sys.executable,'-c',{child_code!r}])\n"
        "def wait_parent():\n    time.sleep(30)\n"
        "wait_parent()\n"
    )
    parent = subprocess.Popen(
        [sys.executable, "-c", parent_code], start_new_session=True
    )
    owner = diagnostics.read_process(parent.pid)
    try:
        deadline = time.monotonic() + 5
        while not marker.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        assert marker.exists(), "Synthetic child did not become ready"
        child_pid = int(marker.read_text())
        diagnostics.snapshot(
            owner, os.environ["AETHERRA_CI_STACK_SAMPLER"], tmp_path, budget=8
        )
        stacks = {item["pid"]: item for item in records(tmp_path, "stacks.jsonl")}
        assert stacks[parent.pid]["status"] == "ok"
        assert stacks[child_pid]["status"] == "ok"
        for pid, function in ((parent.pid, "wait_parent"), (child_pid, "wait_child")):
            assert any(
                frame["function"].endswith(function)
                for thread in stacks[pid]["threads"]
                for frame in thread["frames"]
            )
        assert len(stacks[child_pid]["threads"]) >= 2
        assert "PRIVATE_SENTINEL" not in (tmp_path / "stacks.jsonl").read_text()
    finally:
        diagnostics.stop_owned(parent, owner)
