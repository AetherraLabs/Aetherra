# Standard library imports
import json
import os
import subprocess
import sys
from pathlib import Path

# Third party imports
import pytest

# Aetherra imports
from tools import verify_docs_consistency as verifier

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "verify_docs_consistency.py"
DEBUG_JSON = ROOT / "docs" / "DOCS_CONSISTENCY_DEBUG.json"


def run(cmd, env=None):
    return subprocess.run(
        [sys.executable, *cmd],
        cwd=ROOT,
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
    )


def test_basic_run_exit_zero():
    r = run([str(SCRIPT)])
    assert (
        r.returncode == 0
    ), f"Non-zero exit code. stdout=\n{r.stdout}\n--- stderr=\n{r.stderr}"


def test_debug_flag_creates_json():
    if DEBUG_JSON.exists():
        DEBUG_JSON.unlink()
    r = run([str(SCRIPT), "--debug"])
    assert r.returncode == 0, "Debug run failed"
    assert DEBUG_JSON.exists(), "Expected debug JSON artifact not created"
    data = json.loads(DEBUG_JSON.read_text())
    # Minimal schema keys
    for key in [
        "timestamp",
        "code_envs_count",
        "doc_envs_count",
        "missing_envs",
        "raw_extra_envs",
        "suppressed_doc_only_envs",
        "extra_envs_reported",
        "code_routes_count",
        "doc_routes_count",
        "missing_routes",
        "extra_routes",
        "missing_consciousness_metrics",
    ]:
        assert key in data, f"Missing key in debug JSON: {key}"


def test_env_var_triggers_debug_json():
    if DEBUG_JSON.exists():
        DEBUG_JSON.unlink()
    env = os.environ.copy()
    env["AETHERRA_DOCS_DEBUG"] = "1"
    r = run([str(SCRIPT)], env=env)
    assert r.returncode == 0, "Env var debug run failed"
    assert DEBUG_JSON.exists(), "Expected debug JSON via env var not created"
    data = json.loads(DEBUG_JSON.read_text())
    assert isinstance(data.get("missing_envs"), list)
    assert isinstance(data.get("extra_routes"), list)


@pytest.mark.parametrize("scanner", ["find_env_vars_in_code", "find_routes_in_code"])
def test_source_read_failure_cannot_produce_clean_inspection(
    tmp_path, monkeypatch, scanner
):
    source = tmp_path / "source.py"
    source.write_text("pass", encoding="utf-8")
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    read_text = Path.read_text

    def read(path, *args, **kwargs):
        if path == source:
            raise OSError("synthetic private failure detail")
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    with pytest.raises(OSError, match="source_file_unreadable"):
        getattr(verifier, scanner)()


@pytest.mark.parametrize("scanner", ["find_env_vars_in_code", "find_routes_in_code"])
def test_directory_read_failure_cannot_produce_clean_inspection(monkeypatch, scanner):
    def unreadable_walk(root, *, onerror=None):
        if onerror is not None:
            onerror(PermissionError("synthetic private directory detail"))
        return iter(())

    monkeypatch.setattr(verifier.os, "walk", unreadable_walk)
    with pytest.raises(OSError, match="source_directory_unreadable"):
        getattr(verifier, scanner)()


@pytest.mark.parametrize("content", ["{invalid", "[]", "null"])
def test_invalid_configuration_fails_instead_of_being_ignored(
    tmp_path, monkeypatch, capsys, content
):
    docs = tmp_path / "docs"
    docs.mkdir()
    metrics = [
        "aetherra_consciousness_identity_coherence",
        "aetherra_consciousness_narrative_coherence",
        "aetherra_consciousness_workspace_queue_size",
        "aetherra_consciousness_narrative_chapters_total",
        "aetherra_consciousness_workspace_latency_seconds",
        "aetherra_consciousness_narrative_generation_seconds",
    ]
    (docs / "METRICS_REFERENCE.md").write_text("\n".join(metrics), encoding="utf-8")
    config = docs / "docs_consistency.json"
    config.write_text(content, encoding="utf-8")
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    monkeypatch.setattr(verifier, "DOCS_CFG", config)
    monkeypatch.setattr(verifier, "DOC_OVERVIEW", docs / "overview.md")
    monkeypatch.setattr(verifier, "REPORT", docs / "report.md")
    monkeypatch.setattr(sys, "argv", ["verify_docs_consistency"])
    assert verifier.main() == 1
    assert "configuration inspection failed" in capsys.readouterr().err


def test_main_inspection_failure_is_blocking_and_sanitized(monkeypatch, capsys):
    def unreadable():
        raise OSError("synthetic private failure detail")

    monkeypatch.setattr(verifier, "find_env_vars_in_code", unreadable)
    monkeypatch.setattr(sys, "argv", ["verify_docs_consistency"])
    assert verifier.main() == 1
    error = capsys.readouterr().err
    assert "source inspection failed (OSError)" in error
    assert "private failure detail" not in error


def test_source_inspection_ignores_existing_generated_scratch(tmp_path, monkeypatch):
    (tmp_path / "source.py").write_text(
        'os.getenv("AETHERRA_CURRENT")\n@app.route("/health")\ndef health(): pass',
        encoding="utf-8",
    )
    generated = tmp_path / ".pytest_tmp_snapshot"
    generated.mkdir()
    (generated / "stale.py").write_bytes(b"\xffinvalid generated bytes")
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    assert verifier.find_env_vars_in_code() == {"AETHERRA_CURRENT"}
    assert verifier.find_routes_in_code() == {"/health"}


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig"])
def test_environment_inspection_counts_calls_not_embedded_examples(
    tmp_path, monkeypatch, encoding
):
    source = "\n".join(
        [
            "import os",
            'value = os.getenv("AETHERRA_ACTUAL")',
            'other = os.environ.get("AETHERRA_OTHER", "0")',
            'required = os.environ["AETHERRA_REQUIRED"]',
            "example = 'os.getenv(\"AETHERRA_EXAMPLE\")'",
            '# os.getenv("AETHERRA_COMMENT")',
        ]
    )
    (tmp_path / "source.py").write_text(source, encoding=encoding)
    monkeypatch.setattr(verifier, "ROOT", tmp_path)
    assert verifier.find_env_vars_in_code() == {
        "AETHERRA_ACTUAL",
        "AETHERRA_OTHER",
        "AETHERRA_REQUIRED",
    }
