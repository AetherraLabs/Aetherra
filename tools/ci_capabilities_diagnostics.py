"""Opt-in, bounded Linux capability-test diagnostics; never log process payloads."""

from __future__ import annotations

# Standard library imports
import argparse
import contextlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

PROC = Path("/proc")


def emit(output, name, record):
    try:
        output.mkdir(parents=True, exist_ok=True)
        with (output / name).open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=True) + "\n")
    except (OSError, ValueError):
        pass  # Evidence collection must not replace the test result.


def read_process(pid, proc_root=PROC):
    try:
        folder = proc_root / str(pid)
        fields = (folder / "stat").read_text().rsplit(")", 1)[1].split()
        try:
            python = Path(os.readlink(folder / "exe")).name.startswith("python")
        except OSError:
            python = False
        return {
            "pid": int(pid),
            "ppid": int(fields[1]),
            "session": int(fields[3]),
            "start": int(fields[19]),
            "state": fields[0],
            "threads": int(fields[17]),
            "python": python,
        }
    except (OSError, ValueError, IndexError):
        return None


def owned_processes(session, started, proc_root=PROC):
    try:
        leader = read_process(session, proc_root)
        if leader and leader["start"] != started:
            return []
        processes = (
            read_process(p.name, proc_root)
            for p in proc_root.iterdir()
            if p.name.isdigit()
        )
        return sorted(
            (
                p
                for p in processes
                if p and p["session"] == session and p["start"] >= started
            ),
            key=lambda p: p["pid"],
        )
    except OSError:
        return []


def same_process(process, proc_root=PROC):
    current = read_process(process["pid"], proc_root)
    return bool(
        current and all(current[key] == process[key] for key in ("start", "session"))
    )


def clean_stacks(raw):
    result = []
    for thread in raw[:128]:
        frames = []
        for frame in thread.get("frames", [])[:128]:
            filename = str(frame.get("filename", "")).replace("\\", "/")
            root = str(Path.cwd()).replace("\\", "/").rstrip("/") + "/"
            filename = (
                filename[len(root) :]
                if filename.startswith(root)
                else filename.rsplit("/", 1)[-1]
            )
            frames.append(
                {
                    "function": frame.get("name", ""),
                    "file": filename,
                    "line": int(frame.get("line", 0)),
                }
            )
        result.append(
            {
                key: thread.get(key)
                for key in ("pid", "thread_id", "os_thread_id", "active", "owns_gil")
            }
            | {"frames": frames}
        )
    return result


def capture_sample(command, timeout):
    child = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        start_new_session=os.name == "posix",
    )
    try:
        stdout, _ = child.communicate(timeout=timeout)
        return child.returncode, stdout
    except subprocess.TimeoutExpired:
        with contextlib.suppress(OSError):
            os.killpg(child.pid, signal.SIGKILL) if os.name == "posix" else child.kill()
        with contextlib.suppress(subprocess.TimeoutExpired):
            child.wait(timeout=0.5)
        raise
    finally:
        child.stdout.close()


def sample_process(process, sampler, output, timeout):
    record = {"pid": process["pid"], "status": "unavailable"}
    try:
        command = [
            str(sampler),
            "dump",
            "--json",
            "--nonblocking",
            "--pid",
            str(process["pid"]),
        ]
        if sys.platform == "linux" and os.geteuid() != 0:
            command = [
                "sudo",
                "-n",
                "timeout",
                "--signal=KILL",
                f"{timeout}s",
                *command,
            ]
        code, stdout = capture_sample(command, timeout + 0.5)
        if code == 0:
            record.update(status="ok", threads=clean_stacks(json.loads(stdout)))
        else:
            record["status"] = "sampler_failed"
    except (
        OSError,
        subprocess.TimeoutExpired,
        ValueError,
        TypeError,
        AttributeError,
    ) as exc:
        record["status"] = type(exc).__name__
    emit(output, "stacks.jsonl", record)


