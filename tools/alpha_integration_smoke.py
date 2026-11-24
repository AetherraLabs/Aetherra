"""Disposable source-runtime smoke through the full launcher's CLI main.

Only generation is doubled offline. Startup instrumentation observes the real
launcher; HTTP, policy, Memory, retrieval and shutdown use their implementations.
All prompts are synthetic. Detailed artifacts belong to the requested directory.
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import json
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBSERVATIONS = (
    "/health",
    "/api/hub/readiness",
    "/api/kernel/readiness",
    "/api/ai/status",
)
FACT = "My aunt Leona taught me to mend a flat bike tire."
QUESTION = "Who showed me how to repair a puncture on my bicycle?"
COMPETITORS = [
    "My uncle Mateo taught me how to swim.",
    "My friend Anika repairs cars for a living.",
    "My favorite tea is jasmine.",
]
CHAT_TOKEN = "synthetic-integration-chat"  # noqa: S105 - disposable loopback profile
CONTROL_TOKEN = "synthetic-integration-control"  # noqa: S105 - synthetic


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def child_environment(profile, port, *, live=False):
    """Copy no ambient credentials, endpoints, or Aetherra configuration."""
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.upper().startswith(
            (
                "AETH",
                "LYRIXA",
                "OPENAI",
                "ANTHROPIC",
                "GOOGLE",
                "AZURE",
                "AWS",
                "CLOUDSDK",
                "TEST",
                "PYTHON",
            )
        )
        and not any(
            s in k.upper()
            for s in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL", "PROXY")
        )
    }
    # Keep Git's indexed key/value tuples complete on Windows.
    env.update(
        {k: v for k, v in os.environ.items() if k.upper().startswith("GIT_CONFIG_")}
    )
    policy = profile / "policy"
    env.update(
        {
            "PYTHONPATH": str(ROOT),
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "HOME": str(profile),
            "USERPROFILE": str(profile),
            "TEMP": str(profile / "temp"),
            "TMP": str(profile / "temp"),
            "HF_HOME": os.environ.get(
                "HF_HOME", str(Path.home() / ".cache/huggingface")
            ),
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "TOKENIZERS_PARALLELISM": "false",
            "AETHERRA_SKIP_DOTENV": "1",
            "AETHERRA_PROFILE": "test",
            "AETHERRA_STATE_DIR": str(profile / "state"),
            "AETHERRA_WORKSPACE_ROOT": str(profile),
            "AETHERRA_POLICY_HOME": str(policy),
            "AETHERRA_GUARDIAN_POLICY": str(policy / "guardian.json"),
            "AETHERRA_GUARDIAN_STATE_DIR": str(profile / "guardian"),
            "AETHERRA_GUARDIAN_ENABLED": "1",
            "AETHERRA_GUARDIAN_MODE": "enforcing",
            "AETHERRA_GUARDIAN_REQUIRE_POLICY": "1",
            "AETHERRA_REQUIRE_CAPABILITIES": "1",
            "AETHERRA_NET_STRICT": "1",
            "AETHERRA_SCRIPT_VERIFY_STRICT": "1",
            "AETHERRA_SIGNING_STRICT": "1",
            "AETHERRA_AUDIT": "1",
            "AETHERRA_HOMEOSTASIS_OBSERVE_ONLY": "1",
            "AETHERRA_HOMEOSTASIS_MODE": "observe_only",
            "AETHERRA_SELFINC_ENABLED": "0",
            "AETHERRA_HMR_ENABLED": "0",
            "AETHERRA_SELF_IMPROVEMENT_AUTO_IMPLEMENT": "0",
            "AETHERRA_LYRIXA_FORCE_OFFLINE": "1",
            "AETHERRA_NO_FAKE_DATA": "1",
            "AETHERRA_REGISTRY_URL": "",
            "AETHERRA_HUB_ENABLED": "1",
            "AETHERRA_HUB_URL": f"http://127.0.0.1:{port}",
            "AETHERRA_HUB_PORT": str(port),
            "AETHERRA_HUB_PORT_AUTOFIX": "0",
            "AETHERRA_AI_API_ENABLED": "1",
            "AETHERRA_AI_API_REQUIRE_TOKEN": "1",
            "AETHERRA_AI_API_TOKEN": CHAT_TOKEN,
            "AETHERRA_HUB_CONTROL_TOKEN": CONTROL_TOKEN,
            "AETHERRA_SKIP_LAUNCHER_AI_DEFAULTS": "1",
            "NO_PROXY": "*",
        }
    )
    if live:
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "Live smoke unverified: explicitly configure OPENAI_API_KEY"
            )
        env["OPENAI_API_KEY"] = os.environ["OPENAI_API_KEY"]
        env["AETHERRA_LLM_MODEL"] = "gpt-4o"
    return env


def prepare_profile(profile, *, live=False):
    profile.mkdir(parents=True)
    (profile / "temp").mkdir()
    policy = profile / "policy"
    policy.mkdir()
    rules = [
        {
            "requester": "service_registry",
            "subsystem": "service_registry",
            "action": "service_registry.*",
            "target": "service_registry:service",
        },
        {
            "requester": "hub:chat",
            "subsystem": "chat",
            "action": "chat.ingress",
            "target": "chat_route:/api/ai/ask",
        },
        {
            "requester": "kernel_loop",
            "subsystem": "kernel",
            "action": "kernel.shutdown",
            "target": "kernel:loop",
        },
    ]
    grants = {
        "service_registry": [
            f"registry:{op}"
            for op in (
                "register",
                "unregister",
                "status",
                "heartbeat",
                "message",
                "broadcast",
                "subscribe",
            )
        ],
        "kernel_loop": ["kernel:control"],
    }
    if live:
        rules.append(
            {
                "requester": "core:llm",
                "subsystem": "network",
                "action": "network.request",
                "target": "network:api.openai.com",
                "capabilities": ["network:outbound"],
            }
        )
        grants["core:llm"] = ["network:outbound"]
    write_json(
        policy / "guardian.json", {"version": 1, "default": "deny", "allow": rules}
    )
    write_json(policy / "capabilities.json", {"allow": grants})
    write_json(
        policy / "net_policy.json",
        {
            "allow_domains": [
                "127.0.0.1",
                "localhost",
                *(["api.openai.com"] if live else []),
            ],
            "deny_domains": [],
        },
    )
    write_json(
        profile / "launcher.json",
        {
            "hub_enabled": True,
            "gui_enabled": False,
            "presence_enabled": False,
            "hmr_enabled": False,
            "engine_text_statistics_enabled": False,
        },
    )


def worker(profile, label, *, live=False):
    """Call the actual CLI parser/main; observation never replaces lifecycle work."""
    # Standard library imports
    import _thread
    from unittest.mock import patch

    # Aetherra imports
    from tests.acceptance.continuity_runtime import ContextResponder

    if not live:

        def offline(event, args):
            if event in {"socket.connect", "socket.bind"}:
                address = args[1]
                if not isinstance(address, tuple) or address[0] not in {
                    "127.0.0.1",
                    "::1",
                    "localhost",
                }:
                    raise PermissionError("integration_smoke_external_network_denied")
            if event == "socket.getaddrinfo" and args[0] not in {
                "127.0.0.1",
                "::1",
                "localhost",
                b"localhost",
            }:
                raise PermissionError("integration_smoke_external_dns_denied")
            if event == "subprocess.Popen":
                raise PermissionError("integration_smoke_subprocess_denied")

        sys.addaudithook(offline)
    responder = ContextResponder()
    if live:
        # Aetherra imports
        from Aetherra.core.multi_llm_manager import MultiLLMManager

        generate = MultiLLMManager.generate_response

        async def observed_generate(manager, prompt, **kwargs):
            responder.prompts.append(prompt)
            return await generate(manager, prompt, **kwargs)

        generation = patch.object(
            MultiLLMManager, "generate_response", observed_generate
        )
    else:
        generation = patch(
            "Aetherra.core.multi_llm_manager.get_llm_manager", return_value=responder
        )
    with generation:
        # Aetherra imports
        import aetherra_os_launcher as launcher_module

        original = launcher_module.AetherraOSLauncher._main_operation_loop

        async def observed_loop(launcher):
            engine = launcher.systems["aetherra"].impl
            write_json(
                profile / f"{label}-boot.json",
                {
                    "pid": os.getpid(),
                    "readiness": launcher.readiness_report,
                    "session_id": engine.session_id,
                    "initial_context": engine._public_conversation_context(),
                },
            )
            return await original(launcher)

        finished = threading.Event()

        def stop_watcher():
            while not finished.wait(0.1):
                if (profile / f"{label}-stop").exists():
                    _thread.interrupt_main()
                    return

        threading.Thread(target=stop_watcher, daemon=True).start()
        sys.argv = [
            str(ROOT / "aetherra_os_launcher.py"),
            "--mode",
            "full",
            "--no-gui",
            "--config",
            str(profile / "launcher.json"),
        ]
        exit_code = 1
        try:
            with patch.object(
                launcher_module.AetherraOSLauncher,
                "_main_operation_loop",
                observed_loop,
            ):
                try:
                    exit_code = asyncio.run(launcher_module.main())
                except KeyboardInterrupt:
                    exit_code = 0
        finally:
            finished.set()
            write_json(
                profile / f"{label}-provider.json",
                {
                    "pid": os.getpid(),
                    "exit_code": exit_code,
                    "prompts": responder.prompts,
                },
            )
        return exit_code


def request_json(base, path, *, message=None, token=CONTROL_TOKEN, timeout=5):
    target = urllib.parse.urlsplit(base)
    if (
        target.scheme != "http"
        or target.hostname != "127.0.0.1"
        or not path.startswith("/")
    ):
        raise ValueError(
            "Integration smoke only connects to its loopback HTTP listener"
        )
    data = (
        None
        if message is None
        else json.dumps({"message": message, "scratchpad_policy": "ephemeral"}).encode()
    )
    req = urllib.request.Request(  # noqa: S310 - loopback HTTP checked above
        base + path,
        data=data,
        headers={"X-Aetherra-Token": token, "Content-Type": "application/json"},
    )
    start = time.monotonic()
    while True:
        try:
            with urllib.request.urlopen(req, timeout=timeout) as reply:  # noqa: S310
                if reply.headers.get_content_type() != "application/json":
                    raise RuntimeError(f"Expected JSON: {path}")
                return {
                    "status": reply.status,
                    "seconds": round(time.monotonic() - start, 3),
                    "body": json.load(reply),
                }
        except urllib.error.HTTPError as error:
            # Non-allowlisted observations can briefly overlap response cleanup.
            # Retry only safe GETs explicitly rejected by admission, never chat.
            body = error.read()
            if (
                message is not None
                or error.code != 503
                or time.monotonic() - start >= timeout
            ):
                raise
            if json.loads(body).get("error", {}).get("code") != "hub_busy":
                raise
            time.sleep(0.05)


def validate_status(snapshot):
    for path in OBSERVATIONS:
        if snapshot[path]["status"] != 200:
            raise AssertionError(f"Observation failed: {path}")
    for path in OBSERVATIONS[1:]:
        if snapshot[path]["body"]["readiness"]["readiness"] != "ready":
            raise AssertionError(f"Not ready: {path}")
    guardian = snapshot["/api/guardian/status"]["body"]["guardian"]
    assert guardian["enabled"]
    assert guardian["mode"] == "enforcing"
    assert guardian["audit"]["integrity_ok"] is True
    selfinc = snapshot["/api/selfinc/status"]["body"]
    assert selfinc["status"] == "disabled"
    assert selfinc["config_enabled"] is False
    assert selfinc["running"] is False
    improvement = snapshot["/api/selfimprove/status"]["body"]
    assert improvement["autonomous_implementation_enabled"] is False
    homeostasis = snapshot["/api/homeostasis/status"]["body"]
    assert homeostasis["orchestrator"]["initialized"] is True
    assert homeostasis["orchestrator"]["running"] is True
    assert homeostasis["orchestrator"]["observe_only_requested"] is True
    assert homeostasis["controller"]["mode"] == "observe_only"
    for name in ("actions_attempted", "actions_executed", "actions_blocked"):
        assert homeostasis["actuators"][name] == 0
    assert homeostasis["orchestrator"]["restart_count"] == 0
    assert homeostasis["orchestrator"]["error_recovery_count"] == 0


def validate_turn(result, *, live=False):
    assert result["llm"]["used"] is True
    assert result["llm"]["fallback"] is False
    assert result["llm"]["diag"]["event"] == "ok"
    assert result["recall"]["event"] == "ok"
    if live:
        assert result["llm"]["model"]["provider"] == "openai"
        assert result["llm"]["model"]["model_name"] == "gpt-4o"


def run_session(profile, messages, label, *, live=False):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    env = child_environment(profile, port, live=live)
    command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--worker",
        str(profile),
        "--label",
        label,
        *(["--live"] if live else []),
    ]
    record = {"turns": [], "observations_during_chat": [], "forced_stop": False}
    with (profile / f"{label}-runtime.log").open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(command, cwd=profile, env=env, stdout=log, stderr=log)
        record["pid"] = proc.pid
        try:
            deadline = time.monotonic() + 180
            boot_path = profile / f"{label}-boot.json"
            while not boot_path.exists():
                if proc.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError(
                        f"Launcher did not finish boot; inspect {label}-runtime.log"
                    )
                time.sleep(0.1)
            record["boot"] = json.loads(boot_path.read_text(encoding="utf-8"))
            assert record["boot"]["readiness"]["status"] == "ready"
            assert record["boot"]["session_id"] is None
            assert record["boot"]["initial_context"] == {}
            paths = (
                *OBSERVATIONS,
                "/api/guardian/status",
                "/api/selfinc/status",
                "/api/homeostasis/status",
                "/api/selfimprove/status",
            )
            record["snapshot"] = {path: request_json(base, path) for path in paths}
            validate_status(record["snapshot"])
            with ThreadPoolExecutor(max_workers=1) as pool:
                for message in messages:
                    future = pool.submit(
                        request_json,
                        base,
                        "/api/ai/ask",
                        message=message,
                        token=CHAT_TOKEN,
                        timeout=120,
                    )
                    while not future.done():
                        for path in OBSERVATIONS:
                            observation = request_json(base, path)
                            record["observations_during_chat"].append(
                                {"path": path, **observation}
                            )
                        time.sleep(0.1)
                    turn = future.result()
                    turn["message"] = message
                    record["turns"].append(turn)
                    result = turn["body"]["result"]
                    assert turn["body"]["ok"]
                    validate_turn(result, live=live)
            record["final_snapshot"] = {
                path: request_json(base, path) for path in paths
            }
            validate_status(record["final_snapshot"])
        finally:
            (profile / f"{label}-stop").touch()
            try:
                proc.wait(timeout=65)
            except subprocess.TimeoutExpired:
                # Only our own child; a forced stop is a failed gate, never a pass.
                record["forced_stop"] = True
                proc.kill()
                proc.wait(timeout=10)
            record["process_exit"] = proc.returncode
            provider_path = profile / f"{label}-provider.json"
            record["provider"] = (
                json.loads(provider_path.read_text(encoding="utf-8"))
                if provider_path.exists()
                else None
            )
            write_json(profile / f"{label}-result.json", record)
    assert record["process_exit"] == 0
    assert not record["forced_stop"]
    assert record["provider"]["exit_code"] == 0
    assert "Graceful shutdown complete" in (profile / f"{label}-runtime.log").read_text(
        encoding="utf-8"
    )
    for message in messages:
        assert message not in (profile / f"{label}-runtime.log").read_text(
            encoding="utf-8"
        )
    return record


def evidence_trace(profile, written, recalled):
    saved_id = written["turns"][0]["body"]["result"]["memory_id"]
    result = recalled["turns"][0]["body"]["result"]
    prompts = [p for p in recalled["provider"]["prompts"] if f"User: {QUESTION}\n" in p]
    assert len(prompts) == 1
    supplied = [
        json.loads(line[2:])
        for line in prompts[0].splitlines()
        if line.startswith("- ")
    ]
    ids = [ev["id"] for ev in supplied]
    assert ids == result["recall"]["record_ids"] == result["llm"]["evidence_ids"]
    assert ids == [ev["id"] for ev in result["evidence"]]
    assert ids[0] == saved_id
    assert len(ids) <= 3
    assert written["pid"] != recalled["pid"]
    with sqlite3.connect(profile / "lyrixa_memory.db") as db:
        for ev in supplied:
            stored = json.loads(
                db.execute(
                    "SELECT content FROM memories WHERE id=?", (ev["id"],)
                ).fetchone()[0]
            )
            assert json.loads(ev["content"]) == stored
            if ev["id"] == saved_id:
                assert stored["content"] == FACT
                assert stored["role"] == "user"
    assert FACT in prompts[0]
    assert "Leona" in result["response"]
    assert all(fact not in prompts[0] for fact in COMPETITORS)
    assert result["llm"]["fallback"] is False
    return {
        "record_id": saved_id,
        "write_pid": written["pid"],
        "recall_pid": recalled["pid"],
        "retrieved_ids": ids,
        "provider_evidence_ids": result["llm"]["evidence_ids"],
        "llm": result["llm"],
        "response": result["response"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="New disposable artifact directory; must not exist"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Use intentionally supplied OPENAI_API_KEY with gpt-4o",
    )
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--label", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.worker, args.label, live=args.live)
    if args.output is None:
        parser.error("--output is required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    primary, separate = output / "primary", output / "separate"
    for profile in (primary, separate):
        prepare_profile(profile, live=args.live)
    written = run_session(primary, [FACT, *COMPETITORS], "write", live=args.live)
    recalled = run_session(
        primary, [QUESTION, "What color is my bicycle?"], "recall", live=args.live
    )
    trace = evidence_trace(primary, written, recalled)
    unknown = recalled["turns"][1]["body"]["result"]["response"]
    assert any(
        word in unknown.lower()
        for word in ("don't know", "haven't", "not told", "didn't", "do not know")
    )
    empty = run_session(separate, [QUESTION], "empty", live=args.live)
    negative = empty["turns"][0]["body"]["result"]
    assert negative["evidence"] == []
    assert negative["recall"]["record_ids"] == []
    assert trace["record_id"] not in json.dumps(empty)
    assert "Leona" not in json.dumps(empty)
    summary = {
        "passed": True,
        "entry": "aetherra_os_launcher.py --mode full --no-gui --config PROFILE/launcher.json",
        "responder": "gpt-4o" if args.live else "deterministic-context-responder",
        "trace": trace,
        "unknown_response": unknown,
        "separate_response": negative["response"],
        "process_exits": [r["process_exit"] for r in (written, recalled, empty)],
        "stop_mechanism": "test-harness SIGINT; not interactive ConPTY keyboard evidence",
        "browser": "not exercised: headless entry",
        "max_observation_seconds": max(
            o["seconds"]
            for r in (written, recalled, empty)
            for o in r["observations_during_chat"]
        ),
    }
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
