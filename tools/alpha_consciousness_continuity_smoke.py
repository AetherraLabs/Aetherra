"""C2 restart evidence behind alpha_consciousness_smoke.py --continuity.

The normal full launcher, Memory, Guardian, Security and Core remain real. Only
text generation is doubled. Trusted wrappers seed explicitly synthetic trust
observations and capture aggregates on Core's owner thread; they never perform
or replace checkpoint I/O. Private synthetic artifacts stay in the run directory.
"""

from __future__ import annotations

# Standard library imports
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
from contextlib import ExitStack
from pathlib import Path

# Third party imports
from alpha_consciousness_smoke import (
    STRICT,
    UNKNOWN,
    audit_summary,
    hashes,
    prepare_observer_profile,
    side_effect_snapshot,
    snapshot,
    wait_file,
)
from alpha_integration_smoke import (
    CHAT_TOKEN,
    COMPETITORS,
    FACT,
    OBSERVATIONS,
    QUESTION,
    ROOT,
    child_environment,
    request_json,
    validate_status,
    validate_turn,
    write_json,
)

SENTINEL = "checkpoint_only_sentinel40"
CHECKPOINT_TYPE = "consciousness_observer_checkpoint:"
CORE_PATHS = (
    *OBSERVATIONS,
    "/api/guardian/status",
    "/api/selfinc/status",
    "/api/homeostasis/status",
    "/api/selfimprove/status",
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def aggregate(payload):
    """Capture time and receipt identity are metadata, not imported Core state."""
    return {"qualia": payload["qualia"], "trust": payload["trust"]}


def configure(profile, handle=None, *, fresh=False):
    if fresh:
        prepare_observer_profile(profile, allowed=True)
        path = profile / "policy" / "guardian.json"
        policy = json.loads(path.read_text(encoding="utf-8"))
        policy["allow"].extend(
            {
                "requester": "consciousness:core",
                "subsystem": "consciousness",
                "action": f"consciousness.continuity_{operation}",
                "target": "memory:core",
            }
            for operation in ("save", "restore")
        )
        write_json(path, policy)
        path = profile / "policy" / "capabilities.json"
        capabilities = json.loads(path.read_text(encoding="utf-8"))
        capabilities["allow"]["consciousness:core"] = [
            "consciousness:write",
            "memory:read",
            "memory:write",
            "fs:read",
            "fs:write",
        ]
        write_json(path, capabilities)
    path = profile / "launcher.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["consciousness_continuity"] = {
        "enabled": True,
        "restore_checkpoint_id": handle,
    }
    write_json(path, config)