def request_async_capture(process, output):
    if sys.platform != "linux":
        return
    try:
        marker = json.loads(
            (output / f"async-ready-{process['pid']}.json").read_text(encoding="utf-8")
        )
        if not isinstance(marker, dict) or any(
            marker.get(key) != process[key] for key in ("pid", "start", "session")
        ):
            return
        if same_process(process):
            os.kill(process["pid"], signal.SIGUSR1)
            emit(output, "async-requests.jsonl", {"pid": process["pid"], "sent": True})
    except (OSError, ValueError):
        pass  # An unavailable diagnostic must not affect the supervised command.


def snapshot(owner, sampler, output, budget=10, *, request_async=False):
    deadline = time.monotonic() + budget
    processes = owned_processes(owner["pid"], owner["start"])
    emit(
        output,
        "processes.jsonl",
        {"elapsed_at": time.monotonic(), "processes": processes},
    )
    for process in processes:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        if process["python"] and same_process(process):
            if request_async:
                request_async_capture(process, output)
            if sampler:
                sample_process(process, sampler, output, min(2, remaining))


def stop_owned(child, owner):
    def terminate(sig):
        if owner is None:
            if child.poll() is None:
                child.terminate() if sig == signal.SIGTERM else child.kill()
            return
        for process in reversed(owned_processes(owner["pid"], owner["start"])):
            if process["state"] != "Z" and same_process(process):
                with contextlib.suppress(OSError):
                    os.kill(process["pid"], sig)

    terminate(signal.SIGTERM)
    until = time.monotonic() + 2
    while time.monotonic() < until:
        child.poll()
        live = owned_processes(owner["pid"], owner["start"]) if owner else []
        if child.poll() is not None and not any(p["state"] != "Z" for p in live):
            break
        time.sleep(0.05)
    terminate(getattr(signal, "SIGKILL", signal.SIGTERM))
    with contextlib.suppress(subprocess.TimeoutExpired):
        child.wait(timeout=2)


def supervise(
    command, output, sampler=None, timeout=290, checkpoints=(30, 90, 180, 260)
):
    output = Path(output)
    environment = dict(os.environ, AETHERRA_CI_DIAGNOSTICS=str(output.resolve()))
    started = time.monotonic()
    child = subprocess.Popen(
        command, env=environment, start_new_session=os.name == "posix"
    )
    owner = read_process(child.pid) if sys.platform == "linux" else None
    emit(output, "supervisor.jsonl", {"event": "start", "pid": child.pid})
    pending = iter(checkpoints)
    next_capture = next(pending, float("inf"))
    timed_out = False
    result = 130
    try:
        while child.poll() is None:
            elapsed = time.monotonic() - started
            if elapsed >= timeout:
                timed_out = True
                emit(
                    output,
                    "supervisor.jsonl",
                    {"event": "watchdog", "seconds": timeout},
                )
                break
            if elapsed >= next_capture:
                if owner:
                    snapshot(
                        owner,
                        sampler,
                        output,
                        min(10, timeout - elapsed),
                        request_async=elapsed >= 90,
                    )
                next_capture = next(pending, float("inf"))
            time.sleep(min(0.05, max(0, timeout - (time.monotonic() - started))))
        if not timed_out:
            code = child.returncode
            result = code if code >= 0 else 128 - code
    except KeyboardInterrupt:
        result = 130
    finally:
        live = (
            [
                process
                for process in owned_processes(owner["pid"], owner["start"])
                if process["state"] != "Z"
            ]
            if owner
            else []
        )
        emit(
            output,
            "supervisor.jsonl",
            {
                "event": "before_cleanup",
                "child_returncode": child.poll(),
                "live_processes": live,
            },
        )
        stop_owned(child, owner)
        result = 124 if timed_out else result
        emit(
            output,
            "supervisor.jsonl",
            {"event": "exit", "code": result, "reaped": child.poll() is not None},
        )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sampler", type=Path)
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    pytest_args = (
        args.pytest_args[1:] if args.pytest_args[:1] == ["--"] else args.pytest_args
    )
    return supervise(
        [
            sys.executable,
            "-m",
            "pytest",
            "-p",
            "tools.ci_capabilities_phase",
            *pytest_args,
        ],
        args.output,
        args.sampler,
    )


if __name__ == "__main__":
    raise SystemExit(main())
