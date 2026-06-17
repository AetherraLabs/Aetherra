# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors

# Third party imports
import json

import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
    MemorySystemConfig,
)
from Aetherra.aetherra_core.memory.models import MemoryRecallResult, PolicyViolation


def _memory_config(tmp_path, **overrides):
    values = {
        "core_db_path": str(tmp_path / "lyrixa_memory.db"),
        "fractal_db_path": str(tmp_path / "fractal_memory.db"),
        "concepts_db_path": str(tmp_path / "concept_clusters.db"),
        "timeline_db_path": str(tmp_path / "episodic_timeline.db"),
        "pulse_db_path": str(tmp_path / "memory_pulse.db"),
        "reflector_db_path": str(tmp_path / "memory_reflector.db"),
    }
    values.update(overrides)
    return MemorySystemConfig(**values)


@pytest.mark.asyncio
async def test_recall_typed_returns_memory_recall_result(tmp_path):
    engine = AetherraMemoryEngineAdvanced(config=_memory_config(tmp_path))
    # seed some memories via compat path on simple adapter on Advanced engine
    await engine.remember("alpha test memory", tags=["alpha"], category="test")
    await engine.remember("beta test memory", tags=["beta"], category="test")

    result = await engine.recall_typed("test")
    assert isinstance(result, MemoryRecallResult)
    assert isinstance(result.items, list)
    assert len(result.items) > 0
    assert isinstance(result.scores, list)
    assert len(result.scores) == len(result.items)


@pytest.mark.asyncio
async def test_policy_violation_blocks_unsigned_sensitive_plugin_output(tmp_path):
    cfg = _memory_config(tmp_path, persist_sensitive_only_if_signed=True)
    engine = AetherraMemoryEngineAdvanced(config=cfg)

    # Attempt to persist content flagged as sensitive and plugin-originated without signature
    with pytest.raises(PolicyViolation):
        await engine.remember(
            content={"text": "secret from plugin"},
            tags=["sensitive"],
            category="project",
            narrative_role=None,
        )


@pytest.mark.asyncio
async def test_remember_writes_guardian_audit(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    engine = AetherraMemoryEngineAdvanced(config=_memory_config(tmp_path))

    result = await engine.remember(
        "project plan memory",
        tags=["project"],
        category="project",
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    entries = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert result.success is True
    assert entries[-1]["event_type"] == "guardian_decision"
    assert entries[-1]["details"]["intent"]["action"] == "memory.remember"
    assert entries[-1]["details"]["intent"]["target"] == "memory:project"


@pytest.mark.asyncio
async def test_remember_blocked_by_guardian_missing_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    engine = AetherraMemoryEngineAdvanced(config=_memory_config(tmp_path))

    with pytest.raises(PolicyViolation) as exc_info:
        await engine.remember("blocked memory", tags=["project"], category="project")

    assert exc_info.value.code == "GUARDIAN_DENY"
    assert "missing_capability" in str(exc_info.value)


@pytest.mark.asyncio
async def test_guardian_audit_does_not_store_memory_content(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    engine = AetherraMemoryEngineAdvanced(config=_memory_config(tmp_path))

    result = await engine.remember(
        "private memory content secret-value",
        tags=["project"],
        category="project",
    )
    audit_path = tmp_path / ".aetherra" / "security" / "audit.jsonl"
    ledger_text = audit_path.read_text(encoding="utf-8")

    assert result.success is True
    assert "private memory content secret-value" not in ledger_text
    assert "memory:project" in ledger_text


@pytest.mark.asyncio
async def test_identity_memory_write_is_contained_by_guardian(monkeypatch, tmp_path):
    monkeypatch.setenv("AETHERRA_WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    engine = AetherraMemoryEngineAdvanced(config=_memory_config(tmp_path))

    with pytest.raises(PolicyViolation) as exc_info:
        await engine.remember(
            "identity-shaping memory",
            tags=["identity"],
            category="identity",
        )

    assert exc_info.value.code == "GUARDIAN_CONTAIN"
    assert "critical_risk_requires_containment" in str(exc_info.value)