def worker(profile, artifacts, phase):
    """Observe actual owner-thread work without providing a restore oracle."""
    # Standard library imports
    import _thread
    from unittest.mock import patch

    legacy_access = []

    def offline(event, args):
        if (
            event == "open"
            and isinstance(args[0], (str, bytes, os.PathLike))
            and Path(os.fsdecode(args[0])).name.lower() == "continuity.json"
        ):
            legacy_access.append("continuity_json_access")
            raise PermissionError("continuity_smoke_legacy_file_denied")
        if event in {"socket.connect", "socket.bind"}:
            address = args[1]
            if not isinstance(address, tuple) or address[0] not in {
                "127.0.0.1",
                "::1",
                "localhost",
            }:
                raise PermissionError("continuity_smoke_external_network_denied")
        if event == "socket.getaddrinfo" and args[0] not in {
            "127.0.0.1",
            "::1",
            "localhost",
            b"localhost",
        }:
            raise PermissionError("continuity_smoke_external_dns_denied")
        if event == "subprocess.Popen":
            raise PermissionError("continuity_smoke_subprocess_denied")

    sys.addaudithook(offline)
    # Aetherra imports
    from Aetherra.consciousness.checkpoint import encode_checkpoint
    from Aetherra.consciousness.core.consciousness_core import ConsciousnessCore
    from Aetherra.security.audit_ledger import SecurityAuditLedger
    from aetherra_service_registry import AetherraServiceRegistry
    from tests.acceptance.continuity_runtime import ContextResponder

    responder = ContextResponder()
    finished = threading.Event()
    launcher_seen = None
    command_task = None
    original_init = ConsciousnessCore.__init__
    original_tick = ConsciousnessCore.tick
    original_restore = ConsciousnessCore.restore_observer_checkpoint
    original_status = AetherraServiceRegistry.update_service_status
    status_errors = []

    async def observed_status(registry, name, status, *args, **kwargs):
        started = time.monotonic()
        try:
            return await original_status(registry, name, status, *args, **kwargs)
        except Exception as exc:
            if name == "consciousness_core":
                status_errors.append(
                    {
                        "service": "consciousness_core",
                        "status": getattr(status, "value", "unknown"),
                        "exception_class": type(exc).__name__,
                        "elapsed_seconds": round(time.monotonic() - started, 6),
                    }
                )
                write_json(artifacts / "registry-status-errors.json", status_errors)
            raise

    def seeded_init(core, *args, **kwargs):
        original_init(core, *args, **kwargs)
        if core.observer_only and phase == "a":
            # A bounded synthetic input fixture; persistence and restore stay real.
            seed_time = time.time()
            normal_clock = core.self_trust._clock
            core.self_trust._clock = lambda: seed_time
            try:
                for _ in range(5):
                    core.self_trust.observe(SENTINEL, "failed")
            finally:
                core.self_trust._clock = normal_clock
            for name, value in {
                "valence": -0.4,
                "arousal": 0.3,
                "certainty": 0.6,
                "curiosity": 0.7,
                "care": 0.5,
                "fatigue": 0.2,
            }.items():
                setattr(core.qualia, name, value)
            write_json(
                artifacts / "private-synthetic-seed.json",
                {
                    "synthetic": True,
                    "seed_clock": "Fixed current timestamp for five seed observations only; ordinary clock restored before runtime ticks.",
                    "thread": threading.current_thread().name,
                    "aggregate": aggregate(
                        encode_checkpoint(core.export_observer_checkpoint("0" * 32))
                    ),
                },
            )

    def observed_restore(core, state):
        original_restore(core, state)
        # This runs inside the real observer restore, before its first tick.
        write_json(
            artifacts / "private-restored.json",
            {
                "thread": threading.current_thread().name,
                "checkpoint_id": state.checkpoint_id,
                "tick_count": core.tick_count,
                "events_processed": core.total_events_perceived,
                "aggregate": aggregate(
                    encode_checkpoint(
                        core.export_observer_checkpoint(state.checkpoint_id)
                    )
                ),
            },
        )

    def observed_tick(core):
        if core.observer_only and core.tick_count == 0:
            write_json(
                artifacts / "private-before-first-tick.json",
                {
                    "thread": threading.current_thread().name,
                    "tick_count": core.tick_count,
                    "events_processed": core.total_events_perceived,
                    "aggregate": aggregate(
                        encode_checkpoint(core.export_observer_checkpoint("0" * 32))
                    ),
                },
            )
        return original_tick(core)

    def stop_watcher():
        while not finished.wait(0.1):
            if (artifacts / "stop-runtime").exists():
                _thread.interrupt_main()
                return

    async def commands(launcher):
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
                    artifacts / "settled.json",
                    {
                        "kernel_cycle_count": kernel["cycle_count"],
                        "side_effects": side_effect_snapshot(profile),
                    },
                )
                break
            if time.monotonic() >= deadline:
                return
            await asyncio.sleep(0.05)
        while True:
            if (artifacts / "stop-observer").exists() and not (
                artifacts / "observer-stopped.json"
            ).exists():
                await launcher._stop_consciousness_observer(save_checkpoint=True)
                engine = launcher.systems["aetherra"].impl
                await engine.start_conversation()
                write_json(
                    artifacts / "observer-stopped.json",
                    {
                        "observer": launcher.systems[
                            "consciousness_core"
                        ].get_runtime_status(),
                        "new_context": engine._public_conversation_context(),
                    },
                )
            await asyncio.sleep(0.05)

    with ExitStack() as stack:
        stack.enter_context(
            patch(
                "Aetherra.core.multi_llm_manager.get_llm_manager",
                return_value=responder,
            )
        )
        stack.enter_context(
            patch.object(
                AetherraServiceRegistry, "update_service_status", observed_status
            )
        )
        stack.enter_context(patch.object(ConsciousnessCore, "__init__", seeded_init))
        stack.enter_context(patch.object(ConsciousnessCore, "tick", observed_tick))
        stack.enter_context(
            patch.object(
                ConsciousnessCore, "restore_observer_checkpoint", observed_restore
            )
        )
        # Aetherra imports
        import aetherra_os_launcher as launcher_module

        original_announcement = launcher_module.AetherraOSLauncher._announce_os_online

        async def observed_announcement(launcher):
            nonlocal launcher_seen, command_task
            result = await original_announcement(launcher)
            launcher_seen = launcher
            engine = launcher.systems["aetherra"].impl
            command_task = asyncio.create_task(commands(launcher))
            write_json(
                artifacts / "boot.json",
                {
                    "pid": os.getpid(),
                    "readiness": launcher.readiness_report,
                    "session_id": engine.session_id,
                    "initial_context": engine._public_conversation_context(),
                    "strict_flags": {key: os.environ.get(key) for key in STRICT},
                    "guardian_mode": os.environ.get("AETHERRA_GUARDIAN_MODE"),
                },
            )
            return result

        stack.enter_context(
            patch.object(
                launcher_module.AetherraOSLauncher,
                "_announce_os_online",
                observed_announcement,
            )
        )
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
            ledger = SecurityAuditLedger(
                profile / ".aetherra" / "security" / "audit.jsonl"
            )
            write_json(
                artifacts / "private-provider.json", {"prompts": responder.prompts}
            )
            write_json(
                artifacts / "provider.json",
                {
                    "exit_code": exit_code,
                    "legacy_access_attempts": legacy_access,
                    "final_side_effects": side_effect_snapshot(profile),
                    "final_observer": (
                        observer.get_runtime_status() if observer else None
                    ),
                    "launcher_stopped": launcher_seen is not None
                    and not launcher_seen.running,
                    "signed_audit_verified": ledger.verify_integrity(
                        require_signed_records=True
                    ),
                },
            )
        return exit_code


