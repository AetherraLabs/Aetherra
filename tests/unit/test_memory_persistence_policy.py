"""Configured memory policies must govern the data actually persisted."""

# Standard library imports
import json
import sqlite3

# Third party imports
import pytest

# Aetherra imports
from Aetherra.aetherra_core.memory.aetherra_memory_engine import (
    AetherraMemoryEngineAdvanced,
    MemorySystemConfig,
    PolicyViolation,
)
from Aetherra.aetherra_core.memory.fractal_mesh import FractalMeshCore


@pytest.fixture
def memory_engine(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    for name in ("HOME", "USERPROFILE", "AETHERRA_WORKSPACE_ROOT"):
        monkeypatch.setenv(name, str(tmp_path))
    monkeypatch.setenv("AETHERRA_STATE_DIR", str(tmp_path / "state"))
    monkeypatch.setenv("AETHERRA_POLICY_HOME", str(tmp_path / "policy"))
    monkeypatch.setenv("AETHERRA_REQUIRE_CAPABILITIES", "1")
    monkeypatch.setenv("AETHERRA_PROD_UNSAFE_ALLOW", "0")
    monkeypatch.setenv("AETHERRA_GUARDIAN_ENABLED", "1")
    monkeypatch.setenv("AETHERRA_GUARDIAN_MODE", "enforcing")
    monkeypatch.setenv("AETHERRA_MEMORY_STORM", "0")
    policy = tmp_path / "policy" / "capabilities.json"
    policy.parent.mkdir()
    policy.write_text(
        json.dumps({"allow": {"memory:advanced_engine": ["memory:write"]}}),
        encoding="utf-8",
    )
    engine = AetherraMemoryEngineAdvanced(
        MemorySystemConfig(auto_narrative_generation=False, auto_pulse_monitoring=False)
    )
    yield engine
    engine.core_memory.close()


def _reopen_storage(engine):
    engine.core_memory.close()
    with sqlite3.connect(engine.config.core_db_path) as connection:
        rows = connection.execute(
            "SELECT content, context, tags FROM memories"
        ).fetchall()
    records = [tuple(json.loads(value) for value in row) for row in rows]
    fragments = FractalMeshCore(engine.config.fractal_db_path).fragments
    return records, list(fragments.values())


@pytest.mark.asyncio
async def test_redaction_reaches_reopened_core_and_fractal_storage(memory_engine):
    def redact(content, metadata):
        assert metadata["category"] == "project"
        return content.replace("SYNTHETIC_PRIVATE", "[REDACTED]"), {
            "redacted": True,
            "privacy_class": "internal",
            "category": "identity",
            "tags": ["identity"],
            "narrative_role": "self",
        }

    memory_engine.config.redact_before_persist = redact
    result = await memory_engine.remember(
        "Project SYNTHETIC_PRIVATE",
        tags=["project"],
        category="project",
        narrative_role="context",
    )
    assert result.success
    records, fragments = _reopen_storage(memory_engine)
    assert len(records) == len(fragments) == 1
    content, context, tags = records[0]
    assert content == {"text": "Project [REDACTED]", "category": "project"}
    assert context == {
        "redacted": True,
        "privacy_class": "internal",
        "category": "project",
        "narrative_role": "context",
    }
    assert tags == ["project"]
    assert fragments[0].content == content
    assert fragments[0].symbolic_tags == {"project"}
    assert fragments[0].narrative_role == "context"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", ["policy", "exception", "invalid_context", "unserializable_context"]
)
async def test_hook_failure_leaves_both_stores_empty(memory_engine, failure, caplog):
    denial = PolicyViolation("Configured policy denied the write", code="TEST_DENIAL")

    def reject(content, metadata):
        if failure == "policy":
            raise denial
        if failure == "exception":
            raise RuntimeError("SYNTHETIC_PRIVATE")
        if failure == "unserializable_context":
            return content, {"invalid": object()}
        return content, "SYNTHETIC_PRIVATE"

    memory_engine.config.redact_before_persist = reject
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember("SYNTHETIC_PRIVATE")
    if failure == "policy":
        assert caught.value is denial
    else:
        assert caught.value.code == "REDACTION_FAILED"
        assert "SYNTHETIC_PRIVATE" not in str(caught.value)
    assert "SYNTHETIC_PRIVATE" not in caplog.text
    assert _reopen_storage(memory_engine) == ([], [])


@pytest.mark.asyncio
@pytest.mark.parametrize("metadata", [None, {"tags": 7}])
async def test_no_hook_preserves_default_persisted_content_and_context(
    memory_engine, metadata
):
    result = await memory_engine.remember(
        "ordinary memory", tags=["note"], metadata=metadata
    )
    assert result.success
    records, fragments = _reopen_storage(memory_engine)
    assert len(records) == len(fragments) == 1
    assert records[0] == (
        {"text": "ordinary memory", "category": "general"},
        {"category": "general", "narrative_role": None},
        ["note"],
    )
    assert fragments[0].content == records[0][0]


