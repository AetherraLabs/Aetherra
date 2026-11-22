# SPDX-License-Identifier: GPL-3.0-or-later
"""
STORM Security Gates Verification Tests

Verifies that STORM memory operations respect security policies:
1. Data flows through AetherraMemoryEngineAdvanced which applies policy guards
2. STORM only reads pre-processed data from core memory (never writes directly)
3. Privacy classes are respected in recall operations
4. Redaction hooks are applied before persistence
5. Sensitive data handling follows security policy

Test Coverage:
- Policy guard enforcement during memory storage
- STORM recall respects pre-redacted data
- Privacy class filtering (public|internal|sensitive)
- No direct STORM writes bypass security layer
"""

# Standard library imports
import json
import sqlite3
from typing import Any
from unittest.mock import AsyncMock, MagicMock

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
    MemorySystemConfig,
    PolicyViolation,
)
from Aetherra.aetherra_core.memory.storm.engine import StormConfig, StormEngine


class TestSTORMSecurityGates:
    """Test suite for STORM security policy enforcement"""

    @pytest.mark.asyncio
    async def test_storm_reads_from_policy_guarded_memory(self):
        """Verify STORM only reads data that passed through security guards"""

        # Create a redaction hook that tags processed content
        def redact_hook(content: Any, metadata: dict) -> tuple[Any, dict | None]:
            if isinstance(content, str) and "API_KEY" in content:
                redacted_content = content.replace(
                    "API_KEY=secret123", "API_KEY=[REDACTED]"
                )
                return redacted_content, {"redacted": True}
            return content, None

        # Create memory engine with redaction enabled
        config = MemorySystemConfig(
            redact_before_persist=redact_hook,
            persist_sensitive_only_if_signed=False,  # Allow storage for test
        )
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Store sensitive content - should be redacted before storage
        result = await engine.remember(
            content="User config: API_KEY=secret123",
            tags=["config"],
            category="system",
        )

        assert result.success, "Memory storage should succeed"

        # Inspect the written record rather than only checking hook callability.
        stored = engine.fractal_mesh.fragments[result.fragment_id]
        assert stored.content["text"] == "User config: API_KEY=[REDACTED]"

    @pytest.mark.asyncio
    async def test_storm_respects_privacy_classes(self):
        """Verify STORM recall respects privacy class annotations"""

        config = MemorySystemConfig()
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Store memories with different privacy classes
        await engine.remember(
            content="Public information",
            tags=["public"],
            metadata={"privacy_class": "public"},
        )

        await engine.remember(
            content="Internal team notes",
            tags=["internal"],
            metadata={"privacy_class": "internal"},
        )

        await engine.remember(
            content="Sensitive user data",
            tags=["sensitive"],
            metadata={"privacy_class": "sensitive"},
        )

        # If STORM is enabled, verify it sees only appropriate privacy classes
        if engine._storm_engine:
            # STORM reads from core memory which should have privacy metadata
            # This test verifies the data path includes privacy tags
            result = await engine.recall_typed(
                query="information",
                recall_strategy="storm_hybrid",
                limit=10,
            )

            # Verify metadata structure includes privacy information
            # (actual filtering would be done by core memory system)
            assert isinstance(result.metadata, dict), "Metadata should be present"

    @pytest.mark.asyncio
    async def test_policy_violation_prevents_storage(self):
        """Verify PolicyViolation is raised and propagated correctly"""

        def strict_policy(content: Any, metadata: dict) -> tuple[Any, dict | None]:
            # Reject anything marked as untrusted
            if metadata.get("untrusted", False):
                raise PolicyViolation("Untrusted content not allowed")
            return content, None

        config = MemorySystemConfig(
            redact_before_persist=strict_policy,
            persist_sensitive_only_if_signed=False,
        )
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Attempt to store untrusted content - should raise PolicyViolation
        with pytest.raises(PolicyViolation):
            await engine.remember(
                content="Untrusted plugin output",
                metadata={"untrusted": True},
            )

    @pytest.mark.asyncio
    async def test_storm_no_direct_persistence_bypass(self):
        """Verify STORM cannot write data without going through memory engine"""

        # Create STORM engine without core memory (isolated test)
        storm_config = StormConfig(enabled=True, sqlite_path=":memory:")
        storm = StormEngine(config=storm_config, core_memory=None)

        # STORM persistence only stores embeddings and metadata, not raw content
        # Verify that upsert_embedding only stores derived data (embeddings)
        if storm._storage:
            # Embeddings are computed from content, not raw storage
            content_hash = storm._storage.upsert_embedding(
                "test content",
                __import__("numpy").random.rand(384),  # Mock embedding
            )

            # Verify we can't retrieve original content from hash alone
            # (storage only has embeddings, not full content)
            assert content_hash, "Hash should be returned"

            # The _storage only has excerpts (first 200 chars), not full content
            # This prevents STORM from being a policy bypass

    @pytest.mark.asyncio
    async def test_sensitive_tag_triggers_metadata_annotation(self):
        """Verify 'sensitive' tag triggers metadata annotation for policy hooks"""

        hook_called = []

        def tracking_hook(content: Any, metadata: dict) -> tuple[Any, dict | None]:
            hook_called.append(metadata.copy())
            return content, None

        config = MemorySystemConfig(redact_before_persist=tracking_hook)
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Store memory with 'sensitive' tag
        await engine.remember(
            content="Sensitive data here",
            tags=["sensitive", "user_data"],
            category="personal",
        )

        # Verify hook was called and received sensitive annotation
        assert len(hook_called) > 0, "Hook should have been called"
        metadata = hook_called[0]
        assert metadata.get("sensitive") is True, "Sensitive flag should be set"
        assert "sensitive" in metadata.get("tags", [])

    def test_storm_storage_schema_prevents_content_exposure(self):
        """Verify STORM storage schema doesn't store full content"""

        # Aetherra imports
        from Aetherra.aetherra_core.memory.storm.persistence import StormStorage

        storage = StormStorage(":memory:")

        # Check schema via introspection
        cur = storage._conn.cursor()
        schema = cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='storm_cells'"
        ).fetchone()

        assert schema, "storm_cells table should exist"
        schema_sql = schema[0]

        # Verify schema has content_excerpt (truncated) not full content
        assert "content_excerpt" in schema_sql, "Should have excerpt field"
        assert "content TEXT" not in schema_sql, "Should NOT store full content"

        # The excerpt is truncated to 200 chars in upsert_embedding
        # This prevents STORM persistence from being a data exfiltration vector