def checkpoint_rows(profile):
    """Read-only independent persisted evidence; never creates or repairs a DB."""
    with sqlite3.connect(
        f"file:{(profile / 'lyrixa_memory.db').as_posix()}?mode=ro", uri=True
    ) as db:
        return [
            {"record_id": row[0], "payload": json.loads(row[1]), "memory_type": row[2]}
            for row in db.execute(
                "SELECT id,content,memory_type FROM memories WHERE memory_type LIKE ? ORDER BY id",
                (CHECKPOINT_TYPE + "%",),
            )
        ]


def chat(base, message):
    turn = request_json(
        base, "/api/ai/ask", message=message, token=CHAT_TOKEN, timeout=120
    )
    assert turn["body"]["ok"] is True
    validate_turn(turn["body"]["result"])
    assert turn["body"]["result"]["llm"]["model"] == {
        "provider": "deterministic",
        "model": "context-responder",
    }
    return turn


def projection(value, *, blocked=False):
    think, ui = value["think"], value["ui"]
    assert ui["status"] == 200
    metrics = ui["body"]["subsystem"]["metrics"]
    assert metrics["authority"] == metrics["autonomy_mode"] == "observe"
    assert metrics["qfac_persistence_enabled"] is False
    assert metrics["action_execution_enabled"] is False
    assert metrics["persistence_enabled"] is True
    if blocked:
        assert think["status"] == 503
        assert think["body"]["status"] == "blocked"
        assert metrics["ticks_completed"] == 0
        assert metrics["continuity_state"] == "blocked"
        assert metrics["continuity_error_code"] == "missing"
    else:
        assert think["status"] == 200
        assert think["body"]["status"] == "running"
        assert metrics["ticks_completed"] > 0
        assert metrics["events_processed"] == 4 * metrics["ticks_completed"]
    return metrics


