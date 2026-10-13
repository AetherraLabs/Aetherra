"""Exercise the real artifact hook against disposable Git indexes."""

import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/precommit_block_artifacts.py"
GIT = shutil.which("git")


@pytest.fixture
def repository(tmp_path):
    assert GIT is not None, "Git is required to verify the pre-commit hook"
    subprocess.run([GIT, "init", "--quiet", str(tmp_path)], check=True)
    return tmp_path


def run_hook(directory):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=directory,
        input="",
        capture_output=True,
        text=True,
        timeout=15,
        env={**os.environ, "GIT_CEILING_DIRECTORIES": str(directory.parent)},
    )


def stage(repository, filename):
    path = repository / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("synthetic artifact", encoding="utf-8")
    subprocess.run([GIT, "add", "--", filename], cwd=repository, check=True)


def test_hook_allows_empty_index(repository):
    result = run_hook(repository)
    assert result.returncode == 0, result.stderr


def test_hook_allows_source_and_documents(repository):
    stage(repository, "source/main.py")
    stage(repository, "docs/architecture.md")
    result = run_hook(repository)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "filename",
    [
        "state.db",
        "nested/state.sqlite",
        "nested/module.pyc",
        "nested/run.log",
        "outbox/events.jsonl",
        "audit/private.jsonl",
        "data/aetherra_kernel_metrics.json",
        "nested/generated report.json",
        "nested/caf\u00e9 report.json",
        "frontend/Lib/dependency.py",
    ],
)
def test_hook_blocks_both_original_pattern_sets(repository, filename):
    stage(repository, filename)
    result = run_hook(repository)
    assert result.returncode == 1
    assert "[BLOCKED]" in result.stdout
    assert filename in result.stdout


def test_hook_fails_closed_outside_repository(tmp_path):
    result = run_hook(tmp_path)
    assert result.returncode == 1
    assert "failed to list staged files" in result.stderr


def test_hook_fails_closed_when_git_is_missing(monkeypatch, capsys):
    hook = runpy.run_path(str(SCRIPT))
    monkeypatch.setattr(hook["shutil"], "which", lambda name: None)
    assert hook["main"]() == 1
    assert "failed to list staged files (RuntimeError)" in capsys.readouterr().err
