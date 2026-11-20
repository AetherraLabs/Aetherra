# Standard library imports
import json
from pathlib import Path
from threading import Event, Thread, current_thread
from types import SimpleNamespace

# Third party imports
import pytest

# Aetherra imports
import aetherra_coding.orchestrator as module
from aetherra_coding import CodeOrchestrator, ops_engine


@pytest.fixture
def coding_workspace(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("AETHERRA_MODE", "assist")
    monkeypatch.setenv("AETHERRA_AUDIT", "1")
    monkeypatch.setenv("AETHERRA_AUDIT_PATH", str(tmp_path / "audit/events.jsonl"))
    return CodeOrchestrator(repo_root=tmp_path)


@pytest.mark.parametrize("operation", ["patch", "scaffold"])
def test_snapshot_failure_reports_changed_files_without_token(
    coding_workspace, monkeypatch, operation
):
    orchestrator = coding_workspace
    original_open = Path.open

    def denied(path, *args, **kwargs):
        if path.parent == orchestrator._rollback_store:
            raise PermissionError("private storage detail")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied)
    if operation == "patch":
        target = orchestrator.repo_root / "synthetic.txt"
        result = orchestrator.apply_patch(
            ops_engine.build_new_file_diff(target, "synthetic"), colorize=False
        )
    else:
        target = orchestrator.repo_root / "plugins/sample/sample.py"
        result = orchestrator.scaffold_plugin("sample")
    assert result.applied is True
    assert target.exists()
    assert result.rollback_token is None
    assert any("rollback" in item.lower() for item in result.diagnostics)
    assert all("private storage detail" not in item for item in result.diagnostics)
    if operation == "scaffold":
        events = [
            json.loads(line)
            for line in (orchestrator.repo_root / "audit/events.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
        ]
        event = next(item for item in events if item["event"] == "plugin_scaffold")
        assert event["data"]["token"] is None


def test_invalid_snapshot_metadata_cannot_advertise_a_token(
    coding_workspace, monkeypatch
):
    original_apply = ops_engine.apply_unified_diff

    def malformed(*args, **kwargs):
        result = original_apply(*args, **kwargs)
        for metadata in result.originals.values():
            metadata["content"] = object()
        return result

    monkeypatch.setattr(ops_engine, "apply_unified_diff", malformed)
    target = coding_workspace.repo_root / "synthetic.txt"
    result = coding_workspace.apply_patch(
        ops_engine.build_new_file_diff(target, "synthetic"), colorize=False
    )
    assert result.applied is True
    assert target.read_text(encoding="utf-8") == "synthetic\n"
    assert result.rollback_token is None
    assert any("rollback" in item.lower() for item in result.diagnostics)


def test_repeated_patch_receipts_survive_a_new_orchestrator(coding_workspace):
    target = coding_workspace.repo_root / "synthetic.txt"
    target.write_text("original\n", encoding="utf-8")
    first = coding_workspace.apply_patch(
        ops_engine.build_comment_insertion_diff(target, "first"), colorize=False
    )
    after_first = target.read_text(encoding="utf-8")
    second = coding_workspace.apply_patch(
        ops_engine.build_comment_insertion_diff(target, "second"), colorize=False
    )
    assert first.rollback_token
    assert second.rollback_token
    assert first.rollback_token != second.rollback_token
    restarted = CodeOrchestrator(repo_root=coding_workspace.repo_root)
    assert restarted.revert(second.rollback_token).applied is True
    assert target.read_text(encoding="utf-8") == after_first
    assert restarted.revert(first.rollback_token).applied is True
    assert target.read_text(encoding="utf-8") == "original\n"


def test_same_second_scaffolds_have_distinct_receipts(coding_workspace, monkeypatch):
    monkeypatch.setattr(module.time, "time", lambda: 1700000000)
    first = coding_workspace.scaffold_plugin("first")
    second = coding_workspace.scaffold_plugin("second")
    assert first.rollback_token
    assert second.rollback_token
    assert first.rollback_token != second.rollback_token
    assert coding_workspace.revert(second.rollback_token).applied is True
    assert (coding_workspace.repo_root / "plugins/first/first.py").exists()
    assert not (coding_workspace.repo_root / "plugins/second/second.py").exists()
    assert coding_workspace.revert(first.rollback_token).applied is True
    assert not (coding_workspace.repo_root / "plugins/first/first.py").exists()


def test_scaffold_rollback_restores_a_preexisting_test(coding_workspace):
    test_file = coding_workspace.repo_root / "tests/plugins/test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("original test\n", encoding="utf-8")
    result = coding_workspace.scaffold_plugin("sample")
    assert result.rollback_token
    assert coding_workspace.revert(result.rollback_token).applied is True
    assert test_file.read_text(encoding="utf-8") == "original test\n"


@pytest.mark.parametrize("existing", [False, True])
def test_scaffold_rollback_restores_registration_state(coding_workspace, existing):
    registry = (
        coding_workspace.repo_root / "Aetherra/plugins/core/registered_plugins.json"
    )
    original = '{"plugins": ["existing"]}\n'
    if existing:
        registry.parent.mkdir(parents=True)
        registry.write_text(original, encoding="utf-8")
    result = coding_workspace.scaffold_plugin("sample")
    assert result.rollback_token
    assert coding_workspace.revert(result.rollback_token).applied is True
    if existing:
        assert registry.read_text(encoding="utf-8") == original
    else:
        assert not registry.exists()


def test_stale_scaffold_rollback_does_not_erase_later_registration(coding_workspace):
    first = coding_workspace.scaffold_plugin("first")
    second = coding_workspace.scaffold_plugin("second")
    assert first.rollback_token
    assert second.rollback_token
    registry = (
        coding_workspace.repo_root / "Aetherra/plugins/core/registered_plugins.json"
    )
    before = registry.read_text(encoding="utf-8")
    result = coding_workspace.revert(first.rollback_token)
    assert result.applied is False
    assert registry.read_text(encoding="utf-8") == before
    assert (coding_workspace.repo_root / "plugins/first/first.py").exists()
    assert (coding_workspace.repo_root / "plugins/second/second.py").exists()


def test_scaffold_preimage_failure_precedes_file_writes(coding_workspace, monkeypatch):
    test_file = coding_workspace.repo_root / "tests/plugins/test_sample.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("original test", encoding="utf-8")
    original_read = Path.read_text

    def denied(path, *args, **kwargs):
        if path == test_file:
            raise PermissionError("synthetic preimage denial")
        return original_read(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(PermissionError, match="synthetic preimage denial"):
        coding_workspace.scaffold_plugin("sample")
    assert not (coding_workspace.repo_root / "plugins/sample/sample.py").exists()
    assert not (coding_workspace.repo_root / "plugins/sample/plugin.json").exists()


@pytest.mark.parametrize("failure", ["exception", "short_write"])
def test_failed_registry_write_cannot_advertise_rollback(
    coding_workspace, monkeypatch, failure
):
    registry = (
        coding_workspace.repo_root / "Aetherra/plugins/core/registered_plugins.json"
    )
    original_write = Path.write_text

    def incomplete(path, contents, *args, **kwargs):
        if path == registry:
            count = original_write(path, contents[:3], *args, **kwargs)
            if failure == "exception":
                raise OSError("private registry write detail")
            return count
        return original_write(path, contents, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", incomplete)
    result = coding_workspace.scaffold_plugin("sample")
    assert result.applied is True
    assert result.rollback_token is None
    assert any("rollback" in item.lower() for item in result.diagnostics)
    assert all(
        "private registry write detail" not in item for item in result.diagnostics
    )


@pytest.mark.parametrize("failure", ["short_write", "fsync", "publish"])
def test_failed_atomic_snapshot_has_no_receipt_or_partial_file(
    coding_workspace, monkeypatch, failure
):
    if failure == "short_write":
        original_open = Path.open

        class ShortWriter:
            def __init__(self, stream):
                self.stream = stream

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return self.stream.__exit__(*args)

            def write(self, contents):
                return self.stream.write(contents[:-1])

        def shortened(path, *args, **kwargs):
            stream = original_open(path, *args, **kwargs)
            if path.parent == coding_workspace._rollback_store:
                return ShortWriter(stream)
            return stream

        monkeypatch.setattr(Path, "open", shortened)
    elif failure == "fsync":

        def denied_sync(*args):
            raise OSError("private synchronization detail")

        monkeypatch.setattr(module.os, "fsync", denied_sync)
    else:
        original_replace = Path.replace

        def denied_publish(path, target):
            if path.parent == coding_workspace._rollback_store:
                raise PermissionError("private publication detail")
            return original_replace(path, target)

        monkeypatch.setattr(Path, "replace", denied_publish)
    target = coding_workspace.repo_root / "synthetic.txt"
    result = coding_workspace.apply_patch(
        ops_engine.build_new_file_diff(target, "synthetic"), colorize=False
    )
    assert result.applied is True
    assert target.read_text(encoding="utf-8") == "synthetic\n"
    assert result.rollback_token is None
    assert list(coding_workspace._rollback_store.iterdir()) == []


def test_unowned_pending_snapshot_is_not_deleted(coding_workspace, monkeypatch):
    monkeypatch.setattr(module, "uuid4", lambda: SimpleNamespace(hex="fixed"))
    target = coding_workspace.repo_root / "synthetic.txt"
    candidate = f"{ops_engine._make_rollback_token([target])}-fixed"
    pending = coding_workspace._rollback_store / f".{candidate}.tmp"
    pending.write_text("owned by another operation", encoding="utf-8")
    result = coding_workspace.apply_patch(
        ops_engine.build_new_file_diff(target, "synthetic"), colorize=False
    )
    assert result.applied is True
    assert result.rollback_token is None
    assert pending.read_text(encoding="utf-8") == "owned by another operation"


def test_legacy_receipt_remains_usable(coding_workspace):
    target = coding_workspace.repo_root / "synthetic.txt"
    target.write_text("changed", encoding="utf-8")
    snapshot = coding_workspace._rollback_store / "legacy.json"
    snapshot.write_text(
        json.dumps({"synthetic.txt": {"content": "original", "existed": True}}),
        encoding="utf-8",
    )
    assert coding_workspace.revert("legacy").applied is True
    assert target.read_text(encoding="utf-8") == "original"


def test_snapshot_publication_cannot_clobber_a_concurrent_receipt(
    coding_workspace, monkeypatch
):
    monkeypatch.setattr(module, "uuid4", lambda: SimpleNamespace(hex="race"))
    checked = Event()
    resume = Event()
    original_exists = Path.exists
    results = {}
    failures = []
    original_a = {"synthetic.txt": {"content": "A", "existed": True}}
    original_b = {"synthetic.txt": {"content": "B", "existed": True}}

    def pause_after_check(path):
        exists = original_exists(path)
        if path.name == "same-race.json" and current_thread().name == "snapshot-B":
            checked.set()
            if not resume.wait(timeout=3):
                raise RuntimeError("test synchronization timed out")
        return exists

    def publish_b():
        try:
            results["B"] = coding_workspace._persist_rollback_snapshot(
                "same", original_b
            )
        except Exception as exc:
            failures.append(exc)

    monkeypatch.setattr(Path, "exists", pause_after_check)
    writer = Thread(target=publish_b, name="snapshot-B")
    writer.start()
    try:
        assert checked.wait(timeout=3)
        results["A"] = coding_workspace._persist_rollback_snapshot("same", original_a)
    finally:
        resume.set()
        writer.join(timeout=5)
    assert not writer.is_alive()
    assert failures == []
    committed = {owner: token for owner, token in results.items() if token is not None}
    assert len(committed) == 1
    owner, token = next(iter(committed.items()))
    saved = json.loads(
        (coding_workspace._rollback_store / f"{token}.json").read_text(encoding="utf-8")
    )
    assert saved == (original_a if owner == "A" else original_b)