def run_process(profile, artifacts, phase, observe_seconds):
    artifacts.mkdir(parents=True, exist_ok=False)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    record = {"phase": phase, "turns": [], "forced_stop": False}
    audit_before = (
        len(audit_summary(profile))
        if (profile / ".aetherra/security/audit.jsonl").exists()
        else 0
    )
    with (artifacts / "runtime.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                str(ROOT / "tools/alpha_consciousness_smoke.py"),
                "--continuity",
                "--worker",
                str(profile),
                "--artifacts",
                str(artifacts),
                "--phase",
                phase,
            ],
            cwd=profile,
            env=child_environment(profile, port),
            stdout=log,
            stderr=log,
        )
        record["pid"] = process.pid
        try:
            boot = record["boot"] = wait_file(artifacts / "boot.json", process)
            assert boot["readiness"]["status"] == "ready"
            assert boot["session_id"] is None
            assert boot["initial_context"] == {}
            assert set(boot["strict_flags"].values()) == {"1"}
            assert boot["guardian_mode"] == "enforcing"
            record["startup_settled"] = wait_file(
                artifacts / "settled.json", process, 125
            )
            record["core_snapshot"] = {
                path: request_json(base, path) for path in CORE_PATHS
            }
            validate_status(record["core_snapshot"])
            deadline = time.monotonic() + 15
            while True:
                first = snapshot(base)
                if first["think"]["body"].get("status") in {
                    "running",
                    "blocked",
                    "failed",
                    "stopped",
                }:
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
            record["observer_first"] = first
            first_metrics = projection(first, blocked=phase == "c")
            deadline = time.monotonic() + observe_seconds
            while time.monotonic() < deadline:
                assert process.poll() is None
                time.sleep(min(0.2, max(0, deadline - time.monotonic())))
            record["observer_last"] = last = snapshot(base)
            last_metrics = projection(last, blocked=phase == "c")
            if phase != "c":
                assert (
                    last_metrics["ticks_completed"] > first_metrics["ticks_completed"]
                )
            # Stop independently before all chat. Repeat runtime shutdown later must not resave.
            (artifacts / "stop-observer").touch()
            stopped = record["stopped"] = wait_file(
                artifacts / "observer-stopped.json", process, 15
            )
            assert stopped["observer"]["thread_alive"] is False
            assert stopped["new_context"]["message_count"] == 0
            continuity = stopped["observer"]["continuity"]
            if phase == "c":
                assert continuity["state"] == "blocked"
                assert continuity["saved_record_id"] is None
            else:
                assert stopped["observer"]["runtime_state"] == "stopped"
                assert continuity["state"] == "saved"
                assert continuity["saved_record_id"]
                assert continuity["saved_checkpoint_id"]
                assert continuity["outstanding"] is False
            record["checkpoint_rows_after_stop"] = [
                {
                    "record_id": row["record_id"],
                    "checkpoint_id": row["payload"]["checkpoint_id"],
                }
                for row in checkpoint_rows(profile)
            ]
            messages = ([FACT, *COMPETITORS] if phase == "a" else []) + [
                QUESTION,
                UNKNOWN,
            ]
            record["turns"] = [chat(base, message) for message in messages]
            record["after_stop"] = snapshot(base)
            assert record["after_stop"]["think"]["status"] == 503
            record["final_core_snapshot"] = {
                path: request_json(base, path) for path in CORE_PATHS
            }
            validate_status(record["final_core_snapshot"])
        finally:
            (artifacts / "stop-runtime").touch()
            try:
                process.wait(timeout=65)
            except subprocess.TimeoutExpired:
                record["forced_stop"] = True
                process.kill()
                process.wait(timeout=10)
            record["process_exit"] = process.returncode
            path = artifacts / "provider.json"
            record["provider"] = (
                json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
            )
            write_json(artifacts / "result.json", record)
    assert record["process_exit"] == 0
    assert record["forced_stop"] is False
    provider = record["provider"]
    assert provider["exit_code"] == 0
    assert provider["launcher_stopped"] is True
    assert provider["signed_audit_verified"] is True
    assert provider["legacy_access_attempts"] == []
    assert provider["final_observer"]["thread_alive"] is False
    effects = provider["final_side_effects"]
    assert effects["experimental_modules"] == effects["continuity_files"] == []
    assert effects["qfac_graph_records"] == effects["qfac_simple_records"] == 0
    assert len(checkpoint_rows(profile)) == len(record["checkpoint_rows_after_stop"])
    with socket.socket() as sock:
        sock.settimeout(2)
        assert sock.connect_ex(("127.0.0.1", port)) != 0
    record["port_closed"] = True
    runtime_log = (artifacts / "runtime.log").read_text(encoding="utf-8")
    assert "Graceful shutdown complete" in runtime_log
    assert all(
        value not in runtime_log
        for value in (FACT, *COMPETITORS, QUESTION, UNKNOWN, SENTINEL)
    )
    decisions = audit_summary(profile)[audit_before:]
    assert decisions
    assert all(len(row["audit_id"]) == 64 for row in decisions)
    assert all(
        row["decision"]["status"] in {"allow", "allow_limited"} for row in decisions
    )
    actions = [row["action"] for row in decisions]
    assert actions.count("consciousness.continuity_save") == (0 if phase == "c" else 1)
    assert actions.count("consciousness.continuity_restore") == (
        0 if phase == "a" else 1
    )
    record["guardian_decisions"] = decisions
    write_json(artifacts / "result.json", record)
    return record


