"""Bounded, offline P0 investigation; observations are not acceptance contracts.

Uses the normal full launcher and existing Hub/registry/Self-Incorporation paths.
Controls are labeled: validator fixture, POSIX path model, execution tripwire
and the existing offline generation double. No integration permission is granted.
Output requires a NEW directory.
"""

from __future__ import annotations

# Standard library imports
import argparse
import asyncio
import dataclasses
import faulthandler
import hashlib
import json
import os
import platform
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Aetherra imports
from tools import alpha_integration_smoke as smoke  # noqa: E402

PREFIX = "aetherra_qfac_validator_"
FLAGS = (
    "AETHERRA_QFAC_VALIDATOR_FAKE",
    "AETHERRA_QFAC_VALIDATOR_FAKE_GREEN",
    "AETHERRA_QFAC_VALIDATOR_FAKE_BLOCKED",
    "AETHERRA_QFAC_SHADOW_FAKE",
    "AETHERRA_QFAC_FAST_STUB",
    "AETHERRA_SELFINC_ENABLED",
    "AETHERRA_SELFINC_STRICT",
    "AETHERRA_SIGNING_STRICT",
    "AETHERRA_SCRIPT_VERIFY_STRICT",
    "AETHERRA_REQUIRE_CAPABILITIES",
    "AETHERRA_NET_STRICT",
)


def http(port, path, *, apply=False, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["X-Aetherra-Token"] = token
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=b"{}" if apply else None,
        headers=headers,
    )
    try:
        response = urllib.request.urlopen(request, timeout=10)  # noqa: S310
    except urllib.error.HTTPError as error:
        response = error
    with response:
        text = response.read().decode()
        if path == "/metrics":
            value = {
                line.split()[0]: float(line.split()[1])
                for line in text.splitlines()
                if line.startswith(PREFIX)
            }
        else:
            value = json.loads(text)
        return {"http_status": response.status, "value": value}


class ValidatorFixture:
    """Synthetic producer, never represented as a real validator backend."""

    failing = False
    calls = 0

    def get_status(self):
        self.calls += 1
        if self.failing:
            raise RuntimeError("synthetic_validator_unavailable")
        return {"green_total": 17, "blocked_total": 4}


async def observe(launcher, profile, port):
    registry = launcher.service_registry
    service = registry.get_service("self_incorporation")
    launcher_service = launcher.systems["self_incorporation"]
    result = {
        "platform": platform.system(),
        "python": platform.python_version(),
        "effective_flags": {key: os.getenv(key) for key in FLAGS},
        "validator_registered_at_boot": registry.get_service("qfac_validator")
        is not None,
        "launcher_selfinc_enabled": launcher_service.config.enabled,
        "registry_selfinc_enabled": service.config.enabled,
        "same_selfinc_instance": service is launcher_service,
        "classifications_before_manual_evaluation": len(
            service.classification_index.list_classifications()
        ),
        "missing_validator": await asyncio.to_thread(http, port, "/metrics"),
    }
    fixture = ValidatorFixture()
    assert await registry.register_service(
        "qfac_validator", fixture, metadata={"synthetic_p0_fixture": True}
    )
    prior = os.environ.get("AETHERRA_QFAC_VALIDATOR_FAKE")
    try:
        result["fixture_expected_counts"] = fixture.get_status()
        result["fixture_full_flags"] = await asyncio.to_thread(http, port, "/metrics")
        os.environ["AETHERRA_QFAC_VALIDATOR_FAKE"] = "0"
        result["fixture_override_disabled_control"] = await asyncio.to_thread(
            http, port, "/metrics"
        )
        fixture.failing = True
        result["fixture_unavailable_control"] = await asyncio.to_thread(
            http, port, "/metrics"
        )
        result["fixture_status_calls"] = fixture.calls
    finally:
        if prior is None:
            os.environ.pop("AETHERRA_QFAC_VALIDATOR_FAKE", None)
        else:
            os.environ["AETHERRA_QFAC_VALIDATOR_FAKE"] = prior
        assert await registry.unregister_service("qfac_validator")
    result["selfinc_http_status"] = await asyncio.to_thread(
        http, port, "/api/selfinc/status"
    )
    result["unauthenticated_apply"] = await asyncio.to_thread(
        http, port, "/api/selfinc/apply", apply=True
    )
    if service.config.enabled:
        result["scan"] = await service.trigger_scan()
        result["classify"] = await service.trigger_classify()
        result["evaluate"] = await service.trigger_security_eval()
        files = service.code_index.list_files()
        assert len(files) == 1, "Only the harmless fixture should be discovered"
        item = files[0]
        decision = service.safety_index.get_decision(item.id)
        result["native_decision"] = dataclasses.asdict(decision)
        result["file_id"] = item.id
        result["artifact_has_signature"] = Path(item.path + ".sig").exists()
        unsigned_result = await service.security_layer.verify_signature(Path(item.path))
        result["separate_helper_unsigned_result"] = unsigned_result
        # Path-string model ONLY: no claim of native Linux execution.
        # Aetherra imports
        import aetherra_self_incorporation as selfinc

        modeled = dataclasses.replace(item, path=Path(item.path).as_posix())
        with patch.object(selfinc, "Path", PurePosixPath):
            verified, signing = service.security_gate._verify_signatures(modeled)
        result["posix_path_model_only"] = {"verified": verified, "signing": signing}
        plan = await service._run_integration_planning()
        result["plan"] = {
            key: plan[key]
            for key in ("plan_id", "status", "active_components", "integration_order")
        }
        result["plan"]["actions"] = [dataclasses.asdict(a) for a in plan["actions"]]
        reopened = selfinc.SafetyIndex(service.safety_index.db_path)
        result["reopened_decision"] = dataclasses.asdict(reopened.get_decision(item.id))
        result["second_evaluation"] = await service.trigger_security_eval()
        # Tripwire only: if a guard unexpectedly permits execution, fail before mutation.
        with patch.object(
            service.core_integrator,
            "execute_plan",
            side_effect=AssertionError("unexpected_execution_boundary_crossed"),
        ) as execution:
            result["authenticated_apply"] = await asyncio.to_thread(
                http, port, "/api/selfinc/apply", apply=True, token=smoke.CONTROL_TOKEN
            )
            result["direct_service_apply"] = await service.trigger_integrate(
                requester="p0:unapproved"
            )
            result["execute_plan_calls"] = execution.call_count
            assert execution.call_count == 0
    else:
        result["disabled_scan"] = await service.trigger_scan()
    smoke.write_json(profile / "probe.json", result)