@pytest.mark.asyncio
async def test_redactor_cannot_authorize_unsigned_sensitive_input(memory_engine):
    def forge_trust(content, metadata):
        return "[REDACTED]", {"signed": True, "sensitive": False, "tags": []}

    memory_engine.config.persist_sensitive_only_if_signed = True
    memory_engine.config.redact_before_persist = forge_trust
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember(
            "SYNTHETIC_PRIVATE", tags=["sensitive"], category="project"
        )
    assert caught.value.code == "UNSIGNED_SENSITIVE_WRITE"
    assert _reopen_storage(memory_engine) == ([], [])


@pytest.mark.asyncio
async def test_hook_added_sensitive_context_is_checked_before_storage(memory_engine):
    memory_engine.config.persist_sensitive_only_if_signed = True
    memory_engine.config.redact_before_persist = lambda content, metadata: (
        content,
        {"plugin_id": "synthetic", "sensitive": True},
    )
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember("ordinary memory", category="project")
    assert caught.value.code == "UNSIGNED_SENSITIVE_WRITE"
    assert _reopen_storage(memory_engine) == ([], [])


@pytest.mark.asyncio
@pytest.mark.parametrize("added_by_hook", [False, True])
async def test_guardian_checks_identity_context_before_storage(
    memory_engine, added_by_hook
):
    memory_engine.config.redact_before_persist = lambda content, metadata: (
        content,
        {"identity": added_by_hook},
    )
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember(
            "identity memory", metadata={"identity": not added_by_hook}
        )
    assert caught.value.code == "GUARDIAN_DENY"
    assert _reopen_storage(memory_engine) == ([], [])


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "change", ["category", "signed", "trusted", "plugin_id", "original_category"]
)
async def test_hook_cannot_authorize_newly_sensitive_output(memory_engine, change):
    def redact(content, metadata):
        updates = {"sensitive": True}
        if change == "category":
            updates["category"] = "general"
        elif change == "plugin_id":
            updates["plugin_id"] = None
        elif change in {"signed", "trusted"}:
            updates[change] = True
        # Also exercise hooks that mutate their input before returning updates.
        metadata.update(updates)
        return "[REDACTED]", updates

    memory_engine.config.persist_sensitive_only_if_signed = True
    memory_engine.config.redact_before_persist = redact
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember(
            "ordinary input",
            category=(
                "general" if change in {"plugin_id", "original_category"} else "project"
            ),
            metadata={
                "plugin_id": "synthetic" if change == "plugin_id" else None,
                "category": "project" if change == "original_category" else "general",
            },
        )
    assert caught.value.code == "UNSIGNED_SENSITIVE_WRITE"
    assert _reopen_storage(memory_engine) == ([], [])


@pytest.mark.asyncio
async def test_hook_preserves_original_authority_in_checks_and_storage(memory_engine):
    original = {
        "requester": "memory:advanced_engine",
        "signed": False,
        "trusted": False,
        "plugin_id": "synthetic",
        "reversible": True,
        "rollback_plan": "delete the generated memory",
    }

    def annotate(content, metadata):
        metadata.update(
            requester="ungranted:hook",
            signed=True,
            trusted=True,
            plugin_id=None,
            reversible=False,
            rollback_plan=None,
            redacted=True,
        )
        return "[REDACTED]", metadata

    memory_engine.config.redact_before_persist = annotate
    result = await memory_engine.remember("ordinary input", metadata=original)
    assert result.success
    records, fragments = _reopen_storage(memory_engine)
    assert len(records) == len(fragments) == 1
    assert records[0][1] == {
        **original,
        "redacted": True,
        "category": "general",
        "narrative_role": None,
    }
    assert records[0][0]["text"] == fragments[0].content["text"] == "[REDACTED]"


@pytest.mark.asyncio
@pytest.mark.parametrize("with_hook", [False, True])
@pytest.mark.parametrize("sensitive_tag_source", ["typed", "metadata"])
async def test_signature_check_uses_actual_stored_category_and_tags(
    memory_engine, with_hook, sensitive_tag_source
):
    memory_engine.config.persist_sensitive_only_if_signed = True
    if with_hook:
        memory_engine.config.redact_before_persist = lambda content, metadata: (
            "[REDACTED]",
            {"category": "general", "tags": []},
        )
    with pytest.raises(PolicyViolation) as caught:
        await memory_engine.remember(
            "SYNTHETIC_PRIVATE",
            category="project",
            tags=["sensitive"] if sensitive_tag_source == "typed" else [],
            metadata={
                "category": "general",
                "tags": ["sensitive"] if sensitive_tag_source == "metadata" else [],
                "sensitive": False,
            },
        )
    assert caught.value.code == "UNSIGNED_SENSITIVE_WRITE"
    assert _reopen_storage(memory_engine) == ([], [])