def check_chat(record, artifacts, saved_fact_id, forbidden):
    prompts = json.loads(
        (artifacts / "private-provider.json").read_text(encoding="utf-8")
    )["prompts"]
    prompt_text = json.dumps(prompts)
    assert all(value not in prompt_text for value in forbidden)
    for turn in record["turns"]:
        result = turn["body"]["result"]
        supplied = json.dumps(
            {key: result[key] for key in ("evidence", "recall", "llm")}
        )
        assert all(value not in supplied for value in forbidden)
    recalled = record["turns"][-2]["body"]["result"]
    prompt = [value for value in prompts if f"User: {QUESTION}\n" in value]
    assert len(prompt) == 1
    evidence = [
        json.loads(line[2:]) for line in prompt[0].splitlines() if line.startswith("- ")
    ]
    ids = [item["id"] for item in evidence]
    assert ids == recalled["recall"]["record_ids"] == recalled["llm"]["evidence_ids"]
    assert ids == [item["id"] for item in recalled["evidence"]]
    if saved_fact_id:
        assert ids[0] == saved_fact_id
        assert len(ids) <= 3
        assert "Leona" in recalled["response"]
        assert FACT in prompt[0]
        assert all(value not in prompt[0] for value in COMPETITORS)
    else:
        assert ids == []
        assert "Leona" not in recalled["response"]
        assert "don't have" in recalled["response"].lower()
    assert "don't know" in record["turns"][-1]["body"]["result"]["response"].lower()
    return {
        "record_ids": ids,
        "provider_evidence_ids": recalled["llm"]["evidence_ids"],
        "llm": recalled["llm"],
        "response": recalled["response"],
        "unknown_response": record["turns"][-1]["body"]["result"]["response"],
    }


