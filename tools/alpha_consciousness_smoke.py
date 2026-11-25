"""Bounded offline Phase C1 evidence through the real full launcher CLI.

Only text generation is doubled. A wrapper around the startup announcement
observes the owned launcher and accepts local file commands to stop its observer
and start an empty conversation. HTTP chat, retrieval, policy, core ticks and
shutdown retain their real implementations. All conversation data is synthetic.
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

# Third party imports
from alpha_integration_smoke import (
    CHAT_TOKEN,
    COMPETITORS,
    CONTROL_TOKEN,
    FACT,
    OBSERVATIONS,
    QUESTION,
    ROOT,
    child_environment,
    prepare_profile,
    request_json,
    validate_status,
    validate_turn,
    write_json,
)

THINK = "/api/consciousness/state"
UI = "/api/runtime-ui/subsystems/consciousness"
UNKNOWN = "What color is my bicycle?"
STRICT = (
    "AETHERRA_GUARDIAN_ENABLED",
    "AETHERRA_GUARDIAN_REQUIRE_POLICY",
    "AETHERRA_REQUIRE_CAPABILITIES",
    "AETHERRA_NET_STRICT",
    "AETHERRA_SCRIPT_VERIFY_STRICT",
    "AETHERRA_SIGNING_STRICT",
    "AETHERRA_AUDIT",
)
SOURCES = (
    "aetherra_os_launcher.py",
    "aetherra_service_registry.py",
    "Aetherra/consciousness/runtime_observer.py",
    "Aetherra/consciousness/core/consciousness_core.py",
    "Aetherra/consciousness/core/think_stream.py",
    "Aetherra/consciousness/continuity_memory.py",
    "Aetherra/consciousness/checkpoint.py",
    "Aetherra/consciousness/self_trust.py",
    "Aetherra/aetherra_core/memory/lifecycle_checkpoint.py",
    "Aetherra/aetherra_core/memory/memory_core.py",
    "Aetherra/aetherra_core/memory/aetherra_memory_engine.py",
    "Aetherra/runtime_ui/snapshot.py",
    "aetherra_hub/blueprints/consciousness.py",
    "tools/alpha_consciousness_smoke.py",
    "tools/alpha_consciousness_continuity_smoke.py",
    "tools/alpha_integration_smoke.py",
    "tests/acceptance/continuity_runtime.py",
)


def hashes():
    return {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES
    }


def prepare_observer_profile(profile, *, allowed):
    prepare_profile(profile)
    config_path = profile / "launcher.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config.update(
        consciousness_enabled=True,
        consciousness_mode="observe",
        consciousness_tick_hz=1,
    )
    write_json(config_path, config)
    if allowed:
        path = profile / "policy" / "guardian.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        for kind in ("micro", "macro"):
            policy["allow"].append(
                {
                    "requester": "consciousness:core",
                    "subsystem": "consciousness",
                    "action": f"consciousness.{kind}_reflection_update",
                    "target": f"reflection:{kind}",
                }
            )
        write_json(path, policy)


def side_effect_snapshot(profile):
    """Read counts/opaque identifiers only, without initializing any subsystem."""
    records = []
    database = profile / "lyrixa_memory.db"
    if database.exists():
        with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as db:
            records = [
                row[0] for row in db.execute("SELECT id FROM memories ORDER BY id")
            ]
    graph = sys.modules.get("Aetherra.aetherra_core.memory.qfac.api")
    simple = sys.modules.get("Aetherra.aetherra_core.memory.qfac.qfac_api")
    return {
        "memory_ids": records,
        "qfac_graph_records": len(getattr(graph, "_RECORDS", {})),
        "qfac_simple_records": len(
            getattr(getattr(simple, "_store", None), "_by_id", {})
        ),
        "experimental_modules": sorted(
            name
            for name in sys.modules
            if name.startswith(
                (
                    "Aetherra.consciousness.quantum",
                    "Aetherra.consciousness.cosmic",
                    "Aetherra.consciousness.transcendence",
                )
            )
            or "temporal_consciousness_engine" in name.lower()
        ),
        "continuity_files": [
            str(path.relative_to(profile)) for path in profile.rglob("continuity.json")
        ],
    }


def worker(profile):
    # Standard library imports
    import _thread
    from unittest.mock import patch

    # Aetherra imports
    from tests.acceptance.continuity_runtime import ContextResponder

    continuity_attempts = []

    def audit(event, args):
        if (
            event == "open"
            and isinstance(args[0], (str, bytes, os.PathLike))
            and Path(os.fsdecode(args[0])).name.lower() == "continuity.json"
        ):
            continuity_attempts.append("continuity_json_access")
            raise PermissionError("observer_smoke_continuity_access_denied")
        if event in {"socket.connect", "socket.bind"}:
            address = args[1]
            if not isinstance(address, tuple) or address[0] not in {
                "127.0.0.1",
                "::1",
                "localhost",
            }:
                raise PermissionError("observer_smoke_external_network_denied")
        if event == "socket.getaddrinfo" and args[0] not in {
            "127.0.0.1",
            "::1",
            "localhost",
            b"localhost",
        }:
            raise PermissionError("observer_smoke_external_dns_denied")
        if event == "subprocess.Popen":
            raise PermissionError("observer_smoke_subprocess_denied")

    sys.addaudithook(audit)
    responder = ContextResponder()
    finished = threading.Event()
    command_task = None
    launcher_seen = None

    def stop_watcher():
        while not finished.wait(0.1):
            if (profile / "stop-runtime").exists():
                _thread.interrupt_main()
                return

    async def commands(launcher):
        # The ordinary startup announcement queues one real Engine thought.
        # Let that existing work finish before measuring observer-only effects.
        first_cycle = launcher.kernel_loop.get_status()["cycle_count"]
        deadline = time.monotonic() + 120
        while True:
            kernel = launcher.kernel_loop.get_status()
            if (
                kernel["cycle_count"] > first_cycle
                and kernel["queue_sizes"]["high_priority"] == 0
                and kernel["inflight"].get("engine", 0) == 0
            ):
                write_json(
                    profile / "settled.json",
                    {
                        "kernel_cycle_count": kernel["cycle_count"],
                        "high_priority_queue": kernel["queue_sizes"]["high_priority"],
                        "engine_inflight": kernel["inflight"].get("engine", 0),
                        "side_effects": side_effect_snapshot(profile),
                    },
                )
                break
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep(0.05)
        while True:
            if (profile / "capture-side-effects").exists() and not (
                profile / "side-effects.json"
            ).exists():
                write_json(profile / "side-effects.json", side_effect_snapshot(profile))
            if (profile / "stop-observer").exists() and not (
                profile / "observer-stopped.json"
            ).exists():
                await launcher._stop_consciousness_observer()
                engine = launcher.systems["aetherra"].impl
                await engine.start_conversation()
                write_json(
                    profile / "observer-stopped.json",
                    {
                        "observer": launcher.systems[
                            "consciousness_core"
                        ].get_runtime_status(),
                        "new_context": engine._public_conversation_context(),
                    },
                )
            await asyncio.sleep(0.05)

    with patch(
        "Aetherra.core.multi_llm_manager.get_llm_manager", return_value=responder
    ):
        # Aetherra imports
        import aetherra_os_launcher as launcher_module

        original = launcher_module.AetherraOSLauncher._announce_os_online

        async def observed_announcement(launcher):
            nonlocal command_task, launcher_seen
            result = await original(launcher)
            launcher_seen = launcher
            engine = launcher.systems["aetherra"].impl
            command_task = asyncio.create_task(commands(launcher))
            write_json(
                profile / "boot.json",
                {
                    "pid": os.getpid(),
                    "readiness": launcher.readiness_report,
                    "session_id": engine.session_id,
                    "initial_context": engine._public_conversation_context(),
                    "strict_flags": {key: os.environ.get(key) for key in STRICT},
                    "guardian_mode": os.environ.get("AETHERRA_GUARDIAN_MODE"),
                    "side_effects": side_effect_snapshot(profile),
                },
            )
            return result

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
                "_announce_os_online",
                observed_announcement,
            ):
                try:
                    exit_code = asyncio.run(launcher_module.main())
                except KeyboardInterrupt:
                    exit_code = 0
        finally:
            finished.set()
            if command_task is not None and not command_task.done():
                command_task.cancel()
            observer = (
                launcher_seen.systems.get("consciousness_core")
                if launcher_seen
                else None
            )
            write_json(
                profile / "provider.json",
                {
                    "exit_code": exit_code,
                    "prompts": responder.prompts,
                    "continuity_access_attempts": continuity_attempts,
                    "final_side_effects": side_effect_snapshot(profile),
                    "final_observer": (
                        observer.get_runtime_status() if observer else None
                    ),
                },
            )
        return exit_code


def observer_request(base, path):
    """Include intentional unavailable states as inspectable JSON evidence."""
    assert base.startswith("http://127.0.0.1:")
    assert path in {THINK, UI}
    req = urllib.request.Request(  # noqa: S310 - loopback only, checked above
        base + path, headers={"X-Aetherra-Token": CONTROL_TOKEN}
    )
    start = time.monotonic()
    try:
        response = urllib.request.urlopen(req, timeout=5)  # noqa: S310 - loopback only
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return {
            "status": response.status,
            "seconds": round(time.monotonic() - start, 3),
            "body": json.load(response),
        }


def snapshot(base):
    return {"think": observer_request(base, THINK), "ui": observer_request(base, UI)}


def wait_file(path, process, seconds=180):
    deadline = time.monotonic() + seconds
    while not path.exists():
        if process.poll() is not None or time.monotonic() >= deadline:
            raise RuntimeError(
                f"Timed out waiting for {path.name}; inspect runtime.log"
            )
        time.sleep(0.1)
    return json.loads(path.read_text(encoding="utf-8"))


def audit_summary(profile):
    path = profile / ".aetherra" / "security" / "audit.jsonl"
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    decisions = []
    for row in rows:
        details = row.get("details", {})
        intent = details.get("intent", {})
        action = intent.get("action", "")
        if action.startswith(("consciousness.", "memory.qfac", "continuity.")):
            decisions.append(
                {
                    "action": action,
                    "decision": details.get("decision", {}),
                    "audit_id": row.get("hash"),
                }
            )
    return decisions


def check_decisions(decisions, *, allowed):
    assert decisions, "No observable Guardian reflection decisions"
    assert all(
        row["action"]
        in {
            "consciousness.micro_reflection_update",
            "consciousness.macro_reflection_update",
        }
        for row in decisions
    )
    assert all(
        isinstance(row["audit_id"], str) and len(row["audit_id"]) == 64
        for row in decisions
    )
    statuses = {row["decision"]["status"] for row in decisions}
    assert statuses <= {"allow", "allow_limited"} if allowed else statuses == {"deny"}


def check_side_effects(before, after):
    unchanged = before["memory_ids"] == after["memory_ids"]
    assert unchanged, "Observer-only window wrote chat Memory"
    for key in ("qfac_graph_records", "qfac_simple_records"):
        assert before[key] == after[key] == 0
    assert after["experimental_modules"] == []
    assert after["continuity_files"] == []


def check_projection(value, *, allowed):
    think, ui = value["think"], value["ui"]
    assert ui["status"] == 200
    subsystem = ui["body"]["subsystem"]
    metrics = subsystem["metrics"]
    assert metrics["authority"] == metrics["autonomy_mode"] == "observe"
    for key in (
        "persistence_enabled",
        "qfac_persistence_enabled",
        "action_execution_enabled",
    ):
        assert metrics[key] is False
    if allowed:
        assert think["status"] == 200
        assert think["body"]["status"] == "running"
        assert subsystem["status"] == "active"
        assert metrics["available"] is True
        assert metrics["freshness"] == "fresh"
        assert metrics["ticks_completed"] > 0
        assert metrics["events_processed"] == 4 * metrics["ticks_completed"]
        focuses = think["body"]["focuses"]
        assert focuses
        assert all(
            item["source"] == "runtime" and item["target"] == "svc.health"
            for item in focuses
        )
        runtime = think["body"]["runtime"]
        assert runtime["available"] is True
        assert 0 < think["body"]["tick_id"] <= runtime["ticks_completed"]
        assert think["body"]["events_processed"] == runtime["events_processed"]
        assert runtime["ticks_completed"] <= metrics["ticks_completed"]
        assert think["body"]["autonomy_mode"] == "observe"
    else:
        assert think["status"] == 503
        assert think["body"]["status"] == "blocked"
        assert subsystem["status"] == "degraded"
        assert metrics["available"] is False
        assert metrics["ticks_completed"] == 0
    return metrics


def run_profile(profile, *, allowed, observe_seconds):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    record = {"allowed": allowed, "turns": [], "forced_stop": False}
    with (profile / "runtime.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--worker", str(profile)],
            cwd=profile,
            env=child_environment(profile, port),
            stdout=log,
            stderr=log,
        )
        record["pid"] = process.pid
        try:
            boot = record["boot"] = wait_file(profile / "boot.json", process)
            assert boot["readiness"]["status"] == "ready"
            assert boot["session_id"] is None
            assert boot["initial_context"] == {}
            assert set(boot["strict_flags"].values()) == {"1"}
            assert boot["guardian_mode"] == "enforcing"
            settled = record["startup_settled"] = wait_file(
                profile / "settled.json", process, 125
            )
            paths = (
                *OBSERVATIONS,
                "/api/guardian/status",
                "/api/selfinc/status",
                "/api/homeostasis/status",
                "/api/selfimprove/status",
            )
            record["core_snapshot"] = {path: request_json(base, path) for path in paths}
            validate_status(record["core_snapshot"])
            deadline = time.monotonic() + 15
            while True:
                first = snapshot(base)
                state = first["think"]["body"].get("status")
                if (
                    state in {"running", "blocked", "failed"}
                    or time.monotonic() >= deadline
                ):
                    break
                time.sleep(0.1)
            record["observer_first"] = first
            first_metrics = check_projection(first, allowed=allowed)
            deadline = time.monotonic() + observe_seconds
            while time.monotonic() < deadline:
                assert process.poll() is None
                time.sleep(min(0.2, max(0, deadline - time.monotonic())))
            record["observer_last"] = last = snapshot(base)
            last_metrics = check_projection(last, allowed=allowed)
            if allowed:
                assert (
                    last_metrics["ticks_completed"] > first_metrics["ticks_completed"]
                )
                assert (
                    last_metrics["events_processed"] > first_metrics["events_processed"]
                )
            (profile / "capture-side-effects").touch()
            after = record["side_effects_after_observer_window"] = wait_file(
                profile / "side-effects.json", process, 10
            )
            check_side_effects(settled["side_effects"], after)
            record["observer_window_guardian_decisions"] = audit_summary(profile)
            check_decisions(
                record["observer_window_guardian_decisions"], allowed=allowed
            )
            messages = [FACT, *COMPETITORS] if allowed else [QUESTION]
            for message in messages:
                turn = request_json(
                    base, "/api/ai/ask", message=message, token=CHAT_TOKEN, timeout=120
                )
                assert turn["body"]["ok"]
                validate_turn(turn["body"]["result"])
                record["turns"].append(turn)
            if allowed:
                record["after_chat"] = snapshot(base)
                check_projection(record["after_chat"], allowed=True)
                assert all(
                    message not in json.dumps(record["after_chat"])
                    for message in (FACT, *COMPETITORS)
                )
                (profile / "stop-observer").touch()
                stopped = record["stopped"] = wait_file(
                    profile / "observer-stopped.json", process, 15
                )
                assert stopped["observer"]["runtime_state"] == "stopped"
                assert stopped["observer"]["thread_alive"] is False
                assert stopped["new_context"]["message_count"] == 0
                record["after_stop"] = stopped_projection = snapshot(base)
                assert stopped_projection["think"]["status"] == 503
                assert stopped_projection["think"]["body"]["status"] == "stopped"
                assert (
                    stopped_projection["ui"]["body"]["subsystem"]["status"] == "offline"
                )
                for message in (QUESTION, UNKNOWN):
                    turn = request_json(
                        base,
                        "/api/ai/ask",
                        message=message,
                        token=CHAT_TOKEN,
                        timeout=120,
                    )
                    assert turn["body"]["ok"]
                    validate_turn(turn["body"]["result"])
                    record["turns"].append(turn)
            record["final_core_snapshot"] = {
                path: request_json(base, path) for path in paths
            }
            validate_status(record["final_core_snapshot"])
        finally:
            (profile / "stop-runtime").touch()
            try:
                process.wait(timeout=65)
            except subprocess.TimeoutExpired:
                record["forced_stop"] = True
                process.kill()
                process.wait(timeout=10)
            record["process_exit"] = process.returncode
            provider_path = profile / "provider.json"
            record["provider"] = (
                json.loads(provider_path.read_text(encoding="utf-8"))
                if provider_path.exists()
                else None
            )
            write_json(profile / "result.json", record)
    assert record["process_exit"] == 0
    assert record["forced_stop"] is False
    assert record["provider"]["exit_code"] == 0
    assert record["provider"]["continuity_access_attempts"] == []
    effects = record["provider"]["final_side_effects"]
    assert effects["experimental_modules"] == effects["continuity_files"] == []
    assert effects["qfac_graph_records"] == effects["qfac_simple_records"] == 0
    assert record["provider"]["final_observer"]["thread_alive"] is False
    with socket.socket() as sock:
        sock.settimeout(2)
        assert sock.connect_ex(("127.0.0.1", port)) != 0
    record["port_closed"] = True
    runtime_log = (profile / "runtime.log").read_text(encoding="utf-8")
    assert "Graceful shutdown complete" in runtime_log
    assert all(
        message not in runtime_log
        for message in (FACT, *COMPETITORS, QUESTION, UNKNOWN)
    )
    decisions = record["observer_guardian_decisions"] = audit_summary(profile)
    check_decisions(decisions, allowed=allowed)
    write_json(profile / "result.json", record)
    return record


def trace(profile, record):
    written, recalled = (
        record["turns"][0]["body"]["result"],
        record["turns"][-2]["body"]["result"],
    )
    saved_id = written["memory_id"]
    prompts = [
        prompt
        for prompt in record["provider"]["prompts"]
        if f"User: {QUESTION}\n" in prompt
    ]
    assert len(prompts) == 1
    supplied = [
        json.loads(line[2:])
        for line in prompts[0].splitlines()
        if line.startswith("- ")
    ]
    ids = [item["id"] for item in supplied]
    assert ids == recalled["recall"]["record_ids"] == recalled["llm"]["evidence_ids"]
    assert ids == [item["id"] for item in recalled["evidence"]]
    assert ids[0] == saved_id
    assert len(ids) <= 3
    with sqlite3.connect(
        f"file:{(profile / 'lyrixa_memory.db').as_posix()}?mode=ro", uri=True
    ) as db:
        stored = json.loads(
            db.execute(
                "SELECT content FROM memories WHERE id=?", (saved_id,)
            ).fetchone()[0]
        )
    assert stored["content"] == FACT
    assert stored["role"] == "user"
    assert FACT in prompts[0]
    assert "Leona" in recalled["response"]
    assert all(fact not in prompts[0] for fact in COMPETITORS)
    unknown = record["turns"][-1]["body"]["result"]["response"]
    assert "don't know" in unknown.lower()
    return {
        "record_id": saved_id,
        "retrieved_ids": ids,
        "provider_evidence_ids": recalled["llm"]["evidence_ids"],
        "llm": recalled["llm"],
        "response": recalled["response"],
        "unknown_response": unknown,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New disposable artifact directory")
    parser.add_argument("--observe-seconds", type=float, default=20)
    parser.add_argument("--worker", type=Path, help=argparse.SUPPRESS)
    parser.add_argument(
        "--continuity",
        action="store_true",
        help="Verify exact checkpoint restart across three normal full launches",
    )
    parser.add_argument("--artifacts", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--phase", choices=("a", "b", "c"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.continuity:
            if args.artifacts is None or args.phase is None:
                parser.error("Continuity workers require --artifacts and --phase")
            # Third party imports
            from alpha_consciousness_continuity_smoke import worker as continuity_worker

            return continuity_worker(args.worker, args.artifacts, args.phase)
        return worker(args.worker)
    if args.output is None or not 5 <= args.observe_seconds <= 300:
        parser.error("--output is required and --observe-seconds must be 5..300")
    output = args.output.resolve()
    if args.continuity:
        # Third party imports
        from alpha_consciousness_continuity_smoke import run as continuity_run

        return continuity_run(output, args.observe_seconds)
    output.mkdir(parents=True, exist_ok=False)
    summary = {"passed": False, "source_hashes_before": hashes()}
    write_json(output / "summary.json", summary)
    try:
        allowed, denied = output / "allowed", output / "denied"
        prepare_observer_profile(allowed, allowed=True)
        prepare_observer_profile(denied, allowed=False)
        positive = run_profile(
            allowed, allowed=True, observe_seconds=args.observe_seconds
        )
        evidence = trace(allowed, positive)
        negative = run_profile(
            denied, allowed=False, observe_seconds=args.observe_seconds
        )
        missing = negative["turns"][0]["body"]["result"]
        assert missing["recall"]["record_ids"] == missing["evidence"] == []
        assert "Leona" not in json.dumps(negative)
        assert "don't have" in missing["response"]
        summary.update(
            passed=True,
            entry="aetherra_os_launcher.py --mode full --no-gui --config PROFILE/launcher.json",
            responder="deterministic-context-responder",
            observation_seconds=args.observe_seconds,
            completed_ticks=[
                positive[key]["ui"]["body"]["subsystem"]["metrics"]["ticks_completed"]
                for key in ("observer_first", "observer_last")
            ],
            denied_completed_ticks=negative["observer_last"]["ui"]["body"]["subsystem"][
                "metrics"
            ]["ticks_completed"],
            trace=evidence,
            missing_response=missing["response"],
            process_exits=[positive["process_exit"], negative["process_exit"]],
            ports_closed=[positive["port_closed"], negative["port_closed"]],
            stop_mechanism="Local harness sentinel calls the owned observer stop; runtime stops with SIGINT, not interactive ConPTY keyboard evidence.",
            browser="Not exercised; Observatory HTTP payload verified.",
            live_model="Unverified; generation is the offline context-derived double.",
        )
    except Exception as exc:
        summary["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        summary["source_hashes_after"] = hashes()
        summary["source_unchanged"] = (
            summary["source_hashes_before"] == summary["source_hashes_after"]
        )
        if not summary["source_unchanged"]:
            summary["passed"] = False
            summary["error"] = (
                "Source changed during verification; rerun against a frozen candidate."
            )
        write_json(output / "summary.json", summary)
        print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
