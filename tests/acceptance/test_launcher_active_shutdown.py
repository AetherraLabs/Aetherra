"""A normal CLI interrupt must finish owned chat work before process teardown."""

from __future__ import annotations

# Standard library imports
import asyncio
import http.client
import json
import socket
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

# Third party imports
import pytest

# Aetherra imports
from tools.alpha_integration_smoke import (
    CHAT_TOKEN,
    child_environment,
    prepare_profile,
    worker,
    write_json,
)

MESSAGE = "What instrument do I play at the synthetic concert?"


def _child(profile):
    # Standard library imports
    import _thread

    # Aetherra imports
    import aetherra_os_launcher as launcher_module
    from aetherra_hub import compat
    from tests.acceptance.continuity_runtime import ContextResponder

    original_generate = ContextResponder.generate_response
    original_stop = compat.AetherraHubServer.stop_server
    original_loop = launcher_module.AetherraOSLauncher._main_operation_loop
    original_interrupt = _thread.interrupt_main
    running_loop = None

    async def observed_loop(launcher):
        nonlocal running_loop
        running_loop = asyncio.get_running_loop()
        return await original_loop(launcher)

    def interrupt_main():
        original_interrupt()
        # interrupt_main sets a pending SIGINT; unlike a real console Ctrl+C,
        # it need not wake Windows' IO poll. Wake it without replacing the
        # signal, main cancellation, or launcher's operation/shutdown methods.
        if running_loop is not None:
            running_loop.call_soon_threadsafe(lambda: None)

    async def paused_generate(self, prompt):
        if MESSAGE in prompt:
            write_json(profile / "generation-entered.json", {"entered": True})
            # Cooperative async waiting avoids an executor/non-daemon thread
            # accidentally keeping the process alive and hiding daemon-worker loss.
            deadline = time.monotonic() + 90
            while not (profile / "release-generation").exists():
                if time.monotonic() >= deadline:
                    raise RuntimeError("test_generation_not_released")
                await asyncio.sleep(0.02)
        return await original_generate(self, prompt)

    def observed_stop(server):
        try:
            return original_stop(server)
        except RuntimeError as error:
            if "Hub request drain timeout" in str(error):
                write_json(
                    profile / "drain-timeout.json",
                    {"active": server._ownership.active, "draining": True},
                )
            raise

    # Keep the real normal CLI, real Hub/Engine/Memory, and signal path. Only
    # generation is doubled; the shorter stop budget makes the edge deterministic.
    with (
        patch.object(ContextResponder, "generate_response", paused_generate),
        patch.object(compat, "REQUEST_DRAIN_TIMEOUT_SECONDS", 0.15),
        patch.object(compat.AetherraHubServer, "stop_server", observed_stop),
        patch.object(
            launcher_module.AetherraOSLauncher, "_main_operation_loop", observed_loop
        ),
        patch.object(_thread, "interrupt_main", interrupt_main),
    ):
        return worker(profile, "active")


def _wait_file(process, path, timeout=90):
    deadline = time.monotonic() + timeout
    while not path.exists():
        assert process.poll() is None, f"Child exited before {path.name}"
        assert time.monotonic() < deadline, f"Timed out waiting for {path.name}"
        time.sleep(0.03)
    return json.loads(path.read_text(encoding="utf-8"))


def _chat(port, path):
    connection = http.client.HTTPConnection("127.0.0.1", port, timeout=30)
    try:
        connection.request(
            "POST",
            path,
            json.dumps({"message": MESSAGE}),
            headers={
                "Content-Type": "application/json",
                "X-Aetherra-Token": CHAT_TOKEN,
                "X-Aetherra-Principal": "hub:chat",
            },
        )
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        return response.status, body
    finally:
        connection.close()


@pytest.mark.parametrize("path", ["/api/ai/ask", "/api/ai/stream"])
def test_normal_cli_sigint_keeps_memory_owned_after_drain_timeout(tmp_path, path):
    profile = tmp_path / "profile"
    prepare_profile(profile)
    guardian_path = profile / "policy" / "guardian.json"
    guardian = json.loads(guardian_path.read_text(encoding="utf-8"))
    guardian["allow"].append(
        {
            "requester": "hub:chat",
            "subsystem": "chat",
            "action": "chat.ingress",
            "target": "chat_route:/api/ai/stream",
        }
    )
    write_json(guardian_path, guardian)
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    env = child_environment(profile, port)
    env["AETHERRA_AI_API_STREAM"] = "1"
    env["AETHERRA_STREAM_SOFT_TIMEOUT_S"] = "1"
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", str(profile)]
    with (profile / "runtime.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command, cwd=profile, env=env, stdout=log, stderr=log
        )
        with ThreadPoolExecutor(max_workers=1) as client:
            try:
                boot = _wait_file(process, profile / "active-boot.json")
                assert boot["readiness"]["status"] == "ready"
                future = client.submit(_chat, port, path)
                _wait_file(process, profile / "generation-entered.json", timeout=10)
                if path.endswith("stream"):
                    status, body = future.result(timeout=5)
                    assert status == 200
                    assert "soft_timeout" in body
                # The smoke worker delivers a real SIGINT through interrupt_main;
                # the launcher follows its normal cancellation/finally path.
                (profile / "active-stop").touch()
                timeout = _wait_file(
                    process, profile / "drain-timeout.json", timeout=10
                )
                assert timeout["active"] > 0
                time.sleep(0.3)
                assert process.poll() is None
                assert not (profile / "active-provider.json").exists(), (
                    "CLI main returned before its retained "  # Memory is still owned.
                    "Engine worker completed"
                )
                assert "Graceful shutdown complete" not in (
                    profile / "runtime.log"
                ).read_text(encoding="utf-8")
                (profile / "release-generation").touch()
                status, body = future.result(timeout=15)
                assert status == 200
                if path.endswith("ask"):
                    result = json.loads(body)["result"]
                    assert result["memory_id"]
                    assert result["llm"]["fallback"] is False
                    assert (
                        result["persistence"]["assistant_memory"]["status"] == "stored"
                    )
                assert process.wait(timeout=30) == 1  # initial stop budget was missed
                provider = _wait_file(
                    process, profile / "active-provider.json", timeout=1
                )
                assert provider["exit_code"] == 1
                assert any(MESSAGE in prompt for prompt in provider["prompts"])
                runtime_log = (profile / "runtime.log").read_text(encoding="utf-8")
                assert "Graceful shutdown complete" in runtime_log
                with sqlite3.connect(profile / "lyrixa_memory.db") as db:
                    rows = [
                        json.loads(row[0])
                        for row in db.execute("SELECT content FROM memories")
                    ]
                assert any(
                    row.get("role") == "user" and row.get("content") == MESSAGE
                    for row in rows
                )
                assert any(row.get("role") == "assistant" for row in rows)
            finally:
                (profile / "release-generation").touch()
                (profile / "active-stop").touch()
                if process.poll() is None:
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()  # only this disposable test child on failure
                        process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(_child(Path(sys.argv[2])))