def run(output, observe_seconds):
    output.mkdir(parents=True, exist_ok=False)
    summary = {"passed": False, "mode": "continuity", "source_hashes_before": hashes()}
    write_json(output / "summary.json", summary)
    try:
        primary, foreign = output / "primary", output / "foreign"
        configure(primary, fresh=True)
        a = run_process(primary, output / "run-a", "a", observe_seconds)
        rows_a = checkpoint_rows(primary)
        assert len(rows_a) == 1
        saved = a["stopped"]["observer"]["continuity"]
        row_a = rows_a[0]
        payload = row_a["payload"]
        assert row_a["record_id"] == saved["saved_record_id"]
        assert payload["checkpoint_id"] == saved["saved_checkpoint_id"]
        assert row_a["memory_type"] == CHECKPOINT_TYPE + payload["checkpoint_id"]
        assert row_a["record_id"] != payload["checkpoint_id"]
        trust = next(
            item for item in payload["trust"]["subsystems"] if item["name"] == SENTINEL
        )
        assert trust["score"] == 40.0
        assert trust["history"] == [
            88.0,
            76.0,
            64.0,
            52.0,
            40.0,
        ]
        assert trust["last_event_ts"] > 0
        assert payload["captured_at"] > 0
        assert set(payload["qualia"]) == {
            "valence",
            "arousal",
            "certainty",
            "curiosity",
            "care",
            "fatigue",
        }
        assert -0.4 < payload["qualia"]["valence"] < 0
        assert all(
            value > 0 for name, value in payload["qualia"].items() if name != "valence"
        )
        saved_fact_id = a["turns"][0]["body"]["result"]["memory_id"]
        configure(primary, payload["checkpoint_id"])
        b = run_process(primary, output / "run-b", "b", observe_seconds)
        rows_b = checkpoint_rows(primary)
        assert len(rows_b) == 2
        assert row_a in rows_b
        restored = json.loads(
            (output / "run-b/private-restored.json").read_text(encoding="utf-8")
        )
        first_tick = json.loads(
            (output / "run-b/private-before-first-tick.json").read_text(
                encoding="utf-8"
            )
        )
        assert restored["thread"] == first_tick["thread"] == "consciousness-observer"
        assert restored["tick_count"] == first_tick["tick_count"] == 0
        assert restored["events_processed"] == first_tick["events_processed"] == 0
        assert restored["checkpoint_id"] == payload["checkpoint_id"]
        assert restored["aggregate"] == first_tick["aggregate"] == aggregate(payload)
        selected = b["stopped"]["observer"]["continuity"]
        assert selected["selected_checkpoint_id"] == payload["checkpoint_id"]
        assert selected["restored_record_id"] == row_a["record_id"]
        configure(foreign, payload["checkpoint_id"], fresh=True)
        c = run_process(foreign, output / "run-c", "c", observe_seconds)
        assert checkpoint_rows(foreign) == []
        assert not (output / "run-c/private-restored.json").exists()
        assert not (output / "run-c/private-before-first-tick.json").exists()
        forbidden = [
            SENTINEL,
            *[row["record_id"] for row in rows_b],
            *[row["payload"]["checkpoint_id"] for row in rows_b],
        ]
        traces = [
            check_chat(record, output / f"run-{phase}", fact_id, forbidden)
            for phase, record, fact_id in (
                ("a", a, saved_fact_id),
                ("b", b, saved_fact_id),
                ("c", c, None),
            )
        ]
        assert len({record["pid"] for record in (a, b, c)}) == 3
        blocked = c["stopped"]["observer"]
        summary.update(
            passed=True,
            entry="aetherra_os_launcher.py --mode full --no-gui --config PROFILE/launcher.json",
            responder="deterministic-context-responder",
            live_provider_verified=False,
            observation_seconds=observe_seconds,
            processes={
                phase: {
                    "pid": record["pid"],
                    "artifact_directory": f"run-{phase}",
                    "initial_continuity": {
                        key: value
                        for key, value in record["observer_first"]["ui"]["body"][
                            "subsystem"
                        ]["metrics"].items()
                        if key.startswith("continuity_")
                    },
                    "stopped_observer": record["stopped"]["observer"],
                    "checkpoint_audit_references": [
                        {"action": row["action"], "audit_id": row["audit_id"]}
                        for row in record["guardian_decisions"]
                        if row["action"].startswith("consciousness.continuity_")
                    ],
                    "exit_code": record["process_exit"],
                }
                for phase, record in (("a", a), ("b", b), ("c", c))
            },
            checkpoint={
                "checkpoint_id": payload["checkpoint_id"],
                "saved_record_id": row_a["record_id"],
                "restored_record_id": selected["restored_record_id"],
                "persisted_payload_sha256": digest(payload),
                "restored_aggregate_sha256": digest(restored["aggregate"]),
                "persisted_aggregate_sha256": digest(aggregate(payload)),
                "exact_state_match": True,
                "pre_first_tick_count": 0,
                "nontrivial_trust_observations": len(trust["history"]),
                "nontrivial_trust_score": trust["score"],
                "nontrivial_qualia_dimensions": len(payload["qualia"]),
                "negative_valence_restored": restored["aggregate"]["qualia"]["valence"]
                < 0,
            },
            checkpoint_records_after_a=1,
            checkpoint_records_after_b=2,
            checkpoint_records_after_c=0,
            process_exits=[record["process_exit"] for record in (a, b, c)],
            ports_closed=[record["port_closed"] for record in (a, b, c)],
            signed_audits_verified=[
                record["provider"]["signed_audit_verified"] for record in (a, b, c)
            ],
            fresh_chat_history=[
                record["boot"]["initial_context"] == {} for record in (a, b, c)
            ],
            foreign_restore_state=blocked["continuity"]["state"],
            foreign_restore_error=blocked["continuity"]["last_error_code"],
            foreign_restore_ticks=blocked["ticks_completed"],
            checkpoint_excluded_from_chat=True,
            personal_recall_verified=[True, True],
            honest_unknown_verified=[True, True, True],
            traces=traces,
            synthetic_seed="Five real SelfTrust.observe failed observations at a fixed synthetic seed timestamp plus nontrivial qualia on the Core owner thread; normal clock resumes before runtime ticks.",
            stop_mechanism="Trusted local harness requests orderly observer stop; runtime stops with SIGINT.",
            browser="Not exercised; Observatory HTTP status verified.",
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
