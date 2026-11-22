"""Recall routing and manual-probe collection must preserve caller choices."""

# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("enabled", "shadow"), [(False, False), (True, False), (True, True)]
)
@pytest.mark.parametrize("strategy", ["base", "storm_hybrid", "storm", "hybrid", None])
async def test_recall_strategy_routes_persisted_memories(
    monkeypatch, tmp_path, enabled, shadow, strategy
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_MEMORY_STORM", "1" if enabled else "0")
    monkeypatch.setenv("AETHERRA_STORM_SHADOW_MODE", "1" if shadow else "0")
    monkeypatch.setenv("AETHERRA_STORM_SQLITE_PATH", str(tmp_path / "storm.db"))
    engine = AetherraMemoryEngineAdvanced()
    try:
        memory_id = await engine.core_memory.store_memory(
            {"text": "strategy alpha"}, importance=0.9
        )
        assert memory_id
        assert await engine.core_memory.store_memory(
            {"text": "strategy beta"}, importance=0.2
        )
        # Reopen SQLite so results must come from persisted rows, not the write cache.
        engine.core_memory.close()
        kwargs = {} if strategy is None else {"recall_strategy": strategy}
        result = await engine.recall_typed("strategy", limit=1, **kwargs)

        if enabled and not shadow and strategy == "storm":
            assert result.source == "storm"
            assert "storm_meta" in result.metadata
        else:
            expected_source = (
                "storm_hybrid"
                if enabled and not shadow and strategy != "base"
                else "hybrid"
            )
            assert result.source == expected_source
            assert len(result.items) == 1
            assert result.items[0]["content"] == {"text": "strategy alpha"}
            assert result.items[0]["memory_id"] == memory_id
        if strategy == "base":
            assert "storm_meta" not in result.metadata
    finally:
        engine.core_memory.close()
        if (
            engine._storm_engine is not None
            and engine._storm_engine._storage is not None
        ):
            engine._storm_engine._storage.close()


@pytest.mark.parametrize("probe", ["storm_skeleton_probe.py", "storm_canary_probe.py"])
def test_manual_storm_probe_import_does_not_change_environment(tmp_path, probe):
    # Supply only test configuration to the child, so assertion output cannot expose
    # credentials inherited by the parent process.
    env = {
        "PATH": os.defpath,
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "PYTHONPATH": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "HOME": str(tmp_path),
        "USERPROFILE": str(tmp_path),
        "AETHERRA_WORKSPACE_ROOT": str(tmp_path),
        "AETHERRA_SKIP_DOTENV": "1",
        "AETHERRA_MEMORY_STORM": "0",
        "AETHERRA_STORM_CANARY_PCT": "0",
    }
    script = """
import contextlib
import io
import json
import os
import runpy
import sys
from pathlib import Path

before = dict(os.environ)
output = io.StringIO()
with contextlib.redirect_stdout(output):
    runpy.run_path(sys.argv[1], run_name="storm_probe_collection")
changed = sorted(
    key for key in before.keys() | os.environ.keys()
    if before.get(key) != os.environ.get(key)
)
print(json.dumps({
    "changed_keys": changed,
    "created_files": sorted(p.name for p in Path.cwd().iterdir()),
    "printed_output": bool(output.getvalue()),
}))
"""
    result = subprocess.run(
        [sys.executable, "-B", "-c", script, str(ROOT / "tests/storm/manual" / probe)],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)
    assert report == {"changed_keys": [], "created_files": [], "printed_output": False}
