"""Real file-backed Memory and separate interpreter processes; no provider doubles."""

# Standard library imports
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

# Third party imports
import pytest

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 11, 23, 12, tzinfo=UTC)


def _run_worker(profile, mode, handle=""):
    profile.mkdir(exist_ok=True)
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.upper().startswith(
            (
                "AETH",
                "LYRIXA",
                "PYTHON",
                "OPENAI",
                "ANTHROPIC",
                "AZURE",
                "AWS",
                "GOOGLE",
            )
        )
        and not any(
            s in k.upper() for s in ("TOKEN", "SECRET", "KEY", "PASSWORD", "CREDENTIAL")
        )
    }
    env.update(
        PYTHONPATH=str(ROOT),
        PYTHONUTF8="1",
        PYTHONDONTWRITEBYTECODE="1",
        AETHERRA_SKIP_DOTENV="1",
        AETHERRA_GUARDIAN_MODE="enforcing",
        AETHERRA_REQUIRE_CAPABILITIES="1",
        AETHERRA_WORKSPACE_ROOT=str(profile),
        AETHERRA_POLICY_HOME=str(profile / "policy"),
        AETHERRA_NET_STRICT="1",
        AETHERRA_SIGNING_STRICT="1",
        AETHERRA_SCRIPT_VERIFY_STRICT="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
    )
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), mode, handle],
        cwd=profile,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=90,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.splitlines()[-1])


def test_memory_checkpoint_survives_process_restart_and_profile_isolation(tmp_path):
    profile = tmp_path / "original"
    saved = _run_worker(profile, "save")
    restored = _run_worker(profile, "restore", saved["checkpoint_id"])
    assert restored["pid"] != saved["pid"]
    assert restored["memory_id"] == saved["memory_id"]
    assert restored["moment_ids"] == saved["moment_ids"]
    assert restored["prediction_ids"] == saved["prediction_ids"]
    assert restored["chain_ids"] == saved["chain_ids"]
    assert restored["state_digest"] == saved["state_digest"]
    assert restored["new_moment_id"] not in saved["moment_ids"]
    assert restored["moments_processed"] == saved["moments_processed"] + 1
    assert restored["integrated_ids"] == list(reversed(saved["moment_ids"]))
    missing = _run_worker(tmp_path / "separate", "missing", saved["checkpoint_id"])
    assert missing["moments"] == 0
    assert missing["error"] == "temporal_checkpoint_missing_unreadable_or_ambiguous"


def test_real_memory_read_failure_is_not_successful_empty_restore(tmp_path):
    saved = _run_worker(tmp_path, "save")
    failed = _run_worker(tmp_path, "unreadable", saved["checkpoint_id"])
    assert failed["error"] == "temporal_checkpoint_missing_unreadable_or_ambiguous"
    assert failed["moments"] == 0


async def _worker(mode, handle):
    # Aetherra imports
    from Aetherra.aetherra_core.memory.memory_core import LyrixaMemorySystem
    from Aetherra.consciousness.quantum.temporal_consciousness_system import (
        TemporalConsciousnessEngine,
        TemporalPersistenceError,
    )

    memory = LyrixaMemorySystem("memory.db")
    try:
        engine = TemporalConsciousnessEngine(memory_system=memory, clock=lambda: NOW)
        if mode == "save":
            engine.temporal_window = timedelta(hours=12)
            for i in range(3):
                await engine.process_temporal_moment(
                    {"energy": 3, "nested": {"label": "synthetic"}},
                    NOW - timedelta(minutes=3 - i),
                )
            prediction = await engine.predict_future_state(
                NOW + timedelta(minutes=10), {"energy": 3}
            )
            await engine.validate_prediction_accuracy(
                prediction.prediction_id, {"energy": 3}
            )
            handle = await engine.save_checkpoint()
            rows = await memory.recall_memories(
                "", limit=2, memory_type="temporal_checkpoint:" + handle
            )
            assert len(rows) == 1
            receipt = {"memory_id": rows[0].id}
        elif mode in {"missing", "unreadable"}:
            if mode == "unreadable":
                memory.ensure_connection().execute("DROP TABLE memories")
                memory.ensure_connection().commit()
            try:
                await engine.restore_checkpoint(handle)
            except TemporalPersistenceError as exc:
                return {"error": str(exc), "moments": len(engine.temporal_moments)}
            raise AssertionError("missing/unreadable checkpoint accepted")
        else:
            assert not engine.temporal_moments
            receipt = await engine.restore_checkpoint(handle)
        digest = hashlib.sha256(
            json.dumps(engine._checkpoint(handle), sort_keys=True).encode()
        ).hexdigest()
        result = {
            "pid": os.getpid(),
            "checkpoint_id": handle,
            "memory_id": receipt["memory_id"],
            "moment_ids": list(engine.temporal_moments),
            "prediction_ids": list(engine.temporal_predictions),
            "chain_ids": list(engine.causal_chains),
            "state_digest": digest,
        }
        assert engine.causal_chains
        assert engine.temporal_window == timedelta(hours=12)
        assert engine.prediction_accuracy_history == [1.0]
        if mode == "restore":
            integration = await engine.temporal_memory_integration(NOW, {"energy": 3})
            assert integration["integrated_state"]["nested"]["label"] == "synthetic"
            assert integration["integrated_state"]["energy"] == pytest.approx(3)
            result["integrated_ids"] = integration["contributing_moments"]
            result["new_moment_id"] = await engine.process_temporal_moment(
                {"energy": 4}, NOW
            )
        result["moments_processed"] = engine.moments_processed
        return result
    finally:
        memory.close()


if __name__ == "__main__":
    print(json.dumps(asyncio.run(_worker(sys.argv[1], sys.argv[2]))))