def worker(profile, port):
    # Retain stacks if interpreter shutdown outlives the probe; deadline unchanged.
    faulthandler.enable()
    faulthandler.dump_traceback_later(50)
    # Aetherra imports
    import aetherra_os_launcher as launcher

    original = launcher.AetherraOSLauncher._main_operation_loop

    async def observed_loop(runtime):
        await observe(runtime, profile, port)
        return await original(runtime)

    with patch.object(
        launcher.AetherraOSLauncher, "_main_operation_loop", observed_loop
    ):
        return smoke.worker(profile, "runtime")


def run_profile(output, name, enabled):
    profile = output / name
    smoke.prepare_profile(profile)
    source = profile / "source" / "Aetherra" / "aetherra_core"
    source.mkdir(parents=True)
    (source / "p0_fixture.py").write_text(
        '"""Harmless P0 investigation fixture; never imported or executed."""\n'
        'def value():\n    return "synthetic"\n',
        encoding="utf-8",
    )
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = smoke.child_environment(profile, port)
    env.pop("AETHERRA_SELFINC_ENABLED", None)
    env.update(
        {
            "AETHERRA_SELFINC_ROOTS": str(profile / "source"),
            "AETHERRA_SELFINC_STRICT": "1",
            "AETHERRA_SELFINC_TRUST_MODE": "strict",
            "AETHERRA_QFAC_VALIDATOR_FAKE_GREEN": "99",
            "AETHERRA_QFAC_VALIDATOR_FAKE_BLOCKED": "8",
        }
    )
    if enabled is not None:
        env["AETHERRA_SELFINC_ENABLED"] = "1" if enabled else "0"
        env["AETHERRA_NO_FAKE_DATA"] = "0"  # Full mode itself still selects no-fake.
    started = time.monotonic()
    with (profile / "runtime.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker",
                str(profile),
                "--port",
                str(port),
            ],
            cwd=profile,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        timed_out = False
        try:
            while process.poll() is None and not (profile / "probe.json").exists():
                if time.monotonic() - started > 180:
                    timed_out = True
                    break
                time.sleep(0.1)
            (profile / "runtime-stop").touch()
            process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            timed_out = True
            process.kill()
            process.wait(timeout=10)
    receipt = {
        "exit_code": process.returncode,
        "timed_out": timed_out,
        "seconds": round(time.monotonic() - started, 2),
        "probe_completed": (profile / "probe.json").exists(),
        "stop": "automated interrupt_main; not a physical keyboard check",
    }
    smoke.write_json(profile / "receipt.json", receipt)
    receipt["completed_cleanly"] = (
        process.returncode == 0 and not timed_out and receipt["probe_completed"]
    )
    smoke.write_json(profile / "receipt.json", receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    if args.worker:
        return worker(args.worker, args.port)
    if args.output is None:
        parser.error("--output is required")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    receipts = {
        name: run_profile(output, name, enabled)
        for name, enabled in (
            ("full-default", None),
            ("full-selfinc-opt-in", True),
            ("full-explicit-disable", False),
        )
    }
    smoke.write_json(
        output / "provenance.json",
        {
            "source_revision": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "probe_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "scope": "offline diagnostic observations, not alpha acceptance or fixed bug contracts",
        },
    )
    smoke.write_json(output / "receipts.json", receipts)
    print(json.dumps(receipts, indent=2))
    return int(any(not receipt["completed_cleanly"] for receipt in receipts.values()))


if __name__ == "__main__":
    raise SystemExit(main())