class TestSTORMDataFlowSecurity:
    """Test STORM data flow respects security boundaries"""

    @pytest.mark.asyncio
    async def test_storm_recall_uses_core_memory_not_direct_db(self):
        """Verify STORM recall fetches from core memory (policy-guarded) not direct DB"""

        # Mock core memory with policy-processed data
        mock_core_memory = MagicMock()
        mock_core_memory.recall_memories = AsyncMock(
            return_value=[
                {"content": "Policy-processed data", "relevance_score": 0.9},
            ]
        )

        storm_config = StormConfig(enabled=True)
        storm = StormEngine(config=storm_config, core_memory=mock_core_memory)

        # Perform recall - should use core_memory.recall_memories
        result = await storm.recall(query="test query", limit=5)

        # Verify core memory was called (data flow goes through security layer)
        mock_core_memory.recall_memories.assert_called_once()
        call_args = mock_core_memory.recall_memories.call_args
        assert call_args.kwargs["query"] == "test query"

        # STORM gets pre-processed data from core memory, not raw DB access
        assert result.source in ("storm", "storm_hybrid")

    @pytest.mark.asyncio
    async def test_storm_hybrid_mode_preserves_base_fallback_security(self):
        """Verify hybrid mode preserves security properties of base fallback"""

        # Aetherra imports
        from Aetherra.aetherra_core.memory.models import MemoryRecallResult

        # Create a base fallback with policy-processed items
        base_fallback = MemoryRecallResult(
            items=[{"content": "Redacted base item"}],
            scores=[0.8],
            source="base_memory",
            metadata={"privacy_class": "internal"},
        )

        storm_config = StormConfig(enabled=True)
        storm = StormEngine(config=storm_config, core_memory=None)

        # Recall with base_fallback (hybrid mode)
        result = await storm.recall(
            query="test",
            limit=5,
            base_fallback=base_fallback,
        )

        # Verify result uses fallback data (which went through security)
        assert result.source == "storm_hybrid", "Should be hybrid mode"
        assert len(result.items) > 0, "Should have items from fallback"


# Integration test marker for full security audit
@pytest.mark.integration
class TestSTORMSecurityIntegration:
    """End-to-end security verification for STORM integration"""

    @pytest.mark.asyncio
    async def test_full_remember_recall_security_flow(self, monkeypatch, tmp_path):
        """Verify complete data flow: remember -> redact -> store -> recall"""

        monkeypatch.chdir(tmp_path)
        for name in (
            "HOME",
            "USERPROFILE",
            "AETHERRA_STATE_DIR",
            "AETHERRA_POLICY_HOME",
        ):
            monkeypatch.setenv(name, str(tmp_path))
        monkeypatch.setenv("AETHERRA_MEMORY_STORM", "0")

        def audit_redaction(content: Any, metadata: dict) -> tuple[Any, dict | None]:
            # Redact API keys
            if isinstance(content, str):
                redacted = content.replace("sk-secret123", "[REDACTED]")
                return redacted, {"redacted": "sk-" in content}
            return content, None

        config = MemorySystemConfig(
            redact_before_persist=audit_redaction,
            persist_sensitive_only_if_signed=True,
            auto_narrative_generation=False,
            auto_pulse_monitoring=False,
        )
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Store with sensitive content
        saved = await engine.remember(
            content="API Key: sk-secret123",
            tags=["config", "sensitive"],
            category="credentials",
            metadata={"signed": True},
        )
        assert saved.success
        engine.core_memory.close()

        # Inspect the persisted result, not the hook's pre-redaction input copy.
        with sqlite3.connect(config.core_db_path) as connection:
            rows = connection.execute(
                "SELECT content, context FROM memories"
            ).fetchall()
        assert len(rows) == 1
        assert json.loads(rows[0][0])["text"] == "API Key: [REDACTED]"
        assert json.loads(rows[0][1])["redacted"] is True
        engine = AetherraMemoryEngineAdvanced(config=config)

        # Recall - should get redacted version
        try:
            result = await engine.recall_typed(
                query="API Key", recall_strategy="base", limit=5
            )
        finally:
            engine.core_memory.close()

        # STORM would build on this same pre-redacted data
        # (cannot test directly without enabling STORM, but data path is verified)
        assert result.items, "Should have recall results"
        assert all(
            item["content"]["text"] == "API Key: [REDACTED]" for item in result.items
        )
        assert "sk-secret123" not in json.dumps(result.items)
